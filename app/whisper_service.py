import os
import tempfile
from typing import Iterable, List, Optional, Tuple

from faster_whisper import WhisperModel

from .config import settings
from .schemas import TranscriptionSegment


class WhisperService:
	_instance: Optional["WhisperService"] = None

	def __init__(self, model_name: str, device: str, compute_type: str) -> None:
		self.model_name = model_name
		self.device = device
		self.compute_type = compute_type
		self._model: Optional[WhisperModel] = None

	def _ensure_model_loaded(self) -> WhisperModel:
		if self._model is None:
			self._model = WhisperModel(
				self.model_name,
				device=self.device,
				compute_type=self.compute_type,
			)
		return self._model

	def transcribe(
		self,
		file_path: str,
		language: Optional[str] = None,
		translate: bool = False,
		beam_size: int = 5,
		temperature: float = 0.0,
		vad_filter: bool = True,
		word_timestamps: bool = False,
		initial_prompt: Optional[str] = None,
		condition_on_previous_text: bool = True,
	) -> Tuple[str, List[TranscriptionSegment], Optional[str], Optional[float]]:
		model = self._ensure_model_loaded()
		segments_iter, info = model.transcribe(
			file_path,
			language=language,
			beam_size=beam_size,
			temperature=temperature,
			vad_filter=vad_filter,
			task="translate" if translate else "transcribe",
			word_timestamps=word_timestamps,
			initial_prompt=initial_prompt,
			condition_on_previous_text=condition_on_previous_text,
		)
		segments: List[TranscriptionSegment] = []
		full_text_parts: List[str] = []
		for seg in segments_iter:
			segments.append(TranscriptionSegment(start=float(seg.start), end=float(seg.end), text=seg.text))
			full_text_parts.append(seg.text)
		full_text = "".join(full_text_parts).strip()
		return full_text, segments, info.language, info.duration

	@classmethod
	def get_instance(cls) -> "WhisperService":
		if cls._instance is None:
			cls._instance = WhisperService(
				model_name=settings.MODEL_NAME,
				device=settings.DEVICE,
				compute_type=settings.COMPUTE_TYPE,
			)
		return cls._instance


whisper_service = WhisperService.get_instance()