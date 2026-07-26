#!/usr/bin/env python3
"""
RED Core Air-Gesture Perception Engine.
Translates webcam hand landmarker tracking (MediaPipe) into spatial gestures:
- Single Pinch Drag: Window positioning / Volume adjustment
- Dual Pinch Expand: Expands DynamicWin into optional 3D Holographic Orb Mode
- Open Palm Wave: Alert dismissal / Voice Mute
"""

import os
import sys
import time
import math
import cv2
import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger("RedGestureEngine")

PINCH_THRESHOLD_ON = 0.05
PINCH_THRESHOLD_OFF = 0.08

class RedGestureTracker:
    def __init__(self, on_gesture: Optional[Callable[[str, dict], None]] = None):
        self.on_gesture = on_gesture
        self.is_running = False
        self.camera_thread = None
        self.cap = None
        self.last_gesture_time = 0

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.camera_thread = threading.Thread(target=self._gesture_loop, daemon=True)
        self.camera_thread.start()
        logger.info("[RED] RedGestureTracker: Webcam gesture tracking initialized.")

    def stop(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        logger.info("[RED] RedGestureTracker: Stopped gesture tracking.")

    def _gesture_loop(self):
        try:
            import mediapipe as mp
            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6
            )
        except Exception as e:
            logger.warning(f"MediaPipe hands init warning: {e}")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logger.warning("RedGestureTracker: Unable to open webcam for air gestures.")
            return

        prev_hands_dist = None

        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
                hand_landmarks_list = results.multi_hand_landmarks
                
                # Single Hand Pinch Detection
                if len(hand_landmarks_list) == 1:
                    landmarks = hand_landmarks_list[0].landmark
                    thumb_tip = landmarks[4]
                    index_tip = landmarks[8]
                    
                    dist = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
                    if dist < PINCH_THRESHOLD_ON:
                        now = time.time()
                        if now - self.last_gesture_time > 1.0:
                            self.last_gesture_time = now
                            logger.info("[GESTURE] Gesture Detected: Single Pinch Drag")
                            if self.on_gesture:
                                self.on_gesture("pinch_drag", {"x": index_tip.x, "y": index_tip.y})

                # Dual Hand Expansion Zoom Detection
                elif len(hand_landmarks_list) == 2:
                    h1 = hand_landmarks_list[0].landmark[8]
                    h2 = hand_landmarks_list[1].landmark[8]
                    curr_dist = math.hypot(h1.x - h2.x, h1.y - h2.y)

                    if prev_hands_dist is not None:
                        delta = curr_dist - prev_hands_dist
                        if delta > 0.15:
                            now = time.time()
                            if now - self.last_gesture_time > 1.5:
                                self.last_gesture_time = now
                                logger.info("[GESTURE] Gesture Detected: Dual Hand Expand -> Triggering Orb Mode")
                                if self.on_gesture:
                                    self.on_gesture("expand_orb", {})

                    prev_hands_dist = curr_dist

            time.sleep(0.03)

        self.cap.release()

if __name__ == "__main__":
    tracker = RedGestureTracker(on_gesture=lambda g, data: print(f"Gesture: {g}, Data: {data}"))
    tracker.start()
    time.sleep(5)
    tracker.stop()
