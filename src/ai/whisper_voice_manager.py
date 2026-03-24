"""
WhisperVoiceManager - Reconocimiento de voz usando OpenAI Whisper
Mejor precisión en español que Vosk.
"""
import os
import queue
import threading
import numpy as np
from typing import Optional, Callable
from loguru import logger

# Lazy imports
whisper = None
sounddevice = None


def _ensure_whisper():
    """Carga Whisper de forma lazy."""
    global whisper
    if whisper is None:
        try:
            import whisper as _whisper
            whisper = _whisper
        except ImportError:
            logger.error("Whisper no está instalado. Ejecuta: pip install openai-whisper")
            raise


def _ensure_sounddevice():
    """Carga sounddevice de forma lazy."""
    global sounddevice
    if sounddevice is None:
        try:
            import sounddevice as _sd
            sounddevice = _sd
        except ImportError:
            logger.error("sounddevice no está instalado. Ejecuta: pip install sounddevice")
            raise


class WhisperVoiceManager:
    """
    Manager de voz usando OpenAI Whisper para transcripción offline.
    Soporta comandos en español con alta precisión.
    """
    
    SAMPLE_RATE = 16000
    BLOCK_DURATION = 3  # Segundos por bloque de audio
    
    def __init__(self, model_name: str = "small", language: str = "es"):
        """
        Args:
            model_name: Modelo de Whisper (tiny, base, small, medium, large)
            language: Código de idioma (es, en, etc.)
        """
        self._model_name = model_name
        self._language = language
        self._model = None
        self._audio_queue = queue.Queue()
        self._running = False
        self._thread = None
        self._callback: Optional[Callable[[str], None]] = None
        self._audio_buffer = []
        self._buffer_duration = 0
    
    def start(self, on_transcript: Optional[Callable[[str], None]] = None):
        """Inicia el reconocimiento de voz."""
        _ensure_whisper()
        _ensure_sounddevice()
        
        self._callback = on_transcript
        
        # Cargar modelo
        logger.info(f"Cargando modelo Whisper '{self._model_name}'...")
        self._model = whisper.load_model(self._model_name)
        logger.success(f"Modelo Whisper cargado.")
        
        self._running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        
        # Iniciar stream de audio
        self._start_audio_stream()
        
        logger.info("WhisperVoiceManager iniciado.")
    
    def stop(self):
        """Detiene el reconocimiento."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("WhisperVoiceManager detenido.")
    
    def _start_audio_stream(self):
        """Inicia captura de audio."""
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            self._audio_queue.put(indata.copy())
        
        try:
            self._stream = sounddevice.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=1,
                dtype='float32',
                callback=audio_callback,
                blocksize=int(self.SAMPLE_RATE * 0.1)  # 100ms blocks
            )
            self._stream.start()
        except Exception as e:
            logger.error(f"Error al iniciar stream de audio: {e}")
    
    def _process_loop(self):
        """Loop de procesamiento de audio."""
        while self._running:
            try:
                # Acumular audio
                audio_chunk = self._audio_queue.get(timeout=0.5)
                self._audio_buffer.append(audio_chunk)
                self._buffer_duration += len(audio_chunk) / self.SAMPLE_RATE
                
                # Procesar cuando tengamos suficiente audio
                if self._buffer_duration >= self.BLOCK_DURATION:
                    self._process_buffer()
                    
            except queue.Empty:
                # Procesar buffer restante si hay silencio
                if self._buffer_duration > 1.0:
                    self._process_buffer()
    
    def _process_buffer(self):
        """Procesa el buffer de audio acumulado."""
        if not self._audio_buffer:
            return
        
        # Concatenar audio
        audio = np.concatenate(self._audio_buffer, axis=0).flatten()
        self._audio_buffer = []
        self._buffer_duration = 0
        
        # Transcribir
        try:
            result = self._model.transcribe(
                audio,
                language=self._language,
                fp16=False,  # CPU-friendly
                task="transcribe"
            )
            
            text = result["text"].strip()
            
            if text and len(text) > 2:
                logger.info(f"Whisper: '{text}'")
                
                if self._callback:
                    self._callback(text)
                    
        except Exception as e:
            logger.error(f"Error en transcripción: {e}")
    
    def set_callback(self, callback: Callable[[str], None]):
        """Establece callback para transcripciones."""
        self._callback = callback
