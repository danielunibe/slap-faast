"""
Tema Visual Tony Stark para Slap!Faast v2.0
Basado exactamente en los mockups originales con estilo Metro UI Xbox 360
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class TileConfig:
    """Configuración de un tile Metro UI"""
    id: str
    title: str
    icon: str
    color: str
    size: str  # 'large', 'medium', 'small', 'wide'
    position: Tuple[int, int]  # (row, col)
    span: Tuple[int, int]  # (rows, cols)
    action: str
    description: str
    enabled: bool = True
    animated: bool = False
    live_data: bool = False

@dataclass
class ColorPalette:
    """Paleta de colores Tony Stark / Iron Man"""
    # Colores principales basados en mockups
    primary_blue: str = "#1E90FF"      # Azul principal tiles
    kinect_blue: str = "#4169E1"       # Azul sensor Kinect
    success_green: str = "#32CD32"     # Verde gestos
    action_teal: str = "#20B2AA"       # Teal acciones
    config_orange: str = "#FF8C00"     # Naranja configuración
    stats_cyan: str = "#00CED1"        # Cyan estadísticas
    help_gray: str = "#708090"         # Gris ayuda
    
    # Colores Iron Man adicionales
    arc_reactor_blue: str = "#00D4FF"  # Azul Arc Reactor
    iron_red: str = "#DC143C"          # Rojo Iron Man
    gold_accent: str = "#FFD700"       # Dorado acentos
    
    # Colores de fondo y texto
    background_dark: str = "#2D2D30"   # Fondo oscuro principal
    background_darker: str = "#1E1E1E" # Fondo más oscuro
    text_primary: str = "#FFFFFF"      # Texto principal
    text_secondary: str = "#CCCCCC"    # Texto secundario
    text_accent: str = "#00D4FF"       # Texto acento
    
    # Estados y feedback
    success: str = "#00FF00"           # Verde éxito
    warning: str = "#FFA500"           # Naranja advertencia
    error: str = "#FF4500"             # Rojo error
    info: str = "#87CEEB"              # Azul información
    
    # Efectos y transparencias
    overlay_dark: str = "rgba(0, 0, 0, 0.7)"
    overlay_light: str = "rgba(255, 255, 255, 0.1)"
    glow_blue: str = "rgba(0, 212, 255, 0.5)"
    glow_gold: str = "rgba(255, 215, 0, 0.3)"

class TonyStarkTheme:
    """Tema visual completo estilo Tony Stark / Iron Man"""
    
    def __init__(self):
        self.colors = ColorPalette()
        self.tiles_config = self._create_tiles_config()
        self.animations = self._create_animations()
        self.effects = self._create_effects()
        self.typography = self._create_typography()
        self.layouts = self._create_layouts()
        
        # Configuración de tema
        self.theme_config = {
            'name': 'Tony Stark',
            'version': '2.0',
            'description': 'Tema visual estilo Iron Man basado en Metro UI Xbox 360',
            'author': 'Slap!Faast Team',
            'enable_animations': True,
            'enable_glow_effects': True,
            'enable_particles': False,  # Para futuras mejoras
            'enable_sound_effects': True,
            'tile_hover_delay': 0.2,
            'animation_duration': 0.3,
            'glow_intensity': 0.6
        }
    
    def _create_tiles_config(self) -> List[TileConfig]:
        """Crea configuración de tiles basada en mockups"""
        return [
            # Tile principal - Sensor Kinect (grande, arriba izquierda)
            TileConfig(
                id="sensor_status",
                title="Sensor Kinect",
                icon="🎮",  # Será reemplazado por icono skeleton
                color=self.colors.kinect_blue,
                size="large",
                position=(0, 0),
                span=(2, 2),
                action="show_sensor_details",
                description="Estado del sensor Kinect y información de conexión",
                live_data=True,
                animated=True
            ),
            
            # Tile skeleton preview (grande, arriba derecha)
            TileConfig(
                id="skeleton_preview",
                title="Vista Esqueleto",
                icon="🦴",  # Será reemplazado por skeleton visual
                color=self.colors.primary_blue,
                size="large",
                position=(0, 2),
                span=(2, 2),
                action="show_skeleton_preview",
                description="Vista en tiempo real del esqueleto detectado",
                live_data=True,
                animated=True
            ),
            
            # Fila inferior - 4 tiles medianos
            TileConfig(
                id="gestos",
                title="Gestos",
                icon="✋",
                color=self.colors.success_green,
                size="medium",
                position=(2, 0),
                span=(1, 1),
                action="open_gestures_manager",
                description="Gestión y entrenamiento de gestos personalizados"
            ),
            
            TileConfig(
                id="acciones",
                title="Acciones",
                icon="⚡",
                color=self.colors.action_teal,
                size="medium",
                position=(2, 1),
                span=(1, 1),
                action="open_actions_manager",
                description="Configuración de mapeos de gestos a acciones"
            ),
            
            TileConfig(
                id="perfiles",
                title="Perfiles",
                icon="👤",
                color=self.colors.success_green,
                size="medium",
                position=(2, 2),
                span=(1, 1),
                action="open_profiles_manager",
                description="Gestión de perfiles de usuario"
            ),
            
            TileConfig(
                id="configuracion",
                title="Configuración",
                icon="⚙️",
                color=self.colors.config_orange,
                size="medium",
                position=(2, 3),
                span=(1, 1),
                action="open_settings",
                description="Ajustes del sistema y preferencias"
            ),
            
            # Fila inferior - tiles adicionales
            TileConfig(
                id="estadisticas",
                title="Estadísticas",
                icon="📊",
                color=self.colors.stats_cyan,
                size="wide",
                position=(3, 0),
                span=(1, 2),
                action="open_statistics",
                description="Métricas de uso y rendimiento del sistema",
                live_data=True
            ),
            
            TileConfig(
                id="ayuda",
                title="Ayuda",
                icon="❓",
                color=self.colors.help_gray,
                size="medium",
                position=(3, 2),
                span=(1, 1),
                action="open_help",
                description="Tutoriales y documentación"
            ),
            
            TileConfig(
                id="ia_status",
                title="IA Tony Stark",
                icon="🤖",
                color=self.colors.arc_reactor_blue,
                size="medium",
                position=(3, 3),
                span=(1, 1),
                action="show_ai_status",
                description="Estado del sistema de IA local",
                live_data=True,
                animated=True
            )
        ]
    
    def _create_animations(self) -> Dict[str, str]:
        """Crea animaciones CSS estilo Tony Stark"""
        return {
            'tile_hover': """
                @keyframes tile-hover {
                    0% { transform: scale(1) translateZ(0); box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
                    100% { transform: scale(1.05) translateZ(10px); box-shadow: 0 8px 25px rgba(0,212,255,0.4); }
                }
            """,
            
            'arc_reactor_pulse': """
                @keyframes arc-reactor-pulse {
                    0% { box-shadow: 0 0 5px rgba(0,212,255,0.5); }
                    50% { box-shadow: 0 0 20px rgba(0,212,255,0.8), 0 0 30px rgba(0,212,255,0.6); }
                    100% { box-shadow: 0 0 5px rgba(0,212,255,0.5); }
                }
            """,
            
            'skeleton_glow': """
                @keyframes skeleton-glow {
                    0% { filter: drop-shadow(0 0 5px rgba(255,255,255,0.5)); }
                    50% { filter: drop-shadow(0 0 15px rgba(0,212,255,0.8)); }
                    100% { filter: drop-shadow(0 0 5px rgba(255,255,255,0.5)); }
                }
            """,
            
            'data_stream': """
                @keyframes data-stream {
                    0% { opacity: 0.3; transform: translateY(0); }
                    50% { opacity: 1; transform: translateY(-5px); }
                    100% { opacity: 0.3; transform: translateY(0); }
                }
            """,
            
            'tile_appear': """
                @keyframes tile-appear {
                    0% { opacity: 0; transform: scale(0.8) rotateY(-90deg); }
                    100% { opacity: 1; transform: scale(1) rotateY(0deg); }
                }
            """,
            
            'status_blink': """
                @keyframes status-blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.3; }
                }
            """,
            
            'hologram_flicker': """
                @keyframes hologram-flicker {
                    0%, 100% { opacity: 1; filter: hue-rotate(0deg); }
                    25% { opacity: 0.8; filter: hue-rotate(90deg); }
                    50% { opacity: 0.9; filter: hue-rotate(180deg); }
                    75% { opacity: 0.85; filter: hue-rotate(270deg); }
                }
            """
        }
    
    def _create_effects(self) -> Dict[str, str]:
        """Crea efectos visuales estilo Iron Man"""
        return {
            'glow_border': f"""
                border: 2px solid transparent;
                background: linear-gradient({self.colors.background_dark}, {self.colors.background_dark}) padding-box,
                           linear-gradient(45deg, {self.colors.arc_reactor_blue}, {self.colors.gold_accent}) border-box;
            """,
            
            'arc_reactor_glow': f"""
                box-shadow: 
                    0 0 10px {self.colors.glow_blue},
                    inset 0 0 10px {self.colors.glow_blue},
                    0 0 20px {self.colors.glow_blue},
                    0 0 40px {self.colors.glow_blue};
            """,
            
            'holographic_overlay': f"""
                background: linear-gradient(
                    135deg,
                    rgba(0, 212, 255, 0.1) 0%,
                    rgba(255, 215, 0, 0.05) 50%,
                    rgba(0, 212, 255, 0.1) 100%
                );
                backdrop-filter: blur(1px);
            """,
            
            'metal_gradient': f"""
                background: linear-gradient(
                    145deg,
                    {self.colors.background_darker} 0%,
                    {self.colors.background_dark} 25%,
                    rgba(255, 215, 0, 0.1) 50%,
                    {self.colors.background_dark} 75%,
                    {self.colors.background_darker} 100%
                );
            """,
            
            'energy_border': f"""
                border: 1px solid {self.colors.arc_reactor_blue};
                box-shadow: 
                    0 0 5px {self.colors.glow_blue},
                    inset 0 0 5px {self.colors.glow_blue};
            """,
            
            'glass_morphism': f"""
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            """
        }
    
    def _create_typography(self) -> Dict[str, str]:
        """Crea tipografía estilo futurista"""
        return {
            'font_family_primary': "'Segoe UI', 'Roboto', 'Arial', sans-serif",
            'font_family_display': "'Orbitron', 'Segoe UI', monospace",
            'font_family_mono': "'Consolas', 'Monaco', monospace",
            
            'font_size_hero': '48px',
            'font_size_title': '36px',
            'font_size_subtitle': '24px',
            'font_size_body': '16px',
            'font_size_caption': '14px',
            'font_size_small': '12px',
            
            'font_weight_light': '300',
            'font_weight_normal': '400',
            'font_weight_medium': '500',
            'font_weight_bold': '700',
            
            'line_height_tight': '1.2',
            'line_height_normal': '1.5',
            'line_height_loose': '1.8',
            
            'letter_spacing_tight': '-0.5px',
            'letter_spacing_normal': '0px',
            'letter_spacing_wide': '1px'
        }
    
    def _create_layouts(self) -> Dict[str, Any]:
        """Crea layouts responsivos"""
        return {
            'dashboard_grid': {
                'columns': 4,
                'rows': 4,
                'gap': '16px',
                'padding': '24px',
                'min_tile_size': '200px',
                'max_width': '1400px'
            },
            
            'tile_sizes': {
                'small': {'width': '200px', 'height': '200px'},
                'medium': {'width': '200px', 'height': '200px'},
                'large': {'width': '416px', 'height': '416px'},
                'wide': {'width': '416px', 'height': '200px'},
                'tall': {'width': '200px', 'height': '416px'}
            },
            
            'breakpoints': {
                'mobile': '768px',
                'tablet': '1024px',
                'desktop': '1200px',
                'large': '1600px'
            },
            
            'spacing': {
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px',
                'xxl': '48px'
            }
        }
    
    def get_complete_css(self) -> str:
        """Genera CSS completo del tema Tony Stark"""
        css_parts = [
            self._get_base_styles(),
            self._get_tile_styles(),
            self._get_animation_styles(),
            self._get_component_styles(),
            self._get_responsive_styles(),
            self._get_utility_classes()
        ]
        
        return '\n\n'.join(css_parts)
    
    def _get_base_styles(self) -> str:
        """Estilos base del tema"""
        return f"""
/* ===== TONY STARK THEME - BASE STYLES ===== */

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: {self.typography['font_family_primary']};
    background: {self.colors.background_darker};
    color: {self.colors.text_primary};
    overflow-x: hidden;
    line-height: {self.typography['line_height_normal']};
}}

.tony-stark-app {{
    background: linear-gradient(
        135deg,
        {self.colors.background_darker} 0%,
        {self.colors.background_dark} 50%,
        {self.colors.background_darker} 100%
    );
    min-height: 100vh;
    position: relative;
}}

.tony-stark-app::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 215, 0, 0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}}

/* Scrollbars estilo Tony Stark */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: {self.colors.background_darker};
}}

::-webkit-scrollbar-thumb {{
    background: linear-gradient(
        45deg,
        {self.colors.arc_reactor_blue},
        {self.colors.gold_accent}
    );
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: linear-gradient(
        45deg,
        {self.colors.gold_accent},
        {self.colors.arc_reactor_blue}
    );
}}
"""
    
    def _get_tile_styles(self) -> str:
        """Estilos de tiles Metro UI"""
        return f"""
/* ===== TILES METRO UI TONY STARK ===== */

.dashboard-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(4, auto);
    gap: {self.layouts['dashboard_grid']['gap']};
    padding: {self.layouts['dashboard_grid']['padding']};
    max-width: {self.layouts['dashboard_grid']['max_width']};
    margin: 0 auto;
    min-height: 100vh;
}}

.tile {{
    background: {self.colors.background_dark};
    border-radius: 8px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 200px;
}}

.tile::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.05) 0%,
        transparent 50%,
        rgba(0, 212, 255, 0.05) 100%
    );
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}}

.tile:hover {{
    transform: scale(1.02) translateZ(10px);
    box-shadow: 
        0 8px 25px rgba(0, 0, 0, 0.3),
        0 0 20px rgba(0, 212, 255, 0.3);
    border-color: {self.colors.arc_reactor_blue};
}}

.tile:hover::before {{
    opacity: 1;
}}

.tile:active {{
    transform: scale(0.98);
    transition: transform 0.1s ease;
}}

/* Tamaños de tiles */
.tile-large {{
    grid-column: span 2;
    grid-row: span 2;
    min-height: 416px;
}}

.tile-wide {{
    grid-column: span 2;
    grid-row: span 1;
    min-height: 200px;
}}

.tile-tall {{
    grid-column: span 1;
    grid-row: span 2;
    min-height: 416px;
}}

.tile-medium {{
    grid-column: span 1;
    grid-row: span 1;
    min-height: 200px;
}}

/* Colores específicos de tiles */
.tile-kinect-blue {{
    background: linear-gradient(135deg, {self.colors.kinect_blue} 0%, rgba(65, 105, 225, 0.8) 100%);
}}

.tile-primary-blue {{
    background: linear-gradient(135deg, {self.colors.primary_blue} 0%, rgba(30, 144, 255, 0.8) 100%);
}}

.tile-success-green {{
    background: linear-gradient(135deg, {self.colors.success_green} 0%, rgba(50, 205, 50, 0.8) 100%);
}}

.tile-action-teal {{
    background: linear-gradient(135deg, {self.colors.action_teal} 0%, rgba(32, 178, 170, 0.8) 100%);
}}

.tile-config-orange {{
    background: linear-gradient(135deg, {self.colors.config_orange} 0%, rgba(255, 140, 0, 0.8) 100%);
}}

.tile-stats-cyan {{
    background: linear-gradient(135deg, {self.colors.stats_cyan} 0%, rgba(0, 206, 209, 0.8) 100%);
}}

.tile-help-gray {{
    background: linear-gradient(135deg, {self.colors.help_gray} 0%, rgba(112, 128, 144, 0.8) 100%);
}}

.tile-arc-reactor {{
    background: linear-gradient(135deg, {self.colors.arc_reactor_blue} 0%, rgba(0, 212, 255, 0.8) 100%);
    animation: arc-reactor-pulse 2s ease-in-out infinite;
}}

/* Contenido de tiles */
.tile-header {{
    display: flex;
    align-items: center;
    margin-bottom: 16px;
}}

.tile-icon {{
    font-size: 32px;
    margin-right: 12px;
    filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.5));
}}

.tile-title {{
    font-size: {self.typography['font_size_subtitle']};
    font-weight: {self.typography['font_weight_bold']};
    color: {self.colors.text_primary};
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}}

.tile-subtitle {{
    font-size: {self.typography['font_size_body']};
    color: {self.colors.text_secondary};
    margin-top: 4px;
}}

.tile-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}}

.tile-footer {{
    margin-top: auto;
    padding-top: 16px;
}}

.tile-description {{
    font-size: {self.typography['font_size_caption']};
    color: {self.colors.text_secondary};
    line-height: {self.typography['line_height_tight']};
}}

/* Tiles con datos en vivo */
.tile-live-data {{
    position: relative;
}}

.tile-live-data::after {{
    content: '';
    position: absolute;
    top: 8px;
    right: 8px;
    width: 8px;
    height: 8px;
    background: {self.colors.success};
    border-radius: 50%;
    animation: status-blink 2s ease-in-out infinite;
}}

/* Tiles animados */
.tile-animated {{
    animation: tile-appear 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}}

.tile-animated:nth-child(1) {{ animation-delay: 0.1s; }}
.tile-animated:nth-child(2) {{ animation-delay: 0.2s; }}
.tile-animated:nth-child(3) {{ animation-delay: 0.3s; }}
.tile-animated:nth-child(4) {{ animation-delay: 0.4s; }}
.tile-animated:nth-child(5) {{ animation-delay: 0.5s; }}
.tile-animated:nth-child(6) {{ animation-delay: 0.6s; }}
.tile-animated:nth-child(7) {{ animation-delay: 0.7s; }}
.tile-animated:nth-child(8) {{ animation-delay: 0.8s; }}
"""
    
    def _get_animation_styles(self) -> str:
        """Estilos de animaciones"""
        animations_css = "/* ===== ANIMACIONES TONY STARK ===== */\n\n"
        
        for name, animation in self.animations.items():
            animations_css += f"{animation}\n\n"
        
        return animations_css
    
    def _get_component_styles(self) -> str:
        """Estilos de componentes específicos"""
        return f"""
/* ===== COMPONENTES ESPECÍFICOS ===== */

/* Sensor Status */
.sensor-status {{
    text-align: center;
}}

.sensor-icon {{
    font-size: 64px;
    margin-bottom: 16px;
    animation: skeleton-glow 3s ease-in-out infinite;
}}

.sensor-title {{
    font-size: {self.typography['font_size_title']};
    font-weight: {self.typography['font_weight_bold']};
    margin-bottom: 8px;
}}

.sensor-subtitle {{
    font-size: {self.typography['font_size_body']};
    color: {self.colors.text_secondary};
}}

.connection-status {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 6px 12px;
    background: rgba(0, 255, 0, 0.2);
    border: 1px solid {self.colors.success};
    border-radius: 20px;
    font-size: {self.typography['font_size_caption']};
}}

.connection-status.disconnected {{
    background: rgba(255, 0, 0, 0.2);
    border-color: {self.colors.error};
}}

.connection-indicator {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {self.colors.success};
    animation: status-blink 1.5s ease-in-out infinite;
}}

.connection-indicator.disconnected {{
    background: {self.colors.error};
}}

/* Skeleton Preview */
.skeleton-preview {{
    position: relative;
    width: 100%;
    height: 300px;
    background: radial-gradient(
        circle at center,
        rgba(0, 212, 255, 0.1) 0%,
        transparent 70%
    );
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.skeleton-figure {{
    width: 120px;
    height: 200px;
    position: relative;
    filter: drop-shadow(0 0 10px {self.colors.arc_reactor_blue});
}}

.skeleton-joint {{
    position: absolute;
    width: 8px;
    height: 8px;
    background: {self.colors.arc_reactor_blue};
    border-radius: 50%;
    box-shadow: 0 0 10px {self.colors.glow_blue};
    animation: data-stream 2s ease-in-out infinite;
}}

.skeleton-bone {{
    position: absolute;
    background: linear-gradient(
        90deg,
        transparent 0%,
        {self.colors.arc_reactor_blue} 50%,
        transparent 100%
    );
    height: 2px;
    box-shadow: 0 0 5px {self.colors.glow_blue};
}}

/* Estadísticas en vivo */
.live-stats {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    height: 100%;
}}

.stat-item {{
    text-align: center;
    padding: 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}}

.stat-value {{
    font-size: {self.typography['font_size_subtitle']};
    font-weight: {self.typography['font_weight_bold']};
    color: {self.colors.arc_reactor_blue};
    text-shadow: 0 0 10px {self.colors.glow_blue};
}}

.stat-label {{
    font-size: {self.typography['font_size_caption']};
    color: {self.colors.text_secondary};
    margin-top: 4px;
}}

/* IA Status */
.ai-status {{
    text-align: center;
    position: relative;
}}

.ai-brain {{
    font-size: 48px;
    margin-bottom: 12px;
    animation: hologram-flicker 4s ease-in-out infinite;
}}

.ai-capabilities {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    justify-content: center;
    margin-top: 12px;
}}

.capability-badge {{
    padding: 2px 6px;
    background: rgba(0, 212, 255, 0.2);
    border: 1px solid {self.colors.arc_reactor_blue};
    border-radius: 10px;
    font-size: 10px;
    color: {self.colors.text_primary};
}}

/* Botones estilo Tony Stark */
.btn-stark {{
    background: linear-gradient(
        135deg,
        {self.colors.arc_reactor_blue} 0%,
        {self.colors.gold_accent} 100%
    );
    border: none;
    color: {self.colors.background_dark};
    padding: 12px 24px;
    border-radius: 6px;
    font-weight: {self.typography['font_weight_bold']};
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
    position: relative;
    overflow: hidden;
}}

.btn-stark::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.3),
        transparent
    );
    transition: left 0.5s ease;
}}

.btn-stark:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
}}

.btn-stark:hover::before {{
    left: 100%;
}}

.btn-stark:active {{
    transform: translateY(0);
}}

/* Indicadores de estado */
.status-indicator {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: {self.typography['font_size_small']};
    font-weight: {self.typography['font_weight_medium']};
}}

.status-online {{
    background: rgba(0, 255, 0, 0.2);
    color: {self.colors.success};
    border: 1px solid {self.colors.success};
}}

.status-offline {{
    background: rgba(255, 0, 0, 0.2);
    color: {self.colors.error};
    border: 1px solid {self.colors.error};
}}

.status-processing {{
    background: rgba(255, 165, 0, 0.2);
    color: {self.colors.warning};
    border: 1px solid {self.colors.warning};
}}

.status-ready {{
    background: rgba(0, 212, 255, 0.2);
    color: {self.colors.arc_reactor_blue};
    border: 1px solid {self.colors.arc_reactor_blue};
}}
"""
    
    def _get_responsive_styles(self) -> str:
        """Estilos responsivos"""
        return f"""
/* ===== RESPONSIVE DESIGN ===== */

@media (max-width: {self.layouts['breakpoints']['tablet']}) {{
    .dashboard-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        padding: 16px;
    }}
    
    .tile-large {{
        grid-column: span 2;
        grid-row: span 1;
        min-height: 200px;
    }}
    
    .tile-wide {{
        grid-column: span 2;
        grid-row: span 1;
    }}
    
    .tile-tall {{
        grid-column: span 1;
        grid-row: span 1;
        min-height: 200px;
    }}
    
    .tile-title {{
        font-size: {self.typography['font_size_body']};
    }}
    
    .tile-icon {{
        font-size: 24px;
    }}
}}

@media (max-width: {self.layouts['breakpoints']['mobile']}) {{
    .dashboard-grid {{
        grid-template-columns: 1fr;
        gap: 8px;
        padding: 12px;
    }}
    
    .tile {{
        min-height: 150px;
        padding: 16px;
    }}
    
    .tile-large,
    .tile-wide,
    .tile-tall,
    .tile-medium {{
        grid-column: span 1;
        grid-row: span 1;
        min-height: 150px;
    }}
    
    .sensor-icon {{
        font-size: 48px;
    }}
    
    .skeleton-preview {{
        height: 200px;
    }}
    
    .live-stats {{
        grid-template-columns: 1fr;
        gap: 8px;
    }}
}}

@media (min-width: {self.layouts['breakpoints']['large']}) {{
    .dashboard-grid {{
        grid-template-columns: repeat(6, 1fr);
        gap: 20px;
        padding: 32px;
    }}
    
    .tile-large {{
        grid-column: span 3;
        grid-row: span 2;
        min-height: 500px;
    }}
    
    .tile-wide {{
        grid-column: span 3;
        grid-row: span 1;
    }}
}}
"""
    
    def _get_utility_classes(self) -> str:
        """Clases de utilidad"""
        return f"""
/* ===== UTILITY CLASSES ===== */

/* Espaciado */
.m-0 {{ margin: 0; }}
.m-1 {{ margin: {self.layouts['spacing']['xs']}; }}
.m-2 {{ margin: {self.layouts['spacing']['sm']}; }}
.m-3 {{ margin: {self.layouts['spacing']['md']}; }}
.m-4 {{ margin: {self.layouts['spacing']['lg']}; }}
.m-5 {{ margin: {self.layouts['spacing']['xl']}; }}

.p-0 {{ padding: 0; }}
.p-1 {{ padding: {self.layouts['spacing']['xs']}; }}
.p-2 {{ padding: {self.layouts['spacing']['sm']}; }}
.p-3 {{ padding: {self.layouts['spacing']['md']}; }}
.p-4 {{ padding: {self.layouts['spacing']['lg']}; }}
.p-5 {{ padding: {self.layouts['spacing']['xl']}; }}

/* Texto */
.text-primary {{ color: {self.colors.text_primary}; }}
.text-secondary {{ color: {self.colors.text_secondary}; }}
.text-accent {{ color: {self.colors.text_accent}; }}
.text-success {{ color: {self.colors.success}; }}
.text-warning {{ color: {self.colors.warning}; }}
.text-error {{ color: {self.colors.error}; }}

.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}

.font-light {{ font-weight: {self.typography['font_weight_light']}; }}
.font-normal {{ font-weight: {self.typography['font_weight_normal']}; }}
.font-medium {{ font-weight: {self.typography['font_weight_medium']}; }}
.font-bold {{ font-weight: {self.typography['font_weight_bold']}; }}

/* Flexbox */
.flex {{ display: flex; }}
.flex-col {{ flex-direction: column; }}
.flex-row {{ flex-direction: row; }}
.items-center {{ align-items: center; }}
.items-start {{ align-items: flex-start; }}
.items-end {{ align-items: flex-end; }}
.justify-center {{ justify-content: center; }}
.justify-start {{ justify-content: flex-start; }}
.justify-end {{ justify-content: flex-end; }}
.justify-between {{ justify-content: space-between; }}

/* Grid */
.grid {{ display: grid; }}
.grid-cols-1 {{ grid-template-columns: repeat(1, 1fr); }}
.grid-cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
.grid-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.grid-cols-4 {{ grid-template-columns: repeat(4, 1fr); }}

.gap-1 {{ gap: {self.layouts['spacing']['xs']}; }}
.gap-2 {{ gap: {self.layouts['spacing']['sm']}; }}
.gap-3 {{ gap: {self.layouts['spacing']['md']}; }}
.gap-4 {{ gap: {self.layouts['spacing']['lg']}; }}

/* Efectos */
.glow-blue {{
    box-shadow: 0 0 10px {self.colors.glow_blue};
}}

.glow-gold {{
    box-shadow: 0 0 10px {self.colors.glow_gold};
}}

.glass-effect {{
    {self.effects['glass_morphism']}
}}

.energy-border {{
    {self.effects['energy_border']}
}}

.holographic {{
    {self.effects['holographic_overlay']}
}}

/* Animaciones */
.animate-pulse {{
    animation: arc-reactor-pulse 2s ease-in-out infinite;
}}

.animate-glow {{
    animation: skeleton-glow 3s ease-in-out infinite;
}}

.animate-flicker {{
    animation: hologram-flicker 4s ease-in-out infinite;
}}

.animate-stream {{
    animation: data-stream 2s ease-in-out infinite;
}}

/* Estados */
.disabled {{
    opacity: 0.5;
    pointer-events: none;
}}

.hidden {{
    display: none;
}}

.invisible {{
    visibility: hidden;
}}

.opacity-0 {{ opacity: 0; }}
.opacity-50 {{ opacity: 0.5; }}
.opacity-100 {{ opacity: 1; }}

/* Posicionamiento */
.relative {{ position: relative; }}
.absolute {{ position: absolute; }}
.fixed {{ position: fixed; }}

.top-0 {{ top: 0; }}
.right-0 {{ right: 0; }}
.bottom-0 {{ bottom: 0; }}
.left-0 {{ left: 0; }}

.z-10 {{ z-index: 10; }}
.z-20 {{ z-index: 20; }}
.z-30 {{ z-index: 30; }}
.z-40 {{ z-index: 40; }}
.z-50 {{ z-index: 50; }}

/* Overflow */
.overflow-hidden {{ overflow: hidden; }}
.overflow-auto {{ overflow: auto; }}
.overflow-scroll {{ overflow: scroll; }}

/* Cursor */
.cursor-pointer {{ cursor: pointer; }}
.cursor-default {{ cursor: default; }}
.cursor-not-allowed {{ cursor: not-allowed; }}

/* Transiciones */
.transition-all {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

.transition-transform {{
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

.transition-opacity {{
    transition: opacity 0.3s ease;
}}

/* Hover effects */
.hover-scale:hover {{
    transform: scale(1.05);
}}

.hover-glow:hover {{
    box-shadow: 0 0 20px {self.colors.glow_blue};
}}

.hover-lift:hover {{
    transform: translateY(-4px);
}}
"""
    
    def get_tile_config_by_id(self, tile_id: str) -> Optional[TileConfig]:
        """Obtiene configuración de tile por ID"""
        for tile in self.tiles_config:
            if tile.id == tile_id:
                return tile
        return None
    
    def get_tiles_by_size(self, size: str) -> List[TileConfig]:
        """Obtiene tiles por tamaño"""
        return [tile for tile in self.tiles_config if tile.size == size]
    
    def get_color_palette(self) -> ColorPalette:
        """Obtiene paleta de colores completa"""
        return self.colors
    
    def get_theme_config(self) -> Dict[str, Any]:
        """Obtiene configuración del tema"""
        return self.theme_config.copy()
    
    def update_theme_config(self, config: Dict[str, Any]):
        """Actualiza configuración del tema"""
        self.theme_config.update(config)
        logger.info(f"🎨 Configuración de tema actualizada: {config}")
    
    def export_theme(self, file_path: Path) -> bool:
        """Exporta tema completo a archivo JSON"""
        try:
            theme_data = {
                'name': self.theme_config['name'],
                'version': self.theme_config['version'],
                'colors': asdict(self.colors),
                'tiles': [asdict(tile) for tile in self.tiles_config],
                'typography': self.typography,
                'layouts': self.layouts,
                'config': self.theme_config
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🎨 Tema exportado a: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando tema: {e}")
            return False
    
    def import_theme(self, file_path: Path) -> bool:
        """Importa tema desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Actualizar configuración
            if 'config' in theme_data:
                self.theme_config.update(theme_data['config'])
            
            # Actualizar colores
            if 'colors' in theme_data:
                for key, value in theme_data['colors'].items():
                    if hasattr(self.colors, key):
                        setattr(self.colors, key, value)
            
            # Actualizar tipografía
            if 'typography' in theme_data:
                self.typography.update(theme_data['typography'])
            
            # Actualizar layouts
            if 'layouts' in theme_data:
                self.layouts.update(theme_data['layouts'])
            
            logger.info(f"🎨 Tema importado desde: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error importando tema: {e}")
            return False

# Instancia global del tema
tony_stark_theme = TonyStarkTheme()

# Ejemplo de uso
if __name__ == "__main__":
    theme = TonyStarkTheme()
    
    print("🎨 Tema Tony Stark inicializado")
    print(f"📊 Tiles configurados: {len(theme.tiles_config)}")
    print(f"🎯 Colores disponibles: {len([attr for attr in dir(theme.colors) if not attr.startswith('_')])}")
    print(f"✨ Animaciones: {len(theme.animations)}")
    print(f"🔧 Efectos: {len(theme.effects)}")
    
    # Generar CSS completo
    css = theme.get_complete_css()
    print(f"📝 CSS generado: {len(css)} caracteres")
    
    # Mostrar configuración de tiles
    print(f"\n🎮 Configuración de tiles:")
    for tile in theme.tiles_config:
        print(f"  {tile.id}: {tile.title} ({tile.size}, {tile.color})")
    
    # Exportar tema
    export_path = Path("tony_stark_theme.json")
    if theme.export_theme(export_path):
        print(f"✅ Tema exportado a: {export_path}")

