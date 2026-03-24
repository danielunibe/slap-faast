"""
Scan exhaustivo de TODAS las cámaras disponibles
"""
import cv2

print("=== ESCANEANDO TODAS LAS CÁMARAS ===\n")

for i in range(15):
    print(f"Probando índice {i}...", end=" ")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    
    if cap.isOpened():
        # Intentar leer
        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            
            # Obtener info del backend
            backend = cap.getBackendName()
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ FUNCIONA - {w}x{h} @ {fps} FPS - Backend: {backend}")
            
            # Identificar tipo
            if w == 640 and h == 480:
                print(f"   ⚠️  POSIBLE KINECT (resolución típica 640x480)")
            elif w >= 1280:
                print(f"   💻 Probablemente WEBCAM laptop (alta resolución)")
                
        else:
            print(f"⚠️  Se abrió pero no dio frame")
        
        cap.release()
    else:
        print("❌ No disponible")

print("\n=== FIN DEL ESCANEO ===")
print("\nSi ves MÚLTIPLES cámaras 640x480, una es el Kinect.")
print("Vamos a probar cada una manualmente.")
