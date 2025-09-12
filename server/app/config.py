import os
from dataclasses import dataclass


@dataclass
class Settings:
    server_api_key: str | None
    default_provider: str
    openai_api_key: str | None
    deepgram_api_key: str | None
    faster_whisper_model: str
    faster_whisper_device: str
    faster_whisper_cpu_threads: int
    jwt_secret: str
    google_client_id: str | None


def get_settings() -> Settings:
    return Settings(
        server_api_key=os.getenv("SERVER_API_KEY"),
        default_provider=os.getenv("PROVIDER", "openai"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        deepgram_api_key=os.getenv("DEEPGRAM_API_KEY"),
        faster_whisper_model=os.getenv("FASTER_WHISPER_MODEL", "base.en"),
        faster_whisper_device=os.getenv("FASTER_WHISPER_DEVICE", "cpu"),
        faster_whisper_cpu_threads=int(os.getenv("FASTER_WHISPER_CPU_THREADS", "4")),
        jwt_secret=os.getenv("JWT_SECRET", "change_me"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
    )


def get_provider_from_env() -> str:
    return get_settings().default_provider

