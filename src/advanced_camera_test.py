"""
Test directo de acceso a cámara con diagnóstico detallado.
"""
import cv2
import numpy as np

print("=== TEST DE ACCESO A CÁMARA ===\n")

for idx in [0, 1]:
    print(f"Probando índice {idx}...")
    
    # Probar con diferentes backends
    for backend_name, backend in [("DSHOW", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF), ("ANY", cv2.CAP_ANY)]:
        try:
            cap = cv2.VideoCapture(idx, backend)
            
            if not cap.isOpened():
                print(f"  [{backend_name}] No pudo abrir")
                continue
                
            # Intentar leer
            ret, frame = cap.read()
            
            if not ret:
                print(f"  [{backend_name}] Abrió pero read() falló")
                cap.release()
                continue
            
            # Verificar si el frame es válido
            if frame is None:
                print(f"  [{backend_name}] Frame es None")
                cap.release()
                continue
                
            # Verificar si es ruido (desviación estándar muy alta)
            std = np.std(frame)
            mean = np.mean(frame)
            
            print(f"  [{backend_name}] ✅ Frame leído - Shape: {frame.shape}, Mean: {mean:.1f}, StdDev: {std:.1f}")
            
            # Si StdDev > 70, probablemente es ruido
            if std > 70:
                print(f"              ⚠️  ADVERTENCIA: Valores sugieren ruido/corrupción")
            else:
                # Guardar para verificar
                cv2.imwrite(f"test_backend_{backend_name}_idx{idx}.jpg", frame)
                print(f"              Guardado: test_backend_{backend_name}_idx{idx}.jpg")
                
            cap.release()
            break  # Si funcionó, no probar más backends
            
        except Exception as e:
            print(f"  [{backend_name}] Error: {e}")
    
    print()
