"""Test directo del motor Kinect - diagnóstico"""
import usb.core
import usb.util
import time

print("=== TEST DIRECTO MOTOR KINECT ===\n")

# Buscar motor
dev = usb.core.find(idVendor=0x045E, idProduct=0x02B0)

if dev is None:
    print("ERROR: Motor no encontrado")
    print("Posibles causas:")
    print("  1. Kinect no conectado")
    print("  2. Driver libusbK puede bloquear acceso PyUSB")
    exit(1)

print(f"Motor encontrado: VID={hex(dev.idVendor)}, PID={hex(dev.idProduct)}")
print(f"Manufacturer: {usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else 'N/A'}")

# Intentar configurar
try:
    dev.set_configuration()
    print("Configuración establecida")
except Exception as e:
    print(f"Nota: set_configuration: {e}")

# Test LED
print("\n--- Test LED ---")
for led_mode in [1, 2, 3, 0]:
    led_names = {0: "OFF", 1: "VERDE", 2: "ROJO", 3: "AMARILLO"}
    try:
        dev.ctrl_transfer(0x40, 0x06, led_mode, 0x00, [])
        print(f"  LED {led_names[led_mode]}: OK")
        time.sleep(0.5)
    except Exception as e:
        print(f"  LED {led_names[led_mode]}: ERROR - {e}")

# Test Motor
print("\n--- Test Motor ---")
for angle in [0, 15, 0, -15, 0]:
    try:
        tilt_val = angle * 2
        if tilt_val < 0:
            tilt_val = 256 + tilt_val
        dev.ctrl_transfer(0x40, 0x31, tilt_val, 0x00, [])
        print(f"  Tilt {angle:+d}°: Comando enviado")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Tilt {angle:+d}°: ERROR - {e}")

print("\n=== TEST COMPLETADO ===")
print("Revisa el Kinect:")
print("  - ¿El LED cambió de color?")
print("  - ¿El motor se movió?")
