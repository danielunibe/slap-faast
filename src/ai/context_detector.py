import time
import ctypes
from typing import Optional
from loguru import logger

# Cypes loading
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class ContextDetector:
    """Detecta la ventana y aplicación activa para ajustar el contexto."""
    
    CONTEXT_MAPPING = {
        "spotify": "MEDIA",
        "vlc": "MEDIA",
        "chrome": "BROWSER",
        "firefox": "BROWSER",
        "edge": "BROWSER",
        "code": "WORK",
        "pycharm": "WORK",
        "discord": "SOCIAL",
        "slack": "SOCIAL",
        "whatsapp": "SOCIAL",
        "steam": "GAMING",
        "minecraft": "GAMING",
        "league": "GAMING"
    }

    def __init__(self):
        self._current_context = "DESKTOP"
        self._last_check = 0
        self._cache_duration = 1.0
    
    def get_active_window_title(self) -> str:
        """Obtiene el título de la ventana activa usando ctypes."""
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value

    def get_context(self) -> str:
        """Retorna el contexto actual (MEDIA, WORK, GAMING, etc.)"""
        now = time.time()
        if now - self._last_check < self._cache_duration:
            return self._current_context
            
        try:
            window_title = self.get_active_window_title().lower()
            
            # Simple keyword matching on title since we don't have psutil/pid here easily without more ctypes
            # Ideally we'd use GetWindowThreadProcessId -> OpenProcess -> GetModuleFileNameEx
            # But title is often enough for a prototype
            
            context_found = False
            for key, context in self.CONTEXT_MAPPING.items():
                if key in window_title:
                    self._current_context = context
                    context_found = True
                    break
            
            if not context_found:
                if "youtube" in window_title or "netflix" in window_title:
                    self._current_context = "MEDIA"
                elif "game" in window_title:
                    self._current_context = "GAMING"
                elif "visual studio" in window_title:
                     self._current_context = "WORK"
                else:
                    self._current_context = "DESKTOP"
                
        except Exception as e:
            logger.debug(f"Error checking context: {e}")
            pass
            
        self._last_check = now
        return self._current_context
