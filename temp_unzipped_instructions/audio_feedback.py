"""
Sistema de Audio Feedback JARVIS para Slap!Faast v2.0
Sonidos y respuestas de voz estilo Tony Stark / Iron Man
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
import threading
import queue
import wave
import numpy as np
import pygame
import pyttsx3

logger = logging.getLogger(__name__)

class AudioEventType(Enum):
    """Tipos de eventos de audio"""
    COMMAND_RECEIVED = "command_received"
    COMMAND_PROCESSING = "command_processing"
    COMMAND_EXECUTED = "command_executed"
    COMMAND_FAILED = "command_failed"
    SYSTEM_READY = "system_ready"
    SYSTEM_ERROR = "system_error"
    GESTURE_DETECTED = "gesture_detected"
    VOICE_DETECTED = "voice_detected"
    AI_RESPONSE = "ai_response"
    CONFIRMATION_REQUEST = "confirmation_request"
    NOTIFICATION = "notification"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"

@dataclass
class AudioConfig:
    """Configuración de audio"""
    enable_sound_effects: bool = True
    enable_voice_feedback: bool = True
    master_volume: float = 0.7
    effects_volume: float = 0.8
    voice_volume: float = 0.9
    voice_rate: int = 180  # palabras por minuto
    voice_language: str = "es"
    voice_gender: str = "male"  # male, female
    sound_theme: str = "iron_man"  # iron_man, minimal, classic

@dataclass
class SoundEffect:
    """Efecto de sonido"""
    name: str
    file_path: Optional[str]
    duration: float
    volume: float
    loop: bool = False
    generated: bool = False  # Si es generado sintéticamente

class JarvisAudioFeedback:
    """Sistema de audio feedback estilo JARVIS"""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        
        # Estado del sistema
        self.is_initialized = False
        self.is_enabled = True
        
        # Componentes de audio
        self.pygame_mixer = None
        self.tts_engine = None
        
        # Efectos de sonido
        self.sound_effects = {}
        self.sound_queue = queue.Queue()
        
        # Threading para audio
        self.audio_thread = None
        self.stop_audio = threading.Event()
        
        # Cache de audio generado
        self.generated_sounds = {}
        self.voice_cache = {}
        
        # Configuración de sonidos Iron Man
        self.iron_man_sounds = {
            AudioEventType.COMMAND_RECEIVED: {
                'frequency': 800,
                'duration': 0.2,
                'wave_type': 'sine',
                'envelope': 'quick_fade'
            },
            AudioEventType.COMMAND_PROCESSING: {
                'frequency': 600,
                'duration': 0.5,
                'wave_type': 'pulse',
                'envelope': 'sustained'
            },
            AudioEventType.COMMAND_EXECUTED: {
                'frequency': 1000,
                'duration': 0.3,
                'wave_type': 'triangle',
                'envelope': 'success'
            },
            AudioEventType.COMMAND_FAILED: {
                'frequency': 300,
                'duration': 0.8,
                'wave_type': 'sawtooth',
                'envelope': 'error'
            },
            AudioEventType.SYSTEM_READY: {
                'frequency': [400, 800, 1200],
                'duration': 1.0,
                'wave_type': 'chord',
                'envelope': 'startup'
            },
            AudioEventType.GESTURE_DETECTED: {
                'frequency': 1200,
                'duration': 0.15,
                'wave_type': 'sine',
                'envelope': 'quick'
            },
            AudioEventType.VOICE_DETECTED: {
                'frequency': 900,
                'duration': 0.25,
                'wave_type': 'sine',
                'envelope': 'voice_start'
            }
        }
        
        # Frases JARVIS
        self.jarvis_phrases = {
            'startup': [
                "Sistemas en línea, señor.",
                "JARVIS activado y listo para asistir.",
                "Todos los sistemas funcionando correctamente."
            ],
            'command_received': [
                "Comando recibido.",
                "Procesando solicitud.",
                "Entendido, señor."
            ],
            'command_executed': [
                "Comando ejecutado exitosamente.",
                "Tarea completada.",
                "Hecho, señor."
            ],
            'command_failed': [
                "No pude completar esa tarea.",
                "Ha ocurrido un error, señor.",
                "Comando no ejecutado."
            ],
            'gesture_detected': [
                "Gesto detectado.",
                "Movimiento reconocido.",
                "Señal recibida."
            ],
            'system_ready': [
                "Sistema listo para comandos.",
                "Esperando instrucciones.",
                "A su servicio, señor."
            ],
            'confirmation': [
                "¿Confirma la acción?",
                "¿Procedo con la operación?",
                "¿Desea continuar?"
            ]
        }
        
        # Estadísticas
        self.stats = {
            'sounds_played': 0,
            'voice_responses': 0,
            'total_audio_time': 0.0,
            'cache_hits': 0,
            'generation_time': 0.0
        }
    
    async def initialize(self) -> bool:
        """Inicializa el sistema de audio"""
        try:
            logger.info("🔊 Inicializando sistema de audio JARVIS...")
            
            # Inicializar pygame mixer
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.pygame_mixer = pygame.mixer
            
            # Inicializar TTS
            self.tts_engine = pyttsx3.init()
            self._configure_tts()
            
            # Generar efectos de sonido
            await self._generate_sound_effects()
            
            # Iniciar thread de audio
            self._start_audio_thread()
            
            self.is_initialized = True
            logger.info("✅ Sistema de audio JARVIS inicializado")
            
            # Reproducir sonido de inicio
            await self.play_audio_event(AudioEventType.STARTUP)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando audio JARVIS: {e}")
            return False
    
    def _configure_tts(self):
        """Configura el motor de text-to-speech"""
        if not self.tts_engine:
            return
        
        try:
            # Configurar velocidad
            self.tts_engine.setProperty('rate', self.config.voice_rate)
            
            # Configurar volumen
            self.tts_engine.setProperty('volume', self.config.voice_volume)
            
            # Configurar voz (intentar encontrar voz en español)
            voices = self.tts_engine.getProperty('voices')
            
            target_voice = None
            for voice in voices:
                voice_id = voice.id.lower()
                
                # Buscar voz en español
                if 'spanish' in voice_id or 'es' in voice_id:
                    if self.config.voice_gender == 'male' and 'male' in voice_id:
                        target_voice = voice.id
                        break
                    elif self.config.voice_gender == 'female' and 'female' in voice_id:
                        target_voice = voice.id
                        break
                    elif not target_voice:  # Cualquier voz en español
                        target_voice = voice.id
            
            if target_voice:
                self.tts_engine.setProperty('voice', target_voice)
                logger.info(f"🗣️ Voz configurada: {target_voice}")
            else:
                logger.warning("⚠️ No se encontró voz en español, usando voz por defecto")
                
        except Exception as e:
            logger.error(f"❌ Error configurando TTS: {e}")
    
    async def _generate_sound_effects(self):
        """Genera efectos de sonido sintéticos estilo Iron Man"""
        logger.info("🎵 Generando efectos de sonido Iron Man...")
        
        sample_rate = 44100
        
        for event_type, sound_config in self.iron_man_sounds.items():
            try:
                audio_data = self._generate_synthetic_sound(sound_config, sample_rate)
                
                # Convertir a formato pygame
                sound_array = (audio_data * 32767).astype(np.int16)
                sound_stereo = np.column_stack((sound_array, sound_array))
                
                # Crear surface de pygame
                sound = pygame.sndarray.make_sound(sound_stereo)
                
                self.sound_effects[event_type] = sound
                
                logger.debug(f"🎵 Sonido generado: {event_type.value}")
                
            except Exception as e:
                logger.error(f"❌ Error generando sonido {event_type.value}: {e}")
        
        logger.info(f"✅ {len(self.sound_effects)} efectos de sonido generados")
    
    def _generate_synthetic_sound(self, config: Dict, sample_rate: int) -> np.ndarray:
        """Genera sonido sintético basado en configuración"""
        duration = config['duration']
        samples = int(sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Generar onda base
        if config['wave_type'] == 'sine':
            wave = np.sin(2 * np.pi * config['frequency'] * t)
        elif config['wave_type'] == 'triangle':
            wave = 2 * np.arcsin(np.sin(2 * np.pi * config['frequency'] * t)) / np.pi
        elif config['wave_type'] == 'sawtooth':
            wave = 2 * (t * config['frequency'] - np.floor(t * config['frequency'] + 0.5))
        elif config['wave_type'] == 'pulse':
            wave = np.sign(np.sin(2 * np.pi * config['frequency'] * t))
        elif config['wave_type'] == 'chord':
            # Acorde de múltiples frecuencias
            wave = np.zeros_like(t)
            for freq in config['frequency']:
                wave += np.sin(2 * np.pi * freq * t) / len(config['frequency'])
        else:
            wave = np.sin(2 * np.pi * config['frequency'] * t)
        
        # Aplicar envolvente
        envelope = self._generate_envelope(config['envelope'], samples)
        wave = wave * envelope
        
        # Añadir efectos Iron Man
        wave = self._apply_iron_man_effects(wave, config)
        
        # Normalizar
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave))
        
        return wave * 0.7  # Volumen base
    
    def _generate_envelope(self, envelope_type: str, samples: int) -> np.ndarray:
        """Genera envolvente de amplitud"""
        t = np.linspace(0, 1, samples)
        
        if envelope_type == 'quick_fade':
            return np.exp(-t * 8)
        elif envelope_type == 'sustained':
            return np.ones_like(t) * 0.8
        elif envelope_type == 'success':
            return np.exp(-t * 3) * (1 + 0.3 * np.sin(t * 20))
        elif envelope_type == 'error':
            return np.exp(-t * 2) * (1 + 0.5 * np.sin(t * 10))
        elif envelope_type == 'startup':
            return np.minimum(t * 4, 1) * np.exp(-t * 1.5)
        elif envelope_type == 'quick':
            return np.exp(-t * 12)
        elif envelope_type == 'voice_start':
            return np.exp(-t * 6) * (1 + 0.2 * np.sin(t * 30))
        else:
            return np.ones_like(t)
    
    def _apply_iron_man_effects(self, wave: np.ndarray, config: Dict) -> np.ndarray:
        """Aplica efectos específicos de Iron Man"""
        # Añadir ligero reverb digital
        delay_samples = int(len(wave) * 0.1)
        if delay_samples > 0 and delay_samples < len(wave):
            delayed = np.zeros_like(wave)
            delayed[delay_samples:] = wave[:-delay_samples] * 0.3
            wave = wave + delayed
        
        # Añadir modulación sutil para efecto futurista
        t = np.linspace(0, 1, len(wave))
        modulation = 1 + 0.05 * np.sin(t * 50)
        wave = wave * modulation
        
        # Filtro paso alto sutil para claridad
        if len(wave) > 100:
            # Filtro simple de diferencias
            filtered = np.diff(wave, prepend=wave[0])
            wave = 0.7 * wave + 0.3 * filtered
        
        return wave
    
    def _start_audio_thread(self):
        """Inicia thread para procesamiento de audio"""
        def audio_worker():
            logger.info("🎵 Thread de audio iniciado")
            
            while not self.stop_audio.is_set():
                try:
                    # Procesar cola de audio
                    try:
                        audio_task = self.sound_queue.get(timeout=0.1)
                        self._process_audio_task(audio_task)
                        self.sound_queue.task_done()
                    except queue.Empty:
                        continue
                        
                except Exception as e:
                    logger.error(f"❌ Error en thread de audio: {e}")
            
            logger.info("🎵 Thread de audio detenido")
        
        self.audio_thread = threading.Thread(target=audio_worker, daemon=True)
        self.audio_thread.start()
    
    def _process_audio_task(self, task: Dict[str, Any]):
        """Procesa tarea de audio"""
        task_type = task.get('type')
        
        if task_type == 'play_sound':
            self._play_sound_effect(task['event_type'])
        elif task_type == 'speak_text':
            self._speak_text_sync(task['text'])
        elif task_type == 'play_sequence':
            self._play_sound_sequence(task['sequence'])
    
    def _play_sound_effect(self, event_type: AudioEventType):
        """Reproduce efecto de sonido"""
        if not self.config.enable_sound_effects or not self.is_enabled:
            return
        
        try:
            if event_type in self.sound_effects:
                sound = self.sound_effects[event_type]
                sound.set_volume(self.config.effects_volume * self.config.master_volume)
                sound.play()
                
                self.stats['sounds_played'] += 1
                logger.debug(f"🔊 Sonido reproducido: {event_type.value}")
            else:
                logger.warning(f"⚠️ Sonido no encontrado: {event_type.value}")
                
        except Exception as e:
            logger.error(f"❌ Error reproduciendo sonido {event_type.value}: {e}")
    
    def _speak_text_sync(self, text: str):
        """Reproduce texto con TTS (síncrono)"""
        if not self.config.enable_voice_feedback or not self.is_enabled or not self.tts_engine:
            return
        
        try:
            # Verificar cache
            cache_key = f"{text}_{self.config.voice_rate}_{self.config.voice_language}"
            
            if cache_key in self.voice_cache:
                self.stats['cache_hits'] += 1
                logger.debug(f"🗣️ Usando cache para: {text[:30]}...")
            
            # Reproducir con TTS
            start_time = time.time()
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            duration = time.time() - start_time
            self.stats['voice_responses'] += 1
            self.stats['total_audio_time'] += duration
            
            logger.debug(f"🗣️ Texto reproducido: {text[:30]}... ({duration:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo texto: {e}")
    
    async def play_audio_event(self, event_type: AudioEventType, 
                             custom_text: Optional[str] = None,
                             include_voice: bool = True) -> bool:
        """Reproduce evento de audio completo"""
        if not self.is_initialized or not self.is_enabled:
            return False
        
        try:
            # Reproducir efecto de sonido
            if self.config.enable_sound_effects:
                task = {
                    'type': 'play_sound',
                    'event_type': event_type
                }
                self.sound_queue.put(task)
            
            # Reproducir voz si está habilitada
            if include_voice and self.config.enable_voice_feedback:
                text = custom_text or self._get_jarvis_phrase(event_type)
                if text:
                    # Pequeña pausa antes de la voz
                    await asyncio.sleep(0.2)
                    
                    task = {
                        'type': 'speak_text',
                        'text': text
                    }
                    self.sound_queue.put(task)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo evento {event_type.value}: {e}")
            return False
    
    def _get_jarvis_phrase(self, event_type: AudioEventType) -> Optional[str]:
        """Obtiene frase JARVIS para evento"""
        event_key = event_type.value
        
        # Mapear eventos a categorías de frases
        phrase_mapping = {
            'system_ready': 'system_ready',
            'startup': 'startup',
            'command_received': 'command_received',
            'command_executed': 'command_executed',
            'command_failed': 'command_failed',
            'gesture_detected': 'gesture_detected',
            'confirmation_request': 'confirmation'
        }
        
        phrase_category = phrase_mapping.get(event_key)
        if phrase_category and phrase_category in self.jarvis_phrases:
            phrases = self.jarvis_phrases[phrase_category]
            # Rotar frases para variedad
            import random
            return random.choice(phrases)
        
        return None
    
    async def speak_custom_text(self, text: str, priority: bool = False) -> bool:
        """Reproduce texto personalizado"""
        if not self.is_initialized or not self.is_enabled:
            return False
        
        try:
            task = {
                'type': 'speak_text',
                'text': text,
                'priority': priority
            }
            
            if priority:
                # Limpiar cola para mensajes prioritarios
                while not self.sound_queue.empty():
                    try:
                        self.sound_queue.get_nowait()
                    except queue.Empty:
                        break
            
            self.sound_queue.put(task)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo texto personalizado: {e}")
            return False
    
    async def play_command_sequence(self, command_type: str) -> bool:
        """Reproduce secuencia de audio para comando específico"""
        sequences = {
            'voice_command': [
                (AudioEventType.VOICE_DETECTED, None),
                (AudioEventType.COMMAND_PROCESSING, "Procesando comando de voz"),
                (AudioEventType.COMMAND_EXECUTED, "Comando ejecutado")
            ],
            'gesture_command': [
                (AudioEventType.GESTURE_DETECTED, None),
                (AudioEventType.COMMAND_PROCESSING, "Analizando gesto"),
                (AudioEventType.COMMAND_EXECUTED, "Gesto reconocido")
            ],
            'multimodal_command': [
                (AudioEventType.COMMAND_RECEIVED, None),
                (AudioEventType.COMMAND_PROCESSING, "Fusionando datos multimodales"),
                (AudioEventType.COMMAND_EXECUTED, "Comando multimodal ejecutado")
            ]
        }
        
        if command_type not in sequences:
            return False
        
        try:
            sequence = sequences[command_type]
            
            for event_type, custom_text in sequence:
                await self.play_audio_event(event_type, custom_text)
                await asyncio.sleep(0.5)  # Pausa entre eventos
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reproduciendo secuencia {command_type}: {e}")
            return False
    
    def set_enabled(self, enabled: bool):
        """Habilita/deshabilita sistema de audio"""
        self.is_enabled = enabled
        logger.info(f"🔊 Audio {'habilitado' if enabled else 'deshabilitado'}")
    
    def update_config(self, config: Dict[str, Any]):
        """Actualiza configuración de audio"""
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Reconfigurar TTS si es necesario
        if any(key in config for key in ['voice_rate', 'voice_volume', 'voice_language']):
            self._configure_tts()
        
        logger.info(f"🔊 Configuración de audio actualizada: {config}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de audio"""
        return self.stats.copy()
    
    async def cleanup(self):
        """Limpia recursos de audio"""
        logger.info("🧹 Limpiando sistema de audio...")
        
        # Detener thread de audio
        self.stop_audio.set()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
        
        # Limpiar pygame
        if self.pygame_mixer:
            pygame.mixer.quit()
        
        # Limpiar TTS
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        # Limpiar cache
        self.sound_effects.clear()
        self.voice_cache.clear()
        
        self.is_initialized = False
        logger.info("✅ Sistema de audio limpiado")

# Ejemplo de uso
if __name__ == "__main__":
    async def test_jarvis_audio():
        """Función de prueba"""
        config = AudioConfig(
            enable_sound_effects=True,
            enable_voice_feedback=True,
            master_volume=0.8
        )
        
        jarvis = JarvisAudioFeedback(config)
        
        try:
            # Inicializar
            if not await jarvis.initialize():
                print("❌ No se pudo inicializar audio JARVIS")
                return
            
            print("🔊 Sistema JARVIS inicializado")
            
            # Probar eventos
            events_to_test = [
                AudioEventType.SYSTEM_READY,
                AudioEventType.COMMAND_RECEIVED,
                AudioEventType.GESTURE_DETECTED,
                AudioEventType.COMMAND_EXECUTED
            ]
            
            for event in events_to_test:
                print(f"🎵 Reproduciendo: {event.value}")
                await jarvis.play_audio_event(event)
                await asyncio.sleep(2)
            
            # Probar texto personalizado
            await jarvis.speak_custom_text("Sistema Tony Stark completamente operativo, señor.")
            await asyncio.sleep(3)
            
            # Probar secuencia
            await jarvis.play_command_sequence('multimodal_command')
            
            # Mostrar estadísticas
            stats = jarvis.get_stats()
            print(f"\n📊 Estadísticas:")
            print(f"  Sonidos reproducidos: {stats['sounds_played']}")
            print(f"  Respuestas de voz: {stats['voice_responses']}")
            print(f"  Tiempo total de audio: {stats['total_audio_time']:.2f}s")
            
        finally:
            await jarvis.cleanup()
    
    # Ejecutar prueba
    asyncio.run(test_jarvis_audio())

