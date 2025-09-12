from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import time

from .config import Settings, get_settings, get_provider_from_env
from .models import TranscriptionResponse
from .commands import process_text_with_commands
from .providers.base import get_provider_by_name, TranscriptionProvider


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

    if commands:
        text = process_text_with_commands(text)

    response = TranscriptionResponse(
        text=text,
        provider=chosen_provider_name,
        tokens=None,
        durationSec=duration_sec,
    )
    return JSONResponse(content=response.model_dump())

