"""
AI Manager para Slap!Faast v2.0
Coordinador principal de todos los componentes IA para experiencia Tony Stark
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import threading
from pathlib import Path

from .ollama_client import OllamaClient
from .whisper_local import WhisperLocal, VoiceCommand
from .vision_local import VisionLocal, ScreenContext
from .intent_processor import IntentProcessor, MultimodalInput, ProcessedIntent
from ..core.events import EventBus, Event
from ..recognition.data_structures import GestureMatch

logger = logging.getLogger(__name__)

class AISystemState(Enum):
    """Estados del sistema IA"""
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AICapability(Enum):
    """Capacidades IA disponibles"""
    VOICE_RECOGNITION = "voice_recognition"
    VISUAL_ANALYSIS = "visual_analysis"
    INTENT_PROCESSING = "intent_processing"
    NATURAL_LANGUAGE = "natural_language"
    GESTURE_FUSION = "gesture_fusion"
    SMART_ACTIONS = "smart_actions"
    CONTEXT_AWARENESS = "context_awareness"

@dataclass
class AISystemStatus:
    """Estado completo del sistema IA"""
    state: AISystemState
    capabilities: List[AICapability]
    components_status: Dict[str, bool]
    performance_metrics: Dict[str, float]
    last_update: datetime
    error_message: Optional[str] = None

@dataclass
class TonyStarkCommand:
    """Comando completo estilo Tony Stark"""
    voice_input: Optional[VoiceCommand] = None
    gesture_input: Optional[GestureMatch] = None
    visual_context: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    session_id: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class AIResponse:
    """Respuesta completa del sistema IA"""
    intent: ProcessedIntent
    execution_plan: List[Dict[str, Any]]
    confidence: float
    processing_time: float
    components_used: List[str]
    requires_confirmation: bool
    explanation: str
    fallback_options: List[Dict[str, Any]]

class LocalAIManager:
    """Coordinador principal de todos los componentes IA"""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or EventBus()
        
        # Componentes IA
        self.ollama_client = None
        self.whisper_local = None
        self.vision_local = None
        self.intent_processor = None
        
        # Estado del sistema
        self.system_state = AISystemState.OFFLINE
        self.capabilities = []
        self.components_status = {
            'ollama': False,
            'whisper': False,
            'vision': False,
            'intent_processor': False
        }
        
        # Configuración
        self.config = {
            'auto_initialize_components': True,
            'enable_continuous_monitoring': True,
            'voice_activation_enabled': True,
            'visual_context_enabled': True,
            'intent_fusion_enabled': True,
            'performance_monitoring': True,
            'max_processing_time': 10.0,  # segundos
            'confidence_threshold': 0.6,
            'confirmation_threshold': 0.8
        }
        
        # Monitoreo y estadísticas
        self.performance_metrics = {
            'commands_processed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_processing_time': 0.0,
            'average_confidence': 0.0,
            'uptime_seconds': 0.0,
            'components_restarts': 0
        }
        
        # Callbacks para eventos
        self.callbacks = {
            'on_command_received': [],
            'on_intent_processed': [],
            'on_action_executed': [],
            'on_error_occurred': [],
            'on_state_changed': []
        }
        
        # Threading para procesamiento asíncrono
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
        self.processor_task = None
        
        # Contexto de sesión
        self.session_context = {
            'current_session_id': None,
            'active_commands': {},
            'recent_intents': [],
            'user_preferences': {},
            'performance_history': []
        }
        
        self.start_time = None
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Inicializa todos los componentes IA"""
        try:
            logger.info("🤖 Inicializando AI Manager...")
            self.system_state = AISystemState.INITIALIZING
            self.start_time = datetime.now()
            
            # Inicializar componentes en orden de dependencia
            success = True
            
            # 1. Ollama Client
            if self.config['auto_initialize_components']:
                logger.info("🧠 Inicializando Ollama Client...")
                self.ollama_client = OllamaClient()
                if await self.ollama_client.connect():
                    self.components_status['ollama'] = True
                    self.capabilities.append(AICapability.NATURAL_LANGUAGE)
                    logger.info("✅ Ollama Client inicializado")
                else:
                    logger.warning("⚠️ Ollama Client no disponible")
                    success = False
            
            # 2. Whisper Local
            if self.config['voice_activation_enabled']:
                logger.info("🎤 Inicializando Whisper Local...")
                self.whisper_local = WhisperLocal()
                if await self.whisper_local.initialize():
                    self.components_status['whisper'] = True
                    self.capabilities.append(AICapability.VOICE_RECOGNITION)
                    logger.info("✅ Whisper Local inicializado")
                else:
                    logger.warning("⚠️ Whisper Local no disponible")
            
            # 3. Vision Local
            if self.config['visual_context_enabled']:
                logger.info("👁️ Inicializando Vision Local...")
                self.vision_local = VisionLocal()
                if await self.vision_local.initialize():
                    self.components_status['vision'] = True
                    self.capabilities.extend([
                        AICapability.VISUAL_ANALYSIS,
                        AICapability.CONTEXT_AWARENESS
                    ])
                    logger.info("✅ Vision Local inicializado")
                else:
                    logger.warning("⚠️ Vision Local no disponible")
            
            # 4. Intent Processor
            if self.config['intent_fusion_enabled']:
                logger.info("🧠 Inicializando Intent Processor...")
                self.intent_processor = IntentProcessor(self.ollama_client)
                if await self.intent_processor.initialize():
                    self.components_status['intent_processor'] = True
                    self.capabilities.extend([
                        AICapability.INTENT_PROCESSING,
                        AICapability.GESTURE_FUSION,
                        AICapability.SMART_ACTIONS
                    ])
                    logger.info("✅ Intent Processor inicializado")
                else:
                    logger.warning("⚠️ Intent Processor no disponible")
                    success = False
            
            # Iniciar procesamiento asíncrono
            await self._start_async_processing()
            
            # Iniciar monitoreo continuo si está habilitado
            if self.config['enable_continuous_monitoring']:
                await self._start_continuous_monitoring()
            
            # Determinar estado final
            if success and self.components_status['ollama'] and self.components_status['intent_processor']:
                self.system_state = AISystemState.READY
                logger.info("🚀 AI Manager inicializado exitosamente")
                await self._emit_event('ai_manager_ready', {'capabilities': [c.value for c in self.capabilities]})
            else:
                self.system_state = AISystemState.ERROR
                logger.error("❌ AI Manager inicializado con errores")
            
            self.is_initialized = True
            return success
            
        except Exception as e:
            logger.error(f"❌ Error inicializando AI Manager: {e}")
            self.system_state = AISystemState.ERROR
            return False
    
    async def process_tony_stark_command(self, 
                                       voice_input: Optional[VoiceCommand] = None,
                                       gesture_input: Optional[GestureMatch] = None,
                                       session_id: str = None) -> Optional[AIResponse]:
        """
        Procesa un comando completo estilo Tony Stark
        """
        if self.system_state != AISystemState.READY:
            logger.warning("⚠️ AI Manager no está listo para procesar comandos")
            return None
        
        start_time = time.time()
        session_id = session_id or f"session_{int(time.time())}"
        
        try:
            # Crear comando Tony Stark
            visual_context = None
            if self.vision_local and self.config['visual_context_enabled']:
                visual_context = await self.vision_local.get_application_context()
            
            command = TonyStarkCommand(
                voice_input=voice_input,
                gesture_input=gesture_input,
                visual_context=visual_context,
                session_id=session_id
            )
            
            # Emitir evento de comando recibido
            await self._emit_event('command_received', {
                'session_id': session_id,
                'has_voice': voice_input is not None,
                'has_gesture': gesture_input is not None,
                'has_visual': visual_context is not None
            })
            
            # Procesar con Intent Processor
            if not self.intent_processor:
                raise Exception("Intent Processor no disponible")
            
            self.system_state = AISystemState.PROCESSING
            
            multimodal_input = MultimodalInput(
                voice_command=voice_input,
                gesture_match=gesture_input,
                visual_context=visual_context
            )
            
            processed_intent = await self.intent_processor.process_multimodal_input(multimodal_input)
            
            # Generar plan de ejecución
            execution_plan = await self._generate_execution_plan(processed_intent, command)
            
            # Crear respuesta IA
            processing_time = time.time() - start_time
            
            ai_response = AIResponse(
                intent=processed_intent,
                execution_plan=execution_plan,
                confidence=processed_intent.confidence,
                processing_time=processing_time,
                components_used=self._get_components_used(command),
                requires_confirmation=processed_intent.requires_confirmation,
                explanation=processed_intent.explanation,
                fallback_options=self._generate_fallback_options(processed_intent)
            )
            
            # Actualizar contexto de sesión
            self._update_session_context(session_id, command, ai_response)
            
            # Actualizar métricas
            self._update_performance_metrics(ai_response)
            
            # Emitir evento de intención procesada
            await self._emit_event('intent_processed', {
                'session_id': session_id,
                'intent_type': processed_intent.intent_type.value,
                'confidence': processed_intent.confidence,
                'processing_time': processing_time,
                'requires_confirmation': processed_intent.requires_confirmation
            })
            
            self.system_state = AISystemState.READY
            
            logger.info(f"🧠 Comando Tony Stark procesado: {processed_intent.intent_type.value} "
                       f"(confianza: {processed_intent.confidence:.2f}, "
                       f"tiempo: {processing_time:.2f}s)")
            
            return ai_response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Error procesando comando Tony Stark: {e}")
            
            self.system_state = AISystemState.READY
            self.performance_metrics['failed_executions'] += 1
            
            await self._emit_event('error_occurred', {
                'session_id': session_id,
                'error': str(e),
                'processing_time': processing_time
            })
            
            return None
    
    async def _generate_execution_plan(self, 
                                     processed_intent: ProcessedIntent,
                                     command: TonyStarkCommand) -> List[Dict[str, Any]]:
        """Genera plan de ejecución detallado"""
        execution_plan = []
        
        try:
            # Convertir acciones inteligentes a plan de ejecución
            for i, action in enumerate(processed_intent.actions):
                execution_step = {
                    'step': i + 1,
                    'action_type': action.type,
                    'target': action.target,
                    'parameters': action.parameters,
                    'priority': action.priority,
                    'estimated_duration': action.estimated_duration,
                    'requires_confirmation': action.requires_confirmation,
                    'description': action.description,
                    'execution_method': self._determine_execution_method(action.type),
                    'rollback_possible': self._can_rollback_action(action.type)
                }
                
                execution_plan.append(execution_step)
            
            # Ordenar por prioridad
            execution_plan.sort(key=lambda x: x['priority'], reverse=True)
            
            # Añadir pasos de confirmación si es necesario
            if processed_intent.requires_confirmation:
                confirmation_step = {
                    'step': 0,
                    'action_type': 'confirmation_request',
                    'target': 'user',
                    'parameters': {
                        'message': f"¿Confirmas ejecutar: {processed_intent.explanation}?",
                        'timeout': 10.0
                    },
                    'priority': 10,
                    'estimated_duration': 0.5,
                    'requires_confirmation': False,
                    'description': 'Solicitar confirmación del usuario',
                    'execution_method': 'ui_dialog',
                    'rollback_possible': True
                }
                execution_plan.insert(0, confirmation_step)
            
        except Exception as e:
            logger.error(f"❌ Error generando plan de ejecución: {e}")
        
        return execution_plan
    
    def _determine_execution_method(self, action_type: str) -> str:
        """Determina el método de ejecución para un tipo de acción"""
        method_mapping = {
            'open_application': 'system_command',
            'close_application': 'system_command',
            'key_press': 'input_simulation',
            'mouse_click': 'input_simulation',
            'organize_windows': 'window_management',
            'system_command': 'shell_execution',
            'notification': 'ui_notification',
            'custom_action': 'script_execution'
        }
        
        return method_mapping.get(action_type, 'unknown')
    
    def _can_rollback_action(self, action_type: str) -> bool:
        """Determina si una acción puede deshacerse"""
        rollback_actions = {
            'open_application', 'key_press', 'mouse_click', 
            'organize_windows', 'notification'
        }
        
        return action_type in rollback_actions
    
    def _get_components_used(self, command: TonyStarkCommand) -> List[str]:
        """Obtiene lista de componentes utilizados"""
        components = []
        
        if command.voice_input and self.components_status['whisper']:
            components.append('whisper')
        
        if command.gesture_input:
            components.append('gesture_recognition')
        
        if command.visual_context and self.components_status['vision']:
            components.append('vision')
        
        if self.components_status['ollama']:
            components.append('ollama')
        
        if self.components_status['intent_processor']:
            components.append('intent_processor')
        
        return components
    
    def _generate_fallback_options(self, processed_intent: ProcessedIntent) -> List[Dict[str, Any]]:
        """Genera opciones de respaldo"""
        fallback_options = []
        
        # Si la confianza es baja, ofrecer alternativas
        if processed_intent.confidence < self.config['confidence_threshold']:
            fallback_options.append({
                'type': 'retry_with_clarification',
                'description': 'Solicitar aclaración del comando',
                'confidence': 0.8
            })
            
            fallback_options.append({
                'type': 'show_similar_commands',
                'description': 'Mostrar comandos similares disponibles',
                'confidence': 0.7
            })
        
        # Siempre ofrecer opción manual
        fallback_options.append({
            'type': 'manual_execution',
            'description': 'Ejecutar manualmente desde interfaz',
            'confidence': 1.0
        })
        
        return fallback_options
    
    async def execute_smart_actions(self, ai_response: AIResponse) -> Dict[str, Any]:
        """Ejecuta las acciones inteligentes generadas"""
        if not ai_response or not ai_response.execution_plan:
            return {'success': False, 'error': 'No hay plan de ejecución'}
        
        execution_results = {
            'success': True,
            'executed_steps': [],
            'failed_steps': [],
            'total_time': 0.0,
            'rollback_performed': False
        }
        
        start_time = time.time()
        
        try:
            for step in ai_response.execution_plan:
                step_start = time.time()
                
                try:
                    # Ejecutar paso individual
                    step_result = await self._execute_single_step(step)
                    
                    step_duration = time.time() - step_start
                    step_result['duration'] = step_duration
                    step_result['step_info'] = step
                    
                    if step_result['success']:
                        execution_results['executed_steps'].append(step_result)
                        logger.info(f"✅ Paso ejecutado: {step['description']}")
                    else:
                        execution_results['failed_steps'].append(step_result)
                        logger.warning(f"⚠️ Paso falló: {step['description']} - {step_result.get('error', 'Error desconocido')}")
                        
                        # Si es un paso crítico, detener ejecución
                        if step.get('priority', 0) >= 8:
                            execution_results['success'] = False
                            break
                    
                except Exception as e:
                    step_duration = time.time() - step_start
                    step_result = {
                        'success': False,
                        'error': str(e),
                        'duration': step_duration,
                        'step_info': step
                    }
                    execution_results['failed_steps'].append(step_result)
                    logger.error(f"❌ Error ejecutando paso: {step['description']} - {e}")
            
            execution_results['total_time'] = time.time() - start_time
            
            # Si hay fallos críticos, intentar rollback
            if not execution_results['success'] and execution_results['executed_steps']:
                logger.info("🔄 Intentando rollback de acciones ejecutadas...")
                rollback_success = await self._perform_rollback(execution_results['executed_steps'])
                execution_results['rollback_performed'] = rollback_success
            
            # Actualizar métricas
            if execution_results['success']:
                self.performance_metrics['successful_executions'] += 1
            else:
                self.performance_metrics['failed_executions'] += 1
            
            # Emitir evento de ejecución
            await self._emit_event('action_executed', {
                'success': execution_results['success'],
                'steps_executed': len(execution_results['executed_steps']),
                'steps_failed': len(execution_results['failed_steps']),
                'total_time': execution_results['total_time']
            })
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando acciones: {e}")
            execution_results['success'] = False
            execution_results['error'] = str(e)
            execution_results['total_time'] = time.time() - start_time
        
        return execution_results
    
    async def _execute_single_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un paso individual del plan"""
        execution_method = step.get('execution_method', 'unknown')
        
        try:
            if execution_method == 'system_command':
                return await self._execute_system_command(step)
            elif execution_method == 'input_simulation':
                return await self._execute_input_simulation(step)
            elif execution_method == 'window_management':
                return await self._execute_window_management(step)
            elif execution_method == 'ui_notification':
                return await self._execute_ui_notification(step)
            elif execution_method == 'ui_dialog':
                return await self._execute_ui_dialog(step)
            else:
                return {
                    'success': False,
                    'error': f'Método de ejecución no soportado: {execution_method}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_system_command(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta comando del sistema"""
        # Implementación básica - en producción usaría subprocess o similar
        logger.info(f"🖥️ Ejecutando comando del sistema: {step['target']}")
        
        # Simular ejecución exitosa
        await asyncio.sleep(0.1)
        
        return {
            'success': True,
            'result': f"Comando {step['target']} ejecutado",
            'method': 'system_command'
        }
    
    async def _execute_input_simulation(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta simulación de entrada"""
        logger.info(f"⌨️ Simulando entrada: {step['action_type']}")
        
        # Simular ejecución exitosa
        await asyncio.sleep(0.05)
        
        return {
            'success': True,
            'result': f"Entrada {step['action_type']} simulada",
            'method': 'input_simulation'
        }
    
    async def _execute_window_management(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta gestión de ventanas"""
        logger.info(f"🪟 Gestionando ventanas: {step['target']}")
        
        # Simular ejecución exitosa
        await asyncio.sleep(0.2)
        
        return {
            'success': True,
            'result': f"Ventanas organizadas: {step['target']}",
            'method': 'window_management'
        }
    
    async def _execute_ui_notification(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta notificación UI"""
        message = step.get('parameters', {}).get('message', 'Notificación')
        logger.info(f"🔔 Mostrando notificación: {message}")
        
        # Emitir evento de notificación
        await self._emit_event('notification_requested', {
            'message': message,
            'type': step.get('parameters', {}).get('type', 'info')
        })
        
        return {
            'success': True,
            'result': f"Notificación mostrada: {message}",
            'method': 'ui_notification'
        }
    
    async def _execute_ui_dialog(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta diálogo UI"""
        message = step.get('parameters', {}).get('message', '¿Continuar?')
        logger.info(f"💬 Mostrando diálogo: {message}")
        
        # Emitir evento de diálogo
        await self._emit_event('dialog_requested', {
            'message': message,
            'timeout': step.get('parameters', {}).get('timeout', 10.0)
        })
        
        # Simular respuesta positiva del usuario
        await asyncio.sleep(0.5)
        
        return {
            'success': True,
            'result': f"Diálogo confirmado: {message}",
            'method': 'ui_dialog'
        }
    
    async def _perform_rollback(self, executed_steps: List[Dict[str, Any]]) -> bool:
        """Realiza rollback de pasos ejecutados"""
        try:
            logger.info("🔄 Iniciando rollback...")
            
            # Rollback en orden inverso
            for step_result in reversed(executed_steps):
                step_info = step_result.get('step_info', {})
                
                if step_info.get('rollback_possible', False):
                    logger.info(f"↩️ Deshaciendo: {step_info.get('description', 'Paso desconocido')}")
                    # Aquí iría la lógica específica de rollback
                    await asyncio.sleep(0.1)
            
            logger.info("✅ Rollback completado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en rollback: {e}")
            return False
    
    async def _start_async_processing(self):
        """Inicia procesamiento asíncrono de comandos"""
        async def process_queue():
            while True:
                try:
                    # Esperar por comandos en la cola
                    command_data = await self.processing_queue.get()
                    
                    if command_data is None:  # Señal de parada
                        break
                    
                    # Procesar comando
                    await self.process_tony_stark_command(**command_data)
                    
                except Exception as e:
                    logger.error(f"❌ Error en procesamiento asíncrono: {e}")
        
        self.processor_task = asyncio.create_task(process_queue())
        self.is_processing = True
        logger.info("🔄 Procesamiento asíncrono iniciado")
    
    async def _start_continuous_monitoring(self):
        """Inicia monitoreo continuo del sistema"""
        if self.vision_local:
            await self.vision_local.start_continuous_monitoring(interval=3.0)
            logger.info("📊 Monitoreo continuo iniciado")
    
    def _update_session_context(self, 
                              session_id: str, 
                              command: TonyStarkCommand, 
                              response: AIResponse):
        """Actualiza contexto de sesión"""
        self.session_context['current_session_id'] = session_id
        
        # Añadir a comandos activos
        self.session_context['active_commands'][session_id] = {
            'command': command,
            'response': response,
            'timestamp': datetime.now()
        }
        
        # Añadir a intenciones recientes
        self.session_context['recent_intents'].append({
            'session_id': session_id,
            'intent_type': response.intent.intent_type.value,
            'confidence': response.confidence,
            'timestamp': datetime.now()
        })
        
        # Mantener solo las últimas 10 intenciones
        if len(self.session_context['recent_intents']) > 10:
            self.session_context['recent_intents'] = self.session_context['recent_intents'][-10:]
    
    def _update_performance_metrics(self, response: AIResponse):
        """Actualiza métricas de rendimiento"""
        self.performance_metrics['commands_processed'] += 1
        
        # Actualizar tiempo promedio
        count = self.performance_metrics['commands_processed']
        current_avg = self.performance_metrics['average_processing_time']
        self.performance_metrics['average_processing_time'] = (
            (current_avg * (count - 1) + response.processing_time) / count
        )
        
        # Actualizar confianza promedio
        current_conf_avg = self.performance_metrics['average_confidence']
        self.performance_metrics['average_confidence'] = (
            (current_conf_avg * (count - 1) + response.confidence) / count
        )
        
        # Actualizar uptime
        if self.start_time:
            self.performance_metrics['uptime_seconds'] = (
                datetime.now() - self.start_time
            ).total_seconds()
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emite evento a través del bus de eventos"""
        try:
            event = Event(
                type=f"ai_manager.{event_type}",
                data=data,
                timestamp=datetime.now()
            )
            await self.event_bus.emit(event)
            
            # Ejecutar callbacks registrados
            for callback in self.callbacks.get(f'on_{event_type}', []):
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"❌ Error en callback {event_type}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error emitiendo evento {event_type}: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registra callback para eventos"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        
        self.callbacks[event_type].append(callback)
        logger.info(f"📝 Callback registrado para {event_type}")
    
    def get_system_status(self) -> AISystemStatus:
        """Obtiene estado completo del sistema"""
        return AISystemStatus(
            state=self.system_state,
            capabilities=self.capabilities.copy(),
            components_status=self.components_status.copy(),
            performance_metrics=self.performance_metrics.copy(),
            last_update=datetime.now()
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento"""
        return self.performance_metrics.copy()
    
    def get_session_context(self) -> Dict[str, Any]:
        """Obtiene contexto de sesión"""
        return self.session_context.copy()
    
    def update_config(self, config: Dict[str, Any]):
        """Actualiza configuración del sistema"""
        self.config.update(config)
        logger.info(f"⚙️ Configuración actualizada: {config}")
    
    async def restart_component(self, component_name: str) -> bool:
        """Reinicia un componente específico"""
        try:
            logger.info(f"🔄 Reiniciando componente: {component_name}")
            
            if component_name == 'ollama' and self.ollama_client:
                await self.ollama_client.disconnect()
                success = await self.ollama_client.connect()
                self.components_status['ollama'] = success
                
            elif component_name == 'whisper' and self.whisper_local:
                await self.whisper_local.cleanup()
                success = await self.whisper_local.initialize()
                self.components_status['whisper'] = success
                
            elif component_name == 'vision' and self.vision_local:
                await self.vision_local.cleanup()
                success = await self.vision_local.initialize()
                self.components_status['vision'] = success
                
            elif component_name == 'intent_processor' and self.intent_processor:
                await self.intent_processor.cleanup()
                success = await self.intent_processor.initialize()
                self.components_status['intent_processor'] = success
                
            else:
                logger.warning(f"⚠️ Componente desconocido: {component_name}")
                return False
            
            if success:
                self.performance_metrics['components_restarts'] += 1
                logger.info(f"✅ Componente {component_name} reiniciado exitosamente")
            else:
                logger.error(f"❌ Error reiniciando componente {component_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error reiniciando {component_name}: {e}")
            return False
    
    async def cleanup(self):
        """Limpia recursos del AI Manager"""
        logger.info("🧹 Limpiando AI Manager...")
        
        # Detener procesamiento asíncrono
        if self.is_processing and self.processor_task:
            await self.processing_queue.put(None)  # Señal de parada
            await self.processor_task
            self.is_processing = False
        
        # Limpiar componentes
        if self.ollama_client:
            await self.ollama_client.disconnect()
        
        if self.whisper_local:
            await self.whisper_local.cleanup()
        
        if self.vision_local:
            await self.vision_local.cleanup()
        
        if self.intent_processor:
            await self.intent_processor.cleanup()
        
        # Limpiar contexto
        self.session_context.clear()
        self.callbacks.clear()
        
        self.system_state = AISystemState.OFFLINE
        logger.info("✅ AI Manager limpiado")

# Ejemplo de uso
if __name__ == "__main__":
    async def test_ai_manager():
        """Función de prueba"""
        ai_manager = LocalAIManager()
        
        try:
            # Inicializar
            if not await ai_manager.initialize():
                print("❌ No se pudo inicializar AI Manager")
                return
            
            # Mostrar estado
            status = ai_manager.get_system_status()
            print(f"🤖 Estado del sistema: {status.state.value}")
            print(f"🎯 Capacidades: {[c.value for c in status.capabilities]}")
            print(f"🔧 Componentes: {status.components_status}")
            
            # Simular comando Tony Stark
            from ..whisper_local import VoiceCommand
            from ..recognition.data_structures import GestureMatch
            
            voice_cmd = VoiceCommand(
                text="JARVIS, abre Visual Studio Code",
                confidence=0.9,
                language="es",
                timestamp=datetime.now(),
                duration=2.5
            )
            
            gesture_match = GestureMatch(
                gesture_name="point_right",
                confidence=0.8,
                timestamp=datetime.now()
            )
            
            print(f"\n🎬 Procesando comando Tony Stark...")
            response = await ai_manager.process_tony_stark_command(
                voice_input=voice_cmd,
                gesture_input=gesture_match
            )
            
            if response:
                print(f"✅ Comando procesado:")
                print(f"  Intención: {response.intent.intent_type.value}")
                print(f"  Confianza: {response.confidence:.2f}")
                print(f"  Tiempo: {response.processing_time:.2f}s")
                print(f"  Componentes usados: {response.components_used}")
                print(f"  Plan de ejecución: {len(response.execution_plan)} pasos")
                
                # Ejecutar acciones
                print(f"\n⚡ Ejecutando acciones...")
                execution_result = await ai_manager.execute_smart_actions(response)
                print(f"  Éxito: {execution_result['success']}")
                print(f"  Pasos ejecutados: {len(execution_result['executed_steps'])}")
                print(f"  Tiempo total: {execution_result['total_time']:.2f}s")
            
            # Mostrar métricas
            metrics = ai_manager.get_performance_metrics()
            print(f"\n📊 Métricas:")
            print(f"  Comandos procesados: {metrics['commands_processed']}")
            print(f"  Ejecuciones exitosas: {metrics['successful_executions']}")
            print(f"  Tiempo promedio: {metrics['average_processing_time']:.3f}s")
            
        finally:
            await ai_manager.cleanup()
    
    # Ejecutar prueba
    asyncio.run(test_ai_manager())

