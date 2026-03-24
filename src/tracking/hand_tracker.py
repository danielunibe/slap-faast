import mediapipe as mp
from loguru import logger

class HandTracker:
    """Wrapper para MediaPipe Hands."""
    
    def __init__(self, static_mode=False, max_hands=2, detection_conf=0.5, tracking_conf=0.5):
        self._mp_hands = mp.solutions.hands
        self._hands = None
        self._config = {
            "static_image_mode": static_mode,
            "max_num_hands": max_hands,
            "min_detection_confidence": detection_conf,
            "min_tracking_confidence": tracking_conf
        }

    def initialize(self):
        self._hands = self._mp_hands.Hands(**self._config)
        logger.info("HandTracker inicializado.")

    def close(self):
        if self._hands:
            self._hands.close()
            self._hands = None

    def process_frame(self, frame_rgb):
        if not self._hands:
            return None
        return self._hands.process(frame_rgb)
