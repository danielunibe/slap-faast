"""
GestureTrainer - LSTM-based Custom Gesture Training
Permite entrenar gestos personalizados usando secuencias de landmarks.
"""
import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from loguru import logger
from collections import deque
import time

# TensorFlow imports (lazy load para no bloquear si no está instalado)
tf = None
Sequential = None
LSTM = None
Dense = None
Dropout = None


def _ensure_tensorflow():
    """Carga TensorFlow de forma lazy."""
    global tf, Sequential, LSTM, Dense, Dropout
    if tf is None:
        try:
            import tensorflow as _tf
            from tensorflow.keras.models import Sequential as _Sequential
            from tensorflow.keras.layers import LSTM as _LSTM, Dense as _Dense, Dropout as _Dropout
            tf = _tf
            Sequential = _Sequential
            LSTM = _LSTM
            Dense = _Dense
            Dropout = _Dropout
            logger.info("TensorFlow cargado correctamente.")
        except ImportError:
            logger.error("TensorFlow no está instalado. Ejecuta: pip install tensorflow")
            raise


class GestureTrainer:
    """
    Sistema de entrenamiento y reconocimiento de gestos personalizados.
    Usa LSTM para clasificar secuencias temporales de landmarks.
    """
    
    SEQUENCE_LENGTH = 30  # Frames por secuencia
    NUM_HAND_LANDMARKS = 21
    COORDS_PER_LANDMARK = 3  # x, y, z
    
    def __init__(self, gestures_dir: str = "models/gestures"):
        self._gestures_dir = gestures_dir
        self._model = None
        self._gesture_names: List[str] = []
        self._current_sequence: deque = deque(maxlen=self.SEQUENCE_LENGTH)
        self._is_recording = False
        self._recorded_sequences: Dict[str, List[np.ndarray]] = {}
        
        os.makedirs(gestures_dir, exist_ok=True)
        self._load_gesture_names()
    
    def _load_gesture_names(self):
        """Carga nombres de gestos desde el directorio."""
        names_file = os.path.join(self._gestures_dir, "gesture_names.json")
        if os.path.exists(names_file):
            with open(names_file, 'r') as f:
                self._gesture_names = json.load(f)
            logger.info(f"Gestos cargados: {self._gesture_names}")
    
    def _save_gesture_names(self):
        """Guarda nombres de gestos."""
        names_file = os.path.join(self._gestures_dir, "gesture_names.json")
        with open(names_file, 'w') as f:
            json.dump(self._gesture_names, f)
    
    def _extract_hand_features(self, hand_landmarks) -> np.ndarray:
        """
        Extrae características normalizadas de una mano.
        Normaliza posiciones relativas al punto 0 (muñeca).
        """
        if hand_landmarks is None:
            return np.zeros(self.NUM_HAND_LANDMARKS * self.COORDS_PER_LANDMARK)
        
        # Obtener landmarks
        landmarks = hand_landmarks.landmark
        wrist = landmarks[0]
        
        features = []
        for lm in landmarks:
            # Normalizar respecto a la muñeca
            features.extend([
                lm.x - wrist.x,
                lm.y - wrist.y,
                lm.z - wrist.z
            ])
        
        return np.array(features)
    
    def add_gesture(self, name: str):
        """Agrega un nuevo gesto al sistema."""
        if name not in self._gesture_names:
            self._gesture_names.append(name)
            self._recorded_sequences[name] = []
            self._save_gesture_names()
            logger.info(f"Gesto '{name}' agregado.")
    
    def start_recording(self, gesture_name: str):
        """Inicia grabación de samples para un gesto."""
        if gesture_name not in self._gesture_names:
            self.add_gesture(gesture_name)
        self._is_recording = True
        self._current_sequence.clear()
        logger.info(f"Grabando gesto: {gesture_name}")
    
    def stop_recording(self, gesture_name: str) -> int:
        """Detiene grabación y guarda la secuencia."""
        self._is_recording = False
        
        if len(self._current_sequence) >= self.SEQUENCE_LENGTH:
            sequence = np.array(list(self._current_sequence))
            if gesture_name not in self._recorded_sequences:
                self._recorded_sequences[gesture_name] = []
            self._recorded_sequences[gesture_name].append(sequence)
            count = len(self._recorded_sequences[gesture_name])
            logger.info(f"Secuencia guardada para '{gesture_name}'. Total: {count}")
            return count
        else:
            logger.warning("Secuencia muy corta, no guardada.")
            return 0
    
    def feed_frame(self, left_hand, right_hand):
        """
        Alimenta un frame al sistema.
        Extrae features y los agrega a la secuencia actual.
        """
        # Usar mano derecha por defecto, o izquierda si no hay derecha
        hand = right_hand if right_hand else left_hand
        features = self._extract_hand_features(hand)
        self._current_sequence.append(features)
    
    def save_dataset(self):
        """Guarda el dataset de entrenamiento."""
        dataset_file = os.path.join(self._gestures_dir, "dataset.npz")
        
        X = []
        y = []
        for gesture_idx, gesture_name in enumerate(self._gesture_names):
            sequences = self._recorded_sequences.get(gesture_name, [])
            for seq in sequences:
                X.append(seq)
                y.append(gesture_idx)
        
        if X:
            np.savez(dataset_file, X=np.array(X), y=np.array(y))
            logger.info(f"Dataset guardado: {len(X)} secuencias.")
        else:
            logger.warning("No hay datos para guardar.")
    
    def load_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """Carga el dataset de entrenamiento."""
        dataset_file = os.path.join(self._gestures_dir, "dataset.npz")
        if os.path.exists(dataset_file):
            data = np.load(dataset_file)
            return data['X'], data['y']
        return np.array([]), np.array([])
    
    def build_model(self):
        """Construye el modelo LSTM."""
        _ensure_tensorflow()
        
        input_shape = (self.SEQUENCE_LENGTH, self.NUM_HAND_LANDMARKS * self.COORDS_PER_LANDMARK)
        num_classes = len(self._gesture_names)
        
        self._model = Sequential([
            LSTM(64, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        
        self._model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info(f"Modelo LSTM construido. Clases: {num_classes}")
        return self._model
    
    def train(self, epochs: int = 50, validation_split: float = 0.2):
        """Entrena el modelo con el dataset guardado."""
        _ensure_tensorflow()
        
        X, y = self.load_dataset()
        if len(X) == 0:
            logger.error("No hay datos de entrenamiento.")
            return None
        
        if self._model is None:
            self.build_model()
        
        logger.info(f"Entrenando con {len(X)} muestras...")
        history = self._model.fit(
            X, y,
            epochs=epochs,
            validation_split=validation_split,
            verbose=1
        )
        
        # Guardar modelo
        model_path = os.path.join(self._gestures_dir, "gesture_model.keras")
        self._model.save(model_path)
        logger.success(f"Modelo guardado en: {model_path}")
        
        return history
    
    def load_model(self):
        """Carga modelo entrenado."""
        _ensure_tensorflow()
        
        model_path = os.path.join(self._gestures_dir, "gesture_model.keras")
        if os.path.exists(model_path):
            self._model = tf.keras.models.load_model(model_path)
            logger.info("Modelo de gestos cargado.")
            return True
        return False
    
    def predict(self) -> Optional[Tuple[str, float]]:
        """
        Predice el gesto actual basándose en la secuencia acumulada.
        Retorna (nombre_gesto, confianza) o None.
        """
        if self._model is None:
            return None
        
        if len(self._current_sequence) < self.SEQUENCE_LENGTH:
            return None
        
        sequence = np.array(list(self._current_sequence))
        sequence = np.expand_dims(sequence, axis=0)
        
        predictions = self._model.predict(sequence, verbose=0)
        gesture_idx = np.argmax(predictions[0])
        confidence = predictions[0][gesture_idx]
        
        if confidence > 0.7:  # Umbral de confianza
            return self._gesture_names[gesture_idx], float(confidence)
        
        return None
    
    def get_gesture_count(self, gesture_name: str) -> int:
        """Retorna cantidad de samples para un gesto."""
        return len(self._recorded_sequences.get(gesture_name, []))
