"""
RED Core Transcript Engine.
Native real-time audio transcript buffering, speaker diarization tracking, and sentence splitting.
"""
import uuid
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

SENTENCE_ENDERS = frozenset('.?!。！？؟۔।॥')
SENTENCE_ENDERS_CLASS = '[' + re.escape(''.join(SENTENCE_ENDERS)) + ']'
SENTENCE_SPLIT_RE = re.compile(r'(?<=' + SENTENCE_ENDERS_CLASS + r')\s*')


class RedTranscriptSegment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    speaker: str = "SPEAKER_00"
    speaker_id: int = 0
    is_user: bool = False
    start: float = 0.0
    end: float = 0.0

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.speaker and "_" in self.speaker:
            try:
                self.speaker_id = int(self.speaker.split("_", 1)[1])
            except (ValueError, IndexError):
                self.speaker_id = 0


class RedTranscriptEngine:
    """
    Manages continuous incoming transcript streams, segmenting sentences and keeping memory buffers.
    """
    def __init__(self):
        self.segments: List[RedTranscriptSegment] = []

    def add_segment(self, text: str, speaker: str = "SPEAKER_00", is_user: bool = False, start: float = 0.0, end: float = 0.0) -> RedTranscriptSegment:
        clean_text = text.strip()
        segment = RedTranscriptSegment(
            text=clean_text,
            speaker=speaker,
            is_user=is_user,
            start=start,
            end=end
        )
        self.segments.append(segment)
        return segment

    def get_full_transcript(self) -> str:
        return "\n".join([f"{seg.speaker}: {seg.text}" for seg in self.segments])

    def clear(self):
        self.segments.clear()
