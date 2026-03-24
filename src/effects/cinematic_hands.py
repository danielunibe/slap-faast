"""
Cinematic Hand Effects - Efectos de cine para manos
Estilo Iron Man / Sci-Fi con trails luminosos, glow volumétrico y auras de energía.
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
from pathlib import Path
from collections import deque
import math


@dataclass
class TrailPoint:
    """Punto en un trail con posición y timestamp."""
    x: float
    y: float
    age: int = 0  # Frames desde creación


class CinematicHandEffects:
    """
    Sistema de efectos cinematográficos para manos.
    Incluye:
    - Glowing orbs en fingertips (estilo holográfico)
    - Light trails suaves (motion blur)
    - Energy connections entre dedos
    - Aura volumétrica en la palma
    """
    
    # Fingertip indices en MediaPipe
    FINGERTIPS = [4, 8, 12, 16, 20]
    PALM_CENTER = 0  # Wrist
    
    # Colores cinematográficos (BGR)
    COLORS = {
        'cyan': (255, 255, 0),      # Cyan brillante
        'magenta': (255, 0, 255),   # Magenta
        'gold': (0, 215, 255),      # Dorado
        'white': (255, 255, 255),   # Blanco puro
        'blue': (255, 100, 50),     # Azul eléctrico
    }
    
    def __init__(self,
                 trail_length: int = 25,
                 glow_radius: int = 35,
                 glow_intensity: float = 0.8,
                 enable_connections: bool = True,
                 color_scheme: str = 'cyan'):
        """
        Args:
            trail_length: Longitud del trail en frames
            glow_radius: Radio del glow en fingertips
            glow_intensity: Intensidad del glow (0-1)
            enable_connections: Mostrar conexiones de energía entre dedos
            color_scheme: Esquema de color ('cyan', 'magenta', 'gold', 'blue')
        """
        self.trail_length = trail_length
        self.glow_radius = glow_radius
        self.glow_intensity = glow_intensity
        self.enable_connections = enable_connections
        self.color_scheme = color_scheme
        self.enabled = True
        
        # Trails para cada fingertip: {(hand_idx, finger_idx): deque of TrailPoint}
        self._trails: Dict[Tuple[int, int], deque] = {}
        
        # Cache para glow precomputado
        self._glow_cache = {}
        
        # Frame counter para animaciones
        self._frame_count = 0
    
    def _get_color(self, finger_idx: int = 0) -> Tuple[int, int, int]:
        """Retorna color basado en esquema y dedo."""
        base = self.COLORS.get(self.color_scheme, self.COLORS['cyan'])
        # Variación sutil por dedo
        shift = (finger_idx * 10) % 30
        return tuple(min(255, c + shift) for c in base)
    
    def _create_glow_mask(self, radius: int, intensity: float = 1.0) -> np.ndarray:
        """Crea máscara de glow gaussiano precalculada."""
        cache_key = (radius, int(intensity * 100))
        if cache_key in self._glow_cache:
            return self._glow_cache[cache_key]
        
        size = radius * 2 + 1
        mask = np.zeros((size, size), dtype=np.float32)
        center = radius
        
        for y in range(size):
            for x in range(size):
                dist = math.sqrt((x - center)**2 + (y - center)**2)
                # Falloff exponencial suave
                if dist <= radius:
                    mask[y, x] = math.exp(-dist * 2.5 / radius) * intensity
        
        self._glow_cache[cache_key] = mask
        return mask
    
    def _draw_glow_orb(self, frame: np.ndarray, x: int, y: int, 
                       radius: int, color: Tuple[int, int, int], 
                       intensity: float = 1.0):
        """Dibuja un orb con glow volumétrico estilo holográfico."""
        h, w = frame.shape[:2]
        
        # Asegurar que estamos dentro del frame
        if x < 0 or x >= w or y < 0 or y >= h:
            return
        
        # Crear overlay para blending
        overlay = frame.copy()
        
        # Múltiples capas para efecto volumétrico
        layers = [
            (radius, 0.15),      # Capa exterior (glow difuso)
            (int(radius * 0.6), 0.3),   # Capa media
            (int(radius * 0.3), 0.6),   # Capa interior
            (int(radius * 0.15), 1.0),  # Core brillante
        ]
        
        for layer_radius, layer_intensity in layers:
            if layer_radius < 1:
                layer_radius = 1
            
            # Color con intensidad ajustada
            layer_color = tuple(int(c * layer_intensity * intensity) for c in color)
            
            # Dibujar círculo con anti-aliasing
            cv2.circle(overlay, (x, y), layer_radius, layer_color, -1, cv2.LINE_AA)
        
        # Blend suave
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Core blanco brillante (centro del orb)
        core_size = max(2, int(radius * 0.1))
        cv2.circle(frame, (x, y), core_size, (255, 255, 255), -1, cv2.LINE_AA)
    
    def _draw_light_trail(self, frame: np.ndarray, trail: deque, 
                          color: Tuple[int, int, int]):
        """Dibuja trail de luz con fade gradual."""
        if len(trail) < 2:
            return
        
        points = list(trail)
        
        for i in range(1, len(points)):
            # Calcular alpha basado en posición en el trail
            alpha = 1.0 - (i / len(points))
            alpha = alpha ** 0.5  # Curva más suave
            
            # Grosor decrece con la distancia
            thickness = max(1, int(8 * alpha))
            
            # Color con fade
            faded_color = tuple(int(c * alpha) for c in color)
            
            pt1 = (int(points[i-1].x), int(points[i-1].y))
            pt2 = (int(points[i].x), int(points[i].y))
            
            # Línea con anti-aliasing
            cv2.line(frame, pt1, pt2, faded_color, thickness, cv2.LINE_AA)
        
        # Glow en el trail (blur selectivo)
        # Solo si hay suficientes puntos
        if len(points) > 3:
            # Mini-glows en puntos intermedios
            for i in range(0, len(points), 3):
                alpha = 1.0 - (i / len(points))
                pt = points[i]
                glow_size = max(3, int(12 * alpha))
                glow_color = tuple(int(c * alpha * 0.5) for c in color)
                cv2.circle(frame, (int(pt.x), int(pt.y)), glow_size, 
                          glow_color, -1, cv2.LINE_AA)
    
    def _draw_energy_connections(self, frame: np.ndarray, 
                                  fingertip_positions: List[Tuple[int, int]],
                                  color: Tuple[int, int, int]):
        """Dibuja conexiones de energía entre fingertips."""
        if len(fingertip_positions) < 2:
            return
        
        # Pulsación basada en frame count
        pulse = 0.5 + 0.5 * math.sin(self._frame_count * 0.1)
        
        # Conectar fingertips adyacentes
        connections = [(0, 1), (1, 2), (2, 3), (3, 4)]  # Thumb-Index, Index-Middle, etc.
        
        for i, j in connections:
            if i < len(fingertip_positions) and j < len(fingertip_positions):
                pt1 = fingertip_positions[i]
                pt2 = fingertip_positions[j]
                
                # Color pulsante
                pulse_color = tuple(int(c * (0.3 + 0.4 * pulse)) for c in color)
                
                # Línea de energía con glow
                cv2.line(frame, pt1, pt2, pulse_color, 2, cv2.LINE_AA)
                
                # Puntos intermedios para efecto "energía"
                mid_x = (pt1[0] + pt2[0]) // 2
                mid_y = (pt1[1] + pt2[1]) // 2
                cv2.circle(frame, (mid_x, mid_y), 
                          int(4 * pulse), pulse_color, -1, cv2.LINE_AA)
    
    def _draw_palm_aura(self, frame: np.ndarray, palm_pos: Tuple[int, int],
                        color: Tuple[int, int, int]):
        """Dibuja aura de energía en la palma."""
        x, y = palm_pos
        
        # Múltiples anillos con glow
        pulse = 0.5 + 0.5 * math.sin(self._frame_count * 0.08)
        
        radii = [40, 55, 70]
        for i, r in enumerate(radii):
            alpha = 0.3 - (i * 0.08)
            ring_color = tuple(int(c * alpha * pulse) for c in color)
            cv2.circle(frame, (x, y), int(r * (0.9 + 0.1 * pulse)), 
                      ring_color, 2, cv2.LINE_AA)
    
    def process_hands(self, hands: List, frame_width: int, frame_height: int):
        """
        Procesa landmarks de manos y actualiza trails.
        
        Args:
            hands: Lista de hand_landmarks de MediaPipe (wrapper format)
            frame_width: Ancho del frame
            frame_height: Alto del frame
        """
        if not self.enabled or not hands:
            return
        
        for hand_idx, hand in enumerate(hands):
            if not hasattr(hand, 'landmark'):
                continue
            
            for finger_idx in self.FINGERTIPS:
                if finger_idx >= len(hand.landmark):
                    continue
                
                lm = hand.landmark[finger_idx]
                x = lm.x * frame_width
                y = lm.y * frame_height
                
                # Actualizar trail
                key = (hand_idx, finger_idx)
                if key not in self._trails:
                    self._trails[key] = deque(maxlen=self.trail_length)
                
                self._trails[key].append(TrailPoint(x, y))
        
        self._frame_count += 1
    
    def render(self, frame: np.ndarray, hands: List):
        """
        Renderiza todos los efectos sobre el frame.
        
        Args:
            frame: Frame BGR de OpenCV (modificado in-place)
            hands: Lista de hand_landmarks
        """
        if not self.enabled:
            return
        
        h, w = frame.shape[:2]
        color = self._get_color()
        
        for hand_idx, hand in enumerate(hands or []):
            if not hasattr(hand, 'landmark'):
                continue
            
            fingertip_positions = []
            
            # Procesar cada fingertip
            for finger_idx in self.FINGERTIPS:
                if finger_idx >= len(hand.landmark):
                    continue
                
                lm = hand.landmark[finger_idx]
                x, y = int(lm.x * w), int(lm.y * h)
                fingertip_positions.append((x, y))
                
                # 1. Dibujar trail
                key = (hand_idx, finger_idx)
                if key in self._trails:
                    self._draw_light_trail(frame, self._trails[key], color)
                
                # 2. Dibujar glow orb en fingertip
                self._draw_glow_orb(frame, x, y, self.glow_radius, color, 
                                   self.glow_intensity)
            
            # 3. Conexiones de energía entre dedos
            if self.enable_connections and len(fingertip_positions) >= 2:
                self._draw_energy_connections(frame, fingertip_positions, color)
            
            # 4. Aura en la palma
            if self.PALM_CENTER < len(hand.landmark):
                palm = hand.landmark[self.PALM_CENTER]
                palm_pos = (int(palm.x * w), int(palm.y * h))
                self._draw_palm_aura(frame, palm_pos, color)
    
    def toggle(self) -> bool:
        """Toggle on/off."""
        self.enabled = not self.enabled
        if not self.enabled:
            self._trails.clear()
        return self.enabled
    
    def set_color_scheme(self, scheme: str):
        """Cambia esquema de color."""
        if scheme in self.COLORS:
            self.color_scheme = scheme
    
    def next_color_scheme(self) -> str:
        """Cicla al siguiente esquema de color."""
        schemes = list(self.COLORS.keys())
        idx = schemes.index(self.color_scheme)
        self.color_scheme = schemes[(idx + 1) % len(schemes)]
        return self.color_scheme


# Test standalone
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from tracking.mediapipe_wrapper import MediaPipeWrapper
    
    print("Testing Cinematic Hand Effects...")
    
    # Crear sistema de efectos
    effects = CinematicHandEffects(
        trail_length=30,
        glow_radius=40,
        glow_intensity=0.9,
        enable_connections=True,
        color_scheme='cyan'
    )
    
    # Init MediaPipe
    wrapper = MediaPipeWrapper()
    hands_detector = wrapper.create_hands(max_num_hands=2)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir la camara")
        exit(1)
    
    print("[*] Muestra tus manos - Efecto cinematografico activo")
    print("    'c' = cambiar color, 'e' = toggle, 'q' = salir")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Oscurecer fondo para efecto más dramático
        frame = (frame * 0.4).astype(np.uint8)
        
        # Procesar con MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_detector.process(frame_rgb)
        
        # Procesar y renderizar efectos
        if results.multi_hand_landmarks:
            effects.process_hands(results.multi_hand_landmarks, w, h)
            effects.render(frame, results.multi_hand_landmarks)
        
        # Info
        cv2.putText(frame, f"Color: {effects.color_scheme.upper()}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Cinematic Hand Effects', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            new_color = effects.next_color_scheme()
            print(f"Color: {new_color}")
        elif key == ord('e'):
            effects.toggle()
    
    cap.release()
    cv2.destroyAllWindows()
    wrapper.close_all()
    
    print("[OK] Test completado")
