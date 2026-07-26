import os
import sys
import mss
import base64
import requests
import logging
from PIL import Image
from io import BytesIO
from typing import Optional

red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if red_root not in sys.path:
    sys.path.append(red_root)

try:
    from system.ai.groq_engine import GroqEngine
except ImportError:
    GroqEngine = None

logger = logging.getLogger("RedVision")

_REQUEST_TIMEOUT = 60

class RedVision:
    """
    The Dual 'Eyes' of RED Core.
    """
    def __init__(self, local_model="llama3.2-vision", fallback_local_model="moondream"):
        self.sct = mss.mss()
        self.ollama_url = "http://localhost:11434/api/generate"
        self.local_model = local_model
        self.fallback_local_model = fallback_local_model
        self.groq_engine = GroqEngine() if GroqEngine else None

    def capture_screen(self, max_dim=1024) -> str:
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.thumbnail((max_dim, max_dim))
        
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze_screen(self, prompt="What is on my screen? describe it briefly in high technical detail.", force_local=False) -> str:
        image_b64 = self.capture_screen()

        if not force_local and self.groq_engine and self.groq_engine.is_available():
            logger.info("Analyzing screen via Groq Llama 3.2 Vision...")
            success, text = self.groq_engine.analyze_image(
                image_b64=image_b64,
                prompt=f"You are RED, Daniel's personal AI assistant. Look at this screen and answer: {prompt}",
                model="llama-3.2-11b-vision-preview"
            )
            if success and text:
                return text

        logger.info(f"Analyzing screen via Local Ollama [{self.local_model}]...")
        for model_to_try in [self.local_model, self.fallback_local_model]:
            payload = {
                "model": model_to_try,
                "prompt": f"You are RED, Daniel's personal AI assistant. Look at this screen and describe what is visible: {prompt}",
                "images": [image_b64],
                "stream": False
            }

            try:
                response = requests.post(self.ollama_url, json=payload, timeout=_REQUEST_TIMEOUT)
                if response.status_code == 200:
                    result = response.json()
                    res_text = result.get("response", "").strip()
                    if res_text:
                        return res_text
            except Exception as e:
                logger.warning(f"Local vision model '{model_to_try}' failed: {e}")

        return "Vision Engine offline. Local and cloud vision unreachable."

if __name__ == "__main__":
    vision = RedVision()
    print("Testing Dual Vision Engine...")
    print(vision.analyze_screen())
