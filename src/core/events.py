from enum import Enum
from typing import Callable, List, Dict, Any
from loguru import logger

class Events(Enum):
    """Eventos del sistema Ethyria."""
    FRAME_READY = "frame_ready"          # Nuevo frame de video
    POSE_READY = "pose_ready"            # Datos de tracking (pose, hands, face)
    GESTURE_DETECTED = "gesture_detected" # Gesto reconocido
    CONTEXT_CHANGED = "context_changed"   # Cambio de app activa
    VOICE_COMMAND = "voice_command"       # Comando de voz detectado
    SYSTEM_COMMAND = "system_command"     # Comando de sistema (hardware control)
    SYSTEM_STATUS = "system_status"       # Cambio de estado del sistema
    ERROR_OCCURRED = "error_occurred"     # Error crítico

class EventBus:
    """Bus de eventos simple Pub/Sub."""
    _subscribers: Dict[Events, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: Events, callback: Callable):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)
        # logger.debug(f"Subscribed to {event_type.value}: {callback.__name__}")

    @classmethod
    def publish(cls, event_type: Events, data: Any = None):
        if event_type in cls._subscribers:
            for callback in cls._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error handling event {event_type.value}: {e}")
