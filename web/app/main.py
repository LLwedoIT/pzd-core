import time
import threading
import sys
import os
import subprocess
import math
import tkinter as tk
from tkinter import ttk

class HPDManager:
    """
    Handles hardware-level Human Presence Detection (HPD) and OS sleep inhibition.
    In a full release, this would interface with actual webcam sensors or system APIs.
    """
    def __init__(self):
        self.lock_inhibited = False
        self.is_windows = sys.platform.startswith('win')
        self.is_macos = sys.platform.startswith('darwin')

    def inhibit_sleep(self, reason="PZD Active"):
        """Prevents the OS from locking or sleeping."""
        if self.lock_inhibited:
            return
        try:
            if self.is_windows:
                import ctypes
                # 0x80000001: ES_CONTINUOUS | ES_SYSTEM_REQUIRED
                # 0x00000002: ES_DISPLAY_REQUIRED
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001 | 0x00000002)
            elif self.is_macos:
                self.caffeinate_process = subprocess.Popen(['caffeinate', '-i'])
            self.lock_inhibited = True
            print(f"[HPD] System vitality maintained: {reason}")
        except Exception as e:
            print(f"[HPD] Error inhibiting sleep: {e}")

    def allow_sleep(self):
        """Resumes standard OS power policies."""
        if not self.lock_inhibited:
            return
        try:
            if self.is_windows:
                import ctypes
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            elif self.is_macos:
                if hasattr(self, 'caffeinate_process'):
                    self.caffeinate_process.terminate()
            self.lock_inhibited = False
            print("[HPD] Releasing system to standard security policies.")
        except Exception as e:
            print(f"[HPD] Error allowing sleep: {e}")

class PZDetectorApp:
    def __init__(self, root):
        self.root = root
        self.hpd = HPDManager()
        
        # State Variables
        self.presence_confidence = 1.0  # 1.0 = Present, 0.0 = Absent
        self.last_led_update = 0
        
        # UI Configuration
        self.root.title("PZDetector v1.2")
        self.root.geometry("520x650")
        self.root.configure(bg="#050505")
        self.setup_styles()
        self.build_ui()
        
        self.update_loop()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("PZD.Horizontal.TProgressbar", 
                             troughcolor='#111', bordercolor='#111', 
                             background='#00ffcc', thickness=16)

    def build_ui(self):
        # Header Area
        header_frame = tk.Frame(self.root, bg="#050505")
        header_frame.pack(pady=(25, 2))
        
        tk.Label(header_frame, text="PZD", fg="#00ffcc", bg="#050505", 
                 font=("Helvetica", 24, "bold")).pack(side="left")
        
        # Hardware LED Mirror (The "Breathing" Signal)
        self.led_mirror = tk.Canvas(header_frame, width=16, height=16, bg="#050505", highlightthickness=0)
        self.led_circle = self.led_mirror.create_oval(2, 2, 14, 14, fill="#1a1a1a")
        self.led_mirror.pack(side="left", padx=10)
        
        tk.Label(self.root, text="HUMAN PRESENCE DETECTION UTILITY", fg="#444", bg="#050505", 
                 font=("Helvetica", 8, "bold")).pack(pady=(0, 15))

        # Confidence Meter (The Kitten Buffer visualizer)
        self.progress = ttk.Progressbar(self.root, style="PZD.Horizontal.TProgressbar", 
                                       orient="horizontal", length=420, mode="determinate")
        self.progress.pack(pady=5)

        self.status_var = tk.StringVar(value="MONITORING ZONE")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="#fff", 
                                     bg="#050505", font=("Helvetica", 11, "bold"))
        self.status_label.pack(pady=10)

        # Signal Architecture Controls
        signal_frame = tk.LabelFrame(self.root, text=" SIGNAL ARCHITECTURE ", fg="#333", bg="#050505", 
                                     font=("Helvetica", 8, "bold"), padx=25, pady=15)
        signal_frame.pack(pady=10, padx=40, fill="x")

        # Fog Mode / Glazed Vision Toggle
        self.fog_mode_var = tk.BooleanVar(value=True)
        tk.Checkbutton(signal_frame, text="Glazed Vision (Fog Mode)", variable=self.fog_mode_var, 
                       fg="#00ffcc", bg="#050505", selectcolor="#111", activebackground="#050505",
                       font=("Helvetica", 10, "bold")).pack(anchor="w")

        # LED Pattern Studio
        pattern_options = tk.Frame(signal_frame, bg="#050505")
        pattern_options.pack(anchor="w", pady=10)
        tk.Label(pattern_options, text="LED Pattern:", fg="#666", bg="#050505", font=("Helvetica", 9)).pack(side="left")
        
        self.led_pattern_var = tk.StringVar(value="Breathe")
        for pattern in ["Breathe", "Pulse", "Soft Glow"]:
            tk.Radiobutton(pattern_options, text=pattern, variable=self.led_pattern_var, value=pattern,
                           fg="#aaa", bg="#050505", selectcolor="#222", activebackground="#050505", 
                           font=("Helvetica", 9)).pack(side="left", padx=5)

        # Simulation Toggle (Simulates PEBCAK / Manual Presence)
        self.manual_in_zone = tk.BooleanVar(value=True)
        tk.Checkbutton(signal_frame, text="Presence Verified (In-Zone)", variable=self.manual_in_zone, 
                       fg="#999", bg="#050505", selectcolor="#222", activebackground="#050505").pack(anchor="w", pady=(10, 0))

        # The Kitten Buffer Slider (Decay Speed)
        buffer_frame = tk.Frame(self.root, bg="#050505")
        buffer_frame.pack(pady=20)
        tk.Label(buffer_frame, text="Kitten Buffer (Seconds):", fg="#666", bg="#050505", font=("Helvetica", 9)).grid(row=0, column=0)
        self.buffer_val = tk.Scale(buffer_frame, from_=5, to=600, orient="horizontal", 
                                   bg="#050505", fg="#00ffcc", highlightthickness=0, length=240)
        self.buffer_val.set(45)
        self.buffer_val.grid(row=0, column=1, padx=15)

        # Footer
        tk.Label(self.root, text="PEBCAK OPTIMIZED • NO BIOMETRICS • PZDETECTOR.COM", 
                 fg="#222", bg="#050505", font=("Helvetica", 7, "bold")).pack(side="bottom", pady=20)

    def _get_led_color(self, intensity):
        """Converts 0-255 intensity to a teal/green hex code."""
        intensity = max(0, min(255, int(intensity)))
        return f'#00{intensity:02x}{int(intensity*0.8):02x}'

    def update_loop(self):
        """The main PZD state engine."""
        current_time = time.time()
        is_user_present = self.manual_in_zone.get()
        buffer_seconds = self.buffer_val.get()
        
        # 1. LED SIGNAL CALCULATIONS
        intensity = 0
        if is_user_present and self.fog_mode_var.get():
            pattern = self.led_pattern_var.get()
            if pattern == "Breathe":
                # Sine wave pulse (1.2.3 logic: gentle breathing)
                intensity = 40 + (math.sin(current_time * 2.5) + 1) * 80
            elif pattern == "Pulse":
                intensity = 200 if (int(current_time * 2) % 4 == 0) else 20
            elif pattern == "Soft Glow":
                intensity = 80
        
        self.led_mirror.itemconfig(self.led_circle, fill=self._get_led_color(intensity))

        # 2. PRESENCE STATE MACHINE
        if is_user_present:
            self.presence_confidence = 1.0
            self.hpd.inhibit_sleep(reason="User in Presence Zone")
            self.status_var.set("ZONE OCCUPIED")
            self.status_label.config(fg="#00ffcc")
        else:
            # Kitten Buffer (Confidence Decay)
            if self.presence_confidence > 0:
                # Decay over the set buffer time
                decay_per_tick = 0.1 / buffer_seconds # 100ms ticks
                self.presence_confidence -= decay_per_tick
                self.status_var.set(f"DECAYING: {int(self.presence_confidence * 100)}%")
                self.status_label.config(fg="#ffcc00")
            else:
                self.presence_confidence = 0
                self.hpd.allow_sleep()
                self.status_var.set("ZONE EMPTY")
                self.status_label.config(fg="#ff4444")

        # Update UI
        self.progress['value'] = max(0, self.presence_confidence * 100)
        self.root.after(100, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = PZDetectorApp(root)
    
    def on_closing():
        app.hpd.allow_sleep()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()