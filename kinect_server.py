"""
Servidor Flask para Dashboard de Kinect
Conecta la interfaz web con el hardware real usando driver unificado libfreenect
"""
from flask import Flask, render_template, jsonify, Response
from flask_cors import CORS
from pathlib import Path
import ctypes
from ctypes import c_int, c_void_p, c_double, POINTER, byref, create_string_buffer, Structure, c_int16, c_int8
import numpy as np
import cv2
import threading
import time
import sys

# Add root to path just in case
sys.path.append(str(Path(__file__).parent))

try:
    from src.tracking.mediapipe_wrapper import MediaPipeWrapper
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI modules not found: {e}")
    AI_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for React Frontend

DLL_PATH = Path(__file__).parent / "freenect.dll"

# Definición de estructuras de ctypes
class FreenectRawTiltState(Structure):
    _fields_ = [
        ("accelerometer_x", c_int16),
        ("accelerometer_y", c_int16),
        ("accelerometer_z", c_int16),
        ("tilt_angle", c_int8),
        ("tilt_status", c_int) # enum
    ]

class KinectServer:
    def __init__(self):
        self.lib = None
        self.ctx = c_void_p()
        self.dev = c_void_p()
        
        self.video_buffer = None
        self.depth_buffer = None
        
        self.current_tilt = 0
        self.current_led = 1
        self.video_enabled = True
        self.depth_enabled = True
        self.current_colormap = 2  # JET
        
        self.latest_video_frame = None
        self.latest_depth_frame = None
        
        self.running = False
        self.thread = None
        self.mock_mode = False  # Modo simulación si no hay hardware
        
        # AI Tracking
        self.mp_wrapper = None
        self.hands_detector = None
        self.pose_detector = None
        
        if AI_AVAILABLE:
            try:
                self.mp_wrapper = MediaPipeWrapper()
                self.hands_detector = self.mp_wrapper.create_hands()
                self.pose_detector = self.mp_wrapper.create_pose()
                print("AI detectors initialized")
            except Exception as e:
                print(f"Failed to init AI detectors: {e}")
        else:
            print("AI not available")
        
    def init(self):
        """Inicializar Kinect usando SOLO libfreenect"""
        try:
            self.lib = ctypes.CDLL(str(DLL_PATH))
            
            # --- Configurar funciones libfreenect ---
            self.lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
            self.lib.freenect_init.restype = c_int
            
            self.lib.freenect_shutdown.argtypes = [c_void_p]
            self.lib.freenect_shutdown.restype = c_int
            
            self.lib.freenect_num_devices.argtypes = [c_void_p]
            self.lib.freenect_num_devices.restype = c_int
            
            self.lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
            self.lib.freenect_open_device.restype = c_int
            
            self.lib.freenect_close_device.argtypes = [c_void_p]
            self.lib.freenect_close_device.restype = c_int
            
            self.lib.freenect_select_subdevices.argtypes = [c_void_p, c_int]
            self.lib.freenect_select_subdevices.restype = None
            
            self.lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
            self.lib.freenect_set_video_buffer.restype = c_int
            
            self.lib.freenect_set_depth_buffer.argtypes = [c_void_p, c_void_p]
            self.lib.freenect_set_depth_buffer.restype = c_int
            
            self.lib.freenect_start_video.argtypes = [c_void_p]
            self.lib.freenect_start_video.restype = c_int
            
            self.lib.freenect_start_depth.argtypes = [c_void_p]
            self.lib.freenect_start_depth.restype = c_int
            
            self.lib.freenect_process_events.argtypes = [c_void_p]
            self.lib.freenect_process_events.restype = c_int

            # Funciones Motor y LED
            self.lib.freenect_set_led.argtypes = [c_void_p, c_int]
            self.lib.freenect_set_led.restype = c_int
            
            self.lib.freenect_set_tilt_degs.argtypes = [c_void_p, c_double]
            self.lib.freenect_set_tilt_degs.restype = c_int
            
            self.lib.freenect_update_tilt_state.argtypes = [c_void_p]
            self.lib.freenect_update_tilt_state.restype = c_int
            
            self.lib.freenect_get_tilt_state.argtypes = [c_void_p]
            self.lib.freenect_get_tilt_state.restype = POINTER(FreenectRawTiltState)
            
            self.lib.freenect_get_tilt_degs.argtypes = [POINTER(FreenectRawTiltState)]
            self.lib.freenect_get_tilt_degs.restype = c_double
            
            # --- Inicialización ---
            self.lib.freenect_init(byref(self.ctx), None)
            
            # IMPORTANTE: Seleccionar MOTOR (0x01) y CAMERA (0x02) = 0x03
            FREENECT_DEVICE_MOTOR = 0x01
            FREENECT_DEVICE_CAMERA = 0x02
            self.lib.freenect_select_subdevices(self.ctx, FREENECT_DEVICE_MOTOR | FREENECT_DEVICE_CAMERA)
            
            num = self.lib.freenect_num_devices(self.ctx)
            print(f"Dispositivos encontrados: {num}")
            if num <= 0:
                print("No Kinect found - ENTRANDO EN MODO SIMULACIÓN")
                self.mock_mode = True
                return True
            
            ret = self.lib.freenect_open_device(self.ctx, byref(self.dev), 0)
            if ret < 0:
                print("Error opening device - ENTRANDO EN MODO SIMULACIÓN")
                self.mock_mode = True
                return True
            
            # Buffers
            self.video_buffer = create_string_buffer(640 * 480 * 3)
            self.depth_buffer = create_string_buffer(640 * 480 * 2)
            
            self.lib.freenect_set_video_buffer(self.dev, ctypes.cast(self.video_buffer, c_void_p))
            self.lib.freenect_set_depth_buffer(self.dev, ctypes.cast(self.depth_buffer, c_void_p))
            
            self.lib.freenect_start_video(self.dev)
            self.lib.freenect_start_depth(self.dev)
            
            # Set initial LED green
            self.set_led(1) 
            
            return True
        except Exception as e:
            print(f"Error init: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_tilt(self, angle):
        """Mover motor usando libfreenect o Mock"""
        if self.mock_mode:
            self.current_tilt = angle
            print(f"MOCK TILT: {angle}")
            return True
        if not self.dev:
            return False
        try:
            angle = max(-30, min(30, angle))
            self.current_tilt = angle
            ret = self.lib.freenect_set_tilt_degs(self.dev, c_double(angle))
            return ret == 0
        except Exception as e:
            print(f"Error tilt: {e}")
            return False
    
    def set_led(self, mode):
        """Cambiar LED usando libfreenect o Mock"""
        if self.mock_mode:
            self.current_led = mode
            print(f"MOCK LED: {mode}")
            return True
        if not self.dev:
            return False
        try:
            self.current_led = mode
            ret = self.lib.freenect_set_led(self.dev, mode)
            return ret == 0
        except Exception as e:
            print(f"Error LED: {e}")
            return False
    
    def process_loop(self):
        """Loop continuo para procesar frames y eventos (Soporta MOCK)"""
        while self.running:
            if self.mock_mode:
                # Simular flujos
                if self.video_enabled:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, f"KINECT MOCK RGB - {time.ctime()}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                    self.latest_video_frame = frame
                if self.depth_enabled:
                    d_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(d_frame, "KINECT MOCK DEPTH", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    self.latest_depth_frame = cv2.applyColorMap(d_frame[:,:,0], self.current_colormap)
                time.sleep(0.033)
                continue

            try:
                # IMPORTANTE: process_events maneja toda la comunicación USB (video, depth, motor)
                self.lib.freenect_process_events(self.ctx)
                
                # Procesar video
                if self.video_enabled:
                    video_data = np.frombuffer(self.video_buffer.raw, dtype=np.uint8)
                    if video_data.sum() > 0:
                        frame_rgb = video_data.reshape((480, 640, 3))
                        
                        # AI Processing & Drawing
                        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                        
                        if self.mp_wrapper:
                            try:
                                h, w = frame_bgr.shape[:2]
                                
                                # 1. Hands
                                if self.hands_detector:
                                    res = self.hands_detector.process(frame_rgb)
                                    if res.multi_hand_landmarks:
                                        for hand_lms in res.multi_hand_landmarks:
                                            # Draw points
                                            points = []
                                            for lm in hand_lms.landmark:
                                                cx, cy = int(lm.x * w), int(lm.y * h)
                                                points.append((cx, cy))
                                                cv2.circle(frame_bgr, (cx, cy), 3, (0, 255, 0), -1)
                                            
                                            # Draw connections (Simplified basic hand)
                                            # Thumb: 0-1-2-3-4, Index: 0-5-6-7-8, ...
                                            fingers = [
                                                (0,1),(1,2),(2,3),(3,4),       # Thumb
                                                (0,5),(5,6),(6,7),(7,8),       # Index
                                                (0,9),(9,10),(10,11),(11,12),  # Middle
                                                (0,13),(13,14),(14,15),(15,16),# Ring
                                                (0,17),(17,18),(18,19),(19,20) # Pinky
                                            ]
                                            for s, e in fingers:
                                                if s < len(points) and e < len(points):
                                                    cv2.line(frame_bgr, points[s], points[e], (0, 255, 0), 2)
                                
                                # 2. Pose
                                if self.pose_detector:
                                    res = self.pose_detector.process(frame_rgb)
                                    if res.pose_landmarks:
                                        # Draw points
                                        points = {} # ID -> (x,y)
                                        lms = res.pose_landmarks.landmark
                                        for i, lm in enumerate(lms):
                                            if lm.visibility > 0.5:
                                                cx, cy = int(lm.x * w), int(lm.y * h)
                                                points[i] = (cx, cy)
                                                cv2.circle(frame_bgr, (cx, cy), 3, (0, 0, 255), -1)
                                        
                                        # Draw connections (Standard Pose)
                                        connections = [
                                            (11,12),(11,13),(13,15),(12,14),(14,16), # Arms
                                            (11,23),(12,24),(23,24),                 # Torso
                                            (23,25),(24,26),(25,27),(26,28),         # Legs
                                            (27,29),(29,31),(28,30),(30,32)          # Feet
                                        ]
                                        for s, e in connections:
                                            if s in points and e in points:
                                                cv2.line(frame_bgr, points[s], points[e], (0, 0, 255), 2)

                            except Exception as e:
                                print(f"AI Process Error: {e}")
                                
                        self.latest_video_frame = frame_bgr
                
                # Procesar depth
                if self.depth_enabled:
                    depth_data = np.frombuffer(self.depth_buffer.raw, dtype=np.uint16)
                    current_sum = depth_data.sum()
                    if current_sum > 0:
                        depth = depth_data.reshape((480, 640))
                        # Normalizacion fija para evitar parpadeos o pantalla negra por ruido
                        depth_norm = (depth.astype(np.float32) / 2048.0 * 255).astype(np.uint8)
                        # Invertir para que cerca sea mas brillante (opcional, pero estandar)
                        depth_norm = 255 - depth_norm
                        self.latest_depth_frame = cv2.applyColorMap(depth_norm, self.current_colormap)
                        if time.time() % 5 < 0.1: print("Depth Data OK")
                    else:
                        if time.time() % 5 < 0.1: print("Depth EMPTY")
                
            except Exception as e:
                print(f"Error en loop: {e}")
            
            time.sleep(0.005) # Loop más rápido para eventos USB fluidos
    
    def start(self):
        """Iniciar servidor Kinect"""
        if self.init():
            self.running = True
            self.thread = threading.Thread(target=self.process_loop, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop(self):
        """Detener servidor"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.lib and self.dev:
            self.lib.freenect_stop_depth(self.dev)
            self.lib.freenect_stop_video(self.dev)
            self.lib.freenect_close_device(self.dev)
        if self.lib and self.ctx:
            self.lib.freenect_shutdown(self.ctx)

# Instancia global
kinect = KinectServer()

@app.route('/')
def index():
    return open('kinect_dashboard.html', 'r', encoding='utf-8').read()

@app.route('/api/status')
def status():
    return jsonify({
        'connected': kinect.running,
        'tilt': kinect.current_tilt,
        'led': kinect.current_led,
        'video_enabled': kinect.video_enabled,
        'depth_enabled': kinect.depth_enabled
    })

@app.route('/api/tilt/<angle>')
def api_tilt(angle):
    try:
        angle_int = int(angle)
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid angle'}), 400
    success = kinect.set_tilt(angle_int)
    return jsonify({'success': success, 'angle': kinect.current_tilt})

@app.route('/api/led/<int:mode>')
def api_led(mode):
    success = kinect.set_led(mode)
    return jsonify({'success': success, 'mode': kinect.current_led})

@app.route('/api/video/<int:enabled>')
def api_video(enabled):
    kinect.video_enabled = bool(enabled)
    return jsonify({'success': True, 'enabled': kinect.video_enabled})

@app.route('/api/depth/<int:enabled>')
def api_depth(enabled):
    kinect.depth_enabled = bool(enabled)
    return jsonify({'success': True, 'enabled': kinect.depth_enabled})

@app.route('/api/colormap/<int:cmap>')
def api_colormap(cmap):
    kinect.current_colormap = cmap
    return jsonify({'success': True, 'colormap': kinect.current_colormap})

def generate_video():
    while True:
        frame_to_send = kinect.latest_video_frame
        if frame_to_send is None:
            # Fallback frame while starting
            frame_to_send = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame_to_send, "WAITING FOR RGB...", (140, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            
        ret, buffer = cv2.imencode('.jpg', frame_to_send, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.06) # Throttle for simulation

def generate_depth():
    while True:
        frame_to_send = kinect.latest_depth_frame
        if frame_to_send is None:
            # Fallback frame while starting
            frame_to_send = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame_to_send, "WAITING FOR DEPTH...", (140, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame_to_send, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.06)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/depth_feed')
def depth_feed():
    return Response(generate_depth(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("=" * 60)
    print("    KINECT UNIFIED DASHBOARD SERVER (LIBFREENECT ONLY)")
    print("=" * 60)
    
    if kinect.start():
        print("✓ Kinect initialized (Video + Motor + LED)")
        print("\n🌐 Server: http://localhost:5001")
        try:
            app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
        except KeyboardInterrupt:
            kinect.stop()
    else:
        print("✗ Error: Could not initialize Kinect")
