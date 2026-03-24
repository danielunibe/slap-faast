"""
Test usando la librería oficial pykinect para Kinect v1.
"""
try:
    from pykinect import nui
    print("✅ pykinect importado correctamente.")
except ImportError as e:
    print(f"❌ Error importando pykinect: {e}")
    exit(1)

print("Intentando conectar con el Kinect v1...")

try:
    kinect = nui.Runtime()
    print("✅✅✅ KINECT V1 CONECTADO ✅✅✅")
    print(f"    Unique Device ID: {kinect.unique_device_id}")
    kinect.close()
except Exception as e:
    print(f"❌ Error al conectar: {type(e).__name__}: {e}")
    
    # Diagnóstico adicional
    if "no Kinect sensor" in str(e).lower():
        print("\n⚠️  DIAGNÓSTICO: El SDK no detecta ningún Kinect conectado.")
        print("    1. Verifica que el Kinect tenga LUZ VERDE (no naranja).")
        print("    2. Si es naranja, conecta el adaptador de corriente AC.")
        print("    3. Prueba otro puerto USB 3.0.")
