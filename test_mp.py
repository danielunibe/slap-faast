import mediapipe as mp
print(f"MediaPipe version: {mp.__version__}")
try:
    print(f"Has solutions? {hasattr(mp, 'solutions')}")
    print(f"Solutions: {mp.solutions}")
    print(f"Holistic: {mp.solutions.holistic}")
except Exception as e:
    print(f"Error: {e}")
