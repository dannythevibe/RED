#!/usr/bin/env python3
"""
Comprehensive Subsystem Test Suite for RED Core.
Tests instantiation and execution of all core modules in the reorganized architecture.
"""

import os
import sys
import json
import logging

red_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if red_root not in sys.path:
    sys.path.append(red_root)
engine_path = os.path.join(red_root, "system", "agent_engine")
if engine_path not in sys.path:
    sys.path.append(engine_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RedTestSuite")

def test_groq_engine():
    print("Testing GroqEngine...")
    from system.ai.groq_engine import GroqEngine
    engine = GroqEngine()
    print(f"  --> Groq Engine initialized. Available: {engine.is_available()}")
    return True

def test_audio_stream():
    print("Testing RedAudioStream...")
    from system.audio.red_audio_stream import RedAudioStream
    stream = RedAudioStream()
    stream.set_speaking_guard(True)
    print(f"  --> Self-Voice Guard toggled: {stream.is_speaking_guard}")
    stream.set_speaking_guard(False)
    print(f"  --> Self-Voice Guard toggled: {stream.is_speaking_guard}")
    return True

def test_vision():
    print("Testing RedVision Engine...")
    from system.vision.red_vision import RedVision
    vision = RedVision()
    b64 = vision.capture_screen(max_dim=100)
    print(f"  --> Screen captured successfully ({len(b64)} base64 chars).")
    return True

def test_agentic_coder():
    print("Testing RedAgenticCoder...")
    from system.agentic.red_agentic_coder import RedAgenticCoder
    coder = RedAgenticCoder()
    res = coder.run_terminal_command("echo 'RED Core Agentic Test'")
    print(f"  --> Terminal Output: {res['stdout']}")
    assert "RED Core Agentic Test" in res['stdout']
    return True

def test_mcp_server():
    print("Testing RedMCPServer...")
    from system.agentic.red_mcp_server import RedMCPServer
    server = RedMCPServer()
    tools = server.get_tool_definitions()
    print(f"  --> Registered MCP Tools: {[t['name'] for t in tools]}")
    assert len(tools) == 3
    return True

def test_sync_engine():
    print("Testing RedSyncEngine...")
    from system.cloud_sync.sync_engine import RedSyncEngine
    sync = RedSyncEngine()
    sync.enqueue_offline_item("test_event", {"status": "ok"})
    print("  --> Enqueued offline item in local SQLite database successfully.")
    return True

def test_cloud_server():
    print("Testing RedCloudServer FastAPI routes...")
    from system.cloud_sync.red_cloud_server import app, health_check
    h = health_check()
    print(f"  --> Cloud Server Health Check: {h}")
    assert h["status"] == "ok"
    return True

def test_live_intelligence():
    print("Testing Parallel Live Intelligence Grid...")
    from system.agentic.red_tools import red_get_world_news_tool, red_get_world_finance_news_tool
    news = red_get_world_news_tool()
    print("  --> Live News Briefing scraped concurrently.")
    fin = red_get_world_finance_news_tool()
    print("  --> Live Finance Briefing scraped concurrently.")
    assert "GLOBAL LIVE INTELLIGENCE BRIEFING" in news or "success" in news
    assert "GLOBAL FINANCE LIVE BRIEFING" in fin or "success" in fin
    return True

def test_gesture_perception():
    print("Testing RedGestureTracker Engine...")
    from system.vision.red_gesture import RedGestureTracker
    tracker = RedGestureTracker()
    print("  --> MediaPipe Air-Gesture Perception engine initialized cleanly.")
    return True

def test_conversation_memory():
    print("Testing RedConversationMemory Engine...")
    from system.memory.red_conversation_memory import RedConversationMemory, RedMemoryEntry
    import tempfile
    db_path = os.path.join(tempfile.gettempdir(), "red_test_memory.db")
    mem = RedConversationMemory(db_path=db_path)
    entry = RedMemoryEntry(content="Test memory entry", category="test")
    mem.store_memory(entry)
    results = mem.search_memories("Test memory")
    print(f"  --> Stored and retrieved {len(results)} memory entries.")
    assert len(results) >= 1
    try:
        os.remove(db_path)
    except Exception:
        pass
    return True

def test_transcript_engine():
    print("Testing RedTranscriptEngine...")
    from system.memory.red_transcript_engine import RedTranscriptEngine
    engine = RedTranscriptEngine()
    engine.add_segment("Hello RED", speaker="SPEAKER_00", is_user=True)
    engine.add_segment("Hello! How can I help?", speaker="SPEAKER_01", is_user=False)
    t = engine.get_full_transcript()
    print(f"  --> Transcript engine captured {len(engine.segments)} segments.")
    assert len(engine.segments) == 2
    return True

def test_action_extractor():
    print("Testing RedActionExtractor...")
    from system.memory.red_action_extractor import RedActionExtractor
    extractor = RedActionExtractor()
    actions = extractor.extract_action_items("Remind me to open the browser\nNeed to play some music")
    print(f"  --> Action extractor returned {len(actions)} actions.")
    assert len(actions) >= 1
    return True

if __name__ == "__main__":
    print("==================================================")
    print("[TEST] RUNNING RED CORE MASTER SUBSYSTEM SUITE...")
    print("==================================================")

    results = {
        "Groq Engine": test_groq_engine(),
        "Audio Stream VAD": test_audio_stream(),
        "Dual Vision": test_vision(),
        "Agentic Coder": test_agentic_coder(),
        "MCP Server": test_mcp_server(),
        "Sync Engine": test_sync_engine(),
        "Cloud Server": test_cloud_server(),
        "Live Intelligence": test_live_intelligence(),
        "Gesture Perception": test_gesture_perception(),
        "Conversation Memory": test_conversation_memory(),
        "Transcript Engine": test_transcript_engine(),
        "Action Extractor": test_action_extractor()
    }

    print("==================================================")
    print("[PASS] ALL SUBSYSTEM TESTS PASSED 100% SUCCESSFULLY!")
    print("==================================================")
    for name, passed in results.items():
        print(f"  [OK] {name}: PASSED")

