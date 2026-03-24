"""
Kinect Native Bridge - Ejecuta comandos via executable C++
Solución híbrida: C++ para USB/Hardware, Python para todo lo demás
"""
import subprocess
from pathlib import Path
from loguru import logger

EXE_PATH = Path(__file__).parent / "kinect_native" / "kinect_control.exe"

class KinectNativeBridge:
    """Bridge que ejecuta comandos C++ nativos."""
    
    def __init__(self):
        self._connected = False
        
    def initialize(self) -> bool:
        """Verifica conexión con Kinect."""
        if not EXE_PATH.exists():
            logger.error(f"Ejecutable no encontrado: {EXE_PATH}")
            return False
            
        try:
            result = subprocess.run(
                [str(EXE_PATH), "init"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "OK:CONNECTED" in result.stdout:
                self._connected = True
                logger.success("✅ Kinect conectado via C++ nativo")
                return True
            else:
                logger.error(f"Error: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error ejecutando: {e}")
            return False
    
    def set_tilt(self, degrees: float) -> bool:
        """Mueve el motor."""
        if not self._connected:
            return False
        try:
            degrees = max(-31, min(31, degrees))
            result = subprocess.run(
                [str(EXE_PATH), "tilt", str(degrees)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "OK:TILT" in result.stdout
        except:
            return False
    
    def set_led(self, color: int) -> bool:
        """Cambia LED."""
        if not self._connected:
            return False
        try:
            result = subprocess.run(
                [str(EXE_PATH), "led", str(color)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "OK:LED" in result.stdout
        except:
            return False
    
    def is_connected(self) -> bool:
        return self._connected


# Test
if __name__ == "__main__":
    bridge = KinectNativeBridge()
    if bridge.initialize():
        print("LED Verde...")
        bridge.set_led(1)
        print("Motor +15...")
        bridge.set_tilt(15)
        print("✅ Funciona!")
    else:
        print("❌ No conectó")
