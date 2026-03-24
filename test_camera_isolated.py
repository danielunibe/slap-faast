"""
PRUEBA AISLADA DE CÁMARA KINECT
Solo video, sin tracking, sin UI, sin efectos.
Objetivo: Verificar FPS real del driver.
"""
import cv2
import time
import ctypes
from ctypes import c_int, c_void_p, c_double, POINTER, byref, create_string_buffer
import numpy as np
from pathlib import Path

DLL_PATH = Path(__file__).parent / "freenect.dll"

print("=" * 60)
print("   PRUEBA AISLADA - KINECT CAMERA (SOLO VIDEO)")
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
lib.freenect_start_video.argtypes = [c_void_p]
lib.freenect_start_video.restype = c_int
lib.freenect_stop_video.argtypes = [c_void_p]
lib.freenect_stop_video.restype = c_int
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
lib.freenect_select_subdevices(ctx, 0x02)  # Solo CAMERA (sin motor)

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

# Buffer de video
video_buffer = create_string_buffer(640 * 480 * 3)
lib.freenect_set_video_buffer(dev, ctypes.cast(video_buffer, c_void_p))
lib.freenect_start_video(dev)

print("\n✓ Kinect iniciado. Mostrando video...")
print("Presiona 'Q' para salir\n")

# Estadísticas
frame_count = 0
start_time = time.time()
fps = 0

cv2.namedWindow("KINECT ISOLATED TEST", cv2.WINDOW_NORMAL)

try:
    while True:
        # Procesar eventos USB
        lib.freenect_process_events(ctx)
        
        # Leer buffer
        video_data = np.frombuffer(video_buffer.raw, dtype=np.uint8)
        
        if video_data.sum() > 0:
            frame = video_data.reshape((480, 640, 3))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
            
            # Mostrar FPS en pantalla
            cv2.putText(frame_bgr, f"FPS: {fps:.1f}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            cv2.putText(frame_bgr, f"Frames: {frame_count}", (20, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
            cv2.putText(frame_bgr, "Presiona Q para salir", (20, 460), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            cv2.imshow("KINECT ISOLATED TEST", frame_bgr)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break

except KeyboardInterrupt:
    pass

# Limpiar
print(f"\n--- RESULTADO ---")
print(f"Frames totales: {frame_count}")
print(f"Tiempo: {time.time() - start_time:.1f}s")
print(f"FPS promedio: {fps:.1f}")

cv2.destroyAllWindows()
lib.freenect_stop_video(dev)
lib.freenect_close_device(dev)
lib.freenect_shutdown(ctx)

print("\nTest finalizado.")
input("Enter para cerrar...")
