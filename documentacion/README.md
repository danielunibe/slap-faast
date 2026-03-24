# SpeedDocumentAI

Aplicación Next.js para procesamiento de documentos con IA, integración con Ray/Prefect y monitoreo en tiempo real.

## Estructura del Proyecto

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

## Primeros Pasos

1. Instalar dependencias: `npm install`
2. Ejecutar en desarrollo: `npm run dev`
3. Abrir [http://localhost:3000](http://localhost:3000)

## Scripts Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Construir para producción
- `npm run start` - Servidor de producción
- `npm run lint` - Linter de código
- `npm run format:css` - Formatear archivos CSS

## Tecnologías

- Next.js 14 con App Router
- TypeScript
- Tailwind CSS
- Ray/Prefect para procesamiento distribuido
- Gemini API para IA

