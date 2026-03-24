
import usb.core
import usb.util
import time
import sys

# VID/PID
VID = 0x045E
PID = 0x02AE

def main():
    print("🥷 KINECT NINJA INIT - CUSTOM DRIVER ATTEMPT")
    
    # 1. Find Device
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        print("❌ Device not found (Check Zadig/USB connection)")
        return

    print(f"✅ Device found: {dev.bus}/{dev.address}")
    
    # 2. Config & Interface
    try:
        dev.set_configuration()
        print("✅ Config set")
    except Exception as e:
        print(f"⚠️ Set Config warning: {e}")

    try:
        usb.util.claim_interface(dev, 0)
        print("✅ Interface 0 claimed")
    except Exception as e:
        print(f"⚠️ Claim Interface warning: {e}")

    # 3. ISO Bandwidth - Alt Setting 1
    try:
        dev.set_interface_alt_setting(0, 1)
        print("✅ Alt Setting 1 set (ISO Bandwidth Enabled)")
    except Exception as e:
        print(f"❌ Failed to set Alt Setting 1: {e}")
        # Try manual control transfer for SetInterface (0x0B)
        try:
            dev.ctrl_transfer(0x00, 0x0B, 0x01, 0x00, [])
            print("✅ Alt Setting 1 set via Control Transfer")
        except:
             print("   Double failure on Alt Setting. ISO might fail.")

    # 4. MAGIC SEQUENCE (Reverse Engineered from libfreenect)
    print("\n🔮 Sending Magic Start Sequence...")
    
    try:
        # NUI_CAMERA_REG_PROJECTOR_TYPE (0x105)?? No, usually simpler control requests for start.
        # Sequence based on freenect_start_video logs
        
        # 1. Set Video Mode to Off (0x05 -> 0)
        dev.ctrl_transfer(0x40, 0x05, 0x00, 0x00, [])
        
        # 2. Set Format/Resolution ?? (0x06 -> 0)
        # 0x00 = FREENECT_VIDEO_RGB
        dev.ctrl_transfer(0x40, 0x06, 0x00, 0x00, [])
        
        # 3. Set Video Mode to On (0x05 -> 0x01)
        dev.ctrl_transfer(0x40, 0x05, 0x01, 0x00, [])
        
        print("✅ Magic packets sent successfully")
    except Exception as e:
        print(f"❌ Magic init failed: {e}")
        return

    # 5. READ LOOP
    print("\n📡 Attempting to read ISO Stream (EP 0x81)...")
    
    success_bytes = 0
    packets = 0
    
    # Try reading for 3 seconds
    start_t = time.time()
    
    while time.time() - start_t < 3.0:
        try:
            # Read 1920 bytes (bayer line?) or 3008 (max iso)
            data = dev.read(0x81, 3008, timeout=50)
            if len(data) > 0:
                packets += 1
                success_bytes += len(data)
                if packets % 10 == 0:
                    print(f"   Rx: {len(data)} bytes (Total: {success_bytes})")
        except usb.core.USBError as e:
            if e.errno == 10060: # Timeout
                pass
            elif e.errno == 5: # IO Error
                # Check for "reap" issues?
                pass
            else:
                print(f"Error: {e}")

    print("\n" + "="*40)
    print(f"RESULTADO: {packets} packets receiveid, {success_bytes} bytes total.")
    if packets > 0:
        print("🎉 SUCCESS! WE HAVE A CUSTOM DRIVER.")
    else:
        print("💀 FAILURE. No data received.")

if __name__ == "__main__":
    main()
