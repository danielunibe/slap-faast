"""
Slap!Faast Ethyria - Status Bar

Barra de estado con indicadores.
"""

try:
    from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme


if PYQT_AVAILABLE:
    class StatusIndicator(QLabel):
        """Indicador de estado individual"""
        
        def __init__(self, name: str, parent=None):
            super().__init__(parent)
            self._name = name
            self._status = "off"
            self.update_status("off")
        
        def update_status(self, status: str):
            """Actualiza estado: on, off, warning, error"""
            self._status = status
            
            colors = {
                "on": EthyriaTheme.SUCCESS,
                "off": EthyriaTheme.TEXT_MUTED,
                "warning": EthyriaTheme.WARNING,
                "error": EthyriaTheme.ERROR,
                "active": EthyriaTheme.PRIMARY
            }
            
            color = colors.get(status, EthyriaTheme.TEXT_MUTED)
            
            self.setText(f"● {self._name}")
            self.setStyleSheet(f"color: {color}; font-size: 12px;")
    
    
    class StatusBar(QFrame):
        """
        Barra de estado inferior.
        
        Muestra:
        - Estado de sensor
        - Estado de IA
        - Estado de tracking
        - FPS
        """
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._setup_ui()
        
        def _setup_ui(self):
            self.setFixedHeight(32)
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {EthyriaTheme.SURFACE};
                    border-top: 1px solid {EthyriaTheme.BORDER};
                }}
            """)
            
            layout = QHBoxLayout(self)
            layout.setContentsMargins(12, 0, 12, 0)
            layout.setSpacing(20)
            
            # Indicadores
            self._sensor = StatusIndicator("Sensor")
            self._tracking = StatusIndicator("Tracking")
            self._ai = StatusIndicator("IA")
            
            layout.addWidget(self._sensor)
            layout.addWidget(self._tracking)
            layout.addWidget(self._ai)
            
            layout.addStretch()
            
            # FPS
            self._fps_label = QLabel("0 FPS")
            self._fps_label.setStyleSheet(f"color: {EthyriaTheme.TEXT_MUTED}; font-size: 12px;")
            layout.addWidget(self._fps_label)
            
            # Estado
            self._status_label = QLabel("Listo")
            self._status_label.setStyleSheet(f"color: {EthyriaTheme.PRIMARY}; font-size: 12px;")
            layout.addWidget(self._status_label)
        
        def set_sensor_status(self, status: str):
            self._sensor.update_status(status)
        
        def set_tracking_status(self, status: str):
            self._tracking.update_status(status)
        
        def set_ai_status(self, status: str):
            self._ai.update_status(status)
        
        def set_fps(self, fps: float):
            self._fps_label.setText(f"{fps:.1f} FPS")
        
        def set_status_text(self, text: str):
            self._status_label.setText(text)
else:
    class StatusBar:
        def __init__(self, *args, **kwargs):
            pass
    class StatusIndicator:
        def __init__(self, *args, **kwargs):
            pass
