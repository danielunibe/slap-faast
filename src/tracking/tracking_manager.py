"""
TrackingManager - MediaPipe Holistic Implementation
Unifica pose, manos y cara en un solo modelo optimizado.
"""
import cv2
import mediapipe as mp
import time
from typing import Optional, List, Tuple, Any
from loguru import logger

from ..core.events import EventBus, Events
from .motion_filter import PointFilter
from ..core.config import Config


class TrackingManager:
    """Gestor central de tracking usando MediaPipe Holistic."""
    
    def __init__(self):
        self._mp_holistic = mp.solutions.holistic
        self._mp_drawing = mp.solutions.drawing_utils
        
        # Holistic unifica pose, manos y cara - OPTIMIZED FOR PERFORMANCE
        self._holistic = self._mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=0,  # FASTEST (was: Config value, often 1 or 2)
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False,
            refine_face_landmarks=False,  # DISABLED iris tracking (saves ~15ms)
            min_detection_confidence=Config.TRACKING.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.TRACKING.MIN_TRACKING_CONFIDENCE
        )
        
        # Filtros One Euro para suavizado adicional (33 pose landmarks)
        self._pose_filters = [PointFilter(
            min_cutoff=Config.TRACKING.SMOOTHING_CUTOFF, 
            beta=Config.TRACKING.SMOOTHING_BETA
        ) for _ in range(33)]
        
        self._last_time = 0
        self._fps = 0
        
        logger.info("TrackingManager (Holistic) inicializado.")

    def start(self):
        logger.info("TrackingManager Holistic activo.")

    def stop(self):
        if self._holistic:
            self._holistic.close()
        logger.info("TrackingManager detenido.")

    def process_frame(self, frame_rgb) -> Tuple[Any, Any, Any, Any, Any]:
        """
        Procesa un frame y retorna (pose, left_hand, right_hand, face, world_landmarks).
        Usa MediaPipe Holistic para procesamiento unificado.
        """
        current_time = time.time()
        if self._last_time > 0:
            self._fps = 1 / (current_time - self._last_time)
        self._last_time = current_time

        # Procesamiento unificado con Holistic
        results = self._holistic.process(frame_rgb)
        
        # === POSE ===
        pose_data = results.pose_landmarks
        if pose_data:
            # Aplicar filtro One Euro para suavizado extra
            for i, landmark in enumerate(pose_data.landmark):
                if i < len(self._pose_filters):
                    nx, ny, nz = self._pose_filters[i].filter(
                        landmark.x, landmark.y, landmark.z, current_time
                    )
                    landmark.x, landmark.y, landmark.z = nx, ny, nz
        
        # === MANOS (Holistic provee manos separadas) ===
        left_hand = results.left_hand_landmarks
        right_hand = results.right_hand_landmarks
        
        # Compatibilidad: crear lista para CameraWidget
        hands_data = []
        if left_hand:
            hands_data.append(left_hand)
        if right_hand:
            hands_data.append(right_hand)
        
        # === CARA ===
        face_data = results.face_landmarks
        
        # === WORLD LANDMARKS (coordenadas 3D reales) ===
        world_landmarks = results.pose_world_landmarks
        
        # Publicar evento unificado (compatible con formato anterior)
        EventBus.publish(Events.POSE_READY, (pose_data, hands_data, face_data))
        
        return pose_data, hands_data, face_data, left_hand, right_hand

    def get_stats(self):
        return {"fps": self._fps}
    
    def get_holistic_results(self, frame_rgb):
        """Retorna resultados raw de Holistic para uso avanzado."""
        return self._holistic.process(frame_rgb)
