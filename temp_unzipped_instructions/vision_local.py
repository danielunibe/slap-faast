"""
Vision Local para Slap!Faast v2.0
Análisis de contexto visual de la pantalla para IA Tony Stark
"""

import asyncio
import logging
import json
import time
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
from pathlib import Path
import base64
import io
from PIL import Image, ImageGrab
import psutil
import win32gui
import win32process
import win32con
import win32api
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class WindowInfo:
    """Información de una ventana"""
    hwnd: int
    title: str
    class_name: str
    process_name: str
    pid: int
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    is_visible: bool
    is_minimized: bool
    is_maximized: bool
    z_order: int
    area: int

@dataclass
class ApplicationInfo:
    """Información de una aplicación"""
    name: str
    process_name: str
    pid: int
    windows: List[WindowInfo]
    main_window: Optional[WindowInfo]
    is_active: bool
    cpu_usage: float
    memory_usage: float  # MB

@dataclass
class UIElement:
    """Elemento de interfaz detectado"""
    type: str  # 'button', 'menu', 'text_field', 'icon', 'window'
    text: str
    rect: Tuple[int, int, int, int]
    confidence: float
    properties: Dict[str, Any]

@dataclass
class ScreenContext:
    """Contexto completo de la pantalla"""
    timestamp: datetime
    active_window: Optional[WindowInfo]
    visible_windows: List[WindowInfo]
    applications: List[ApplicationInfo]
    ui_elements: List[UIElement]
    screen_resolution: Tuple[int, int]
    desktop_state: Dict[str, Any]
    content_analysis: Dict[str, Any]
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class VisionLocal:
    """Análisis de contexto visual local de la pantalla"""
    
    def __init__(self):
        self.is_initialized = False
        self.is_monitoring = False
        
        # Threading para captura continua
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()
        
        # Cache de contexto
        self.current_context = None
        self.context_history = []
        self.max_history = 10
        
        # Configuración de análisis
        self.analysis_config = {
            'capture_interval': 2.0,  # segundos entre capturas
            'window_detection': True,
            'ui_element_detection': True,
            'content_analysis': True,
            'performance_monitoring': True,
            'screenshot_analysis': False,  # Deshabilitado por defecto por privacidad
            'max_windows': 50,
            'min_window_area': 100
        }
        
        # Mapeo de procesos conocidos
        self.known_applications = {
            'chrome.exe': 'Google Chrome',
            'firefox.exe': 'Mozilla Firefox',
            'msedge.exe': 'Microsoft Edge',
            'code.exe': 'Visual Studio Code',
            'notepad.exe': 'Notepad',
            'explorer.exe': 'Windows Explorer',
            'cmd.exe': 'Command Prompt',
            'powershell.exe': 'PowerShell',
            'winword.exe': 'Microsoft Word',
            'excel.exe': 'Microsoft Excel',
            'outlook.exe': 'Microsoft Outlook',
            'teams.exe': 'Microsoft Teams',
            'discord.exe': 'Discord',
            'spotify.exe': 'Spotify',
            'steam.exe': 'Steam',
            'vlc.exe': 'VLC Media Player'
        }
        
        # Estadísticas
        self.stats = {
            'contexts_analyzed': 0,
            'windows_detected': 0,
            'applications_tracked': 0,
            'ui_elements_found': 0,
            'average_analysis_time': 0.0,
            'uptime_seconds': 0.0,
            'start_time': None
        }
    
    async def initialize(self) -> bool:
        """Inicializa el sistema de visión local"""
        try:
            logger.info("👁️ Inicializando Vision Local...")
            
            # Verificar permisos de Windows
            if not self._check_windows_permissions():
                logger.warning("⚠️ Permisos limitados, algunas funciones pueden no estar disponibles")
            
            # Inicializar estadísticas
            self.stats['start_time'] = datetime.now()
            
            # Realizar análisis inicial
            initial_context = await self.analyze_screen_context()
            if initial_context:
                logger.info(f"✅ Contexto inicial: {len(initial_context.visible_windows)} ventanas, "
                           f"{len(initial_context.applications)} aplicaciones")
            
            self.is_initialized = True
            logger.info("✅ Vision Local inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Vision Local: {e}")
            self.is_initialized = False
            return False
    
    def _check_windows_permissions(self) -> bool:
        """Verifica permisos necesarios en Windows"""
        try:
            # Intentar enumerar ventanas
            win32gui.EnumWindows(lambda hwnd, param: True, None)
            
            # Intentar obtener información de procesos
            list(psutil.process_iter(['pid', 'name']))
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Permisos limitados: {e}")
            return False
    
    async def analyze_screen_context(self) -> Optional[ScreenContext]:
        """Analiza el contexto completo de la pantalla"""
        if not self.is_initialized:
            raise Exception("Vision Local no inicializado")
        
        start_time = time.time()
        
        try:
            # Obtener información de ventanas
            windows = await self._get_window_information()
            
            # Obtener información de aplicaciones
            applications = await self._get_application_information(windows)
            
            # Detectar ventana activa
            active_window = await self._get_active_window(windows)
            
            # Detectar elementos UI (si está habilitado)
            ui_elements = []
            if self.analysis_config['ui_element_detection']:
                ui_elements = await self._detect_ui_elements(active_window)
            
            # Análisis de contenido (si está habilitado)
            content_analysis = {}
            if self.analysis_config['content_analysis']:
                content_analysis = await self._analyze_content(active_window, applications)
            
            # Obtener resolución de pantalla
            screen_resolution = self._get_screen_resolution()
            
            # Estado del escritorio
            desktop_state = await self._get_desktop_state(windows, applications)
            
            # Crear contexto
            context = ScreenContext(
                timestamp=datetime.now(),
                active_window=active_window,
                visible_windows=[w for w in windows if w.is_visible],
                applications=applications,
                ui_elements=ui_elements,
                screen_resolution=screen_resolution,
                desktop_state=desktop_state,
                content_analysis=content_analysis
            )
            
            # Actualizar cache y historial
            self.current_context = context
            self._update_context_history(context)
            
            # Actualizar estadísticas
            analysis_time = time.time() - start_time
            self._update_stats(context, analysis_time)
            
            logger.debug(f"👁️ Contexto analizado: {len(context.visible_windows)} ventanas, "
                        f"{len(context.applications)} apps, tiempo: {analysis_time:.2f}s")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Error analizando contexto de pantalla: {e}")
            return None
    
    async def _get_window_information(self) -> List[WindowInfo]:
        """Obtiene información de todas las ventanas"""
        windows = []
        
        def enum_windows_callback(hwnd, param):
            try:
                # Verificar si la ventana es válida
                if not win32gui.IsWindow(hwnd):
                    return True
                
                # Obtener información básica
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # Filtrar ventanas sin título o invisibles importantes
                if not title and class_name not in ['Progman', 'WorkerW', 'Shell_TrayWnd']:
                    return True
                
                # Obtener rectángulo de la ventana
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    area = (rect[2] - rect[0]) * (rect[3] - rect[1])
                    
                    # Filtrar ventanas muy pequeñas
                    if area < self.analysis_config['min_window_area']:
                        return True
                        
                except:
                    return True
                
                # Obtener información del proceso
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    process_name = process.name()
                except:
                    pid = 0
                    process_name = "unknown"
                
                # Determinar estado de la ventana
                is_visible = win32gui.IsWindowVisible(hwnd)
                is_minimized = win32gui.IsIconic(hwnd)
                is_maximized = win32gui.IsZoomed(hwnd)
                
                # Obtener Z-order (aproximado)
                z_order = 0
                try:
                    z_order = win32gui.GetWindowLong(hwnd, win32con.GWL_HWNDPARENT)
                except:
                    pass
                
                window_info = WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    class_name=class_name,
                    process_name=process_name,
                    pid=pid,
                    rect=rect,
                    is_visible=is_visible,
                    is_minimized=is_minimized,
                    is_maximized=is_maximized,
                    z_order=z_order,
                    area=area
                )
                
                windows.append(window_info)
                
                # Limitar número de ventanas
                if len(windows) >= self.analysis_config['max_windows']:
                    return False
                
            except Exception as e:
                logger.debug(f"Error procesando ventana {hwnd}: {e}")
            
            return True
        
        try:
            win32gui.EnumWindows(enum_windows_callback, None)
        except Exception as e:
            logger.error(f"❌ Error enumerando ventanas: {e}")
        
        # Ordenar por área (ventanas más grandes primero)
        windows.sort(key=lambda w: w.area, reverse=True)
        
        return windows
    
    async def _get_application_information(self, windows: List[WindowInfo]) -> List[ApplicationInfo]:
        """Obtiene información de aplicaciones basada en ventanas"""
        app_dict = defaultdict(lambda: {
            'windows': [],
            'pids': set(),
            'process_names': set()
        })
        
        # Agrupar ventanas por aplicación
        for window in windows:
            if window.process_name == "unknown":
                continue
                
            app_name = self.known_applications.get(
                window.process_name, 
                window.process_name.replace('.exe', '').title()
            )
            
            app_dict[app_name]['windows'].append(window)
            app_dict[app_name]['pids'].add(window.pid)
            app_dict[app_name]['process_names'].add(window.process_name)
        
        applications = []
        
        for app_name, app_data in app_dict.items():
            try:
                # Encontrar ventana principal (más grande y visible)
                main_window = None
                visible_windows = [w for w in app_data['windows'] if w.is_visible and not w.is_minimized]
                if visible_windows:
                    main_window = max(visible_windows, key=lambda w: w.area)
                
                # Determinar si la aplicación está activa
                is_active = any(w.hwnd == win32gui.GetForegroundWindow() for w in app_data['windows'])
                
                # Obtener métricas de rendimiento
                cpu_usage = 0.0
                memory_usage = 0.0
                
                for pid in app_data['pids']:
                    try:
                        process = psutil.Process(pid)
                        cpu_usage += process.cpu_percent()
                        memory_usage += process.memory_info().rss / 1024 / 1024  # MB
                    except:
                        continue
                
                # Usar el primer PID y nombre de proceso
                main_pid = list(app_data['pids'])[0] if app_data['pids'] else 0
                main_process_name = list(app_data['process_names'])[0] if app_data['process_names'] else "unknown"
                
                app_info = ApplicationInfo(
                    name=app_name,
                    process_name=main_process_name,
                    pid=main_pid,
                    windows=app_data['windows'],
                    main_window=main_window,
                    is_active=is_active,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage
                )
                
                applications.append(app_info)
                
            except Exception as e:
                logger.debug(f"Error procesando aplicación {app_name}: {e}")
        
        # Ordenar por importancia (activa primero, luego por uso de CPU)
        applications.sort(key=lambda a: (not a.is_active, -a.cpu_usage))
        
        return applications
    
    async def _get_active_window(self, windows: List[WindowInfo]) -> Optional[WindowInfo]:
        """Obtiene la ventana actualmente activa"""
        try:
            active_hwnd = win32gui.GetForegroundWindow()
            
            for window in windows:
                if window.hwnd == active_hwnd:
                    return window
                    
        except Exception as e:
            logger.debug(f"Error obteniendo ventana activa: {e}")
        
        return None
    
    async def _detect_ui_elements(self, active_window: Optional[WindowInfo]) -> List[UIElement]:
        """Detecta elementos de UI en la ventana activa"""
        ui_elements = []
        
        if not active_window or not self.analysis_config['ui_element_detection']:
            return ui_elements
        
        try:
            # Análisis básico basado en información de ventana
            # En una implementación completa, aquí se usaría OCR o análisis de imagen
            
            # Detectar tipo de ventana basado en clase
            window_type = self._classify_window_type(active_window)
            
            # Generar elementos UI básicos basados en el tipo
            if window_type == 'browser':
                ui_elements.extend(self._generate_browser_ui_elements(active_window))
            elif window_type == 'editor':
                ui_elements.extend(self._generate_editor_ui_elements(active_window))
            elif window_type == 'explorer':
                ui_elements.extend(self._generate_explorer_ui_elements(active_window))
            
        except Exception as e:
            logger.debug(f"Error detectando elementos UI: {e}")
        
        return ui_elements
    
    def _classify_window_type(self, window: WindowInfo) -> str:
        """Clasifica el tipo de ventana"""
        process_name = window.process_name.lower()
        class_name = window.class_name.lower()
        title = window.title.lower()
        
        if any(browser in process_name for browser in ['chrome', 'firefox', 'edge', 'safari']):
            return 'browser'
        elif any(editor in process_name for editor in ['code', 'notepad', 'sublime', 'atom']):
            return 'editor'
        elif 'explorer' in process_name or 'cabinets' in class_name:
            return 'explorer'
        elif any(office in process_name for office in ['winword', 'excel', 'powerpnt']):
            return 'office'
        elif any(media in process_name for media in ['vlc', 'wmplayer', 'spotify']):
            return 'media'
        else:
            return 'generic'
    
    def _generate_browser_ui_elements(self, window: WindowInfo) -> List[UIElement]:
        """Genera elementos UI típicos de navegador"""
        elements = []
        rect = window.rect
        
        # Barra de direcciones (estimada)
        elements.append(UIElement(
            type='text_field',
            text='Address Bar',
            rect=(rect[0] + 100, rect[1] + 50, rect[2] - 100, rect[1] + 80),
            confidence=0.8,
            properties={'editable': True, 'purpose': 'navigation'}
        ))
        
        # Botones de navegación (estimados)
        elements.append(UIElement(
            type='button',
            text='Back',
            rect=(rect[0] + 10, rect[1] + 50, rect[0] + 40, rect[1] + 80),
            confidence=0.7,
            properties={'action': 'navigate_back'}
        ))
        
        return elements
    
    def _generate_editor_ui_elements(self, window: WindowInfo) -> List[UIElement]:
        """Genera elementos UI típicos de editor"""
        elements = []
        rect = window.rect
        
        # Área de texto principal
        elements.append(UIElement(
            type='text_field',
            text='Editor Area',
            rect=(rect[0] + 50, rect[1] + 100, rect[2] - 50, rect[3] - 50),
            confidence=0.9,
            properties={'editable': True, 'purpose': 'editing'}
        ))
        
        return elements
    
    def _generate_explorer_ui_elements(self, window: WindowInfo) -> List[UIElement]:
        """Genera elementos UI típicos de explorador"""
        elements = []
        rect = window.rect
        
        # Barra de ruta
        elements.append(UIElement(
            type='text_field',
            text='Path Bar',
            rect=(rect[0] + 50, rect[1] + 50, rect[2] - 50, rect[1] + 80),
            confidence=0.8,
            properties={'editable': True, 'purpose': 'navigation'}
        ))
        
        return elements
    
    async def _analyze_content(self, active_window: Optional[WindowInfo], 
                             applications: List[ApplicationInfo]) -> Dict[str, Any]:
        """Analiza el contenido de la pantalla"""
        analysis = {
            'window_count': len([app for app in applications if app.windows]),
            'active_app': active_window.process_name if active_window else None,
            'app_categories': self._categorize_applications(applications),
            'workspace_type': self._determine_workspace_type(applications),
            'multitasking_level': self._calculate_multitasking_level(applications),
            'focus_suggestions': self._generate_focus_suggestions(applications)
        }
        
        return analysis
    
    def _categorize_applications(self, applications: List[ApplicationInfo]) -> Dict[str, int]:
        """Categoriza aplicaciones por tipo"""
        categories = defaultdict(int)
        
        category_mapping = {
            'browser': ['chrome', 'firefox', 'edge', 'safari'],
            'development': ['code', 'visual studio', 'intellij', 'eclipse'],
            'office': ['word', 'excel', 'powerpoint', 'outlook'],
            'media': ['vlc', 'spotify', 'media player', 'photos'],
            'communication': ['teams', 'discord', 'skype', 'zoom'],
            'system': ['explorer', 'cmd', 'powershell', 'task manager']
        }
        
        for app in applications:
            app_name_lower = app.name.lower()
            categorized = False
            
            for category, keywords in category_mapping.items():
                if any(keyword in app_name_lower for keyword in keywords):
                    categories[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                categories['other'] += 1
        
        return dict(categories)
    
    def _determine_workspace_type(self, applications: List[ApplicationInfo]) -> str:
        """Determina el tipo de espacio de trabajo"""
        categories = self._categorize_applications(applications)
        
        if categories.get('development', 0) >= 2:
            return 'development'
        elif categories.get('office', 0) >= 2:
            return 'productivity'
        elif categories.get('media', 0) >= 2:
            return 'entertainment'
        elif categories.get('browser', 0) >= 2:
            return 'research'
        elif categories.get('communication', 0) >= 1:
            return 'collaboration'
        else:
            return 'general'
    
    def _calculate_multitasking_level(self, applications: List[ApplicationInfo]) -> str:
        """Calcula el nivel de multitarea"""
        visible_apps = len([app for app in applications if app.main_window and app.main_window.is_visible])
        
        if visible_apps <= 2:
            return 'low'
        elif visible_apps <= 5:
            return 'medium'
        else:
            return 'high'
    
    def _generate_focus_suggestions(self, applications: List[ApplicationInfo]) -> List[str]:
        """Genera sugerencias para mejorar el enfoque"""
        suggestions = []
        
        visible_apps = [app for app in applications if app.main_window and app.main_window.is_visible]
        
        if len(visible_apps) > 7:
            suggestions.append("Considera cerrar algunas aplicaciones para mejorar el rendimiento")
        
        high_cpu_apps = [app for app in applications if app.cpu_usage > 20]
        if high_cpu_apps:
            suggestions.append(f"Aplicaciones con alto uso de CPU: {', '.join([app.name for app in high_cpu_apps])}")
        
        return suggestions
    
    def _get_screen_resolution(self) -> Tuple[int, int]:
        """Obtiene la resolución de pantalla"""
        try:
            return (win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))
        except:
            return (1920, 1080)  # Valor por defecto
    
    async def _get_desktop_state(self, windows: List[WindowInfo], 
                                applications: List[ApplicationInfo]) -> Dict[str, Any]:
        """Obtiene el estado del escritorio"""
        visible_windows = [w for w in windows if w.is_visible and not w.is_minimized]
        
        state = {
            'total_windows': len(windows),
            'visible_windows': len(visible_windows),
            'minimized_windows': len([w for w in windows if w.is_minimized]),
            'maximized_windows': len([w for w in windows if w.is_maximized]),
            'total_applications': len(applications),
            'active_applications': len([app for app in applications if app.is_active]),
            'desktop_cluttered': len(visible_windows) > 8,
            'has_fullscreen_app': any(w.is_maximized for w in visible_windows),
            'primary_activity': self._determine_workspace_type(applications)
        }
        
        return state
    
    def _update_context_history(self, context: ScreenContext):
        """Actualiza el historial de contextos"""
        self.context_history.append(context)
        
        # Mantener solo los últimos N contextos
        if len(self.context_history) > self.max_history:
            self.context_history = self.context_history[-self.max_history:]
    
    def _update_stats(self, context: ScreenContext, analysis_time: float):
        """Actualiza estadísticas de análisis"""
        self.stats['contexts_analyzed'] += 1
        self.stats['windows_detected'] += len(context.visible_windows)
        self.stats['applications_tracked'] += len(context.applications)
        self.stats['ui_elements_found'] += len(context.ui_elements)
        
        # Actualizar tiempo promedio de análisis
        count = self.stats['contexts_analyzed']
        current_avg = self.stats['average_analysis_time']
        self.stats['average_analysis_time'] = (current_avg * (count - 1) + analysis_time) / count
        
        # Actualizar uptime
        if self.stats['start_time']:
            self.stats['uptime_seconds'] = (datetime.now() - self.stats['start_time']).total_seconds()
    
    async def start_continuous_monitoring(self, interval: float = None):
        """Inicia monitoreo continuo del contexto"""
        if self.is_monitoring:
            logger.warning("⚠️ Monitoreo ya está activo")
            return
        
        if interval:
            self.analysis_config['capture_interval'] = interval
        
        self.is_monitoring = True
        self.stop_monitoring.clear()
        
        def monitor_loop():
            """Loop de monitoreo en thread separado"""
            logger.info(f"🔄 Iniciando monitoreo continuo (intervalo: {self.analysis_config['capture_interval']}s)")
            
            while not self.stop_monitoring.is_set():
                try:
                    # Ejecutar análisis en el loop de eventos principal
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    context = loop.run_until_complete(self.analyze_screen_context())
                    loop.close()
                    
                    if context:
                        logger.debug(f"📊 Contexto actualizado: {len(context.applications)} apps")
                    
                except Exception as e:
                    logger.error(f"❌ Error en monitoreo continuo: {e}")
                
                # Esperar intervalo o hasta que se solicite parar
                self.stop_monitoring.wait(self.analysis_config['capture_interval'])
        
        # Iniciar thread de monitoreo
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ Monitoreo continuo iniciado")
    
    async def stop_continuous_monitoring(self):
        """Detiene el monitoreo continuo"""
        if not self.is_monitoring:
            return
        
        logger.info("🛑 Deteniendo monitoreo continuo...")
        
        self.stop_monitoring.set()
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("✅ Monitoreo continuo detenido")
    
    def get_current_context(self) -> Optional[ScreenContext]:
        """Obtiene el contexto actual"""
        return self.current_context
    
    def get_context_history(self) -> List[ScreenContext]:
        """Obtiene el historial de contextos"""
        return self.context_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de análisis"""
        return self.stats.copy()
    
    def update_config(self, config: Dict[str, Any]):
        """Actualiza configuración de análisis"""
        self.analysis_config.update(config)
        logger.info(f"⚙️ Configuración actualizada: {config}")
    
    async def get_application_context(self) -> Dict[str, Any]:
        """Obtiene contexto específico de aplicaciones para IA"""
        if not self.current_context:
            await self.analyze_screen_context()
        
        if not self.current_context:
            return {}
        
        context = self.current_context
        
        return {
            'open_applications': [app.name for app in context.applications],
            'active_window': context.active_window.title if context.active_window else None,
            'active_application': context.active_window.process_name if context.active_window else None,
            'window_count': len(context.visible_windows),
            'workspace_type': context.content_analysis.get('workspace_type', 'general'),
            'multitasking_level': context.content_analysis.get('multitasking_level', 'low'),
            'desktop_state': context.desktop_state,
            'app_categories': context.content_analysis.get('app_categories', {}),
            'focus_suggestions': context.content_analysis.get('focus_suggestions', [])
        }
    
    async def detect_ui_elements(self) -> List[Dict[str, Any]]:
        """Detecta elementos UI para IA"""
        if not self.current_context:
            await self.analyze_screen_context()
        
        if not self.current_context:
            return []
        
        elements = []
        for ui_element in self.current_context.ui_elements:
            elements.append({
                'type': ui_element.type,
                'text': ui_element.text,
                'position': ui_element.rect,
                'confidence': ui_element.confidence,
                'properties': ui_element.properties
            })
        
        return elements
    
    async def cleanup(self):
        """Limpia recursos del sistema de visión"""
        await self.stop_continuous_monitoring()
        
        self.current_context = None
        self.context_history.clear()
        
        logger.info("🧹 Vision Local limpiado")

# Ejemplo de uso
if __name__ == "__main__":
    async def test_vision_local():
        """Función de prueba"""
        vision = VisionLocal()
        
        try:
            # Inicializar
            if not await vision.initialize():
                print("❌ No se pudo inicializar Vision Local")
                return
            
            # Análisis único
            print("👁️ Analizando contexto de pantalla...")
            context = await vision.analyze_screen_context()
            
            if context:
                print(f"✅ Contexto analizado:")
                print(f"  Ventana activa: {context.active_window.title if context.active_window else 'Ninguna'}")
                print(f"  Ventanas visibles: {len(context.visible_windows)}")
                print(f"  Aplicaciones: {len(context.applications)}")
                print(f"  Elementos UI: {len(context.ui_elements)}")
                print(f"  Tipo de workspace: {context.content_analysis.get('workspace_type', 'N/A')}")
                
                print(f"\n📱 Aplicaciones detectadas:")
                for app in context.applications[:5]:  # Mostrar solo las primeras 5
                    status = "🟢 ACTIVA" if app.is_active else "⚪ Inactiva"
                    print(f"  {status} {app.name} (CPU: {app.cpu_usage:.1f}%, RAM: {app.memory_usage:.1f}MB)")
            
            # Obtener contexto para IA
            print(f"\n🤖 Contexto para IA:")
            ai_context = await vision.get_application_context()
            print(f"  Aplicaciones abiertas: {len(ai_context.get('open_applications', []))}")
            print(f"  Ventana activa: {ai_context.get('active_window', 'N/A')}")
            print(f"  Tipo de workspace: {ai_context.get('workspace_type', 'N/A')}")
            
            # Mostrar estadísticas
            stats = vision.get_stats()
            print(f"\n📊 Estadísticas:")
            print(f"  Contextos analizados: {stats['contexts_analyzed']}")
            print(f"  Ventanas detectadas: {stats['windows_detected']}")
            print(f"  Tiempo promedio: {stats['average_analysis_time']:.3f}s")
            
        finally:
            await vision.cleanup()
    
    # Ejecutar prueba
    asyncio.run(test_vision_local())

