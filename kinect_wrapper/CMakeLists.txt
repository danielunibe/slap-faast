# CMakeLists.txt para kinect_wrapper DLL
cmake_minimum_required(VERSION 3.12)
project(kinect_wrapper)

# Configuración
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Incluir directorios de libfreenect
include_directories(
    "${CMAKE_SOURCE_DIR}/../libfreenect/include"
    "${CMAKE_SOURCE_DIR}/../libusb/include/libusb-1.0"
)

# Biblioteca compartida (DLL)
add_library(kinect_wrapper SHARED
    kinect_wrapper.cpp
)

# Enlazar con libfreenect estática
target_link_libraries(kinect_wrapper
    "${CMAKE_SOURCE_DIR}/../libfreenect/build/lib/Release/freenect.lib"
)

# Configurar salida
set_target_properties(kinect_wrapper PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/../src/drivers"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/../src/drivers"
)
