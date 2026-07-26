#!/usr/bin/env python3
"""
RED Core Audio Stream Engine (Continuous VAD & Hands-Free Conversation Loop).
Listens continuously in the background, detects voice activity (VAD), suppresses
RED's own TTS output, and streams transcribed user speech directly to the reasoning engine.
"""

import os
import sys
import time
import queue
import logging
import threading
import numpy as np
import speech_recognition as sr
from typing import Callable, Optional

logger = logging.getLogger("RedAudioStream")
logging.basicConfig(level=logging.INFO)

class RedAudioStream:
    """
    Continuous VAD-driven Audio Streamer with Self-Voice Suppression.
    Enables 100% hands-free voice interactions without typing.
    """
    def __init__(
        self,
        on_speech_captured: Optional[Callable[[str], None]] = None,
        energy_threshold: int = 300,
        pause_threshold: float = 0.8
    ):
        self.on_speech_captured = on_speech_captured
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = pause_threshold

        self.mic = None
        self.is_running = False
        self.is_speaking_guard = False  # Set to True while RED TTS is playing
        self.stop_listening_fn = None
        self.speech_queue = queue.Queue()
        self.worker_thread = None

    def set_speaking_guard(self, is_speaking: bool):
        """
        Activates or deactivates the self-voice acoustic guard.
        When True, mic inputs are ignored to prevent RED from listening to its own TTS.
        """
        self.is_speaking_guard = is_speaking
        if is_speaking:
            logger.debug("Self-Voice Acoustic Guard: ACTIVE (Ignoring mic)")
        else:
            logger.debug("Self-Voice Acoustic Guard: INACTIVE (Listening)")

    def _audio_callback(self, recognizer, audio_data):
        """Callback executed in background when speech phrase is completed."""
        if self.is_speaking_guard:
            logger.debug("Audio captured during TTS speech guard -- dropped.")
            return

        try:
            # Enqueue audio data for background processing
            self.speech_queue.put(audio_data)
        except Exception as e:
            logger.error(f"Error enqueuing audio data: {e}")

    def _process_queue(self):
        """Worker thread that transcribes captured audio clips."""
        while self.is_running:
            try:
                audio_data = self.speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self.is_speaking_guard:
                continue

            try:
                # Transcribe using SpeechRecognition default or local Whisper
                text = self.recognizer.recognize_google(audio_data)
                text = text.strip()
                if text:
                    logger.info(f"Captured Speech: '{text}'")
                    if self.on_speech_captured:
                        self.on_speech_captured(text)
            except sr.UnknownValueError:
                pass  # Inaudible noise / silence
            except sr.RequestError as e:
                logger.warning(f"Speech recognition service error: {e}")
            except Exception as e:
                logger.error(f"Error processing audio speech clip: {e}")

    def start(self):
        """Starts continuous non-blocking microphone listening."""
        if self.is_running:
            return

        try:
            self.mic = sr.Microphone()
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()

            # Start background ambient listener
            self.stop_listening_fn = self.recognizer.listen_in_background(
                self.mic,
                self._audio_callback,
                phrase_time_limit=15
            )
            logger.info("Continuous Hands-Free Audio Stream STARTED.")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self.is_running = False

    def stop(self):
        """Stops microphone listener and worker thread."""
        self.is_running = False
        if self.stop_listening_fn:
            self.stop_listening_fn(wait_for_stop=False)
            self.stop_listening_fn = None
        logger.info("Continuous Audio Stream STOPPED.")

if __name__ == "__main__":
    def print_text(text):
        print(f"--> User Said: {text}")

    stream = RedAudioStream(on_speech_captured=print_text)
    stream.start()
    print("Listening... Speak into mic (Press Ctrl+C to exit).")
    try:
        time.sleep(10)
    finally:
        stream.stop()
