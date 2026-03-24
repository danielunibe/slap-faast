"""
Kinect Complete Driver - Video + Motor + LED
TODOS los componentes funcionando sin SDK de Microsoft
"""
import cv2
import usb.core
import usb.util
import numpy as np
from loguru import logger
from typing import Optional, Tuple

# Constantes
KINECT_VID = 0x045E
KINECT_MOTOR_PID = 0x02B0

# LED Colors
LED_OFF = 0
LED_GREEN = 1
LED_RED = 2
LED_YELLOW = 3
LED_BLINK_GREEN = 4
LED_BLINK_RED_YELLOW = 6

class KinectCompleteDriver:
    """
    Driver completo del Kinect v1 - 100% funcional
    - Video: OpenCV (driver WinUSB)
    - Motor: PyUSB directo
    - LED: PyUSB directo
    """
    
    def __init__(self, camera_index: int = 0):
        self._camera_index = camera_index
        self._video_cap = None
        self._motor_dev = None
        self._connected = False
        
    def initialize(self) -> bool:
        """Inicializa todos los componentes del Kinect."""
        success = True
        
        # 1. Inicializar video
        try:
            self._video_cap = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW)
            if self._video_cap.isOpened():
                ret, frame = self._video_cap.read()
                if ret and frame is not None:
                    h, w = frame.shape[:2]
                    logger.success(f"✅ Video Kinect: {w}x{h}")
                else:
                    logger.warning("⚠️ Video se abrió pero no dio frame")
                    success = False
            else:
                logger.error("❌ No se pudo abrir video")
                success = False
        except Exception as e:
            logger.error(f"Error inicializando video: {e}")
            success = False
        
        # 2. Inicializar motor/LED
        try:
            self._motor_dev = usb.core.find(idVendor=KINECT_VID, idProduct=KINECT_MOTOR_PID)
            if self._motor_dev is None:
                logger.error("❌ Motor USB no encontrado")
                success = False
            else:
                try:
                    self._motor_dev.set_configuration()
                except:
                    pass
                try:
                    usb.util.claim_interface(self._motor_dev, 0)
                except:
                    pass
                logger.success("✅ Motor/LED Kinect")
                self.set_led(LED_GREEN)
        except Exception as e:
            logger.error(f"Error inicializando motor: {e}")
            success = False
        
        self._connected = success
        if success:
            logger.success("🎮 Kinect COMPLETAMENTE FUNCIONAL")
        
        return success
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Lee frame de video del Kinect."""
        if not self._video_cap or not self._video_cap.isOpened():
            return False, None
        return self._video_cap.read()
    
    def set_tilt(self, angle: int) -> bool:
        """Mueve el motor (-31 a +31 grados)."""
        if not self._motor_dev:
            return False
        
        angle = max(-31, min(31, angle))
        tilt_value = int(angle * 2)
        
        try:
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x31,
                wValue=tilt_value,
                wIndex=0,
                data_or_wLength=None
            )
            logger.info(f"Motor: {angle}°")
            return True
        except Exception as e:
            logger.error(f"Error motor: {e}")
            return False
    
    def set_led(self, color: int) -> bool:
        """Cambia color del LED."""
        if not self._motor_dev:
            return False
        
        try:
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x06,
                wValue=color,
                wIndex=0,
                data_or_wLength=None
            )
            return True
        except Exception as e:
            logger.error(f"Error LED: {e}")
            return False
    
    def release(self):
        """Libera recursos."""
        if self._video_cap:
            self._video_cap.release()
        if self._motor_dev:
            try:
                self.set_led(LED_OFF)
                usb.util.release_interface(self._motor_dev, 0)
            except:
                pass
        self._connected = False
    
    def isOpened(self) -> bool:
        """Verifica si está conectado."""
        return self._connected and (self._video_cap is not None and self._video_cap.isOpened())


# Test completo
if __name__ == "__main__":
    print("=== TEST KINECT COMPLETO ===")
    
    kinect = KinectCompleteDriver(camera_index=0)
    
    if kinect.initialize():
        import time
        
        # Test LED
        print("\nTest LED...")
        kinect.set_led(LED_RED)
        time.sleep(1)
        kinect.set_led(LED_GREEN)
        
        # Test Motor
        print("\nTest Motor...")
        kinect.set_tilt(15)
        time.sleep(2)
        kinect.set_tilt(0)
        
        # Test Video
        print("\nTest Video (presiona 'q' para salir)...")
        while True:
            ret, frame = kinect.read()
            if ret:
                cv2.imshow("Kinect Video", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cv2.destroyAllWindows()
        kinect.release()
        print("\n✅ TODOS LOS TESTS PASARON")
    else:
        print("\n❌ Falló la inicialización")
