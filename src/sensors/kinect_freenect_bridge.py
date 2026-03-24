"""
Kinect Freenect Bridge - SDK Propio Redistribuible
Usa libfreenect compilado (open source) en lugar del SDK de Microsoft.
"""
import ctypes
from ctypes import c_int, c_void_p, c_uint16, c_uint32, c_double, POINTER, byref
from pathlib import Path
import numpy as np
from loguru import logger

# Ubicación de nuestra DLL compilada
DLL_PATH = Path(__file__).parent / "drivers" / "freenect.dll"

# Estados LED
LED_OFF = 0
LED_GREEN = 1
LED_RED = 2
LED_YELLOW = 3
LED_BLINK_GREEN = 4
LED_BLINK_RED_YELLOW = 6

class KinectFreenectBridge:
    """
    Bridge a libfreenect - 100% redistribuible.
    No depende del SDK de Microsoft.
    """
    
    def __init__(self):
        self._lib = None
        self._ctx = c_void_p()
        self._dev = c_void_p()
        self._connected = False
        
    def initialize(self) -> bool:
        """Carga la DLL e inicializa el contexto freenect."""
        try:
            if not DLL_PATH.exists():
                logger.error(f"DLL no encontrada: {DLL_PATH}")
                return False
                
            self._lib = ctypes.CDLL(str(DLL_PATH))
            logger.info("libfreenect.dll cargada")
            
            # Configurar funciones
            self._setup_functions()
            
            # Inicializar contexto
            ret = self._lib.freenect_init(byref(self._ctx), None)
            if ret < 0:
                logger.error(f"freenect_init falló: {ret}")
                return False
                
            logger.info("Contexto freenect creado")
            
            # Buscar dispositivos
            num_devices = self._lib.freenect_num_devices(self._ctx)
            if num_devices <= 0:
                logger.warning("No se encontraron dispositivos Kinect")
                return False
                
            logger.info(f"Encontrados {num_devices} dispositivo(s) Kinect")
            
            # Abrir primer dispositivo
            ret = self._lib.freenect_open_device(self._ctx, byref(self._dev), 0)
            if ret < 0:
                logger.error(f"freenect_open_device falló: {ret}")
                return False
                
            self._connected = True
            logger.success("✅ Kinect conectado via libfreenect (SDK Propio)")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando: {e}")
            return False
    
    def _setup_functions(self):
        """Configura los tipos de las funciones de la DLL."""
        # freenect_init
        self._lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
        self._lib.freenect_init.restype = c_int
        
        # freenect_shutdown
        self._lib.freenect_shutdown.argtypes = [c_void_p]
        self._lib.freenect_shutdown.restype = c_int
        
        # freenect_num_devices
        self._lib.freenect_num_devices.argtypes = [c_void_p]
        self._lib.freenect_num_devices.restype = c_int
        
        # freenect_open_device
        self._lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
        self._lib.freenect_open_device.restype = c_int
        
        # freenect_close_device
        self._lib.freenect_close_device.argtypes = [c_void_p]
        self._lib.freenect_close_device.restype = c_int
        
        # freenect_set_tilt_degs
        self._lib.freenect_set_tilt_degs.argtypes = [c_void_p, c_double]
        self._lib.freenect_set_tilt_degs.restype = c_int
        
        # freenect_set_led
        self._lib.freenect_set_led.argtypes = [c_void_p, c_int]
        self._lib.freenect_set_led.restype = c_int
    
    def set_tilt(self, degrees: float) -> bool:
        """Mueve el motor del Kinect."""
        if not self._connected:
            return False
        degrees = max(-31, min(31, degrees))
        ret = self._lib.freenect_set_tilt_degs(self._dev, c_double(degrees))
        return ret >= 0
    
    def set_led(self, color: int) -> bool:
        """Cambia el color del LED."""
        if not self._connected:
            return False
        ret = self._lib.freenect_set_led(self._dev, c_int(color))
        return ret >= 0
    
    def shutdown(self):
        """Cierra la conexión."""
        if self._lib and self._connected:
            self._lib.freenect_close_device(self._dev)
            self._lib.freenect_shutdown(self._ctx)
            self._connected = False
            logger.info("Kinect cerrado")
    
    def is_connected(self) -> bool:
        return self._connected


# Test standalone
if __name__ == "__main__":
    print("=== TEST: SDK Propio con libfreenect ===")
    bridge = KinectFreenectBridge()
    
    if bridge.initialize():
        print("LED Verde...")
        bridge.set_led(LED_GREEN)
        
        import time
        time.sleep(1)
        
        print("Motor a +15 grados...")
        bridge.set_tilt(15)
        time.sleep(2)
        
        print("Motor a 0 grados...")
        bridge.set_tilt(0)
        
        print("LED Rojo...")
        bridge.set_led(LED_RED)
        time.sleep(1)
        
        bridge.shutdown()
        print("✅ Test completado")
    else:
        print("❌ No se pudo conectar")
