"""
Configuration Core - Xbox Theme & System Settings
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ColorPalette:
    """Xbox Gaming Theme - Neon Green Aesthetic."""
    # Core Theme Colors
    XBOX_GREEN: str = "#9bf00b"      # Xbox Neon Green (Primary Accent)
    XBOX_DARK_GREEN: str = "#107C10" # Xbox Dark Green
    
    # Backgrounds
    BACKGROUND: str = "#050505"      # Pure Black Background
    PANEL_BG: str = "#0f0f0f"        # Panel Background
    CARD_BG: str = "#0a0a0a"         # Card Background
    
    # UI Elements
    PRIMARY: str = "#9bf00b"         # Neon Green (Main Accent)
    SECONDARY: str = "#FFFFFF"       # White (Secondary)
    ACCENT: str = "#9bf00b"          # Neon Green Highlight
    BORDER: str = "rgba(255, 255, 255, 0.1)"  # Subtle Border
    BORDER_GLOW: str = "rgba(155, 240, 11, 0.3)"  # Green Glow Border
    
    # Status Colors
    SUCCESS: str = "#9bf00b"         # Green Success
    ALERT: str = "#FF3300"           # Red Alert
    WARNING: str = "#FFAA00"         # Orange Warning
    ONLINE: str = "#9bf00b"          # Online Status
    
    # Text
    TEXT_MAIN: str = "#FFFFFF"       # White Text
    TEXT_DIM: str = "#666666"        # Dim Gray Text
    TEXT_DARKER: str = "#333333"     # Darker Gray
    
    # Effects
    GLOW: str = "rgba(155, 240, 11, 0.2)"  # Neon Glow Effect
    OVERLAY_BG: str = "rgba(10, 10, 10, 0.9)"  # Dark Overlay

@dataclass
class TrackingConfig:
    """Configuración de tracking."""
    MIN_DETECTION_CONFIDENCE: float = 0.5
    MIN_TRACKING_CONFIDENCE: float = 0.5
    MODEL_COMPLEXITY: int = 0
    SMOOTHING_BETA: float = 0.8
    SMOOTHING_CUTOFF: float = 0.05

@dataclass
class SystemConfig:
    """Configuración general del sistema."""
    APP_NAME: str = "Slap!Faast"
    VERSION: str = "0.9.5 (God Mode)"
    WINDOW_SIZE: tuple = (1280, 720)
    # Rutas
    VOSK_MODEL_PATH: str = "models/model"
    LOG_FILE: str = "ethyria.log"
    CAMERA_INDEX: int = 1 # 0=Webcam/Laptop, 1=Kinect/External (Prefered)
    USE_KINECT: bool = True # Intentar usar driver nativo de Kinect
    STRICT_KINECT_MODE: bool = True # CRITICAL: Fail if Kinect not found (don't use webcam)
    FULLSCREEN: bool = False
    DEBUG_MODE: bool = True

class Config:
    """Acceso global a la configuración."""
    COLORS = ColorPalette()
    TRACKING = TrackingConfig()
    SYSTEM = SystemConfig()
