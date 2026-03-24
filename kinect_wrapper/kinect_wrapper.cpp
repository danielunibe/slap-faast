// kinect_wrapper.cpp - DLL Wrapper para exportar funciones de libfreenect
#include <windows.h>
#include "libfreenect.h"

// Macros para exportar funciones
#define EXPORT extern "C" __declspec(dllexport)

// Variables globales
static freenect_context* g_ctx = NULL;
static freenect_device* g_dev = NULL;

// Wrapper: Inicializar contexto
EXPORT int kinect_init() {
    if (freenect_init(&g_ctx, NULL) < 0) {
        return -1;
    }
    
    int num_devices = freenect_num_devices(g_ctx);
    if (num_devices <= 0) {
        freenect_shutdown(g_ctx);
        return -2;
    }
    
    if (freenect_open_device(g_ctx, &g_dev, 0) < 0) {
        freenect_shutdown(g_ctx);
        return -3;
    }
    
    return num_devices;
}

// Wrapper: Cerrar
EXPORT void kinect_shutdown() {
    if (g_dev) {
        freenect_close_device(g_dev);
        g_dev = NULL;
    }
    if (g_ctx) {
        freenect_shutdown(g_ctx);
        g_ctx = NULL;
    }
}

// Wrapper: Mover motor
EXPORT int kinect_set_tilt(double degrees) {
    if (!g_dev) return -1;
    return freenect_set_tilt_degs(g_dev, degrees);
}

// Wrapper: Obtener ángulo
EXPORT int kinect_get_tilt(double* angle) {
    if (!g_dev || !angle) return -1;
    freenect_raw_tilt_state* state;
    if (freenect_update_tilt_state(g_dev) < 0) return -2;
    state = freenect_get_tilt_state(g_dev);
    *angle = freenect_get_tilt_degs(state);
    return 0;
}

// Wrapper: LED
EXPORT int kinect_set_led(int color) {
    if (!g_dev) return -1;
    return freenect_set_led(g_dev, (freenect_led_options)color);
}

// Wrapper: Video stream (placeholder para expansión)
EXPORT int kinect_start_video() {
    if (!g_dev) return -1;
    // TODO: Implementar video streaming
    return 0;
}

EXPORT int kinect_stop_video() {
    if (!g_dev) return -1;
    // TODO: Implementar video stop
    return 0;
}
