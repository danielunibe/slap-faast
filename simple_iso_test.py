import usb.core
import usb.util
import usb.backend.libusb1 as lb
import libusb_package
import time

def test_iso():
    print("Buscando Kinect...")
    lib_path = libusb_package.get_library_path()
    backend = lb.get_backend(find_library=lambda x: lib_path)
    
    dev = usb.core.find(idVendor=0x045e, idProduct=0x02ae, backend=backend)
    
    if not dev:
        print("Kinect no encontrado")
        return

    print("Kinect encontrado. Configurando...")
    try:
        dev.set_configuration()
        usb.util.claim_interface(dev, 0)
        dev.set_interface_alt_setting(0, 1)
        print("Alt Setting 1 OK")
    except Exception as e:
        print(f"Error config: {e}")

    # Start stream magic
    try:
        dev.ctrl_transfer(0x40, 0x06, 0x00, 0x00, [])
        dev.ctrl_transfer(0x40, 0x05, 0x01, 0x00, [])
        print("Start commands sent")
    except Exception as e:
        print(f"Error start: {e}")

    # Read loop
    print("Intentando leer del EP 0x81...")
    success_count = 0
    errors = 0
    
    for i in range(50):
        try:
            data = dev.read(0x81, 3008, timeout=100)
            if len(data) > 0:
                print(f"[{i}] DATOS! {len(data)} bytes")
                success_count += 1
        except usb.core.USBError as e:
            if e.errno == 10060:
                print(".", end="", flush=True)
            else:
                print(f"\nError {e.errno}: {e}")
                errors += 1
        
        time.sleep(0.01)

    print(f"\nResumen: {success_count} paquetes ok, {errors} errores")

if __name__ == "__main__":
    test_iso()
