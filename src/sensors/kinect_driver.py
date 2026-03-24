from pykinect2 import PyKinectV2
from pykinect2.PyKinectRuntime import PyKinectRuntime
import numpy as np
import cv2
from loguru import logger

class KinectDriver:
    def __init__(self):
        logger.info("Inicializando Driver PyKinect2...")
        self._kinect = PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
        self._last_frame = None
        
    def isOpened(self):
        return self._kinect is not None

    def read(self):
        if self._kinect.has_new_color_frame():
            frame = self._kinect.get_last_color_frame()
            # PyKinect devuelve un vector plano, hay que redimensionar
            # Formato BGRA (1080x1920)
            frame = frame.reshape((1080, 1920, 4)).astype(np.uint8)
            
            # Convertir a RGB/BGR para OpenCV (Quitamos Alpha)
            frame = frame[:, :, 0:3] 
            
            # Opcional: Redimensionar para rendimiento (Slap!Faast usa 720p optimo)
            frame = cv2.resize(frame, (1280, 720))
            
            self._last_frame = frame
            return True, frame
        
        # Si no hay frame nuevo, devolver el último si existe (para no bloquear UI)
        if self._last_frame is not None:
            return True, self._last_frame
            
        return False, None

    def release(self):
        if self._kinect:
            self._kinect.close()
            self._kinect = None
