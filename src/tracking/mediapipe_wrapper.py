"""
MediaPipe Wrapper - Compatibilidad con MediaPipe Tasks API 0.10.x
Proporciona una interfaz similar a la antigua API solutions para Hands, Pose y Face Mesh.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, NamedTuple
from dataclasses import dataclass
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision
from loguru import logger

# Paths a los modelos
MODEL_DIR = Path(__file__).parent.parent.parent / "src" / "models"
HAND_LANDMARKER_MODEL = MODEL_DIR / "hand_landmarker.task"
POSE_LANDMARKER_MODEL = MODEL_DIR / "pose_landmarker.task"
FACE_LANDMARKER_MODEL = MODEL_DIR / "face_landmarker.task"

@dataclass
class Landmark:
    """Landmark compatible con la API antigua."""
    x: float
    y: float
    z: float = 0.0
    visibility: float = 0.0 # Para Pose

class LandmarkListWrapper:
    """Wrapper genérico para lista de landmarks."""
    def __init__(self, landmarks_list):
        self.landmark = [
            Landmark(lm.x, lm.y, lm.z, getattr(lm, 'visibility', 0.0)) 
            for lm in landmarks_list
        ]

class HandsWrapper:
    """Wrapper para Hand Landmarker."""
    
    def __init__(self, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        if not HAND_LANDMARKER_MODEL.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {HAND_LANDMARKER_MODEL}")
            
        base_options = mp_tasks.BaseOptions(model_asset_path=str(HAND_LANDMARKER_MODEL))
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            running_mode=vision.RunningMode.IMAGE
        )
        self._detector = vision.HandLandmarker.create_from_options(options)
        logger.info(f"HandLandmarker inicializado")
    
    def process(self, frame_rgb: np.ndarray):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._detector.detect(mp_image)
        return self._convert_results(result)
    
    def _convert_results(self, result):
        class Results:
            def __init__(self):
                self.multi_hand_landmarks = None
                self.multi_handedness = None
        
        results = Results()
        if result.hand_landmarks:
            results.multi_hand_landmarks = [LandmarkListWrapper(l) for l in result.hand_landmarks]
            results.multi_handedness = result.handedness
        return results
    
    def close(self):
        if self._detector: self._detector.close()

class PoseWrapper:
    """Wrapper para Pose Landmarker."""
    
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        if not POSE_LANDMARKER_MODEL.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {POSE_LANDMARKER_MODEL}")
            
        base_options = mp_tasks.BaseOptions(model_asset_path=str(POSE_LANDMARKER_MODEL))
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            num_poses=1,
            min_pose_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            running_mode=vision.RunningMode.IMAGE
        )
        self._detector = vision.PoseLandmarker.create_from_options(options)
        logger.info(f"PoseLandmarker inicializado")
    
    def process(self, frame_rgb: np.ndarray):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._detector.detect(mp_image)
        return self._convert_results(result)
    
    def _convert_results(self, result):
        class Results:
            def __init__(self):
                self.pose_landmarks = None
                self.pose_world_landmarks = None
        
        results = Results()
        if result.pose_landmarks:
            results.pose_landmarks = LandmarkListWrapper(result.pose_landmarks[0])
        if result.pose_world_landmarks:
            results.pose_world_landmarks = LandmarkListWrapper(result.pose_world_landmarks[0])
        return results

    def close(self):
        if self._detector: self._detector.close()

class FaceMeshWrapper:
    """Wrapper para Face Landmarker."""
    
    def __init__(self, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        if not FACE_LANDMARKER_MODEL.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {FACE_LANDMARKER_MODEL}")
            
        base_options = mp_tasks.BaseOptions(model_asset_path=str(FACE_LANDMARKER_MODEL))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=max_num_faces,
            min_face_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=True,
            running_mode=vision.RunningMode.IMAGE
        )
        self._detector = vision.FaceLandmarker.create_from_options(options)
        logger.info(f"FaceLandmarker inicializado")
    
    def process(self, frame_rgb: np.ndarray):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._detector.detect(mp_image)
        return self._convert_results(result)

    def _convert_results(self, result):
        class Results:
            def __init__(self):
                self.multi_face_landmarks = None
        
        results = Results()
        if result.face_landmarks:
            results.multi_face_landmarks = [LandmarkListWrapper(l) for l in result.face_landmarks]
        return results

    def close(self):
        if self._detector: self._detector.close()

class MediaPipeWrapper:
    """Wrapper principal para DI."""
    def __init__(self):
        self._hands = None
        self._pose = None
        self._face = None
    
    def create_hands(self, **kwargs):
        self._hands = HandsWrapper(**kwargs)
        return self._hands
        
    def create_pose(self, **kwargs):
        self._pose = PoseWrapper(**kwargs)
        return self._pose
        
    def create_face_mesh(self, **kwargs):
        self._face = FaceMeshWrapper(**kwargs)
        return self._face

    def close_all(self):
        if self._hands: self._hands.close()
        if self._pose: self._pose.close()
        if self._face: self._face.close()
