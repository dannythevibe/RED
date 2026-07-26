"""
RED Core Memory & Transcript Processing Subsystem.
Integrates wearable audio transcript buffer, action item extraction, and conversation memory.
"""
from system.memory.red_transcript_engine import RedTranscriptEngine, RedTranscriptSegment
from system.memory.red_action_extractor import RedActionExtractor, RedActionItem
from system.memory.red_conversation_memory import RedConversationMemory

__all__ = [
    "RedTranscriptEngine",
    "RedTranscriptSegment",
    "RedActionExtractor",
    "RedActionItem",
    "RedConversationMemory",
]
