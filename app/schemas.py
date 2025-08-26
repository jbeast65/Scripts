from typing import List, Optional
from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
	start: float = Field(..., description="Segment start time in seconds")
	end: float = Field(..., description="Segment end time in seconds")
	text: str


class TranscriptionRequestOptions(BaseModel):
	language: Optional[str] = Field(None, description="Language code, e.g., 'en'. If None, auto-detect")
	translate: bool = Field(False, description="Translate to English")
	beam_size: int = Field(5, ge=1, le=10)
	temperature: float = Field(0.0, ge=0.0, le=1.0)
	vad_filter: bool = Field(True, description="Enable VAD filtering")
	word_timestamps: bool = Field(False, description="Return word timestamps (may be slower)")
	initial_prompt: Optional[str] = Field(None, description="Optional text prompt to prime the model with domain terms")
	condition_on_previous_text: bool = Field(True, description="Condition on previous text for context")


class TranscriptionResponse(BaseModel):
	text: str
	segments: List[TranscriptionSegment]
	language: Optional[str] = None
	duration: Optional[float] = None


class User(BaseModel):
	id: str
	email: str
	name: Optional[str] = None
	picture: Optional[str] = None