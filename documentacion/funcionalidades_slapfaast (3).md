# Especificación de Funcionalidades y Personalización de Gestos para Slap!Faast

## Introducción

Esta sección detalla las funcionalidades clave de **Slap!Faast**, el programa diseñado para permitir a los usuarios controlar su sistema operativo Windows mediante gestos con sensores Kinect. El enfoque principal está en la capacidad de los usuarios para crear, entrenar y personalizar sus propios gestos, así como en la flexibilidad para mapear estos gestos a una amplia gama de acciones del sistema operativo. La interfaz de usuario jugará un papel crucial en la facilidad de uso y la experiencia de personalización.

## 1. Funcionalidades Principales del Programa

Slap!Faast ofrecerá las siguientes funcionalidades principales:

### 1.1. Detección y Gestión de Sensores Kinect

*   **Detección Automática**: Al iniciar, Slap!Faast detectará automáticamente el modelo de Kinect conectado (Kinect v1, Kinect v2, Azure Kinect DK).
*   **Indicador de Estado**: La interfaz de usuario mostrará claramente el estado de conexión del sensor (conectado, desconectado, error) y el modelo detectado.
*   **Manejo de Múltiples Sensores**: Aunque el programa se centrará en un solo sensor activo a la vez, la arquitectura permitirá la futura expansión para gestionar múltiples Kinects si fuera necesario.
*   **Diagnóstico Básico**: Proporcionará información básica de diagnóstico si el sensor no se conecta correctamente (ej. "Verifique la conexión USB 3.0", "Instale el SDK de Azure Kinect").

### 1.2. Seguimiento de Esqueletos en Tiempo Real

*   **Visualización del Esqueleto**: La GUI incluirá una ventana de visualización en tiempo real que mostrará el esqueleto rastreado por el Kinect. Esto es fundamental para el entrenamiento de gestos y para que el usuario entienda cómo el sensor lo está "viendo".
*   **Múltiples Usuarios**: Capacidad para rastrear múltiples usuarios, aunque el reconocimiento de gestos activo se centrará en un usuario principal configurable.
*   **Normalización de Joints**: Los datos de los joints de los diferentes modelos de Kinect se normalizarán a un conjunto común para asegurar la compatibilidad con el módulo de reconocimiento de gestos.

### 1.3. Modo Escucha y Activación/Desactivación

*   **Control del Modo Escucha**: El programa permitirá al usuario activar o desactivar el reconocimiento de gestos para evitar activaciones accidentales. Esto se podrá hacer mediante:
    *   **Gesto de Activación/Desactivación**: Un gesto predefinido y muy distintivo (ej. el "golpe de cachetada" propuesto por el usuario, o una postura de "manos en alto").
    *   **Atajo de Teclado Global**: Una combinación de teclas configurable que active/desactive el modo escucha.
    *   **Botón en la GUI**: Un botón claro en la interfaz principal del programa.
*   **Indicador Visual**: La GUI mostrará un indicador visual (ej. un icono, un cambio de color) que refleje el estado actual del modo escucha (activo/inactivo).

### 1.4. Reconocimiento de Gestos

*   **Gestos Predefinidos**: Slap!Faast incluirá un conjunto básico de gestos predefinidos (ej. "deslizar mano izquierda", "pellizcar", "mano en stop") con acciones comunes ya mapeadas.
*   **Reconocimiento de Gestos Personalizados**: Esta es la funcionalidad central. El sistema permitirá a los usuarios:
    *   **Grabar Nuevos Gestos**: El usuario podrá realizar un movimiento frente al Kinect, y el programa grabará la secuencia de datos del esqueleto asociada.
    *   **Etiquetar Gestos**: Asignar un nombre descriptivo a cada gesto grabado.
    *   **Entrenar Gestos**: Utilizar los datos grabados para entrenar el modelo de reconocimiento de gestos (posiblemente usando DTW o un modelo de ML). El sistema podría requerir múltiples repeticiones del gesto para un entrenamiento efectivo.
    *   **Probar Gestos**: Una funcionalidad para probar la precisión del reconocimiento de un gesto recién entrenado.
*   **Gestión de Gestos**: La GUI permitirá ver, editar, renombrar y eliminar gestos personalizados.

### 1.5. Mapeo de Gestos a Acciones del Sistema Operativo

*   **Asociación Flexible**: Los usuarios podrán asociar cualquier gesto reconocido (predefinido o personalizado) a una o varias acciones del sistema operativo.
*   **Gestión de Mapeos**: La GUI proporcionará una interfaz para ver, editar y eliminar los mapeos de gestos a acciones.

### 1.6. Gestión de Perfiles

*   **Perfiles de Usuario**: Permitirá crear y gestionar múltiples perfiles de usuario, cada uno con su propio conjunto de gestos personalizados y mapeos de acciones. Esto es útil para diferentes usuarios o para diferentes contextos de uso (ej. "trabajo", "entretenimiento").
*   **Carga/Guardado de Perfiles**: Funcionalidad para cargar y guardar perfiles de forma persistente.

## 2. Interfaz de Usuario para Entrenamiento y Asignación de Gestos

La interfaz de usuario (GUI) será el punto de interacción principal para la personalización de gestos. Se diseñará para ser intuitiva y visual.

### 2.1. Pantalla Principal / Dashboard

*   **Estado del Sensor**: Indicador claro del estado del Kinect (conectado/desconectado, modelo).
*   **Visualización del Esqueleto**: Una vista en tiempo real del esqueleto rastreado por el Kinect, posiblemente con una representación visual de los joints y las conexiones.
*   **Estado del Modo Escucha**: Botón e indicador visual para activar/desactivar el modo escucha.
*   **Notificaciones**: Área para mostrar notificaciones sobre gestos reconocidos y acciones ejecutadas.
*   **Acceso Rápido**: Botones o pestañas para acceder a las secciones de "Gestos", "Acciones" y "Configuración".

### 2.2. Sección de Gestión de Gestos

*   **Lista de Gestos**: Una tabla o lista que muestre todos los gestos disponibles (predefinidos y personalizados), con su nombre y una breve descripción.
*   **Botón "Grabar Nuevo Gesto"**: Al hacer clic, se iniciará un proceso guiado para grabar un nuevo gesto:
    *   **Instrucciones en Pantalla**: Mensajes claros que guíen al usuario sobre cómo realizar el gesto (ej. "Prepárese para realizar el gesto", "Realice el gesto ahora", "Gesto grabado").
    *   **Visualización de la Grabación**: Mientras el usuario realiza el gesto, se mostrará una representación visual de la secuencia de movimiento grabada.
    *   **Repeticiones**: Posibilidad de grabar múltiples repeticiones del mismo gesto para mejorar la precisión del entrenamiento.
    *   **Asignación de Nombre**: Un campo para que el usuario asigne un nombre único al gesto.
*   **Edición de Gesto**: Opción para renombrar un gesto o volver a entrenarlo.
*   **Eliminación de Gesto**: Opción para eliminar un gesto personalizado.

### 2.3. Sección de Mapeo de Acciones

*   **Lista de Mapeos**: Una tabla o lista que muestre los mapeos existentes (Gesto -> Acción).
*   **Botón "Añadir Nuevo Mapeo"**: Al hacer clic, se abrirá un asistente:
    *   **Selección de Gesto**: Un desplegable o buscador para seleccionar un gesto existente.
    *   **Selección de Acción**: Un desplegable o interfaz para seleccionar el tipo de acción del sistema operativo (ver sección 3).
    *   **Configuración de Acción**: Campos adicionales para configurar los parámetros de la acción (ej. combinación de teclas, ruta del programa, URL).
*   **Edición de Mapeo**: Opción para modificar el gesto o la acción asociada a un mapeo existente.
*   **Eliminación de Mapeo**: Opción para eliminar un mapeo.

### 2.4. Sección de Configuración

*   **Configuración del Sensor**: Opciones para seleccionar el sensor principal (si hay varios conectados), ajustar la sensibilidad (si es aplicable).
*   **Configuración del Modo Escucha**: Personalizar el gesto de activación/desactivación o el atajo de teclado.
*   **Gestión de Perfiles**: Cargar, guardar, crear y eliminar perfiles de usuario.
*   **Opciones Generales**: Idioma, tema de la interfaz, etc.

## 3. Tipos de Acciones del Sistema Operativo Mapeables

Slap!Faast permitirá mapear gestos a una variedad de acciones comunes del sistema operativo Windows, aprovechando las librerías `pyautogui`, `keyboard` y `win32gui`.

### 3.1. Emulación de Teclado

*   **Pulsación de Tecla Simple**: Cualquier tecla individual (ej. `Enter`, `Esc`, `Space`).
*   **Combinaciones de Teclas**: Atajos de teclado (ej. `Ctrl + C`, `Ctrl + V`, `Alt + Tab`, `Win + D`, `Win + Ctrl + Flecha Izquierda/Derecha`).
*   **Escritura de Texto**: Simular la escritura de una cadena de texto predefinida.

### 3.2. Emulación de Ratón

*   **Movimiento del Cursor**: Mover el cursor a una posición absoluta o relativa en la pantalla.
*   **Clics del Ratón**: Clic izquierdo, clic derecho, doble clic.
*   **Arrastrar y Soltar**: Simular arrastrar un elemento y soltarlo.
*   **Desplazamiento (Scroll)**: Desplazamiento vertical u horizontal.

### 3.3. Control de Ventanas

*   **Activar Ventana**: Traer una ventana específica al frente (por título o nombre de proceso).
*   **Minimizar/Maximizar/Restaurar Ventana**: Controlar el estado de una ventana.
*   **Cerrar Ventana**: Cerrar una aplicación o ventana.
*   **Mover/Redimensionar Ventana**: Cambiar la posición y el tamaño de una ventana.

### 3.4. Ejecución de Programas y Scripts

*   **Abrir Aplicación**: Lanzar un programa específico (ej. navegador web, reproductor de música) por su ruta de acceso.
*   **Ejecutar Comando**: Ejecutar un comando de línea de comandos o un script (ej. `.bat`, `.ps1`, `.py`).
*   **Abrir URL**: Abrir una URL específica en el navegador predeterminado.

### 3.5. Control Multimedia

*   **Reproducir/Pausar**: Controlar la reproducción de medios.
*   **Siguiente/Anterior Pista**: Navegar entre pistas de audio/video.
*   **Subir/Bajar Volumen**: Ajustar el volumen del sistema.
*   **Silenciar/Activar Sonido**: Alternar el estado del sonido.

### 3.6. Acciones del Sistema

*   **Bloquear Pantalla**: Bloquear la sesión de Windows (`Win + L`).
*   **Apagar/Reiniciar/Suspender**: Opciones para controlar el estado de energía del sistema (con advertencia al usuario).
*   **Captura de Pantalla**: Realizar una captura de pantalla.

La flexibilidad en la definición de estas acciones permitirá a los usuarios adaptar Slap!Faast a una amplia variedad de flujos de trabajo y preferencias personales.

