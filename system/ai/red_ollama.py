import os
import sys
import json
import random
import logging

logger = logging.getLogger(__name__)

red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if red_root not in sys.path:
    sys.path.append(red_root)

from system.ai.red_native_engine import RedNativeEngine

from system.ai.groq_engine import GroqEngine

class RedSoul:
    """
    The 'Soul' of Red. Routes reasoning through Groq LPU cloud (when online)
    or the Native In-Memory Engine (zero ports, pure Python) when offline.
    """
    def __init__(self, model=None):
        self.system_prompt = (
            "You are RED, an advanced, highly intelligent personal AI assistant created by Daniel Iwayemi. "
            "Your responses are direct, elegant, professional, and precise. You speak with natural intelligence, "
            "delivering crisp answers without filler or artificial slang. When Danny requests changes to your codebase "
            "or system actions, execute them immediately and precisely."
        )
        self.conversation_history = []
        self.groq_engine = GroqEngine()
        self.native_engine = RedNativeEngine()
        logger.info("[RedSoul] Routing reasoning through Native In-Memory Engine (zero ports).")

    def think(self, user_input, override_prompt=None):
        prompt = override_prompt if override_prompt else user_input
        prompt_lc = prompt.lower().strip().strip("?.!,")

        # 0. Immediate greeting check for 0ms responses
        if prompt_lc in ("hello", "hi", "hey", "yo", "hello red", "hey red", "yo red", "hi red"):
            greetings = [
                "Hello Danny. Systems online and operational. How can I assist you?",
                "Greetings Danny. Ready for your command.",
                "Online, Danny. Standing by.",
                "Hello Danny. All subsystems active."
            ]
            reply = random.choice(greetings)
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply

        # 1. Try Groq Engine if available (ultra-fast LPU, sub-200ms latency)
        if self.groq_engine.is_available():
            try:
                messages = [{"role": "system", "content": self.system_prompt}]
                for msg in self.conversation_history[-6:]:
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": msg["content"]})
                messages.append({"role": "user", "content": prompt})

                model = "llama-3.1-8b-instant"
                success, reply, _ = self.groq_engine.generate_text(
                    messages=messages,
                    model=model,
                    temperature=0.3,
                    max_tokens=256
                )
                if success and reply:
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": reply})
                    return reply
            except Exception as e:
                logger.warning(f"[Groq Engine] Cloud inference failed: {e}. Falling back to Native Engine.")

        # 2. Native In-Memory Engine (zero ports, pure Python)
        self.conversation_history.append({"role": "user", "content": prompt})

        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            reply = self.native_engine.generate_chat(messages, max_tokens=256, temperature=0.3)
            if reply:
                self.conversation_history.append({"role": "assistant", "content": reply})
                return reply
            return "Brain lag. Native engine returned empty."
        except Exception as e:
            logger.error(f"[RedSoul] Native Engine failed: {e}")
            return f"Native engine offline: {e}"

    def extract_intent(self, user_input):
        user_input_lc = user_input.lower().strip()
        farewells = ["bye", "goodbye", "catch you later", "see ya", "shut down", "exit", "go to sleep", "sleep"]
        if any(f in user_input_lc for f in farewells):
            return {"farewell": True}
        return {"farewell": False}

if __name__ == "__main__":
    soul = RedSoul()
    print("Testing RedSoul Engine...")
    print(soul.think("Hello Red"))

