import os
import sys
import json
import logging

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

logger = logging.getLogger(__name__)

class RedNativeEngine:
    """
    True Native LLM Engine for RED.
    Loads GGUF models directly into red.exe's memory pool using llama-cpp-python.
    Zero ports, zero HTTP requests, pure native inference.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedNativeEngine, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.model_path = None
        return cls._instance

    def __init__(self, model_path=None):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            default_model = os.path.join(red_root, "models", "qwen2.5-coder-7b-instruct-q4_k_m.gguf")
            self.model_path = model_path if model_path else default_model
            self.model = None

    def load_model(self):
        """Loads the LLM into RAM/VRAM."""
        if self.model is not None:
            return True

        if not HAS_LLAMA_CPP:
            logger.error("[RedNativeEngine] llama-cpp-python is not installed! Run: pip install llama-cpp-python")
            return False

        if not os.path.exists(self.model_path):
            logger.warning(f"[RedNativeEngine] Model file not found at {self.model_path}. Please place your GGUF model there.")
            return False

        try:
            logger.info(f"[RedNativeEngine] Loading {self.model_path} directly into memory pool...")
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=8192,  # 8k context window
                n_threads=8, # Optimize for CPU
                verbose=False # Keep console clean
            )
            logger.info("[RedNativeEngine] Native Model Loaded Successfully.")
            return True
        except Exception as e:
            logger.error(f"[RedNativeEngine] FATAL: Failed to load native model: {e}")
            return False

    def generate(self, prompt, max_tokens=1024, temperature=0.3):
        """Synchronous native text generation."""
        if not self.model:
            if not self.load_model():
                return "Error: Native model offline or not found."
        
        try:
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|endoftext|>", "<|im_end|>"]
            )
            return output["choices"][0]["text"]
        except Exception as e:
            logger.error(f"[RedNativeEngine] Inference Exception Caught Natively: {e}")
            return f"Brain lag: {e}"

    def generate_chat(self, messages, max_tokens=1024, temperature=0.3):
        """Handles chat format mapping to native generation."""
        if not self.model:
            if not self.load_model():
                return "Error: Native model offline or not found."

        try:
            response = self.model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|endoftext|>", "<|im_end|>"]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"[RedNativeEngine] Chat Inference Exception Caught Natively: {e}")
            return f"Brain lag: {e}"

if __name__ == "__main__":
    # Test Native Initialization
    engine = RedNativeEngine()
    print("RedNativeEngine initialized. Awaiting model load.")
