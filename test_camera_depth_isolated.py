"""
PRUEBA AISLADA DE KINECT - VIDEO + PROFUNDIDAD
Ambos sensores simultáneos, sin tracking, sin UI.
"""
import cv2
import time
import ctypes
from ctypes import c_int, c_void_p, c_double, POINTER, byref, create_string_buffer
import numpy as np
from pathlib import Path

DLL_PATH = Path(__file__).parent / "freenect.dll"

print("=" * 60)
print("   PRUEBA AISLADA - KINECT VIDEO + DEPTH")
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
lib.freenect_select_subdevices(ctx, 0x02)  # CAMERA = 0x02 (incluye video y depth)

num = lib.freenect_num_devices(ctx)
print(f"Dispositivos encontrados: {num}")

if num <= 0:
    print("ERROR: No hay Kinect conectado")
    lib.freenect_shutdown(ctx)
    input("Enter para salir...")
    exit(1)

ret = lib.freenect_open_device(ctx, byref(dev), 0)
if ret < 0:
    print("ERROR: No se pudo abrir el dispositivo")
    lib.freenect_shutdown(ctx)
    input("Enter para salir...")
    exit(1)

# Buffers
video_buffer = create_string_buffer(640 * 480 * 3)
depth_buffer = create_string_buffer(640 * 480 * 2)

lib.freenect_set_video_buffer(dev, ctypes.cast(video_buffer, c_void_p))
lib.freenect_set_depth_buffer(dev, ctypes.cast(depth_buffer, c_void_p))

lib.freenect_start_video(dev)
lib.freenect_start_depth(dev)

print("\n✓ Kinect iniciado (VIDEO + DEPTH)")
print("Presiona 'Q' para salir\n")

# Estadísticas
frame_count = 0
start_time = time.time()
fps = 0

cv2.namedWindow("KINECT VIDEO", cv2.WINDOW_NORMAL)
cv2.namedWindow("KINECT DEPTH", cv2.WINDOW_NORMAL)

try:
    while True:
        # Procesar eventos USB
        lib.freenect_process_events(ctx)
        
        # === VIDEO ===
        video_data = np.frombuffer(video_buffer.raw, dtype=np.uint8)
        frame_video = None
        
        if video_data.sum() > 0:
            frame = video_data.reshape((480, 640, 3))
            frame_video = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
            
            cv2.putText(frame_video, f"FPS: {fps:.1f}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            cv2.imshow("KINECT VIDEO", frame_video)
        
        # === DEPTH ===
        depth_data = np.frombuffer(depth_buffer.raw, dtype=np.uint16)
        
        if depth_data.sum() > 0:
            depth = depth_data.reshape((480, 640))
            # Normalizar a 8-bit para visualización
            depth_norm = (depth.astype(np.float32) / 2048.0 * 255).astype(np.uint8)
            depth_norm = 255 - depth_norm  # Invertir (cerca = brillante)
            depth_color = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
            
            cv2.putText(depth_color, f"FPS: {fps:.1f}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            cv2.imshow("KINECT DEPTH", depth_color)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break

except KeyboardInterrupt:
    pass

# Limpiar
print(f"\n--- RESULTADO ---")
print(f"Frames totales: {frame_count}")
print(f"FPS promedio: {fps:.1f}")

cv2.destroyAllWindows()
lib.freenect_stop_video(dev)
lib.freenect_stop_depth(dev)
lib.freenect_close_device(dev)
lib.freenect_shutdown(ctx)

print("\nTest finalizado.")
input("Enter para cerrar...")
