"""
Kinect Video Driver COMPLETO usando libfreenect compilado
"""
import ctypes
from ctypes import c_int, c_void_p, c_uint8, c_uint32, POINTER, CFUNCTYPE, byref
from pathlib import Path
import numpy as np
from loguru import logger
import cv2

# Ruta a nuestra DLL
DLL_PATH = Path(__file__).parent.parent.parent / "freenect.dll"

# Callback type para video
VIDEO_CALLBACK = CFUNCTYPE(None, c_void_p, c_void_p, c_uint32)

class KinectVideoDriver:
    """Driver completo de video Kinect con nuestra DLL."""
    
    def __init__(self):
        self._lib = None
        self._ctx = c_void_p()
        self._dev = c_void_p()
        self._connected = False
        self._video_frame = None
        
    def initialize(self) -> bool:
        """Inicializa libfreenect."""
        print(f"DEBUG: Initializing KinectVideoDriver. DLL Path: {DLL_PATH}")
        try:
            if not DLL_PATH.exists():
                print(f"DEBUG: DLL NOT FOUND at {DLL_PATH}")
                logger.error(f"DLL no encontrada: {DLL_PATH}")
                return False
            
            print("DEBUG: DLL found. Loading CDLL...")
            self._lib = ctypes.CDLL(str(DLL_PATH))
            print("DEBUG: CDLL loaded.")
            logger.info("✅ DLL cargada")
            
            # Setup funciones básicas
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
            
            # Setup funciones de video
            self._lib.freenect_set_video_mode.argtypes = [c_void_p, c_int, c_int, c_int]
            self._lib.freenect_set_video_mode.restype = c_int
            
            self._lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
            self._lib.freenect_set_video_buffer.restype = c_int
            
            self._lib.freenect_set_video_callback.argtypes = [c_void_p, VIDEO_CALLBACK]
            self._lib.freenect_set_video_callback.restype = c_int
            
            self._lib.freenect_start_video.argtypes = [c_void_p]
            self._lib.freenect_start_video.restype = c_int
            
            self._lib.freenect_stop_video.argtypes = [c_void_p]
            self._lib.freenect_stop_video.restype = c_int
            
            self._lib.freenect_process_events.argtypes = [c_void_p]
            self._lib.freenect_process_events.restype = c_int
            
            # Inicializar
            print("DEBUG: Calling freenect_init...")
            ret = self._lib.freenect_init(byref(self._ctx), None)
            if ret < 0:
                print(f"DEBUG: freenect_init failed: {ret}")
                logger.error(f"Init falló: {ret}")
                return False
            
            print("DEBUG: Checking num devices...")
            num = self._lib.freenect_num_devices(self._ctx)
            print(f"DEBUG: Num devices: {num}")
            if num <= 0:
                logger.warning("No se encontraron Kinects")
                print("DEBUG: No devices found.")
                self._lib.freenect_shutdown(self._ctx)
                return False
            
            logger.info(f"✅ Encontrados {num} Kinect(s)")
            
            print("DEBUG: Opening device...")
            ret = self._lib.freenect_open_device(self._ctx, byref(self._dev), 0)
            if ret < 0:
                print(f"DEBUG: Open device failed: {ret}")
                logger.error(f"Open falló: {ret}")
                self._lib.freenect_shutdown(self._ctx)
                return False
            
            # CRÍTICO: Configurar formato de video
            # Formato: 0 = RGB, Resolución: 0 = MEDIUM (640x480)
            # logger.info("Configurando formato de video...")
            # ret = self._lib.freenect_set_video_mode(self._dev, 0, 0, 0)
            # if ret < 0:
            #     logger.warning(f"Set video mode warning: {ret}")
            
            # Configurar callback de video
            @VIDEO_CALLBACK
            def video_callback(dev, data, timestamp):
                # Copiar datos a numpy array
                # RGB: 640x480x3 = 921600 bytes
                try:
                    buffer = ctypes.string_at(data, 640 * 480 * 3)
                    frame = np.frombuffer(buffer, dtype=np.uint8)
                    frame = frame.reshape((480, 640, 3))
                    self._video_frame = frame.copy()
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            self._video_callback_ref = video_callback
            self._lib.freenect_set_video_callback(self._dev, video_callback)
            
            # Iniciar video
            print("DEBUG: Starting video...")
            ret = self._lib.freenect_start_video(self._dev)
            if ret < 0:
                print(f"DEBUG: Start video failed: {ret}")
                logger.error(f"Start video falló: {ret}")
                return False
            
            self._connected = True
            
            # Iniciar thread de eventos
            import threading
            self._running = True
            def event_loop():
                while self._running:
                    self._lib.freenect_process_events(self._ctx)
            
            self._event_thread = threading.Thread(target=event_loop, daemon=True)
            self._event_thread.start()
            
            logger.success("🎥 VIDEO KINECT INICIADO!")
            return True
            
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read(self):
        """Lee un frame de video."""
        if not self._connected:
            return False, None
        
        try:
            if self._video_frame is not None:
                # Convertir RGB a BGR para OpenCV
                frame_bgr = cv2.cvtColor(self._video_frame, cv2.COLOR_RGB2BGR)
                return True, frame_bgr
            else:
                return False, None
        except Exception as e:
            logger.error(f"Read error: {e}")
            return False, None
    
    def shutdown(self):
        """Cierra todo."""
        if self._lib and self._connected:
            try:
                self._running = False
                self._lib.freenect_stop_video(self._dev)
                self._lib.freenect_close_device(self._dev)
                self._lib.freenect_shutdown(self._ctx)
            except:
                pass
            self._connected = False
            logger.info("Kinect cerrado")


# TEST
if __name__ == "__main__":
    print("=== TEST KINECT VIDEO COMPLETO ===\n")
    
    driver = KinectVideoDriver()
    
    if driver.initialize():
        print("\n✅ Video inicializado!")
        print("Mostrando video (presiona 'q' para salir)...\n")
        
        import time
        time.sleep(1)  # Dar tiempo para que lleguen frames
        
        frame_count = 0
        while True:
            ret, frame = driver.read()
            
            if ret and frame is not None:
                frame_count += 1
                cv2.putText(frame, f"Kinect Frame #{frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("KINECT VIDEO - libfreenect", frame)
                
                if frame_count % 30 == 0:
                    print(f"✅ {frame_count} frames capturados...")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        driver.shutdown()
        print(f"\n🎉 ¡ÉXITO! Capturados {frame_count} frames del Kinect")
    else:
        print("\n❌ Falló inicialización")
