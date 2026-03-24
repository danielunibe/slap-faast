"""
Professional VFX System - Efectos visuales de nivel profesional
Incluye: Real Bloom, HDR Glow, Additive Blending, Post-Processing Pipeline
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from pathlib import Path
from collections import deque
import math


class BloomEffect:
    """
    Bloom/HDR real usando blur gaussiano en zonas brillantes.
    Técnica usada en motores de juegos AAA.
    """
    
    def __init__(self, threshold: int = 200, intensity: float = 0.8, 
                 blur_size: int = 21):
        self.threshold = threshold
        self.intensity = intensity
        self.blur_size = blur_size if blur_size % 2 == 1 else blur_size + 1
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Aplica bloom al frame."""
        # 1. Extraer zonas brillantes (threshold)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv)
        
        # Máscara de brillo
        _, bright_mask = cv2.threshold(v, self.threshold, 255, cv2.THRESH_BINARY)
        bright_areas = cv2.bitwise_and(frame, frame, mask=bright_mask)
        
        # 2. Blur las zonas brillantes (múltiples pasadas para suavidad)
        bloom = cv2.GaussianBlur(bright_areas, (self.blur_size, self.blur_size), 0)
        bloom = cv2.GaussianBlur(bloom, (self.blur_size * 2 + 1, self.blur_size * 2 + 1), 0)
        
        # 3. Additive blending
        result = cv2.addWeighted(frame, 1.0, bloom, self.intensity, 0)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class ColorGrading:
    """
    Color grading cinematográfico.
    Presets inspirados en películas.
    """
    
    PRESETS = {
        'cyberpunk': {
            'shadows': (20, 0, 40),      # Púrpura en sombras
            'midtones': (0, 10, 20),     # Cyan sutil
            'highlights': (0, 30, 40),   # Cyan/teal en highlights
            'contrast': 1.2,
            'saturation': 1.3
        },
        'blade_runner': {
            'shadows': (40, 20, 0),      # Naranja/ámbar en sombras
            'midtones': (20, 10, 0),
            'highlights': (0, 20, 30),   # Teal en highlights
            'contrast': 1.3,
            'saturation': 1.1
        },
        'matrix': {
            'shadows': (0, 20, 0),       # Verde en todo
            'midtones': (0, 15, 0),
            'highlights': (0, 30, 10),
            'contrast': 1.4,
            'saturation': 0.8
        },
        'tron': {
            'shadows': (50, 20, 0),      # Azul profundo
            'midtones': (40, 10, 0),
            'highlights': (60, 40, 20),  # Cyan brillante
            'contrast': 1.5,
            'saturation': 1.4
        }
    }
    
    def __init__(self, preset: str = 'cyberpunk'):
        self.set_preset(preset)
    
    def set_preset(self, preset: str):
        if preset in self.PRESETS:
            self.preset = preset
            self.settings = self.PRESETS[preset]
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Aplica color grading."""
        result = frame.astype(np.float32)
        
        # Crear máscaras por luminosidad
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        
        shadows_mask = np.clip(1.0 - gray * 3, 0, 1)
        highlights_mask = np.clip(gray * 3 - 2, 0, 1)
        midtones_mask = 1.0 - shadows_mask - highlights_mask
        
        # Aplicar tintes por zona
        for i, color in enumerate([
            self.settings['shadows'],
            self.settings['midtones'],
            self.settings['highlights']
        ]):
            mask = [shadows_mask, midtones_mask, highlights_mask][i]
            for c in range(3):
                result[:, :, c] += mask * color[c]
        
        # Contraste
        contrast = self.settings['contrast']
        result = (result - 128) * contrast + 128
        
        # Saturación
        hsv = cv2.cvtColor(np.clip(result, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= self.settings['saturation']
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return np.clip(result, 0, 255).astype(np.uint8)


class VignetteEffect:
    """Viñeta cinematográfica."""
    
    def __init__(self, intensity: float = 0.4):
        self.intensity = intensity
        self._cache = {}
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        cache_key = (h, w)
        
        if cache_key not in self._cache:
            # Crear máscara de viñeta
            X = np.arange(0, w)
            Y = np.arange(0, h)
            X, Y = np.meshgrid(X, Y)
            
            centerX, centerY = w // 2, h // 2
            
            # Distancia al centro normalizada
            dist = np.sqrt((X - centerX)**2 + (Y - centerY)**2)
            max_dist = np.sqrt(centerX**2 + centerY**2)
            dist = dist / max_dist
            
            # Curva de viñeta suave
            vignette = 1 - (dist ** 2) * self.intensity
            vignette = np.clip(vignette, 0.3, 1.0)
            
            self._cache[cache_key] = vignette[:, :, np.newaxis]
        
        return (frame * self._cache[cache_key]).astype(np.uint8)


class ChromaticAberration:
    """Aberración cromática sutil (efecto de lente)."""
    
    def __init__(self, offset: int = 2):
        self.offset = offset
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        
        # Separar canales
        b, g, r = cv2.split(frame)
        
        # Offset del canal rojo hacia afuera del centro
        M_r = np.float32([[1, 0, self.offset], [0, 1, 0]])
        r = cv2.warpAffine(r, M_r, (w, h))
        
        # Offset del canal azul en dirección opuesta
        M_b = np.float32([[1, 0, -self.offset], [0, 1, 0]])
        b = cv2.warpAffine(b, M_b, (w, h))
        
        return cv2.merge([b, g, r])


class ProfessionalTrails:
    """
    Trails profesionales con curvas Bezier y gradientes.
    """
    
    def __init__(self, max_length: int = 40, glow_layers: int = 5):
        self.max_length = max_length
        self.glow_layers = glow_layers
        self._trails: Dict[Tuple[int, int], deque] = {}
    
    def update(self, hand_idx: int, finger_idx: int, x: float, y: float):
        """Agrega punto al trail."""
        key = (hand_idx, finger_idx)
        if key not in self._trails:
            self._trails[key] = deque(maxlen=self.max_length)
        self._trails[key].append((x, y))
    
    def _bezier_curve(self, points: List[Tuple[float, float]], 
                      num_points: int = 50) -> List[Tuple[int, int]]:
        """Genera curva Bezier suave a través de los puntos."""
        if len(points) < 2:
            return [(int(p[0]), int(p[1])) for p in points]
        
        # Simplificar a curva cuadrática por segmentos
        result = []
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            
            # Punto de control en el medio
            if i + 2 < len(points):
                p2 = points[i + 2]
                ctrl = ((p0[0] + p1[0] + p2[0]) / 3, (p0[1] + p1[1] + p2[1]) / 3)
            else:
                ctrl = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            
            # Interpolar
            steps = max(2, num_points // len(points))
            for t in range(steps):
                t = t / steps
                # Bezier cuadrática
                x = (1-t)**2 * p0[0] + 2*(1-t)*t * ctrl[0] + t**2 * p1[0]
                y = (1-t)**2 * p0[1] + 2*(1-t)*t * ctrl[1] + t**2 * p1[1]
                result.append((int(x), int(y)))
        
        return result
    
    def render(self, frame: np.ndarray, color: Tuple[int, int, int]):
        """Renderiza todos los trails con glow profesional."""
        overlay = np.zeros_like(frame, dtype=np.float32)
        
        for key, trail in self._trails.items():
            if len(trail) < 2:
                continue
            
            points = list(trail)
            curve = self._bezier_curve(points)
            
            # Renderizar múltiples capas de glow
            for layer in range(self.glow_layers, 0, -1):
                alpha = (self.glow_layers - layer + 1) / self.glow_layers
                thickness = layer * 3
                layer_color = tuple(int(c * alpha * 0.5) for c in color)
                
                for i in range(1, len(curve)):
                    # Fade basado en posición
                    pos_alpha = i / len(curve)
                    final_color = tuple(int(c * pos_alpha) for c in layer_color)
                    
                    cv2.line(overlay, curve[i-1], curve[i], final_color, 
                            thickness, cv2.LINE_AA)
            
            # Core brillante
            for i in range(1, len(curve)):
                pos_alpha = i / len(curve)
                core_color = tuple(int(c * pos_alpha) for c in color)
                cv2.line(overlay, curve[i-1], curve[i], core_color, 2, cv2.LINE_AA)
        
        # Additive blend
        result = frame.astype(np.float32) + overlay
        return np.clip(result, 0, 255).astype(np.uint8)


class ProfessionalGlowOrb:
    """
    Orb con glow HDR profesional.
    Múltiples capas con falloff exponencial.
    """
    
    def __init__(self, base_radius: int = 30, layers: int = 8):
        self.base_radius = base_radius
        self.layers = layers
    
    def render(self, frame: np.ndarray, x: int, y: int, 
               color: Tuple[int, int, int], pulse: float = 1.0):
        """Renderiza orb con glow HDR."""
        overlay = np.zeros_like(frame, dtype=np.float32)
        
        # Múltiples capas con falloff exponencial
        for i in range(self.layers):
            layer_ratio = (self.layers - i) / self.layers
            radius = int(self.base_radius * (1 + (1 - layer_ratio) * 2) * pulse)
            
            # Intensidad exponencial
            intensity = math.exp(-3 * (1 - layer_ratio)) * 0.3
            layer_color = tuple(int(c * intensity) for c in color)
            
            cv2.circle(overlay, (x, y), radius, layer_color, -1, cv2.LINE_AA)
        
        # Core súper brillante
        core_radius = max(2, int(self.base_radius * 0.15 * pulse))
        cv2.circle(overlay, (x, y), core_radius, (255, 255, 255), -1, cv2.LINE_AA)
        
        # Additive blend
        result = frame.astype(np.float32) + overlay
        return np.clip(result, 0, 255).astype(np.uint8)


class ProfessionalVFX:
    """
    Sistema VFX profesional completo.
    Combina todos los efectos con pipeline de post-procesado.
    """
    
    FINGERTIPS = [4, 8, 12, 16, 20]
    
    # Colores profesionales (más saturados y vibrantes)
    COLORS = {
        'electric_blue': (255, 150, 50),
        'cyber_pink': (255, 50, 200),
        'neon_green': (50, 255, 100),
        'plasma_orange': (50, 150, 255),
        'quantum_white': (255, 255, 255),
    }
    
    def __init__(self, 
                 color_scheme: str = 'electric_blue',
                 enable_bloom: bool = True,
                 enable_grading: bool = True,
                 enable_vignette: bool = True,
                 enable_chromatic: bool = False,  # Sutil, opcional
                 grading_preset: str = 'cyberpunk'):
        
        self.color_scheme = color_scheme
        self.enabled = True
        self._frame_count = 0
        
        # Componentes
        self.bloom = BloomEffect(threshold=180, intensity=0.6) if enable_bloom else None
        self.grading = ColorGrading(grading_preset) if enable_grading else None
        self.vignette = VignetteEffect(0.3) if enable_vignette else None
        self.chromatic = ChromaticAberration(1) if enable_chromatic else None
        
        self.trails = ProfessionalTrails(max_length=35, glow_layers=6)
        self.orb = ProfessionalGlowOrb(base_radius=25, layers=10)
    
    def _get_color(self) -> Tuple[int, int, int]:
        return self.COLORS.get(self.color_scheme, self.COLORS['electric_blue'])
    
    def process_frame(self, frame: np.ndarray, hands: List) -> np.ndarray:
        """
        Procesa un frame completo con todos los efectos.
        
        Args:
            frame: Frame BGR original
            hands: Lista de hand_landmarks del wrapper
            
        Returns:
            Frame procesado con efectos VFX
        """
        if not self.enabled:
            return frame
        
        h, w = frame.shape[:2]
        color = self._get_color()
        
        # Oscurecer base para mejor contraste
        result = (frame * 0.3).astype(np.uint8)
        
        # Pulsación global
        pulse = 0.9 + 0.1 * math.sin(self._frame_count * 0.05)
        
        # Procesar cada mano
        for hand_idx, hand in enumerate(hands or []):
            if not hasattr(hand, 'landmark'):
                continue
            
            for finger_idx in self.FINGERTIPS:
                if finger_idx >= len(hand.landmark):
                    continue
                
                lm = hand.landmark[finger_idx]
                x, y = int(lm.x * w), int(lm.y * h)
                
                # Actualizar trail
                self.trails.update(hand_idx, finger_idx, x, y)
                
                # Renderizar orb
                result = self.orb.render(result, x, y, color, pulse)
        
        # Renderizar trails
        result = self.trails.render(result, color)
        
        # === POST-PROCESSING PIPELINE ===
        
        # 1. Bloom
        if self.bloom:
            result = self.bloom.apply(result)
        
        # 2. Color Grading
        if self.grading:
            result = self.grading.apply(result)
        
        # 3. Aberración cromática (sutil)
        if self.chromatic:
            result = self.chromatic.apply(result)
        
        # 4. Vignette (último)
        if self.vignette:
            result = self.vignette.apply(result)
        
        self._frame_count += 1
        return result
    
    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled
    
    def next_color(self) -> str:
        colors = list(self.COLORS.keys())
        idx = colors.index(self.color_scheme)
        self.color_scheme = colors[(idx + 1) % len(colors)]
        return self.color_scheme
    
    def next_grading(self) -> str:
        if self.grading:
            presets = list(ColorGrading.PRESETS.keys())
            idx = presets.index(self.grading.preset)
            new_preset = presets[(idx + 1) % len(presets)]
            self.grading.set_preset(new_preset)
            return new_preset
        return ""


# Test standalone
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from tracking.mediapipe_wrapper import MediaPipeWrapper
    
    print("=" * 50)
    print("PROFESSIONAL VFX SYSTEM TEST")
    print("=" * 50)
    
    # Crear VFX
    vfx = ProfessionalVFX(
        color_scheme='electric_blue',
        enable_bloom=True,
        enable_grading=True,
        enable_vignette=True,
        grading_preset='cyberpunk'
    )
    
    # Init MediaPipe
    wrapper = MediaPipeWrapper()
    hands = wrapper.create_hands(max_num_hands=2)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("[ERROR] No camera found")
        exit(1)
    
    print("\nControls:")
    print("  'c' = Change color")
    print("  'g' = Change grading preset")
    print("  'e' = Toggle effects")
    print("  'q' = Quit")
    print("\nShow your hands to the camera...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # Procesar con MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Aplicar VFX
        if results.multi_hand_landmarks:
            frame = vfx.process_frame(frame, results.multi_hand_landmarks)
        else:
            # Aplicar solo post-processing sin manos
            frame = vfx.process_frame(frame, [])
        
        # UI Info
        info = f"Color: {vfx.color_scheme}"
        if vfx.grading:
            info += f" | Grading: {vfx.grading.preset}"
        cv2.putText(frame, info, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        
        cv2.imshow('Professional VFX', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            print(f"Color: {vfx.next_color()}")
        elif key == ord('g'):
            print(f"Grading: {vfx.next_grading()}")
        elif key == ord('e'):
            vfx.toggle()
    
    cap.release()
    cv2.destroyAllWindows()
    wrapper.close_all()
    
    print("\n[OK] Test completed")
