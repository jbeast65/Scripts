from __future__ import annotations

import tempfile
from typing import Optional

from faster_whisper import WhisperModel

from ..config import Settings
from .base import TranscriptionProvider


_MODEL_CACHE: dict[str, WhisperModel] = {}


class FasterWhisperProvider(TranscriptionProvider):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        key = f"{settings.faster_whisper_model}:{settings.faster_whisper_device}:{settings.faster_whisper_cpu_threads}"
        if key not in _MODEL_CACHE:
            _MODEL_CACHE[key] = WhisperModel(
                model_size_or_path=settings.faster_whisper_model,
                device=settings.faster_whisper_device,
                compute_type="int8" if settings.faster_whisper_device == "cpu" else "float16",
                cpu_threads=settings.faster_whisper_cpu_threads,
            )
        self.model = _MODEL_CACHE[key]

    def transcribe(self, file_bytes: bytes, language: Optional[str] = None) -> str:
        # Write to temp file to let ffmpeg handle various formats
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            segments, _ = self.model.transcribe(tmp.name, language=language)
        text_parts: list[str] = [seg.text for seg in segments]
        return " ".join(part.strip() for part in text_parts).strip()

