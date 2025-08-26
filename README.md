# Whisper Local API with Google Login

A production-ready FastAPI server that exposes a local Whisper transcription API using `faster-whisper`, secured by Google OAuth login and JWT.

## Features
- Google OAuth login (`/login/google`) and callback (`/auth/callback`)
- JWT set as httpOnly cookie; protected `/transcribe` and `/me`
- `faster-whisper` model with configurable `MODEL_NAME`, `DEVICE`, `COMPUTE_TYPE`
- Dockerfile with `ffmpeg` installed

## Requirements
- Python 3.10+
- FFmpeg (Dockerfile installs it automatically)
- Google OAuth credentials (Web application)

## Setup
1. Copy env file and configure:
```bash
cp .env.example .env
```

2. Create a Google Cloud project and OAuth 2.0 Client ID (Web application):
   - Authorized redirect URI: `http://localhost:8000/auth/callback`
   - Put `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` into `.env`

3. Install dependencies and run:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Login flow:
   - Visit `http://localhost:8000/login/google`
   - After consent, you'll be redirected to `/auth/success` and a cookie `access_token` will be set

5. Transcribe audio:
```bash
curl -X POST \
  -H "Authorization: Bearer $(python -c 'import http.cookies,requests;print("" )')" \
  -F "file=@/path/to/audio.wav" \
  http://localhost:8000/transcribe
```

Alternatively, since the cookie is httpOnly, use a browser-based client that forwards the cookie, or modify the `client_example.py` to include a Bearer token you copy from your browser devtools (Storage > Cookies) or add logic to fetch it after login if you host a simple UI.

## Docker
```bash
docker build -t whisper-local-api .
docker run --rm -it -p 8000:8000 --env-file .env whisper-local-api
```

## Config
- `MODEL_NAME`: tiny, base, small, medium, large-v2, large-v3, or local path
- `DEVICE`: cpu or cuda
- `COMPUTE_TYPE`: int8, int8_float16, float16, float32
- `MAX_UPLOAD_MB`: upload limit

## Client Example
See `client_example.py` for calling `/transcribe` with a Bearer token.