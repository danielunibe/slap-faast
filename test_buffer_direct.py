"""
Test simple: leer video usando buffer directo (sin callbacks)
"""
import ctypes
from ctypes import c_int, c_void_p, c_uint8, POINTER, byref, create_string_buffer
from pathlib import Path
import numpy as np
import cv2
from loguru import logger

DLL_PATH = Path(__file__).parent / "freenect.dll"

print("=== TEST BUFFER DIRECTO ===\n")

try:
    lib = ctypes.CDLL(str(DLL_PATH))
    print("✅ DLL cargada\n")
    
    # Setup
    lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
    lib.freenect_init.restype = c_int
    lib.freenect_num_devices.argtypes = [c_void_p]
    lib.freenect_num_devices.restype = c_int
    lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
    lib.freenect_open_device.restype = c_int
    lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
    lib.freenect_set_video_buffer.restype = c_int
    lib.freenect_start_video.argtypes = [c_void_p]
    lib.freenect_start_video.restype = c_int
    lib.freenect_process_events.argtypes = [c_void_p]
    lib.freenect_process_events.restype = c_int
    
    ctx = c_void_p()
    dev = c_void_p()
    
    # Init
    lib.freenect_init(byref(ctx), None)
    num = lib.freenect_num_devices(ctx)
    print(f"Kinects encontrados: {num}\n")
    
    if num > 0:
        lib.freenect_open_device(ctx, byref(dev), 0)
        print("✅ Device abierto\n")
        
        # Crear buffer para video RGB: 640x480x3
        video_buffer = create_string_buffer(640 * 480 * 3)
        buffer_ptr = ctypes.cast(video_buffer, c_void_p)
        
        # Asignar buffer
        ret = lib.freenect_set_video_buffer(dev, buffer_ptr)
        print(f"Set buffer: {ret}\n")
        
        # Iniciar video
        ret = lib.freenect_start_video(dev)
        print(f"Start video: {ret}\n")
        
        if ret >= 0:
            print("Procesando eventos y leyendo buffer...\n")
            
            for i in range(100):
                # Procesar eventos
                lib.freenect_process_events(ctx)
                
                # Leer buffer
                data = np.frombuffer(video_buffer, dtype=np.uint8)
                
                # Verificar si hay datos
                if data.sum() > 0:
                    print(f"✅ Frame {i}: {data.sum()} suma de píxeles")
                    frame = data.reshape((480, 640, 3))
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Kinect Buffer Test", frame_bgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                elif i % 20 == 0:
                    print(f"Frame {i}: buffer vacío...")
            
            cv2.destroyAllWindows()
            print("\n🎉 Test completado!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
