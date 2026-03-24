"""
Slap!Faast Ethyria - Theme

Tema visual Ethyria (estilo Iron Man/futurista).
"""


class EthyriaTheme:
    """
    Tema visual de Ethyria.
    
    Colores inspirados en Iron Man:
    - Cyan: Primario
    - Dorado: Acentos
    - Negro profundo: Fondo
    """
    
    # Colores principales
    PRIMARY = "#00FFFF"      # Cyan brillante
    PRIMARY_DARK = "#00B8B8"
    SECONDARY = "#FFD700"    # Dorado
    SECONDARY_DARK = "#B8860B"
    
    # Fondos
    BACKGROUND = "#0A0A0F"   # Negro profundo
    SURFACE = "#12121A"      # Cards
    SURFACE_LIGHT = "#1A1A25"
    
    # Estados
    SUCCESS = "#32CD32"      # Verde
    WARNING = "#FF8C00"      # Naranja
    ERROR = "#FF4444"        # Rojo
    INFO = "#4169E1"         # Azul
    
    # Texto
    TEXT = "#FFFFFF"
    TEXT_SECONDARY = "#B0B0B0"
    TEXT_MUTED = "#6B6B80"
    
    # Bordes
    BORDER = "#2A2A35"
    BORDER_LIGHT = "#3A3A45"
    
    @classmethod
    def get_stylesheet(cls) -> str:
        """Retorna stylesheet completo para PyQt6"""
        return f"""
        QMainWindow, QWidget {{
            background-color: {cls.BACKGROUND};
            color: {cls.TEXT};
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }}
        
        QLabel {{
            color: {cls.TEXT};
        }}
        
        QPushButton {{
            background-color: {cls.SURFACE};
            color: {cls.PRIMARY};
            border: 1px solid {cls.PRIMARY};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {cls.PRIMARY};
            color: {cls.BACKGROUND};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.PRIMARY_DARK};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT_MUTED};
            border-color: {cls.BORDER};
        }}
        
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT};
            border: 1px solid {cls.BORDER};
            border-radius: 4px;
            padding: 8px;
            selection-background-color: {cls.PRIMARY};
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {cls.PRIMARY};
        }}
        
        QComboBox {{
            background-color: {cls.SURFACE};
            color: {cls.TEXT};
            border: 1px solid {cls.BORDER};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QScrollBar:vertical {{
            background-color: {cls.SURFACE};
            width: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.BORDER_LIGHT};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.PRIMARY};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {cls.BORDER};
            background-color: {cls.SURFACE};
        }}
        
        QTabBar::tab {{
            background-color: {cls.BACKGROUND};
            color: {cls.TEXT_SECONDARY};
            padding: 8px 16px;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            color: {cls.PRIMARY};
            border-bottom-color: {cls.PRIMARY};
        }}
        
        QGroupBox {{
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
        }}
        
        QGroupBox::title {{
            color: {cls.PRIMARY};
            subcontrol-origin: margin;
            left: 10px;
        }}
        
        QSlider::groove:horizontal {{
            height: 4px;
            background-color: {cls.BORDER};
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {cls.PRIMARY};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {cls.PRIMARY};
            border-radius: 2px;
        }}
        
        QCheckBox {{
            color: {cls.TEXT};
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {cls.BORDER};
            background-color: {cls.SURFACE};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {cls.PRIMARY};
            border-color: {cls.PRIMARY};
        }}
        
        QProgressBar {{
            background-color: {cls.SURFACE};
            border-radius: 4px;
            text-align: center;
            color: {cls.TEXT};
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.PRIMARY};
            border-radius: 4px;
        }}
        
        QListWidget {{
            background-color: {cls.SURFACE};
            border: 1px solid {cls.BORDER};
            border-radius: 6px;
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {cls.BORDER};
        }}
        
        QListWidget::item:selected {{
            background-color: {cls.PRIMARY};
            color: {cls.BACKGROUND};
        }}
        
        QListWidget::item:hover {{
            background-color: {cls.SURFACE_LIGHT};
        }}
        """
    
    @classmethod
    def glow_effect(cls, intensity: float = 0.5) -> str:
        """CSS para efecto glow"""
        return f"box-shadow: 0 0 {int(20*intensity)}px {cls.PRIMARY};"
