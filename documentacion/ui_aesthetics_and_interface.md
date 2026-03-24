# Estética e Interfaz de Usuario de SpeedDocumentAI

Este documento describe la estética general y el diseño de la interfaz de usuario (UI) de las principales ventanas y componentes de la aplicación SpeedDocumentAI. Se incluyen referencias visuales basadas en texto para ilustrar los conceptos.

## 1. Estética General y Paleta de Colores

La estética de SpeedDocumentAI se basa en un diseño limpio, moderno y funcional, con un enfoque en la claridad y la facilidad de uso. Se utiliza una paleta de colores que combina tonos neutros con acentos vibrantes para resaltar elementos interactivos y estados importantes.

**Paleta de Colores (Referencia Tailwind CSS):**

- **Fondo Principal (`bg-background`):** Blanco puro en modo claro, gris oscuro/negro en modo oscuro. Proporciona un lienzo limpio para el contenido.
- **Texto Principal (`text-foreground`):** Negro suave en modo claro, blanco brillante en modo oscuro. Asegura alta legibilidad.
- **Bordes y Separadores (`border-border`):** Gris claro sutil. Define secciones sin ser intrusivo.
- **Acentos y Elementos Interactivos (`bg-blue-600`, `text-blue-600`):** Azul vibrante. Utilizado para botones primarios, barras de progreso y texto de enlace, indicando interactividad y progreso.
- **Estados (Verde, Amarillo, Rojo):**
    - **Verde (`bg-green-500`):** Éxito, activo, completado.
    - **Amarillo (`bg-yellow-500`):** Advertencia, inactivo, pendiente.
    - **Rojo (`bg-red-500`):** Error, fallido.

**Tipografía:**

Se utiliza una fuente sans-serif moderna y legible (ej. Inter, configurada en `layout.tsx`) para todo el texto, con diferentes pesos y tamaños para jerarquía.

**Elementos de Diseño:**

- **Esquinas Redondeadas (`rounded-lg`):** Suaves y consistentes en todos los contenedores y elementos interactivos para una sensación amigable.
- **Sombras (`shadow-lg`):** Sutiles sombras para dar profundidad y separar los componentes del fondo, especialmente en el modo claro.

## 2. Diseño de la Interfaz de Usuario por Componente

### 2.1. Página Principal (`src/app/page.tsx`)

La página principal actúa como un dashboard, organizando los componentes clave en un diseño de cuadrícula responsivo. En pantallas grandes, se divide en dos columnas principales: una más ancha a la izquierda para el HUD y otra más estrecha a la derecha para el Cluster Strip. Debajo, una barra de pestañas ocupa todo el ancho, seguida de otra sección de dos columnas para el Mini-DAG y el Inspector Drawer.

**Estructura Visual:**

```
+-----------------------------------------------------------------------+
| HEADER (SpeedDocumentAI - borde inferior)                             |
+-----------------------------------------------------------------------+
|                                                                       |
|  +---------------------------------+  +-----------------------------+
|  |                                 |  |                             |
|  |  HUD (Panel de Control)         |  |  Cluster Strip              |
|  |  (Ancho: 2/3 en desktop)        |  |  (Ancho: 1/3 en desktop)    |
|  |                                 |  |                             |
|  +---------------------------------+  +-----------------------------+
|                                                                       |
|  +-----------------------------------------------------------------+
|  |                                                                 |
|  |  TabBar (Pestañas de Navegación)                                |
|  |  (Ancho completo)                                               |
|  |                                                                 |
|  +-----------------------------------------------------------------+
|                                                                       |
|  +---------------------------------+  +-----------------------------+
|  |                                 |  |                             |
|  |  Mini-DAG                       |  |  Inspector Drawer           |
|  |  (Ancho: 1/2 en desktop)        |  |  (Ancho: 1/2 en desktop)    |
|  |                                 |  |                             |
|  +---------------------------------+  +-----------------------------+
|                                                                       |
+-----------------------------------------------------------------------+
```

### 2.2. HUD (Head-Up Display) - Panel de Control (`src/components/HUD.tsx`)

El HUD es una tarjeta prominente que muestra un resumen de los proyectos activos. Cada proyecto se presenta como una sub-tarjeta con su nombre, progreso, fase, ETA y cuotas.

**Estructura Visual de un Proyecto en el HUD:**

```
+---------------------------------------------------+
| Panel de Control (Título)                         |
+---------------------------------------------------+
|  +---------------------------------------------+  |
|  | Nombre del Proyecto           ETA           |  |
|  |                                             |  |
|  | Progreso: [Barra de Progreso Azul]  XX%     |  |
|  |                                             |  |
|  | Fase: [Texto]                 Cuotas: X/Y   |  |
|  +---------------------------------------------+  |
|  | ... (Otros Proyectos)                       |  |
+---------------------------------------------------+
```

**Elementos Clave:**

- **Título:** 


Panel de Control (h2).
- **Tarjetas de Proyecto:** Cada proyecto es una tarjeta con borde, fondo blanco/gris oscuro, y sombra. Contiene:
    - **Nombre del Proyecto (h3):** Texto prominente.
    - **ETA (Estimated Time of Arrival):** Texto pequeño a la derecha del nombre.
    - **Barra de Progreso:** Una barra horizontal con un relleno azul que indica el porcentaje completado.
    - **Fase y Cuotas:** Texto descriptivo en la parte inferior.

### 2.3. Cluster Strip - Estado del Cluster (`src/components/ClusterStrip.tsx`)

El Cluster Strip es una tarjeta que muestra el estado de los nodos del cluster. Cada nodo se representa con un indicador de estado de color (verde, amarillo, rojo) y sus métricas clave (CPU, VRAM, Jobs).

**Estructura Visual de un Nodo en el Cluster Strip:**

```
+---------------------------------------------------+
| Estado del Cluster (Título)                       |
+---------------------------------------------------+
|  +---------------------------------------------+  |
|  | ● [ID Nodo]                   CPU: XX%      |  |
|  | (Color según estado)          VRAM: XXXXMB  |  |
|  |                               Jobs: X       |  |
|  +---------------------------------------------+  |
|  | ... (Otros Nodos)                           |  |
|  +---------------------------------------------+  |
|  | Resumen: Activos: X | Inactivos: Y | Error: Z |
+---------------------------------------------------+
```

**Elementos Clave:**

- **Título:** Estado del Cluster (h2).
- **Tarjetas de Nodo:** Cada nodo es una entrada con borde, mostrando:
    - **Indicador de Estado:** Un círculo de color (verde, amarillo, rojo) a la izquierda del ID del nodo.
    - **ID del Nodo:** Texto identificador.
    - **Métricas:** CPU, VRAM y Jobs listados a la derecha.
- **Resumen Inferior:** Un área separada por un borde superior que muestra el conteo total de nodos activos, inactivos y con error.

### 2.4. TabBar - Pestañas de Navegación (`src/components/TabBar.tsx`)

La TabBar es una barra de navegación horizontal con pestañas que permiten al usuario cambiar entre diferentes vistas (Proyectos, Tareas, Cola, Completados, Errores). La pestaña activa se resalta con un borde inferior azul y texto azul.

**Estructura Visual de la TabBar:**

```
+-----------------------------------------------------------------------+
|                                                                       |
|  [Proyectos (5)] [Tareas (12)] [Cola (8)] [Completados (23)] [Errores (2)]
|  ---------------------------------------------------------------------
|  (Borde inferior azul en la pestaña activa)                           |
|                                                                       |
|  +-----------------------------------------------------------------+
|  | Contenido de la pestaña activa                                  |
|  | (Ej. "Contenido de la pestaña Proyectos")                       |
|  +-----------------------------------------------------------------+
|                                                                       |
+-----------------------------------------------------------------------+
```

**Elementos Clave:**

- **Pestañas:** Botones con texto y un contador numérico entre paréntesis. El texto de la pestaña activa es azul y tiene un borde inferior azul.
- **Contenido de la Pestaña:** Un área debajo de las pestañas que muestra el contenido correspondiente a la pestaña seleccionada.

### 2.5. Inspector Drawer - Panel de Inspección (`src/components/InspectorDrawer.tsx`)

El Inspector Drawer es un panel que muestra detalles exhaustivos de un elemento seleccionado (proyecto, tarea, nodo). Se activa mediante un botón y presenta la información en un formato de lista de clave-valor, con opciones para exportar o editar.

**Estructura Visual del Inspector Drawer (cuando está abierto):**

```
+---------------------------------------------------+
| Inspector (Título)                                |
| [Botón: Inspeccionar Proyecto]                    |
+---------------------------------------------------+
|                                                   |
|  +---------------------------------------------+  |
|  | Nombre del Elemento Seleccionado  [X]       |  |
|  | (Título)                          (Cerrar)  |  |
|  +---------------------------------------------+  |
|  |                                             |  |
|  | Tipo: [Texto]                               |  |
|  | ID: [Texto]                                 |  |
|  |                                             |  |
|  | Detalles (Título)                           |  |
|  |   Clave 1: Valor 1                          |  |
|  |   Clave 2: Valor 2                          |  |
|  |   ... (Lista de detalles)                   |  |
|  |                                             |  |
|  +---------------------------------------------+  |
|  | [Botón: Exportar] [Botón: Editar]           |  |
|  +---------------------------------------------+  |
|                                                   |
+---------------------------------------------------+
```

**Elementos Clave:**

- **Título:** Inspector (h2).
- **Botón de Activación:** "Inspeccionar Proyecto" para abrir el panel con datos de ejemplo.
- **Panel Abierto:** Contiene:
    - **Nombre del Elemento y Botón Cerrar:** Título del elemento inspeccionado y un icono 'X' para cerrar el panel.
    - **Información General:** Tipo e ID del elemento.
    - **Sección de Detalles:** Una lista desplazable de pares clave-valor que muestran todas las propiedades del elemento.
    - **Botones de Acción:** "Exportar" y "Editar" en la parte inferior.

### 2.6. Mini-DAG - Flujo de Procesamiento (`src/components/MiniDAG.tsx`)

El Mini-DAG (Directed Acyclic Graph) visualiza el flujo de procesamiento de documentos como una serie de nodos conectados. Cada nodo representa un paso en el flujo y muestra su estado (completado, en ejecución, pendiente, fallido) con un icono y color distintivo.

**Estructura Visual del Mini-DAG:**

```
+---------------------------------------------------+
| Flujo de Procesamiento (DAG) (Título)             |
+---------------------------------------------------+
|                                                   |
|  +---------------------------------------------+  |
|  |                                             |  |
|  |  [Nodo 1] ----> [Nodo 2] ----> [Nodo 3]     |  |
|  |  (Icono/Color) (Icono/Color) (Icono/Color)  |  |
|  |                                             |  |
|  |  [Nodo 4] ----^                             |  |
|  |  (Icono/Color)                              |  |
|  |                                             |  |
|  +---------------------------------------------+  |
|                                                   |
|  Leyenda: ● Completado ● En ejecución ● Pendiente |
|  X/Y completados                                  |
+---------------------------------------------------+
```

**Elementos Clave:**

- **Título:** Flujo de Procesamiento (DAG) (h2).
- **Área de Visualización:** Un contenedor con fondo gris claro que alberga el SVG del DAG.
- **Nodos:** Rectángulos redondeados que representan cada paso. Contienen:
    - **Icono de Estado:** Un icono (check, spinner, cruz, etc.) y color de fondo que indican el estado (verde para completado, azul para en ejecución, gris para pendiente, rojo para fallido).
    - **Nombre del Nodo:** Texto descriptivo del paso.
- **Aristas:** Líneas con flechas que conectan los nodos, indicando la dirección del flujo.
- **Leyenda:** Una sección en la parte inferior que explica el significado de los colores de estado y muestra el conteo de nodos completados.

