"""
Kinect v1 Driver usando WinUSB directamente via ctypes.
Compatible con el driver WinUSB instalado por Zadig.
"""
import ctypes
from ctypes import wintypes
import time
from loguru import logger

# Cargar DLLs de Windows
setupapi = ctypes.windll.LoadLibrary("setupapi.dll")
winusb = ctypes.windll.LoadLibrary("winusb.dll")
kernel32 = ctypes.windll.kernel32

# Constantes
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_OVERLAPPED = 0x40000000

# GUIDs
GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"

# Kinect VID/PID
KINECT_CAMERA_VID = 0x045e
KINECT_CAMERA_PID = 0x02ae
KINECT_MOTOR_VID = 0x045e
KINECT_MOTOR_PID = 0x02b0

class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize",wintypes.DWORD),
        ("InterfaceClassGuid", wintypes.BYTE * 16),
        ("Flags", wintypes.DWORD),
        ("Reserved", ctypes.POINTER(wintypes.ULONG))
    ]

class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("ClassGuid", wintypes.BYTE * 16),
        ("DevInst", wintypes.DWORD),
        ("Reserved", ctypes.POINTER(wintypes.ULONG))
    ]

def find_kinect_device_path():
    """Busca el path del dispositivo Kinect usando SetupAPI."""
    logger.info("Buscando dispositivo Kinect con WinUSB...")
    
    # Convertir GUID string a bytes
    guid = ctypes.create_unicode_buffer(GUID_DEVINTERFACE_USB_DEVICE)
    guid_struct = (wintypes.BYTE * 16)()
    
    # Obtener lista de dispositivos USB
    device_info_set = setupapi.SetupDiGetClassDevsW(
        None,
        ctypes.c_wchar_p("USB"),
        None,
        0x00000010 | 0x00000002  # DIGCF_PRESENT | DIGCF_ALLCLASSES
    )
    
    if device_info_set == -1:
        logger.error("No se pudo enumerar dispositivos USB")
        return None
    
    # Buscar dispositivo Kinect
    index = 0
    while True:
        dev_info_data = SP_DEVINFO_DATA()
        dev_info_data.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)
        
        if not setupapi.SetupDiEnumDeviceInfo(device_info_set, index, ctypes.byref(dev_info_data)):
            break
        
        # Obtener Hardware ID
        buffer = ctypes.create_unicode_buffer(256)
        if setupapi.SetupDiGetDeviceRegistryPropertyW(
            device_info_set,
            ctypes.byref(dev_info_data),
            0x00000001,  # SPDRP_HARDWAREID
            None,
            ctypes.cast(buffer, ctypes.POINTER(wintypes.BYTE)),
            ctypes.sizeof(buffer),
            None
        ):
            hw_id = buffer.value
            # Buscar VID/PID del Kinect
            if f"VID_{KINECT_CAMERA_VID:04X}" in hw_id.upper() and f"PID_{KINECT_CAMERA_PID:04X}" in hw_id.upper():
                logger.success(f"✅ Kinect Camera encontrado: {hw_id}")
                
                # Obtener Device Path
                interface_data = SP_DEVICE_INTERFACE_DATA()
                interface_data.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)
                
                # Este path es complejo de obtener - por ahora retornamos señal de éxito
                setupapi.SetupDiDestroyDeviceInfoList(device_info_set)
                return f"Kinect detectado: {hw_id}"
        
        index += 1
    
    setupapi.SetupDiDestroyDeviceInfoList(device_info_set)
    logger.error("❌ Kinect no encontrado en el sistema")
    return None

class KinectWinUSBDriver:
    """Driver simplificado que verifica detección del Kinect."""
    
    def __init__(self):
        self._device_path = find_kinect_device_path()
        self._connected = self._device_path is not None
    
    def isOpened(self):
        return self._connected
    
    def test_detection(self):
        """Prueba simple de detección."""
        if self._connected:
            logger.success("🎉 KINECT DETECTADO POR WINDOWS CON WINUSB!")
            logger.info("Aunque pyusb no funciona con WinUSB, el driver está correctamente instalado.")
            logger.info("Para acceso completo, necesitarías:")
            logger.info("  1. Reinstalar con libusbK en Zadig (en lugar de WinUSB), o")
            logger.info("  2. Usar libfreenect compilado, o")
            logger.info("  3. Implementar protocolo WinUSB completo en Python")
            return True
        else:
            logger.error("Kinect no detectado")
            return False
    
    def release(self):
        pass

if __name__ == "__main__":
    driver = KinectWinUSBDriver()
    driver.test_detection()
