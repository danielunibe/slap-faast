"""
PRUEBA AISLADA DE KINECT - VIDEO + PROFUNDIDAD EN UNA SOLA VENTANA
Vista lado a lado.
"""
import cv2
import time
import ctypes
from ctypes import c_int, c_void_p, c_double, POINTER, byref, create_string_buffer
import numpy as np
from pathlib import Path

DLL_PATH = Path(__file__).parent / "freenect.dll"

print("=" * 60)
print("   KINECT DUAL VIEW (VIDEO + DEPTH) - VENTANA ÚNICA")
print("=" * 60)

if not DLL_PATH.exists():
    print(f"ERROR: No se encuentra {DLL_PATH}")
    input("Enter para salir...")
    exit(1)

# Cargar DLL
lib = ctypes.CDLL(str(DLL_PATH))

# Configurar firmas
lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
lib.freenect_init.restype = c_int
lib.freenect_num_devices.argtypes = [c_void_p]
lib.freenect_num_devices.restype = c_int
lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
lib.freenect_open_device.restype = c_int
lib.freenect_close_device.argtypes = [c_void_p]
lib.freenect_close_device.restype = c_int
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
lib.freenect_select_subdevices.argtypes = [c_void_p, c_int]
lib.freenect_select_subdevices.restype = None
lib.freenect_shutdown.argtypes = [c_void_p]
lib.freenect_shutdown.restype = c_int

# Inicializar
ctx = c_void_p()
dev = c_void_p()

lib.freenect_init(byref(ctx), None)
lib.freenect_select_subdevices(ctx, 0x02)  # CAMERA

num = lib.freenect_num_devices(ctx)
print(f"Dispositivos: {num}")

if num <= 0:
    print("ERROR: No hay Kinect")
    lib.freenect_shutdown(ctx)
    input("Enter...")
    exit(1)

ret = lib.freenect_open_device(ctx, byref(dev), 0)
if ret < 0:
    print("ERROR: No se pudo abrir dispositivo")
    lib.freenect_shutdown(ctx)
    input("Enter...")
    exit(1)

# Buffers
video_buffer = create_string_buffer(640 * 480 * 3)
depth_buffer = create_string_buffer(640 * 480 * 2)

lib.freenect_set_video_buffer(dev, ctypes.cast(video_buffer, c_void_p))
lib.freenect_set_depth_buffer(dev, ctypes.cast(depth_buffer, c_void_p))

lib.freenect_start_video(dev)
lib.freenect_start_depth(dev)

print("\n✓ Kinect listo. Presiona 'Q' para salir\n")

# Stats
frame_count = 0
start_time = time.time()
fps = 0

# Crear canvas combinado (lado a lado: 1280 x 480)
combined = np.zeros((480, 1280, 3), dtype=np.uint8)

cv2.namedWindow("KINECT DUAL VIEW", cv2.WINDOW_NORMAL)
cv2.resizeWindow("KINECT DUAL VIEW", 1280, 480)

try:
    while True:
        lib.freenect_process_events(ctx)
        
        # === VIDEO (izquierda) ===
        video_data = np.frombuffer(video_buffer.raw, dtype=np.uint8)
        if video_data.sum() > 0:
            frame = video_data.reshape((480, 640, 3))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            combined[:, 0:640, :] = frame_bgr
            
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
        
        # === DEPTH (derecha) ===
        depth_data = np.frombuffer(depth_buffer.raw, dtype=np.uint16)
        if depth_data.sum() > 0:
            depth = depth_data.reshape((480, 640))
            depth_norm = (depth.astype(np.float32) / 2048.0 * 255).astype(np.uint8)
            depth_norm = 255 - depth_norm
            depth_color = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
            combined[:, 640:1280, :] = depth_color
        
        # === OVERLAYS ===
        # Etiquetas
        cv2.putText(combined, "VIDEO RGB", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(combined, "DEPTH SENSOR", (660, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # FPS central
        cv2.putText(combined, f"FPS: {fps:.1f}", (580, 460), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Línea divisoria
        cv2.line(combined, (640, 0), (640, 480), (100, 100, 100), 2)
        
        cv2.imshow("KINECT DUAL VIEW", combined)
        
        if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
            break

except KeyboardInterrupt:
    pass

print(f"\n--- RESULTADO ---")
print(f"FPS promedio: {fps:.1f}")

cv2.destroyAllWindows()
lib.freenect_stop_video(dev)
lib.freenect_stop_depth(dev)
lib.freenect_close_device(dev)
lib.freenect_shutdown(ctx)

print("Finalizado.")
input("Enter...")
