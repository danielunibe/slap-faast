"""
Kinect Video Driver - Lectura ISO Directa
Intento final: Control manual del USB para video
"""
import usb.core
import usb.util
import numpy as np
import struct
from loguru import logger

# VID/PID
KINECT_VID = 0x045E
KINECT_CAMERA_PID = 0x02AE

class KinectVideoUSB:
    """Driver de video usando lectura ISO directa."""
    
    def __init__(self):
        self._dev = None
        self._running = False
        
    def initialize(self) -> bool:
        """Inicializa el dispositivo de cámara."""
        try:
            logger.info("Buscando Kinect Camera (VID:045E, PID:02AE)...")
            
            # Buscar TODOS los dispositivos Microsoft primero
            all_ms = list(usb.core.find(find_all=True, idVendor=KINECT_VID))
            logger.info(f"Dispositivos Microsoft encontrados: {len(all_ms)}")
            for d in all_ms:
                logger.info(f"  - PID: 0x{d.idProduct:04X}")
            
            # Buscar cámara específicamente
            self._dev = usb.core.find(idVendor=KINECT_VID, idProduct=KINECT_CAMERA_PID)
            
            if self._dev is None:
                logger.error("Kinect Camera no encontrada (PID 02AE)")
                logger.info("¿Está conectado y con driver WinUSB/libusbK?")
                return False
            
            logger.info(f"Kinect Camera encontrada: Bus {self._dev.bus}, Address {self._dev.address}")
            
            # Configurar
            try:
                self._dev.set_configuration()
                logger.success("Configuración set")
            except usb.core.USBError as e:
                logger.warning(f"Set configuration: {e} (puede estar OK)")
            
            # Claim interface 0
            try:
                usb.util.claim_interface(self._dev, 0)
                logger.success("Interface 0 claimed")
            except usb.core.USBError as e:
                logger.warning(f"Claim interface: {e}")
            
            # CRÍTICO: Configurar Alt Setting 1 para habilitar ancho de banda ISO
            # Método 1: Control transfer manual (si el método directo falla)
            try:
                # USB SET_INTERFACE request: 0x0B
                # wValue = Alt Setting (1)
                # wIndex = Interface (0)
                result = self._dev.ctrl_transfer(
                    bmRequestType=0x01,  # Standard request to interface
                    bRequest=0x0B,       # SET_INTERFACE
                    wValue=1,            # Alt Setting 1
                    wIndex=0,            # Interface 0
                    data_or_wLength=0
                )
                logger.success("✅ Alt Setting 1 activado via control transfer")
            except Exception as e:
                logger.error(f"Error configurando Alt Setting: {e}")
                return False
            
            # Enviar comando de inicio de stream (protocolo libfreenect)
            try:
                # Comando: Start video stream
                # Request 0x00, Value 0x00 (según libfreenect)
                self._dev.ctrl_transfer(
                    bmRequestType=0x40,
                    bRequest=0x00,
                    wValue=0x00,
                    wIndex=0,
                    data_or_wLength=None
                )
                logger.info("Comando start stream enviado")
            except Exception as e:
                logger.warning(f"Start stream command: {e}")
            
            self._running = True
            logger.success("🎥 Kinect Video inicializado")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando: {repr(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_frame(self) -> tuple:
        """Intenta leer un frame del endpoint ISO."""
        if not self._running:
            return False, None
        
        try:
            # Endpoint 0x81 = ISO IN para video
            # Tamaño típico: 1920 bytes por paquete
            data = self._dev.read(0x81, 1920, timeout=1000)
            
            if len(data) > 0:
                logger.info(f"✅ Recibidos {len(data)} bytes del endpoint ISO")
                # TODO: Convertir Bayer raw a RGB
                return True, data
            else:
                return False, None
                
        except usb.core.USBTimeoutError:
            logger.debug("Timeout (normal si no hay data)")
            return False, None
        except usb.core.USBError as e:
            logger.error(f"Error ISO read: {e}")
            return False, None
    
    def test_read(self, num_attempts=10):
        """Test de lectura múltiple."""
        logger.info(f"Intentando leer {num_attempts} veces...")
        success_count = 0
        
        for i in range(num_attempts):
            ret, data = self.read_frame()
            if ret:
                success_count += 1
                logger.success(f"Intento {i+1}: {len(data)} bytes")
            else:
                logger.debug(f"Intento {i+1}: Sin data")
        
        logger.info(f"Resultado: {success_count}/{num_attempts} exitosos")
        return success_count > 0
    
    def shutdown(self):
        """Cierra conexión."""
        if self._dev:
            try:
                usb.util.release_interface(self._dev, 0)
            except:
                pass
        self._running = False


# Test
if __name__ == "__main__":
    print("=== KINECT VIDEO USB TEST ===\n")
    
    driver = KinectVideoUSB()
    
    if driver.initialize():
        print("\n✅ Inicialización exitosa")
        print("Intentando leer video...\n")
        
        if driver.test_read(20):
            print("\n🎉 ¡VIDEO FUNCIONANDO!")
            print("Se recibieron datos del Kinect.")
        else:
            print("\n❌ No se recibieron datos de video")
            print("El endpoint ISO no está enviando información.")
        
        driver.shutdown()
    else:
        print("\n❌ Falló la inicialización")
        print("Verifica drivers y conexión.")
