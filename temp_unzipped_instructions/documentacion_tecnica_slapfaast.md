# Documentación Técnica de Slap!Faast

## Versión: 1.0
## Fecha: 22 de junio de 2025
## Autor: Manus AI

## Resumen Ejecutivo

Este documento detalla la planificación y el diseño técnico del software **Slap!Faast**, una aplicación para Windows 11 que permitirá a los usuarios controlar su sistema operativo mediante gestos utilizando sensores Kinect. El proyecto busca ofrecer compatibilidad con los modelos Kinect v1 (modelo 1414), Kinect v2 y Azure Kinect DK, proporcionando una solución flexible y personalizable para la interacción gestual. El enfoque principal de Slap!Faast es capacitar a los usuarios para definir, entrenar y mapear sus propios gestos a una amplia gama de acciones del sistema operativo, mejorando la accesibilidad y la eficiencia en el uso del PC.





## 1. Resumen de la Planificación Existente




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




## 2. Investigación Técnica del Kinect v1




### 2.1. Soporte de Kinect v1 (Modelo 1414) en Windows 11

El Kinect v1, originalmente diseñado para Xbox 360 y posteriormente con soporte oficial para Windows hasta Windows 10 a través del *Kinect for Windows SDK v1.8*, no cuenta con soporte oficial directo ni controladores específicos para Windows 11 por parte de Microsoft. La compañía ha descontinuado el desarrollo y soporte para esta versión del sensor.

Sin embargo, la comunidad de usuarios ha encontrado **soluciones y métodos alternativos** para hacerlo funcionar en Windows 11. Estos métodos generalmente implican:

*   **Instalación del *Kinect for Windows SDK v1.8***: Aunque está diseñado para versiones anteriores de Windows, este SDK incluye los controladores necesarios que, con ajustes, pueden ser reconocidos por Windows 11.
*   **Actualización Manual de Controladores**: En muchos casos, es necesario acceder al Administrador de Dispositivos de Windows 11 y actualizar manualmente los controladores del Kinect, seleccionando los que vienen con el SDK v1.8.
*   **Deshabilitar la Integridad de Memoria**: Algunos usuarios han reportado que la función de "Integridad de Memoria" en la Seguridad de Windows 11 puede interferir con el funcionamiento del Kinect. Deshabilitarla (bajo `Seguridad de Windows > Seguridad del dispositivo > Aislamiento del núcleo`) ha resuelto problemas para algunos.

**Conclusión sobre el soporte**: Es posible hacer funcionar el Kinect v1 en Windows 11, pero requiere pasos manuales y no hay garantía de estabilidad total debido a la falta de soporte oficial. La solución dependerá en gran medida de la persistencia del usuario y de la configuración específica de su sistema.

### 2.2. Librerías para Interacción con Kinect v1 en Python

La planificación inicial sugirió varias librerías para interactuar con el Kinect v1 en Python. A continuación, se detalla el estado actual y la compatibilidad con Windows 11 y Python:

#### a) `libfreenect`

*   **Descripción**: `libfreenect` es una librería de código abierto que proporciona una interfaz de bajo nivel para el sensor Kinect. Permite acceder a los datos de profundidad, color y audio directamente desde el hardware.
*   **Compatibilidad con Windows 11 y Python**: El repositorio oficial de `libfreenect` en GitHub indica soporte para Windows y Python. Sin embargo, se han reportado **problemas de compilación en Windows 10 y 11**, particularmente relacionados con la gestión de hilos (`pthreads`). Esto sugiere que la instalación y configuración en un entorno Windows moderno puede ser compleja y requerir conocimientos avanzados de compilación y resolución de dependencias. Existen bindings de Python (`pylibfreenect`), pero su instalación también puede ser desafiante debido a las dependencias de compilación.
*   **Estado Actual**: El proyecto parece tener actividad, pero la instalación en Windows puede ser un obstáculo significativo para usuarios no técnicos.

#### b) `OpenNI2` y `NiTE2`

*   **Descripción**: `OpenNI` (Open Natural Interaction) es un framework multiplataforma para el desarrollo de aplicaciones de interacción natural. `NiTE` (Natural Interaction Technologies) es un middleware construido sobre OpenNI que proporciona funcionalidades avanzadas como el seguimiento de esqueletos y el reconocimiento de gestos. `OpenNI2` es la segunda generación del framework.
*   **Compatibilidad con Windows 11 y Python**: Existen bindings de Python para `OpenNI2` y `NiTE2` (por ejemplo, el paquete `openni` en PyPI). Sin embargo, estos bindings requieren que `OpenNI2` y `NiTE2` estén instalados previamente en el sistema. La instalación de `OpenNI2` y `NiTE2` en Windows 11 puede ser problemática, ya que los proyectos originales fueron descontinuados por PrimeSense (adquirida por Apple). Aunque hay versiones comunitarias y forks, encontrar binarios estables y actualizados para Windows 11 puede ser difícil. La mayoría de las referencias a la instalación son de hace varios años, lo que indica una falta de soporte activo para las versiones más recientes de Windows.
*   **Estado Actual**: Aunque potentes para el seguimiento de esqueletos, la dificultad de instalación y la falta de soporte activo para Windows 11 hacen que esta opción sea menos atractiva para un proyecto que busca facilidad de uso.

#### c) `pykinect`

*   **Descripción**: `pykinect` es un binding de Python para el *Kinect for Windows SDK* de Microsoft. Permite acceder a las funcionalidades del Kinect v1 de manera más sencilla desde Python, aprovechando los controladores y la API oficial (aunque descontinuada).
*   **Compatibilidad con Windows 11 y Python**: `pykinect` depende directamente del *Kinect for Windows SDK v1.8*. Si el SDK puede instalarse y los controladores pueden forzarse a funcionar en Windows 11 (como se mencionó en la sección de soporte), entonces `pykinect` debería ser funcional. Sin embargo, al ser un binding de un SDK descontinuado, no recibirá actualizaciones para abordar problemas específicos de Windows 11 o nuevas versiones de Python. La compatibilidad puede ser variable y depender de la configuración del sistema.
*   **Estado Actual**: Es una opción viable si el SDK v1.8 se puede instalar y configurar correctamente en Windows 11, pero su futuro está limitado por la descontinuación del SDK subyacente.

### 2.3. Drivers de Kinect para Windows 11

Como se mencionó, no existen drivers oficiales de Microsoft específicos para Kinect v1 en Windows 11. La solución principal es utilizar los drivers incluidos en el **Kinect for Windows SDK v1.8** y, si es necesario, instalarlos manualmente a través del Administrador de Dispositivos. Es fundamental que el usuario se asegure de que el Kinect esté conectado a un puerto USB 2.0 (para el Kinect v1) y que la alimentación externa esté correctamente conectada.

### 2.4. Frameworks para Reconocimiento de Gestos

*   **MediaPipe**: Es una librería de Google de código abierto para construir pipelines de procesamiento de datos de percepción. Ofrece soluciones pre-entrenadas para detección de manos, seguimiento de esqueletos (Pose), y reconocimiento facial. Aunque no es nativa para Kinect, se podría alimentar con el stream de video del Kinect y utilizar sus modelos para el reconocimiento de gestos. Esto requeriría un paso intermedio para obtener el stream de video del Kinect y pasarlo a MediaPipe. Es una opción muy potente y activa en desarrollo.