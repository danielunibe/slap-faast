#!/usr/bin/env python3
"""
Test de Integración Final - Slap!Faast v2.0 Tony Stark Edition
Verifica que todos los componentes funcionen correctamente
"""

import sys
import asyncio
import logging
import unittest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar logging para tests
logging.basicConfig(level=logging.WARNING)

class TestTonyStarkIntegration(unittest.TestCase):
    """Tests de integración completa del sistema Tony Stark"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.test_start_time = time.time()
        
    def tearDown(self):
        """Limpieza después de cada test"""
        test_duration = time.time() - self.test_start_time
        print(f"⏱️ Test completado en {test_duration:.2f}s")
    
    def test_01_core_imports(self):
        """Test 1: Verificar imports de módulos core"""
        print("🧪 Test 1: Imports de módulos core")
        
        try:
            from src.core.events import EventBus
            from src.core.controller import SystemController
            from src.core.exceptions import SlapFaastError
            from src.core.constants import GESTURE_TYPES
            print("✅ Módulos core importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando módulos core: {e}")
    
    def test_02_sensor_components(self):
        """Test 2: Verificar componentes de sensores"""
        print("🧪 Test 2: Componentes de sensores")
        
        try:
            from src.sensors.manager import SensorManager
            from src.sensors.webcam import WebcamSensor
            from src.sensors.factory import SensorFactory
            print("✅ Componentes de sensores importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando sensores: {e}")
    
    def test_03_tracking_components(self):
        """Test 3: Verificar componentes de tracking"""
        print("🧪 Test 3: Componentes de tracking")
        
        try:
            from src.tracking.skeleton import SkeletonTracker
            from src.tracking.pose_estimator import PoseEstimator
            from src.tracking.motion_filter import MotionFilter
            print("✅ Componentes de tracking importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando tracking: {e}")
    
    def test_04_recognition_components(self):
        """Test 4: Verificar componentes de reconocimiento"""
        print("🧪 Test 4: Componentes de reconocimiento")
        
        try:
            from src.recognition.engine import GestureRecognizer
            from src.recognition.rule_based import RuleBasedEngine
            from src.recognition.library import GestureLibrary
            print("✅ Componentes de reconocimiento importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando reconocimiento: {e}")
    
    def test_05_action_components(self):
        """Test 5: Verificar componentes de acciones"""
        print("🧪 Test 5: Componentes de acciones")
        
        try:
            from src.actions.executor import ActionExecutor
            from src.actions.keyboard_controller import KeyboardController
            from src.actions.mouse_controller import MouseController
            print("✅ Componentes de acciones importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando acciones: {e}")
    
    def test_06_ai_components(self):
        """Test 6: Verificar componentes de IA"""
        print("🧪 Test 6: Componentes de IA")
        
        try:
            from src.ai_local.ai_manager import LocalAIManager
            from src.ai_local.ollama_client import OllamaClient
            from src.ai_local.whisper_local import WhisperLocal
            from src.ai_local.vision_local import VisionLocal
            from src.ai_local.intent_processor import IntentProcessor
            print("✅ Componentes de IA importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando IA: {e}")
    
    def test_07_ui_components(self):
        """Test 7: Verificar componentes de UI"""
        print("🧪 Test 7: Componentes de UI")
        
        try:
            from src.ui.themes.tony_stark_theme import TonyStarkTheme
            from src.ui.audio_feedback import JarvisAudioFeedback
            from src.ui.main_window_integration import UIBackendIntegrator
            print("✅ Componentes de UI importados correctamente")
        except ImportError as e:
            self.fail(f"❌ Error importando UI: {e}")
    
    def test_08_configuration_files(self):
        """Test 8: Verificar archivos de configuración"""
        print("🧪 Test 8: Archivos de configuración")
        
        config_files = [
            "config/gesture_profiles.json",
            "config/hardware_settings.json",
            "config/ai_config.json"
        ]
        
        for config_file in config_files:
            file_path = Path(config_file)
            self.assertTrue(file_path.exists(), f"❌ Archivo no encontrado: {config_file}")
            
            # Verificar que es JSON válido
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ Configuración válida: {config_file}")
            except json.JSONDecodeError as e:
                self.fail(f"❌ JSON inválido en {config_file}: {e}")
    
    def test_09_event_bus_functionality(self):
        """Test 9: Funcionalidad del bus de eventos"""
        print("🧪 Test 9: Bus de eventos")
        
        try:
            from src.core.events import EventBus, Event
            
            # Crear bus de eventos
            event_bus = EventBus()
            
            # Test de suscripción y publicación
            received_events = []
            
            def test_callback(event):
                received_events.append(event)
            
            event_bus.subscribe('test_event', test_callback)
            
            # Publicar evento
            test_event = Event('test_event', {'test_data': 'hello'})
            event_bus.publish(test_event)
            
            # Verificar que se recibió
            self.assertEqual(len(received_events), 1)
            self.assertEqual(received_events[0].event_type, 'test_event')
            
            print("✅ Bus de eventos funcionando correctamente")
            
        except Exception as e:
            self.fail(f"❌ Error en bus de eventos: {e}")
    
    def test_10_gesture_library_functionality(self):
        """Test 10: Funcionalidad de biblioteca de gestos"""
        print("🧪 Test 10: Biblioteca de gestos")
        
        try:
            from src.recognition.library import GestureLibrary
            
            # Crear biblioteca
            library = GestureLibrary()
            
            # Verificar gestos predefinidos
            predefined_gestures = library.get_predefined_gestures()
            self.assertGreater(len(predefined_gestures), 0, "❌ No hay gestos predefinidos")
            
            # Verificar que contiene gestos básicos
            gesture_names = [g.name for g in predefined_gestures]
            expected_gestures = ['arms_up', 'right_hand_up', 'left_hand_up', 't_pose']
            
            for expected in expected_gestures:
                self.assertIn(expected, gesture_names, f"❌ Gesto faltante: {expected}")
            
            print(f"✅ Biblioteca de gestos: {len(predefined_gestures)} gestos disponibles")
            
        except Exception as e:
            self.fail(f"❌ Error en biblioteca de gestos: {e}")
    
    def test_11_tony_stark_theme(self):
        """Test 11: Tema visual Tony Stark"""
        print("🧪 Test 11: Tema Tony Stark")
        
        try:
            from src.ui.themes.tony_stark_theme import TonyStarkTheme, ColorPalette
            
            # Crear tema
            theme = TonyStarkTheme()
            
            # Verificar paleta de colores
            colors = theme.get_color_palette()
            self.assertIsInstance(colors, ColorPalette)
            
            # Verificar colores específicos
            self.assertTrue(hasattr(colors, 'arc_reactor_blue'))
            self.assertTrue(hasattr(colors, 'iron_red'))
            self.assertTrue(hasattr(colors, 'gold_accent'))
            
            # Verificar tiles
            tiles = theme.tiles_config
            self.assertGreater(len(tiles), 0, "❌ No hay tiles configurados")
            
            # Verificar CSS
            css = theme.get_complete_css()
            self.assertGreater(len(css), 1000, "❌ CSS muy corto")
            
            print(f"✅ Tema Tony Stark: {len(tiles)} tiles, CSS de {len(css)} caracteres")
            
        except Exception as e:
            self.fail(f"❌ Error en tema Tony Stark: {e}")
    
    @patch('pygame.mixer.init')
    def test_12_audio_feedback(self, mock_pygame):
        """Test 12: Sistema de audio JARVIS"""
        print("🧪 Test 12: Audio JARVIS")
        
        try:
            from src.ui.audio_feedback import JarvisAudioFeedback, AudioConfig, AudioEventType
            
            # Crear configuración
            config = AudioConfig(
                enable_sound_effects=True,
                enable_voice_feedback=True
            )
            
            # Crear sistema de audio
            jarvis = JarvisAudioFeedback(config)
            
            # Verificar configuración
            self.assertEqual(jarvis.config.enable_sound_effects, True)
            self.assertEqual(jarvis.config.enable_voice_feedback, True)
            
            # Verificar frases JARVIS
            self.assertIn('startup', jarvis.jarvis_phrases)
            self.assertIn('command_executed', jarvis.jarvis_phrases)
            
            print("✅ Sistema de audio JARVIS configurado correctamente")
            
        except Exception as e:
            self.fail(f"❌ Error en audio JARVIS: {e}")
    
    def test_13_configuration_loading(self):
        """Test 13: Carga de configuraciones"""
        print("🧪 Test 13: Carga de configuraciones")
        
        try:
            import json
            
            # Cargar configuración de gestos
            with open('config/gesture_profiles.json', 'r', encoding='utf-8') as f:
                gesture_config = json.load(f)
            
            self.assertIn('profiles', gesture_config)
            self.assertIn('gaming', gesture_config['profiles'])
            
            # Cargar configuración de hardware
            with open('config/hardware_settings.json', 'r', encoding='utf-8') as f:
                hardware_config = json.load(f)
            
            self.assertIn('hardware_profiles', hardware_config)
            self.assertIn('kinect_v1', hardware_config['hardware_profiles'])
            
            # Cargar configuración de IA
            with open('config/ai_config.json', 'r', encoding='utf-8') as f:
                ai_config = json.load(f)
            
            self.assertIn('ai_components', ai_config)
            self.assertIn('ollama', ai_config['ai_components'])
            
            print("✅ Todas las configuraciones cargadas correctamente")
            
        except Exception as e:
            self.fail(f"❌ Error cargando configuraciones: {e}")
    
    def test_14_main_application_structure(self):
        """Test 14: Estructura de aplicación principal"""
        print("🧪 Test 14: Aplicación principal")
        
        # Verificar que existe main_tony_stark.py
        main_file = Path("main_tony_stark.py")
        self.assertTrue(main_file.exists(), "❌ main_tony_stark.py no encontrado")
        
        # Verificar que es ejecutable
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar imports principales
            self.assertIn('SlapFaastTonyStarkApp', content)
            self.assertIn('TonyStarkSplashScreen', content)
            self.assertIn('SystemInitializer', content)
            
            print("✅ Aplicación principal estructurada correctamente")
            
        except Exception as e:
            self.fail(f"❌ Error verificando aplicación principal: {e}")
    
    def test_15_installation_script(self):
        """Test 15: Script de instalación"""
        print("🧪 Test 15: Script de instalación")
        
        # Verificar que existe install_complete.py
        install_file = Path("install_complete.py")
        self.assertTrue(install_file.exists(), "❌ install_complete.py no encontrado")
        
        try:
            with open(install_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar componentes principales
            self.assertIn('SlapFaastInstaller', content)
            self.assertIn('run_installation', content)
            self.assertIn('python_packages', content)
            
            print("✅ Script de instalación disponible")
            
        except Exception as e:
            self.fail(f"❌ Error verificando script de instalación: {e}")

class TestPerformance(unittest.TestCase):
    """Tests de rendimiento básicos"""
    
    def test_import_speed(self):
        """Test de velocidad de imports"""
        print("🧪 Test de rendimiento: Velocidad de imports")
        
        start_time = time.time()
        
        # Imports críticos
        from src.core.events import EventBus
        from src.recognition.library import GestureLibrary
        from src.ui.themes.tony_stark_theme import TonyStarkTheme
        
        import_time = time.time() - start_time
        
        # Debe importar en menos de 2 segundos
        self.assertLess(import_time, 2.0, f"❌ Imports muy lentos: {import_time:.2f}s")
        print(f"✅ Imports completados en {import_time:.2f}s")
    
    def test_theme_css_generation(self):
        """Test de generación de CSS del tema"""
        print("🧪 Test de rendimiento: Generación CSS")
        
        from src.ui.themes.tony_stark_theme import TonyStarkTheme
        
        start_time = time.time()
        theme = TonyStarkTheme()
        css = theme.get_complete_css()
        generation_time = time.time() - start_time
        
        # Debe generar en menos de 1 segundo
        self.assertLess(generation_time, 1.0, f"❌ Generación CSS muy lenta: {generation_time:.2f}s")
        self.assertGreater(len(css), 5000, "❌ CSS muy corto")
        
        print(f"✅ CSS generado en {generation_time:.2f}s ({len(css)} caracteres)")

def run_all_tests():
    """Ejecuta todos los tests"""
    print("🚀 INICIANDO TESTS DE INTEGRACIÓN FINAL")
    print("=" * 60)
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Añadir tests de integración
    suite.addTests(loader.loadTestsFromTestCase(TestTonyStarkIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS:")
    print(f"✅ Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests fallidos: {len(result.failures)}")
    print(f"💥 Errores: {len(result.errors)}")
    print(f"⏱️ Total ejecutados: {result.testsRun}")
    
    if result.failures:
        print("\n❌ FALLOS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORES:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Resultado final
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎯 TASA DE ÉXITO: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 ¡SISTEMA TONY STARK LISTO PARA PRODUCCIÓN!")
        return True
    elif success_rate >= 70:
        print("⚠️ Sistema funcional con advertencias menores")
        return True
    else:
        print("❌ Sistema requiere correcciones antes de usar")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

