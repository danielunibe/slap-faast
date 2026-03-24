"""
Slap!Faast Ethyria - Camera Widget

Widget de visualización de cámara.
"""

import numpy as np
from typing import Optional
from loguru import logger

try:
    from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtGui import QImage, QPixmap
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


if PYQT_AVAILABLE:
    class CameraWidget(QWidget):
        """
        Widget para mostrar video de cámara en vivo.
        
        Muestra el feed RGB con overlay de skeleton tracking.
        """
        
        frame_received = pyqtSignal(np.ndarray)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._setup_ui()
            self._frame: Optional[np.ndarray] = None
            self._show_skeleton = True
            self._show_info = True
        
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self._label = QLabel()
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._label.setStyleSheet("""
                QLabel {
                    background-color: #0A0A0F;
                    border: 1px solid #2A2A35;
                    border-radius: 8px;
                }
            """)
            self._label.setMinimumSize(320, 240)
            
            layout.addWidget(self._label)
        
        def update_frame(self, frame: np.ndarray) -> None:
            """Actualiza el frame mostrado"""
            if frame is None:
                return
            
            self._frame = frame
            self._display_frame(frame)
            self.frame_received.emit(frame)
        
        def _display_frame(self, frame: np.ndarray) -> None:
            """Convierte y muestra frame"""
            try:
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                
                # Convertir BGR a RGB
                rgb = frame[:, :, ::-1].copy()
                
                image = QImage(
                    rgb.data,
                    w, h,
                    bytes_per_line,
                    QImage.Format.Format_RGB888
                )
                
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(
                    self._label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self._label.setPixmap(scaled)
            except Exception as e:
                logger.error(f"Error display: {e}")
        
        def set_placeholder(self, text: str = "Sin cámara") -> None:
            """Muestra texto placeholder"""
            self._label.setText(text)
            self._label.setStyleSheet("""
                QLabel {
                    background-color: #0A0A0F;
                    color: #6B6B80;
                    font-size: 14px;
                    border: 1px solid #2A2A35;
                    border-radius: 8px;
                }
            """)
        
        def toggle_skeleton(self, show: bool) -> None:
            """Toggle overlay de skeleton"""
            self._show_skeleton = show
        
        def toggle_info(self, show: bool) -> None:
            """Toggle info overlay"""
            self._show_info = show
else:
    class CameraWidget:
        def __init__(self, *args, **kwargs):
            pass
