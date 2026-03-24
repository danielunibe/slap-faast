"""
KinectUSBControl - Control directo del motor y LED del Kinect v1 via USB
Sin depender del SDK de Microsoft.

Basado en el protocolo documentado por libfreenect.
Requiere: pyusb y driver WinUSB (via Zadig)
"""
import usb.core
import usb.util
from loguru import logger
from typing import Optional

class KinectUSBControl:
    """Control USB directo del Kinect v1 Motor y LED."""
    
    # Kinect v1 Motor Device
    VID = 0x045e  # Microsoft
    PID_MOTOR = 0x02b0  # Kinect Motor
    
    # LED Modes
    LED_OFF = 0
    LED_GREEN = 1
    LED_RED = 2
    LED_YELLOW = 3
    LED_BLINK_GREEN = 4
    LED_BLINK_RED_YELLOW = 6
    
    def __init__(self):
        self._dev: Optional[usb.core.Device] = None
        self._connected = False
        self._initialize()
    
    def _initialize(self):
        """Busca y conecta al dispositivo motor del Kinect."""
        logger.info("🔌 Buscando Kinect Motor via USB...")
        
        try:
            self._dev = usb.core.find(idVendor=self.VID, idProduct=self.PID_MOTOR)
            
            if self._dev is None:
                logger.warning("Kinect Motor no encontrado (VID:045e PID:02b0)")
                logger.info("Asegúrate de usar Zadig para instalar driver WinUSB")
                return
            
            # Intentar configurar el dispositivo
            try:
                self._dev.set_configuration()
            except usb.core.USBError as e:
                # En Windows, puede fallar si ya está configurado
                logger.debug(f"set_configuration: {e}")
            
            self._connected = True
            logger.success("✅ Kinect Motor conectado via USB directo")
            
        except Exception as e:
            logger.error(f"Error inicializando USB: {e}")
            self._connected = False
    
    def is_connected(self) -> bool:
        """Verifica si el motor está conectado."""
        return self._connected and self._dev is not None
    
    def set_tilt(self, angle: int) -> bool:
        """
        Ajusta el ángulo del motor.
        
        Args:
            angle: Ángulo en grados (-27 a +27)
            
        Returns:
            True si el comando fue enviado exitosamente
        """
        if not self.is_connected():
            logger.warning("Motor no conectado")
            return False
        
        # Clamp angle to safe limits
        angle = max(-27, min(27, angle))
        
        try:
            # USB Control Transfer
            # bmRequestType: 0x40 = Vendor, Host-to-Device
            # bRequest: 0x31 = SET_TILT_ANGLE
            # wValue: angle * 2 (el Kinect usa media-grados internamente)
            # wIndex: 0
            self._dev.ctrl_transfer(0x40, 0x31, angle * 2, 0, [])
            logger.info(f"🔄 Motor ajustado a {angle}°")
            return True
            
        except usb.core.USBError as e:
            logger.error(f"Error enviando comando de tilt: {e}")
            return False
    
    def set_led(self, mode: int) -> bool:
        """
        Controla el LED del Kinect.
        
        Args:
            mode: Modo de LED (usar constantes LED_*)
            
        Returns:
            True si el comando fue enviado exitosamente
        """
        if not self.is_connected():
            logger.warning("Motor no conectado")
            return False
        
        try:
            # USB Control Transfer
            # bRequest: 0x06 = SET_LED
            self._dev.ctrl_transfer(0x40, 0x06, mode, 0, [])
            logger.info(f"💡 LED cambiado a modo {mode}")
            return True
            
        except usb.core.USBError as e:
            logger.error(f"Error enviando comando de LED: {e}")
            return False
    
    def get_accelerometer(self) -> Optional[tuple]:
        """
        Lee los datos del acelerómetro.
        
        Returns:
            Tuple (x, y, z) o None si falla
        """
        if not self.is_connected():
            return None
        
        try:
            # bRequest: 0x32 = GET_ACCELEROMETER
            data = self._dev.ctrl_transfer(0xC0, 0x32, 0, 0, 10)
            if len(data) >= 6:
                import struct
                x, y, z = struct.unpack('<hhh', bytes(data[:6]))
                return (x, y, z)
        except:
            pass
        return None
    
    def release(self):
        """Libera el dispositivo USB."""
        if self._dev:
            try:
                usb.util.dispose_resources(self._dev)
            except:
                pass
        self._connected = False
        logger.info("Kinect USB Control liberado")


# Test si se ejecuta directamente
if __name__ == "__main__":
    ctrl = KinectUSBControl()
    if ctrl.is_connected():
        print("Probando motor...")
        ctrl.set_tilt(10)
        import time
        time.sleep(2)
        ctrl.set_tilt(0)
        
        print("Probando LED...")
        ctrl.set_led(KinectUSBControl.LED_GREEN)
        time.sleep(1)
        ctrl.set_led(KinectUSBControl.LED_OFF)
        
        ctrl.release()
    else:
        print("No se pudo conectar al Kinect Motor")
