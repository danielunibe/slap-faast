"""
GPU-Accelerated VFX System - Efectos con Shaders GLSL
Rendering en GPU usando ModernGL para efectos de nivel AAA.
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from collections import deque
import math

# GPU Libraries
import moderngl
import glfw


# ============== GLSL SHADERS ==============

VERTEX_SHADER = """
#version 330 core

in vec2 in_position;
in vec2 in_texcoord;

out vec2 v_texcoord;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    v_texcoord = in_texcoord;
}
"""

# Bloom shader - extrae highlights y aplica blur
BLOOM_SHADER = """
#version 330 core

uniform sampler2D u_texture;
uniform float u_threshold;
uniform float u_intensity;
uniform vec2 u_direction;  // (1,0) for horizontal, (0,1) for vertical

in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    vec4 color = texture(u_texture, v_texcoord);
    
    // Calcular luminancia
    float luminance = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    
    // Extraer solo partes brillantes
    if (luminance < u_threshold) {
        color.rgb *= 0.0;
    }
    
    // Gaussian blur
    vec2 tex_offset = 1.0 / textureSize(u_texture, 0);
    vec3 result = color.rgb * 0.227027;
    
    for (int i = 1; i < 5; ++i) {
        float weight = 0.1945946 / float(i);
        vec2 offset = u_direction * tex_offset * float(i) * 2.0;
        result += texture(u_texture, v_texcoord + offset).rgb * weight;
        result += texture(u_texture, v_texcoord - offset).rgb * weight;
    }
    
    fragColor = vec4(result * u_intensity, 1.0);
}
"""

# Glow Orb shader - renderiza orbes con falloff suave
GLOW_SHADER = """
#version 330 core

uniform vec2 u_center;
uniform vec3 u_color;
uniform float u_radius;
uniform float u_intensity;
uniform vec2 u_resolution;

in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    vec2 uv = v_texcoord * u_resolution;
    float dist = length(uv - u_center);
    
    // Falloff exponencial suave
    float glow = exp(-dist * 3.0 / u_radius) * u_intensity;
    
    // Core brillante
    float core = smoothstep(u_radius * 0.1, 0.0, dist);
    
    vec3 color = u_color * glow + vec3(1.0) * core * 0.5;
    
    fragColor = vec4(color, glow + core);
}
"""

# Color Grading shader
COLOR_GRADING_SHADER = """
#version 330 core

uniform sampler2D u_texture;
uniform vec3 u_shadows_tint;
uniform vec3 u_highlights_tint;
uniform float u_contrast;
uniform float u_saturation;
uniform float u_vignette;

in vec2 v_texcoord;
out vec4 fragColor;

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec3 color = texture(u_texture, v_texcoord).rgb;
    
    // Luminancia para split toning
    float luma = dot(color, vec3(0.299, 0.587, 0.114));
    
    // Split toning (sombras y highlights)
    vec3 shadows = mix(color, u_shadows_tint, (1.0 - luma) * 0.3);
    vec3 highlights = mix(shadows, u_highlights_tint, luma * 0.3);
    color = highlights;
    
    // Contraste
    color = (color - 0.5) * u_contrast + 0.5;
    
    // Saturación
    vec3 hsv = rgb2hsv(color);
    hsv.y *= u_saturation;
    color = hsv2rgb(hsv);
    
    // Vignette
    vec2 uv = v_texcoord * 2.0 - 1.0;
    float vignette = 1.0 - dot(uv, uv) * u_vignette;
    color *= vignette;
    
    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
"""

# Composite shader - combina todas las capas
COMPOSITE_SHADER = """
#version 330 core

uniform sampler2D u_base;
uniform sampler2D u_bloom;
uniform sampler2D u_effects;
uniform float u_bloom_intensity;

in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    vec3 base = texture(u_base, v_texcoord).rgb;
    vec3 bloom = texture(u_bloom, v_texcoord).rgb;
    vec4 effects = texture(u_effects, v_texcoord);
    
    // Additive blending para bloom
    vec3 result = base + bloom * u_bloom_intensity;
    
    // Alpha blending para effects
    result = mix(result, effects.rgb, effects.a);
    
    // Tonemapping simple (Reinhard)
    result = result / (result + vec3(1.0));
    
    // Gamma correction
    result = pow(result, vec3(1.0/2.2));
    
    fragColor = vec4(result, 1.0);
}
"""


class GPUContext:
    """Contexto OpenGL headless para rendering."""
    
    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        self.ctx = None
        self._initialized = False
        
    def initialize(self):
        """Inicializa contexto OpenGL."""
        if self._initialized:
            return
            
        # Crear contexto standalone (headless)
        self.ctx = moderngl.create_standalone_context()
        self._initialized = True
        print(f"[GPU] OpenGL: {self.ctx.info['GL_VERSION']}")
        print(f"[GPU] Renderer: {self.ctx.info['GL_RENDERER']}")
    
    def create_texture(self, width: int, height: int) -> moderngl.Texture:
        """Crea textura GPU."""
        return self.ctx.texture((width, height), 3, dtype='f1')
    
    def create_framebuffer(self, texture: moderngl.Texture) -> moderngl.Framebuffer:
        """Crea framebuffer para render-to-texture."""
        return self.ctx.framebuffer(color_attachments=[texture])
    
    def release(self):
        if self.ctx:
            self.ctx.release()


class GPUVFXSystem:
    """
    Sistema VFX acelerado por GPU.
    Usa shaders GLSL para efectos en tiempo real.
    """
    
    FINGERTIPS = [4, 8, 12, 16, 20]
    
    COLORS = {
        'electric_cyan': (0.2, 0.9, 1.0),
        'neon_pink': (1.0, 0.2, 0.8),
        'plasma_gold': (1.0, 0.8, 0.2),
        'quantum_blue': (0.2, 0.4, 1.0),
    }
    
    def __init__(self, 
                 width: int = 640, 
                 height: int = 480,
                 color_scheme: str = 'electric_cyan'):
        
        self.width = width
        self.height = height
        self.color_scheme = color_scheme
        self.enabled = True
        self._frame_count = 0
        
        # GPU Context
        self.gpu = GPUContext(width, height)
        self._shaders_compiled = False
        
        # Trail data
        self._trails: Dict[Tuple[int, int], deque] = {}
        self._trail_max_len = 30
    
    def _compile_shaders(self):
        """Compila todos los shaders."""
        if self._shaders_compiled:
            return
        
        ctx = self.gpu.ctx
        
        # Quad para fullscreen rendering
        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 1.0,
        ], dtype='f4')
        
        self._quad_vbo = ctx.buffer(vertices)
        
        # Bloom shader
        self._bloom_prog = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=BLOOM_SHADER
        )
        self._bloom_vao = ctx.vertex_array(
            self._bloom_prog,
            [(self._quad_vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # Color grading shader
        self._grading_prog = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=COLOR_GRADING_SHADER
        )
        self._grading_vao = ctx.vertex_array(
            self._grading_prog,
            [(self._quad_vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # Composite shader
        self._composite_prog = ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=COMPOSITE_SHADER
        )
        self._composite_vao = ctx.vertex_array(
            self._composite_prog,
            [(self._quad_vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
        
        # Crear texturas y framebuffers
        self._tex_input = ctx.texture((self.width, self.height), 3, dtype='f1')
        self._tex_bloom = ctx.texture((self.width, self.height), 3, dtype='f1')
        self._tex_output = ctx.texture((self.width, self.height), 3, dtype='f1')
        
        self._fb_bloom = ctx.framebuffer(color_attachments=[self._tex_bloom])
        self._fb_output = ctx.framebuffer(color_attachments=[self._tex_output])
        
        self._shaders_compiled = True
        print("[GPU] Shaders compiled successfully")
    
    def initialize(self):
        """Inicializa el sistema GPU."""
        self.gpu.initialize()
        self._compile_shaders()
    
    def _update_trails(self, hands: List, w: int, h: int):
        """Actualiza trails de dedos."""
        for hand_idx, hand in enumerate(hands or []):
            if not hasattr(hand, 'landmark'):
                continue
            
            for finger_idx in self.FINGERTIPS:
                if finger_idx >= len(hand.landmark):
                    continue
                
                lm = hand.landmark[finger_idx]
                x, y = lm.x * w, lm.y * h
                
                key = (hand_idx, finger_idx)
                if key not in self._trails:
                    self._trails[key] = deque(maxlen=self._trail_max_len)
                self._trails[key].append((x, y))
    
    def _render_trails_cpu(self, frame: np.ndarray, color: Tuple[float, ...]):
        """Renderiza trails (CPU fallback para combinar con GPU effects)."""
        h, w = frame.shape[:2]
        overlay = np.zeros_like(frame, dtype=np.float32)
        
        bgr_color = (int(color[2]*255), int(color[1]*255), int(color[0]*255))
        
        for key, trail in self._trails.items():
            if len(trail) < 2:
                continue
            
            points = list(trail)
            for i in range(1, len(points)):
                alpha = i / len(points)
                thickness = max(1, int(6 * alpha))
                layer_color = tuple(int(c * alpha) for c in bgr_color)
                
                pt1 = (int(points[i-1][0]), int(points[i-1][1]))
                pt2 = (int(points[i][0]), int(points[i][1]))
                cv2.line(overlay, pt1, pt2, layer_color, thickness, cv2.LINE_AA)
        
        # Glow orbs en fingertips
        for key, trail in self._trails.items():
            if trail:
                x, y = int(trail[-1][0]), int(trail[-1][1])
                
                # Múltiples capas de glow
                for radius in [35, 25, 15, 8, 3]:
                    intensity = 1.0 - (radius / 35.0) * 0.7
                    glow_color = tuple(int(c * intensity) for c in bgr_color)
                    cv2.circle(overlay, (x, y), radius, glow_color, -1, cv2.LINE_AA)
                
                # Core blanco
                cv2.circle(overlay, (x, y), 2, (255, 255, 255), -1, cv2.LINE_AA)
        
        # Additive blend
        result = frame.astype(np.float32) + overlay
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _apply_gpu_postprocess(self, frame: np.ndarray) -> np.ndarray:
        """Aplica post-processing GPU."""
        ctx = self.gpu.ctx
        h, w = frame.shape[:2]
        
        # Resize si es necesario
        if w != self.width or h != self.height:
            frame_resized = cv2.resize(frame, (self.width, self.height))
        else:
            frame_resized = frame
        
        # Upload a GPU
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        self._tex_input.write(frame_rgb.tobytes())
        
        # === BLOOM PASS ===
        self._fb_bloom.use()
        self._tex_input.use(0)
        self._bloom_prog['u_texture'] = 0
        self._bloom_prog['u_threshold'] = 0.6
        self._bloom_prog['u_intensity'] = 0.8
        self._bloom_prog['u_direction'] = (1.0, 0.0)  # Horizontal
        self._bloom_vao.render(moderngl.TRIANGLE_STRIP)
        
        # === COLOR GRADING PASS ===
        self._fb_output.use()
        self._tex_bloom.use(0)
        self._grading_prog['u_texture'] = 0
        self._grading_prog['u_shadows_tint'] = (0.1, 0.0, 0.2)  # Purple shadows
        self._grading_prog['u_highlights_tint'] = (0.0, 0.3, 0.4)  # Cyan highlights
        self._grading_prog['u_contrast'] = 1.2
        self._grading_prog['u_saturation'] = 1.3
        self._grading_prog['u_vignette'] = 0.3
        self._grading_vao.render(moderngl.TRIANGLE_STRIP)
        
        # Read back
        result_bytes = self._tex_output.read()
        result = np.frombuffer(result_bytes, dtype=np.uint8).reshape(self.height, self.width, 3)
        result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
        
        # Resize back si es necesario
        if w != self.width or h != self.height:
            result = cv2.resize(result, (w, h))
        
        return result
    
    def process_frame(self, frame: np.ndarray, hands: List) -> np.ndarray:
        """Procesa frame con efectos GPU."""
        if not self.enabled:
            return frame
        
        h, w = frame.shape[:2]
        color = self.COLORS.get(self.color_scheme, self.COLORS['electric_cyan'])
        
        # Oscurecer base
        result = (frame * 0.3).astype(np.uint8)
        
        # Update trails
        self._update_trails(hands, w, h)
        
        # Render trails y orbs (CPU por ahora para simplicidad)
        result = self._render_trails_cpu(result, color)
        
        # GPU post-processing
        try:
            result = self._apply_gpu_postprocess(result)
        except Exception as e:
            print(f"[GPU] Fallback to CPU: {e}")
        
        self._frame_count += 1
        return result
    
    def next_color(self) -> str:
        colors = list(self.COLORS.keys())
        idx = colors.index(self.color_scheme)
        self.color_scheme = colors[(idx + 1) % len(colors)]
        return self.color_scheme
    
    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled
    
    def release(self):
        self.gpu.release()


# Test standalone
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from tracking.mediapipe_wrapper import MediaPipeWrapper
    
    print("=" * 50)
    print("GPU-ACCELERATED VFX SYSTEM")
    print("=" * 50)
    
    # Crear VFX
    vfx = GPUVFXSystem(
        width=640,
        height=480,
        color_scheme='electric_cyan'
    )
    
    try:
        vfx.initialize()
    except Exception as e:
        print(f"[ERROR] GPU init failed: {e}")
        print("[INFO] Falling back to CPU-only mode")
    
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
    print("  'e' = Toggle effects")
    print("  'q' = Quit")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # GPU VFX
        hand_list = results.multi_hand_landmarks if results.multi_hand_landmarks else []
        frame = vfx.process_frame(frame, hand_list)
        
        # Info
        cv2.putText(frame, f"GPU VFX | Color: {vfx.color_scheme}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('GPU VFX System', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            print(f"Color: {vfx.next_color()}")
        elif key == ord('e'):
            vfx.toggle()
    
    cap.release()
    cv2.destroyAllWindows()
    vfx.release()
    wrapper.close_all()
    
    print("\n[OK] Test completed")
