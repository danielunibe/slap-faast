"""
Script para ejecutar el "Detector de Huesos" (Skeletal Tracking)
Usando Kinect v1 y MediaPipe (via HybridTracker)
"""
import cv2
import sys
from loguru import logger
import numpy as np

# Asegurar que podemos importar modulos de src
from src.sensors.kinect_video_final import KinectVideoDriver
from src.tracking.hybrid_tracker import HybridTracker

def main():
    logger.info("💀 Iniciando Detector de Huesos...")
    
    # 1. Inicializar Driver Kinect (Video)
    driver = KinectVideoDriver()
    if not driver.initialize():
        logger.error("No se pudo iniciar el Kinect. Verifica conexión USB y drivers.")
        print("ERROR: Kinect initialization failed.")
        input("Press Enter to exit...")
        return

    # 2. Inicializar Tracker (Huesos/Manos/Cara)
    tracker = HybridTracker()
    
    logger.success("Sistema listo. Presiona 'q' para salir.")
    
    while True:
        # 3. Leer frame del Kinect
        ret, frame_bgr = driver.read()
        
        if ret and frame_bgr is not None:
            # 4. Procesar Tracking
            # HybridTracker espera RGB
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            
            # Obtener resultados
            results = tracker.process_frame(frame_rgb)
            
            # 5. Dibujar resultados sobre el frame original
            # (Usamos el BGR para mostrar en OpenCV correctamente)
            output_frame = tracker.draw_results(frame_bgr, results)
            
            # Añadir info
            cv2.putText(output_frame, "KINECT BONE DETECTOR", (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(output_frame, "Presiona 'q' para salir", (20, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # 6. Mostrar ventana
            cv2.imshow("Kinect Bone Detector", output_frame)
            
        else:
            # Si no hay frame, esperamos un poco
            cv2.waitKey(10)
            
        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Limpieza
    driver.shutdown()
    tracker.release()
    cv2.destroyAllWindows()
    logger.info("Detector finalizado.")
    print("Press Enter to close...")
    input() # Keep window open to see errors

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit error...")
