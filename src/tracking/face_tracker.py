import mediapipe as mp
import cv2
from loguru import logger

class FaceTracker:
    """Wrapper para MediaPipe Face Mesh."""
    
    def __init__(self):
        self._mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh = None
        self._drawing_spec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)

    def initialize(self):
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("FaceTracker inicializado.")

    def close(self):
        if self._face_mesh:
            self._face_mesh.close()
            self._face_mesh = None

    def process_frame(self, frame_rgb):
        """Procesa frame y retorna landmarks faciales."""
        if not self._face_mesh:
            return None
            
        results = self._face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0] # Retornar solo la primera cara
        return None
