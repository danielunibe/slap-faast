"""
Gesture Recognizer - Sistema de reconocimiento de gestos para Slap!Faast
Basado en MediaPipe hand landmarks con clasificación de gestos estáticos y dinámicos.
Inspirado en GRLib pero implementado directamente con MediaPipe.
"""
import numpy as np
from typing import Optional, List, Tuple, Dict
from loguru import logger
from enum import Enum

class StaticGesture(Enum):
    """Gestos estáticos reconocidos."""
    UNKNOWN = 0
    THUMBS_UP = 1
    THUMBS_DOWN = 2
    PEACE = 3
    OK = 4
    FIST = 5
    OPEN_PALM = 6  
    POINTING = 7
    ROCK = 8
    CALL_ME = 9

class DynamicGesture(Enum):
    """Gestos dinámicos reconocidos."""
    UNKNOWN = 0
    SWIPE_LEFT = 1
    SWIPE_RIGHT = 2
    SWIPE_UP = 3
    SWIPE_DOWN = 4
    WAVE = 5
    CIRCLE_CW = 6
    CIRCLE_CCW = 7

class GestureRecognizer:
    """
    Reconoce gestos de mano basado en landmarks de MediaPipe.
    Soporta gestos estáticos y dinámicos.
    """
    
    def __init__(self, 
                 confidence_threshold: float = 0.7,
                 buffer_size: int = 10):
        """
        Args:
            confidence_threshold: Umbral mínimo de confianza para reconocer gesto
            buffer_size: Tamaño del buffer para gestos dinámicos
        """
        self.confidence_threshold = confidence_threshold
        self.buffer_size = buffer_size
        
        # Buffer para gestos dinámicos (almacena posiciones de mano)
        self.position_buffer = []
        
        # Último gesto reconocido
        self.last_static_gesture = StaticGesture.UNKNOWN
        self.last_dynamic_gesture = DynamicGesture.UNKNOWN
        
        logger.info(f"GestureRecognizer inicializado (threshold={confidence_threshold})")
    
    def recognize_static(self, hand_landmarks) -> Tuple[StaticGesture, float]:
        """
        Reconoce gesto estático basado en la configuración de la mano.
        
        Args:
            hand_landmarks: Landmarks de MediaPipe (21 puntos)
            
        Returns:
            (gesto_reconocido, confianza)
        """
        if not hand_landmarks:
            return StaticGesture.UNKNOWN, 0.0
        
        # Extraer características de la mano
        fingers_extended = self._get_fingers_extended(hand_landmarks.landmark)
        angles = self._get_finger_angles(hand_landmarks.landmark)
        
        # Clasificar gesto basado en configuración de dedos
        gesture, confidence = self._classify_static_gesture(fingers_extended, angles)
        
        if confidence >= self.confidence_threshold:
            self.last_static_gesture = gesture
            return gesture, confidence
        
        return StaticGesture.UNKNOWN, confidence
    
    def recognize_dynamic(self, hand_landmarks) -> Tuple[DynamicGesture, float]:
        """
        Reconoce gesto dinámico basado en movimiento de la mano.
        
        Args:
            hand_landmarks: Landmarks de MediaPipe
            
        Returns:
            (gesto_reconocido, confianza)
        """
        if not hand_landmarks:
            return DynamicGesture.UNKNOWN, 0.0
        
        # Obtener posición de la muñeca (landmark 0)
        wrist = hand_landmarks.landmark[0]
        position = (wrist.x, wrist.y)
        
        # Añadir al buffer
        self.position_buffer.append(position)
        
        # Mantener tamaño del buffer
        if len(self.position_buffer) > self.buffer_size:
            self.position_buffer.pop(0)
        
        # Necesitamos buffer lleno para detectar gestos dinámicos
        if len(self.position_buffer) < self.buffer_size:
            return DynamicGesture.UNKNOWN, 0.0
        
        # Analizar trayectoria
        gesture, confidence = self._classify_dynamic_gesture(self.position_buffer)
        
        if confidence >= self.confidence_threshold:
            self.last_dynamic_gesture = gesture
            # Limpiar buffer después de detectar gesto
            self.position_buffer = []
            return gesture, confidence
        
        return DynamicGesture.UNKNOWN, confidence
    
    def _get_fingers_extended(self, landmarks) -> List[bool]:
        """
        Determina qué dedos están extendidos.
        
        Returns:
            Lista de 5 booleanos [pulgar, índice, medio, anular, meñique]
        """
        fingers = []
        
        # Landmarks de las puntas de los dedos
        # Pulgar: 4, Índice: 8, Medio: 12, Anular: 16, Meñique: 20
        finger_tips = [4, 8, 12, 16, 20]
        # Landmarks de las articulaciones medias
        finger_pips = [2, 6, 10, 14, 18]
        
        for i, (tip, pip) in enumerate(zip(finger_tips, finger_pips)):
            if i == 0:  # Pulgar (eje X más importante)
                fingers.append(landmarks[tip].x > landmarks[pip].x)
            else:  # Otros dedos (eje Y)
                fingers.append(landmarks[tip].y < landmarks[pip].y)
        
        return fingers
    
    def _get_finger_angles(self, landmarks) -> List[float]:
        """
        Calcula ángulos de flexión de dedos.
        
        Returns:
            Lista de 5 ángulos en grados
        """
        angles = []
        
        # Secuencias de landmarks para cada dedo
        finger_sequences = [
            [1, 2, 3, 4],    # Pulgar
            [5, 6, 7, 8],    # Índice
            [9, 10, 11, 12], # Medio
            [13, 14, 15, 16],# Anular
            [17, 18, 19, 20] # Meñique
        ]
        
        for sequence in finger_sequences:
            # Calcular ángulo en la articulación media (índice 1)
            p1 = np.array([landmarks[sequence[0]].x, landmarks[sequence[0]].y])
            p2 = np.array([landmarks[sequence[1]].x, landmarks[sequence[1]].y])
            p3 = np.array([landmarks[sequence[2]].x, landmarks[sequence[2]].y])
            
            angle = self._calculate_angle(p1, p2, p3)
            angles.append(angle)
        
        return angles
    
    def _calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calcula ángulo entre tres puntos."""
        v1 = p1 - p2
        v2 = p3 - p2
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def _classify_static_gesture(self, 
                                 fingers_extended: List[bool], 
                                 angles: List[float]) -> Tuple[StaticGesture, float]:
        """
        Clasifica gesto estático basado en configuración de dedos.
        
        Args:
            fingers_extended: [pulgar, índice, medio, anular, meñique]
            angles: Ángulos de flexión
            
        Returns:
            (gesto, confianza)
        """
        # Thumbs Up - Solo pulgar extendido
        if fingers_extended == [True, False, False, False, False]:
            return StaticGesture.THUMBS_UP, 0.95
        
        # Thumbs Down - Solo pulgar hacia abajo (invertir check)
        if not fingers_extended[0] and not any(fingers_extended[1:]):
            return StaticGesture.THUMBS_DOWN, 0.90
        
        # Peace - Índice y medio extendidos
        if fingers_extended == [False, True, True, False, False]:
            return StaticGesture.PEACE, 0.95
        
        # OK - Pulgar e índice tocándose, otros extendidos
        # Aproximación: pulgar no extendido, índice no extendido, otros sí
        if (not fingers_extended[0] and not fingers_extended[1] and 
            fingers_extended[2] and fingers_extended[3] and fingers_extended[4]):
            return StaticGesture.OK, 0.85
        
        # Fist - Todos los dedos cerrados
        if not any(fingers_extended):
            return StaticGesture.FIST, 0.95
        
        # Open Palm - Todos los dedos abiertos
        if all(fingers_extended):
            return StaticGesture.OPEN_PALM, 0.95
        
        # Pointing - Solo índice extendido
        if fingers_extended == [False, True, False, False, False]:
            return StaticGesture.POINTING, 0.95
        
        # Rock - Índice y meñique extendidos
        if fingers_extended == [False, True, False, False, True]:
            return StaticGesture.ROCK, 0.90
        
        # Call Me - Pulgar y meñique extendidos
        if fingers_extended == [True, False, False, False, True]:
            return StaticGesture.CALL_ME, 0.90
        
        return StaticGesture.UNKNOWN, 0.0
    
    def _classify_dynamic_gesture(self, 
                                  positions: List[Tuple[float, float]]) -> Tuple[DynamicGesture, float]:
        """
        Clasifica gesto dinámico basado en trayectoria de la mano.
        
        Args:
            positions: Lista de (x, y) posiciones de la muñeca
            
        Returns:
            (gesto, confianza)
        """
        if len(positions) < 2:
            return DynamicGesture.UNKNOWN, 0.0
        
        # Calcular deltas
        delta_x = positions[-1][0] - positions[0][0]
        delta_y = positions[-1][1] - positions[0][1]
        
        # Magnitud del movimiento
        magnitude = np.sqrt(delta_x**2 + delta_y**2)
        
        # Umbral mínimo de movimiento
        if magnitude < 0.15:  # Ajustar según resolución
            return DynamicGesture.UNKNOWN, 0.0
        
        # Swipes (movimientos lineales)
        angle = np.degrees(np.arctan2(delta_y, delta_x))
        
        # Swipe RIGHT
        if -30 < angle < 30:
            return DynamicGesture.SWIPE_RIGHT, min(0.95, magnitude * 2)
        
        # Swipe LEFT
        if 150 < abs(angle) < 180:
            return DynamicGesture.SWIPE_LEFT, min(0.95, magnitude * 2)
        
        # Swipe DOWN
        if 60 < angle < 120:
            return DynamicGesture.SWIPE_DOWN, min(0.90, magnitude * 2)
        
        # Swipe UP
        if -120 < angle < -60:
            return DynamicGesture.SWIPE_UP, min(0.90, magnitude * 2)
        
        # Wave - movimientos oscilatorios en X
        x_values = [p[0] for p in positions]
        if self._is_oscillating(x_values):
            return DynamicGesture.WAVE, 0.85
        
        # Círculos - detectar trayectoria circular
        circularity = self._calculate_circularity(positions)
        if circularity > 0.7:
            # Determinar dirección (CW vs CCW)
            is_cw = self._is_clockwise(positions)
            if is_cw:
                return DynamicGesture.CIRCLE_CW, circularity
            else:
                return DynamicGesture.CIRCLE_CCW, circularity
        
        return DynamicGesture.UNKNOWN, 0.0
    
    def _is_oscillating(self, values: List[float], min_oscillations: int = 2) -> bool:
        """Detecta si una serie de valores oscila."""
        if len(values) < 5:
            return False
        
        # Contar cambios de dirección
        direction_changes = 0
        for i in range(1, len(values) - 1):
            if (values[i] > values[i-1] and values[i] > values[i+1]) or \
               (values[i] < values[i-1] and values[i] < values[i+1]):
                direction_changes += 1
        
        return direction_changes >= min_oscillations
    
    def _calculate_circularity(self, positions: List[Tuple[float, float]]) -> float:
        """
        Calcula qué tan circular es una trayectoria (0-1).
        """
        if len(positions) < 4:
            return 0.0
        
        # Calcular centro de masa
        center_x = np.mean([p[0] for p in positions])
        center_y = np.mean([p[1] for p in positions])
        
        # Calcular distancias al centro
        distances = [np.sqrt((p[0] - center_x)**2 + (p[1] - center_y)**2) 
                    for p in positions]
        
        # Circularity = 1 - (std_dev / mean)
        # Más circular = desviación estándar menor
        mean_dist = np.mean(distances)
        std_dist = np.std(distances)
        
        if mean_dist < 0.01:  # Evitar división por cero
            return 0.0
        
        circularity = 1.0 - (std_dist / mean_dist)
        return max(0.0, min(1.0, circularity))
    
    def _is_clockwise(self, positions: List[Tuple[float, float]]) -> bool:
        """Determina si una trayectoria circular es clockwise."""
        if len(positions) < 3:
            return True
        
        # Calcular suma de ángulos (algoritmo de área)
        total_angle = 0
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            total_angle += (x2 - x1) * (y2 + y1)
        
        return total_angle > 0


# Test rápido
if __name__ == "__main__":
    import mediapipe as mp
    import cv2
    
    print("Testing Gesture Recognizer...")
    
    # Crear recognizer
    recognizer = GestureRecognizer()
    
    # Inicializar MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    
    # Capturar de webcam
    cap = cv2.VideoCapture(0)
    
    print("Muestra gestos a la cámara. Presiona 'q' para salir.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Procesar con MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Reconocer gestos
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Gesto estático
                static_gesture, static_conf = recognizer.recognize_static(hand_landmarks)
                
                # Gesto dinámico
                dynamic_gesture, dynamic_conf = recognizer.recognize_dynamic(hand_landmarks)
                
                # Mostrar en pantalla
                cv2.putText(frame, f"Static: {static_gesture.name} ({static_conf:.2f})", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Dynamic: {dynamic_gesture.name} ({dynamic_conf:.2f})", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # Dibujar landmarks
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        cv2.imshow('Gesture Recognizer Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    print("✅ Test completado")
