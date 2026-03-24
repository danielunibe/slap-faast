"""
Sistema Híbrido OpenCV + MediaPipe Tasks API
Versión actualizada para MediaPipe 0.10.x con Full Body & Face Tracking
"""
import cv2
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

# Import wrapper para MediaPipe Tasks
try:
    from .mediapipe_wrapper import MediaPipeWrapper
except ImportError:
    from mediapipe_wrapper import MediaPipeWrapper


class HybridTracker:
    """
    Tracker híbrido completo:
    - Hands (MediaPipe Tasks)
    - Pose (MediaPipe Tasks)
    - FaceMesh (MediaPipe Tasks)
    - OpenCV features (Backup)
    """
    
    def __init__(self):
        # MediaPipe wrapper
        self._mp_wrapper = MediaPipeWrapper()
        
        self._hands = None
        self._pose = None
        self._face_mesh = None
        
        # Inicializar modulos IA
        try:
            self._hands = self._mp_wrapper.create_hands(max_num_hands=2)
            logger.info("IA Hands: OK")
        except Exception as e: logger.warning(f"IA Hands Error: {e}")

        try:
            self._pose = self._mp_wrapper.create_pose()
            logger.info("IA Pose: OK")
        except Exception as e: logger.warning(f"IA Pose Error: {e}")
        
        try:
            self._face_mesh = self._mp_wrapper.create_face_mesh(max_num_faces=1)
            logger.info("IA FaceMesh: OK")
        except Exception as e: logger.warning(f"IA FaceMesh Error: {e}")
        
        # OpenCV Fallbacks
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Motion
        self.prev_frame = None
        
        # Configuration
        self.enable_hands = True
        self.enable_pose = True
        self.enable_face_mesh = True
        self.enable_opencv_face = False # Desactivado por defecto si tenemos FaceMesh
        self.enable_motion = False
        self.enable_edges = False
        
        logger.info("HybridTracker Full System Initialized")
    
    def process_frame(self, frame_rgb: np.ndarray) -> Dict:
        results = {
            'pose': None,
            'hands': [],
            'face_mesh': [],
            'opencv_faces': [],
            'motion_mask': None
        }
        
        # 1. Hands
        if self.enable_hands and self._hands:
            try:
                res = self._hands.process(frame_rgb)
                if res.multi_hand_landmarks:
                    results['hands'] = res.multi_hand_landmarks
            except: pass
            
        # 2. Pose
        if self.enable_pose and self._pose:
            try:
                res = self._pose.process(frame_rgb)
                if res.pose_landmarks:
                    results['pose'] = res.pose_landmarks
            except: pass
            
        # 3. Face Mesh
        if self.enable_face_mesh and self._face_mesh:
            try:
                res = self._face_mesh.process(frame_rgb)
                if res.multi_face_landmarks:
                    results['face_mesh'] = res.multi_face_landmarks
            except: pass

        # 4. OpenCV Face (Fallback)
        if self.enable_opencv_face:
            frame_gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(frame_gray, 1.1, 5, minSize=(30, 30))
            results['opencv_faces'] = faces

        return results
    
    def draw_results(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        h, w = frame.shape[:2]
        
        # Draw Pose
        if results['pose']:
            lm_list = results['pose'].landmark
            # Draw Points
            for lm in lm_list:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 3, (255, 255, 0), -1)
            
            # Simple Skeleton Connections
            connections = [
                (11, 12), (11, 13), (13, 15), (12, 14), (14, 16), # Arms
                (11, 23), (12, 24), (23, 24), # Torso
                (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30) # Legs
            ]
            for start, end in connections:
                if start < len(lm_list) and end < len(lm_list):
                    pt1 = (int(lm_list[start].x * w), int(lm_list[start].y * h))
                    pt2 = (int(lm_list[end].x * w), int(lm_list[end].y * h))
                    cv2.line(frame, pt1, pt2, (255, 255, 0), 2)

        # Draw Hands
        for hand in results['hands']:
            for lm in hand.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
            # Simplest connections
            wrist = hand.landmark[0]
            for finger_tip_idx in [4, 8, 12, 16, 20]:
                tip = hand.landmark[finger_tip_idx]
                pt1 = (int(wrist.x * w), int(wrist.y * h))
                pt2 = (int(tip.x * w), int(tip.y * h))
                cv2.line(frame, pt1, pt2, (0, 255, 0), 1)

        # Draw Face Mesh
        if results['face_mesh']:
            for face in results['face_mesh']:
                for lm in face.landmark:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # Draw tiny dots for mesh
                    cv2.circle(frame, (cx, cy), 1, (200, 200, 200), -1)

        # Draw OpenCV Faces
        for (x, y, fw, fh) in results['opencv_faces']:
            cv2.rectangle(frame, (x, y), (x+fw, y+fh), (255, 0, 0), 2)

        return frame
        
    def release(self):
        self._mp_wrapper.close_all()
        logger.info("HybridTracker released")

if __name__ == "__main__":
    # Test rápido
    tracker = HybridTracker()
    cap = cv2.VideoCapture(0)
    print("Testing Full Tracking... Press 'q' to quit.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = tracker.process_frame(rgb)
        out = tracker.draw_results(frame, res)
        cv2.imshow("Full Tracking", out)
        if cv2.waitKey(1) == ord('q'): break
    cap.release()
    cv2.destroyAllWindows()
