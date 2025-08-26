import io
import os
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .schemas import TranscriptionRequestOptions, TranscriptionResponse, User
from .deps import get_current_user
from .whisper_service import whisper_service
from . import auth as auth_routes


app = FastAPI(title=settings.APP_NAME)

# CORS for local dev frontends
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins(),
	allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
	allow_methods=[settings.CORS_ALLOW_METHODS] if settings.CORS_ALLOW_METHODS != "*" else ["*"] ,
	allow_headers=[settings.CORS_ALLOW_HEADERS] if settings.CORS_ALLOW_HEADERS != "*" else ["*"],
)

# Session middleware required for OAuth state and PKCE
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, session_cookie=settings.SESSION_COOKIE_NAME)

# Include auth router
app.include_router(auth_routes.router)


@app.middleware("http")
async def attach_user_to_request(request: Request, call_next):
	# Optional convenience: decode user if cookie present to support /me without dependency import cycle
	try:
		user = None
		auth_header = request.headers.get("Authorization")
		from .deps import _extract_bearer_token
		from jose import jwt
		from jose.exceptions import JWTError
		token = _extract_bearer_token(auth_header) or request.cookies.get("access_token")
		if token:
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
			user = User(id=str(payload.get("sub")), email=payload.get("email"), name=payload.get("name"), picture=payload.get("picture"))
		request.state.user = user
	except Exception:
		request.state.user = None
	response = await call_next(request)
	return response


@app.get("/health")
async def health():
	return {"status": "ok", "model": settings.MODEL_NAME, "device": settings.DEVICE}


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
	file: UploadFile = File(...),
	options: Optional[TranscriptionRequestOptions] = None,
	user: User = Depends(get_current_user),
):
	max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
	contents = await file.read()
	if len(contents) > max_bytes:
		raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File too large. Max {settings.MAX_UPLOAD_MB} MB")
	# Write to temp file for faster-whisper consumption
	with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "audio")[1]) as tmp:
		tmp.write(contents)
		tmp_path = tmp.name
	try:
		opts = options or TranscriptionRequestOptions()
		text, segments, language, duration = whisper_service.transcribe(
			file_path=tmp_path,
			language=opts.language,
			translate=opts.translate,
			beam_size=opts.beam_size,
			temperature=opts.temperature,
			vad_filter=opts.vad_filter,
			word_timestamps=opts.word_timestamps,
			initial_prompt=opts.initial_prompt,
			condition_on_previous_text=opts.condition_on_previous_text,
		)
		return TranscriptionResponse(text=text, segments=segments, language=language, duration=duration)
	finally:
		try:
			os.remove(tmp_path)
		except Exception:
			pass