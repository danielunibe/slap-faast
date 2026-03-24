## Resumen de la Planificación Existente

El objetivo principal del proyecto es desarrollar un programa para Windows 11 que permita a los usuarios controlar su PC mediante gestos utilizando un Kinect v1 (modelo 1414). La idea central es ofrecer un control total del dispositivo y la capacidad de crear y personalizar gestos.

### Puntos Clave y Decisiones:

1.  **Viabilidad del Proyecto**: Se considera viable y realista, aunque requiere trabajo técnico. Se menciona que existen librerías para Kinect 360, aunque algunas son anticuadas, y se necesitará integración manual para traducir gestos en acciones del sistema.

2.  **Tecnologías Sugeridas (Python)**:
    *   **Librerías para Kinect**: `pykinect`, `OpenNI2 + NiTE2`, `libfreenect`. Se sugiere `OpenNI2 + NiTE2` como la opción más estable para el seguimiento corporal.
    *   **Reconocimiento de Gestos**: `MediaPipe` o un modelo de Machine Learning (ML) para flexibilidad y personalización.
    *   **Control del Sistema Operativo**: `pyautogui`, `keyboard`, `win32gui` para emular acciones del sistema.
    *   **Interfaz Gráfica (GUI)**: `Tkinter`, `PyQt` o `Electron` para una interfaz de usuario.

3.  **Concepto de Gestos**: Se busca que los gestos sean evidentes y no interfieran con movimientos cotidianos, evitando falsos positivos. Se propone la idea de un programa que permita al usuario diseñar y entrenar sus propios gestos, asociándolos a acciones específicas del sistema operativo.

4.  **Fase de Investigación Previa al Desarrollo**: Se propone una investigación estructurada en cuatro bloques:
    *   **Tecnologías Base y Soporte Actual**: Identificar librerías funcionales, drivers para Windows 11 y frameworks de reconocimiento de gestos.
    *   **Reconocimiento de Gestos Personalizado**: Determinar el mejor enfoque (esqueletos vs. IA), puntos clave del cuerpo y métodos para gestos dinámicos.
    *   **Mapeo de Gestos a Acciones del SO**: Cómo ejecutar acciones del sistema desde Python/C# y cómo implementar un "modo escucha" para evitar interferencias.
    *   **Interfaz Visual y Lógica de Entrenamiento**: Diseñar la GUI para ver gestos, entrenar gestos propios y asociarlos a comandos.

### Información Faltante y Áreas a Investigar:

*   **Compatibilidad Específica de Drivers**: Aunque se menciona la necesidad de investigar los drivers para Windows 11, no se especifica si hay desafíos conocidos o soluciones particulares para el Kinect v1 en esta versión del SO.
*   **Estado Actual de las Librerías**: Se menciona que algunas librerías son "algo anticuadas". Es crucial investigar el estado actual de mantenimiento y la comunidad de soporte para `pykinect`, `OpenNI2 + NiTE2`, y `libfreenect` en 2025.
*   **Rendimiento y Latencia**: No se aborda explícitamente el rendimiento esperado del sistema de reconocimiento de gestos y la latencia en la ejecución de acciones, lo cual es vital para una buena experiencia de usuario.
*   **Persistencia de Gestos Personalizados**: Cómo se almacenarán y cargarán los gestos personalizados creados por el usuario.
*   **Manejo de Errores y Excepciones**: No se menciona cómo el software manejará errores de conexión del Kinect, fallos en el reconocimiento de gestos, o conflictos con otras aplicaciones.
*   **Seguridad y Privacidad**: Consideraciones sobre la seguridad al permitir que un programa controle el sistema operativo y la privacidad de los datos de movimiento capturados por el Kinect.
*   **Alternativas a Python**: Aunque se sugiere Python, se menciona brevemente Node.js o C# con WPF. Sería útil una justificación más profunda si se descartan estas opciones o si se consideran para partes específicas del proyecto.

Esta planificación inicial proporciona una base sólida, y la fase de investigación propuesta es fundamental para abordar las incertidumbres y refinar el diseño del software.

