import time
import threading
import sys
import os
import subprocess
import math
import cv2  # Requires: pip install opencv-python
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import pystray

class HPDManager:
    """Handles low-level OS sleep inhibition (Kernel Level)."""
    def __init__(self):
        self.lock_inhibited = False
        self.is_windows = sys.platform.startswith('win')
        self.is_macos = sys.platform.startswith('darwin')

    def inhibit_sleep(self):
        if self.lock_inhibited: return
        try:
            if self.is_windows:
                import ctypes
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001 | 0x00000002)
            elif self.is_macos:
                self.caffeinate_process = subprocess.Popen(['caffeinate', '-i'])
            self.lock_inhibited = True
        except Exception as e: print(f"[HPD Error] {e}")

    def allow_sleep(self):
        if not self.lock_inhibited: return
        try:
            if self.is_windows:
                import ctypes
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            elif self.is_macos:
                if hasattr(self, 'caffeinate_process'): self.caffeinate_process.terminate()
            self.lock_inhibited = False
        except Exception as e: print(f"[HPD Error] {e}")

class GlazedSensor(threading.Thread):
    def __init__(self, callback, camera_index=0):
        super().__init__(daemon=True)
        self.callback = callback
        self.camera_index = camera_index
        self.running = True
        self.last_gray = None
        self.motion_history = []
        
        # Adjustable Params
        self.sensitivity = 350
        self.pz_reach = 0.7  
        self.proximity_min = 50 
        self.calibration_mode = True 

    def run(self):
        cap = None
        # Brio/Windows often require cycling through backends
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF] if sys.platform.startswith('win') else [None]
        
        found = False
        for backend in backends:
            cap = cv2.VideoCapture(self.camera_index, backend) if backend else cv2.VideoCapture(self.camera_index)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                ret, _ = cap.read()
                if ret:
                    found = True
                    break
            cap.release()
        
        if not found:
            self.callback(None, False, 0, "CAMERA_FAILED")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.5)
                continue

            # 1. APPLY PZ REACH (Map the Zone)
            h, w, _ = frame.shape
            rw, rh = int(w * self.pz_reach), int(h * self.pz_reach)
            x1, y1 = (w - rw) // 2, (h - rh) // 2
            
            if self.calibration_mode:
                display_frame = frame.copy()
                cv2.rectangle(display_frame, (x1, y1), (x1+rw, y1+rh), (0, 255, 204), 2)
                overlay = display_frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                cv2.rectangle(overlay, (x1, y1), (x1+rw, y1+rh), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)
                processed_frame = cv2.resize(display_frame, (320, 240))
            else:
                # Active Mode: Crop and Glaze
                cropped = frame[y1:y1+rh, x1:x1+rw]
                small = cv2.resize(cropped, (20, 15), interpolation=cv2.INTER_LINEAR)
                glazed = cv2.resize(small, (320, 240), interpolation=cv2.INTER_NEAREST)
                processed_frame = cv2.GaussianBlur(glazed, (99, 99), 0)

            # 2. SPATIAL MOTION ANALYTICS
            cropped_for_calc = frame[y1:y1+rh, x1:x1+rw]
            calc_small = cv2.resize(cropped_for_calc, (40, 30), interpolation=cv2.INTER_LINEAR)
            gray = cv2.cvtColor(calc_small, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            
            is_motion = False
            current_proximity = 0
            
            if self.last_gray is not None:
                delta = cv2.absdiff(self.last_gray, gray)
                thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    current_proximity = cv2.contourArea(largest_contour)
                    if current_proximity > (self.proximity_min / 10): 
                        if np.sum(thresh) > self.sensitivity:
                            is_motion = True
            
            self.last_gray = gray
            
            # 3. STABILIZATION
            self.motion_history.append(is_motion)
            if len(self.motion_history) > 3: self.motion_history.pop(0)
            stable_trigger = all(self.motion_history) if len(self.motion_history) >= 2 else False

            self.callback(processed_frame, stable_trigger, current_proximity)
            time.sleep(0.06)

        cap.release()

    def stop(self):
        self.running = False

class App:
    def __init__(self, root):
        self.root = root
        self.hpd = HPDManager()
        self.presence_confidence = 1.0
        self.motion_active = False
        self.sensor_error = False
        self.current_camera_index = 0
        self.sensor = None
        self.last_prox = 0
        self.icon = None
        self.icon_thread = None
        
        self.root.title("PZDetector | Presence Zone Utility")
        self.root.geometry("520x980")
        self.root.configure(bg="#030303")
        self.root.resizable(False, False)
        
        self.setup_styles()
        self.build_ui()
        self.setup_tray()
        self.start_sensor()
        self.update_loop()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("PZD.Horizontal.TProgressbar", troughcolor='#0a0a0a', 
                        background='#00ffcc', thickness=12, bordercolor='#030303')
        style.configure("TCombobox", fieldbackground="#111", background="#333", foreground="#00ffcc")
        style.configure("Setup.TButton", font=("Helvetica", 10, "bold"), background="#00ffcc", foreground="#000")

    def build_ui(self):
        header = tk.Frame(self.root, bg="#030303")
        header.pack(pady=20)
        tk.Label(header, text="PZDetector", fg="#00ffcc", bg="#030303", font=("Helvetica", 28, "bold")).pack(side="left")
        
        self.led_canvas = tk.Canvas(header, width=20, height=20, bg="#030303", highlightthickness=0)
        self.led_dot = self.led_canvas.create_oval(4, 4, 16, 16, fill="#111")
        self.led_canvas.pack(side="left", padx=15)
        
        self.cal_banner = tk.Frame(self.root, bg="#00ffcc")
        self.cal_banner.pack(fill="x")
        self.cal_label = tk.Label(self.cal_banner, text="CALIBRATION MODE: MAP YOUR ZONE", fg="#000", bg="#00ffcc", font=("Helvetica", 8, "bold"))
        self.cal_label.pack(pady=2)

        self.view_frame = tk.Frame(self.root, bg="#0a0a0a", bd=1, relief="flat")
        self.view_frame.pack(pady=5)
        self.cam_label = tk.Label(self.view_frame, bg="#0a0a0a", width=320, height=240)
        self.cam_label.pack(padx=2, pady=2)
        
        self.prox_var = tk.StringVar(value="DEPTH SCORE: 0")
        tk.Label(self.root, textvariable=self.prox_var, fg="#00ffcc", bg="#030303", font=("JetBrains Mono", 8)).pack()

        meter_frame = tk.Frame(self.root, bg="#030303")
        meter_frame.pack(fill="x", padx=60, pady=10)
        self.status_var = tk.StringVar(value="WAITING...")
        tk.Label(meter_frame, textvariable=self.status_var, fg="#fff", bg="#030303", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.progress = ttk.Progressbar(meter_frame, style="PZD.Horizontal.TProgressbar", length=380, mode="determinate")
        self.progress.pack(pady=5)

        ctrl = tk.LabelFrame(self.root, text=" SIGNAL ARCHITECTURE ", fg="#444", bg="#030303", padx=20, pady=15)
        ctrl.pack(fill="x", padx=60, pady=5)
        
        self.setup_btn = ttk.Button(ctrl, text="FINISH SETUP & GLAZE", style="Setup.TButton", command=self.toggle_calibration)
        self.setup_btn.pack(fill="x", pady=(0, 15))

        cam_frame = tk.Frame(ctrl, bg="#030303")
        cam_frame.pack(fill="x", pady=(0, 15))
        tk.Label(cam_frame, text="Sensor Input:", fg="#666", bg="#030303", font=("Helvetica", 9)).pack(side="left")
        self.cam_selector = ttk.Combobox(cam_frame, values=["Camera 0", "Camera 1", "Camera 2", "Camera 3"], state="readonly", width=12)
        self.cam_selector.current(0)
        self.cam_selector.bind("<<ComboboxSelected>>", self.on_camera_change)
        self.cam_selector.pack(side="left", padx=10)

        tk.Label(ctrl, text="PZ Reach (Crop Background Noise)", fg="#666", bg="#030303", font=("Helvetica", 8)).pack(anchor="w")
        self.reach_scale = tk.Scale(ctrl, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", bg="#030303", fg="#00ffcc", 
                                   highlightthickness=0, troughcolor="#111")
        self.reach_scale.set(0.7)
        self.reach_scale.pack(fill="x", pady=(0, 10))

        tk.Label(ctrl, text="Proximity Floor (Ignore Small Objects)", fg="#666", bg="#030303", font=("Helvetica", 8)).pack(anchor="w")
        self.prox_scale = tk.Scale(ctrl, from_=1, to=200, orient="horizontal", bg="#030303", fg="#00ffcc", 
                                   highlightthickness=0, troughcolor="#111")
        self.prox_scale.set(50)
        self.prox_scale.pack(fill="x")
        
        self.buffer_scale = tk.Scale(self.root, from_=5, to=600, orient="horizontal", label="Kitten Buffer (Seconds)", 
                                     bg="#030303", fg="#00ffcc", highlightthickness=0, troughcolor="#111", length=380)
        self.buffer_scale.set(45)
        self.buffer_scale.pack(pady=15)

        tk.Label(self.root, text="PEBCAK OPTIMIZED • NO BIOMETRICS • PZDETECTOR.COM", 
                 fg="#222", bg="#030303", font=("Helvetica", 7, "bold")).pack(side="bottom", pady=15)

    def create_icon_image(self, color):
        image = Image.new('RGB', (64, 64), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse([(4, 4), (60, 60)], fill=color)
        return image

    def setup_tray(self):
        self.icons = {
            'active': self.create_icon_image('#00ffcc'),
            'decay': self.create_icon_image('#ffff00'),
            'empty': self.create_icon_image('#ff0000')
        }
        menu = (pystray.MenuItem('Show', self.show_window, default=True),
                pystray.MenuItem('Quit', self.quit_app))
        self.icon = pystray.Icon("PZDetector", self.icons['empty'], "PZDetector", menu)
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)

    def hide_window(self):
        self.root.withdraw()
        if not self.icon_thread or not self.icon_thread.is_alive():
            self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
            self.icon_thread.start()

    def show_window(self):
        self.icon.stop()
        self.root.deiconify()

    def quit_app(self):
        self.icon.stop()
        if self.sensor:
            self.sensor.stop()
        self.hpd.allow_sleep()
        self.root.quit()

    def start_sensor(self):
        if self.sensor: self.sensor.stop()
        self.sensor_error = False
        self.sensor = GlazedSensor(self.on_sensor_data, camera_index=self.current_camera_index)
        if hasattr(self, 'setup_btn') and "RE-ENTER" in self.setup_btn.cget('text'):
            self.sensor.calibration_mode = False
        self.sensor.start()

    def on_camera_change(self, event):
        new_index = self.cam_selector.current()
        if new_index != self.current_camera_index:
            self.current_camera_index = new_index
            self.start_sensor()

    def toggle_calibration(self):
        if self.sensor:
            self.sensor.calibration_mode = not self.sensor.calibration_mode
            if not self.sensor.calibration_mode:
                self.setup_btn.config(text="RE-ENTER CALIBRATION")
                self.cal_banner.config(bg="#111")
                self.cal_label.config(text="PZD ACTIVE: GLAZED VISION ON", fg="#444", bg="#111")
            else:
                self.setup_btn.config(text="FINISH SETUP & GLAZE")
                self.cal_banner.config(bg="#00ffcc")
                self.cal_label.config(text="CALIBRATION MODE: MAP YOUR ZONE", fg="#000", bg="#00ffcc")

    def on_sensor_data(self, frame, motion, proximity, error=None):
        if error == "CAMERA_FAILED":
            self.sensor_error = True
            self.cam_label.config(image='', text="SENSOR BLOCKED OR IN USE", fg="#ff4444")
            return

        self.last_prox = proximity
        if frame is not None:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=img)
            self.cam_label.config(image=self.photo, text="")
        if motion: self.motion_active = True

    def update_loop(self):
        if self.sensor:
            self.sensor.pz_reach = self.reach_scale.get()
            self.sensor.proximity_min = self.prox_scale.get()
        
        self.prox_var.set(f"DEPTH SCORE: {int(self.last_prox)} / TARGET: {int(self.prox_scale.get()/10)}")

        t = time.time()
        alpha = 40 + (math.sin(t * 3) + 1) * 80 if self.presence_confidence > 0.05 else 20
        self.led_canvas.itemconfig(self.led_dot, fill=f'#00{int(alpha):02x}{int(alpha*0.8):02x}')

        current_icon = self.icon.icon
        new_icon_name = 'empty'

        if self.sensor_error:
            self.status_var.set("HARDWARE ERROR")
            new_icon_name = 'empty'
        elif not self.sensor or (self.sensor and self.sensor.calibration_mode):
            self.status_var.set("CALIBRATING...")
            new_icon_name = 'decay'
        elif self.motion_active:
            self.presence_confidence = 1.0
            self.hpd.inhibit_sleep()
            self.status_var.set("PRESENCE CONFIRMED")
            self.motion_active = False
            new_icon_name = 'active'
        else:
            decay = 0.1 / self.buffer_scale.get()
            self.presence_confidence = max(0, self.presence_confidence - decay)
            if self.presence_confidence <= 0:
                self.hpd.allow_sleep()
                self.status_var.set("ZONE EMPTY")
                new_icon_name = 'empty'
            else:
                self.status_var.set(f"DECAYING: {int(self.presence_confidence*100)}%")
                new_icon_name = 'decay'
        
        if self.icons[new_icon_name] != current_icon:
            self.icon.icon = self.icons[new_icon_name]

        self.progress['value'] = self.presence_confidence * 100
        self.root.after(100, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()