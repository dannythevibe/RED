"""
RED Core Conversation Memory Engine.
Stores and retrieves conversation histories, summaries, and structured memory entries locally.
"""
import json
import os
import uuid
import sqlite3
import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RedMemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    category: str = "general"
    source: str = "conversation"
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RedConversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None
    segments: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class RedConversationMemory:
    """
    Persistent conversation memory engine backed by local SQLite.
    Stores conversations, memories, and structured extractions for retrieval.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(red_root, "system", "red_memory.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                segments TEXT,
                action_items TEXT,
                created_at REAL,
                updated_at REAL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT,
                category TEXT,
                source TEXT,
                timestamp REAL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store_conversation(self, conversation: RedConversation) -> str:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO conversations (id, title, summary, segments, action_items, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                conversation.id,
                conversation.title,
                conversation.summary,
                json.dumps(conversation.segments),
                json.dumps(conversation.action_items),
                conversation.created_at,
                conversation.updated_at,
            ),
        )
        conn.commit()
        conn.close()
        return conversation.id

    def store_memory(self, entry: RedMemoryEntry) -> str:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO memories (id, content, category, source, timestamp, metadata) VALUES (?, ?, ?, ?, ?, ?)",
            (
                entry.id,
                entry.content,
                entry.category,
                entry.source,
                entry.timestamp,
                json.dumps(entry.metadata),
            ),
        )
        conn.commit()
        conn.close()
        return entry.id

    def search_memories(self, query: str, limit: int = 10) -> List[RedMemoryEntry]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT id, content, category, source, timestamp, metadata FROM memories WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        rows = c.fetchall()
        conn.close()
        results = []
        for row in rows:
            results.append(
                RedMemoryEntry(
                    id=row[0],
                    content=row[1],
                    category=row[2],
                    source=row[3],
                    timestamp=row[4],
                    metadata=json.loads(row[5]) if row[5] else {},
                )
            )
        return results

    def get_recent_conversations(self, limit: int = 5) -> List[RedConversation]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT id, title, summary, segments, action_items, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )
        rows = c.fetchall()
        conn.close()
        results = []
        for row in rows:
            results.append(
                RedConversation(
                    id=row[0],
                    title=row[1],
                    summary=row[2],
                    segments=json.loads(row[3]) if row[3] else [],
                    action_items=json.loads(row[4]) if row[4] else [],
                    created_at=row[5],
                    updated_at=row[6],
                )
            )
        return results

    def available(self) -> bool:
        return os.path.exists(self.db_path) or True
