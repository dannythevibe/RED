#!/usr/bin/env python3
"""
RED Core Groq Engine (Ultra-Fast Cloud AI & Vision Provider).
Provides sub-second inference using Groq LPUs for Llama 3.3 70B, Llama 3.2 Vision,
and Llama 4 family, with resilient error handling and local fallback awareness.
"""

import os
import sys
import json
import time
import logging
import base64
import requests
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger("RedGroqEngine")
logging.basicConfig(level=logging.INFO)

TEXT_MODEL_LLAMA4 = "llama-4-70b-versatile"
TEXT_MODEL_DEFAULT = "llama-3.1-8b-instant"
TEXT_MODEL_FALLBACK = "llama-3.3-70b-versatile"
TEXT_MODEL_FAST = "llama-3.1-8b-instant"
VISION_MODEL_DEFAULT = "llama-3.2-11b-vision-preview"
VISION_MODEL_LARGE = "llama-3.2-90b-vision-preview"

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

class GroqEngine:
    """
    High-performance Groq API Client for RED Core.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.api_key = api_key or self._load_api_key()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        } if self.api_key else {}

    def _load_api_key(self) -> str:
        key = os.environ.get("GROQ_API_KEY", "").strip()
        if key:
            return key
            
        memory_path = os.path.join(self.red_root, "config", "red_memory.json")
        try:
            if os.path.exists(memory_path):
                with open(memory_path, "r", encoding="utf-8") as f:
                    mem = json.load(f)
                    key = mem.get("groq_api_key", "").strip()
                    if key:
                        return key
        except Exception as e:
            logger.warning(f"Failed to read groq_api_key from config/red_memory.json: {e}")
        return ""

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        os.environ["GROQ_API_KEY"] = self.api_key

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate_text(
        self,
        messages: List[Dict[str, Any]],
        model: str = TEXT_MODEL_DEFAULT,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict[str, Any]]] = None,
        timeout: float = 5.0
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if not self.is_available():
            return False, "Groq API Key missing.", None
            
        # Fast offline check
        try:
            requests.get("https://api.groq.com", timeout=1.0)
        except requests.exceptions.RequestException:
            return False, "Groq unreachable (Offline)", None

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if tools:
            payload["tools"] = tools

        start_time = time.time()
        try:
            res = requests.post(GROQ_ENDPOINT, headers=self.headers, json=payload, timeout=timeout)
            elapsed = time.time() - start_time
            
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    message_obj = choices[0].get("message", {})
                    content = message_obj.get("content", "") or ""
                    logger.info(f"Groq [{model}] response generated in {elapsed:.2f}s")
                    return True, content.strip(), data
                return False, "Groq returned empty response choices.", data
            else:
                error_msg = f"Groq HTTP {res.status_code}: {res.text}"
                logger.error(error_msg)
                if model != TEXT_MODEL_FALLBACK:
                    logger.info(f"Retrying with fallback model [{TEXT_MODEL_FALLBACK}]...")
                    return self.generate_text(messages, model=TEXT_MODEL_FALLBACK, temperature=temperature, max_tokens=max_tokens, tools=tools, timeout=timeout)
                return False, error_msg, None
        except requests.exceptions.Timeout:
            return False, f"Groq request timed out after {timeout}s", None
        except Exception as e:
            return False, f"Groq request failed: {e}", None

    def analyze_image(
        self,
        image_b64: str,
        prompt: str = "Describe what is on this screen in high technical detail.",
        model: str = VISION_MODEL_DEFAULT,
        temperature: float = 0.5,
        max_tokens: int = 1024,
        timeout: float = 20.0
    ) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Groq API Key missing for Vision model."

        image_url = f"data:image/jpeg;base64,{image_b64}" if not image_b64.startswith("data:") else image_b64
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        start_time = time.time()
        try:
            res = requests.post(GROQ_ENDPOINT, headers=self.headers, json=payload, timeout=timeout)
            elapsed = time.time() - start_time
            
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    logger.info(f"Groq Vision [{model}] processed frame in {elapsed:.2f}s")
                    return True, content.strip()
                return False, "Empty vision response from Groq."
            else:
                return False, f"Groq Vision HTTP {res.status_code}: {res.text}"
        except Exception as e:
            return False, f"Groq Vision request failed: {e}"

if __name__ == "__main__":
    engine = GroqEngine()
    print(f"Groq Engine Available: {engine.is_available()}")
