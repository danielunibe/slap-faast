import mediapipe as mp
try:
    import mediapipe.python.solutions as solutions
    mp.solutions = solutions
    print(f"Solutions: {mp.solutions}")
    print(f"Holistic: {mp.solutions.holistic}")
except Exception as e:
    print(f"Error: {e}")
