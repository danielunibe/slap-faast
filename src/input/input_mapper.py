from loguru import logger
from ..core.events import EventBus, Events
from ..actions.mouse_controller import MouseController

class InputMapper:
    """Mapea eventos del sistema a acciones de control (Mouse/Teclado)."""
    
    def __init__(self):
        self._mouse = MouseController()
        self._is_enabled = True
        self._setup_listeners()

    def _setup_listeners(self):
        EventBus.subscribe(Events.VOICE_COMMAND, self._on_voice)
        EventBus.subscribe(Events.GESTURE_DETECTED, self._on_gesture)
        # EventBus.subscribe(Events.POSE_READY, self._on_pose) # Too noisy for direct mapping without gesture logic

    def _on_voice(self, text: str):
        if not self._is_enabled: return
        
        cmd = text.lower()
        if "click" in cmd:
            self._mouse.click('left')
        elif "derecho" in cmd:
            self._mouse.click('right')
        elif "arriba" in cmd:
            self._mouse.scroll(200)
        elif "abajo" in cmd:
            self._mouse.scroll(-200)
        elif "escribir" in cmd:
            content = cmd.replace("escribir", "").strip()
            self._mouse.type_string(content)

    def _on_gesture(self, gesture_data):
        # Placeholder for gesture mapping
        pass
