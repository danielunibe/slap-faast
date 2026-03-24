# ⚡ Slap!Faast Core

> **Next-Gen Context-Aware Interface System**  
> *Una interfaz de usuario futurista controlada por voz, gestos y contexto ambiental.*

![Status](https://img.shields.io/badge/Status-Operational-00AA88?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

## 📋 Descripción
Slap!Faast es un núcleo de sistema diseñado para transformar la interacción humano-computadora. Utilizando visión por computadora, reconocimiento de voz offline y lógica difusa, el sistema adapta su interfaz "Hard FUI" (Future User Interface) al contexto del usuario en tiempo real.

### ✨ Características Principales ("AAA" Core)
*   **👁️ Visión Activa**: Tracking corporal y facial en tiempo real (MediaPipe).
*   **🗣️ Voz Offline**: Comandos de voz sin latencia ni dependencia de internet (Vosk).
*   **🧠 Conciencia de Contexto**: Detecta si estás jugando, trabajando o viendo media y adapta la UI.
*   **🎨 Estética Hard FUI**: Interfaz visual de alto contraste y respuesta inmediata, desacoplada de la lógica.
*   **⚙️ Configuración Centralizada**: Gestión robusta de parámetros mediante `dataclasses`.

## 🚀 Inicio Rápido

### Requisitos Previo
*   Python 3.10+
*   Webcam o Sensor Kinect compatible
*   Windows 10/11

### Instalación
```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/slap-faast.git
cd slap-faast

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Ejecución
Simplemente ejecuta el script de arranque:
```powershell
start_system.bat
```

## 🛠️ Estructura del Proyecto
```
Slap!Faast/
├── src/                # Código Fuente Modular
│   ├── ai/             # Motores de Inteligencia (Voz, Contexto)
│   ├── core/           # Configuración y EventBus
│   ├── tracking/       # Computer Vision Pipeline
│   └── ui/             # Componentes PyQt6 (FUI Cards)
├── models/             # Modelos de IA (Vosk)
└── start_system.bat    # Launcher Automatizado
```

## 🤝 Contribución
Este proyecto sigue una arquitectura modular estricta.
1.  **Config**: Todo parámetro debe ir en `src/core/config.py`.
2.  **UI**: Todo componente visual debe heredar de `FUICard`.

---
*Desarrollado con pasión y precisión.*
