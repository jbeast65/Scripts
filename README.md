## Orthopedic Speech Dictation (Cloud + Windows Client)

End-to-end reference implementation for a cost-effective cloud transcription service with a Windows 10/11 push-to-talk client. Supports Whisper/OpenAI and Deepgram providers, autotexts/macros, and spoken punctuation commands. Designed for dictaphones, Dragon PowerMic, and Philips SpeechMike via hotkey or HID stubs.

### Features
- Cloud FastAPI server with pluggable transcription providers
- API key auth via `X-API-Key`
- Autotexts/macros and spoken commands (e.g., "new line", "comma", "macro hip exam")
- Windows client with global hotkey to record, send audio, and paste output
- Dockerized server for AWS EC2 (or any VM/container host)

### Repo Structure
```
server/
  app/
    main.py
    config.py
    models.py
    commands.py
    providers/
      base.py
      openai_provider.py
      deepgram_provider.py
      faster_whisper_provider.py
  requirements.txt
  Dockerfile
  compose.yml
client/
  windows_client.py
  usb_stubs.py
  config.example.json
  requirements.txt
  build.ps1
```

### Quick Start (Local)
1) Server
```
cd server
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export SERVER_API_KEY=dev_key_123
export PROVIDER=openai  # or deepgram or faster_whisper
export OPENAI_API_KEY=...   # if PROVIDER=openai
export DEEPGRAM_API_KEY=... # if PROVIDER=deepgram
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2) Windows Client (on Windows)
```
cd client
py -m venv .venv && .venv\\Scripts\\activate
py -m pip install -r requirements.txt
copy config.example.json config.json
  # edit config.json: set server_url and api_key
py windows_client.py
```
Press Ctrl+Shift+R to start/stop recording. The result copies to clipboard and optionally auto-pastes.

### AWS EC2 Deployment (cost-effective baseline)
1) Create an Ubuntu 22.04 EC2 (e.g., t3.small), 20 GB disk. In security group, allow TCP 80/443 from 0.0.0.0/0.
2) SSH to the instance, install Docker:
```
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
3) Copy `server/` to the instance (or git clone your repo). Build and run:
```
cd server
sudo docker build -t ortho-dictation:latest .
sudo docker run -d --name ortho-api \
  -e SERVER_API_KEY=your_long_random_key \
  -e PROVIDER=openai \
  -e OPENAI_API_KEY=sk-... \
  -p 80:8000 \
  ortho-dictation:latest
```
4) Optional: Use a domain and terminate TLS with a reverse proxy (e.g., Caddy or Nginx). For quickest TLS:
```
sudo docker run -d --name caddy --network host \
  -v caddy_data:/data -v caddy_config:/config \
  -e ACME_AGREE=true \
  -e DOMAIN=api.example.com \
  -e UPSTREAM=http://127.0.0.1:8000 \
  caddy:2
```
Then configure a Caddyfile mapping your domain to the upstream.

Notes on cost:
- OpenAI Whisper API is billed per minute; Deepgram offers competitive tiers and better latency.
- If you need fixed cost, run `faster-whisper` on the EC2 (requires CPU/GPU and ffmpeg). A CPU-friendly model like `medium` is workable on c6i/c7i; for real-time, prefer GPU (g4dn).

### Commands and Autotexts
Spoken punctuation and control phrases are transformed server-side. Example phrases:
- "new line", "new paragraph", "comma", "period"
- "macro hip exam", "macro shoulder exam", "macro knee plan"

You can customize triggers and templates in `server/app/commands.py`.

### Packaging Windows Client
```
cd client
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py build.ps1
```
Distribute the generated EXE and a `config.json`.

### Security
- Use a long random `SERVER_API_KEY`. The client sends `X-API-Key` header.
- Prefer running behind TLS with a domain. Never expose the server without HTTPS in production.

### API
`POST /v1/transcribe` (multipart)
- file: audio data (wav/flac/mp3/m4a)
- language: optional (e.g., "en")
- provider: optional override ("openai" | "deepgram" | "faster_whisper")
- commands: optional bool (default true)

Response:
```
{
  "text": "...",
  "provider": "openai",
  "tokens": null,
  "durationSec": 3.1
}
```

`GET /health` returns `{ "status": "ok" }`.

### USB Dictaphone Buttons
See `client/usb_stubs.py` for starting points using `hid` to map PowerMic/SpeechMike buttons to the hotkey.

