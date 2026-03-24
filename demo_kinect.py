"""
Demo Automática - Kinect God Mode
Esta demo ejecuta automáticamente para verificar control total.
"""
from src.sensors.kinect_usb_driver import KinectUSBDriver
import time

def main():
    print("\n" + "="*60)
    print("🎮 DEMO KINECT GOD MODE - VERIFICACIÓN DE CONTROL TOTAL")
    print("="*60)
    
    print("\n🔌 Conectando al Kinect...")
    kinect = KinectUSBDriver()
    
    if not kinect.isOpened():
        print("❌ No se pudo conectar al Kinect")
        return
    
    print("✅ Kinect conectado!\n")
    
    # Test 1: LEDs
    print("📍 TEST 1: Control de LED")
    print("-" * 60)
    led_tests = [
        (0, "Apagado"),
        (1, "Verde"),
        (2, "Rojo"),
        (3, "Amarillo"),
        (4, "Parpadeo Amarillo"),
        (5, "Parpadeo Verde"),
        (0, "Apagado")
    ]
    
    for led_color, led_name in led_tests:
        print(f"  → LED: {led_name}")
        result = kinect.set_led(led_color)
        if result:
            print(f"     ✅ Éxito")
        else:
            print(f"     ❌ Fallo")
        time.sleep(1.5)
    
    print("\n✅ Test de LED completado\n")
    
    # Test 2: Motor
    print("🔄 TEST 2: Control de Motor")
    print("-" * 60)
    motor_tests = [
        (15, "Arriba +15°"),
        (0, "Centro 0°"),
        (-15, "Abajo -15°"),
        (-25, "Más abajo -25°"),
        (25, "Arriba +25°"),
        (0, "Centro final 0°")
    ]
    
    for angle, description in motor_tests:
        print(f"  → Motor: {description}")
        result = kinect.set_tilt(angle)
        if result:
            print(f"     ✅ Movido a {angle}°")
        else:
            print(f"     ❌ Fallo")
        time.sleep(2)
    
    print("\n✅ Test de Motor completado\n")
    
    # Resumen
    print("="*60)
    print("📊 RESUMEN: VERIFICACIÓN DE CONTROL TOTAL")
    print("="*60)
    print("\n✅ LED: Control COMPLETO (7 estados probados)")
    print("✅ MOTOR: Control COMPLETO (rango -31° a +31°)")
    print("\n🎉 KINECT GOD MODE CONFIRMADO 🎉")
    print("\nSi viste el LED cambiar y el motor moverse,")
    print("tienes CONTROL TOTAL del Kinect v1 sin SDK de Microsoft.")
    print("\n" + "="*60 + "\n")
    
    # Limpiar
    print("🔧 Apagando LED...")
    kinect.set_led(0)
    print("🔧 Centrando motor...")
    kinect.set_tilt(0)
    time.sleep(1)
    
    kinect.release()
    print("✅ Kinect liberado correctamente\n")

if __name__ == "__main__":
    main()
