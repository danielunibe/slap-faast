"""
Test CORREGIDO: Firmas de API correctas de libfreenect.h
"""
import ctypes
from ctypes import c_int, c_void_p, POINTER, byref, create_string_buffer
from pathlib import Path
import numpy as np
import cv2

DLL_PATH = Path(__file__).parent / "freenect.dll"

print("=== TEST LIBFREENECT CORREGIDO ===\n")

try:
    lib = ctypes.CDLL(str(DLL_PATH))
    print("DLL cargada\n")
    
    # Definir tipos correctos segun libfreenect.h
    # freenect_context** y freenect_device** son punteros a punteros
    
    # int freenect_init(freenect_context **ctx, freenect_usb_context *usb_ctx);
    lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
    lib.freenect_init.restype = c_int
    
    # int freenect_shutdown(freenect_context *ctx);
    lib.freenect_shutdown.argtypes = [c_void_p]
    lib.freenect_shutdown.restype = c_int
    
    # int freenect_num_devices(freenect_context *ctx);
    lib.freenect_num_devices.argtypes = [c_void_p]
    lib.freenect_num_devices.restype = c_int
    
    # int freenect_open_device(freenect_context *ctx, freenect_device **dev, int index);
    lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
    lib.freenect_open_device.restype = c_int
    
    # int freenect_close_device(freenect_device *dev);
    lib.freenect_close_device.argtypes = [c_void_p]
    lib.freenect_close_device.restype = c_int
    
    # void freenect_select_subdevices(freenect_context *ctx, freenect_device_flags subdevs);
    lib.freenect_select_subdevices.argtypes = [c_void_p, c_int]
    lib.freenect_select_subdevices.restype = None
    
    # int freenect_set_video_buffer(freenect_device *dev, void *buf);
    lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
    lib.freenect_set_video_buffer.restype = c_int
    
    # int freenect_start_video(freenect_device *dev);
    lib.freenect_start_video.argtypes = [c_void_p]
    lib.freenect_start_video.restype = c_int
    
    # int freenect_stop_video(freenect_device *dev);
    lib.freenect_stop_video.argtypes = [c_void_p]
    lib.freenect_stop_video.restype = c_int
    
    # int freenect_process_events(freenect_context *ctx);
    lib.freenect_process_events.argtypes = [c_void_p]
    lib.freenect_process_events.restype = c_int
    
    # Variables para contexto y dispositivo
    ctx = c_void_p()
    dev = c_void_p()
    
    # 1. Inicializar contexto
    print("1. Inicializando contexto...")
    ret = lib.freenect_init(byref(ctx), None)
    if ret < 0:
        print(f"   FALLO: freenect_init retorno {ret}")
        exit(1)
    print(f"   OK: Contexto inicializado (handle: {ctx.value})")
    
    # 2. Seleccionar subdispositivo CAMERA solo
    print("\n2. Seleccionando subdispositivo camara...")
    FREENECT_DEVICE_CAMERA = 0x02
    lib.freenect_select_subdevices(ctx, FREENECT_DEVICE_CAMERA)
    print("   OK: Solo camara seleccionada")
    
    # 3. Contar dispositivos
    print("\n3. Contando dispositivos...")
    num = lib.freenect_num_devices(ctx)
    print(f"   Dispositivos encontrados: {num}")
    
    if num <= 0:
        print("   FALLO: No hay Kinects conectados")
        lib.freenect_shutdown(ctx)
        exit(1)
    
    # 4. Abrir dispositivo
    print("\n4. Abriendo dispositivo 0...")
    ret = lib.freenect_open_device(ctx, byref(dev), 0)
    if ret < 0:
        print(f"   FALLO: freenect_open_device retorno {ret}")
        lib.freenect_shutdown(ctx)
        exit(1)
    print(f"   OK: Dispositivo abierto (handle: {dev.value})")
    
    # 5. Configurar buffer de video
    print("\n5. Configurando buffer de video...")
    VIDEO_SIZE = 640 * 480 * 3  # RGB
    video_buffer = create_string_buffer(VIDEO_SIZE)
    buffer_ptr = ctypes.cast(video_buffer, c_void_p)
    ret = lib.freenect_set_video_buffer(dev, buffer_ptr)
    print(f"   Set buffer retorno: {ret}")
    
    # 6. Iniciar video
    print("\n6. Iniciando stream de video...")
    ret = lib.freenect_start_video(dev)
    if ret < 0:
        print(f"   FALLO: freenect_start_video retorno {ret}")
    else:
        print(f"   OK: Stream iniciado (ret={ret})")
    
    # 7. Procesar eventos y leer frames
    print("\n7. Procesando eventos y leyendo frames...")
    print("   (Presiona Ctrl+C para salir)\n")
    
    frame_count = 0
    empty_count = 0
    
    while True:
        # Procesar eventos USB
        ret = lib.freenect_process_events(ctx)
        
        # Verificar si hay datos en el buffer
        data = np.frombuffer(video_buffer.raw, dtype=np.uint8)
        data_sum = data.sum()
        
        if data_sum > 0:
            frame_count += 1
            frame = data.reshape((480, 640, 3))
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            cv2.putText(frame_bgr, f"Frame #{frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("KINECT VIDEO - libfreenect", frame_bgr)
            
            if frame_count % 30 == 0:
                print(f"   Frame {frame_count} capturado!")
        else:
            empty_count += 1
            if empty_count % 100 == 0:
                print(f"   Esperando datos... ({empty_count} intentos)")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Limpiar
    cv2.destroyAllWindows()
    lib.freenect_stop_video(dev)
    lib.freenect_close_device(dev)
    lib.freenect_shutdown(ctx)
    
    print(f"\n=== RESULTADO ===")
    print(f"Frames capturados: {frame_count}")
    if frame_count > 0:
        print("VIDEO KINECT FUNCIONAL!")
    else:
        print("No se recibieron frames de video")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
