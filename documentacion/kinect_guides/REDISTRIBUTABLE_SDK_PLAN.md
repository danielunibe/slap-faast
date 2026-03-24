# Plan: SDK Propio Redistribuible con libfreenect

## El Camino Correcto
Para crear un driver que podamos distribuir comercialmente, usaremos **libfreenect** (OpenKinect):
- Licencia: Apache 2.0 / GPL2 = **100% Redistribuible**
- Ya tiene todo el protocolo USB implementado
- Lo compilamos como nuestra propia DLL

## Arquitectura Final

```
┌─────────────────────────────────────────────┐
│        SLAP!FAAST (Producto Final)          │
│            (Python + GUI)                   │
├─────────────────────────────────────────────┤
│     kinect_freenect_bridge.py (ctypes)      │
├─────────────────────────────────────────────┤
│    libfreenect.dll (NUESTRA DLL compilada)  │  ← Redistribuible
├─────────────────────────────────────────────┤
│         libusbK.dll (open source)           │  ← Redistribuible
├─────────────────────────────────────────────┤
│              Hardware Kinect                │
└─────────────────────────────────────────────┘
```

## Prerequisitos para Compilar

| Herramienta | Propósito | Instalación |
|-------------|-----------|-------------|
| Visual Studio 2019/2022 | Compilador C++ | Descargar de Microsoft (gratis Community) |
| CMake | Sistema de build | `winget install cmake` |
| Git | Clonar repositorio | `winget install git` |
| libusb-win32 | Acceso USB | Incluido en el repo |

## Pasos de Compilación

### 1. Clonar libfreenect
```bash
git clone https://github.com/OpenKinect/libfreenect.git
cd libfreenect
```

### 2. Crear directorio de build
```bash
mkdir build
cd build
```

### 3. Generar proyecto con CMake
```bash
cmake .. -G "Visual Studio 17 2022" -DBUILD_REDIST_PACKAGE=ON
```

### 4. Compilar
```bash
cmake --build . --config Release
```

### 5. Resultado
- `freenect.dll` - Nuestra DLL redistribuible
- `freenect.lib` - Para linking
- Ejemplos compilados para verificar

## Distribución al Usuario Final
El usuario solo necesita:
1. Instalar nuestro software (que incluye `freenect.dll`)
2. Instalar driver libusbK para el Kinect (Zadig - incluido en nuestro instalador)
3. ¡Listo!

## Siguiente Paso
¿Tienes Visual Studio instalado? Si no, lo descargamos primero.
