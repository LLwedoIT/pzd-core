import time
import threading
import sys
import os
import subprocess
import math
import json
import cv2  # Requires: pip install opencv-python
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import webbrowser
from tkinter import messagebox
import pystray
import psutil
try:
    import keyboard  # Global hotkey support
except ImportError:
    keyboard = None

# Import new multi-sensor waterfall components
from hid_monitor import HIDMonitor
from presence_engine import PresenceEngine, PresenceState, StateChangeEvent
from app_awareness import AppAwarenessService
from config_service import ConfigService
from log_service import LogService
from network_service import NetworkService
from identity_service import IdentityService
from license_service import LicenseService

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

    def lock_workstation(self):
        """Act I: Lock the workstation immediately."""
        try:
            if self.is_windows:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                print(f"[Guardian] LOCKED WORKSTATION at {datetime.now().strftime('%H:%M:%S')}")
                return True
            elif self.is_macos:
                subprocess.run(['open', '-a', '/System/Library/CoreServices/ScreenSaverEngine.app'], check=False)
                print(f"[Guardian] LOCKED WORKSTATION at {datetime.now().strftime('%H:%M:%S')}")
                return True
        except Exception as e:
            print(f"[Guardian Lock Error] {e}")
            return False

class GuardianMode:
    """Manages the Three Acts of Guardian Mode: Lock, Sustain, Complete."""
    def __init__(self, hpd_manager, audit_log_path="audit_log.json", network_service=None, config=None, logger=None):
        self.hpd = hpd_manager
        self.network_service = network_service
        self.config = config
        self.logger = logger
        self.enabled = False
        self.guarded_process_pid = None
        self.guarded_process_name = None
        self.lock_triggered = False
        self.audit_log_path = audit_log_path
        self.audit_log = self._load_audit_log()
        self.last_cpu_check = 0
        self.cpu_idle_duration = 0
        
    def _load_audit_log(self):
        """Load audit log from disk or create new."""
        if os.path.exists(self.audit_log_path):
            try:
                with open(self.audit_log_path, 'r') as f:
                    return json.load(f)
            except: pass
        return {"events": []}
    
    def _save_audit_log(self):
        """Save audit log to disk."""
        try:
            with open(self.audit_log_path, 'w') as f:
                json.dump(self.audit_log, f, indent=2)
        except Exception as e:
            print(f"[Guardian Log Error] {e}")
    
    def log_event(self, event_type, details=""):
        """Log a Guardian Mode event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        self.audit_log["events"].append(event)
        self._save_audit_log()
        print(f"[Guardian Log] {event_type}: {details}")
    
    def act_i_lock_door(self, presence_confidence):
        """Act I: Lock the door when presence reaches 0."""
        if not self.enabled or self.lock_triggered:
            return False
        
        if presence_confidence <= 0:
            if self.hpd.lock_workstation():
                self.lock_triggered = True
                self.log_event("ACT_I_LOCK", f"Workstation locked. Presence confidence: {presence_confidence}")
                return True
        return False
    
    def act_ii_sustain_process(self, presence_confidence):
        """Act II: Keep guarded process alive while it runs."""
        if not self.enabled or self.guarded_process_pid is None:
            return False
        
        try:
            # Check if process still exists
            process = psutil.Process(self.guarded_process_pid)
            is_running = process.is_running()
            
            if is_running:
                # Keep inhibiting sleep while process is active
                self.hpd.inhibit_sleep()
                
                # Monitor CPU usage (log if idle < 1%)
                cpu_percent = process.cpu_percent(interval=0.1)
                if cpu_percent < 1.0:
                    self.cpu_idle_duration += 1
                else:
                    self.cpu_idle_duration = 0
                
                # If process has been < 1% CPU for 30+ seconds, consider it done
                if self.cpu_idle_duration >= 30:
                    print(f"[Guardian] Process {self.guarded_process_name} idle for too long, releasing...")
                    self.guarded_process_pid = None
                    self.guarded_process_name = None
                    self.cpu_idle_duration = 0
                    return True
                
                return True
            else:
                # Process ended - trigger Act III
                print(f"[Guardian] Process {self.guarded_process_name} completed")
                self.guarded_process_pid = None
                self.guarded_process_name = None
                self.cpu_idle_duration = 0
                return True
        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process no longer exists
            if self.guarded_process_pid:
                self.log_event("ACT_II_COMPLETE", f"Process {self.guarded_process_name} (PID {self.guarded_process_pid}) completed")
                self.guarded_process_pid = None
                self.guarded_process_name = None
                self.cpu_idle_duration = 0
            return True
        
        return False
    
    def act_iii_complete(self):
        """Act III: Turn out the lights - cleanup and allow sleep."""
        if not self.enabled:
            return False
        
        # Release sleep inhibition
        self.hpd.allow_sleep()
        self.log_event("ACT_III_COMPLETE", "Sleep inhibition released, hardware sleeping allowed")
        self.lock_triggered = False

        # Optional: Disable network adapters for security (Act III)
        if self.network_service and self.config:
            if self.config.get_bool("enableNetworkWiFiControl", False):
                disabled = self.network_service.disable_all()
                if disabled:
                    self.log_event("ACT_III_NETWORK_DISABLED", "Network adapters disabled")
                else:
                    self.log_event("ACT_III_NETWORK_FAILED", "Failed to disable network adapters")
        
        return True
    
    def set_guarded_process(self, process_pid, process_name):
        """Set the process to monitor (Act II)."""
        self.guarded_process_pid = process_pid
        self.guarded_process_name = process_name
        self.log_event("ACT_II_START", f"Monitoring process: {process_name} (PID {process_pid})")
    
    def get_running_processes(self):
        """Get list of user-accessible running processes."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append((proc.info['pid'], proc.info['name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(set(processes), key=lambda x: x[1])  # Remove duplicates, sort by name

class GlazedSensor(threading.Thread):
    def __init__(self, callback, camera_index=0):
        super().__init__(daemon=True)
        self.callback = callback
        self.camera_index = camera_index
        self.running = True
        self.paused = False
        self.last_gray = None
        self.motion_free_frames = 0
        self.motion_frames = 0
        self.cap = None
        
        # Adaptive FPS control (waterfall pattern)
        self.target_fps = 1          # Start at 1 FPS (idle)
        self.frame_count = 0
        self.motion_confidence = 0   # 0.0 to 1.0
        
        # Adjustable Params
        self.sensitivity = 350
        self.pz_reach = 0.7  
        self.proximity_min = 50 
        self.calibration_mode = True

    def run(self):
        try:
            # Brio/Windows often require cycling through backends
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF] if sys.platform.startswith('win') else [None]
            
            found = False
            for backend in backends:
                self.cap = cv2.VideoCapture(self.camera_index, backend) if backend else cv2.VideoCapture(self.camera_index)
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    ret, _ = self.cap.read()
                    if ret:
                        found = True
                        break
                self.cap.release()
                self.cap = None
            
            if not found:
                self.callback(None, False, 0, "CAMERA_FAILED")
                return

            while self.running:
                # POWER OPTIMIZATION: Check pause flag and skip entire processing
                if self.paused:
                    time.sleep(0.1)  # Sleep while paused, minimal CPU
                    continue

                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.5)
                    continue

                # 1. APPLY PZ REACH (Map the Zone)
                h, w, _ = frame.shape
                rw, rh = int(w * self.pz_reach), int(h * self.pz_reach)
                x1, y1 = (w - rw) // 2, (h - rh) // 2
                
                # WATERFALL PATTERN: Quick check first, expensive ops only if needed
                is_motion = False
                current_proximity = 0
                
                # FAST CHECK (2-3ms): Simple pixel delta comparison
                cropped_fast = frame[y1:y1+rh, x1:x1+rw]
                small_fast = cv2.resize(cropped_fast, (40, 30), interpolation=cv2.INTER_LINEAR)
                gray_fast = cv2.cvtColor(small_fast, cv2.COLOR_BGR2GRAY)
                gray_fast = cv2.GaussianBlur(gray_fast, (5, 5), 0)
                
                if self.last_gray is not None:
                    # Fast delta check - skip expensive ops 95% of the time
                    delta = cv2.absdiff(self.last_gray, gray_fast)
                    quick_motion = np.sum(delta) > 200  # Low threshold for early exit
                    
                    # EXPENSIVE CHECK: Only run if fast check passed
                    if quick_motion:
                        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            largest_contour = max(contours, key=cv2.contourArea)
                            current_proximity = cv2.contourArea(largest_contour)
                            if current_proximity > (self.proximity_min / 10):
                                if np.sum(thresh) > self.sensitivity:
                                    is_motion = True
                
                self.last_gray = gray_fast
                
                # Update motion confidence for adaptive FPS
                if is_motion:
                    self.motion_frames += 1
                    self.motion_free_frames = 0
                else:
                    self.motion_free_frames += 1
                    if self.motion_free_frames > 30:  # 30 frames without motion
                        self.motion_frames = 0
                
                # Adaptive FPS calculation based on motion
                if self.motion_frames > 5:
                    self.target_fps = 16.7      # Active motion: full FPS
                    self.motion_confidence = 1.0
                elif self.motion_free_frames < 5:
                    self.target_fps = 5         # Recent motion: medium FPS
                    self.motion_confidence = 0.6
                else:
                    self.target_fps = 1         # Idle: minimal FPS
                    self.motion_confidence = 0.1
                
                # Render display frame (only in calibration mode) or continue with minimal processing
                if self.calibration_mode:
                    display_frame = frame.copy()
                    cv2.rectangle(display_frame, (x1, y1), (x1+rw, y1+rh), (0, 255, 204), 2)
                    overlay = display_frame.copy()
                    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                    cv2.rectangle(overlay, (x1, y1), (x1+rw, y1+rh), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)
                    processed_frame = cv2.resize(display_frame, (320, 240))
                else:
                    # Active Mode: Crop and Glaze only on motion or frequently
                    if is_motion or self.motion_confidence > 0.5:
                        cropped = frame[y1:y1+rh, x1:x1+rw]
                        small = cv2.resize(cropped, (20, 15), interpolation=cv2.INTER_LINEAR)
                        glazed = cv2.resize(small, (320, 240), interpolation=cv2.INTER_NEAREST)
                        processed_frame = cv2.GaussianBlur(glazed, (99, 99), 0)
                    else:
                        processed_frame = None  # Skip frame generation in idle mode
                
                # Stabilization: simpler approach using motion counters
                stable_trigger = self.motion_frames > 2
                
                self.callback(processed_frame, stable_trigger, current_proximity)
                
                # Adaptive sleep: vary interval based on target FPS
                if self.target_fps > 0:
                    sleep_time = 1.0 / self.target_fps
                    time.sleep(sleep_time)
                else:
                    time.sleep(1.0)
        except Exception as e:
            print(f"[Sensor Error] {e}")
        finally:
            # Absolutely ensure camera is released with maximum force
            if self.cap is not None:
                try:
                    # Set properties to blank first to force release
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 0)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 0)
                    self.cap.release()
                except:
                    pass
                finally:
                    self.cap = None

    def stop(self):
        """Stop the sensor thread and ensure camera is released."""
        self.running = False
        # Daemon thread will be forcefully killed, but attempt cleanup first
        if self.cap is not None:
            try:
                # Set properties to blank first
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 0)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 0)
                self.cap.release()
                self.cap = None
            except:
                pass
    
    def pause(self):
        """Pause the sensor (reduce CPU to ~0% while keeping thread alive)."""
        self.paused = True
    
    def resume(self):
        """Resume the sensor from pause."""
        self.paused = False
        self.target_fps = 1  # Start at idle FPS when resuming

class App:
    def __init__(self, root):
        self.root = root
        
        # Initialize configuration and logging services
        self.config = ConfigService("config.json")
        self.logger = LogService(
            log_path=self.config.get_str("logPath", "logs/"),
            max_files=self.config.get_int("logMaxFiles", 10),
            level=self.config.get_str("logLevel", "INFO")
        )
        self.logger.info("PZD Application Started", "App")

        # License/trial check (optional)
        self.license = None
        if self.config.get_bool("enableLicenseCheck", True):
            self.license = LicenseService(
                trial_days=self.config.get_int("trialDays", 7),
                purchase_url=self.config.get_str("purchaseUrl", ""),
                logger=self.logger
            )
            self.license.record_check()
            if self.license.is_trial_expired():
                self.logger.warning("Trial expired; exiting", "LicenseService")
                purchase_url = self.config.get_str("purchaseUrl", "")
                if purchase_url:
                    open_now = messagebox.askyesno(
                        "Trial Expired",
                        "Your trial has expired. Open the purchase page now?"
                    )
                    if open_now:
                        webbrowser.open(purchase_url)
                else:
                    messagebox.showwarning("Trial Expired", "Your trial has expired.")
                self.root.quit()
                return
        
        # Initialize core services
        self.hpd = HPDManager()
        self.network_service = NetworkService(self.logger)
        self.guardian = GuardianMode(
            self.hpd,
            audit_log_path=self.config.get_str("auditLogPath", "audit_log.json"),
            network_service=self.network_service,
            config=self.config,
            logger=self.logger
        )
        self.presence_confidence = 1.0
        self.motion_active = False
        self.sensor_error = False
        self.current_camera_index = 0
        self.sensor = None
        self.last_prox = 0
        self.icon = None
        self.icon_thread = None
        
        self.root.title("PZDetector | Presence Zone Utility")
        self.root.geometry("520x1200")
        self.root.configure(bg="#030303")
        self.root.resizable(False, True)
        
        # Window minimize/restore events for power optimization
        self.root.bind("<Unmap>", lambda e: self._on_window_minimize())
        self.root.bind("<Map>", lambda e: self._on_window_restore())
        
        # Initialize multi-sensor waterfall components
        self.hid_monitor = HIDMonitor()
        self.app_awareness = AppAwarenessService()
        self.presence_engine = None  # Will be initialized after sensor starts
        self.identity_service = None
        self.identity_prompt_active = False
        self.identity_prompt_message = self.config.get_str("identityPromptMessage", "Confirm you're still here")
        if self.config.get_bool("enableBiometricVerification", False):
            self.identity_service = IdentityService(self.logger)
        
        self.setup_styles()
        self.build_ui()
        if self.guardian_var.get():
            self.toggle_guardian()
        self.setup_tray()
        self.setup_hotkey()
        self.start_sensor()
        if self.config.get_bool("enableAppAwareness", True):
            self.app_awareness.start()  # Start app awareness service
        self.logger.info("Application initialization complete", "App")
        self.update_loop()

    def setup_hotkey(self):
        """Setup global hotkey for Guardian Mode toggle (Ctrl+Alt+Shift+X)."""
        if not self.config.get_bool("enableGlobalHotkey", True):
            self.logger.info("Global hotkey disabled by config", "Hotkey")
            return
        if keyboard is None:
            print("[Hotkey] keyboard module not available, skipping global hotkey")
            return
        
        try:
            def hotkey_callback():
                """Toggle Guardian Mode when hotkey pressed."""
                if hasattr(self, 'guardian_var'):
                    current = self.guardian_var.get()
                    self.guardian_var.set(not current)
                    self.toggle_guardian()
                    print(f"[Hotkey] Guardian Mode toggled: {not current}")
            
            # Register global hotkey from config
            combo = self.config.get_str("globalHotkeyCombo", "ctrl+alt+shift+x")
            keyboard.add_hotkey(combo, hotkey_callback)
            print(f"[Hotkey] Global hotkey registered: {combo} to toggle Guardian Mode")
        except Exception as e:
            print(f"[Hotkey] Failed to register global hotkey: {e}")

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

        # Grace period banner (hidden by default)
        self.grace_banner = tk.Frame(self.root, bg="#332200")
        self.grace_label = tk.Label(
            self.grace_banner,
            text="WARNING: Locking soon",
            fg="#ffcc66",
            bg="#332200",
            font=("Helvetica", 9, "bold")
        )
        self.grace_label.pack(pady=2)
        self.grace_visible = False

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

        # === GUARDIAN MODE SECTION ===
        guardian_frame = tk.LabelFrame(self.root, text=" GUARDIAN MODE (Three Acts) ", fg="#ff6600", bg="#030303", padx=20, pady=15)
        guardian_frame.pack(fill="x", padx=60, pady=10)

        # Guardian Mode Enable Toggle
        initial_guardian = self.config.get_bool("enableGuardianMode", False)
        self.guardian_var = tk.BooleanVar(value=initial_guardian)
        self.guardian_check = tk.Checkbutton(guardian_frame, text="Enable Guardian Mode", variable=self.guardian_var, 
                                             command=self.toggle_guardian, fg="#ff6600", bg="#030303", selectcolor="#030303", 
                                             activebackground="#030303", activeforeground="#ff6600")
        self.guardian_check.pack(anchor="w", pady=(0, 10))

        # Process Selection (Act II)
        process_frame = tk.Frame(guardian_frame, bg="#030303")
        process_frame.pack(fill="x", pady=(0, 10))
        tk.Label(process_frame, text="Guard Process (Act II):", fg="#666", bg="#030303", font=("Helvetica", 9)).pack(side="left")
        
        self.process_var = tk.StringVar(value="None")
        self.process_selector = ttk.Combobox(process_frame, textvariable=self.process_var, state="readonly", width=30)
        self.process_selector.pack(side="left", padx=10, fill="x", expand=True)
        self.refresh_processes_btn = ttk.Button(process_frame, text="Refresh", command=self.refresh_process_list)
        self.refresh_processes_btn.pack(side="left", padx=5)

        # Audit Log Display
        log_frame = tk.Frame(guardian_frame, bg="#0a0a0a", height=100)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        tk.Label(log_frame, text="Audit Log:", fg="#666", bg="#0a0a0a", font=("Helvetica", 8)).pack(anchor="w", padx=5, pady=(5, 2))
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.audit_log_widget = tk.Text(log_frame, height=6, width=60, bg="#000", fg="#00ffcc", 
                                        font=("JetBrains Mono", 7), state="disabled", yscrollcommand=scrollbar.set)
        self.audit_log_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.audit_log_widget.yview)

        tk.Label(self.root, text="PEBCAK OPTIMIZED • GUARDIAN MODE ENABLED • PZDETECTOR.COM", 
                 fg="#222", bg="#030303", font=("Helvetica", 7, "bold")).pack(side="bottom", pady=15)

    def toggle_guardian(self):
        """Toggle Guardian Mode on/off."""
        self.guardian.enabled = self.guardian_var.get()
        if self.guardian.enabled:
            print("[Guardian] Guardian Mode ENABLED")
            self.guardian.log_event("GUARDIAN_ENABLED", "Guardian Mode activated")
        else:
            print("[Guardian] Guardian Mode DISABLED")
            self.guardian.log_event("GUARDIAN_DISABLED", "Guardian Mode deactivated")
            self.guardian.act_iii_complete()

    def refresh_process_list(self):
        """Refresh the process list dropdown."""
        processes = self.guardian.get_running_processes()
        process_names = [f"{name} (PID: {pid})" for pid, name in processes]
        self.process_selector['values'] = ["None"] + process_names
        self.process_selector.current(0)

    def on_process_selected(self, event=None):
        """Handle process selection from dropdown."""
        selection = self.process_var.get()
        if selection and selection != "None":
            try:
                pid = int(selection.split("(PID: ")[1].rstrip(")"))
                name = selection.split(" (PID:")[0]
                self.guardian.set_guarded_process(pid, name)
            except (ValueError, IndexError):
                pass

    def update_audit_log_display(self):
        """Update the audit log widget with recent events."""
        self.audit_log_widget.config(state="normal")
        self.audit_log_widget.delete("1.0", "end")
        
        if self.guardian.audit_log["events"]:
            # Show last 20 events
            for event in self.guardian.audit_log["events"][-20:]:
                timestamp = event.get("timestamp", "").split("T")[1].split(".")[0] if "T" in event.get("timestamp", "") else ""
                event_type = event.get("type", "")
                details = event.get("details", "")
                log_line = f"[{timestamp}] {event_type}: {details}\n"
                self.audit_log_widget.insert("end", log_line)
        
        self.audit_log_widget.see("end")
        self.audit_log_widget.config(state="disabled")

    def create_icon_image(self, color):
        image = Image.new('RGB', (64, 64), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse([(4, 4), (60, 60)], fill=color)
        return image

    def setup_tray(self):
        self.icons = {
            'active': self.create_icon_image('#00ffcc'),
            'warning': self.create_icon_image('#ffff00'),
            'locked': self.create_icon_image('#ff0000'),
            'paused': self.create_icon_image('#999999'),
            'empty': self.create_icon_image('#ff6600')
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
    
    def _on_presence_state_changed(self, event: StateChangeEvent):
        """Handle presence engine state changes."""
        msg = f"State: {event.old_state.value} → {event.new_state.value}"
        self.logger.info(msg, "PresenceEngine")
        self.guardian.log_event("PRESENCE_STATE_CHANGE", msg)
    
    def _on_lock_triggered(self):
        """Handle lock trigger from presence engine."""
        self.logger.warning("Lock triggered by presence engine", "PresenceEngine")
        if self.guardian.enabled:
            self.guardian.act_i_lock_door(0)  # Presence confidence 0 = lock
    
    def _on_grace_period_started(self):
        """Handle grace period started from presence engine."""
        self.logger.info("Grace period started - warning state", "PresenceEngine")

    def _on_identity_prompt(self, message: str):
        """Handle Windows Hello prompt event."""
        self.identity_prompt_active = True
        self.logger.info("Windows Hello verification requested", "IdentityService")
    
    def _on_meeting_started(self):
        """Handle meeting app detected."""
        self.logger.info("Meeting app detected - pausing presence detection", "AppAwareness")
        if self.presence_engine:
            self.presence_engine.pause()
            self.guardian.log_event("MEETING_DETECTED", "Auto-paused presence detection")
    
    def _on_meeting_stopped(self):
        """Handle meeting app closed."""
        self.logger.info("Meeting app stopped - resuming presence detection", "AppAwareness")
        if self.presence_engine:
            self.presence_engine.resume()
            self.guardian.log_event("MEETING_ENDED", "Resumed presence detection")

    def _on_window_minimize(self):
        """Pause sensor when window minimizes to save power."""
        if hasattr(self, 'sensor') and self.sensor:
            try:
                self.sensor.pause()
            except:
                pass
        if hasattr(self, 'presence_engine') and self.presence_engine:
            try:
                self.presence_engine.pause()
            except:
                pass
    
    def _on_window_restore(self):
        """Resume sensor when window is restored."""
        if hasattr(self, 'sensor') and self.sensor:
            try:
                self.sensor.resume()
            except:
                pass
        if hasattr(self, 'presence_engine') and self.presence_engine:
            try:
                self.presence_engine.resume()
            except:
                pass

    def quit_app(self):
        """Shutdown and exit the application."""
        import gc
        import time
        try:
            self.icon.stop()
        except:
            pass
        # Stop sensor first
        if self.sensor:
            try:
                self.sensor.stop()
            except:
                pass
        # Release sleep inhibition
        try:
            self.hpd.allow_sleep()
        except:
            pass
        # Re-enable network adapters on exit if we disabled them
        try:
            if self.config.get_bool("enableNetworkWiFiControl", False):
                self.network_service.enable_all()
        except:
            pass
        # Clean up
        gc.collect()
        time.sleep(0.2)
        # Shutdown gracefully
        try:
            self.root.quit()
        except:
            pass
        
        sys.exit(0)

    def start_sensor(self):
        import gc
        if self.sensor: 
            self.sensor.stop()
            # Force cleanup of old sensor before creating new one
            gc.collect()
        self.sensor_error = False
        self.sensor = GlazedSensor(self.on_sensor_data, camera_index=self.current_camera_index)
        
        # Apply configuration values to sensor
        self.sensor.pz_reach = self.config.get_float("pz_reach", 0.7)
        self.sensor.proximity_min = self.config.get_int("proximityMin", 50)
        self.sensor.sensitivity = self.config.get_int("cameraSensitivity", 350)
        
        if hasattr(self, 'setup_btn') and "RE-ENTER" in self.setup_btn.cget('text'):
            self.sensor.calibration_mode = False
        self.sensor.start()
        self.logger.info(f"Camera sensor started (index={self.current_camera_index})", "Sensor")
        
        # Initialize PresenceEngine with HID monitor and camera sensor
        timeout = self.config.get_int("lockTimeoutSeconds", 60)
        warning_threshold = self.config.get_int("warningThresholdSeconds", 10)
        self.presence_engine = PresenceEngine(
            hid_monitor=self.hid_monitor,
            camera_sensor=self.sensor,
            lock_timeout_seconds=timeout,
            warning_threshold_seconds=warning_threshold,
            identity_service=self.identity_service,
            identity_prompt_message=self.identity_prompt_message
        )
        
        # Register event handlers
        self.presence_engine.on_state_changed(self._on_presence_state_changed)
        self.presence_engine.on_lock_triggered(self._on_lock_triggered)
        self.presence_engine.on_grace_period_started(self._on_grace_period_started)
        self.presence_engine.on_identity_prompt(self._on_identity_prompt)
        
        # Register app awareness handlers
        self.app_awareness.on_meeting_started(self._on_meeting_started)
        self.app_awareness.on_meeting_stopped(self._on_meeting_stopped)

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
                self.refresh_process_list()
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
        # Breathing pulse: sine wave from 100 to 255 for brightness
        if self.presence_confidence > 0.05:
            brightness = int(128 + 127 * math.sin(t * 2))
            brightness = max(100, min(255, brightness))  # Clamp between 100-255
            led_color = f'#00{brightness:02x}ff'  # Cyan pulse: red=00, green=brightness, blue=ff
        else:
            led_color = '#001a33'  # Dim cyan when no confidence
        self.led_canvas.itemconfig(self.led_dot, fill=led_color)

        current_icon = self.icon.icon
        new_icon_name = 'empty'

        # === NEW: Presence Engine Waterfall Detection ===
        if self.presence_engine and not (self.sensor and self.sensor.calibration_mode):
            # Tick the presence engine (stage 1: HID check, stage 2+: camera if needed)
            self.presence_engine.tick()
            
            # Update UI based on presence engine state
            engine_state = self.presence_engine.current_state
            
            if engine_state == PresenceState.ACTIVE:
                self.status_var.set(f"ACTIVE - {self.presence_engine.seconds_remaining}s")
                new_icon_name = 'active'
                self.hpd.inhibit_sleep()
                self.presence_confidence = 1.0
                self.identity_prompt_active = False
                if self.grace_visible:
                    self.grace_banner.pack_forget()
                    self.grace_visible = False
            
            elif engine_state == PresenceState.WARNING:
                if self.identity_prompt_active:
                    self.status_var.set("Windows Hello verification required")
                else:
                    self.status_var.set(f"⚠ WARNING - {self.presence_engine.seconds_remaining}s until lock")
                new_icon_name = 'warning'
                self.hpd.inhibit_sleep()
                self.presence_confidence = 0.5
                if not self.grace_visible:
                    self.grace_banner.pack(fill="x", padx=60, pady=(0, 10))
                    self.grace_visible = True
                if self.identity_prompt_active:
                    self.grace_label.config(text="Verify with Windows Hello to stay unlocked")
                else:
                    self.grace_label.config(
                        text=f"WARNING: Locking in {self.presence_engine.seconds_remaining}s"
                    )
            
            elif engine_state == PresenceState.LOCKING:
                self.status_var.set("🔒 LOCKED")
                new_icon_name = 'locked'
                self.hpd.allow_sleep()
                self.presence_confidence = 0.0
                self.identity_prompt_active = False
                if self.grace_visible:
                    self.grace_banner.pack_forget()
                    self.grace_visible = False
            
            elif engine_state == PresenceState.PAUSED:
                pause_display = self.presence_engine.get_state_display()
                self.status_var.set(f"⏸ {pause_display}")
                new_icon_name = 'paused'
                self.presence_confidence = 0.5
                self.identity_prompt_active = False
                if self.grace_visible:
                    self.grace_banner.pack_forget()
                    self.grace_visible = False
        
        # === Legacy logic for backward compatibility ===
        elif self.sensor_error:
            self.status_var.set("HARDWARE ERROR")
            new_icon_name = 'empty'
            if self.grace_visible:
                self.grace_banner.pack_forget()
                self.grace_visible = False
        elif not self.sensor or (self.sensor and self.sensor.calibration_mode):
            self.status_var.set("CALIBRATING...")
            new_icon_name = 'warning'
            if self.grace_visible:
                self.grace_banner.pack_forget()
                self.grace_visible = False
        elif self.motion_active:
            self.presence_confidence = 1.0
            self.hpd.inhibit_sleep()
            self.status_var.set("PRESENCE CONFIRMED")
            self.motion_active = False
            new_icon_name = 'active'
        else:
            decay = 0.1 / self.buffer_scale.get()
            self.presence_confidence = max(0, self.presence_confidence - decay)
            
            # === GUARDIAN MODE ACT I: Lock when confidence reaches 0 ===
            if self.guardian.enabled and self.presence_confidence <= 0:
                if self.guardian.act_i_lock_door(self.presence_confidence):
                    new_icon_name = 'locked'
                    self.status_var.set("🔒 LOCKED (Guardian Mode)")
            
            # === GUARDIAN MODE ACT II: Sustain guarded process ===
            if self.guardian.enabled and self.guardian.guarded_process_pid:
                completed = self.guardian.act_ii_sustain_process(self.presence_confidence)
                if completed:
                    self.guardian.act_iii_complete()
            
            if self.presence_confidence <= 0 and not self.guardian.lock_triggered:
                self.hpd.allow_sleep()
                self.status_var.set("ZONE EMPTY")
                new_icon_name = 'empty'
            elif self.presence_confidence <= 0 and self.guardian.lock_triggered:
                new_icon_name = 'locked'
            else:
                self.status_var.set(f"DECAYING: {int(self.presence_confidence*100)}%")
                new_icon_name = 'warning'
        
        if self.guardian.enabled and self.guardian.lock_triggered:
            new_icon_name = 'locked'

        if self.icons[new_icon_name] != current_icon:
            self.icon.icon = self.icons[new_icon_name]

        self.progress['value'] = self.presence_confidence * 100
        
        # Update process selection binding
        self.process_selector.bind("<<ComboboxSelected>>", self.on_process_selected)
        
        # Update audit log every ~1 second
        self.update_audit_log_display()

        
        self.root.after(100, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
