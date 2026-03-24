import cv2
import requests
import numpy as np
from loguru import logger
from typing import Optional, Tuple
from ..core.config import Config

class KinectNetworkDriver:
    """
    Driver que conecta con el Kinect Server local (http://localhost:5001)
    para evitar conflictos de USB.
    """
    
    URL_VIDEO = "http://localhost:5001/video_feed"
    URL_API = "http://localhost:5001/api"
    
    def __init__(self):
        self._capture = None
        self._connected = False
        self._dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self._initialize()
    
    def _initialize(self):
        logger.info(f"🌐 Conectando a Kinect Network Driver ({self.URL_VIDEO})...")
        
        # Verificar si el servidor responde
        try:
            resp = requests.get(f"{self.URL_API}/status", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("connected"):
                    logger.success("✅ Servidor Kinect detectado y hardware listo.")
                    self._connected = True
            else:
                logger.warning(f"Servidor respondió {resp.status_code}")
        except Exception as e:
            logger.warning(f"No se pudo conectar al servidor Kinect: {e}")
            return

        if self._connected:
            # OpenCV maneja MJPEG streams nativamente
            self._capture = cv2.VideoCapture(self.URL_VIDEO)
            if self._capture.isOpened():
                logger.success("✅ Stream de video conectado via Network.")
            else:
                logger.error("❌ Fallo al abrir stream de video.")

    def isOpened(self) -> bool:
        return self._capture is not None and self._capture.isOpened()
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self._capture:
            ret, frame = self._capture.read()
            if ret and frame is not None:
                return True, frame
            else:
                # Si el stream falla, intentar reconectar (simple) o retornar falso
                return False, None
        return False, None

    def release(self):
        if self._capture:
            self._capture.release()
        logger.info("KinectNetworkDriver liberado")

    # === GOD MODE CONTROLS (PROXY) ===
    
    def set_elevation(self, angle: int) -> bool:
        try:
            requests.get(f"{self.URL_API}/tilt/{angle}", timeout=1)
            return True
        except:
            return False

    def set_led(self, color_code: int) -> bool:
        # Mapeo de colores si es necesario, o pasar int directo
        # El server espera int mode
        try:
            requests.get(f"{self.URL_API}/led/{color_code}", timeout=1)
            return True
        except:
            return False
