"""
Test Kinect: Video RGB + Depth (activa el láser IR)
"""
import ctypes
from ctypes import c_int, c_void_p, POINTER, byref, create_string_buffer
from pathlib import Path
import numpy as np
import cv2

DLL_PATH = Path(__file__).parent / "freenect.dll"

print("=== TEST KINECT COMPLETO: RGB + DEPTH ===\n")

try:
    lib = ctypes.CDLL(str(DLL_PATH))
    print("DLL cargada\n")
    
    # Configurar funciones
    lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
    lib.freenect_init.restype = c_int
    lib.freenect_shutdown.argtypes = [c_void_p]
    lib.freenect_shutdown.restype = c_int
    lib.freenect_num_devices.argtypes = [c_void_p]
    lib.freenect_num_devices.restype = c_int
    lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
    lib.freenect_open_device.restype = c_int
    lib.freenect_close_device.argtypes = [c_void_p]
    lib.freenect_close_device.restype = c_int
    lib.freenect_select_subdevices.argtypes = [c_void_p, c_int]
    lib.freenect_select_subdevices.restype = None
    lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
    lib.freenect_set_video_buffer.restype = c_int
    lib.freenect_set_depth_buffer.argtypes = [c_void_p, c_void_p]
    lib.freenect_set_depth_buffer.restype = c_int
    lib.freenect_start_video.argtypes = [c_void_p]
    lib.freenect_start_video.restype = c_int
    lib.freenect_start_depth.argtypes = [c_void_p]
    lib.freenect_start_depth.restype = c_int
    lib.freenect_stop_video.argtypes = [c_void_p]
    lib.freenect_stop_video.restype = c_int
    lib.freenect_stop_depth.argtypes = [c_void_p]
    lib.freenect_stop_depth.restype = c_int
    lib.freenect_process_events.argtypes = [c_void_p]
    lib.freenect_process_events.restype = c_int
    
    ctx = c_void_p()
    dev = c_void_p()
    
    # Inicializar
    lib.freenect_init(byref(ctx), None)
    num = lib.freenect_num_devices(ctx)
    print(f"Dispositivos: {num}")
    
    if num > 0:
        # Seleccionar solo cámara (incluye RGB y depth)
        FREENECT_DEVICE_CAMERA = 0x02
        lib.freenect_select_subdevices(ctx, FREENECT_DEVICE_CAMERA)
        
        # Abrir dispositivo
        lib.freenect_open_device(ctx, byref(dev), 0)
        print("Dispositivo abierto")
        
        # Buffer para video RGB: 640x480x3
        VIDEO_SIZE = 640 * 480 * 3
        video_buffer = create_string_buffer(VIDEO_SIZE)
        video_ptr = ctypes.cast(video_buffer, c_void_p)
        lib.freenect_set_video_buffer(dev, video_ptr)
        
        # Buffer para depth: 640x480 x 2 bytes (uint16)
        DEPTH_SIZE = 640 * 480 * 2
        depth_buffer = create_string_buffer(DEPTH_SIZE)
        depth_ptr = ctypes.cast(depth_buffer, c_void_p)
        lib.freenect_set_depth_buffer(dev, depth_ptr)
        
        # Iniciar streams
        ret_video = lib.freenect_start_video(dev)
        print(f"Video iniciado: {ret_video}")
        
        ret_depth = lib.freenect_start_depth(dev)
        print(f"Depth iniciado: {ret_depth} (esto enciende el láser IR!)")
        
        print("\n¡Mira el Kinect - el punto 1 (láser IR) debería estar encendido ahora!")
        print("Presiona Q para salir\n")
        
        frame_count = 0
        
        while True:
            lib.freenect_process_events(ctx)
            
            # Procesar video RGB
            video_data = np.frombuffer(video_buffer.raw, dtype=np.uint8)
            if video_data.sum() > 0:
                frame_rgb = video_data.reshape((480, 640, 3))
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            else:
                frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Procesar depth
            depth_data = np.frombuffer(depth_buffer.raw, dtype=np.uint16)
            if depth_data.sum() > 0:
                depth_frame = depth_data.reshape((480, 640))
                # Normalizar para visualización (0-255)
                depth_display = (depth_frame / depth_frame.max() * 255).astype(np.uint8)
                depth_color = cv2.applyColorMap(depth_display, cv2.COLORMAP_JET)
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Frames depth: {frame_count}")
            else:
                depth_color = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Combinar vistas
            combined = np.hstack([frame_bgr, depth_color])
            cv2.putText(combined, "RGB", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(combined, "DEPTH (IR Laser)", (650, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            cv2.imshow("KINECT - RGB + DEPTH", combined)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        lib.freenect_stop_depth(dev)
        lib.freenect_stop_video(dev)
        lib.freenect_close_device(dev)
    
    lib.freenect_shutdown(ctx)
    print("\n¡Test completado!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
