"""
Slap!Faast Ethyria - Settings View

Vista de configuración.
"""

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
        QTabWidget, QSlider, QCheckBox, QComboBox,
        QPushButton, QGroupBox, QFormLayout
    )
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .ethyria_theme import EthyriaTheme


if PYQT_AVAILABLE:
    class SettingsView(QWidget):
        """Vista de configuración con tabs."""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self._setup_ui()
        
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(16)
            
            title = QLabel("⚙️ Configuración")
            title.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {EthyriaTheme.PRIMARY};
            """)
            layout.addWidget(title)
            
            # Tabs
            tabs = QTabWidget()
            tabs.addTab(self._create_sensor_tab(), "Sensor")
            tabs.addTab(self._create_gestures_tab(), "Gestos")
            tabs.addTab(self._create_ai_tab(), "IA")
            tabs.addTab(self._create_audio_tab(), "Audio")
            layout.addWidget(tabs)
            
            # Botones
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            btn_reset = QPushButton("Restaurar")
            btn_save = QPushButton("Guardar")
            btn_save.setStyleSheet(f"background-color: {EthyriaTheme.PRIMARY};")
            
            btn_layout.addWidget(btn_reset)
            btn_layout.addWidget(btn_save)
            layout.addLayout(btn_layout)
        
        def _create_sensor_tab(self) -> QWidget:
            tab = QWidget()
            layout = QFormLayout(tab)
            
            # Tipo de sensor
            sensor_combo = QComboBox()
            sensor_combo.addItems(["Kinect v1", "Webcam", "Auto-detectar"])
            layout.addRow("Sensor:", sensor_combo)
            
            # FPS Activo
            fps_active = QSlider(Qt.Orientation.Horizontal)
            fps_active.setRange(15, 60)
            fps_active.setValue(30)
            layout.addRow("FPS Activo:", fps_active)
            
            # FPS Idle
            fps_idle = QSlider(Qt.Orientation.Horizontal)
            fps_idle.setRange(1, 15)
            fps_idle.setValue(5)
            layout.addRow("FPS Reposo:", fps_idle)
            
            # Usar profundidad
            use_depth = QCheckBox("Usar datos de profundidad")
            use_depth.setChecked(True)
            layout.addRow("", use_depth)
            
            return tab
        
        def _create_gestures_tab(self) -> QWidget:
            tab = QWidget()
            layout = QFormLayout(tab)
            
            # Confianza
            confidence = QSlider(Qt.Orientation.Horizontal)
            confidence.setRange(50, 95)
            confidence.setValue(70)
            layout.addRow("Confianza mínima:", confidence)
            
            # Cooldown
            cooldown = QSlider(Qt.Orientation.Horizontal)
            cooldown.setRange(200, 2000)
            cooldown.setValue(500)
            layout.addRow("Cooldown (ms):", cooldown)
            
            # Confirmar críticos
            confirm = QCheckBox("Confirmar acciones críticas")
            confirm.setChecked(True)
            layout.addRow("", confirm)
            
            return tab
        
        def _create_ai_tab(self) -> QWidget:
            tab = QWidget()
            layout = QFormLayout(tab)
            
            # Modelo
            model = QComboBox()
            model.addItems(["llama3.2", "llama3.1", "mistral", "gemma2"])
            layout.addRow("Modelo LLM:", model)
            
            # Host
            enable_ai = QCheckBox("Habilitar IA")
            enable_ai.setChecked(True)
            layout.addRow("", enable_ai)
            
            # Whisper
            whisper = QComboBox()
            whisper.addItems(["base", "small", "medium"])
            layout.addRow("Modelo Whisper:", whisper)
            
            return tab
        
        def _create_audio_tab(self) -> QWidget:
            tab = QWidget()
            layout = QFormLayout(tab)
            
            # Volumen
            volume = QSlider(Qt.Orientation.Horizontal)
            volume.setRange(0, 100)
            volume.setValue(70)
            layout.addRow("Volumen:", volume)
            
            # TTS
            tts = QCheckBox("Habilitar TTS")
            tts.setChecked(True)
            layout.addRow("", tts)
            
            # Efectos
            effects = QCheckBox("Efectos de sonido")
            effects.setChecked(True)
            layout.addRow("", effects)
            
            return tab
else:
    class SettingsView:
        def __init__(self, *args, **kwargs):
            pass
