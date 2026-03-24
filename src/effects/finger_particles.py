"""
Finger Particle Effects - Sistema de partículas para fingertips
Inspirado en PointerParticles, adaptado para MediaPipe hand tracking.
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import random
import colorsys


@dataclass
class Particle:
    """Partícula individual que emana de un fingertip."""
    x: float
    y: float
    vx: float  # Velocidad X
    vy: float  # Velocidad Y
    size: float
    decay: float
    hue: float  # Color en HSV (0-360)
    
    def update(self) -> bool:
        """Actualiza la partícula. Retorna False si debe eliminarse."""
        self.x += self.vx * self.size
        self.y += self.vy * self.size
        self.size -= self.decay
        return self.size > 0.1
    
    def get_color_bgr(self) -> Tuple[int, int, int]:
        """Convierte HSV a BGR para OpenCV."""
        # HSV: hue 0-360, sat 0-1, val 0-1
        h = self.hue / 360.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.9, 0.8)
        return (int(b * 255), int(g * 255), int(r * 255))


class FingerParticleSystem:
    """
    Sistema de partículas que emana de los fingertips detectados.
    Compatible con MediaPipe hand landmarks.
    """
    
    # Índices de fingertips en MediaPipe (puntas de dedos)
    FINGERTIP_INDICES = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    
    # Colores por dedo (hue values 0-360)
    FINGER_HUES = {
        4: 60,    # Pulgar - Amarillo
        8: 300,   # Índice - Magenta
        12: 120,  # Medio - Verde
        16: 200,  # Anular - Cyan
        20: 30    # Meñique - Naranja
    }
    
    def __init__(self, 
                 particles_per_finger: int = 5,
                 spread: float = 3.0,
                 speed: float = 2.0,
                 decay: float = 0.03,
                 max_particles: int = 500):
        """
        Args:
            particles_per_finger: Partículas a crear por dedo por frame
            spread: Dispersión de partículas
            speed: Velocidad base de partículas
            decay: Tasa de decaimiento del tamaño
            max_particles: Límite de partículas activas
        """
        self.particles: List[Particle] = []
        self.particles_per_finger = particles_per_finger
        self.spread = spread
        self.speed = speed
        self.decay = decay
        self.max_particles = max_particles
        self.hue_offset = 0  # Para efecto arcoíris gradual
        self.enabled = True
        
        # Posiciones anteriores para calcular velocidad
        self._prev_positions = {}
    
    def create_particles_at(self, x: float, y: float, finger_idx: int, 
                           velocity: Tuple[float, float] = (0, 0)):
        """Crea partículas en una posición dada."""
        if not self.enabled:
            return
            
        # Limitar partículas
        if len(self.particles) >= self.max_particles:
            return
        
        vx, vy = velocity
        base_hue = self.FINGER_HUES.get(finger_idx, 0) + self.hue_offset
        
        for _ in range(self.particles_per_finger):
            # Dispersión aleatoria
            spread_x = (random.random() - 0.5) * self.spread - vx * 0.1
            spread_y = (random.random() - 0.5) * self.spread - vy * 0.1
            
            particle = Particle(
                x=x,
                y=y,
                vx=spread_x * self.speed * 0.08,
                vy=spread_y * self.speed * 0.08,
                size=random.random() * 2 + 1,
                decay=self.decay,
                hue=(base_hue + random.random() * 20) % 360
            )
            self.particles.append(particle)
    
    def process_hands(self, hands: List, frame_width: int, frame_height: int):
        """
        Procesa landmarks de manos y crea partículas en los fingertips.
        
        Args:
            hands: Lista de hand_landmarks de MediaPipe
            frame_width: Ancho del frame
            frame_height: Alto del frame
        """
        if not self.enabled or not hands:
            return
        
        for hand_idx, hand in enumerate(hands):
            if not hasattr(hand, 'landmark'):
                continue
                
            for finger_idx in self.FINGERTIP_INDICES:
                if finger_idx >= len(hand.landmark):
                    continue
                    
                lm = hand.landmark[finger_idx]
                x = lm.x * frame_width
                y = lm.y * frame_height
                
                # Calcular velocidad basada en posición anterior
                key = (hand_idx, finger_idx)
                velocity = (0.0, 0.0)
                
                if key in self._prev_positions:
                    prev_x, prev_y = self._prev_positions[key]
                    velocity = (x - prev_x, y - prev_y)
                
                self._prev_positions[key] = (x, y)
                
                # Crear partículas
                self.create_particles_at(x, y, finger_idx, velocity)
        
        # Actualizar hue para efecto arcoíris
        self.hue_offset = (self.hue_offset + 1) % 360
    
    def update_and_draw(self, frame: np.ndarray):
        """
        Actualiza todas las partículas y las dibuja en el frame.
        
        Args:
            frame: Frame BGR de OpenCV (modificado in-place)
        """
        if not self.enabled:
            return
        
        # Actualizar y filtrar partículas muertas
        alive_particles = []
        
        for particle in self.particles:
            if particle.update():
                alive_particles.append(particle)
                
                # Dibujar partícula
                x, y = int(particle.x), int(particle.y)
                size = max(1, int(particle.size))
                color = particle.get_color_bgr()
                
                cv2.circle(frame, (x, y), size, color, -1)
                
                # Glow effect (círculo más grande y transparente)
                if size > 1:
                    cv2.circle(frame, (x, y), size + 2, color, 1)
        
        self.particles = alive_particles
    
    def clear(self):
        """Elimina todas las partículas."""
        self.particles.clear()
        self._prev_positions.clear()
    
    def toggle(self) -> bool:
        """Activa/desactiva el sistema. Retorna nuevo estado."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.clear()
        return self.enabled
    
    def set_intensity(self, intensity: float):
        """
        Ajusta la intensidad del efecto (0.0 a 2.0).
        1.0 = normal, 0.5 = sutil, 2.0 = intenso
        """
        intensity = max(0.1, min(2.0, intensity))
        self.particles_per_finger = int(5 * intensity)
        self.spread = 3.0 * intensity
        self.decay = 0.03 / intensity


# Test standalone
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from tracking.mediapipe_wrapper import MediaPipeWrapper
    
    print("Testing Finger Particle System...")
    
    # Crear sistema de partículas
    particle_system = FingerParticleSystem(
        particles_per_finger=8,
        spread=4.0,
        speed=2.5
    )
    
    # Init MediaPipe con wrapper
    wrapper = MediaPipeWrapper()
    hands = wrapper.create_hands(max_num_hands=2)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la camara")
        exit(1)
    
    print("[*] Muestra tus manos a la camara. Presiona 'q' para salir.")
    print("   Presiona 'e' para toggle efectos, '+'/'-' para intensidad.")
    
    intensity = 1.0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # Mirror
        h, w = frame.shape[:2]
        
        # Procesar con MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Procesar manos y crear partículas
        if results.multi_hand_landmarks:
            particle_system.process_hands(results.multi_hand_landmarks, w, h)
        
        # Actualizar y dibujar partículas
        particle_system.update_and_draw(frame)
        
        # Info
        status = "ON" if particle_system.enabled else "OFF"
        cv2.putText(frame, f"Particles: {len(particle_system.particles)} | Effects: {status}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Intensity: {intensity:.1f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Finger Particles Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            particle_system.toggle()
        elif key == ord('+') or key == ord('='):
            intensity = min(2.0, intensity + 0.1)
            particle_system.set_intensity(intensity)
        elif key == ord('-'):
            intensity = max(0.1, intensity - 0.1)
            particle_system.set_intensity(intensity)
    
    cap.release()
    cv2.destroyAllWindows()
    wrapper.close_all()
    
    print("[OK] Test completado")
