"""
Driver Kinect Definitivo - Usando PyUSB directo con protocolo OpenKinect
Basado en reverse engineering de libfreenect - FUNCIONAL
"""
import usb.core
import usb.util
import struct
from loguru import logger

# VID/PID
KINECT_VID = 0x045E
KINECT_MOTOR_PID = 0x02B0
KINECT_CAMERA_PID = 0x02AE

# LED Colors
LED_OFF = 0
LED_GREEN = 1
LED_RED = 2
LED_YELLOW = 3
LED_BLINK_GREEN = 4
LED_BLINK_RED_YELLOW = 6

class KinectDirectDriver:
    """Driver USB directo sin dependencias externas - Solo motor/LED por ahora."""
    
    def __init__(self):
        self._motor_dev = None
        self._connected = False
        
    def initialize(self) -> bool:
        """Conecta con el motor/LED del Kinect."""
        try:
            # Buscar dispositivo motor
            self._motor_dev = usb.core.find(idVendor=KINECT_VID, idProduct=KINECT_MOTOR_PID)
            
            if self._motor_dev is None:
                logger.error("Kinect Motor no encontrado")
                return False
            
            # Configurar
            try:
                self._motor_dev.set_configuration()
            except:
                pass  # Ya configurado
            
            # Claim interface
            try:
                usb.util.claim_interface(self._motor_dev, 0)
            except:
                pass  # Ya claimed
            
            self._connected = True
            logger.success("✅ Kinect Motor/LED conectado")
            
            # LED verde inicial
            self.set_led(LED_GREEN)
            
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando: {e}")
            return False
    
    def set_tilt(self, angle: int) -> bool:
        """Mueve el motor (-31 a +31 grados)."""
        if not self._connected:
            return False
            
        angle = max(-31, min(31, angle))
        
        try:
            # Convertir ángulo a valor para el motor
            # Fórmula de libfreenect
            tilt_value = int(angle * 2)
            
            # Control transfer para mover motor
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x31,
                wValue=tilt_value,
                wIndex=0,
                data_or_wLength=None
            )
            
            logger.info(f"Motor movido a {angle}°")
            return True
            
        except Exception as e:
            logger.error(f"Error moviendo motor: {e}")
            return False
    
    def set_led(self, color: int) -> bool:
        """Cambia color del LED."""
        if not self._connected:
            return False
            
        try:
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x06,
                wValue=color,
                wIndex=0,
                data_or_wLength=None
            )
            
            logger.success(f"LED: color {color}")
            return True
            
        except Exception as e:
            logger.error(f"Error cambiando LED: {e}")
            return False
    
    def shutdown(self):
        """Cierra conexión."""
        if self._motor_dev:
            try:
                self.set_led(LED_OFF)
                usb.util.release_interface(self._motor_dev, 0)
            except:
                pass
        self._connected = False
    
    def is_connected(self) -> bool:
        return self._connected


# Test
if __name__ == "__main__":
    print("=== Kinect Direct Driver Test ===")
    driver = KinectDirectDriver()
    
    if driver.initialize():
        import time
        
        print("LED Rojo...")
        driver.set_led(LED_RED)
        time.sleep(1)
        
        print("LED Verde...")
        driver.set_led(LED_GREEN)
        time.sleep(1)
        
        print("Motor +20°...")
        driver.set_tilt(20)
        time.sleep(2)
        
        print("Motor 0°...")
        driver.set_tilt(0)
        time.sleep(1)
        
        print("LED parpadeo...")
        driver.set_led(LED_BLINK_GREEN)
        time.sleep(2)
        
        driver.shutdown()
        print("✅ Test completado!")
    else:
        print("❌ No conectó. Verifica que el Kinect esté enchufado.")
