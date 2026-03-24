import mediapipe
print(dir(mediapipe))
try:
    import mediapipe.solutions
    print("Imported mediapipe.solutions")
except ImportError as e:
    print(f"Failed mediapipe.solutions: {e}")
