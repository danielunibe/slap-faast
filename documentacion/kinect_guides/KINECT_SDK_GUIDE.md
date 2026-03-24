# Guía Definitiva: Kinect SDK 1.8

Esta es la solución "Nuclear" que **garantiza** video en el Kinect v1 para Windows 10/11.
Al instalar los drivers oficiales, Windows reconoce la cámara nativamente y OpenCV puede usarla sin trucos.

> **IMPORTANTE**: Esto sobrescribirá los drivers que pusimos con Zadig. Está bien, es lo que queremos para Video.

## Paso 1: Limpieza
1. Abre **Administrador de Dispositivos**.
2. Busca "Xbox NUI Camera" (probablemente bajo "Dispositivos USB" o "Cámaras").
3. Click derecho -> **Desinstalar dispositivo**.
4. Marca la casilla **"Eliminar software de controlador"**.
5. Haz lo mismo para "Xbox NUI Motor" y "Audio" si aparecen con drivers Zadig/libusbK.
6. Desconecta el Kinect.

## Paso 2: Instalación SDK
1. Descarga el **Kinect SDK 1.8** oficial de Microsoft:
   **[Descargar Kinect SDK 1.8](https://www.microsoft.com/en-us/download/details.aspx?id=40278)**
2. Ejecuta el instalador (`KinectSDK-v1.8-Setup.exe`).
3. Instala todo (Runtime y Drivers son lo importante).
4. **REINICIA TU COMPUTADORA**.

## Paso 3: Verificación
1. Conecta el Kinect.
2. Espera a que Windows instale dispositivos.
3. Debería aparecer "Kinect for Windows" en el Administrador de Dispositivos.
4. La luz del Kinect debería encenderse (Verde).

## Paso 4: Prueba
Ejecuta de nuevo nuestro test:
`python kinect_test_gui.py`

Ahora OpenCV (`cv2.VideoCapture`) encontrará la cámara del Kinect automágicamente.
