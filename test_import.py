import sys
from pathlib import Path

# Add 'src' to path
src_path = Path("src").absolute()
sys.path.append(str(src_path))
print(f"Added to path: {src_path}")

try:
    from tracking.tracking_manager import TrackingManager
    print("Successfully imported TrackingManager")
    tm = TrackingManager()
    print("Successfully initialized TrackingManager")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
