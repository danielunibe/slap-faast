# Guía de Instalación de Drivers Kinect (Zadig)

Si deseas activar la **Cámara Kinect (Video)** en Windows sin el SDK oficial, necesitas reemplazar manualmente los drivers usando **Zadig**.

> **⚠️ ADVERTENCIA:** Esto es avanzado. Si el paso falla, podrías perder acceso al motor/LED momentáneamente hasta reinstalar.

## Pasos

1.  Descarga **Zadig** (ya está en la carpeta del proyecto: `zadig-2.9.exe`).
2.  Abre Zadig como Administrador.
3.  Menú `Options` → Marca `List All Devices`.
4.  Busca **"Xbox NUI Camera"** en la lista desplegable.
    *   *Verifica que el USB ID sea `045E : 02AE`*
5.  En la caja de driver (derecha), selecciona **`WinUSB (v6.1...)`**.
    *   *WinUSB es el driver nativo que mejor funciona con nuestras librerías modernas.*
    *   *Si WinUSB falla después de probar, puedes intentar `libusbK` como alternativa.*
6.  Click en **"Replace Driver"** o **"Install Driver"**.
7.  Espera a que termine.
8.  **Reinicia tu PC** (Recomendado) o desconecta/conecta el Kinect.

## Verificación

Una vez hecho esto:
1.  Ejecuta `python kinect_test_gui.py`
2.  El sistema intentará conectarse. Si `libusbK` funciona, verás video del Kinect en lugar de la webcam.

## Si algo sale mal
Siempre puedes revertir:
1.  Abre "Administrador de Dispositivos".
2.  Busca el dispositivo Kinect.
3.  Click derecho → "Desinstalar dispositivo" (marcando "Eliminar software de controlador").
4.  Reinicia y Windows instalará el driver por defecto (o usa Zadig para poner WinUSB de nuevo para Motor).
