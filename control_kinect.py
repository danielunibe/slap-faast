"""
Control Interactivo del Kinect v1
Usa este script para verificar que tienes control total del Kinect.
"""
from src.sensors.kinect_usb_driver import KinectUSBDriver
import time
import sys

def print_menu():
    print("\n" + "="*50)
    print("🎮 CONTROL KINECT v1 - GOD MODE")
    print("="*50)
    print("\n📍 Control de LED:")
    print("  0 - LED Apagado")
    print("  1 - LED Verde")
    print("  2 - LED Rojo")
    print("  3 - LED Amarillo")
    print("  4 - LED Parpadeando Amarillo")
    print("  5 - LED Parpadeando Verde")
    print("  6 - LED Parpadeando Rojo/Amarillo")
    print("\n🔄 Control de Motor:")
    print("  w - Inclinar ARRIBA (+15°)")
    print("  s - Inclinar ABAJO (-15°)")
    print("  a - Inclinar MÁS arriba (+5°)")
    print("  d - Inclinar MÁS abajo (-5°)")
    print("  c - Centrar motor (0°)")
    print("\n❌ Salir:")
    print("  q - Cerrar")
    print("="*50)

def main():
    print("\n🔌 Conectando al Kinect...")
    kinect = KinectUSBDriver()
    
    if not kinect.isOpened():
        print("❌ No se pudo conectar al Kinect")
        print("   Verifica:")
        print("   1. Kinect conectado y con luz")
        print("   2. Driver libusb-win32 instalado (Zadig)")
        return
    
    print("✅ Kinect conectado exitosamente!")
    print("\n💡 Prueba inicial - LED Verde...")
    kinect.set_led(1)
    time.sleep(0.5)
    
    current_angle = 0
    current_led = 1
    
    print_menu()
    
    try:
        while True:
            print(f"\n📊 Estado actual: LED={current_led}, Motor={current_angle}°")
            cmd = input("Comando > ").strip().lower()
            
            if cmd == 'q':
                print("\n👋 Cerrando...")
                break
            
            # LEDs
            elif cmd in ['0', '1', '2', '3', '4', '5', '6']:
                led = int(cmd)
                if kinect.set_led(led):
                    current_led = led
                    led_names = ["Apagado", "Verde", "Rojo", "Amarillo", 
                                "Parpadeo Amarillo", "Parpadeo Verde", "Parpadeo Rojo/Amarillo"]
                    print(f"✅ LED configurado: {led_names[led]}")
                else:
                    print("❌ Error cambiando LED")
            
            # Motor
            elif cmd == 'w':
                new_angle = min(31, current_angle + 15)
                if kinect.set_tilt(new_angle):
                    current_angle = new_angle
                    print(f"⬆️  Motor inclinado a {current_angle}°")
                else:
                    print("❌ Error moviendo motor")
            
            elif cmd == 's':
                new_angle = max(-31, current_angle - 15)
                if kinect.set_tilt(new_angle):
                    current_angle = new_angle
                    print(f"⬇️  Motor inclinado a {current_angle}°")
                else:
                    print("❌ Error moviendo motor")
            
            elif cmd == 'a':
                new_angle = min(31, current_angle + 5)
                if kinect.set_tilt(new_angle):
                    current_angle = new_angle
                    print(f"⬆️  Motor ajustado a {current_angle}°")
                else:
                    print("❌ Error moviendo motor")
            
            elif cmd == 'd':
                new_angle = max(-31, current_angle - 5)
                if kinect.set_tilt(new_angle):
                    current_angle = new_angle
                    print(f"⬇️  Motor ajustado a {current_angle}°")
                else:
                    print("❌ Error moviendo motor")
            
            elif cmd == 'c':
                if kinect.set_tilt(0):
                    current_angle = 0
                    print("↔️  Motor centrado (0°)")
                else:
                    print("❌ Error moviendo motor")
            
            elif cmd == 'help' or cmd == 'h':
                print_menu()
            
            else:
                print("❓ Comando no reconocido. Escribe 'h' para ver el menú.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
    
    finally:
        print("\n🔧 Apagando LED...")
        kinect.set_led(0)
        print("🔧 Centrando motor...")
        kinect.set_tilt(0)
        time.sleep(0.5)
        kinect.release()
        print("✅ Kinect liberado correctamente\n")

if __name__ == "__main__":
    main()
