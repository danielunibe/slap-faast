# Documentación Técnica del Proyecto SpeedDocumentAI

Este documento detalla la arquitectura, el diseño y las consideraciones técnicas del proyecto SpeedDocumentAI. Está diseñado para ser una "documentación viva", actualizándose automáticamente con los cambios en el código y los recursos del proyecto.

## 1. Introducción

SpeedDocumentAI es una aplicación de procesamiento de documentos impulsada por IA, diseñada para gestionar y analizar grandes volúmenes de información de manera eficiente. Utiliza Next.js para el frontend, con una arquitectura de microservicios para el backend que integra tecnologías como Ray y Prefect para el procesamiento distribuido, y la API de Gemini para capacidades de inteligencia artificial.

## 2. Arquitectura del Sistema

La arquitectura de SpeedDocumentAI se basa en un enfoque modular y escalable, dividida en los siguientes componentes principales:

### 2.1. Frontend (Next.js)

El frontend se construye con Next.js, utilizando el App Router para la gestión de rutas y el renderizado de componentes. Se enfoca en una interfaz de usuario intuitiva y responsiva, con componentes reutilizables y estilos definidos con Tailwind CSS.

### 2.2. Backend (API Mock / Microservicios)

Inicialmente, el proyecto incluye APIs mock para simular el comportamiento del backend. En un entorno de producción, estos serían reemplazados por microservicios reales que manejarían la lógica de negocio, la integración con sistemas de IA y la gestión de datos. Los endpoints mock actuales incluyen:

- `/api/projects`: Gestión de proyectos y su estado.
- `/api/quotas`: Monitoreo del uso de cuotas de la API de Gemini.
- `/api/nodes`: Información sobre los nodos de procesamiento (Ray/Prefect).
- `/api/tasks`: Gestión de tareas en cola y en ejecución.

### 2.3. Procesamiento Distribuido (Ray/Prefect)

Para el procesamiento intensivo de documentos y tareas de IA, SpeedDocumentAI se integrará con plataformas de computación distribuida como Ray y Prefect. Esto permite la ejecución paralela de tareas, la orquestación de flujos de trabajo complejos y la escalabilidad horizontal.

### 2.4. Inteligencia Artificial (Gemini API)

La API de Gemini se utiliza para diversas funcionalidades de IA, incluyendo:

- Análisis de texto y extracción de información.
- Resumen y generación de contenido.
- Clasificación y etiquetado de documentos.

## 3. Estructura de Archivos y Carpetas

La estructura del proyecto sigue una convención clara para facilitar la navegación y el mantenimiento:

```
SpeedDocumentAI/
├── docs/                    # Documentación del proyecto
│   ├── architecture/        # Diagramas de arquitectura del sistema
│   ├── design/             # Especificaciones de diseño UI/UX
│   ├── setup/              # Guías de instalación y configuración
│   └── user-guides/        # Manuales de usuario final
├── src/                    # Código fuente
│   ├── app/                # Punto de entrada Next.js App Router
│   ├── components/         # Componentes React reutilizables
│   ├── pages/              # Páginas Next.js adicionales
│   │   └── api/            # Endpoints API REST mock
│   └── styles/             # Estilos CSS globales
├── public/                 # Recursos estáticos
│   └── assets/             # Imágenes, iconos y recursos
├── tests/                  # Pruebas
│   ├── unit/               # Pruebas unitarias
│   └── integration/        # Pruebas de integración
├── scripts/                # Scripts de configuración PowerShell
├── tools/                  # Utilidades y helpers
├── logs/                   # Archivos de logs
├── docker/                 # Configuración de contenedores
└── .github/workflows/      # Pipelines CI/CD
```

## 4. Configuración y Desarrollo

Para configurar el entorno de desarrollo, se utilizan scripts de PowerShell que automatizan la instalación de dependencias y la configuración inicial del proyecto. Los archivos clave para la configuración incluyen:

- `package.json`: Define las dependencias del proyecto y los scripts de ejecución.
- `tailwind.config.js`: Configuración de Tailwind CSS.
- `postcss.config.js`: Configuración de PostCSS.
- `tsconfig.json`: Configuración de TypeScript.
- `.gitignore`: Archivos y carpetas a ignorar por Git.

## 5. Pipelines CI/CD

El proyecto incluye una carpeta `.github/workflows/` para definir pipelines de Integración Continua y Despliegue Continuo (CI/CD). Estos pipelines automatizarán tareas como:

- **Linting**: Verificación de la calidad del código.
- **Testing**: Ejecución de pruebas unitarias y de integración.
- **Building**: Compilación del proyecto para producción.
- **Deployment**: Despliegue de la aplicación a entornos de staging o producción.

## 6. Consideraciones de Seguridad

Se implementarán las mejores prácticas de seguridad en todas las capas de la aplicación, incluyendo:

- Validación de entrada y sanitización de datos.
- Autenticación y autorización robustas.
- Protección contra vulnerabilidades comunes (OWASP Top 10).
- Gestión segura de secretos y credenciales.

## 7. Escalabilidad y Rendimiento

El diseño modular y el uso de tecnologías distribuidas como Ray y Prefect garantizan la escalabilidad del sistema para manejar grandes volúmenes de datos y usuarios. Se realizarán optimizaciones de rendimiento en el frontend y el backend para asegurar una experiencia de usuario fluida.

## 8. Mantenimiento y Monitoreo

Se establecerán sistemas de monitoreo para supervisar el rendimiento de la aplicación, el uso de recursos y el estado de las tareas de IA. Se implementarán logs detallados para facilitar la depuración y el mantenimiento. Los archivos de logs se almacenarán en la carpeta `logs/`.

