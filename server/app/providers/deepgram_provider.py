from __future__ import annotations

from typing import Optional
import requests

from ..config import Settings
from .base import TranscriptionProvider


class DeepgramProvider(TranscriptionProvider):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not self.settings.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY not set")

    def transcribe(self, file_bytes: bytes, language: Optional[str] = None) -> str:
        # REST call to Deepgram Listen endpoint
        # Docs: https://developers.deepgram.com/docs/prerecorded
        params = {
            "model": "nova-2-general",
            "punctuate": "true",
            "smart_format": "true",
        }
        if language:
            params["language"] = language

        headers = {
            "Authorization": f"Token {self.settings.deepgram_api_key}",
            "Content-Type": "application/octet-stream",
        }
        resp = requests.post(
            "https://api.deepgram.com/v1/listen",
            params=params,
            data=file_bytes,
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # Extract transcript best guess
        try:
            return data["results"]["channels"][0]["alternatives"][0]["transcript"].strip()
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Unexpected Deepgram response: {data}") from exc

