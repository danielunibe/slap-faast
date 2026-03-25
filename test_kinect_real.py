import freenect
import sys

def test_kinect():
    print("--- DIAGNÓSTICO KINECT V1 ---")
    try:
        ctx = freenect.init()
        num_devices = freenect.num_devices(ctx)
        print(f"Dispositivos detectados: {num_devices}")
        
        if num_devices == 0:
            print("❌ ERROR: No se detectaron dispositivos Kinect.")
            print("TIP: Asegúrate de que el driver 'Xbox NUI Camera' esté configurado como WinUSB mediante Zadig.")
        else:
            print("✅ ÉXITO: Kinect detectado.")
            # Intentar abrir el dispositivo 0
            dev = freenect.open_device(ctx, 0)
            print("✅ Dispositivo abierto correctamente.")
            freenect.close_device(dev)
            
        freenect.shutdown(ctx)
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    test_kinect()
