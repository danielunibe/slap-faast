"""
Slap!Faast Ethyria - Dashboard View

Vista principal del dashboard.
"""

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QFrame, QGridLayout
    )
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme


if PYQT_AVAILABLE:
    class StatCard(QFrame):
        """Tarjeta de estadística"""
        
        def __init__(self, title: str, value: str, icon: str = "", parent=None):
            super().__init__(parent)
            self._setup_ui(title, value, icon)
        
        def _setup_ui(self, title: str, value: str, icon: str):
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {EthyriaTheme.SURFACE};
                    border: 1px solid {EthyriaTheme.BORDER};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            
            layout = QVBoxLayout(self)
            layout.setSpacing(8)
            
            # Título
            title_label = QLabel(f"{icon} {title}")
            title_label.setStyleSheet(f"color: {EthyriaTheme.TEXT_SECONDARY}; font-size: 12px;")
            layout.addWidget(title_label)
            
            # Valor
            self._value_label = QLabel(value)
            self._value_label.setStyleSheet(f"""
                color: {EthyriaTheme.PRIMARY};
                font-size: 24px;
                font-weight: bold;
            """)
            layout.addWidget(self._value_label)
        
        def set_value(self, value: str):
            self._value_label.setText(value)
    
    
    class DashboardView(QWidget):
        """
        Vista principal del dashboard.
        
        Muestra:
        - Preview de cámara
        - Estadísticas en tiempo real
        - Estado del sistema
        - Gestos recientes
        """
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._setup_ui()
        
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(16)
            
            # Título
            title = QLabel("✦ Dashboard")
            title.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {EthyriaTheme.PRIMARY};
            """)
            layout.addWidget(title)
            
            # Grid de estadísticas
            stats_layout = QGridLayout()
            stats_layout.setSpacing(12)
            
            self._stat_fps = StatCard("FPS", "0", "📊")
            self._stat_gestures = StatCard("Gestos", "0", "✋")
            self._stat_actions = StatCard("Acciones", "0", "⚡")
            self._stat_status = StatCard("Estado", "Idle", "🔵")
            
            stats_layout.addWidget(self._stat_fps, 0, 0)
            stats_layout.addWidget(self._stat_gestures, 0, 1)
            stats_layout.addWidget(self._stat_actions, 1, 0)
            stats_layout.addWidget(self._stat_status, 1, 1)
            
            layout.addLayout(stats_layout)
            
            # Área de actividad
            activity_frame = QFrame()
            activity_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {EthyriaTheme.SURFACE};
                    border: 1px solid {EthyriaTheme.BORDER};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            activity_layout = QVBoxLayout(activity_frame)
            
            activity_title = QLabel("📋 Actividad Reciente")
            activity_title.setStyleSheet(f"color: {EthyriaTheme.TEXT}; font-weight: bold;")
            activity_layout.addWidget(activity_title)
            
            self._activity_list = QLabel("Sin actividad reciente")
            self._activity_list.setStyleSheet(f"color: {EthyriaTheme.TEXT_MUTED};")
            activity_layout.addWidget(self._activity_list)
            
            layout.addWidget(activity_frame)
            layout.addStretch()
        
        def update_stats(self, fps: float, gestures: int, actions: int, status: str):
            """Actualiza estadísticas"""
            self._stat_fps.set_value(f"{fps:.1f}")
            self._stat_gestures.set_value(str(gestures))
            self._stat_actions.set_value(str(actions))
            self._stat_status.set_value(status)
        
        def add_activity(self, text: str):
            """Añade actividad"""
            current = self._activity_list.text()
            if current == "Sin actividad reciente":
                self._activity_list.setText(text)
            else:
                lines = current.split("\n")[-4:]  # Últimas 5
                lines.append(text)
                self._activity_list.setText("\n".join(lines))
else:
    class DashboardView:
        def __init__(self, *args, **kwargs):
            pass
    class StatCard:
        def __init__(self, *args, **kwargs):
            pass
