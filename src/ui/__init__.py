"""
Slap!Faast Ethyria - UI Package

Interfaz gráfica con PyQt6.
"""

from .main_window import MainWindow
from .ethyria_theme import EthyriaTheme
from .dashboard_view import DashboardView
from .gesture_view import GestureView
from .settings_view import SettingsView
from .ai_chat_widget import AIChatWidget
from .camera_widget import CameraWidget
from .status_bar import StatusBar
from .notification_widget import NotificationManager

__all__ = [
    'MainWindow',
    'EthyriaTheme',
    'DashboardView',
    'GestureView',
    'SettingsView',
    'AIChatWidget',
    'CameraWidget',
    'StatusBar',
    'NotificationManager'
]
