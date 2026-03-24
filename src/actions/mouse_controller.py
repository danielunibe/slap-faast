import pyautogui
from loguru import logger
import math

# Fail-safe mode (mouse to corner to stop)
pyautogui.FAILSAFE = True

class MouseController:
    """Controlador de mouse y teclado usando PyAutoGUI."""
    
    def __init__(self, screen_w=None, screen_h=None):
        if screen_w is None or screen_h is None:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = screen_w, screen_h
            
        self.smoothing = 0.5
        self._last_x = 0
        self._last_y = 0

    def move_to(self, x_norm, y_norm, smooth=True):
        """Mueve el mouse a coordenadas normalizadas (0.0-1.0)."""
        target_x = int(x_norm * self.screen_w)
        target_y = int(y_norm * self.screen_h) # Y is inverted in screen space usually? MediaPipe is 0 top, 1 bottom. Screen is same.
        
        # Clamp
        target_x = max(0, min(self.screen_w, target_x))
        target_y = max(0, min(self.screen_h, target_y))

        if smooth:
            # Simple lerp
            curr_x, curr_y = pyautogui.position()
            new_x = curr_x + (target_x - curr_x) * self.smoothing
            new_y = curr_y + (target_y - curr_y) * self.smoothing
            pyautogui.moveTo(new_x, new_y)
        else:
            pyautogui.moveTo(target_x, target_y)

    def click(self, button='left'):
        pyautogui.click(button=button)

    def scroll(self, clicks):
        pyautogui.scroll(clicks)
        
    def type_string(self, text):
        pyautogui.write(text)
        
    def press_key(self, key):
        pyautogui.press(key)
