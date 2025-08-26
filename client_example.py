import os
import sys
import requests

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
JWT = os.environ.get("JWT")  # Provide your JWT via env var or paste below

# If you want to paste token directly for quick testing, uncomment and set:
# JWT = "paste-token-here"

if not JWT:
	print("Missing JWT. Set JWT env var or paste the token in the script.")
	sys.exit(1)

if len(sys.argv) < 2:
	print("Usage: python client_example.py /path/to/audio.wav")
	sys.exit(1)

audio_path = sys.argv[1]

with open(audio_path, "rb") as f:
	files = {"file": (os.path.basename(audio_path), f, "application/octet-stream")}
	headers = {"Authorization": f"Bearer {JWT}"}
	r = requests.post(f"{API_BASE}/transcribe", files=files, headers=headers, timeout=600)
	print(r.status_code)
	print(r.text)