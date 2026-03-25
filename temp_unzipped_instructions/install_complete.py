#!/usr/bin/env python3
"""
Script de Instalación Completa - Slap!Faast v2.0 Tony Stark Edition
Instala todas las dependencias y configura el sistema
"""

import os
import sys
import subprocess
import platform
import json
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SlapFaastInstaller:
    """Instalador completo de Slap!Faast v2.0"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.python_version = sys.version_info
        
        # Rutas
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.config_path = self.project_root / "config"
        self.logs_path = self.project_root / "logs"
        self.profiles_path = self.project_root / "profiles"
        
        # Dependencias principales
        self.python_packages = [
            "PyQt6==6.6.1",
            "opencv-python==4.8.1.78",
            "mediapipe==0.10.8",
            "numpy==1.24.3",
            "scipy==1.11.4",
            "scikit-learn==1.3.2",
            "requests==2.31.0",
            "aiohttp==3.9.1",
            "asyncio-mqtt==0.13.0",
            "pygame==2.5.2",
            "pyttsx3==2.90",
            "SpeechRecognition==3.10.0",
            "pyaudio==0.2.11",
            "pillow==10.1.0",
            "matplotlib==3.8.2",
            "seaborn==0.13.0",
            "pandas==2.1.4",
            "pyautogui==0.9.54",
            "keyboard==0.13.5",
            "mouse==0.7.1",
            "psutil==5.9.6",
            "watchdog==3.0.0",
            "colorama==0.4.6",
            "tqdm==4.66.1",
            "rich==13.7.0"
        ]
        
        # Dependencias opcionales
        self.optional_packages = [
            "openai-whisper==20231117",
            "torch==2.1.2",
            "torchvision==0.16.2",
            "torchaudio==2.1.2",
            "transformers==4.36.2",
            "sentence-transformers==2.2.2",
            "ultralytics==8.0.232",
            "easyocr==1.7.0"
        ]
        
        # URLs de descarga
        self.downloads = {
            "ollama_windows": "https://ollama.ai/download/windows",
            "kinect_sdk": "https://www.microsoft.com/en-us/download/details.aspx?id=40278",
            "visual_cpp": "https://aka.ms/vs/17/release/vc_redist.x64.exe"
        }
        
        self.installation_steps = [
            ("Verificando sistema", self.check_system),
            ("Verificando Python", self.check_python),
            ("Creando entorno virtual", self.create_virtual_environment),
            ("Instalando dependencias principales", self.install_main_dependencies),
            ("Instalando dependencias opcionales", self.install_optional_dependencies),
            ("Configurando directorios", self.setup_directories),
            ("Instalando Ollama", self.install_ollama),
            ("Configurando modelos IA", self.setup_ai_models),
            ("Verificando hardware", self.check_hardware),
            ("Configurando sistema", self.configure_system),
            ("Ejecutando pruebas", self.run_tests),
            ("Finalizando instalación", self.finalize_installation)
        ]
    
    def run_installation(self):
        """Ejecuta instalación completa"""
        logger.info("🚀 Iniciando instalación de Slap!Faast v2.0 Tony Stark Edition")
        
        try:
            total_steps = len(self.installation_steps)
            
            for i, (step_name, step_func) in enumerate(self.installation_steps, 1):
                logger.info(f"📋 Paso {i}/{total_steps}: {step_name}")
                
                try:
                    success = step_func()
                    if not success:
                        logger.error(f"❌ Error en paso: {step_name}")
                        return False
                    
                    logger.info(f"✅ Completado: {step_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Error ejecutando {step_name}: {e}")
                    return False
            
            logger.info("🎉 ¡Instalación completada exitosamente!")
            self.show_completion_message()
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Instalación cancelada por el usuario")
            return False
        except Exception as e:
            logger.error(f"❌ Error crítico durante instalación: {e}")
            return False
    
    def check_system(self):
        """Verifica compatibilidad del sistema"""
        logger.info(f"🖥️ Sistema: {platform.system()} {platform.release()}")
        logger.info(f"🏗️ Arquitectura: {self.architecture}")
        
        if self.system not in ['windows', 'linux', 'darwin']:
            logger.error(f"❌ Sistema no soportado: {self.system}")
            return False
        
        if self.system == 'windows':
            # Verificar Windows 10/11
            version = platform.version()
            if not any(v in version for v in ['10.0', '11.0']):
                logger.warning("⚠️ Se recomienda Windows 10 o superior")
        
        return True
    
    def check_python(self):
        """Verifica versión de Python"""
        logger.info(f"🐍 Python: {sys.version}")
        
        if self.python_version < (3, 8):
            logger.error("❌ Se requiere Python 3.8 o superior")
            return False
        
        if self.python_version >= (3, 12):
            logger.warning("⚠️ Python 3.12+ puede tener problemas de compatibilidad")
        
        # Verificar pip
        try:
            import pip
            logger.info(f"📦 pip: {pip.__version__}")
        except ImportError:
            logger.error("❌ pip no encontrado")
            return False
        
        return True
    
    def create_virtual_environment(self):
        """Crea entorno virtual"""
        if self.venv_path.exists():
            logger.info("🔄 Entorno virtual existente encontrado")
            return True
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True)
            
            logger.info(f"✅ Entorno virtual creado en: {self.venv_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creando entorno virtual: {e}")
            return False
    
    def install_main_dependencies(self):
        """Instala dependencias principales"""
        pip_path = self.get_pip_path()
        
        logger.info("📦 Instalando dependencias principales...")
        
        # Actualizar pip
        try:
            subprocess.run([
                pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"
            ], check=True)
        except subprocess.CalledProcessError:
            logger.warning("⚠️ No se pudo actualizar pip")
        
        # Instalar dependencias
        failed_packages = []
        
        for package in self.python_packages:
            try:
                logger.info(f"📦 Instalando: {package}")
                subprocess.run([
                    pip_path, "install", package
                ], check=True, capture_output=True)
                
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ Error instalando {package}: {e}")
                failed_packages.append(package)
        
        if failed_packages:
            logger.warning(f"⚠️ Paquetes que fallaron: {failed_packages}")
            logger.info("🔄 Intentando instalación alternativa...")
            
            # Intentar sin versiones específicas
            for package in failed_packages:
                package_name = package.split('==')[0]
                try:
                    subprocess.run([
                        pip_path, "install", package_name
                    ], check=True, capture_output=True)
                    logger.info(f"✅ Instalado (sin versión): {package_name}")
                except subprocess.CalledProcessError:
                    logger.error(f"❌ No se pudo instalar: {package_name}")
        
        return True
    
    def install_optional_dependencies(self):
        """Instala dependencias opcionales"""
        pip_path = self.get_pip_path()
        
        logger.info("📦 Instalando dependencias opcionales (IA)...")
        
        for package in self.optional_packages:
            try:
                logger.info(f"📦 Instalando (opcional): {package}")
                subprocess.run([
                    pip_path, "install", package
                ], check=True, capture_output=True, timeout=300)
                
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                logger.warning(f"⚠️ Dependencia opcional no instalada: {package}")
        
        return True
    
    def setup_directories(self):
        """Configura directorios del proyecto"""
        directories = [
            self.logs_path,
            self.profiles_path,
            self.project_root / "temp",
            self.project_root / "cache",
            self.project_root / "exports",
            self.project_root / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logger.info(f"📁 Directorio creado: {directory.name}")
        
        return True
    
    def install_ollama(self):
        """Instala Ollama para IA local"""
        logger.info("🤖 Verificando instalación de Ollama...")
        
        # Verificar si ya está instalado
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Ollama ya instalado: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        logger.info("📥 Ollama no encontrado, se requiere instalación manual")
        
        if self.system == 'windows':
            logger.info("🔗 Descarga Ollama desde: https://ollama.ai/download/windows")
        elif self.system == 'linux':
            logger.info("💻 Ejecuta: curl -fsSL https://ollama.ai/install.sh | sh")
        elif self.system == 'darwin':
            logger.info("🍎 Descarga Ollama desde: https://ollama.ai/download/mac")
        
        logger.info("⏳ Ollama se instalará después, continuando...")
        return True
    
    def setup_ai_models(self):
        """Configura modelos de IA"""
        logger.info("🧠 Configurando modelos de IA...")
        
        # Verificar si Ollama está disponible
        try:
            subprocess.run(["ollama", "list"], 
                          capture_output=True, check=True)
            
            # Descargar modelos básicos
            models_to_download = ["llama3:8b", "phi3:mini"]
            
            for model in models_to_download:
                logger.info(f"📥 Descargando modelo: {model}")
                try:
                    subprocess.run(["ollama", "pull", model], 
                                  check=True, timeout=600)
                    logger.info(f"✅ Modelo descargado: {model}")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    logger.warning(f"⚠️ No se pudo descargar: {model}")
            
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("⚠️ Ollama no disponible, modelos se descargarán después")
        
        return True
    
    def check_hardware(self):
        """Verifica hardware disponible"""
        logger.info("🔍 Verificando hardware...")
        
        # Verificar cámaras
        import cv2
        camera_found = False
        
        for i in range(3):  # Verificar primeras 3 cámaras
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                logger.info(f"📷 Cámara encontrada: índice {i}")
                camera_found = True
                cap.release()
                break
        
        if not camera_found:
            logger.warning("⚠️ No se encontraron cámaras")
        
        # Verificar Kinect (solo en Windows)
        if self.system == 'windows':
            try:
                # Intentar importar librerías de Kinect
                import ctypes
                kinect_dll = ctypes.util.find_library('Kinect10')
                if kinect_dll:
                    logger.info("🎮 SDK Kinect v1 encontrado")
                else:
                    logger.info("ℹ️ SDK Kinect no encontrado (opcional)")
            except:
                logger.info("ℹ️ Verificación de Kinect omitida")
        
        return True
    
    def configure_system(self):
        """Configura el sistema"""
        logger.info("⚙️ Configurando sistema...")
        
        # Crear archivo de configuración principal
        config = {
            "version": "2.0.0",
            "installation_date": str(Path(__file__).stat().st_mtime),
            "system_info": {
                "platform": self.system,
                "architecture": self.architecture,
                "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}"
            },
            "paths": {
                "project_root": str(self.project_root),
                "venv_path": str(self.venv_path),
                "config_path": str(self.config_path),
                "logs_path": str(self.logs_path)
            }
        }
        
        config_file = self.project_root / "installation_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Configuración guardada en: {config_file}")
        
        return True
    
    def run_tests(self):
        """Ejecuta pruebas básicas"""
        logger.info("🧪 Ejecutando pruebas básicas...")
        
        python_path = self.get_python_path()
        
        # Test de imports básicos
        test_imports = [
            "PyQt6.QtWidgets",
            "cv2",
            "mediapipe",
            "numpy",
            "requests",
            "pygame"
        ]
        
        for module in test_imports:
            try:
                subprocess.run([
                    python_path, "-c", f"import {module}; print(f'✅ {module} OK')"
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.warning(f"⚠️ Módulo no disponible: {module}")
        
        logger.info("✅ Pruebas básicas completadas")
        return True
    
    def finalize_installation(self):
        """Finaliza la instalación"""
        logger.info("🎯 Finalizando instalación...")
        
        # Crear scripts de ejecución
        if self.system == 'windows':
            self.create_windows_scripts()
        else:
            self.create_unix_scripts()
        
        # Crear acceso directo en escritorio (Windows)
        if self.system == 'windows':
            self.create_desktop_shortcut()
        
        return True
    
    def create_windows_scripts(self):
        """Crea scripts para Windows"""
        # Script principal
        bat_content = f"""@echo off
cd /d "{self.project_root}"
"{self.get_python_path()}" main_tony_stark.py
pause
"""
        
        bat_file = self.project_root / "Slap_Faast_Tony_Stark.bat"
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        logger.info(f"✅ Script creado: {bat_file}")
    
    def create_unix_scripts(self):
        """Crea scripts para Unix/Linux"""
        sh_content = f"""#!/bin/bash
cd "{self.project_root}"
"{self.get_python_path()}" main_tony_stark.py
"""
        
        sh_file = self.project_root / "slap_faast_tony_stark.sh"
        with open(sh_file, 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Hacer ejecutable
        os.chmod(sh_file, 0o755)
        
        logger.info(f"✅ Script creado: {sh_file}")
    
    def create_desktop_shortcut(self):
        """Crea acceso directo en escritorio (Windows)"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Slap!Faast Tony Stark.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.project_root / "Slap_Faast_Tony_Stark.bat")
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = str(self.project_root / "icon.ico")
            shortcut.save()
            
            logger.info(f"✅ Acceso directo creado: {shortcut_path}")
            
        except ImportError:
            logger.info("ℹ️ No se pudo crear acceso directo (winshell no disponible)")
        except Exception as e:
            logger.warning(f"⚠️ Error creando acceso directo: {e}")
    
    def get_python_path(self):
        """Obtiene ruta del ejecutable Python del venv"""
        if self.system == 'windows':
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def get_pip_path(self):
        """Obtiene ruta del ejecutable pip del venv"""
        if self.system == 'windows':
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def show_completion_message(self):
        """Muestra mensaje de finalización"""
        message = f"""
🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE! 🎉

Slap!Faast v2.0 Tony Stark Edition está listo para usar.

📋 PRÓXIMOS PASOS:

1. 🤖 Instalar Ollama (si no está instalado):
   - Windows: https://ollama.ai/download/windows
   - Linux: curl -fsSL https://ollama.ai/install.sh | sh
   - Mac: https://ollama.ai/download/mac

2. 📥 Descargar modelos IA (opcional):
   ollama pull llama3:8b
   ollama pull phi3:mini

3. 🎮 Conectar Kinect v1 (opcional) o usar webcam

4. 🚀 EJECUTAR SLAP!FAAST:
   {"python main_tony_stark.py" if self.system != 'windows' else "Doble clic en Slap_Faast_Tony_Stark.bat"}

📁 Archivos importantes:
   - Ejecutable: {self.project_root / ("Slap_Faast_Tony_Stark.bat" if self.system == 'windows' else "slap_faast_tony_stark.sh")}
   - Configuración: {self.config_path}
   - Logs: {self.logs_path}

🎯 ¡Tu sistema de control gestual Tony Stark está listo!

Para soporte: https://github.com/tu-repo/slap-faast
"""
        
        print(message)
        logger.info("🎉 Instalación completada exitosamente")

def main():
    """Función principal"""
    print("🚀 Slap!Faast v2.0 Tony Stark Edition - Instalador")
    print("=" * 60)
    
    installer = SlapFaastInstaller()
    success = installer.run_installation()
    
    if success:
        print("\n✅ ¡Instalación exitosa!")
        return 0
    else:
        print("\n❌ Error durante la instalación")
        return 1

if __name__ == "__main__":
    sys.exit(main())

