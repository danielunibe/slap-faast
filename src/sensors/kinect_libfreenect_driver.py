"""
Kinect Video Driver usando nuestra DLL compilada de libfreenect
¡ESTO ES NUESTRO SDK PROPIO!
"""
import ctypes
from ctypes import c_int, c_void_p, POINTER, byref
from pathlib import Path
import numpy as np
from loguru import logger

# Ruta a nuestra DLL compilada  
DLL_PATH = Path(__file__).parent.parent.parent / "freenect.dll"

class KinectLibfreenectDriver:
    """Driver de video Kinect usando nuestra DLL compilada."""
    
    def __init__(self):
        self._lib = None
        self._ctx = c_void_p()
        self._dev = c_void_p()
        self._connected = False
        
    def initialize(self) -> bool:
        """Inicializa libfreenect."""
        try:
            if not DLL_PATH.exists():
                logger.error(f"DLL no encontrada: {DLL_PATH}")
                return False
            
            # Cargar DLL
            self._lib = ctypes.CDLL(str(DLL_PATH))
            logger.info("✅ freenect.dll cargada")
            
            # Configurar funciones
            self._lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
            self._lib.freenect_init.restype = c_int
            
            self._lib.freenect_shutdown.argtypes = [c_void_p]
            self._lib.freenect_shutdown.restype = c_int
            
            self._lib.freenect_num_devices.argtypes = [c_void_p]
            self._lib.freenect_num_devices.restype = c_int
            
            self._lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
            self._lib.freenect_open_device.restype = c_int
            
            self._lib.freenect_close_device.argtypes = [c_void_p]
            self._lib.freenect_close_device.restype = c_int
            
            # Inicializar contexto
            ret = self._lib.freenect_init(byref(self._ctx), None)
            if ret < 0:
                logger.error(f"freenect_init falló: {ret}")
                return False
            
            logger.success("✅ Contexto libfreenect inicializado")
            
            # Contar dispositivos
            num = self._lib.freenect_num_devices(self._ctx)
            if num <= 0:
                logger.warning("No se encontraron dispositivos Kinect")
                self._lib.freenect_shutdown(self._ctx)
                return False
            
            logger.info(f"✅ Encontrados {num} dispositivo(s) Kinect")
            
            # Abrir dispositivo
            ret = self._lib.freenect_open_device(self._ctx, byref(self._dev), 0)
            if ret < 0:
                logger.error(f"freenect_open_device falló: {ret}")
                self._lib.freenect_shutdown(self._ctx)
                return False
            
            self._connected = True
            logger.success("🎥 KINECT VIDEO CONECTADO VIA LIBFREENECT!")
            return True
            
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def shutdown(self):
        """Cierra conexión."""
        if self._lib and self._connected:
            self._lib.freenect_close_device(self._dev)
            self._lib.freenect_shutdown(self._ctx)
            self._connected = False
            logger.info("Kinect cerrado")
    
    def is_connected(self) -> bool:
        return self._connected


# TEST
if __name__ == "__main__":
    print("=== TEST LIBFREENECT DLL COMPILADA ===\n")
    
    driver = KinectLibfreenectDriver()
    
    if driver.initialize():
        print("\n✅ ¡ÉXITO!")
        print("La DLL funciona y detectó el Kinect.")
        print("Próximo paso: Implementar lectura de frames.")
        driver.shutdown()
    else:
        print("\n❌ Falló inicialización")
        print("Verifica el Kinect esté conectado.")
