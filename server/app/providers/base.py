from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..config import Settings


class TranscriptionProvider(ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    @abstractmethod
    def transcribe(self, file_bytes: bytes, language: Optional[str] = None) -> str:  # noqa: D401
        """Transcribe audio bytes and return text."""


def get_provider_by_name(name: str, settings: Settings) -> TranscriptionProvider | None:
    lname = (name or "").lower()
    if lname == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(settings)
    if lname == "deepgram":
        from .deepgram_provider import DeepgramProvider

        return DeepgramProvider(settings)
    if lname in {"faster_whisper", "faster-whisper", "local"}:
        from .faster_whisper_provider import FasterWhisperProvider

        return FasterWhisperProvider(settings)
    return None

