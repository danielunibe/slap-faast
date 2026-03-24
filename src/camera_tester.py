import cv2
import time

def test_cameras():
    print("=== DIAGNÓSTICO DE CÁMARAS (ETHYRIA CORE) ===")
    print("Buscando dispositivos de vídeo disponibles (Índices 0-4)...\n")
    
    available_cameras = []

    for index in range(5):
        print(f"[-] Probando Índice {index}...", end=" ")
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) # CAP_DSHOW es más rápido en Windows
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w, _ = frame.shape
                print(f"✅ DETECTADO - Resolución: {w}x{h}")
                available_cameras.append(index)
                
                # Guardar snapshot para verificar visualmentes
                filename = f"camera_test_index_{index}.jpg"
                cv2.imwrite(filename, frame)
                print(f"    -> Snapshot guardado: {filename}")
            else:
                print("⚠️  ABIERTO PERO SIN VIDEO (Posiblemente ocupado o IR)")
            cap.release()
        else:
            print("❌ NO DISPONIBLE")
            
    print("\n=== RESUMEN ===")
    if available_cameras:
        print(f"Cámaras funcionales encontradas en índices: {available_cameras}")
        print("Revisa los archivos .jpg generados para identificar cuál es el Kinect.")
    else:
        print("NO SE ENCONTRARON CÁMARAS. Verifica la conexión USB.")

if __name__ == "__main__":
    test_cameras()
