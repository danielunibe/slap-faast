"""
Escaneo completo de todos los dispositivos Microsoft
"""
import usb.core

print("=== ESCANEO DISPOSITIVOS MICROSOFT (VID 045E) ===\n")

devices = list(usb.core.find(find_all=True, idVendor=0x045E))

if not devices:
    print("❌ NO se encontraron dispositivos Microsoft (VID 045E)")
    print("\nPosibles causas:")
    print("1. Kinect no está conectado")
    print("2. Drivers no instalados correctamente")
    print("3. Windows no permite acceso (Zadig no aplicado)")
else:
    print(f"✅ Encontrados {len(devices)} dispositivo(s):\n")
    
    for dev in devices:
        print(f"Device:")
        print(f"  Bus: {dev.bus}")
        print(f"  Address: {dev.address}")
        print(f"  VID: 0x{dev.idVendor:04X}")
        print(f"  PID: 0x{dev.idProduct:04X}")
        
        # Identificar por PID
        if dev.idProduct == 0x02B0:
            print(f"  -> KINECT MOTOR/LED")
        elif dev.idProduct == 0x02AE:
            print(f"  -> KINECT CAMERA")
        elif dev.idProduct == 0x02AD:
            print(f"  -> KINECT AUDIO")
        
        print()

print("\n=== ANÁLISIS ===")
print("Para que el video funcione, necesitas:")
print("1. Device PID 02AE (CAMERA) presente")
print("2. Driver WinUSB/libusbK instalado en ese device")
print("3. Acceso permitido (sin errores de claim)")
