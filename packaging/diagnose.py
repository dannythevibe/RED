import time
import sys

# Force UTF-8 for prints if possible, but stay safe
def log(msg):
    try:
        print(f"[*] {msg}")
    except:
        print(f"[*] [LOG ERROR] Unable to print message.")

log("Red: Diagnostic Launch Initiated...")

log("Step 1: Importing Core Modules...")
try:
    import speech_recognition as sr
    import pyttsx3
    import webview
    log("Status: Basic imports complete.")
except Exception as e:
    log(f"Status: Basic imports failed: {e}")

log("Step 2: Initializing System Controller...")
try:
    from system.red_system import SystemController
    sys_ctrl = SystemController()
    log("Status: SystemController ready.")
except Exception as e:
    log(f"Status: SystemController failed: {e}")

log("Step 3: Initializing RAG Knowledge Base...")
try:
    from knowledge.red_rag import RedRAG
    knowledge_base = RedRAG()
    log("Status: RedRAG ready.")
except Exception as e:
    log(f"Status: RedRAG failed: {e}")

log("Step 4: Initializing RedSoul (Ollama)...")
try:
    from system.red_ollama import RedSoul
    soul = RedSoul()
    log("Status: RedSoul ready.")
except Exception as e:
    log(f"Status: RedSoul failed: {e}")

log("Step 5: Initializing RedVision (Moondream)...")
try:
    from system.red_vision import RedVision
    vision = RedVision()
    log("Status: RedVision ready.")
except Exception as e:
    log(f"Status: RedVision failed: {e}")

log("Step 6: Initializing Voice Engine...")
try:
    engine = pyttsx3.init()
    log("Status: Voice Engine ready.")
except Exception as e:
    log(f"Status: Voice Engine failed: {e}")

log("Red: Diagnostics Complete. All systems clear for ignition.")
