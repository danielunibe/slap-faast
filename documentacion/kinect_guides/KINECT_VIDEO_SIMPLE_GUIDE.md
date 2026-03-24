# Guía Final: Activar Video Kinect con OpenCV

## El Problema
Tenemos control del motor/LED pero falta el video.

## La Solución Simple
No necesitamos compilar nada. Solo necesitamos que Windows vea el Kinect como cámara UVC.

## Pasos

### 1. Descargar Zadig
Zadig es una herramienta para instalar drivers USB genéricos.
- URL: https://zadig.akeo.ie/

### 2. Instalar Driver libusbK para la Cámara
1. Conecta el Kinect
2. Abre Zadig
3. Ve a Options → List All Devices
4. Selecciona "Xbox NUI Camera" (VID: 045E, PID: 02AE)
5. En el dropdown de driver, selecciona **"WinUSB"** o **"libusbK"**
6. Click "Replace Driver" o "Install Driver"
7. Espera a que termine

### 3. Verificar en Device Manager
Abre Device Manager (devmgmt.msc):
- Deberías ver "Xbox NUI Camera" bajo "libusbK USB Devices" o "Universal Serial Bus devices"

### 4. Probar con OpenCV
```python
import cv2

# Probar índices de cámara
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"Cámara {i}: {frame.shape}")
        cap.release()
```

El Kinect debería aparecer en uno de esos índices.

### 5. Usar con Nuestro Sistema
Una vez que OpenCV detecte el Kinect, ya tienes:
- ✅ Video (OpenCV)
- ✅ Motor (kinect_direct_driver.py)
- ✅ LED (kinect_direct_driver.py)
- ✅ Tracking (hybrid_tracker.py)

## Si No Funciona
Alternativa: Instalar Kinect SDK 1.8 oficial (5 minutos, garantizado que funciona).

El SDK instala drivers certificados que Windows reconoce automáticamente.
