from loguru import logger
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    logger.warning("pycaw no instalado. Control multimedia limitado.")

class MediaController:
    """Controlador de audio y medios usando pycaw."""
    
    def __init__(self):
        self._volume_interface = None
        if PYCAW_AVAILABLE:
            self._initialize_volume()

    def _initialize_volume(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.error(f"Error inicializando control de volumen: {e}")

    def is_audio_playing(self) -> bool:
        """Retorna True si alguna aplicación está usando el audio."""
        if not PYCAW_AVAILABLE: 
            return False
            
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.State == 1: # 1 = AudioSessionStateActive
                    return True
            return False
        except Exception:
            return False

    def get_master_volume(self) -> int:
        """Retorna volumen actual (0-100)."""
        if self._volume_interface:
            return int(round(self._volume_interface.GetMasterVolumeLevelScalar() * 100))
        return 0

    def set_master_volume(self, volume: int):
        """Establece volumen (0-100)."""
        if self._volume_interface:
            val = max(0, min(100, volume)) / 100.0
            self._volume_interface.SetMasterVolumeLevelScalar(val, None)

    def change_volume(self, delta: int):
        """Sube o baja volumen relativo."""
        current = self.get_master_volume()
        self.set_master_volume(current + delta)
