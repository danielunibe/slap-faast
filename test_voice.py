import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

from ai.voice_manager import VoiceManager
from core.events import EventBus, Events

def on_voice_command(text):
    print(f"\n[VOICE TEST] Detected: '{text}'")

def main():
    print("--- Voice Recognition Test ---")
    
    # Subscribe to voice events
    EventBus.subscribe(Events.VOICE_COMMAND, on_voice_command)
    
    vm = VoiceManager(model_path="models/model")
    vm.start()
    
    if not vm._is_running:
        print("Error: VoiceManager failed to start.")
        return

    print("Listening... (Speak now, or wait 10 seconds to finish)")
    start_time = time.time()
    try:
        while time.time() - start_time < 10:
            vm.process_audio()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        vm.stop()
        print("\nTest finished.")

if __name__ == "__main__":
    main()
