"""
Kinect v1 USB Driver - Implementación directa usando PyUSB
Sin dependencia del SDK de Microsoft ni libfreenect.
Basado en el protocolo USB documentado del Kinect v1.
"""
import os
import sys

# Configurar path para libusb DLL antes de importar usb.core
if sys.platform == 'win32':
    try:
        import libusb_package
        dll_path = os.path.dirname(libusb_package.get_library_path())
        if os.path.exists(dll_path):
            os.add_dll_directory(dll_path)
    except Exception as e:
        pass  # Si falla, pyusb intentará encontrar la DLL por otros medios

import usb.core
import usb.util
import numpy as np
from loguru import logger
import struct

class KinectUSBDriver:
    """Driver USB directo para Kinect v1 (Xbox 360)"""
    
    # VID/PID del Kinect v1
    KINECT_CAMERA_VID = 0x045e
    KINECT_CAMERA_PID = 0x02ae  # Xbox 360 Kinect Camera
    KINECT_MOTOR_PID = 0x02b0   # Xbox 360 Kinect Motor
    KINECT_AUDIO_PID = 0x02ad   # Xbox 360 Kinect Audio
    
    def __init__(self):
        self._camera_dev = None
        self._motor_dev = None
        self._connected = False
        self._initialize()
    
    def _initialize(self):
        logger.info("🔍 Buscando Kinect v1 en el bus USB...")
        
        # Buscar dispositivo de cámara
        self._camera_dev = usb.core.find(
            idVendor=self.KINECT_CAMERA_VID,
            idProduct=self.KINECT_CAMERA_PID
        )
        
        if self._camera_dev is None:
            logger.error("❌ No se detectó Kinect Camera (VID:045E PID:02AE)")
            return
        
        logger.info(f"✅ Kinect Camera detectado: Bus {self._camera_dev.bus}, Address {self._camera_dev.address}")
        
        # Buscar dispositivo de motor
        self._motor_dev = usb.core.find(
            idVendor=self.KINECT_CAMERA_VID,
            idProduct=self.KINECT_MOTOR_PID
        )
        
        if self._motor_dev:
            logger.info(f"✅ Kinect Motor detectado")
        
        try:
            # En Windows con libusb-win32, no necesitamos detach kernel driver
            usb.util.claim_interface(self._camera_dev, 0)
            self._connected = True
            logger.success("✅ Kinect inicializado correctamente via USB")
            
        except usb.core.USBError as e:
            logger.error(f"❌ Error al reclamar interfaz USB: {e}")
    
    def isOpened(self):
        return self._connected and self._camera_dev is not None
    
    def read(self):
        """
        Intenta leer frame de video del Kinect.
        NOTA: Implementación completa requiere protocolo UVC del Kinect.
        """
        if not self.isOpened():
            return False, None
        
        try:
            # Esto es un stub - la implementación completa requiere
            # parsear el protocolo UVC del Kinect (complejo)
            # Por ahora retornamos un frame de prueba
            logger.debug("Stub: read() - requiere implementación UVC completa")
            return False, None
            
        except Exception as e:
            logger.error(f"Error leyendo frame: {e}")
            return False, None
    
    def set_led(self, color):
        """
        Controla el LED del Kinect.
        color: 0=Off, 1=Green, 2=Red, 3=Yellow, 4=Blink Yellow, 5=Blink Green, 6=Blink Red/Yellow
        """
        if not self._motor_dev:
            return False
        
        try:
            # Comando USB para cambiar LED
            # Endpoint: 0x00, bmRequestType: 0x40
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x06,
                wValue=color,
                wIndex=0,
                data_or_wLength=None
            )
            logger.success(f"✅ LED cambiado a color {color}")
            return True
        except Exception as e:
            logger.error(f"Error cambiando LED: {e}")
            return False
    
    def set_tilt(self, angle):
        """
        Cambia la inclinación del motor del Kinect.
        angle: -31 a +31 grados
        """
        if not self._motor_dev:
            return False
        
        try:
            # Limitar ángulo
            angle = max(-31, min(31, angle))
            
            # Convertir ángulo a valor de motor (escala aproximada)
            motor_value = int(angle * 2)
            
            # Comando USB para mover motor
            self._motor_dev.ctrl_transfer(
                bmRequestType=0x40,
                bRequest=0x31,
                wValue=motor_value,
                wIndex=0,
                data_or_wLength=None
            )
            logger.success(f"✅ Motor inclinado a {angle}°")
            return True
        except Exception as e:
            logger.error(f"Error moviendo motor: {e}")
            return False
    
    def release(self):
        if self._camera_dev:
            try:
                usb.util.release_interface(self._camera_dev, 0)
                usb.util.dispose_resources(self._camera_dev)
            except:
                pass
        
        if self._motor_dev:
            try:
                usb.util.dispose_resources(self._motor_dev)
            except:
                pass
        
        logger.info("Kinect USB Driver liberado")


# Test del driver
if __name__ == "__main__":
    driver = KinectUSBDriver()
    
    if driver.isOpened():
        print("\n✅ Kinect detectado y conectado!")
        print("\nProbando control del LED...")
        
        import time
        
        # Ciclo de colores
        for color, name in [(1, "Verde"), (2, "Rojo"), (3, "Amarillo"), (0, "Apagado")]:
            print(f"  LED: {name}")
            driver.set_led(color)
            time.sleep(1)
        
        # Probar motor
        print("\nProbando motor...")
        for angle in [10, 0, -10, 0]:
            print(f"  Inclinación: {angle}°")
            driver.set_tilt(angle)
            time.sleep(1.5)
        
        driver.release()
    else:
        print("❌ No se pudo conectar al Kinect")
        print("   Asegúrate de:")
        print("   1. El Kinect esté conectado y con luz")
        print("   2. Los drivers estén en modo WinUSB (usar Zadig)")
