"""
Test simple directo del dispositivo de cámara
"""
import usb.core
import usb.util

print("Buscando dispositivo cámara (045E:02AE)...")

try:
    # Método 1: find directo
    dev = usb.core.find(idVendor=0x045E, idProduct=0x02AE)
    
    if dev is None:
        print("❌ No encontrado con find()")
    else:
        print(f"✅ Encontrado: Bus {dev.bus}, Address {dev.address}")
        
        # Intentar set_configuration
        try:
            dev.set_configuration()
            print("✅ Configuration set")
        except usb.core.USBError as e:
            print(f"⚠️  Set config: {e}")
        
        # Intentar claim interface 
        try:
            usb.util.claim_interface(dev, 0)
            print("✅ Interface 0 claimed")
        except usb.core.USBError as e:
            print(f"⚠️  Claim: {e}")
        
        # Intentar SET_INTERFACE (Alt Setting 1)
        try:
            dev.ctrl_transfer(0x01, 0x0B, 1, 0, 0)
            print("✅ Alt Setting 1 activado")
        except usb.core.USBError as e:
            print(f"❌ Alt Setting: {e}")
        
        # Intentar lectura ISO
        try:
            print("Intentando leer endpoint 0x81...")
            data = dev.read(0x81, 1920, timeout=2000)
            print(f"🎉 ÉXITO: {len(data)} bytes leídos")
        except usb.core.USBTimeoutError:
            print("⏱️  Timeout (normal si stream no está activo)")
        except usb.core.USBError as e:
            print(f"❌ Read error: {e}")
        
        # Limpiar
        try:
            usb.util.release_interface(dev, 0)
        except:
            pass
            
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
