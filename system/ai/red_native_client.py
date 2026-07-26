import time
import json
import logging
from typing import Iterator

from system.ai.red_native_engine import RedNativeEngine

logger = logging.getLogger(__name__)

class MockChoiceDelta:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, delta, finish_reason=None):
        self.delta = delta
        self.finish_reason = finish_reason

class MockChunk:
    def __init__(self, content, finish_reason=None):
        self.choices = [MockChoice(MockChoiceDelta(content), finish_reason=finish_reason)]

class MockCompletions:
    def __init__(self, engine):
        self.engine = engine

    def create(self, messages, model=None, stream=False, **kwargs):
        # We process the prompt directly in memory
        try:
            full_response = self.engine.generate_chat(messages, max_tokens=kwargs.get("max_tokens", 1024), temperature=kwargs.get("temperature", 0.3))
        except Exception as e:
            full_response = f"Brain lag: {e}"

        if not stream:
            class MockMessage:
                def __init__(self, content):
                    self.content = content
            class MockMessageChoice:
                def __init__(self, message):
                    self.message = message
            class MockResponse:
                def __init__(self, message_content):
                    self.choices = [MockMessageChoice(MockMessage(message_content))]
            return MockResponse(full_response)
        
        # Stream simulator (yields chunks so Hermes handles it natively)
        def chunk_generator() -> Iterator[MockChunk]:
            # Send the full response in chunks for visual effect in UI, or just one big chunk
            # Hermes expects choices[0].delta.content
            chunk_size = 12
            for i in range(0, len(full_response), chunk_size):
                yield MockChunk(full_response[i:i+chunk_size])
            yield MockChunk("", finish_reason="stop")
            
        return chunk_generator()

class MockChat:
    def __init__(self, engine):
        self.completions = MockCompletions(engine)

class RedNativeClient:
    """
    A duck-typed mock of the OpenAI client that bypasses HTTP ports
    and routes directly to the in-memory RedNativeEngine.
    """
    def __init__(self, **kwargs):
        self.engine = RedNativeEngine()
        self.chat = MockChat(self.engine)

    def close(self):
        # No TCP sockets to close
        pass
