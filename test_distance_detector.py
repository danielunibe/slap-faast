"""
KINECT - DETECTOR DE DISTANCIAS
Muestra video + mapa de profundidad con mediciones en tiempo real.
Click en cualquier punto para ver la distancia en cm/metros.
"""
import cv2
import time
import ctypes
from ctypes import c_int, c_void_p, POINTER, byref, create_string_buffer
import numpy as np
from pathlib import Path

DLL_PATH = Path(__file__).parent / "freenect.dll"

# Variables globales para mouse callback
mouse_x, mouse_y = 320, 240
clicked_x, clicked_y = -1, -1
depth_at_click = 0

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y, clicked_x, clicked_y
    mouse_x, mouse_y = x, y
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_x, clicked_y = x, y

print("=" * 60)
print("   KINECT DISTANCE DETECTOR")
print("   Click para medir distancia | Q para salir")
print("=" * 60)

if not DLL_PATH.exists():
    print(f"ERROR: No se encuentra {DLL_PATH}")
    input("Enter...")
    exit(1)

lib = ctypes.CDLL(str(DLL_PATH))

# Firmas
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

ctx = c_void_p()
dev = c_void_p()

lib.freenect_init(byref(ctx), None)
lib.freenect_select_subdevices(ctx, 0x02)

num = lib.freenect_num_devices(ctx)
if num <= 0:
    print("ERROR: No hay Kinect")
    lib.freenect_shutdown(ctx)
    input("Enter...")
    exit(1)

lib.freenect_open_device(ctx, byref(dev), 0)

video_buffer = create_string_buffer(640 * 480 * 3)
depth_buffer = create_string_buffer(640 * 480 * 2)

lib.freenect_set_video_buffer(dev, ctypes.cast(video_buffer, c_void_p))
lib.freenect_set_depth_buffer(dev, ctypes.cast(depth_buffer, c_void_p))

lib.freenect_start_video(dev)
lib.freenect_start_depth(dev)

print("\n✓ Kinect listo")

# Canvas
combined = np.zeros((480, 1280, 3), dtype=np.uint8)
depth_raw = np.zeros((480, 640), dtype=np.uint16)

cv2.namedWindow("KINECT DISTANCE DETECTOR", cv2.WINDOW_NORMAL)
cv2.resizeWindow("KINECT DISTANCE DETECTOR", 1280, 480)
cv2.setMouseCallback("KINECT DISTANCE DETECTOR", mouse_callback)

frame_count = 0
start_time = time.time()

try:
    while True:
        lib.freenect_process_events(ctx)
        
        # VIDEO
        video_data = np.frombuffer(video_buffer.raw, dtype=np.uint8)
        if video_data.sum() > 0:
            frame = video_data.reshape((480, 640, 3))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            combined[:, 0:640, :] = frame_bgr
            frame_count += 1
        
        # DEPTH
        depth_data = np.frombuffer(depth_buffer.raw, dtype=np.uint16)
        if depth_data.sum() > 0:
            depth_raw = depth_data.reshape((480, 640))
            depth_norm = (depth_raw.astype(np.float32) / 2048.0 * 255).astype(np.uint8)
            depth_norm = 255 - depth_norm
            depth_color = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
            combined[:, 640:1280, :] = depth_color
        
        # === MEDICIÓN DE DISTANCIA ===
        # Obtener distancia en el punto del mouse (lado derecho = depth)
        if mouse_x >= 640:
            depth_x = mouse_x - 640
            depth_y = mouse_y
            if 0 <= depth_x < 640 and 0 <= depth_y < 480:
                raw_depth = depth_raw[depth_y, depth_x]
                # Conversión CORREGIDA para Kinect v1 (11-bit depth)
                # Fórmula: distancia_cm = 100 / (-0.00307 * raw + 3.33)
                # Rango válido: ~50cm a ~400cm
                if raw_depth > 0 and raw_depth < 2047:
                    distance_cm = 100.0 / (-0.00307 * raw_depth + 3.33)
                    if distance_cm < 0 or distance_cm > 1000:
                        distance_cm = 0  # Fuera de rango
                else:
                    distance_cm = 0
                distance_m = distance_cm / 100.0
                
                # Crosshair en depth
                cv2.drawMarker(combined, (mouse_x, mouse_y), (0, 255, 255), 
                              cv2.MARKER_CROSS, 20, 2)
                
                # Mostrar distancia en hover
                text = f"{distance_cm:.0f} cm ({distance_m:.2f} m)"
                cv2.putText(combined, text, (mouse_x + 10, mouse_y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # === PUNTO FIJO CENTRAL ===
        center_raw = depth_raw[240, 320]
        if center_raw > 0 and center_raw < 2047:
            center_depth = 100.0 / (-0.00307 * center_raw + 3.33)
            if center_depth < 0 or center_depth > 1000:
                center_depth = 0
        else:
            center_depth = 0
        cv2.circle(combined, (640 + 320, 240), 8, (0, 0, 255), 2)
        cv2.putText(combined, f"CENTRO: {center_depth:.0f} cm", (640 + 250, 280),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # === UI ===
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        cv2.putText(combined, "VIDEO RGB", (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(combined, "DEPTH (click para medir)", (660, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(combined, f"FPS: {fps:.1f}", (580, 460), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        cv2.line(combined, (640, 0), (640, 480), (100, 100, 100), 2)
        
        cv2.imshow("KINECT DISTANCE DETECTOR", combined)
        
        if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
            break

except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
lib.freenect_stop_video(dev)
lib.freenect_stop_depth(dev)
lib.freenect_close_device(dev)
lib.freenect_shutdown(ctx)

print("Finalizado.")
input("Enter...")
