import cv2
import pyaudio
import wave
import threading
import time
from datetime import datetime

class RedEnforcer:
    def __init__(self):
        self.is_recording = False
        self.current_location = "Searching..."
        self._audio_frames = []  # cleared per-session to prevent unbounded growth

    def start_surveillance(self):
        """Activates silent camera and audio recording."""
        print("Red: Anti-Theft Protocol Alpha activated. Silent capture initiated.")
        self.is_recording = True
        self._audio_frames = []
        threading.Thread(target=self._record_video, daemon=True).start()
        threading.Thread(target=self._record_audio, daemon=True).start()

    def stop_surveillance(self):
        """Stops all recording threads cleanly."""
        self.is_recording = False

    def _record_video(self):
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'logs/evidence_v_{int(time.time())}.avi', fourcc, 20.0, (640, 480))

        while self.is_recording:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()

    def _record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        frames = []

        while self.is_recording:
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)

        # Stop and close stream before terminating PyAudio
        stream.stop_stream()
        stream.close()

        # Capture sample size BEFORE terminating the PyAudio instance
        sample_width = p.get_sample_size(pyaudio.paInt16)
        p.terminate()

        filename = f'logs/evidence_a_{int(time.time())}.wav'
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

    def get_location(self):
        """Retrieves GPS/Location from Windows Service."""
        # winsdk integration placeholder for final implementation
        print("Red: Geofencing theft event...")
        return "Lat: [REDACTED], Lon: [REDACTED]"
