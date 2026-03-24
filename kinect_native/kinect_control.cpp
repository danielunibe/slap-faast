// kinect_control.cpp - Ejecutable C++ standalone para controlar Kinect
// Compilar: cl /EHsc /I"..\libfreenect\include" /I"..\libusb\include\libusb-1.0" kinect_control.cpp ..\libfreenect\build\lib\Release\freenect.lib ..\libusb\VS2022\MS64\static\libusb-1.0.lib /link /OUT:kinect_control.exe

#include <iostream>
#include <string>
#include "libfreenect.h"

using namespace std;

freenect_context* ctx = NULL;
freenect_device* dev = NULL;

bool init_kinect() {
    if (freenect_init(&ctx, NULL) < 0) {
        cerr << "ERROR:INIT_FAILED" << endl;
        return false;
    }
    
    int num = freenect_num_devices(ctx);
    if (num <= 0) {
        cerr << "ERROR:NO_DEVICES" << endl;
        return false;
    }
    
    if (freenect_open_device(ctx, &dev, 0) < 0) {
        cerr << "ERROR:OPEN_FAILED" << endl;
        return false;
    }
    
    cout << "OK:CONNECTED:" << num << endl;
    return true;
}

void shutdown_kinect() {
    if (dev) freenect_close_device(dev);
    if (ctx) freenect_shutdown(ctx);
}

int main(int argc, char** argv) {
    if (argc < 2) {
        cerr << "ERROR:NO_COMMAND" << endl;
        return 1;
    }
    
    string cmd = argv[1];
    
    if (cmd == "init") {
        if (!init_kinect()) return 1;
        shutdown_kinect();
        return 0;
    }
    
    // Inicializar para otros comandos
    if (!init_kinect()) return 1;
    
    if (cmd == "tilt") {
        if (argc < 3) {
            cerr << "ERROR:NO_ANGLE" << endl;
            return 1;
        }
        double angle = stod(argv[2]);
        if (freenect_set_tilt_degs(dev, angle) < 0) {
            cerr << "ERROR:TILT_FAILED" << endl;
            return 1;
        }
        cout << "OK:TILT:" << angle << endl;
    }
    else if (cmd == "led") {
        if (argc < 3) {
            cerr << "ERROR:NO_COLOR" << endl;
            return 1;
        }
        int color = stoi(argv[2]);
        if (freenect_set_led(dev, (freenect_led_options)color) < 0) {
            cerr << "ERROR:LED_FAILED" << endl;
            return 1;
        }
        cout << "OK:LED:" << color << endl;
    }
    else {
        cerr << "ERROR:UNKNOWN_COMMAND:" << cmd << endl;
        return 1;
    }
    
    shutdown_kinect();
    return 0;
}
