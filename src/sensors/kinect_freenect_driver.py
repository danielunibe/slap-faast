from .kinect_v1_driver import KinectV1Driver
import ctypes
from ctypes import c_int, c_void_p, c_double, POINTER, byref, create_string_buffer, Structure, c_int16, c_int8
import numpy as np
import cv2
from pathlib import Path
from loguru import logger
from typing import Optional, Tuple
import time

# Re-using the ctypes structures
class FreenectRawTiltState(Structure):
    _fields_ = [
        ("accelerometer_x", c_int16),
        ("accelerometer_y", c_int16),
        ("accelerometer_z", c_int16),
        ("tilt_angle", c_int8),
        ("tilt_status", c_int) 
    ]

class KinectFreenectDriver:
    """
    Driver NATIVO que usa libfreenect.dll directamente en el proceso principal.
    Reemplaza la necesidad de kinect_server.py + NetworkDriver.
    """
    
    def __init__(self):
        self.lib = None
        self.ctx = c_void_p()
        self.dev = c_void_p()
        self.video_buffer = None
        self.depth_buffer = None
        self.running = False
        self.latest_video = None
        self.latest_depth = None
        
        # Path hardcodeado al DLL conocido (ajustar si es necesario)
        self.DLL_PATH = Path("g:/Otros ordenadores/Mi PC/E/en ejecucion ahora/Slap!Faast/freenect.dll")
        
        if not self._initialize():
            logger.error("Fallo inicializacion de KinectFreenectDriver")
            
    def _initialize(self):
        try:
            if not self.DLL_PATH.exists():
                logger.error(f"DLL no encontrado en {self.DLL_PATH}")
                return False
                
            self.lib = ctypes.CDLL(str(self.DLL_PATH))
            
            # --- Configurar firmas (igual que server) ---
            self.lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
            self.lib.freenect_init.restype = c_int
            self.lib.freenect_num_devices.argtypes = [c_void_p]
            self.lib.freenect_num_devices.restype = c_int
            self.lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
            self.lib.freenect_open_device.restype = c_int
            self.lib.freenect_close_device.argtypes = [c_void_p]
            self.lib.freenect_close_device.restype = c_int
            self.lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
            self.lib.freenect_set_video_buffer.restype = c_int
            self.lib.freenect_set_depth_buffer.argtypes = [c_void_p, c_void_p]
            self.lib.freenect_set_depth_buffer.restype = c_int
            self.lib.freenect_start_video.argtypes = [c_void_p]
            self.lib.freenect_start_video.restype = c_int
            self.lib.freenect_start_depth.argtypes = [c_void_p]
            self.lib.freenect_start_depth.restype = c_int
            self.lib.freenect_process_events.argtypes = [c_void_p]
            self.lib.freenect_process_events.restype = c_int
            self.lib.freenect_set_led.argtypes = [c_void_p, c_int]
            self.lib.freenect_set_led.restype = c_int
            self.lib.freenect_set_tilt_degs.argtypes = [c_void_p, c_double]
            self.lib.freenect_set_tilt_degs.restype = c_int
            self.lib.freenect_select_subdevices.argtypes = [c_void_p, c_int]
            self.lib.freenect_select_subdevices.restype = None
            
            # Init Context
            self.lib.freenect_init(byref(self.ctx), None)
            
            # Select ALL devices (Motor + Camera) = 0x01 | 0x02 = 0x03
            self.lib.freenect_select_subdevices(self.ctx, 0x03)
            
            num = self.lib.freenect_num_devices(self.ctx)
            if num <= 0:
                logger.warning("No se detectaron Kinects (libfreenect)")
                return False
                
            ret = self.lib.freenect_open_device(self.ctx, byref(self.dev), 0)
            if ret < 0:
                logger.error("Error abriendo dispositivo Kinect")
                return False
            
            # Buffers
            self.video_buffer = create_string_buffer(640 * 480 * 3)
            self.depth_buffer = create_string_buffer(640 * 480 * 2)
            
            self.lib.freenect_set_video_buffer(self.dev, ctypes.cast(self.video_buffer, c_void_p))
            self.lib.freenect_set_depth_buffer(self.dev, ctypes.cast(self.depth_buffer, c_void_p))
            
            self.lib.freenect_start_video(self.dev)
            self.lib.freenect_start_depth(self.dev)
            
            self.running = True
            logger.success("KinectFreenectDriver inicializado correctamente (Single Process)")
            return True
            
        except Exception as e:
            logger.error(f"Excepcion en driver freenect: {e}")
            return False

    def isOpened(self) -> bool:
        return self.running and self.dev is not None
        
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee el frame más reciente.
        NOTA: En arquitectura single-thread, necesitamos llamar a process_events AQUI.
        """
        if not self.running: return False, None
        
        try:
            # Procesar eventos USB (CRÍTICO)
            self.lib.freenect_process_events(self.ctx)
            
            # 1. Leer Video
            video_data = np.frombuffer(self.video_buffer.raw, dtype=np.uint8)
            if video_data.sum() > 0:
                frame = video_data.reshape((480, 640, 3))
                self.latest_video = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
            # 2. Leer Depth (Ignoramos el return por ahora, solo actualizamos interno si quisieramos usarlo)
            # depth_data = np.frombuffer(self.depth_buffer.raw, dtype=np.uint16)
            # ...
            
            if self.latest_video is not None:
                return True, self.latest_video
                
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            
        return False, None

    def release(self):
        self.running = False
        if self.lib and self.dev:
            self.lib.freenect_stop_video(self.dev)
            self.lib.freenect_stop_depth(self.dev)
            self.lib.freenect_close_device(self.dev)
            self.lib.freenect_shutdown(self.ctx)
        logger.info("KinectFreenectDriver liberado")

    # === CONTROLES ===
    def set_elevation(self, angle: int):
        if self.dev:
            self.lib.freenect_set_tilt_degs(self.dev, c_double(angle))
            
    def set_led(self, mode: int): # mode int 0-6
        if self.dev:
            try:
                # Convert str input to int if necessary
                if isinstance(mode, str):
                    mode_map = {'OFF': 0, 'GREEN': 1, 'RED': 2, 'YELLOW': 3, 'BLINK': 4}
                    mode = mode_map.get(mode.upper(), 1)
                self.lib.freenect_set_led(self.dev, int(mode))
            except:
                pass
