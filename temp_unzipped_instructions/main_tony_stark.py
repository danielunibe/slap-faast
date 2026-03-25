#!/usr/bin/env python3
"""
Slap!Faast v2.0 - Aplicación Principal Tony Stark
Sistema de control gestual avanzado con IA local
"""

import sys
import asyncio
import logging
import signal
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor

# Imports del proyecto
from src.core.events import EventBus
from src.core.controller import SystemController
from src.sensors.manager import SensorManager
from src.tracking.skeleton import SkeletonTracker
from src.recognition.engine import GestureRecognizer
from src.actions.executor import ActionExecutor
from src.config.user_profiles import UserProfileManager
from src.ui.main_window import MainWindow
from src.ui.themes.tony_stark_theme import tony_stark_theme
from src.ui.audio_feedback import JarvisAudioFeedback, AudioEventType, AudioConfig
from src.ai_local.ai_manager import LocalAIManager
from src.ai_local.ollama_client import OllamaClient
from src.ai_local.whisper_local import WhisperLocal
from src.ai_local.vision_local import VisionLocal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slap_faast.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TonyStarkSplashScreen(QSplashScreen):
    """Splash screen estilo Tony Stark"""
    
    def __init__(self):
        # Crear pixmap para splash
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor("#1E1E1E"))
        
        super().__init__(pixmap)
        
        # Configurar fuente
        font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        self.setFont(font)
        
        # Mostrar mensaje inicial
        self.showMessage(
            "🤖 Inicializando Slap!Faast v2.0...",
            color=QColor("#00D4FF")
        )
    
    def update_message(self, message: str, progress: int = 0):
        """Actualiza mensaje del splash"""
        full_message = f"{message}\n\nProgreso: {progress}%"
        self.showMessage(full_message, color=QColor("#00D4FF"))
        QApplication.processEvents()

class SystemInitializer(QObject):
    """Inicializador del sistema en thread separado"""
    
    progress_updated = pyqtSignal(str, int)
    initialization_completed = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.components = {}
        self.initialization_steps = [
            ("Inicializando bus de eventos", self._init_event_bus),
            ("Configurando perfiles de usuario", self._init_user_profiles),
            ("Inicializando gestor de sensores", self._init_sensor_manager),
            ("Configurando tracking de esqueleto", self._init_skeleton_tracker),
            ("Inicializando reconocimiento de gestos", self._init_gesture_recognizer),
            ("Configurando ejecutor de acciones", self._init_action_executor),
            ("Inicializando IA local (Ollama)", self._init_ai_components),
            ("Configurando audio JARVIS", self._init_audio_feedback),
            ("Inicializando AI Manager", self._init_ai_manager),
            ("Configurando controlador del sistema", self._init_system_controller),
            ("Aplicando tema Tony Stark", self._apply_tony_stark_theme),
            ("Finalizando inicialización", self._finalize_initialization)
        ]
    
    async def initialize_system(self):
        """Inicializa todos los componentes del sistema"""
        try:
            total_steps = len(self.initialization_steps)
            
            for i, (step_name, step_func) in enumerate(self.initialization_steps):
                progress = int((i / total_steps) * 100)
                self.progress_updated.emit(step_name, progress)
                
                logger.info(f"🔄 {step_name}...")
                success = await step_func()
                
                if not success:
                    error_msg = f"Error en: {step_name}"
                    logger.error(f"❌ {error_msg}")
                    self.initialization_completed.emit(False, error_msg)
                    return
                
                # Pequeña pausa para mostrar progreso
                await asyncio.sleep(0.2)
            
            self.progress_updated.emit("✅ Sistema Tony Stark listo", 100)
            self.initialization_completed.emit(True, "Sistema inicializado exitosamente")
            
        except Exception as e:
            error_msg = f"Error crítico durante inicialización: {e}"
            logger.error(f"❌ {error_msg}")
            logger.error(traceback.format_exc())
            self.initialization_completed.emit(False, error_msg)
    
    async def _init_event_bus(self) -> bool:
        """Inicializa bus de eventos"""
        try:
            self.components['event_bus'] = EventBus()
            return True
        except Exception as e:
            logger.error(f"Error inicializando event bus: {e}")
            return False
    
    async def _init_user_profiles(self) -> bool:
        """Inicializa gestor de perfiles"""
        try:
            self.components['profile_manager'] = UserProfileManager()
            await self.components['profile_manager'].load_profiles()
            return True
        except Exception as e:
            logger.error(f"Error inicializando perfiles: {e}")
            return False
    
    async def _init_sensor_manager(self) -> bool:
        """Inicializa gestor de sensores"""
        try:
            self.components['sensor_manager'] = SensorManager(
                event_bus=self.components['event_bus']
            )
            return await self.components['sensor_manager'].initialize()
        except Exception as e:
            logger.error(f"Error inicializando sensores: {e}")
            return False
    
    async def _init_skeleton_tracker(self) -> bool:
        """Inicializa tracking de esqueleto"""
        try:
            self.components['skeleton_tracker'] = SkeletonTracker(
                event_bus=self.components['event_bus']
            )
            return await self.components['skeleton_tracker'].initialize()
        except Exception as e:
            logger.error(f"Error inicializando skeleton tracker: {e}")
            return False
    
    async def _init_gesture_recognizer(self) -> bool:
        """Inicializa reconocimiento de gestos"""
        try:
            self.components['gesture_recognizer'] = GestureRecognizer(
                event_bus=self.components['event_bus']
            )
            return await self.components['gesture_recognizer'].initialize()
        except Exception as e:
            logger.error(f"Error inicializando gesture recognizer: {e}")
            return False
    
    async def _init_action_executor(self) -> bool:
        """Inicializa ejecutor de acciones"""
        try:
            self.components['action_executor'] = ActionExecutor(
                event_bus=self.components['event_bus']
            )
            return await self.components['action_executor'].initialize()
        except Exception as e:
            logger.error(f"Error inicializando action executor: {e}")
            return False
    
    async def _init_ai_components(self) -> bool:
        """Inicializa componentes de IA"""
        try:
            # Ollama Client
            self.components['ollama_client'] = OllamaClient()
            ollama_success = await self.components['ollama_client'].connect()
            
            # Whisper Local
            self.components['whisper_local'] = WhisperLocal()
            whisper_success = await self.components['whisper_local'].initialize()
            
            # Vision Local
            self.components['vision_local'] = VisionLocal()
            vision_success = await self.components['vision_local'].initialize()
            
            # Al menos Ollama debe funcionar
            if not ollama_success:
                logger.warning("⚠️ Ollama no disponible, funcionalidad IA limitada")
            
            return True  # Continuar aunque algunos componentes fallen
            
        except Exception as e:
            logger.error(f"Error inicializando componentes IA: {e}")
            return False
    
    async def _init_audio_feedback(self) -> bool:
        """Inicializa sistema de audio JARVIS"""
        try:
            audio_config = AudioConfig(
                enable_sound_effects=True,
                enable_voice_feedback=True,
                master_volume=0.7,
                voice_language="es"
            )
            
            self.components['audio_feedback'] = JarvisAudioFeedback(audio_config)
            return await self.components['audio_feedback'].initialize()
            
        except Exception as e:
            logger.warning(f"Audio JARVIS no disponible: {e}")
            # Audio no es crítico, continuar sin él
            return True
    
    async def _init_ai_manager(self) -> bool:
        """Inicializa AI Manager"""
        try:
            self.components['ai_manager'] = LocalAIManager(
                event_bus=self.components['event_bus']
            )
            return await self.components['ai_manager'].initialize()
            
        except Exception as e:
            logger.error(f"Error inicializando AI Manager: {e}")
            return False
    
    async def _init_system_controller(self) -> bool:
        """Inicializa controlador del sistema"""
        try:
            self.components['system_controller'] = SystemController(
                event_bus=self.components['event_bus'],
                sensor_manager=self.components['sensor_manager'],
                skeleton_tracker=self.components['skeleton_tracker'],
                gesture_recognizer=self.components['gesture_recognizer'],
                action_executor=self.components['action_executor'],
                ai_manager=self.components.get('ai_manager'),
                audio_feedback=self.components.get('audio_feedback')
            )
            return await self.components['system_controller'].initialize()
            
        except Exception as e:
            logger.error(f"Error inicializando system controller: {e}")
            return False
    
    async def _apply_tony_stark_theme(self) -> bool:
        """Aplica tema visual Tony Stark"""
        try:
            # El tema ya está configurado globalmente
            logger.info("🎨 Tema Tony Stark aplicado")
            return True
        except Exception as e:
            logger.error(f"Error aplicando tema: {e}")
            return False
    
    async def _finalize_initialization(self) -> bool:
        """Finaliza inicialización"""
        try:
            # Reproducir sonido de sistema listo
            if 'audio_feedback' in self.components:
                await self.components['audio_feedback'].play_audio_event(
                    AudioEventType.SYSTEM_READY,
                    "Sistema Tony Stark completamente operativo"
                )
            
            logger.info("🚀 Sistema Slap!Faast v2.0 inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error finalizando inicialización: {e}")
            return False

class SlapFaastTonyStarkApp:
    """Aplicación principal Slap!Faast estilo Tony Stark"""
    
    def __init__(self):
        self.app = None
        self.splash = None
        self.main_window = None
        self.initializer = None
        self.components = {}
        
        # Configuración de la aplicación
        self.app_config = {
            'name': 'Slap!Faast v2.0',
            'version': '2.0.0',
            'author': 'Tony Stark Team',
            'description': 'Sistema de control gestual avanzado con IA local',
            'theme': 'tony_stark'
        }
    
    def setup_application(self):
        """Configura la aplicación Qt"""
        self.app = QApplication(sys.argv)
        
        # Configurar aplicación
        self.app.setApplicationName(self.app_config['name'])
        self.app.setApplicationVersion(self.app_config['version'])
        self.app.setOrganizationName(self.app_config['author'])
        
        # Aplicar tema Tony Stark a nivel de aplicación
        self.app.setStyleSheet(tony_stark_theme.get_complete_css())
        
        # Configurar fuente por defecto
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        logger.info(f"🚀 {self.app_config['name']} configurado")
    
    def show_splash_screen(self):
        """Muestra splash screen"""
        self.splash = TonyStarkSplashScreen()
        self.splash.show()
        self.app.processEvents()
    
    async def initialize_system(self):
        """Inicializa el sistema completo"""
        self.initializer = SystemInitializer()
        
        # Conectar señales
        self.initializer.progress_updated.connect(
            lambda msg, progress: self.splash.update_message(msg, progress)
        )
        
        # Inicializar sistema
        await self.initializer.initialize_system()
        
        # Obtener componentes inicializados
        self.components = self.initializer.components
    
    def create_main_window(self):
        """Crea ventana principal"""
        try:
            self.main_window = MainWindow(
                system_controller=self.components.get('system_controller'),
                ai_manager=self.components.get('ai_manager'),
                audio_feedback=self.components.get('audio_feedback'),
                theme=tony_stark_theme
            )
            
            # Conectar eventos de cierre
            self.main_window.closing.connect(self.cleanup_and_exit)
            
            logger.info("🖥️ Ventana principal creada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando ventana principal: {e}")
            return False
    
    def show_main_window(self):
        """Muestra ventana principal"""
        if self.splash:
            self.splash.close()
        
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            logger.info("🖥️ Ventana principal mostrada")
    
    def setup_signal_handlers(self):
        """Configura manejadores de señales del sistema"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Señal recibida: {signum}")
            self.cleanup_and_exit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def cleanup_and_exit(self):
        """Limpia recursos y sale de la aplicación"""
        logger.info("🧹 Iniciando limpieza del sistema...")
        
        try:
            # Reproducir sonido de cierre
            if 'audio_feedback' in self.components:
                await self.components['audio_feedback'].play_audio_event(
                    AudioEventType.SHUTDOWN,
                    "Sistema desactivándose. Hasta luego, señor."
                )
                await asyncio.sleep(2)  # Esperar que termine el audio
            
            # Limpiar componentes en orden inverso
            cleanup_order = [
                'ai_manager',
                'audio_feedback',
                'system_controller',
                'action_executor',
                'gesture_recognizer',
                'skeleton_tracker',
                'sensor_manager',
                'vision_local',
                'whisper_local',
                'ollama_client'
            ]
            
            for component_name in cleanup_order:
                if component_name in self.components:
                    component = self.components[component_name]
                    if hasattr(component, 'cleanup'):
                        try:
                            await component.cleanup()
                            logger.info(f"✅ {component_name} limpiado")
                        except Exception as e:
                            logger.error(f"❌ Error limpiando {component_name}: {e}")
            
            # Cerrar ventana principal
            if self.main_window:
                self.main_window.close()
            
            # Salir de la aplicación
            if self.app:
                self.app.quit()
            
            logger.info("✅ Limpieza completada")
            
        except Exception as e:
            logger.error(f"❌ Error durante limpieza: {e}")
        
        finally:
            sys.exit(0)
    
    async def run(self):
        """Ejecuta la aplicación"""
        try:
            logger.info("🚀 Iniciando Slap!Faast v2.0 Tony Stark Edition")
            
            # Configurar aplicación Qt
            self.setup_application()
            
            # Mostrar splash screen
            self.show_splash_screen()
            
            # Configurar manejadores de señales
            self.setup_signal_handlers()
            
            # Inicializar sistema
            await self.initialize_system()
            
            # Verificar inicialización exitosa
            if not self.components.get('system_controller'):
                raise Exception("Sistema no inicializado correctamente")
            
            # Crear y mostrar ventana principal
            if not self.create_main_window():
                raise Exception("No se pudo crear ventana principal")
            
            self.show_main_window()
            
            # Iniciar sistema
            if 'system_controller' in self.components:
                await self.components['system_controller'].start()
            
            logger.info("🎯 Sistema Tony Stark listo para comandos")
            
            # Ejecutar loop de eventos Qt
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"❌ Error crítico en aplicación: {e}")
            logger.error(traceback.format_exc())
            
            # Mostrar error al usuario
            if self.app:
                QMessageBox.critical(
                    None,
                    "Error Crítico",
                    f"No se pudo inicializar Slap!Faast:\n\n{e}\n\nRevisa los logs para más detalles."
                )
            
            return 1

async def main():
    """Función principal"""
    app = SlapFaastTonyStarkApp()
    
    try:
        return await app.run()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupción por teclado")
        await app.cleanup_and_exit()
        return 0
    except Exception as e:
        logger.error(f"❌ Error no manejado: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    # Configurar política de eventos para asyncio en Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Ejecutar aplicación
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

