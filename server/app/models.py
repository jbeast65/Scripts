from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    text: str
    provider: str
    tokens: int | None = None
    durationSec: float | None = None

