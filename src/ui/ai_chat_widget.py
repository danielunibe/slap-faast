"""
Slap!Faast Ethyria - AI Chat Widget

Widget de chat con Ethyria.
"""

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QTextEdit, QLineEdit, QPushButton, QFrame, QScrollArea
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme


if PYQT_AVAILABLE:
    class AIChatWidget(QWidget):
        """
        Widget de chat con Ethyria.
        """
        
        message_sent = pyqtSignal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._setup_ui()
        
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(12)
            
            # Título
            title = QLabel("✦ Ethyria")
            title.setStyleSheet(f"""
                font-size: 20px;
                font-weight: bold;
                color: {EthyriaTheme.SECONDARY};
            """)
            layout.addWidget(title)
            
            # Área de chat
            self._chat_area = QTextEdit()
            self._chat_area.setReadOnly(True)
            self._chat_area.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {EthyriaTheme.SURFACE};
                    color: {EthyriaTheme.TEXT};
                    border: 1px solid {EthyriaTheme.BORDER};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            layout.addWidget(self._chat_area)
            
            # Input
            input_layout = QHBoxLayout()
            
            self._input = QLineEdit()
            self._input.setPlaceholderText("Escribe o habla...")
            self._input.returnPressed.connect(self._send_message)
            input_layout.addWidget(self._input)
            
            btn_send = QPushButton("→")
            btn_send.setFixedWidth(40)
            btn_send.clicked.connect(self._send_message)
            input_layout.addWidget(btn_send)
            
            btn_mic = QPushButton("🎤")
            btn_mic.setFixedWidth(40)
            input_layout.addWidget(btn_mic)
            
            layout.addLayout(input_layout)
            
            # Mensaje inicial
            self.add_message("Ethyria", "¡Hola! Soy Ethyria, tu asistente. ¿En qué te ayudo?")
        
        def add_message(self, sender: str, text: str):
            """Añade mensaje al chat"""
            is_user = sender.lower() == "tú" or sender.lower() == "user"
            
            color = EthyriaTheme.TEXT if is_user else EthyriaTheme.SECONDARY
            align = "right" if is_user else "left"
            
            html = f"""
            <div style="text-align: {align}; margin: 8px 0;">
                <span style="color: {EthyriaTheme.TEXT_MUTED}; font-size: 11px;">{sender}</span><br>
                <span style="color: {color};">{text}</span>
            </div>
            """
            
            self._chat_area.append(html)
            scrollbar = self._chat_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        def _send_message(self):
            text = self._input.text().strip()
            if text:
                self.add_message("Tú", text)
                self._input.clear()
                self.message_sent.emit(text)
        
        def set_response(self, text: str):
            """Añade respuesta de Ethyria"""
            self.add_message("Ethyria", text)
else:
    class AIChatWidget:
        def __init__(self, *args, **kwargs):
            pass
