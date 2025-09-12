from __future__ import annotations

import io
import tempfile
from typing import Optional

from openai import OpenAI

from ..config import Settings
from .base import TranscriptionProvider


class OpenAIProvider(TranscriptionProvider):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def transcribe(self, file_bytes: bytes, language: Optional[str] = None) -> str:
        # OpenAI expects a file-like object; use a NamedTemporaryFile for reliability
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            with open(tmp.name, "rb") as fh:
                result = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=fh,
                    language=language,
                    response_format="json",
                )
        # result.text is present in SDK response
        return getattr(result, "text", "").strip()

