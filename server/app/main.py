from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import time

from .config import Settings, get_settings, get_provider_from_env
from .models import TranscriptionResponse
from .commands import process_text_with_commands
from .providers.base import get_provider_by_name, TranscriptionProvider
from .db import engine, Base
from .db_models import Autotext, User
from .routers_profile import router as profile_router
from .auth import create_jwt, verify_google_id_token, get_current_user
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import get_session


settings: Settings = get_settings()
app = FastAPI(title="Orthopedic Dictation API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


def _auth_or_raise(api_key_header: Optional[str]) -> None:
    if not settings.server_api_key:
        return
    if not api_key_header or api_key_header.strip() != settings.server_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/v1/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default=None),
    provider: Optional[str] = Form(default=None),
    commands: bool = Form(default=True),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    _auth_or_raise(x_api_key)

    chosen_provider_name: str = provider or get_provider_from_env()
    provider_impl: TranscriptionProvider = get_provider_by_name(chosen_provider_name, settings)

    if not provider_impl:
        raise HTTPException(status_code=400, detail=f"Unknown provider '{chosen_provider_name}'")

    file_bytes: bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file upload")

    start_time = time.time()
    try:
        text: str = provider_impl.transcribe(file_bytes=file_bytes, language=language)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}") from exc
    duration_sec = round(time.time() - start_time, 3)

    # Load user-specific macros if Authorization bearer token is present
    user_macros: dict[str, str] | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            user = get_current_user(creds=None, db=get_session().__enter__())  # type: ignore[arg-type]
        except Exception:
            user = None
        if user:
            with get_session() as db:
                rows = db.execute(select(Autotext).where(Autotext.user_id == user.id)).scalars().all()
                user_macros = {row.trigger.lower(): row.expansion for row in rows}

    if commands:
        text = process_text_with_commands(text, user_macros=user_macros)

    response = TranscriptionResponse(
        text=text,
        provider=chosen_provider_name,
        tokens=None,
        durationSec=duration_sec,
    )
    return JSONResponse(content=response.model_dump())


@app.post("/auth/google")
def auth_google(id_token: str = Form(...)):
    info = verify_google_id_token(id_token)
    email = info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email missing from Google token")
    name = info.get("name")
    picture = info.get("picture")

    with get_session() as db:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user:
            user = User(email=email, name=name, picture_url=picture)
            db.add(user)
            db.flush()
        else:
            # Update profile fields if changed
            user.name = name or user.name
            user.picture_url = picture or user.picture_url
            db.add(user)
        token = create_jwt(user.id)
        return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.name, "picture": user.picture_url}}


@app.on_event("startup")
def on_startup():
    # Create tables
    Base.metadata.create_all(bind=engine)


app.include_router(profile_router)

