
from loguru import logger
from ..core.events import EventBus, Events

class IntentProcessor:
    """
    Procesa texto natural y emite comandos del sistema.
    """
    def __init__(self):
        self.keywords = {
            "luz verde": {"action": "set_led", "value": 1},
            "luz roja": {"action": "set_led", "value": 2},
            "luz amarilla": {"action": "set_led", "value": 3},
            "apagar luz": {"action": "set_led", "value": 0},
            "subir cámara": {"action": "set_tilt", "value": 20},
            "bajar cámara": {"action": "set_tilt", "value": -20},
            "centrar cámara": {"action": "set_tilt", "value": 0},
            "hola": {"action": "greet", "value": None}
        }
        
        # Suscribirse a eventos de voz
        EventBus.subscribe(Events.VOICE_COMMAND, self.process_text)
        logger.info("IntentProcessor inicializado.")

    def process_text(self, text: str):
        """Analiza texto entrante y dispara acciones."""
        text = text.lower()
        logger.debug(f"Procesando intención: '{text}'")
        
        # Búsqueda simple de keywords
        matched = False
        for key, cmd in self.keywords.items():
            if key in text:
                logger.info(f"Intención detectada: {key} -> {cmd}")
                
                # Publicar comando de sistema (Hardware)
                EventBus.publish(Events.SYSTEM_COMMAND, cmd)
                matched = True
                
        if not matched:
            logger.debug("No se detectó intención conocida.")

