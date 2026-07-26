import os
import sys
import io
import logging

# Ensure Windows stdio handles all unicode characters safely without cp1252 exceptions
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure logging handlers don't crash on unencodable characters
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
for h in logging.root.handlers:
    if hasattr(h, 'setStream') or isinstance(h, logging.StreamHandler):
        h.setLevel(logging.INFO)

import speech_recognition as sr
import edge_tts
import pygame
import asyncio
import json
import random
import queue
import time
import requests
import hashlib
import shutil
from datetime import datetime
import pystray
from PIL import Image

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

is_online = True

def network_monitor():
    global is_online
    while True:
        try:
            requests.get("https://api.groq.com", timeout=2.0)
            is_online = True
        except requests.exceptions.RequestException:
            is_online = False
        time.sleep(10)

def pause_media():
    try:
        import pyautogui
        pyautogui.press('playpause')
    except Exception:
        pass

# Parent directory configuration
red_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if red_root not in sys.path:
    sys.path.append(red_root)

from system.os_controls.red_system import SystemController
from system.os_controls.red_strategy import StrategyCore
from knowledge.red_rag import RedRAG
from polymath_core.scanner import HackerScanner
from polymath_core.exploit_db import ExploitAnalyzer
from polymath_core.report_engine import ReportEngine
from polymath_core.academy import PolymathAcademy
from polymath_core.strategy import ShortcutEngine
from system.agentic.memory_synthesizer import MemorySynthesizer
from system.ai.red_ollama import RedSoul
from system.vision.red_vision import RedVision
from system.ai.groq_engine import GroqEngine
from system.audio.red_audio_stream import RedAudioStream
from system.agentic.red_agentic_coder import RedAgenticCoder
from system.cloud_sync.sync_engine import RedSyncEngine
from system.os_controls.daemon_manager import create_default_manager
from system.ai.red_native_engine import RedNativeEngine
from core.gui_launcher import RedIslandUI
import threading
import re

from system.audio.dictation_service import DictationService
from system.agentic.red_tools import get_red_bridge

# Queue to hold inputs from mic, VAD stream, and Electron UI
input_queue = queue.Queue()

# Global subsystem placeholders
sys_ctrl = None
strat_core = None
knowledge_base = None
hacker_ai = None
exploit_intel = None
reporter = None
academy = None
shortcut_engine = None
memory_synth = None
soul_engine = None
vision_engine = None
groq_engine = None
audio_stream = None
agentic_coder = None
sync_engine = None
dictation_engine = None
ui = None
daemon_mgr = None
native_engine = None

# Initialize pygame mixer for premium audio playback
try:
    pygame.mixer.init()
except Exception as e:
    print(f"⚠️ Pygame mixer init failed: {e}")

def load_memory():
    memory_path = os.path.join(red_root, "config", "red_memory.json")
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Red: Memory file not found in config/. Starting with empty memory.")
        return {}
    except json.JSONDecodeError:
        print("Red: Memory file corrupted. Starting with empty memory.")
        return {}

memory = load_memory()

def save_memory(data):
    memory_path = os.path.join(red_root, "config", "red_memory.json")
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def clean_text_for_speech(text):
    text = re.sub(r'\*', '', text)
    text = re.sub(r'`', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text) # remove markdown links
    return text

def setup_tray():
    def on_quit(icon, item):
        if daemon_mgr:
            daemon_mgr.stop_all()
        icon.stop()
        os._exit(0)
    try:
        icon_path = os.path.join(red_root, "ui", "src", "DynamicWin", "OutPortable.ico")
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            image = Image.new('RGB', (64, 64), color=(255, 0, 0))
        
        menu = pystray.Menu(pystray.MenuItem('Quit RED', on_quit))
        icon = pystray.Icon("RED", image, "RED Core System", menu)
        icon.run()
    except Exception as e:
        print(f"Tray icon failed: {e}")

def speak(text, emotion="neutral"):
    """
    Renders text to voice using Edge-TTS (en-GB-RyanNeural).
    """
    global is_online
    clean_txt = clean_text_for_speech(text)
    voice = "en-GB-RyanNeural"
    if emotion in ("soft", "alternative"):
        voice = "en-GB-ThomasNeural"

    cache_dir = os.path.join(red_root, "cache", "audio")
    os.makedirs(cache_dir, exist_ok=True)
    h = hashlib.md5((clean_txt + voice).encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{h}.mp3")

    is_cached = False
    if os.path.exists(cache_file):
        temp_file = cache_file
        is_cached = True
    else:
        temp_file = os.path.join(red_root, f"red_speech_{random.randint(1000, 9999)}.mp3")
        
        if not is_online:
            if pyttsx3:
                print(f"[RED] Offline Mode: Using local pyttsx3 TTS.")
                engine = pyttsx3.init()
                engine.say(clean_txt)
                engine.runAndWait()
            else:
                print("[RED] Offline and pyttsx3 not installed.")
            return

        async def _generate():
            communicate = edge_tts.Communicate(clean_txt, voice)
            await communicate.save(temp_file)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_generate())
            loop.close()
            shutil.copy(temp_file, cache_file)
        except Exception as e:
            print(f"⚠️ Red Voice generation failed: {e}")
            if audio_stream:
                audio_stream.set_speaking_guard(False)
            if pyttsx3:
                engine = pyttsx3.init()
                engine.say(clean_txt)
                engine.runAndWait()
            return

    try:
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if not input_queue.empty():
                pygame.mixer.music.stop()
                print("[RED] Playback interrupted by user input.")
                break
            pygame.time.Clock().tick(20)
        pygame.mixer.music.unload()
        if not is_cached and os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        print(f"⚠️ Audio playback / cleanup error: {e}")
        print(f"RED: {text}")
    finally:
        if audio_stream:
            audio_stream.set_speaking_guard(False)

def red_response(user_input, typing_mode=False):
    user_input_lc = user_input.lower().strip()

    if any(k in user_input_lc for k in ["expand yourself", "orb mode", "orb view", "show orb"]):
        if ui:
            ui.set_mode("orb")
        return "Expanding to 3D Holographic Orb overlay view.", "neutral"

    if any(k in user_input_lc for k in ["world news", "brief me", "what did i miss", "what's happening in the world"]):
        from system.agentic.red_tools import red_get_world_news_tool, red_open_world_monitor_tool
        news_res = json.loads(red_get_world_news_tool())
        briefing = news_res.get("briefing", "Unable to pull live news feed.")
        red_open_world_monitor_tool()
        return f"Here is your global briefing, Danny:\n\n{briefing}\nOpening World Monitor dashboard now.", "neutral"

    if any(k in user_input_lc for k in ["finance news", "market news", "markets", "economy update"]):
        from system.agentic.red_tools import red_get_world_finance_news_tool, red_open_finance_world_monitor_tool
        fin_res = json.loads(red_get_world_finance_news_tool())
        briefing = fin_res.get("briefing", "Unable to pull financial news.")
        red_open_finance_world_monitor_tool()
        return f"Market update, Danny:\n\n{briefing}\nOpening Finance Monitor dashboard now.", "neutral"

    if any(k in user_input_lc for k in ["look at my screen", "what's on my screen", "what is on my screen", "see my screen"]):
        if vision_engine:
            report = vision_engine.analyze_screen()
            return f"Looking at your screen: {report}", "neutral"

    if any(k in user_input_lc for k in ["change your code", "modify your code", "update your code", "edit your code", "refactor your code"]):
        if agentic_coder:
            return f"Engaging RED DEV Autonomous Coder to execute your requested codebase modifications.", "neutral"

    intent_data = soul_engine.extract_intent(user_input)

    if intent_data.get("farewell", False):
        farewell_reply = soul_engine.think(user_input, "[Danny is leaving. Give a concise, elegant, professional farewell.]")
        return farewell_reply, "dark", True

    dynamic_reply = soul_engine.think(user_input)
    return dynamic_reply, "neutral"

def log_memory(user_input, reply):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs_dir = os.path.join(red_root, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    with open(os.path.join(logs_dir, "conversations.txt"), "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] YOU: {user_input}\n")
        log.write(f"[{timestamp}] RED: {reply}\n\n")

    if sync_engine:
        sync_engine.enqueue_offline_item("interaction", {"user": user_input, "red": reply})

def boot_red():
    print("[RED] Red: Core Ignited. Establishing Core Handshake...")
    speak("RED is online and ready, Danny.", "neutral")

def red_loop():
    global sys_ctrl, strat_core, knowledge_base, hacker_ai, exploit_intel, reporter, academy, memory_synth, soul_engine, vision_engine, groq_engine, audio_stream, agentic_coder, sync_engine, dictation_engine, ui, daemon_mgr, native_engine

    # ── Phase 0: Daemon Manager (OSIRIS, future services) ────────────
    print("[RED] Red: Booting Daemon Manager (OSIRIS World Monitor)...")
    daemon_mgr = create_default_manager()
    daemon_mgr.start_all()

    # ── Phase 0.5: Native LLM Engine (pre-load into RAM) ─────────────
    print("[RED] Red: Pre-loading Native LLM Engine into memory pool...")
    native_engine = RedNativeEngine()
    threading.Thread(target=native_engine.load_model, daemon=True, name="native-llm-loader").start()

    print("[RED] Red: Launching Network Monitor...")
    threading.Thread(target=network_monitor, daemon=True).start()

    print("[RED] Red: Launching System Tray Icon...")
    threading.Thread(target=setup_tray, daemon=True).start()

    print("[RED] Red: Launching RedIsland UI...")
    ui = RedIslandUI()
    ui_thread = threading.Thread(target=ui.start, daemon=True)
    ui_thread.start()
    
    print("[RED] Red: Awakening Subsystems (Native Engine, Dual Vision, Agentic Coder, VAD Stream)...")
    sys_ctrl = SystemController()
    strat_core = StrategyCore()
    knowledge_base = RedRAG()
    hacker_ai = HackerScanner()
    exploit_intel = ExploitAnalyzer()
    reporter = ReportEngine()
    academy = PolymathAcademy(rag_engine=knowledge_base)
    shortcut_engine = ShortcutEngine()
    memory_synth = MemorySynthesizer()
    soul_engine = RedSoul()
    groq_engine = GroqEngine()
    vision_engine = RedVision()
    agentic_coder = RedAgenticCoder()
    sync_engine = RedSyncEngine()

    from system.vision.red_gesture import RedGestureTracker
    from system.agentic.red_mcp_server import RedMCPServer

    gesture_tracker = RedGestureTracker(
        on_gesture=lambda gesture, data: ui.set_mode("orb") if gesture == "expand_orb" else None
    )
    gesture_tracker.start()

    mcp_server = RedMCPServer()
    mcp_thread = threading.Thread(target=mcp_server.run_sse, args=(8000,), daemon=True)
    mcp_thread.start()

    dictation_engine = DictationService(hotkey='f9')
    dictation_thread = threading.Thread(target=dictation_engine.start, daemon=True)
    dictation_thread.start()

    audio_stream = RedAudioStream(on_speech_captured=lambda text: input_queue.put(text))
    audio_stream.start()

    bridge = get_red_bridge()
    bridge["sys_ctrl"] = sys_ctrl
    bridge["strat_core"] = strat_core
    bridge["knowledge_base"] = knowledge_base
    bridge["academy"] = academy
    bridge["vision_engine"] = vision_engine
    bridge["groq_engine"] = groq_engine
    bridge["agentic_coder"] = agentic_coder
    bridge["sync_engine"] = sync_engine

    boot_red()

    ui.message_callback = lambda text: input_queue.put(text)

    typing_mode = False
    while True:
        ui.set_mode("idle")
        user_input = input_queue.get()
        if not user_input.strip():
            continue
            
        pause_media()

        ui.set_mode("active")

        synth_result = memory_synth.synthesize_interaction(user_input)
        if synth_result:
            print(f"🧠 {synth_result}")

        ui.set_mode("thinking")

        result = red_response(user_input, typing_mode)

        if isinstance(result, tuple) and len(result) == 3 and result[2] is True:
            reply, tone, _ = result
            ui.set_mode("boot")
            speak(reply, tone)
            break
        elif isinstance(result, tuple) and len(result) == 3:
            reply, tone, new_mode = result
            typing_mode = new_mode
            ui.set_mode("active")
            speak(reply, tone)
            continue

        reply, tone = result

        if reply:
            clean_reply = clean_text_for_speech(reply)
            ui.show_reply(clean_reply)
            speak(reply, tone)
            log_memory(user_input, reply)

if __name__ == "__main__":
    red_loop()
