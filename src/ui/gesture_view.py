"""
Slap!Faast Ethyria - Gesture View

Vista de gestión de gestos.
"""

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QListWidget, QListWidgetItem, QPushButton, QFrame
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme


if PYQT_AVAILABLE:
    class GestureView(QWidget):
        """
        Vista de gestión de gestos.
        
        Muestra lista de gestos y permite configurarlos.
        """
        
        gesture_selected = pyqtSignal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._gestures = []
            self._setup_ui()
        
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(16)
            
            # Header
            header = QHBoxLayout()
            title = QLabel("✋ Gestos")
            title.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {EthyriaTheme.PRIMARY};
            """)
            header.addWidget(title)
            header.addStretch()
            
            btn_record = QPushButton("+ Nuevo Gesto")
            header.addWidget(btn_record)
            
            layout.addLayout(header)
            
            # Lista de gestos
            self._list = QListWidget()
            self._list.setStyleSheet(f"""
                QListWidget {{
                    background-color: {EthyriaTheme.SURFACE};
                    border: 1px solid {EthyriaTheme.BORDER};
                    border-radius: 8px;
                }}
                QListWidget::item {{
                    padding: 12px;
                    border-bottom: 1px solid {EthyriaTheme.BORDER};
                }}
                QListWidget::item:selected {{
                    background-color: {EthyriaTheme.PRIMARY};
                    color: {EthyriaTheme.BACKGROUND};
                }}
            """)
            self._list.itemClicked.connect(self._on_item_clicked)
            layout.addWidget(self._list)
            
            # Panel de detalles
            self._details = QFrame()
            self._details.setStyleSheet(f"""
                QFrame {{
                    background-color: {EthyriaTheme.SURFACE};
                    border: 1px solid {EthyriaTheme.BORDER};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            details_layout = QVBoxLayout(self._details)
            
            self._detail_label = QLabel("Selecciona un gesto")
            self._detail_label.setStyleSheet(f"color: {EthyriaTheme.TEXT_MUTED};")
            details_layout.addWidget(self._detail_label)
            
            layout.addWidget(self._details)
        
        def load_gestures(self, gestures: list):
            """Carga lista de gestos"""
            self._list.clear()
            self._gestures = gestures
            
            for g in gestures:
                item = QListWidgetItem(f"{g.get('icon', '✋')} {g.get('name', 'Gesto')}")
                item.setData(Qt.ItemDataRole.UserRole, g.get('id'))
                self._list.addItem(item)
        
        def _on_item_clicked(self, item: QListWidgetItem):
            gesture_id = item.data(Qt.ItemDataRole.UserRole)
            self.gesture_selected.emit(gesture_id)
            
            # Mostrar detalles
            for g in self._gestures:
                if g.get('id') == gesture_id:
                    self._detail_label.setText(
                        f"Nombre: {g.get('name')}\n"
                        f"Descripción: {g.get('description', '-')}\n"
                        f"Acción: {g.get('action', '-')}"
                    )
                    break
else:
    class GestureView:
        def __init__(self, *args, **kwargs):
            pass
