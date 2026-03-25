"""
Integración Final MainWindow ↔ Backend
Conecta la interfaz gráfica con todos los componentes del sistema
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import QMessageBox

from ..core.events import EventBus, Event
from ..ai_local.ai_manager import LocalAIManager
from ..ui.audio_feedback import JarvisAudioFeedback, AudioEventType
from ..core.controller import SystemController

logger = logging.getLogger(__name__)

class UIBackendIntegrator(QObject):
    """Integrador entre UI y Backend"""
    
    # Señales para comunicación con UI
    gesture_detected = pyqtSignal(dict)
    ai_response_received = pyqtSignal(str)
    system_status_changed = pyqtSignal(str)
    hardware_status_updated = pyqtSignal(dict)
    audio_event_triggered = pyqtSignal(str)
    
    def __init__(self, main_window, system_controller: Optional[SystemController] = None,
                 ai_manager: Optional[LocalAIManager] = None,
                 audio_feedback: Optional[JarvisAudioFeedback] = None):
        super().__init__()
        
        self.main_window = main_window
        self.system_controller = system_controller
        self.ai_manager = ai_manager
        self.audio_feedback = audio_feedback
        
        # Estado de integración
        self.is_connected = False
        self.event_subscriptions = []
        
        # Timer para actualizaciones periódicas
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._periodic_update)
        self.update_timer.start(1000)  # Actualizar cada segundo
    
    async def connect_components(self) -> bool:
        """Conecta todos los componentes"""
        try:
            logger.info("🔗 Conectando UI con backend...")
            
            # Conectar con EventBus si está disponible
            if self.system_controller and hasattr(self.system_controller, 'event_bus'):
                await self._connect_event_bus()
            
            # Conectar con AI Manager
            if self.ai_manager:
                await self._connect_ai_manager()
            
            # Conectar con Audio Feedback
            if self.audio_feedback:
                await self._connect_audio_feedback()
            
            # Conectar señales de UI
            self._connect_ui_signals()
            
            self.is_connected = True
            logger.info("✅ Integración UI ↔ Backend completada")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando componentes: {e}")
            return False
    
    async def _connect_event_bus(self):
        """Conecta con el bus de eventos"""
        event_bus = self.system_controller.event_bus
        
        # Suscribirse a eventos relevantes
        events_to_subscribe = [
            'gesture_detected',
            'gesture_recognized',
            'action_executed',
            'sensor_connected',
            'sensor_disconnected',
            'system_status_changed',
            'ai_response_generated',
            'voice_command_received',
            'error_occurred'
        ]
        
        for event_type in events_to_subscribe:
            callback = self._create_event_callback(event_type)
            event_bus.subscribe(event_type, callback)
            self.event_subscriptions.append((event_type, callback))
        
        logger.info(f"📡 Suscrito a {len(events_to_subscribe)} eventos")
    
    def _create_event_callback(self, event_type: str) -> Callable:
        """Crea callback para evento específico"""
        def callback(event: Event):
            try:
                # Procesar evento según tipo
                if event_type == 'gesture_detected':
                    self.gesture_detected.emit(event.data)
                    self._update_gesture_display(event.data)
                
                elif event_type == 'gesture_recognized':
                    self._handle_gesture_recognized(event.data)
                
                elif event_type == 'action_executed':
                    self._handle_action_executed(event.data)
                
                elif event_type == 'sensor_connected':
                    self._handle_sensor_status(event.data, True)
                
                elif event_type == 'sensor_disconnected':
                    self._handle_sensor_status(event.data, False)
                
                elif event_type == 'system_status_changed':
                    self.system_status_changed.emit(event.data.get('status', 'unknown'))
                
                elif event_type == 'ai_response_generated':
                    self.ai_response_received.emit(event.data.get('response', ''))
                
                elif event_type == 'voice_command_received':
                    self._handle_voice_command(event.data)
                
                elif event_type == 'error_occurred':
                    self._handle_error(event.data)
                
            except Exception as e:
                logger.error(f"❌ Error procesando evento {event_type}: {e}")
        
        return callback
    
    async def _connect_ai_manager(self):
        """Conecta con AI Manager"""
        # Configurar callbacks para AI Manager
        if hasattr(self.ai_manager, 'set_ui_callbacks'):
            callbacks = {
                'on_intent_processed': self._on_ai_intent_processed,
                'on_command_executed': self._on_ai_command_executed,
                'on_error': self._on_ai_error
            }
            self.ai_manager.set_ui_callbacks(callbacks)
        
        logger.info("🤖 AI Manager conectado")
    
    async def _connect_audio_feedback(self):
        """Conecta con sistema de audio"""
        # El audio feedback ya está integrado via eventos
        logger.info("🔊 Audio Feedback conectado")
    
    def _connect_ui_signals(self):
        """Conecta señales de la UI"""
        # Conectar botones y controles de la ventana principal
        if hasattr(self.main_window, 'start_button'):
            self.main_window.start_button.clicked.connect(self._on_start_system)
        
        if hasattr(self.main_window, 'stop_button'):
            self.main_window.stop_button.clicked.connect(self._on_stop_system)
        
        if hasattr(self.main_window, 'gesture_editor'):
            # Conectar editor de gestos
            pass
        
        logger.info("🖥️ Señales de UI conectadas")
    
    def _update_gesture_display(self, gesture_data: Dict[str, Any]):
        """Actualiza display de gestos en UI"""
        try:
            # Actualizar widget de preview de cámara
            if hasattr(self.main_window, 'camera_preview'):
                self.main_window.camera_preview.update_gesture_overlay(gesture_data)
            
            # Actualizar lista de gestos
            if hasattr(self.main_window, 'gesture_list'):
                self.main_window.gesture_list.highlight_detected_gesture(
                    gesture_data.get('gesture_name')
                )
            
        except Exception as e:
            logger.error(f"❌ Error actualizando display de gestos: {e}")
    
    def _handle_gesture_recognized(self, gesture_data: Dict[str, Any]):
        """Maneja gesto reconocido"""
        try:
            gesture_name = gesture_data.get('gesture_name', 'unknown')
            confidence = gesture_data.get('confidence', 0.0)
            
            # Reproducir audio feedback
            if self.audio_feedback:
                asyncio.create_task(
                    self.audio_feedback.play_audio_event(
                        AudioEventType.GESTURE_DETECTED,
                        f"Gesto {gesture_name} detectado"
                    )
                )
            
            # Actualizar estadísticas
            if hasattr(self.main_window, 'status_indicator'):
                self.main_window.status_indicator.update_gesture_stats(gesture_data)
            
            logger.info(f"👋 Gesto reconocido: {gesture_name} ({confidence:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error manejando gesto reconocido: {e}")
    
    def _handle_action_executed(self, action_data: Dict[str, Any]):
        """Maneja acción ejecutada"""
        try:
            action_type = action_data.get('action_type', 'unknown')
            success = action_data.get('success', False)
            
            # Reproducir audio feedback
            if self.audio_feedback:
                event_type = AudioEventType.COMMAND_EXECUTED if success else AudioEventType.COMMAND_FAILED
                asyncio.create_task(
                    self.audio_feedback.play_audio_event(event_type)
                )
            
            # Mostrar notificación en UI
            if hasattr(self.main_window, 'show_notification'):
                message = f"Acción {action_type} {'ejecutada' if success else 'falló'}"
                self.main_window.show_notification(message, success)
            
            logger.info(f"⚡ Acción ejecutada: {action_type} ({'éxito' if success else 'fallo'})")
            
        except Exception as e:
            logger.error(f"❌ Error manejando acción ejecutada: {e}")
    
    def _handle_sensor_status(self, sensor_data: Dict[str, Any], connected: bool):
        """Maneja cambio de estado de sensor"""
        try:
            sensor_type = sensor_data.get('sensor_type', 'unknown')
            
            # Actualizar indicador de hardware
            if hasattr(self.main_window, 'hardware_monitor'):
                self.main_window.hardware_monitor.update_sensor_status(
                    sensor_type, connected
                )
            
            # Actualizar tile de sensor principal
            if hasattr(self.main_window, 'sensor_status_tile'):
                self.main_window.sensor_status_tile.update_connection_status(connected)
            
            status = "conectado" if connected else "desconectado"
            logger.info(f"📡 Sensor {sensor_type} {status}")
            
        except Exception as e:
            logger.error(f"❌ Error manejando estado de sensor: {e}")
    
    def _handle_voice_command(self, voice_data: Dict[str, Any]):
        """Maneja comando de voz"""
        try:
            command_text = voice_data.get('text', '')
            confidence = voice_data.get('confidence', 0.0)
            
            # Mostrar comando en UI
            if hasattr(self.main_window, 'voice_display'):
                self.main_window.voice_display.show_command(command_text, confidence)
            
            # Reproducir audio feedback
            if self.audio_feedback:
                asyncio.create_task(
                    self.audio_feedback.play_audio_event(
                        AudioEventType.VOICE_DETECTED,
                        "Comando de voz recibido"
                    )
                )
            
            logger.info(f"🎤 Comando de voz: {command_text} ({confidence:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error manejando comando de voz: {e}")
    
    def _handle_error(self, error_data: Dict[str, Any]):
        """Maneja errores del sistema"""
        try:
            error_message = error_data.get('message', 'Error desconocido')
            error_type = error_data.get('type', 'general')
            
            # Mostrar error en UI
            if error_type == 'critical':
                QMessageBox.critical(
                    self.main_window,
                    "Error Crítico",
                    f"Error crítico del sistema:\n\n{error_message}"
                )
            else:
                if hasattr(self.main_window, 'show_notification'):
                    self.main_window.show_notification(f"Error: {error_message}", False)
            
            # Reproducir audio de error
            if self.audio_feedback:
                asyncio.create_task(
                    self.audio_feedback.play_audio_event(
                        AudioEventType.SYSTEM_ERROR,
                        "Ha ocurrido un error"
                    )
                )
            
            logger.error(f"❌ Error del sistema: {error_message}")
            
        except Exception as e:
            logger.error(f"❌ Error manejando error del sistema: {e}")
    
    async def _on_ai_intent_processed(self, intent_data: Dict[str, Any]):
        """Callback para intención procesada por IA"""
        try:
            intent_type = intent_data.get('intent', 'unknown')
            confidence = intent_data.get('confidence', 0.0)
            
            # Mostrar en UI
            if hasattr(self.main_window, 'ai_status_display'):
                self.main_window.ai_status_display.show_intent(intent_type, confidence)
            
            logger.info(f"🧠 Intención IA: {intent_type} ({confidence:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Error procesando intención IA: {e}")
    
    async def _on_ai_command_executed(self, command_data: Dict[str, Any]):
        """Callback para comando IA ejecutado"""
        try:
            command = command_data.get('command', '')
            success = command_data.get('success', False)
            
            # Reproducir audio feedback
            if self.audio_feedback:
                event_type = AudioEventType.COMMAND_EXECUTED if success else AudioEventType.COMMAND_FAILED
                await self.audio_feedback.play_audio_event(event_type)
            
            logger.info(f"🤖 Comando IA ejecutado: {command} ({'éxito' if success else 'fallo'})")
            
        except Exception as e:
            logger.error(f"❌ Error procesando comando IA: {e}")
    
    async def _on_ai_error(self, error_data: Dict[str, Any]):
        """Callback para error de IA"""
        try:
            error_message = error_data.get('message', 'Error de IA')
            
            # Mostrar en UI
            if hasattr(self.main_window, 'show_notification'):
                self.main_window.show_notification(f"Error IA: {error_message}", False)
            
            logger.error(f"🤖❌ Error IA: {error_message}")
            
        except Exception as e:
            logger.error(f"❌ Error manejando error IA: {e}")
    
    def _on_start_system(self):
        """Maneja inicio del sistema"""
        try:
            if self.system_controller:
                asyncio.create_task(self.system_controller.start())
            
            # Reproducir audio de inicio
            if self.audio_feedback:
                asyncio.create_task(
                    self.audio_feedback.play_audio_event(
                        AudioEventType.SYSTEM_READY,
                        "Sistema iniciado"
                    )
                )
            
            logger.info("🚀 Sistema iniciado desde UI")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando sistema: {e}")
    
    def _on_stop_system(self):
        """Maneja parada del sistema"""
        try:
            if self.system_controller:
                asyncio.create_task(self.system_controller.stop())
            
            # Reproducir audio de parada
            if self.audio_feedback:
                asyncio.create_task(
                    self.audio_feedback.play_audio_event(
                        AudioEventType.SHUTDOWN,
                        "Sistema detenido"
                    )
                )
            
            logger.info("🛑 Sistema detenido desde UI")
            
        except Exception as e:
            logger.error(f"❌ Error deteniendo sistema: {e}")
    
    def _periodic_update(self):
        """Actualización periódica de la UI"""
        try:
            # Actualizar estadísticas
            if self.system_controller and hasattr(self.main_window, 'status_indicator'):
                stats = self.system_controller.get_stats()
                self.main_window.status_indicator.update_stats(stats)
            
            # Actualizar estado de IA
            if self.ai_manager and hasattr(self.main_window, 'ai_status_tile'):
                ai_status = self.ai_manager.get_status()
                self.main_window.ai_status_tile.update_status(ai_status)
            
            # Actualizar hardware
            if hasattr(self.main_window, 'hardware_monitor'):
                # El hardware monitor se actualiza via eventos
                pass
            
        except Exception as e:
            logger.error(f"❌ Error en actualización periódica: {e}")
    
    async def disconnect_components(self):
        """Desconecta todos los componentes"""
        try:
            logger.info("🔌 Desconectando UI de backend...")
            
            # Detener timer
            self.update_timer.stop()
            
            # Desuscribirse de eventos
            if self.system_controller and hasattr(self.system_controller, 'event_bus'):
                event_bus = self.system_controller.event_bus
                for event_type, callback in self.event_subscriptions:
                    event_bus.unsubscribe(event_type, callback)
            
            self.event_subscriptions.clear()
            self.is_connected = False
            
            logger.info("✅ UI desconectada del backend")
            
        except Exception as e:
            logger.error(f"❌ Error desconectando componentes: {e}")

# Función helper para integrar fácilmente
async def integrate_ui_backend(main_window, system_controller=None, 
                             ai_manager=None, audio_feedback=None) -> UIBackendIntegrator:
    """Función helper para integrar UI con backend"""
    integrator = UIBackendIntegrator(
        main_window=main_window,
        system_controller=system_controller,
        ai_manager=ai_manager,
        audio_feedback=audio_feedback
    )
    
    success = await integrator.connect_components()
    
    if success:
        logger.info("✅ Integración UI ↔ Backend exitosa")
    else:
        logger.error("❌ Fallo en integración UI ↔ Backend")
    
    return integrator

