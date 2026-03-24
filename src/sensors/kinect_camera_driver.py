"""
Kinect v1 Camera Driver - Driver propio sin SDK de Microsoft
Basado en el protocolo documentado por libfreenect.

La cámara Kinect usa transferencias USB isochronous que son complicadas en Windows.
Este driver intenta usar pyusb con libusb-win32/WinUSB.

Requiere: Zadig para instalar WinUSB en el dispositivo de cámara (02ae)
"""
import usb.core
import usb.util
import usb.backend.libusb1 as lb
import libusb_package

import numpy as np
import cv2
from typing import Optional, Tuple
from loguru import logger
import struct
import time
import threading
from queue import Queue


class KinectCameraDriver:
    """
    Driver de cámara Kinect v1 usando USB directo.
    
    NOTA: Las transferencias isochronous en Windows son problemáticas.
    Este driver intenta múltiples métodos.
    """
    
    # Kinect Camera Device
    VID = 0x045e  # Microsoft
    PID_CAMERA = 0x02ae  # Xbox NUI Camera
    
    # Endpoints
    EP_RGB = 0x81    # RGB stream
    EP_DEPTH = 0x82  # Depth stream
    
    # Resoluciones
    RGB_WIDTH = 640
    RGB_HEIGHT = 480
    DEPTH_WIDTH = 640
    DEPTH_HEIGHT = 480
    
    # Comandos de control (basados en libfreenect)
    KINECT_CONTROL_EP = 0x00
    
    def __init__(self):
        self._dev: Optional[usb.core.Device] = None
        self._connected = False
        self._rgb_frame: Optional[np.ndarray] = None
        self._depth_frame: Optional[np.ndarray] = None
        self._streaming = False
        self._stream_thread: Optional[threading.Thread] = None
        self._frame_queue = Queue(maxsize=5)
        
        self._initialize()
    
    def _initialize(self):
        """Busca y conecta al dispositivo de cámara."""
        logger.info("Buscando Kinect Camera via USB...")
        
        try:
            # Force libusb-1.0 backend
            lib_path = libusb_package.get_library_path()
            backend = lb.get_backend(find_library=lambda x: lib_path)
            if backend:
                logger.info("Using forced libusb-1.0 backend")
            else:
                logger.warning("Could not force libusb-1.0 backend, using default")

            self._dev = usb.core.find(idVendor=self.VID, idProduct=self.PID_CAMERA, backend=backend)
            
            if self._dev is None:
                logger.warning("Kinect Camera no encontrada (VID:045e PID:02ae)")
                logger.info("Asegurate de usar Zadig para instalar WinUSB en 'Xbox NUI Camera'")
                return
            
            # Intentar configurar
            try:
                self._dev.set_configuration()
            except usb.core.USBError as e:
                logger.debug(f"set_configuration: {e}")
            
            # Claim interface
            try:
                if self._dev.is_kernel_driver_active(0):
                    self._dev.detach_kernel_driver(0)
            except (usb.core.USBError, NotImplementedError):
                pass
            
            try:
                usb.util.claim_interface(self._dev, 0)
            except usb.core.USBError as e:
                logger.debug(f"claim_interface: {e}")
            
            self._connected = True
            logger.success("Kinect Camera conectada via USB")
            
            # Intentar inicializar la cámara
            self._init_camera()
            
        except Exception as e:
            logger.error(f"Error inicializando camera USB: {e}")
            self._connected = False
    
    def _init_camera(self):
        """
        Envía comandos de inicialización a la cámara.
        Basado en el protocolo de libfreenect.
        """
        if self._dev:
            return
        
        logger.info("Initializing Kinect Camera...")
        
        try:
            # 1. Set Configuration
            try:
                self._dev.set_configuration()
                logger.info("Configuration set")
            except usb.core.USBError as e:
                logger.debug(f"Set Config warning: {e}")

            # 2. Claim Interface
            usb.util.claim_interface(self._dev, 0)
            
            # 3. Set Alternate Setting (Critical for ISO)
            try:
                # Try standard pyusb method
                self._dev.set_interface_alt_setting(0, 1)
                logger.info("Alt setting 1 selected (Method A)")
            except Exception as e:
                logger.debug(f"Method A failed: {e}")
                # Fallback: Manual Control Transfer
                # Set Interface (0x0B), wValue=Alt(1), wIndex=Intf(0)
                try:
                    self._dev.ctrl_transfer(0x00, 0x0B, 0x01, 0x00, [])
                    logger.info("Alt setting 1 selected (Method B - Manual)")
                except Exception as e2:
                    logger.error(f"Could not set Alt Setting 1: {e2}")

            # Command to active RGB stream

            # Command to active RGB stream
            # Trying wValue=1 for 0x05 (Mode?) which might mean "On"
            # And specific initialization sequence for NUI Camera
            
            commands = [
                # (bRequest, wValue)
                (0x06, 0x00), # LED Mode 0
                (0x05, 0x01), # Mode 1 (Start?)
            ]
            
            logger.info("Sending magic init packets (Mode=1)...")
            # Using known sequence for Xbox NUI Camera
            for bReq, wVal in commands:
                self._dev.ctrl_transfer(0x40, bReq, wVal, 0x00, [])
            
            logger.info("Initialization sequence finished")
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")

    
    def is_connected(self) -> bool:
        """Verifica si la cámara está conectada."""
        return self._connected and self._dev is not None
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee un frame de la cámara.
        """
        if not self.is_connected():
            return False, None
        
        try:
            # Strategies for ISO Read on Windows/libusb-1.0
            
            # Strategy: Read small packets continuously
            # Endpoint 0x81 MaxPacketSize is 3008
            
            PACKET_SIZE = 3008
            packets = []
            total_bytes = 0
            TARGET_BYTES = 640 * 480 # ~300KB (Bayer is 1 byte per pixel)
            
            # Try to read bursts
            start_time = time.time()
            max_loops = 200 # Avoid infinite loop
            
            loops = 0
            while total_bytes < TARGET_BYTES and loops < max_loops:
                loops += 1
                try:
                    # Timeout very short to poll fast
                    data = self._dev.read(self.EP_RGB, PACKET_SIZE, timeout=10)
                    if len(data) > 0:
                        packets.append(data)
                        total_bytes += len(data)
                except usb.core.USBError as e:
                    if e.errno == 10060: # Timeout
                        continue
                    # Ignore other errors and keep trying potentially
                    pass
            
            if total_bytes > 0:
                logger.debug(f"Captured {total_bytes} bytes in {loops} loops")
                
                # Assemble frame
                raw_data = b''.join(packets)
                if len(raw_data) >= 640*480:
                     return True, self._process_raw_data(raw_data)
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            return False, None
    
    def _process_raw_data(self, data: bytes) -> Optional[np.ndarray]:
        """
        Procesa datos raw de la cámara.
        El Kinect envía datos en formato Bayer que necesitan conversión.
        """
        # Placeholder - los datos raw necesitan decodificación especial
        # El formato exacto depende de la configuración de la cámara
        
        if len(data) >= self.RGB_WIDTH * self.RGB_HEIGHT:
            # Intentar interpretar como imagen grayscale
            try:
                img = np.frombuffer(data[:self.RGB_WIDTH * self.RGB_HEIGHT], 
                                   dtype=np.uint8).reshape((self.RGB_HEIGHT, self.RGB_WIDTH))
                return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            except:
                pass
        
        return None
    
    def get_depth_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee un frame de profundidad.
        
        Returns:
            Tuple (success, depth_array) donde depth_array tiene valores en mm
        """
        if not self.is_connected():
            return False, None
        
        try:
            data = self._dev.read(self.EP_DEPTH, 3008, timeout=100)
            if len(data) > 0:
                return True, self._process_depth_data(data)
        except usb.core.USBError as e:
            if e.errno != 110:
                logger.debug(f"Depth read error: {e}")
        
        return False, None
    
    def _process_depth_data(self, data: bytes) -> Optional[np.ndarray]:
        """
        Procesa datos de profundidad.
        El Kinect envía depth en 11-bit packed format.
        """
        # Placeholder - necesita decodificar formato 11-bit
        return None
    
    def release(self):
        """Libera el dispositivo."""
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=1)
        
        if self._dev:
            try:
                usb.util.release_interface(self._dev, 0)
                usb.util.dispose_resources(self._dev)
            except:
                pass
        
        self._connected = False
        logger.info("Kinect Camera Driver liberado")


class KinectCameraFallback:
    """
    Fallback que usa OpenCV para intentar capturar del Kinect.
    Funciona si Windows tiene un driver UVC instalado.
    """
    
    def __init__(self, camera_index: int = 1):
        self._cap = None
        self._initialize(camera_index)
    
    def _initialize(self, start_index: int):
        """Busca una cámara Kinect por índice."""
        logger.info(f"Buscando Kinect via OpenCV (desde índice {start_index})...")
        
        for idx in range(start_index, start_index + 5):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    h, w = frame.shape[:2]
                    logger.success(f"Cámara encontrada en índice {idx} ({w}x{h})")
                    self._cap = cap
                    return
                cap.release()
        
        logger.warning("No se encontró ninguna cámara adicional")
    
    def is_connected(self) -> bool:
        return self._cap is not None and self._cap.isOpened()
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self._cap:
            return self._cap.read()
        return False, None
    
    def release(self):
        if self._cap:
            self._cap.release()


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("KINECT CAMERA DRIVER TEST")
    print("=" * 60)
    
    # Probar driver USB directo
    print("\n[1] Probando driver USB directo...")
    driver = KinectCameraDriver()
    
    if driver.is_connected():
        print("Intentando leer frame...")
        for _ in range(10):
            ret, frame = driver.read_frame()
            if ret and frame is not None:
                print(f"Frame recibido: {frame.shape}")
                cv2.imwrite("kinect_usb_frame.jpg", frame)
                break
            time.sleep(0.1)
    
    driver.release()
    
    # Probar fallback OpenCV
    print("\n[2] Probando fallback OpenCV...")
    fallback = KinectCameraFallback(1)
    
    if fallback.is_connected():
        ret, frame = fallback.read_frame()
        if ret and frame is not None:
            print(f"Frame via OpenCV: {frame.shape}")
            cv2.imwrite("kinect_opencv_frame.jpg", frame)
    else:
        print("Fallback OpenCV no encontró cámara")
    
    fallback.release()
    
    print("\n[OK] Test completado")
