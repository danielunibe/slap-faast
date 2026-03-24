"""
GazeTracker - Detección de dirección de mirada
Usa landmarks faciales de MediaPipe para estimar hacia dónde mira el usuario.
"""
import numpy as np
from typing import Optional, Tuple
from loguru import logger
import mediapipe as mp


class GazeTracker:
    """
    Rastrea la dirección de la mirada del usuario.
    Útil para el feature "Gaze-Audio Trigger".
    """
    
    # Indices de landmarks para los ojos (MediaPipe Face Mesh)
    LEFT_EYE_INDICES = [33, 133, 160, 158, 144, 153]
    RIGHT_EYE_INDICES = [362, 263, 387, 385, 373, 380]
    LEFT_IRIS = [468, 469, 470, 471, 472]
    RIGHT_IRIS = [473, 474, 475, 476, 477]
    
    def __init__(self):
        self._last_gaze_direction = "CENTER"
        self._gaze_ratio = (0.5, 0.5)  # (horizontal, vertical)
    
    def process(self, face_landmarks) -> Tuple[str, Tuple[float, float]]:
        """
        Procesa landmarks faciales y retorna dirección de mirada.
        
        Returns:
            Tuple[str, Tuple[float, float]]: 
                - Dirección ("LEFT", "RIGHT", "CENTER", "UP", "DOWN")
                - Ratio (horizontal 0-1, vertical 0-1)
        """
        if face_landmarks is None or not hasattr(face_landmarks, 'landmark'):
            return self._last_gaze_direction, self._gaze_ratio
        
        landmarks = face_landmarks.landmark
        
        try:
            # Calcular centro del iris izquierdo
            left_iris_x = np.mean([landmarks[i].x for i in self.LEFT_IRIS])
            left_iris_y = np.mean([landmarks[i].y for i in self.LEFT_IRIS])
            
            # Calcular centro del iris derecho
            right_iris_x = np.mean([landmarks[i].x for i in self.RIGHT_IRIS])
            right_iris_y = np.mean([landmarks[i].y for i in self.RIGHT_IRIS])
            
            # Calcular límites del ojo izquierdo
            left_eye_left = landmarks[33].x
            left_eye_right = landmarks[133].x
            left_eye_top = landmarks[159].y
            left_eye_bottom = landmarks[145].y
            
            # Calcular límites del ojo derecho
            right_eye_left = landmarks[362].x
            right_eye_right = landmarks[263].x
            
            # Calcular ratio horizontal (0 = izquierda, 1 = derecha)
            left_h_ratio = (left_iris_x - left_eye_left) / (left_eye_right - left_eye_left + 1e-6)
            right_h_ratio = (right_iris_x - right_eye_left) / (right_eye_right - right_eye_left + 1e-6)
            h_ratio = (left_h_ratio + right_h_ratio) / 2
            
            # Calcular ratio vertical
            v_ratio = (left_iris_y - left_eye_top) / (left_eye_bottom - left_eye_top + 1e-6)
            
            self._gaze_ratio = (float(np.clip(h_ratio, 0, 1)), float(np.clip(v_ratio, 0, 1)))
            
            # Determinar dirección
            if h_ratio < 0.35:
                self._last_gaze_direction = "LEFT"
            elif h_ratio > 0.65:
                self._last_gaze_direction = "RIGHT"
            elif v_ratio < 0.3:
                self._last_gaze_direction = "UP"
            elif v_ratio > 0.7:
                self._last_gaze_direction = "DOWN"
            else:
                self._last_gaze_direction = "CENTER"
                
        except (IndexError, KeyError) as e:
            # Si faltan landmarks, mantener último valor
            pass
        
        return self._last_gaze_direction, self._gaze_ratio
    
    def get_target_monitor(self, num_monitors: int = 2) -> int:
        """
        Determina a qué monitor está mirando el usuario.
        
        Args:
            num_monitors: Número de monitores configurados
            
        Returns:
            int: Índice del monitor (0, 1, 2...)
        """
        h_ratio = self._gaze_ratio[0]
        
        if num_monitors == 1:
            return 0
        elif num_monitors == 2:
            return 0 if h_ratio < 0.5 else 1
        else:
            # Dividir proporcionalmente
            return min(int(h_ratio * num_monitors), num_monitors - 1)
    
    def is_looking_at_screen(self) -> bool:
        """Verifica si el usuario está mirando a la pantalla."""
        return self._last_gaze_direction == "CENTER"
