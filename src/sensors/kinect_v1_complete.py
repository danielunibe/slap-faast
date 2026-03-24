"""
Kinect v1 Driver Completo - Video + Motor + LED
Combina acceso USB directo para hardware control y video capture.
"""
import cv2
import usb.core
import usb.util
import numpy as np
from loguru import logger
from typing import Optional, Tuple
import struct

class KinectV1DriverComplete:
    """
    Driver completo para Kinect v1 con soporte de:
    - Video RGB (via USB raw o DirectShow fallback)
    - Motor tilt
    - LED control
    - Audio (via Windows)
    """
    
    # VID/PID del Kinect v1
    KINECT_CAMERA_VID = 0x045e
    KINECT_CAMERA_PID = 0x02ae
    KINECT_MOTOR_VID = 0x045e
    KINECT_MOTOR_PID = 0x02b0
    
    def __init__(self):
        self._camera_dev = None
        self._motor_dev = None
        self._video_capture = None
        self._video_method = None
        self._connected = False
        self._last_frame = None
        self._initialize()
    
    def _initialize(self):
        logger.info("🔍 Inicializando Kinect v1 Completo...")
        
        # Inicializar hardware USB (motor/LED)
        self._init_usb_hardware()
        
        # Inicializar video
        self._init_video()
    
    def _init_usb_hardware(self):
        """Inicializa acceso USB para motor y LED."""
        try:
            # Buscar dispositivo de cámara (para futura impl. de video raw)
            self._camera_dev = usb.core.find(
                idVendor=self.KINECT_CAMERA_VID,
                idProduct=self.KINECT_CAMERA_PID
            )
            
            if self._camera_dev:
                logger.info(f"✅ Kinect Camera USB detectado")
            
            # Buscar dispositivo de motor
            self._motor_dev = usb.core.find(
                idVendor=self.KINECT_MOTOR_VID,
                idProduct=self.KINECT_MOTOR_PID
            )
            
            if self._motor_dev:
                logger.success("✅ Kinect Motor USB conectado")
                self._connected = True
            
        except Exception as e:
            logger.error(f"Error inicializando USB hardware: {e}")
    
    def _init_video(self):
        """Inicializa captura de video (DirectShow fallback)."""
        # Por ahora usamos DirectShow como fallback
        # TODO: Implementar lectura USB raw del endpoint de video
        
        for idx in range(5):
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Verificar que no sea ruido
                        if np.std(frame) < 70:  # Umbral de ruido
                            self._video_capture = cap
                            self._video_method = f"DirectShow[{idx}]"
                            w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                            h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                            logger.success(f"✅ Video capturado vía {self._video_method} ({w}x{h})")
                            return
                        cap.release()
                    else:
                        cap.release()
            except Exception as e:
                logger.debug(f"Error probando cámara {idx}: {e}")
        
        logger.warning("⚠️ No se pudo inicializar video - solo disponible control de hardware")
    
    def isOpened(self) -> bool:
        """Retorna True si al menos el hardware USB está conectado."""
        return self._connected and self._motor_dev is not None
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Lee frame de video (si está disponible)."""
        if self._video_capture and self._video_capture.isOpened():
            ret, frame = self._video_capture.read()
            if ret and frame is not None:
                self._last_frame = frame
                
                # Overlay Source Info
                info_text = f"SOURCE: {self._video_method}"
                color = (0, 255, 0) if "Kinect" in info_text or "Xbox" in info_text else (0, 165, 255)
                cv2.putText(frame, info_text, (20, frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                           
                return True, frame
        
        # Retornar último frame si está disponible
        if self._last_frame is not None:
            return True, self._last_frame
        
        return False, None
    
    def set_led(self, color: int) -> bool:
        """
        Controla el LED del Kinect.
        color: 0=Off, 1=Green, 2=Red, 3=Yellow, 4=Blink Yellow, 5=Blink Green, 6=Blink Red/Yellow
        """
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
            logger.success(f"✅ LED cambiado a color {color}")
            return True
        except Exception as e:
            logger.error(f"Error cambiando LED: {e}")
            return False
    
    def set_tilt(self, angle: int) -> bool:
        """
        Cambia la inclinación del motor del Kinect.
        angle: -31 a +31 grados
        """
        if not self._motor_dev:
            return False
        
        try:
            # Limitar ángulo
            angle = max(-31, min(31, angle))
            
            # Convertir ángulo a valor de motor
            motor_value = int(angle * 2)
            
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x31,
                wValue=motor_value,
                wIndex=0,
                data_or_wLength=None
            )
            logger.success(f"✅ Motor inclinado a {angle}°")
            return True
        except Exception as e:
            logger.error(f"Error moviendo motor: {e}")
            return False
    
    def get_video_resolution(self) -> Tuple[int, int]:
        """Retorna resolución del video actual."""
        if self._video_capture and self._video_capture.isOpened():
            w = int(self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (w, h)
        return (0, 0)
    
    def get_fps(self) -> float:
        """Retorna FPS del video."""
        if self._video_capture and self._video_capture.isOpened():
            return self._video_capture.get(cv2.CAP_PROP_FPS)
        return 0.0
    
    def release(self):
        """Libera todos los recursos."""
        # Apagar LED y centrar motor
        if self._motor_dev:
            try:
                self.set_led(0)
                self.set_tilt(0)
            except:
                pass
        
        # Liberar video
        if self._video_capture:
            self._video_capture.release()
        
        # Liberar dispositivos USB
        if self._camera_dev:
            try:
                usb.util.dispose_resources(self._camera_dev)
            except:
                pass
        
        if self._motor_dev:
            try:
                usb.util.dispose_resources(self._motor_dev)
            except:
                pass
        
        logger.info("Kinect v1 Driver Completo liberado")


# Test simple
if __name__ == "__main__":
    kinect = KinectV1DriverComplete()
    
    if kinect.isOpened():
        print("✅ Kinect conectado!")
        
        # Test LED
        kinect.set_led(1)
        
        # Test video
        ret, frame = kinect.read()
        if ret:
            print(f"✅ Frame capturado: {frame.shape}")
            cv2.imwrite("kinect_complete_test.jpg", frame)
        
        kinect.release()
    else:
        print("❌ Kinect no conectado")
