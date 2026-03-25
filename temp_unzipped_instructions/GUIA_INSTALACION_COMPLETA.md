# 🚀 GUÍA DE INSTALACIÓN COMPLETA - SLAP!FAAST v2.0 TONY STARK EDITION

**Versión:** 2.0.0  
**Fecha:** Diciembre 2024  
**Tiempo estimado:** 30-60 minutos  
**Dificultad:** Intermedio  

---

## 📋 **TABLA DE CONTENIDOS**

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Instalación Automática](#instalación-automática)
4. [Instalación Manual](#instalación-manual)
5. [Configuración de Hardware](#configuración-de-hardware)
6. [Instalación de IA Local](#instalación-de-ia-local)
7. [Configuración Inicial](#configuración-inicial)
8. [Verificación y Testing](#verificación-y-testing)
9. [Primer Uso](#primer-uso)
10. [Solución de Problemas](#solución-de-problemas)

---

## 🖥️ **REQUISITOS DEL SISTEMA**

### **💻 Sistema Operativo**
- ✅ **Windows 10** (versión 1903 o superior) - **RECOMENDADO**
- ✅ **Windows 11** (cualquier versión) - **ÓPTIMO**
- ⚠️ Linux Ubuntu 20.04+ (experimental)

### **🔧 Hardware Mínimo**
- **CPU:** Intel i5-6000 series / AMD Ryzen 5 2600 o superior
- **RAM:** 8 GB mínimo, **16 GB recomendado**
- **Almacenamiento:** 10 GB libres mínimo, **20 GB recomendado**
- **GPU:** Cualquier GPU moderna (opcional pero recomendada)
- **USB:** Puertos USB 2.0+ disponibles

### **📷 Hardware de Captura (Elige uno)**

#### **🎮 Opción 1: Microsoft Kinect v1 (RECOMENDADO)**
- **Modelo:** Xbox 360 Kinect (modelo 1414)
- **Incluye:** Sensor + cable USB + adaptador de corriente
- **Ventajas:** Mejor precisión, detección de profundidad, control LED
- **Precio:** $50-100 USD usado

#### **📹 Opción 2: Webcam HD**
- **Resolución:** 720p mínimo, **1080p recomendado**
- **FPS:** 30 FPS mínimo
- **Marcas compatibles:** Logitech, Microsoft, cualquier webcam USB
- **Ventajas:** Más económico, fácil de conseguir

### **🐍 Software Base**
- **Python:** 3.8, 3.9, 3.10, o 3.11 (3.10 recomendado)
- **Git:** Para clonar el repositorio
- **Visual C++ Redistributable** (Windows)

---

## 🛠️ **PREPARACIÓN DEL ENTORNO**

### **Paso 1: Verificar Python**

1. **Abrir Command Prompt** (cmd) como administrador
2. **Verificar Python:**
   ```cmd
   python --version
   ```
   
   **Resultado esperado:** `Python 3.10.x` (o similar)

3. **Si Python no está instalado:**
   - Descargar desde: https://www.python.org/downloads/
   - ✅ **IMPORTANTE:** Marcar "Add Python to PATH"
   - Instalar con opciones por defecto

### **Paso 2: Instalar Git**

1. **Descargar Git:** https://git-scm.com/download/windows
2. **Instalar** con opciones por defecto
3. **Verificar instalación:**
   ```cmd
   git --version
   ```

### **Paso 3: Instalar Visual C++ Redistributable**

1. **Descargar:** https://aka.ms/vs/17/release/vc_redist.x64.exe
2. **Ejecutar** e instalar
3. **Reiniciar** si es necesario

### **Paso 4: Descargar Slap!Faast**

1. **Crear carpeta de trabajo:**
   ```cmd
   mkdir C:\SlapFaast
   cd C:\SlapFaast
   ```

2. **Clonar repositorio:**
   ```cmd
   git clone https://github.com/tu-usuario/slap-faast.git
   cd slap-faast
   ```

   **O descargar ZIP y extraer en C:\SlapFaast\**

---

## 🤖 **INSTALACIÓN AUTOMÁTICA (RECOMENDADO)**

### **Opción A: Instalador Automático**

1. **Abrir Command Prompt** como administrador
2. **Navegar al directorio:**
   ```cmd
   cd C:\SlapFaast\slap-faast
   ```

3. **Ejecutar instalador:**
   ```cmd
   python install_complete.py
   ```

4. **Seguir instrucciones** en pantalla
5. **Esperar** (15-30 minutos dependiendo de conexión)

### **¿Qué hace el instalador automático?**
- ✅ Crea entorno virtual Python
- ✅ Instala todas las dependencias
- ✅ Configura directorios
- ✅ Descarga modelos IA (opcional)
- ✅ Verifica hardware
- ✅ Ejecuta tests básicos
- ✅ Crea accesos directos

### **Si el instalador automático funciona:**
**¡Saltar a [Instalación de IA Local](#instalación-de-ia-local)!**

---

## 🔧 **INSTALACIÓN MANUAL**

### **Solo si el instalador automático falla**

#### **Paso 1: Crear Entorno Virtual**

```cmd
cd C:\SlapFaast\slap-faast
python -m venv venv
venv\Scripts\activate
```

#### **Paso 2: Actualizar pip**

```cmd
python -m pip install --upgrade pip setuptools wheel
```

#### **Paso 3: Instalar Dependencias Principales**

```cmd
pip install PyQt6==6.6.1
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.8
pip install numpy==1.24.3
pip install scipy==1.11.4
pip install requests==2.31.0
pip install aiohttp==3.9.1
pip install pygame==2.5.2
pip install pyttsx3==2.90
pip install SpeechRecognition==3.10.0
pip install pillow==10.1.0
pip install pyautogui==0.9.54
pip install psutil==5.9.6
pip install colorama==0.4.6
pip install tqdm==4.66.1
```

#### **Paso 4: Instalar Dependencias IA (Opcional)**

```cmd
pip install openai-whisper
pip install torch torchvision torchaudio
pip install transformers
pip install ultralytics
pip install easyocr
```

**⚠️ Nota:** Estas dependencias son grandes (2-5 GB). Omitir si hay problemas de espacio.

#### **Paso 5: Crear Directorios**

```cmd
mkdir logs profiles temp cache exports backups
```

#### **Paso 6: Verificar Instalación**

```cmd
python test_dependencies.py
```

---

## 📷 **CONFIGURACIÓN DE HARDWARE**

### **🎮 Configuración Kinect v1**

#### **Paso 1: Instalar SDK Kinect**

1. **Descargar Kinect SDK v1.8:**
   - URL: https://www.microsoft.com/en-us/download/details.aspx?id=40278
   - Archivo: `KinectSDK-v1.8-Setup.exe`

2. **Instalar SDK:**
   - Ejecutar como administrador
   - Seguir instalación por defecto
   - **Reiniciar** cuando termine

#### **Paso 2: Instalar Kinect Runtime**

1. **Descargar Kinect Runtime:**
   - Incluido en SDK v1.8
   - O descargar por separado si es necesario

2. **Verificar instalación:**
   - Abrir "Device Manager"
   - Buscar "Kinect for Windows" en "Sound, video and game controllers"

#### **Paso 3: Conectar Kinect**

1. **Conectar adaptador de corriente** al Kinect
2. **Conectar cable USB** al PC
3. **Esperar** a que Windows instale drivers
4. **Verificar LED:** Debe parpadear y luego ponerse verde

#### **Paso 4: Probar Kinect**

```cmd
cd C:\SlapFaast\slap-faast
python hardware_tester.py
```

**Seleccionar opción 1:** "Escanear Hardware"  
**Resultado esperado:** "Kinect v1 detectado"

### **📹 Configuración Webcam**

#### **Paso 1: Conectar Webcam**

1. **Conectar webcam** vía USB
2. **Esperar** instalación automática de drivers
3. **Verificar** en "Device Manager" → "Cameras"

#### **Paso 2: Probar Webcam**

```cmd
python hardware_tester.py
```

**Seleccionar opción 1:** "Escanear Hardware"  
**Resultado esperado:** "Webcam detectada en índice X"

#### **Paso 3: Configurar Resolución**

1. **Abrir aplicación de cámara** de Windows
2. **Configurar resolución** a 1280x720 o 1920x1080
3. **Verificar FPS** (debe ser 30 FPS)

---

## 🤖 **INSTALACIÓN DE IA LOCAL**

### **🦙 Instalación de Ollama**

#### **Paso 1: Descargar Ollama**

1. **Ir a:** https://ollama.ai/download/windows
2. **Descargar** `OllamaSetup.exe`
3. **Ejecutar** como administrador

#### **Paso 2: Instalar Ollama**

1. **Seguir instalación** por defecto
2. **Esperar** a que termine
3. **Reiniciar** si es necesario

#### **Paso 3: Verificar Ollama**

```cmd
ollama --version
```

**Resultado esperado:** `ollama version 0.x.x`

#### **Paso 4: Descargar Modelos IA**

```cmd
ollama pull llama3:8b
ollama pull phi3:mini
```

**⏳ Tiempo:** 10-30 minutos (modelos son grandes)  
**📊 Espacio:** ~8 GB total

#### **Paso 5: Probar Modelos**

```cmd
ollama list
```

**Resultado esperado:**
```
NAME            ID              SIZE    MODIFIED
llama3:8b       abc123...       4.7GB   2 minutes ago
phi3:mini       def456...       2.3GB   1 minute ago
```

### **🎤 Instalación de Whisper (Opcional)**

#### **Si ya instalaste dependencias IA:**

```cmd
venv\Scripts\activate
python -c "import whisper; print('Whisper OK')"
```

#### **Si no tienes Whisper:**

```cmd
pip install openai-whisper
```

**⚠️ Nota:** Whisper descargará modelos automáticamente en el primer uso.

---

## ⚙️ **CONFIGURACIÓN INICIAL**

### **Paso 1: Configurar Perfiles**

1. **Abrir archivo:** `config/gesture_profiles.json`
2. **Seleccionar perfil por defecto:**
   ```json
   "default_profile": "gaming"
   ```
3. **Opciones disponibles:**
   - `gaming` - Para juegos y entretenimiento
   - `productivity` - Para trabajo y presentaciones
   - `media_control` - Para control multimedia
   - `development` - Para programación
   - `accessibility` - Para accesibilidad

### **Paso 2: Configurar Hardware**

1. **Abrir archivo:** `config/hardware_settings.json`
2. **Configurar sensor preferido:**
   ```json
   "preferred_order": ["kinect_v1", "webcam_generic"]
   ```

### **Paso 3: Configurar IA**

1. **Abrir archivo:** `config/ai_config.json`
2. **Verificar configuración Ollama:**
   ```json
   "ollama": {
     "enabled": true,
     "host": "localhost",
     "port": 11434
   }
   ```

3. **Configurar Whisper:**
   ```json
   "whisper": {
     "enabled": true,
     "model": "base",
     "language": "es"
   }
   ```

---

## 🧪 **VERIFICACIÓN Y TESTING**

### **Paso 1: Test de Componentes**

```cmd
cd C:\SlapFaast\slap-faast
venv\Scripts\activate
python test_tony_stark_complete.py
```

**Resultado esperado:**
```
🧪 Test 1: Imports de módulos core ✅
🧪 Test 2: Componentes de sensores ✅
🧪 Test 3: Componentes de tracking ✅
...
🎯 TASA DE ÉXITO: 95.0%+
```

### **Paso 2: Test de Hardware**

```cmd
python hardware_tester.py
```

**Menú de opciones:**
1. **Escanear Hardware** - Detecta sensores disponibles
2. **Probar Dispositivo** - Prueba sensor específico
3. **Monitor en Tiempo Real** - Ve datos en vivo
4. **Calibrar Sensor** - Calibración automática

### **Paso 3: Test de IA**

```cmd
python -c "
from src.ai_local.ollama_client import OllamaClient
import asyncio
async def test():
    client = OllamaClient()
    response = await client.generate('Hola JARVIS')
    print(f'IA Response: {response}')
asyncio.run(test())
"
```

**Resultado esperado:** Respuesta de IA en español

---

## 🚀 **PRIMER USO**

### **Método 1: Script de Windows**

1. **Doble clic** en `Slap_Faast_Tony_Stark.bat`
2. **Esperar** pantalla de carga
3. **¡Listo!**

### **Método 2: Command Line**

```cmd
cd C:\SlapFaast\slap-faast
venv\Scripts\activate
python main_tony_stark.py
```

### **¿Qué esperar en el primer uso?**

1. **🎬 Splash Screen Tony Stark** - Pantalla de carga
2. **🔍 Detección de Hardware** - Busca sensores
3. **🤖 Inicialización IA** - Carga modelos
4. **🎨 Interfaz Principal** - Ventana principal se abre

### **Interfaz Principal - Elementos:**

#### **Panel Izquierdo:**
- **📷 Preview de Cámara** - Ve tu imagen en tiempo real
- **🎯 Estado del Sistema** - Indicadores de funcionamiento
- **🎮 Control Principal** - Botón Iniciar/Detener

#### **Panel Derecho (Pestañas):**
- **👋 Gestos** - Lista de gestos disponibles
- **🔧 Hardware** - Monitor de sensores
- **⚙️ Configuración** - Ajustes del sistema

### **Primer Comando de Prueba:**

1. **Hacer gesto "Brazos Arriba"** - Levantar ambos brazos
2. **Decir:** "JARVIS, hola"
3. **Resultado esperado:** 
   - Gesto detectado en pantalla
   - Audio JARVIS responde
   - Acción ejecutada (Play/Pausa)

---

## 🛠️ **SOLUCIÓN DE PROBLEMAS**

### **❌ Problema: Python no encontrado**

**Error:** `'python' is not recognized as an internal or external command`

**Solución:**
1. Reinstalar Python con "Add to PATH" marcado
2. O usar ruta completa: `C:\Python310\python.exe`

### **❌ Problema: Error al instalar dependencias**

**Error:** `ERROR: Could not install packages due to an EnvironmentError`

**Solución:**
1. Ejecutar cmd como **administrador**
2. Usar: `pip install --user [paquete]`
3. O instalar Visual C++ Build Tools

### **❌ Problema: Kinect no detectado**

**Error:** `No Kinect sensor found`

**Solución:**
1. Verificar conexión USB y corriente
2. Reinstalar Kinect SDK v1.8
3. Verificar en Device Manager
4. Probar otro puerto USB
5. Reiniciar PC

### **❌ Problema: Ollama no responde**

**Error:** `Connection refused to localhost:11434`

**Solución:**
1. Verificar que Ollama esté ejecutándose:
   ```cmd
   ollama serve
   ```
2. Verificar puerto en Task Manager
3. Reiniciar servicio Ollama
4. Verificar firewall

### **❌ Problema: Webcam no funciona**

**Error:** `Could not open camera`

**Solución:**
1. Cerrar otras aplicaciones que usen cámara
2. Verificar drivers en Device Manager
3. Probar con otra aplicación (ej: Camera de Windows)
4. Cambiar resolución en código

### **❌ Problema: Audio no funciona**

**Error:** `pygame.error: No available audio device`

**Solución:**
1. Verificar dispositivos de audio en Windows
2. Instalar drivers de audio
3. Configurar dispositivo por defecto
4. Reiniciar aplicación

### **❌ Problema: Interfaz no se abre**

**Error:** `QApplication: invalid style override`

**Solución:**
1. Verificar instalación PyQt6:
   ```cmd
   pip uninstall PyQt6
   pip install PyQt6
   ```
2. Verificar drivers gráficos
3. Ejecutar en modo compatibilidad

### **❌ Problema: Gestos no se detectan**

**Error:** Gestos no reconocidos

**Solución:**
1. Verificar iluminación (buena luz)
2. Verificar distancia (1.5-3 metros)
3. Calibrar sensor en hardware_tester.py
4. Ajustar confianza en configuración
5. Verificar que no hay obstrucciones

### **❌ Problema: IA muy lenta**

**Error:** Respuestas tardan mucho

**Solución:**
1. Usar modelo más pequeño: `phi3:mini`
2. Verificar uso de CPU/RAM
3. Cerrar otras aplicaciones
4. Considerar GPU si disponible

---

## 📞 **SOPORTE ADICIONAL**

### **🔍 Logs del Sistema**

**Ubicación:** `logs/slap_faast.log`

**Ver logs en tiempo real:**
```cmd
tail -f logs/slap_faast.log
```

### **📊 Información del Sistema**

```cmd
python -c "
import platform
import sys
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.machine()}')
"
```

### **🧪 Diagnóstico Completo**

```cmd
python hardware_tester.py
# Seleccionar opción 4: "Diagnóstico Completo"
```

### **📱 Contacto**

- **GitHub Issues:** https://github.com/tu-usuario/slap-faast/issues
- **Email:** soporte@slapfaast.com
- **Discord:** SlapFaast Community

---

## 🎉 **¡INSTALACIÓN COMPLETADA!**

### **🎯 Próximos Pasos:**

1. **🎮 Personalizar gestos** en el editor visual
2. **🎨 Cambiar tema** en configuración
3. **🤖 Entrenar IA** con tus comandos favoritos
4. **📊 Explorar analytics** en el dashboard
5. **🔧 Crear perfiles** personalizados

### **🚀 ¡Disfruta tu JARVIS personal!**

**Tu sistema de control gestual Tony Stark está listo para usar. ¡Que la fuerza (y los gestos) te acompañen!** ✨

---

**📝 Documento creado:** Diciembre 2024  
**✍️ Versión:** 1.0  
**🔄 Última actualización:** 19/12/2024

