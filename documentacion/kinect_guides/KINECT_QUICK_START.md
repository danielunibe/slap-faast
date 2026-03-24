# Slap!Faast - Kinect Quick Start Guide

## 🚀 Ready-to-Use Components

### 1. Control Kinect Motor and LED

```python
from src.sensors.kinect_direct_driver import KinectDirectDriver

# Initialize
kinect = KinectDirectDriver()
kinect.initialize()

# Examples
kinect.set_tilt(20)      # Tilt camera up 20 degrees
kinect.set_tilt(-15)     # Tilt camera down 15 degrees
kinect.set_tilt(0)       # Center position

kinect.set_led(1)        # Green LED
kinect.set_led(2)        # Red LED
kinect.set_led(4)        # Blinking green

# Cleanup
kinect.shutdown()
```

### 2. Track Hands, Body, and Face

```python
from src.tracking.hybrid_tracker import HybridTracker
import cv2

tracker = HybridTracker()
tracker.start()

cap = cv2.VideoCapture(0)  # Webcam

while True:
    ret, frame = cap.read()
    results = tracker.process_frame(frame)
    
    # Use tracking data
    if results['hands']:
        print(f"Detected {len(results['hands'])} hand(s)")
    
    if results['pose']:
        print("Body detected")
    
    if results['face']:
        print("Face detected")
    
    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 3. Auto-Tracking Camera (Kinect Motorized!)

```python
"""
Use face detection to automatically move Kinect camera
"""
from src.sensors.kinect_direct_driver import KinectDirectDriver
from src.tracking.hybrid_tracker import HybridTracker
import cv2

kinect = KinectDirectDriver()
kinect.initialize()
kinect.set_led(1)  # Green = active

tracker = HybridTracker()
tracker.start()

cap = cv2.VideoCapture(0)
current_tilt = 0

while True:
    ret, frame = cap.read()
    results = tracker.process_frame(frame)
    
    # Auto-track face
    if results['face']:
        h, w = frame.shape[:2]
        # Get face Y position
        face_y = results['face'].bounding_box[1]
        
        # Calculate tilt adjustment
        center_y = h / 2
        offset = face_y - center_y
        
        # Adjust camera tilt
        if abs(offset) > 50:  # Dead zone
            adjustment = int(offset / 100)  # Scale
            current_tilt = max(-31, min(31, current_tilt + adjustment))
            kinect.set_tilt(current_tilt)
    
    cv2.imshow("Auto-Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kinect.set_tilt(0)  # Reset
kinect.shutdown()
```

## 📦 Required Dependencies

```bash
pip install pyusb opencv-python mediapipe loguru numpy
```

## ⚠️ Important Notes

- **Kinect Motor/LED**: Requires WinUSB driver on `Xbox NUI Motor` device
- **Video**: Currently using laptop webcam (Kinect video not functional)
- **Tracking**: Works with any camera source
- **LED Codes**: 0=Off, 1=Green, 2=Red, 3=Yellow, 4=Blink Green, 6=Blink Red/Yellow

## 🎯 What Works vs. What Doesn't

### ✅ Works 100%
- Kinect motor control (-31° to +31°)
- Kinect LED (6 color modes)
- Hand tracking (21 points per hand)
- Body tracking (33 skeleton points)
- Face tracking (468 mesh points)

### ❌ Doesn't Work
- Kinect video stream (use webcam instead)

## 🔧 Troubleshooting

**"Kinect Motor no encontrado"**:
- Check USB connection
- Verify WinUSB driver installed (use Zadig)

**"No tracking detected"**:
- Ensure good lighting
- Models downloaded to `src/models/`
- Camera has clear view

**Motor doesn't move**:
- Check angle is between -31 and 31
- Wait 1-2 seconds between commands
- Kinect needs USB power

## 📚 Full Documentation

See `walkthrough.md` for complete technical details, troubleshooting, and future development paths.
