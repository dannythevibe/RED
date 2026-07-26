"""
RED Core Action Item Extractor.
Extracts structured action items, reminders, and tasks from transcript stream segments.
"""
import re
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class RedActionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    completed: bool = False
    due_date: Optional[str] = None
    priority: str = "medium"


class RedActionExtractor:
    """
    Scans transcripts for task triggers and action items.
    """
    ACTION_KEYWORDS = [
        "remind me to", "need to", "don't forget to", "make sure to",
        "todo:", "action item:", "follow up on", "schedule"
    ]

    def extract_action_items(self, transcript_text: str) -> List[RedActionItem]:
        items = []
        lines = transcript_text.splitlines()
        for line in lines:
            line_lower = line.lower()
            for kw in self.ACTION_KEYWORDS:
                if kw in line_lower:
                    idx = line_lower.find(kw)
                    desc = line[idx + len(kw):].strip(" :-,.")
                    if desc:
                        items.append(RedActionItem(description=desc))
                    break
        return items
