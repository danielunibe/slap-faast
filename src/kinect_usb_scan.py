"""
Kinect USB Scanner - Escanea todos los dispositivos USB del Kinect v1
"""
import usb.core
import usb.util

print("=" * 60)
print("KINECT V1 USB DEVICE SCANNER")
print("=" * 60)

# Kinect v1 Product IDs
KINECT_DEVICES = {
    0x02b0: "Xbox NUI Motor",
    0x02ad: "Xbox NUI Audio", 
    0x02ae: "Xbox NUI Camera",
    0x02c2: "Xbox NUI Motor (alt)",
}

# Buscar todos los dispositivos Microsoft
devices = list(usb.core.find(find_all=True, idVendor=0x045e))

print(f"\nDispositivos Microsoft encontrados: {len(devices)}")
print("-" * 60)

for dev in devices:
    pid = dev.idProduct
    name = KINECT_DEVICES.get(pid, "Unknown")
    
    try:
        product_str = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "N/A"
    except:
        product_str = "N/A"
    
    print(f"\n[0x{pid:04x}] {name}")
    print(f"  Product String: {product_str}")
    print(f"  Bus: {dev.bus}, Address: {dev.address}")
    print(f"  Configurations: {dev.bNumConfigurations}")
    
    # Listar interfaces
    try:
        for cfg in dev:
            print(f"  Config {cfg.bConfigurationValue}:")
            for intf in cfg:
                print(f"    Interface {intf.bInterfaceNumber}: " +
                      f"Class=0x{intf.bInterfaceClass:02x}, " +
                      f"SubClass=0x{intf.bInterfaceSubClass:02x}, " +
                      f"Endpoints={intf.bNumEndpoints}")
                
                for ep in intf:
                    direction = "IN" if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"
                    ep_type_code = usb.util.endpoint_type(ep.bmAttributes)
                    ep_type = {0: "CTRL", 1: "ISO", 2: "BULK", 3: "INT"}.get(ep_type_code, f"? ({ep_type_code})")
                    
                    print(f"      EP 0x{ep.bEndpointAddress:02x}: {direction} {ep_type}")
                    print(f"        MaxPacket={ep.wMaxPacketSize}")
                    print(f"        Attributes=0x{ep.bmAttributes:02x}")
                    print(f"        Interval={ep.bInterval}")

    except Exception as e:
        print(f"  Error listing interfaces: {e}")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)

motor = usb.core.find(idVendor=0x045e, idProduct=0x02b0)
audio = usb.core.find(idVendor=0x045e, idProduct=0x02ad)
camera = usb.core.find(idVendor=0x045e, idProduct=0x02ae)

print(f"Motor (02b0):  {'ENCONTRADO' if motor else 'NO ENCONTRADO'}")
print(f"Audio (02ad):  {'ENCONTRADO' if audio else 'NO ENCONTRADO'}")
print(f"Camera (02ae): {'ENCONTRADO' if camera else 'NO ENCONTRADO'}")
