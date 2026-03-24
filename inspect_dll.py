"""
Inspeccionar símbolos exportados de freenect.dll
"""
import ctypes
import sys
from pathlib import Path

dll_path = str(Path(__file__).parent / "freenect.dll")

print(f"Cargando {dll_path}...\n")

try:
    lib = ctypes.CDLL(dll_path)
    print("✅ DLL cargada exitosamente\n")
    
    # Probar funciones básicas que sabemos que existen
    test_functions = [
        "freenect_init",
        "freenect_shutdown",
        "freenect_num_devices",
        "freenect_open_device",
        "freenect_close_device",
        "freenect_set_video_mode",
        "freenect_set_video_callback",
        "freenect_start_video",
        "freenect_stop_video",
        "freenect_process_events",
        "freenect_set_video_format",
        "freenect_set_video_buffer",
    ]
    
    print("Verificando funciones...\n")
    for func_name in test_functions:
        try:
            func = getattr(lib, func_name)
            print(f"✅ {func_name}")
        except AttributeError:
            print(f"❌ {func_name} - NO ENCONTRADA")
    
except Exception as e:
    print(f"❌ Error cargando DLL: {e}")
    sys.exit(1)
