# Diseño de Arquitectura del Software Multi-Kinect: Slap!Faast

## Introducción

El objetivo de **Slap!Faast** es proporcionar una solución integral para el control de gestos en Windows 11, utilizando una variedad de sensores Kinect, incluyendo el Kinect v1 (modelo 1414), Kinect v2 y Azure Kinect DK. Dada la diversidad de hardware y SDKs asociados, la arquitectura del software debe ser modular, extensible y capaz de abstraer las complejidades específicas de cada sensor, presentando una interfaz unificada al módulo de reconocimiento de gestos y al resto de la aplicación. El diseño propuesto busca maximizar la compatibilidad, el rendimiento y la facilidad de uso, al tiempo que permite la personalización de gestos por parte del usuario.

## Principios de Diseño

Para lograr los objetivos de Slap!Faast, la arquitectura se basará en los siguientes principios:

*   **Modularidad**: Dividir el sistema en componentes independientes y cohesivos, cada uno con una responsabilidad clara. Esto facilita el desarrollo, la prueba y el mantenimiento.
*   **Abstracción**: Ocultar los detalles de implementación específicos de cada modelo de Kinect detrás de interfaces comunes, permitiendo que los módulos de nivel superior interactúen con los datos del sensor de manera uniforme.
*   **Extensibilidad**: Diseñar el sistema de manera que sea fácil añadir soporte para nuevos modelos de Kinect o algoritmos de reconocimiento de gestos en el futuro.
*   **Rendimiento**: Optimizar las rutas de datos y el procesamiento para garantizar una baja latencia en el reconocimiento de gestos y la ejecución de acciones, especialmente considerando las limitaciones de hardware de los modelos más antiguos de Kinect.
*   **Robustez**: Implementar mecanismos de manejo de errores y recuperación para asegurar la estabilidad del sistema frente a desconexiones del sensor o fallos en el reconocimiento.
*   **Configurabilidad**: Permitir al usuario configurar fácilmente los gestos, las acciones asociadas y los parámetros del sistema a través de una interfaz gráfica intuitiva.

## Componentes Principales de la Arquitectura

La arquitectura de Slap!Faast se puede dividir en los siguientes componentes principales:

1.  **Módulo de Adquisición de Datos del Sensor (Sensor Data Acquisition Module)**
2.  **Módulo de Procesamiento de Esqueletos (Skeleton Processing Module)**
3.  **Módulo de Reconocimiento de Gestos (Gesture Recognition Module)**
4.  **Módulo de Ejecución de Acciones (Action Execution Module)**
5.  **Módulo de Interfaz de Usuario (User Interface Module)**
6.  **Módulo de Configuración y Persistencia (Configuration & Persistence Module)**
7.  **Módulo de Control de Aplicación (Application Control Module)**

Cada uno de estos módulos se comunicará a través de interfaces bien definidas, utilizando mecanismos de comunicación entre procesos o hilos según sea necesario para garantizar la operación en segundo plano y la capacidad de respuesta de la interfaz de usuario.

### 1. Módulo de Adquisición de Datos del Sensor

Este módulo es responsable de la interacción directa con los diferentes modelos de Kinect para capturar los datos brutos. Será la capa más cercana al hardware y encapsulará las particularidades de cada SDK de Kinect.

*   **Responsabilidades**:
    *   Inicializar y configurar el sensor Kinect conectado (v1, v2 o Azure Kinect).
    *   Capturar flujos de datos de color (RGB), profundidad e infrarrojos.
    *   Manejar la conexión y desconexión del sensor.
    *   Proporcionar una interfaz unificada para acceder a los datos del sensor, independientemente del modelo de Kinect.
*   **Implementación (Python)**:
    *   **Kinect v1**: Utilizará `pykinect` (requiere Kinect for Windows SDK v1.8) o una implementación basada en `libfreenect` si se supera la complejidad de instalación.
    *   **Kinect v2**: Utilizará `PyKinect2` (requiere Kinect for Windows SDK 2.0).
    *   **Azure Kinect DK**: Utilizará `pyk4a` o `pyKinectAzure` (requiere Azure-Kinect-Sensor-SDK).
*   **Salida**: Proporcionará streams de datos (frames) de color, profundidad e infrarrojos a los módulos subsiguientes. Estos datos se normalizarán a un formato común (por ejemplo, arrays de NumPy) para facilitar el procesamiento posterior.

### 2. Módulo de Procesamiento de Esqueletos

Este módulo se encargará de tomar los datos brutos del sensor y extraer la información del esqueleto humano, que es fundamental para el reconocimiento de gestos.

*   **Responsabilidades**:
    *   Procesar los datos de profundidad (y posiblemente color) para detectar y rastrear uno o más esqueletos humanos en tiempo real.
    *   Normalizar los datos de los joints del esqueleto a un formato consistente, independientemente del número de joints que proporcione cada modelo de Kinect (20 para v1, 25 para v2, 32 para Azure Kinect). Esto podría implicar la interpolación o la selección de un subconjunto común de joints.
    *   Manejar la identificación de usuarios y el seguimiento de esqueletos a lo largo del tiempo.
*   **Implementación (Python)**:
    *   **Kinect v1**: Si se usa `pykinect`, el SDK v1.8 ya proporciona el seguimiento de esqueletos. Si se usa `libfreenect`, se podría integrar con `OpenNI2/NiTE2` (si se logra instalar) o utilizar un algoritmo de seguimiento de esqueletos basado en visión por computadora (por ejemplo, MediaPipe Pose) que procese el stream de profundidad/color.
    *   **Kinect v2**: El `Kinect for Windows SDK 2.0` (a través de `PyKinect2`) proporciona un seguimiento de esqueletos robusto.
    *   **Azure Kinect DK**: El `Azure-Kinect-Body-Tracking-SDK` (a través de `pyk4a` o `pyKinectAzure`) es la solución más avanzada y precisa para el seguimiento corporal.
*   **Salida**: Proporcionará una estructura de datos que contenga las coordenadas 3D (y posiblemente orientación) de los joints del esqueleto para cada usuario detectado, junto con un identificador de usuario y un timestamp.

### 3. Módulo de Reconocimiento de Gestos

Este es el corazón de Slap!Faast, responsable de interpretar las secuencias de movimientos del esqueleto como gestos significativos. Se basará en el enfoque híbrido de Machine Learning y reglas simples.

*   **Responsabilidades**:
    *   Recibir los datos de los esqueletos del Módulo de Procesamiento de Esqueletos.
    *   Implementar algoritmos de reconocimiento de gestos dinámicos (DTW, LSTMs/GRUs o clasificadores basados en características) para identificar gestos predefinidos y personalizados.
    *   Gestionar el "modo escucha" (activación/desactivación) para evitar falsos positivos.
    *   Proporcionar una interfaz para el entrenamiento de nuevos gestos personalizados por parte del usuario.
*   **Implementación (Python)**:
    *   **Algoritmos**: Implementación de DTW (por ejemplo, con `fastdtw` o `scipy.signal.correlate`) o modelos de Machine Learning (usando `TensorFlow`, `PyTorch` o `scikit-learn` para clasificadores). La integración con `MediaPipe` para el reconocimiento de poses/gestos podría ser una opción si se alimenta con el stream de video.
    *   **Lógica de Modo Escucha**: Lógica condicional para activar/desactivar el procesamiento de gestos basada en un gesto específico o una entrada externa.
*   **Salida**: Cuando se detecta un gesto, emitirá un evento o un mensaje que contenga el identificador del gesto reconocido y, opcionalmente, parámetros asociados (por ejemplo, dirección del deslizamiento, magnitud del zoom).

### 4. Módulo de Ejecución de Acciones

Este módulo es el encargado de traducir los gestos reconocidos en acciones concretas del sistema operativo.

*   **Responsabilidades**:
    *   Recibir eventos de gestos reconocidos del Módulo de Reconocimiento de Gestos.
    *   Mapear el gesto reconocido a una acción predefinida o personalizada por el usuario.
    *   Ejecutar la acción correspondiente en el sistema operativo Windows.
*   **Implementación (Python)**:
    *   **Emulación de Teclado/Ratón**: Utilizar `pyautogui` para simular pulsaciones de teclas (atajos de teclado, escritura de texto) y movimientos/clics del ratón.
    *   **Control de Ventanas**: Utilizar `win32gui` (parte de `pywin32`) para interactuar con ventanas (activar, mover, redimensionar, cerrar, etc.).
    *   **Ejecución de Comandos/Programas**: Utilizar `subprocess` para ejecutar programas externos o scripts.
*   **Salida**: Ejecutará la acción en el sistema operativo y, opcionalmente, proporcionará retroalimentación al Módulo de Interfaz de Usuario sobre la acción realizada.

### 5. Módulo de Interfaz de Usuario (GUI)

Este módulo proporcionará la interfaz gráfica para que el usuario interactúe con Slap!Faast, configure sus gestos y acciones, y reciba retroalimentación visual.

*   **Responsabilidades**:
    *   Mostrar el estado actual del sensor Kinect (conectado/desconectado, modelo).
    *   Visualizar el esqueleto rastreado en tiempo real (opcional, pero muy útil para el entrenamiento).
    *   Proporcionar una interfaz para definir y entrenar nuevos gestos (grabación de movimientos, etiquetado).
    *   Permitir al usuario asociar gestos con acciones del sistema operativo (atajos de teclado, comandos, control de ventanas).
    *   Mostrar el estado del "modo escucha" y permitir su activación/desactivación.
    *   Proporcionar retroalimentación visual cuando un gesto es reconocido y una acción es ejecutada.
    *   Gestionar perfiles de usuario y configuraciones.
*   **Implementación (Python)**:
    *   **Framework GUI**: `PyQt` (recomendado por su robustez, flexibilidad y capacidad para crear interfaces modernas) o `Tkinter` (más simple, pero menos potente visualmente). `Electron` podría ser una opción para una GUI basada en web, pero añadiría complejidad al empaquetado y distribución.
    *   **Visualización**: Integración con librerías de visualización (por ejemplo, `matplotlib` o `OpenCV` para dibujar esqueletos sobre el stream de video) si se implementa la visualización en tiempo real.

### 6. Módulo de Configuración y Persistencia

Este módulo se encargará de almacenar y recuperar la configuración del usuario, incluyendo los gestos personalizados y sus mapeos a acciones.

*   **Responsabilidades**:
    *   Guardar la configuración de gestos y acciones en un formato persistente (por ejemplo, JSON, YAML, base de datos SQLite).
    *   Cargar la configuración al inicio de la aplicación.
    *   Gestionar perfiles de usuario (si se implementa).
*   **Implementación (Python)**:
    *   **Formato de Almacenamiento**: Archivos JSON o YAML para configuraciones simples. SQLite para una base de datos más estructurada si la complejidad de los gestos y perfiles aumenta.
    *   **Serialización/Deserialización**: Utilizar librerías estándar de Python para manejar la lectura y escritura de los datos.

### 7. Módulo de Control de Aplicación

Este módulo actuará como el orquestador central, gestionando el ciclo de vida de la aplicación, la comunicación entre los módulos y el manejo de eventos.

*   **Responsabilidades**:
    *   Inicializar todos los módulos al inicio de la aplicación.
    *   Gestionar el flujo de datos entre los módulos.
    *   Manejar eventos y excepciones globales.
    *   Controlar el estado general de la aplicación (ej. modo escucha activo/inactivo).
*   **Implementación (Python)**:
    *   Podría ser la clase principal de la aplicación, utilizando un patrón de diseño como el **Patrón Observador** para la comunicación entre módulos (donde los módulos emiten eventos y otros módulos se suscriben a ellos).

## Diagrama de Arquitectura (Conceptual)

```mermaid
graph TD
    A[Módulo de Adquisición de Datos del Sensor] --> B{Interfaz Unificada de Datos del Sensor}
    B --> C[Módulo de Procesamiento de Esqueletos]
    C --> D[Módulo de Reconocimiento de Gestos]
    D --> E[Módulo de Ejecución de Acciones]
    D -- Eventos de Gesto --> F[Módulo de Interfaz de Usuario]
    E -- Retroalimentación --> F
    F -- Configuración de Gesto --> G[Módulo de Configuración y Persistencia]
    G -- Cargar/Guardar --> H[Almacenamiento Persistente]
    F -- Control de Modo Escucha --> D
    SubGraph Slap!Faast Application
        A
        C
        D
        E
        F
        G
    End
    H
    Kinect1(Kinect v1) --> A
    Kinect2(Kinect v2) --> A
    AzureKinect(Azure Kinect DK) --> A
```

## Consideraciones Adicionales

*   **Manejo de Errores**: Cada módulo debe implementar un manejo robusto de errores, registrando fallos y, cuando sea posible, intentando recuperarse o notificar al usuario.
*   **Logging**: Un sistema de logging centralizado será esencial para depurar problemas y monitorear el comportamiento de la aplicación.
*   **Rendimiento y Optimización**: Dada la naturaleza en tiempo real del reconocimiento de gestos, se requerirá una cuidadosa optimización del código, especialmente en los módulos de procesamiento de datos y reconocimiento de gestos. El uso de librerías optimizadas (como NumPy para operaciones matriciales) y la delegación de tareas intensivas a la GPU (para Azure Kinect) serán clave.
*   **Instalador y Dependencias**: El proceso de instalación de Slap!Faast deberá ser lo más sencillo posible, guiando al usuario a través de la instalación de los SDKs de Kinect necesarios y las dependencias de Python. Se podría considerar el uso de herramientas de empaquetado como PyInstaller para crear un ejecutable independiente.

Esta arquitectura proporciona una base sólida para el desarrollo de Slap!Faast, permitiendo la integración de múltiples modelos de Kinect y la implementación de un sistema de reconocimiento de gestos personalizable y robusto.



### Definición de la Interacción entre los Componentes

La comunicación y el flujo de datos entre los módulos de Slap!Faast son esenciales para su correcto funcionamiento. Se utilizarán mecanismos de comunicación asíncronos para garantizar que la aplicación sea responsiva y que el procesamiento de datos del Kinect no bloquee la interfaz de usuario.

#### Flujo de Datos Principal:

1.  **Sensor a Procesamiento de Esqueletos**: El **Módulo de Adquisición de Datos del Sensor** capturará continuamente los frames de color, profundidad e infrarrojos del Kinect. Estos frames serán pasados al **Módulo de Procesamiento de Esqueletos**. La comunicación será un flujo constante de datos, posiblemente a través de una cola de mensajes o un buffer compartido para manejar la tasa de frames.
2.  **Procesamiento de Esqueletos a Reconocimiento de Gestos**: Una vez que el **Módulo de Procesamiento de Esqueletos** haya extraído los datos de los joints del esqueleto, estos datos (normalizados) se enviarán al **Módulo de Reconocimiento de Gestos**. Este flujo también será continuo, proporcionando las poses actuales del usuario.
3.  **Reconocimiento de Gestos a Ejecución de Acciones**: Cuando el **Módulo de Reconocimiento de Gestos** detecte un gesto válido (y el sistema esté en "modo escucha"), emitirá un evento o un mensaje que contendrá el identificador del gesto reconocido y cualquier parámetro relevante. Este evento será recibido por el **Módulo de Ejecución de Acciones**, que se encargará de realizar la acción correspondiente en el sistema operativo.
4.  **Retroalimentación a la Interfaz de Usuario**: Todos los módulos pueden enviar mensajes o eventos al **Módulo de Interfaz de Usuario** para actualizar el estado de la aplicación, mostrar visualizaciones en tiempo real (como el esqueleto rastreado), o notificar al usuario sobre gestos reconocidos y acciones ejecutadas.

#### Mecanismos de Comunicación:

*   **Colas de Mensajes (Queues)**: Para el flujo de datos entre módulos que operan en hilos o procesos separados (ej. Adquisición de Datos -> Procesamiento de Esqueletos -> Reconocimiento de Gestos). Esto permite desacoplar los módulos y manejar diferentes tasas de procesamiento.
*   **Eventos y Callbacks**: Para notificaciones asíncronas, como la detección de un gesto o un cambio en el estado del sensor. El Módulo de Reconocimiento de Gestos podría emitir un evento `GestureRecognized`, al cual el Módulo de Ejecución de Acciones y el Módulo de Interfaz de Usuario estarían suscritos.
*   **Objetos Compartidos/Bloqueo (Locks)**: Para acceder a datos compartidos de forma segura entre hilos, como la configuración actual del sistema o el estado del "modo escucha".

#### Patrones de Diseño Aplicados:

*   **Productor-Consumidor**: El Módulo de Adquisición de Datos es el productor de frames, y el Módulo de Procesamiento de Esqueletos es el consumidor. De manera similar, el Módulo de Procesamiento de Esqueletos es el productor de datos de esqueleto, y el Módulo de Reconocimiento de Gestos es el consumidor.
*   **Observador (Observer Pattern)**: El Módulo de Reconocimiento de Gestos (sujeto) notifica a los observadores (Módulo de Ejecución de Acciones, Módulo de Interfaz de Usuario) cuando se detecta un gesto. Esto permite añadir o quitar observadores sin modificar el sujeto.
*   **Fachada (Facade Pattern)**: El Módulo de Control de Aplicación actuará como una fachada, proporcionando una interfaz simplificada para interactuar con los subsistemas complejos de la aplicación.

### Diseño de una Capa de Abstracción para Múltiples Modelos de Kinect

La clave para soportar Kinect v1, v2 y Azure Kinect en una sola aplicación es una robusta capa de abstracción. Esta capa ocultará las diferencias en los SDKs y las APIs de cada sensor, presentando una interfaz unificada al resto de la aplicación.

#### Interfaz `IKinectSensor` (Conceptual)

Se definirá una interfaz o clase base abstracta `IKinectSensor` que especificará los métodos comunes que cualquier implementación de sensor Kinect debe proporcionar. Las clases específicas para cada modelo de Kinect (`KinectV1Sensor`, `KinectV2Sensor`, `AzureKinectSensor`) implementarán esta interfaz.

**Métodos Clave de `IKinectSensor`:**

*   `initialize()`: Inicializa el sensor y sus dependencias (SDKs, drivers).
*   `start_stream()`: Comienza la captura de datos (color, profundidad, infrarrojos, esqueleto).
*   `stop_stream()`: Detiene la captura de datos.
*   `get_frame()`: Recupera el último frame de datos (que contendrá imágenes y datos de esqueleto normalizados).
*   `is_connected()`: Devuelve el estado de conexión del sensor.
*   `get_sensor_info()`: Devuelve información específica del sensor (modelo, número de serie, capacidades).

#### Normalización de Datos de Esqueleto

Una de las mayores diferencias entre los modelos de Kinect es el número y la denominación de los joints del esqueleto. Para el **Módulo de Procesamiento de Esqueletos** y el **Módulo de Reconocimiento de Gestos**, es crucial trabajar con un formato de datos de esqueleto consistente.

*   **Conjunto de Joints Común**: Se definirá un conjunto estándar de joints que sea un subconjunto de los joints disponibles en todos los modelos de Kinect (por ejemplo, los 20 joints del Kinect v1, ya que son los más limitados). Las implementaciones de `IKinectSensor` serán responsables de mapear sus joints nativos a este conjunto común.
*   **Estructura de Datos del Esqueleto Normalizada**: Se creará una estructura de datos (`SkeletonData`) que contendrá una lista de objetos `JointData`, donde cada `JointData` tendrá un `joint_id` (del conjunto común), `position` (x, y, z), y `orientation` (si está disponible y es relevante).
*   **Transformaciones**: Si es necesario, se aplicarán transformaciones para normalizar las coordenadas espaciales (por ejemplo, escalar a un rango común) para que los algoritmos de reconocimiento de gestos no dependan de la escala del espacio de trabajo de cada sensor.

#### Fábrica de Sensores (Sensor Factory)

Para simplificar la inicialización, se utilizará un patrón de diseño de Fábrica Abstracta o Fábrica Simple. Un `KinectSensorFactory` será responsable de detectar el modelo de Kinect conectado y devolver la implementación correcta de `IKinectSensor`.

**Flujo de Detección e Inicialización:**

1.  Al inicio de Slap!Faast, el `KinectSensorFactory` intentará inicializar cada tipo de sensor (Azure Kinect, luego Kinect v2, luego Kinect v1) en un orden de preferencia (generalmente del más nuevo al más antiguo, o del más capaz al menos capaz).
2.  Una vez que un sensor se inicializa con éxito, el `KinectSensorFactory` devolverá la instancia correspondiente de `IKinectSensor`.
3.  Si no se detecta ningún Kinect, se notificará al usuario y la aplicación podría funcionar en un modo de demostración o simulación.

Esta capa de abstracción permitirá que el resto de la aplicación (Módulo de Procesamiento de Esqueletos, Módulo de Reconocimiento de Gestos, etc.) trabaje con una interfaz consistente, sin necesidad de conocer los detalles específicos de cada modelo de Kinect. Esto facilitará enormemente la extensibilidad y el mantenimiento del código.

