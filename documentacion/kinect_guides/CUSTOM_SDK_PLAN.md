# Plan: Nuestro SDK Personalizado para Kinect

## Estrategia
Usaremos el **SDK 1.8 de Microsoft como capa de drivers** (para el acceso USB a nivel de kernel), pero construiremos **nuestra propia API en Python** que llame directamente a las funciones de la DLL oficial.

## Arquitectura

```
┌─────────────────────────────────────────────┐
│           SLAP!FAAST CUSTOM SDK             │
│  (Python - kinect_native_bridge.py)         │
├─────────────────────────────────────────────┤
│           ctypes / cffi                     │
├─────────────────────────────────────────────┤
│         Kinect10.dll (Microsoft)            │
├─────────────────────────────────────────────┤
│     kinectusa.sys / kinectcam.sys           │
│         (Kernel Mode Drivers)               │
├─────────────────────────────────────────────┤
│              USB Hardware                   │
└─────────────────────────────────────────────┘
```

## Componentes del SDK Oficial que Usaremos

### 1. DLL Principal: `Kinect10.dll`
Ubicación: `C:\Windows\System32\Kinect10.dll`
Contiene las funciones NUI:

| Función | Uso |
|---------|-----|
| `NuiInitialize` | Inicializa el sensor |
| `NuiShutdown` | Cierra la conexión |
| `NuiCameraElevationSetAngle` | Control del motor (tilt) |
| `NuiCameraElevationGetAngle` | Lee ángulo actual |
| `NuiImageStreamOpen` | Abre stream de video/depth |
| `NuiImageStreamGetNextFrame` | Obtiene frame |
| `NuiSkeletonTrackingEnable` | Activa skeleton tracking |

### 2. APIs de Control de Hardware

#### Motor (Tilt)
```python
# Rango: -27 a +27 grados
NuiCameraElevationSetAngle(angle: c_long) -> HRESULT
```

#### LED
El LED se controla implícitamente:
- Verde = Drivers cargados correctamente
- Rojo = Error
- Parpadeo = Inicializando

Para control manual del LED, usaremos nuestro driver USB existente (`kinect_usb_driver.py`) que ya funciona.

### 3. Video Streams
```python
# Tipos de stream
NUI_IMAGE_TYPE_COLOR = 0
NUI_IMAGE_TYPE_DEPTH = 1
NUI_IMAGE_TYPE_DEPTH_AND_PLAYER_INDEX = 2
```

## Pasos de Implementación

1. **Prerequisito**: Usuario instala SDK 1.8 (solo para tener `Kinect10.dll` y drivers).
2. **Crear `kinect_native_bridge.py`**: Wrapper Python que carga la DLL con `ctypes`.
3. **Exponer API Limpia**: Funciones simples como `kinect.set_tilt(15)`, `kinect.get_frame()`.
4. **Integrar con `main.py`**: Usar nuestro bridge en lugar de OpenCV directo.

## Ventajas de Este Enfoque
- ✅ Control total desde Python.
- ✅ Acceso a funciones que OpenCV no expone (Motor, Depth raw, Skeleton).
- ✅ No dependemos de wrappers de terceros como `pykinect`.
- ✅ Podemos extender y modificar a gusto.
- ✅ El "trabajo sucio" del USB lo hace el driver de Microsoft.

## Próximo Paso
Implementar `kinect_native_bridge.py` con las funciones básicas.
