"""
Kinect Desktop App
Aplicación nativa de Python (Tkinter) para controlar Kinect v1.
Usa libfreenect unificado para Video, Depth, Motor y LED.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time
import ctypes
from ctypes import c_int, c_void_p, c_double, POINTER, byref, create_string_buffer, Structure, c_int16, c_int8
from pathlib import Path
import numpy as np

# --- DRIVER LIBFREENECT (Misma lógica probada que en el servidor) ---
DLL_PATH = Path(__file__).parent / "freenect.dll"

class FreenectRawTiltState(Structure):
    _fields_ = [
        ("accelerometer_x", c_int16),
        ("accelerometer_y", c_int16),
        ("accelerometer_z", c_int16),
        ("tilt_angle", c_int8),
        ("tilt_status", c_int)
    ]

class KinectDriver:
    def __init__(self):
        self.lib = None
        self.ctx = c_void_p()
        self.dev = c_void_p()
        self.video_buffer = None
        self.depth_buffer = None
        self.running = False
        self.latest_video = None
        self.latest_depth = None
        self.tilt_angle = 0
        self.lock = threading.Lock()

    def init(self):
        try:
            self.lib = ctypes.CDLL(str(DLL_PATH))
            # Firmas
            self.lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
            self.lib.freenect_init.restype = c_int
            self.lib.freenect_select_subdevices.argtypes = [c_void_p, c_int]
            self.lib.freenect_open_device.argtypes = [c_void_p, POINTER(c_void_p), c_int]
            self.lib.freenect_open_device.restype = c_int
            self.lib.freenect_set_video_buffer.argtypes = [c_void_p, c_void_p]
            self.lib.freenect_set_depth_buffer.argtypes = [c_void_p, c_void_p]
            self.lib.freenect_start_video.argtypes = [c_void_p]
            self.lib.freenect_start_depth.argtypes = [c_void_p]
            self.lib.freenect_process_events.argtypes = [c_void_p]
            self.lib.freenect_set_led.argtypes = [c_void_p, c_int]
            self.lib.freenect_set_tilt_degs.argtypes = [c_void_p, c_double]
            self.lib.freenect_close_device.argtypes = [c_void_p]
            self.lib.freenect_shutdown.argtypes = [c_void_p]

            self.lib.freenect_init(byref(self.ctx), None)
            # Motor(0x01) + Camera(0x02) = 0x03
            self.lib.freenect_select_subdevices(self.ctx, 0x03)
            
            if self.lib.freenect_open_device(self.ctx, byref(self.dev), 0) < 0:
                return False

            # Buffers
            self.video_buffer = create_string_buffer(640 * 480 * 3)
            self.depth_buffer = create_string_buffer(640 * 480 * 2)
            self.lib.freenect_set_video_buffer(self.dev, ctypes.cast(self.video_buffer, c_void_p))
            self.lib.freenect_set_depth_buffer(self.dev, ctypes.cast(self.depth_buffer, c_void_p))
            
            self.lib.freenect_start_video(self.dev)
            self.lib.freenect_start_depth(self.dev)
            
            self.running = True
            threading.Thread(target=self._process_loop, daemon=True).start()
            return True
        except Exception as e:
            print(f"Driver Error: {e}")
            return False

    def _process_loop(self):
        while self.running:
            try:
                self.lib.freenect_process_events(self.ctx)
                
                # Video
                v_data = np.frombuffer(self.video_buffer.raw, dtype=np.uint8)
                if v_data.sum() > 0:
                    frame = v_data.reshape((480, 640, 3))
                    with self.lock:
                        self.latest_video = frame # RGB nativo de freenect
                
                # Depth
                d_data = np.frombuffer(self.depth_buffer.raw, dtype=np.uint16)
                if d_data.sum() > 0:
                    depth = d_data.reshape((480, 640))
                    depth_norm = (depth / 2048.0 * 255).astype(np.uint8)
                    colored = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
                    with self.lock:
                        self.latest_depth = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
                        
            except:
                pass
            time.sleep(0.005)

    def set_tilt(self, angle):
        if self.dev:
            self.lib.freenect_set_tilt_degs(self.dev, c_double(angle))

    def set_led(self, mode):
        if self.dev:
            self.lib.freenect_set_led(self.dev, mode)

    def close(self):
        self.running = False
        time.sleep(0.5)
        if self.dev:
            self.lib.freenect_close_device(self.dev)
        if self.ctx:
            self.lib.freenect_shutdown(self.ctx)

# --- GUI APP ---
class KinectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kinect Control Center v1.0")
        self.root.geometry("1300x700")
        self.root.configure(bg="#1e1e1e")

        self.driver = KinectDriver()
        if not self.driver.init():
            messagebox.showerror("Error", "No se encontró Kinect conectado.")
            root.destroy()
            return

        self._setup_ui()
        self.update_loop()

    def _setup_ui(self):
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TButton", background="#3e3e3e", foreground="#ffffff", borderwidth=0)
        style.map("TButton", background=[('active', '#5e5e5e')])

        # Main Container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Video Frame (Left)
        video_panel = ttk.LabelFrame(main_frame, text=" Monitor RGB ", labelanchor="n")
        video_panel.grid(row=0, column=0, padx=10, sticky="nsew")
        self.video_label = ttk.Label(video_panel)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Depth Frame (Right)
        depth_panel = ttk.LabelFrame(main_frame, text=" Mapa de Profundidad ", labelanchor="n")
        depth_panel.grid(row=0, column=1, padx=10, sticky="nsew")
        self.depth_label = ttk.Label(depth_panel)
        self.depth_label.pack(fill=tk.BOTH, expand=True)

        # Controls (Bottom)
        controls_panel = ttk.Frame(main_frame)
        controls_panel.grid(row=1, column=0, columnspan=2, pady=20, sticky="ew")

        # Motor Control
        motor_group = ttk.LabelFrame(controls_panel, text=" Motor Tilt ", padding=15)
        motor_group.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.tilt_var = tk.DoubleVar(value=0)
        self.tilt_scale = ttk.Scale(motor_group, from_=-30, to=30, variable=self.tilt_var, 
                                   command=self.on_tilt_change, length=300)
        self.tilt_scale.pack(pady=5)
        
        self.tilt_lbl = ttk.Label(motor_group, text="0°")
        self.tilt_lbl.pack()

        # LED Control
        led_group = ttk.LabelFrame(controls_panel, text=" LED Status ", padding=15)
        led_group.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        btns = [("OFF", 0), ("VERDE", 1), ("ROJO", 2), ("AMARILLO", 3), ("PARPADEO", 4)]
        for text, mode in btns:
            btn = tk.Button(led_group, text=text, bg="#2d2d2d", fg="white",
                          command=lambda m=mode: self.driver.set_led(m), width=10)
            btn.pack(side=tk.LEFT, padx=5)

        # Status
        status_group = ttk.Frame(controls_panel)
        status_group.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        ttk.Label(status_group, text="Estado: CONECTADO", foreground="#00ff00").pack(anchor="e")
        ttk.Label(status_group, text="Driver: LibFreenect Unified").pack(anchor="e")

        # Grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def on_tilt_change(self, val):
        angle = int(float(val))
        self.tilt_lbl.config(text=f"{angle}°")
        self.driver.set_tilt(angle)

    def update_loop(self):
        with self.driver.lock:
            if self.driver.latest_video is not None:
                # Resize for performance if needed, or keep VGA
                img = Image.fromarray(self.driver.latest_video)
                img = img.resize((640, 480)) # Ensure VGA fit
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk # Keep ref
                self.video_label.configure(image=imgtk)

            if self.driver.latest_depth is not None:
                img = Image.fromarray(self.driver.latest_depth)
                img = img.resize((640, 480))
                imgtk = ImageTk.PhotoImage(image=img)
                self.depth_label.imgtk = imgtk
                self.depth_label.configure(image=imgtk)

        self.root.after(30, self.update_loop)

    def on_close(self):
        self.driver.close()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = KinectApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    except Exception as e:
        print(f"Error fatal: {e}")
