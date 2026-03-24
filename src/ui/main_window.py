"""
Slap!Faast Ethyria - Main Window

Ventana principal de la aplicación.
"""

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QStackedWidget, QPushButton, QFrame, QLabel
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme
from .dashboard_view import DashboardView
from .gesture_view import GestureView
from .settings_view import SettingsView
from .ai_chat_widget import AIChatWidget
from .camera_widget import CameraWidget
from .status_bar import StatusBar
from .notification_widget import NotificationManager


if PYQT_AVAILABLE:
    class Sidebar(QFrame):
        """Barra lateral de navegación"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._buttons = []
            self._current = 0
            self._setup_ui()
        
        def _setup_ui(self):
            self.setFixedWidth(60)
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {EthyriaTheme.SURFACE};
                    border-right: 1px solid {EthyriaTheme.BORDER};
                }}
            """)
            
            layout = QVBoxLayout(self)
            layout.setContentsMargins(8, 16, 8, 16)
            layout.setSpacing(8)
            
            # Logo
            logo = QLabel("✦")
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo.setStyleSheet(f"""
                font-size: 24px;
                color: {EthyriaTheme.PRIMARY};
                padding: 8px;
            """)
            layout.addWidget(logo)
            layout.addSpacing(20)
            
            # Botones de navegación
            nav_items = [
                ("🏠", "Dashboard"),
                ("✋", "Gestos"),
                ("💬", "Ethyria"),
                ("⚙️", "Config"),
            ]
            
            for i, (icon, tooltip) in enumerate(nav_items):
                btn = QPushButton(icon)
                btn.setFixedSize(40, 40)
                btn.setToolTip(tooltip)
                btn.setStyleSheet(self._button_style(i == 0))
                btn.clicked.connect(lambda checked, idx=i: self._on_nav(idx))
                layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
                self._buttons.append(btn)
            
            layout.addStretch()
        
        def _button_style(self, active: bool) -> str:
            if active:
                return f"""
                    QPushButton {{
                        background-color: {EthyriaTheme.PRIMARY};
                        color: {EthyriaTheme.BACKGROUND};
                        border: none;
                        border-radius: 8px;
                        font-size: 18px;
                    }}
                """
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {EthyriaTheme.TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: {EthyriaTheme.SURFACE_LIGHT};
                }}
            """
        
        def _on_nav(self, index: int):
            self._current = index
            for i, btn in enumerate(self._buttons):
                btn.setStyleSheet(self._button_style(i == index))
            
            # Emitir señal (parent la captura)
            parent = self.parent()
            if hasattr(parent, 'navigate_to'):
                parent.navigate_to(index)
    
    
    class MainWindow(QMainWindow):
        """
        Ventana principal de Slap!Faast Ethyria.
        """
        
        def __init__(self):
            super().__init__()
            self._setup_window()
            self._setup_ui()
            self._notifications = NotificationManager(self)
        
        def _setup_window(self):
            self.setWindowTitle("Slap!Faast - Ethyria Edition")
            self.setMinimumSize(1000, 700)
            self.setStyleSheet(EthyriaTheme.get_stylesheet())
        
        def _setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            
            main_layout = QHBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Sidebar
            self._sidebar = Sidebar(self)
            main_layout.addWidget(self._sidebar)
            
            # Content area
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
            
            # Stacked widget para vistas
            self._stack = QStackedWidget()
            
            # Vistas
            self._dashboard = DashboardView()
            self._gestures = GestureView()
            self._ai_chat = AIChatWidget()
            self._settings = SettingsView()
            
            self._stack.addWidget(self._dashboard)
            self._stack.addWidget(self._gestures)
            self._stack.addWidget(self._ai_chat)
            self._stack.addWidget(self._settings)
            
            content_layout.addWidget(self._stack)
            
            # Status bar
            self._status_bar = StatusBar()
            content_layout.addWidget(self._status_bar)
            
            main_layout.addLayout(content_layout)
        
        def navigate_to(self, index: int):
            """Navega a vista por índice"""
            self._stack.setCurrentIndex(index)
        
        def notify(self, message: str, type_: str = "info"):
            """Muestra notificación"""
            getattr(self._notifications, type_, self._notifications.info)(message)
        
        def update_status(self, sensor: str = None, tracking: str = None, 
                         ai: str = None, fps: float = None):
            """Actualiza barra de estado"""
            if sensor:
                self._status_bar.set_sensor_status(sensor)
            if tracking:
                self._status_bar.set_tracking_status(tracking)
            if ai:
                self._status_bar.set_ai_status(ai)
            if fps is not None:
                self._status_bar.set_fps(fps)
else:
    class MainWindow:
        def __init__(self):
            pass
    class Sidebar:
        def __init__(self, *args, **kwargs):
            pass
