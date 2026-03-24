import os
import json
import queue
import sounddevice as sd
from loguru import logger
from typing import Optional, List

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk no instalado. Control de voz deshabilitado.")

from ..core.events import EventBus, Events

class VoiceManager:
    """Gestor de reconocimiento de voz offline usando Vosk."""
    
    def __init__(self, model_path=None):
        if model_path is None:
            # Auto-detect relative path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self._model_path = os.path.join(base_dir, "src", "models", "vosk-model")
        else:
            self._model_path = model_path
            
        self._model = None
        self._recognizer = None
        self._stream = None
        self._queue = queue.Queue()
        self._is_running = False

    def start(self):
        if not VOSK_AVAILABLE:
            return

        if not os.path.exists(self._model_path):
            logger.error(f"Modelo de voz no encontrado en {self._model_path}")
            return

        try:
            logger.info("Cargando modelo de voz...")
            self._model = Model(self._model_path)
            self._recognizer = KaldiRecognizer(self._model, 16000)
            
            # Callback para el stream
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(status)
                self._queue.put(bytes(indata))

            self._stream = sd.RawInputStream(
                samplerate=16000, 
                blocksize=8000, 
                dtype='int16',
                channels=1, 
                callback=callback
            )
            self._stream.start()
            self._is_running = True
            logger.info("VoiceManager iniciado. Escuchando...")
            
        except Exception as e:
            logger.error(f"Error iniciando VoiceManager: {e}")

    def stop(self):
        self._is_running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
        logger.info("VoiceManager detenido.")

    def process_audio(self):
        """Procesa audio de la cola (llamar en el loop principal)."""
        if not self._is_running or self._queue.empty():
            return

        try:
            while not self._queue.empty():
                data = self._queue.get_nowait()
                if self._recognizer.AcceptWaveform(data):
                    result = json.loads(self._recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self._handle_command(text)
                else:
                    # Partial result (opcional: mostrar mientras habla)
                    # partial = json.loads(self._recognizer.PartialResult())
                    pass
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")

    def _handle_command(self, text: str):
        logger.info(f"Comando de voz detectado: '{text}'")
        EventBus.publish(Events.VOICE_COMMAND, text)
