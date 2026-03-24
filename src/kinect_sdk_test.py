"""
Test de acceso directo al Kinect v1 via SDK de Microsoft.
Requiere: Kinect SDK 1.8 instalado en el sistema.
"""
import ctypes
from ctypes import wintypes
import time

# Cargar la DLL del SDK
try:
    kinect_dll = ctypes.windll.LoadLibrary("Kinect10.dll")
    print("✅ Kinect10.dll cargado correctamente.")
except OSError as e:
    print(f"❌ Error cargando Kinect10.dll: {e}")
    exit(1)

# Definiciones de tipos (simplificadas)
HRESULT = ctypes.c_long
S_OK = 0

# NuiInitialize
NUI_INITIALIZE_FLAG_USES_COLOR = 0x00000010
NUI_INITIALIZE_FLAG_USES_DEPTH = 0x00000020
NUI_INITIALIZE_FLAG_USES_SKELETON = 0x00000008

try:
    NuiInitialize = kinect_dll.NuiInitialize
    NuiInitialize.argtypes = [ctypes.c_uint32]
    NuiInitialize.restype = HRESULT
except AttributeError:
    print("⚠️  NuiInitialize no encontrado. SDK incompleto.")
    exit(1)

print("Intentando inicializar Kinect...")
flags = NUI_INITIALIZE_FLAG_USES_COLOR | NUI_INITIALIZE_FLAG_USES_DEPTH
result = NuiInitialize(flags)

if result == S_OK:
    print("✅✅✅ KINECT INICIALIZADO CORRECTAMENTE ✅✅✅")
    print("    El SDK tiene acceso al hardware.")
    # Limpiar
    NuiShutdown = kinect_dll.NuiShutdown
    NuiShutdown()
else:
    # Interpretar códigos de error comunes
    errors = {
        -2147024894: "ERROR_FILE_NOT_FOUND: Kinect no conectado o sin power.",
        -2147024891: "ERROR_ACCESS_DENIED: Otro programa está usando el Kinect.",
        -2147024809: "ERROR_INVALID_PARAMETER: Flags de inicialización incorrectos.",
        -1: "E_FAIL: Fallo genérico del SDK.",
    }
    error_msg = errors.get(result, f"Código desconocido: {result} ({hex(result)})")
    print(f"❌ Error de inicialización: {error_msg}")
