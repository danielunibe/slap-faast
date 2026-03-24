"""
Test de Video Kinect - Detectar índice de cámara
"""
import cv2
import numpy as np

print("=== Buscando cámaras disponibles ===")
print()

working_cameras = []

for i in range(10):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            working_cameras.append({
                'index': i,
                'width': w,
                'height': h,
                'frame': frame
            })
            print(f"✅ Cámara {i}: {w}x{h} - FUNCIONA")
        else:
            print(f"⚠️  Cámara {i}: Se abrió pero no dio frame")
        cap.release()
    else:
        print(f"❌ Cámara {i}: No disponible")

print()
print(f"Total cámaras funcionando: {len(working_cameras)}")
print()

if working_cameras:
    print("Mostrando preview de cada cámara (presiona cualquier tecla para siguiente)...")
    for cam in working_cameras:
        cv2.imshow(f"Camera {cam['index']} - {cam['width']}x{cam['height']}", cam['frame'])
        cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Identificar posible Kinect
    print()
    print("=== Análisis ===")
    for cam in working_cameras:
        if cam['width'] == 640 and cam['height'] == 480:
            print(f"Cámara {cam['index']}: Posiblemente es el KINECT (640x480 es resolución típica)")
        else:
            print(f"Cámara {cam['index']}: Probablemente webcam ({cam['width']}x{cam['height']})")
else:
    print("❌ No se detectaron cámaras")
    print("Verifica que el driver WinUSB esté instalado correctamente")
