"""
Slap!Faast Ethyria - Notification Widget

Sistema de notificaciones toast.
"""

try:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
    from PyQt6.QtGui import QColor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme


if PYQT_AVAILABLE:
    class Toast(QWidget):
        """Notificación toast individual"""
        
        def __init__(self, message: str, type_: str = "info", duration: int = 3000, parent=None):
            super().__init__(parent)
            self._setup_ui(message, type_)
            
            # Auto-cerrar
            QTimer.singleShot(duration, self.close)
        
        def _setup_ui(self, message: str, type_: str):
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            colors = {
                "info": EthyriaTheme.PRIMARY,
                "success": EthyriaTheme.SUCCESS,
                "warning": EthyriaTheme.WARNING,
                "error": EthyriaTheme.ERROR
            }
            color = colors.get(type_, EthyriaTheme.PRIMARY)
            
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {EthyriaTheme.SURFACE};
                    border: 1px solid {color};
                    border-radius: 8px;
                    border-left: 4px solid {color};
                }}
            """)
            
            layout = QHBoxLayout(self)
            layout.setContentsMargins(12, 8, 12, 8)
            
            label = QLabel(message)
            label.setStyleSheet(f"color: {EthyriaTheme.TEXT};")
            layout.addWidget(label)
            
            close_btn = QPushButton("✕")
            close_btn.setFixedSize(20, 20)
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {EthyriaTheme.TEXT_MUTED};
                    border: none;
                }}
                QPushButton:hover {{
                    color: {EthyriaTheme.TEXT};
                }}
            """)
            close_btn.clicked.connect(self.close)
            layout.addWidget(close_btn)
    
    
    class NotificationManager:
        """
        Gestor de notificaciones.
        
        Uso:
            notifications = NotificationManager(parent_window)
            notifications.info("Mensaje informativo")
            notifications.success("Gesto detectado!")
            notifications.error("Error de conexión")
        """
        
        def __init__(self, parent=None):
            self._parent = parent
            self._toasts = []
            self._y_offset = 50
        
        def _show_toast(self, message: str, type_: str = "info"):
            toast = Toast(message, type_, parent=self._parent)
            
            # Posicionar
            if self._parent:
                parent_geo = self._parent.geometry()
                x = parent_geo.right() - 320
                y = parent_geo.top() + self._y_offset + len(self._toasts) * 60
                toast.move(x, y)
            
            toast.show()
            self._toasts.append(toast)
            
            # Limpiar después
            QTimer.singleShot(3500, lambda: self._remove_toast(toast))
        
        def _remove_toast(self, toast):
            if toast in self._toasts:
                self._toasts.remove(toast)
        
        def info(self, message: str):
            self._show_toast(message, "info")
        
        def success(self, message: str):
            self._show_toast(message, "success")
        
        def warning(self, message: str):
            self._show_toast(message, "warning")
        
        def error(self, message: str):
            self._show_toast(message, "error")
else:
    class Toast:
        def __init__(self, *args, **kwargs):
            pass
    class NotificationManager:
        def __init__(self, *args, **kwargs):
            pass
        def info(self, msg): pass
        def success(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
