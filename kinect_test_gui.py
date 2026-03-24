"""
Kinect v1 Test GUI - Ventana de Demostración Completa
Muestra todas las capacidades del Kinect en tiempo real.
"""
import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSlider, QGroupBox,
                             QGridLayout, QComboBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from src.sensors.kinect_v1_complete import KinectV1DriverComplete
from src.tracking.hybrid_tracker import HybridTracker
import mediapipe as mp
import sounddevice as sd

class KinectTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kinect = None
        self.camera = None
        self.current_led = 0
        self.current_tilt = 0
        self.audio_stream = None
        
        # Hybrid Tracker (MediaPipe + OpenCV)
        self.tracker = HybridTracker()
        
        # Estado de toggles
        self.show_pose = True
        self.show_hands = True
        self.show_face_cv = False
        self.show_motion = False
        self.show_edges = False
        
        self.initUI()
        self.initKinect()
        self.initCamera()
        self.startTimers()
    
    def initUI(self):
        self.setWindowTitle("🎮 Kinect v1 - Test Completo | God Mode")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # === LADO IZQUIERDO: VIDEO ===
        left_panel = QVBoxLayout()
        
        # Video display
        self.video_label = QLabel("Conectando a cámara...")
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.video_label)
        
        # Info de video
        self.video_info = QLabel("Resolución: -- | FPS: --")
        self.video_info.setStyleSheet("font-size: 12px; padding: 5px;")
        left_panel.addWidget(self.video_info)
        
        main_layout.addLayout(left_panel, 2)
        
        # === LADO DERECHO: CONTROLES ===
        right_panel = QVBoxLayout()
        
        # Estado de conexión
        status_group = QGroupBox("📡 Estado de Conexión")
        status_layout = QVBoxLayout()
        self.kinect_status = QLabel("❌ Kinect: Desconectado")
        self.kinect_status.setStyleSheet("font-size: 14px; color: red;")
        self.camera_status = QLabel("❌ Cámara: Desconectada")
        self.camera_status.setStyleSheet("font-size: 14px; color: red;")
        self.audio_status = QLabel("❌ Audio: No detectado")
        self.audio_status.setStyleSheet("font-size: 14px; color: red;")
        status_layout.addWidget(self.kinect_status)
        status_layout.addWidget(self.camera_status)
        status_layout.addWidget(self.audio_status)
        status_group.setLayout(status_layout)
        right_panel.addWidget(status_group)
        
        # Control de LED
        led_group = QGroupBox("💡 Control de LED")
        led_layout = QGridLayout()
        
        led_buttons = [
            ("⚫ Apagado", 0),
            ("🟢 Verde", 1),
            ("🔴 Rojo", 2),
            ("🟡 Amarillo", 3),
            ("⚡ Parpadeo Amarillo", 4),
            ("⚡ Parpadeo Verde", 5),
            ("⚡ Parpadeo Rojo/Amarillo", 6)
        ]
        
        for i, (text, value) in enumerate(led_buttons):
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, v=value: self.setLED(v))
            led_layout.addWidget(btn, i // 2, i % 2)
        
        led_group.setLayout(led_layout)
        right_panel.addWidget(led_group)
        
        # Toggles de Tracking
        tracking_group = QGroupBox("👁️ Visualización de Tracking")
        tracking_layout = QVBoxLayout()
        
        # Toggles MediaPipe
        self.toggle_hands_btn = QPushButton("✅ Manos (MP)")
        self.toggle_hands_btn.setCheckable(True)
        self.toggle_hands_btn.setChecked(True)
        self.toggle_hands_btn.clicked.connect(self.toggleHands)
        self.toggle_hands_btn.setStyleSheet("padding: 5px; background-color: #4caf50; color: white;")
        
        self.toggle_pose_btn = QPushButton("✅ Cuerpo (MP)")
        self.toggle_pose_btn.setCheckable(True)
        self.toggle_pose_btn.setChecked(True)
        self.toggle_pose_btn.clicked.connect(self.togglePose)
        self.toggle_pose_btn.setStyleSheet("padding: 5px; background-color: #4caf50; color: white;")
        
        # Toggles OpenCV
        self.toggle_cv_face_btn = QPushButton("❌ Cara (OpenCV)")
        self.toggle_cv_face_btn.setCheckable(True)
        self.toggle_cv_face_btn.setChecked(False)
        self.toggle_cv_face_btn.clicked.connect(self.toggleCVFace)
        self.toggle_cv_face_btn.setStyleSheet("padding: 5px; background-color: #757575; color: white;")
        
        self.toggle_motion_btn = QPushButton("❌ Movimiento")
        self.toggle_motion_btn.setCheckable(True)
        self.toggle_motion_btn.setChecked(False)
        self.toggle_motion_btn.clicked.connect(self.toggleMotion)
        self.toggle_motion_btn.setStyleSheet("padding: 5px; background-color: #757575; color: white;")

        self.toggle_edges_btn = QPushButton("❌ Bordes")
        self.toggle_edges_btn.setCheckable(True)
        self.toggle_edges_btn.setChecked(False)
        self.toggle_edges_btn.clicked.connect(self.toggleEdges)
        self.toggle_edges_btn.setStyleSheet("padding: 5px; background-color: #757575; color: white;")
        
        tracking_layout.addWidget(self.toggle_hands_btn)
        tracking_layout.addWidget(self.toggle_pose_btn)
        tracking_layout.addWidget(self.toggle_cv_face_btn)
        tracking_layout.addWidget(self.toggle_motion_btn)
        tracking_layout.addWidget(self.toggle_edges_btn)
        
        tracking_group.setLayout(tracking_layout)
        right_panel.addWidget(tracking_group)
        
        # Control de Motor
        motor_group = QGroupBox("🔄 Control de Motor")
        motor_layout = QVBoxLayout()
        
        self.motor_slider = QSlider(Qt.Orientation.Horizontal)
        self.motor_slider.setMinimum(-31)
        self.motor_slider.setMaximum(31)
        self.motor_slider.setValue(0)
        self.motor_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.motor_slider.setTickInterval(5)
        self.motor_slider.valueChanged.connect(self.setMotorTilt)
        
        self.motor_label = QLabel("Inclinación: 0°")
        self.motor_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.motor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        motor_buttons = QHBoxLayout()
        btn_up = QPushButton("⬆️ Arriba (+15°)")
        btn_up.clicked.connect(lambda: self.adjustMotor(15))
        btn_center = QPushButton("↔️ Centro (0°)")
        btn_center.clicked.connect(lambda: self.motor_slider.setValue(0))
        btn_down = QPushButton("⬇️ Abajo (-15°)")
        btn_down.clicked.connect(lambda: self.adjustMotor(-15))
        
        motor_buttons.addWidget(btn_up)
        motor_buttons.addWidget(btn_center)
        motor_buttons.addWidget(btn_down)
        
        motor_layout.addWidget(self.motor_label)
        motor_layout.addWidget(self.motor_slider)
        motor_layout.addLayout(motor_buttons)
        
        motor_group.setLayout(motor_layout)
        right_panel.addWidget(motor_group)
        
        # Visualización de Audio
        audio_group = QGroupBox("🎤 Audio del Kinect")
        audio_layout = QVBoxLayout()
        
        self.audio_meter = QLabel()
        self.audio_meter.setMinimumHeight(30)
        self.audio_meter.setStyleSheet("background-color: #2a2a2a; border: 1px solid #555;")
        
        self.audio_level = QLabel("Nivel: 0%")
        self.audio_level.setStyleSheet("font-size: 12px;")
        
        audio_layout.addWidget(self.audio_meter)
        audio_layout.addWidget(self.audio_level)
        audio_group.setLayout(audio_layout)
        right_panel.addWidget(audio_group)
        
        # Botones de utilidad
        util_layout = QVBoxLayout()
        
        btn_refresh = QPushButton("🔄 Reconectar Todo")
        btn_refresh.clicked.connect(self.reconnectAll)
        btn_refresh.setStyleSheet("padding: 10px; font-size: 14px;")
        
        btn_close = QPushButton("❌ Cerrar")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("padding: 10px; font-size: 14px; background-color: #d32f2f; color: white;")
        
        util_layout.addWidget(btn_refresh)
        util_layout.addWidget(btn_close)
        
        right_panel.addLayout(util_layout)
        right_panel.addStretch()
        
        main_layout.addLayout(right_panel, 1)
    
    def initKinect(self):
        try:
            self.kinect = KinectV1DriverComplete()
            if self.kinect.isOpened():
                self.kinect_status.setText("✅ Kinect: Conectado (God Mode)")
                self.kinect_status.setStyleSheet("font-size: 14px; color: green;")
                # LED verde inicial
                self.setLED(1)
        except Exception as e:
            self.kinect_status.setText(f"❌ Kinect: Error - {str(e)[:30]}")
    
    def initCamera(self):
        # Intentar cámara (índice 0 es usualmente la webcam o Kinect si está enumerado)
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            self.camera_status.setText("✅ Cámara: Conectada")
            self.camera_status.setStyleSheet("font-size: 14px; color: green;")
        else:
            self.camera_status.setText("❌ Cámara: No disponible")
    
    def startTimers(self):
        # Timer para actualizar video
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.updateVideo)
        self.video_timer.start(33)  # ~30 FPS
        
        # Timer para audio (simulado - no captura real)
        self.audio_timer = QTimer()
        self.audio_timer.timeout.connect(self.updateAudio)
        self.audio_timer.start(100)
    
    def updateVideo(self):
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Actualizar configuración del tracker
                self.tracker.enable_pose = self.show_pose
                self.tracker.enable_hands = self.show_hands
                self.tracker.enable_opencv_face = self.show_face_cv
                self.tracker.enable_motion = self.show_motion
                self.tracker.enable_edges = self.show_edges
                
                # Convert to RGB for processing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                results = self.tracker.process_frame(frame_rgb)
                
                # Draw results on frame
                # Note: draw_results expects BGR if using cv2 drawing functions, 
                # but we are displaying RGB. 
                # Let's standardize on processing copy for display.
                display_frame = frame.copy()
                display_frame = self.tracker.draw_results(display_frame, results)
                
                # Update info
                h, w = frame.shape[:2]
                fps = self.camera.get(cv2.CAP_PROP_FPS)
                summary = self.tracker.get_detection_summary(results)
                
                self.video_info.setText(
                    f"Res: {w}x{h} | FPS: {fps:.1f} | Det: {summary}"
                )
                
                # Convert BGR to RGB for Qt
                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                
                q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                
                # Scale to fit
                scaled_pixmap = pixmap.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
                self.video_label.setPixmap(scaled_pixmap)
    
    def updateAudio(self):
        # Simular nivel de audio (en producción, leerías del Kinect)
        try:
            # Verificar si hay dispositivo Kinect Audio
            devices = sd.query_devices()
            kinect_audio = None
            for i, dev in enumerate(devices):
                if 'Kinect' in dev['name'] and dev['max_input_channels'] > 0:
                    kinect_audio = i
                    self.audio_status.setText(f"✅ Audio: {dev['name'][:30]}")
                    self.audio_status.setStyleSheet("font-size: 14px; color: green;")
                    break
            
            # Simular nivel (en producción usarías sounddevice.InputStream)
            level = np.random.randint(0, 100)
            self.audio_level.setText(f"Nivel: {level}%")
            
            # Barra visual
            width = int(640 * (level / 100))
            color = "#4caf50" if level < 70 else "#ff9800" if level < 90 else "#f44336"
            self.audio_meter.setStyleSheet(
                f"background: qlineargradient(x1:0, x2:1, stop:0 {color}, stop:{level/100} {color}, stop:{level/100 + 0.01} #2a2a2a, stop:1 #2a2a2a);"
                f"border: 1px solid #555;"
            )
        except Exception:
            pass
    
    def setLED(self, color):
        if self.kinect and self.kinect.isOpened():
            if self.kinect.set_led(color):
                self.current_led = color
                print(f"✅ LED configurado: {color}")
    
    def setMotorTilt(self, angle):
        if self.kinect and self.kinect.isOpened():
            if self.kinect.set_tilt(angle):
                self.current_tilt = angle
                self.motor_label.setText(f"Inclinación: {angle}°")
    
    def adjustMotor(self, delta):
        new_angle = max(-31, min(31, self.motor_slider.value() + delta))
        self.motor_slider.setValue(new_angle)
    
    def toggleHands(self):
        self.show_hands = self.toggle_hands_btn.isChecked()
        self._updateButtonStyle(self.toggle_hands_btn, self.show_hands, "Manos (MP)")
        
    def togglePose(self):
        self.show_pose = self.toggle_pose_btn.isChecked()
        self._updateButtonStyle(self.toggle_pose_btn, self.show_pose, "Cuerpo (MP)")
    
    def toggleCVFace(self):
        self.show_face_cv = self.toggle_cv_face_btn.isChecked()
        self._updateButtonStyle(self.toggle_cv_face_btn, self.show_face_cv, "Cara (CV)")
        
    def toggleMotion(self):
        self.show_motion = self.toggle_motion_btn.isChecked()
        self._updateButtonStyle(self.toggle_motion_btn, self.show_motion, "Movimiento")
        
    def toggleEdges(self):
        self.show_edges = self.toggle_edges_btn.isChecked()
        self._updateButtonStyle(self.toggle_edges_btn, self.show_edges, "Bordes")
        
    def _updateButtonStyle(self, btn, state, text):
        if state:
            btn.setText(f"✅ {text}")
            btn.setStyleSheet("padding: 5px; background-color: #4caf50; color: white;")
        else:
            btn.setText(f"❌ {text}")
            btn.setStyleSheet("padding: 5px; background-color: #757575; color: white;")
    
    def reconnectAll(self):
        print("🔄 Reconectando dispositivos...")
        
        # Reconectar Kinect
        if self.kinect:
            self.kinect.release()
        self.initKinect()
        
        # Reconectar cámara
        if self.camera:
            self.camera.release()
        self.initCamera()
    
    def closeEvent(self, event):
        print("🔧 Cerrando aplicación...")
        
        # Apagar LED y centrar motor
        if self.kinect and self.kinect.isOpened():
            self.kinect.set_led(0)
            self.kinect.set_tilt(0)
            self.kinect.release()
        
        # Liberar cámara
        if self.camera:
            self.camera.release()
        
        # Liberar tracker
        if self.tracker:
            self.tracker.release()
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = KinectTestWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
