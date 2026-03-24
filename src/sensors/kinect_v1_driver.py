"""
Kinect v1 Driver for Slap!Faast
100% SDK-Free - Uses DirectShow for video + USB directo para motor/LED.
"""
import cv2
from loguru import logger
from typing import Optional, Tuple
import numpy as np

class KinectV1Driver:
    """
    Driver para Kinect v1 SIN dependencias de Microsoft SDK.
    - Video: DirectShow (cámara USB genérica)
    - Motor/LED: Control USB directo via pyusb
    """
    
    def __init__(self):
        self._capture = None
        self._method = None
        self._last_frame = None
        self._usb_control = None
        self._initialize()
    
    def _initialize(self):
        logger.info("🔍 Inicializando KinectV1Driver (Sin SDK)...")
        
        # 1. Control USB para motor/LED
        self._init_usb_control()
        
        # 2. Video via DirectShow (evitando index 0 = laptop)
        if self._try_directshow():
            return
            
        logger.warning("⚠️ Video no disponible. Motor/LED pueden funcionar si USB está conectado.")
    
    def _init_usb_control(self):
        """Inicializa control USB directo para motor/LED."""
        try:
            from .kinect_usb_control import KinectUSBControl
            self._usb_control = KinectUSBControl()
            if self._usb_control.is_connected():
                logger.success("🎮 Control USB activo (Motor/LED)")
        except ImportError:
            logger.warning("KinectUSBControl no disponible - instala pyusb")
        except Exception as e:
            logger.warning(f"USB Control falló: {e}")
    
    def _try_directshow(self) -> bool:
        """Busca el Kinect usando DirectShow (saltando index 0)."""
        try:
            for idx in range(1, 5):
                logger.debug(f"Probando cámara índice {idx}...")
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    
                    if w > 0 and h > 0:
                        ret, _ = cap.read()
                        if ret:
                            cap.release()
                            self._capture = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                            self._method = f"DirectShow[{idx}]"
                            logger.success(f"✅ Kinect video en índice {idx} ({int(w)}x{int(h)})")
                            return True
                    cap.release()
        except Exception as e:
            logger.debug(f"DirectShow error: {e}")
        return False
    
    def isOpened(self) -> bool:
        """Video está disponible."""
        return self._capture is not None and self._capture.isOpened()
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Lee un frame de video."""
        if self._capture:
            return self._capture.read()
        return False, None
    
    def release(self):
        """Libera recursos."""
        if self._capture:
            self._capture.release()
        if self._usb_control:
            self._usb_control.release()
        logger.info("KinectV1Driver liberado.")

    # === GOD MODE CONTROLS (USB Directo) ===
    
    def set_elevation(self, angle: int) -> bool:
        """Ajusta el ángulo del motor (-27 a +27 grados)."""
        if self._usb_control and self._usb_control.is_connected():
            return self._usb_control.set_tilt(angle)
        logger.warning("Control de motor no disponible (USB no conectado)")
        return False

    def set_led(self, color: str) -> bool:
        """
        Controla el LED del Kinect.
        Opciones: 'OFF', 'GREEN', 'RED', 'YELLOW', 'BLINK_GREEN', 'BLINK_RED_YELLOW'
        """
        if not self._usb_control or not self._usb_control.is_connected():
            logger.warning("Control LED no disponible (USB no conectado)")
            return False
        
        modes = {
            'OFF': 0, 'GREEN': 1, 'RED': 2, 'YELLOW': 3,
            'BLINK_GREEN': 4, 'BLINK_RED_YELLOW': 6
        }
        return self._usb_control.set_led(modes.get(color.upper(), 0))


# Test si se ejecuta directamente
if __name__ == "__main__":
    driver = KinectV1Driver()
    
    # Test Motor
    if driver._usb_control and driver._usb_control.is_connected():
        print("Moviendo motor...")
        driver.set_elevation(15)
        import time
        time.sleep(2)
        driver.set_elevation(0)
    
    # Test Video
    if driver.isOpened():
        ret, frame = driver.read()
        if ret:
            cv2.imwrite("kinect_test.jpg", frame)
            print(f"Frame: {frame.shape}")
    
    driver.release()
