#!/usr/bin/env python3
"""
RED Core Sync Engine (Local-First Offline/Online Auto-Sync).
Buffers memories, speech logs, action items, and vision events locally in SQLite when offline.
Automatically synchronizes with Render central cloud server when connected.
"""

import os
import sys
import json
import sqlite3
import time
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("RedSyncEngine")
logging.basicConfig(level=logging.INFO)

class RedSyncEngine:
    """
    Local-First Auto-Sync Manager for RED Core.
    """
    def __init__(self, db_path: Optional[str] = None, cloud_server_url: str = "http://localhost:8000"):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(parent_dir, "red_sync_buffer.db")
        self.cloud_server_url = cloud_server_url.rstrip("/")
        self._init_sqlite()

    def _init_sqlite(self):
        """Initializes local SQLite queue schema for offline buffering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def enqueue_offline_item(self, item_type: str, payload: Dict[str, Any]):
        """Buffers an item locally for later cloud synchronization."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sync_queue (item_type, payload, synced) VALUES (?, ?, 0)",
            (item_type, json.dumps(payload))
        )
        conn.commit()
        conn.close()
        logger.info(f"Buffered offline item [{item_type}] locally.")

    def check_cloud_online(self) -> bool:
        """Checks network connectivity to central cloud server."""
        try:
            res = requests.get(f"{self.cloud_server_url}/health", timeout=3.0)
            return res.status_code == 200
        except Exception:
            return False

    def sync_pending_items(self) -> int:
        """Pushes pending local items to cloud server and marks them as synced."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_type, payload FROM sync_queue WHERE synced = 0 LIMIT 50")
        rows = cursor.fetchall()

        if not rows:
            conn.close()
            return 0

        synced_count = 0
        for row_id, item_type, payload_str in rows:
            try:
                payload = json.loads(payload_str)
                res = requests.post(
                    f"{self.cloud_server_url}/v1/sync/push",
                    json={"item_type": item_type, "payload": payload},
                    timeout=5.0
                )
                if res.status_code == 200:
                    cursor.execute("UPDATE sync_queue SET synced = 1 WHERE id = ?", (row_id,))
                    synced_count += 1
            except Exception as e:
                logger.warning(f"Failed to sync item #{row_id}: {e}")
                break

        conn.commit()
        conn.close()
        logger.info(f"Successfully synced {synced_count} pending offline items to cloud.")
        return synced_count

if __name__ == "__main__":
    sync_engine = RedSyncEngine()
    sync_engine.enqueue_offline_item("fact", {"text": "Danny is building RED Core master upgrade."})
    print("Enqueued test offline item.")
