# Development Guide for PZD

This guide covers setting up your development environment, understanding the codebase, and common development tasks.

## Prerequisites

- **Python 3.8 or higher**
- **Git**
- **A webcam** (for testing sensor functionality)
- **Windows 10+, macOS 10.14+, or Linux with X11** (for OS kernel integration)

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/LLwedoIT/pzd-core.git
cd pzd-core
```

### 2. Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r app/requirements.txt
```

**Dependency Breakdown:**
- `opencv-python` (>=4.8.0) - Computer vision and motion detection
- `numpy` (>=1.24.0) - Numerical computing for frame processing
- `Pillow` (>=10.0.0) - Image processing for UI display
- `pystray` (>=0.19.0) - System tray integration

### 4. Verify Installation

```bash
python app/main.py
```

You should see the PZDetector window with "CALIBRATION MODE" banner.

## Project Structure

```
pzd-core/
├── app/
│   ├── main.py              # Main application (HPDManager, GlazedSensor, App classes)
│   └── requirements.txt      # Python dependencies
├── web/
│   └── index.html           # Landing page (Netlify hosted)
├── docs/                    # Documentation (future)
├── .github/
│   └── workflows/           # CI/CD pipelines (to be created)
├── README.md                # Project overview
├── ARCHITECTURE.md          # Monorepo and infra decisions
├── DEVELOPMENT.md           # This file
├── CONTRIBUTING.md          # Contributor guidelines
└── [other documentation]
```

## Understanding the Codebase

### Core Modules in app/main.py

**HPDManager**
- Manages OS-level sleep inhibition
- Windows: Uses `ctypes.windll.kernel32.SetThreadExecutionState()`
- macOS: Uses `caffeinate` subprocess

**GlazedSensor (threading.Thread)**
- Captures frames from webcam at ~12 FPS
- Implements "Glazed Vision" privacy (99x99 Gaussian blur + downsampling)
- Computes motion detection and proximity (contour area = "Depth Score")
- Runs in background thread to avoid blocking UI

**App (main UI)**
- Tkinter-based GUI with dark "cyber-industrial" aesthetic
- Manages presence confidence decay (the "Kitten Buffer")
- Displays real-time sensor feed and metrics
- Controls system tray integration

### Key Concepts

**Presence Zone (PZ)**
- Configurable region where the user is considered "active"
- Defined as percentage of frame width/height (`pz_reach` parameter)
- Default: 70% of frame (cropped from center)

**Glazed Vision**
- Privacy-first motion detection
- Captured frame → 20x15 downsampling → 99x99 Gaussian blur → upscale to 320x240
- Only motion presence is detected, never facial features or biometrics

**Kitten Buffer**
- Confidence decay from 1.0 (active) to 0.0 (empty)
- Decay rate: `0.1 / buffer_time_in_seconds`
- Example: 45-second buffer = ~0.2% decay per 100ms update

**Depth Score**
- Contour area from motion frame (40x30 size)
- Larger movement/objects = higher proximity score
- Used to visualize how close user is to camera

## Running and Testing

### Basic Run
```bash
python app/main.py
```

### Testing Different Scenarios

**1. Camera Initialization**
```bash
# Cycles through CAP_DSHOW and CAP_MSMF backends on Windows
# Check the calibration overlay appears correctly
python app/main.py
```

**2. Calibration Mode**
- Initial state displays rectangle overlay showing PZ boundaries
- Adjust "PZ Reach" slider to change zone size
- Adjust "Proximity Floor" to filter out background noise
- Click "FINISH SETUP & GLAZE" to switch to active mode

**3. Active Mode**
- Frame shows Glazed (blurred) vision
- Depth Score updates based on motion proximity
- Status shows "PRESENCE CONFIRMED", "DECAYING", or "ZONE EMPTY"
- LED indicator (top-right) pulses when confident

**4. Kitten Buffer Decay**
- Set buffer to 5 seconds for quick testing
- Move out of frame, observe confidence drop
- Green → Yellow → Red indicator transitions

**5. Camera Switching**
```bash
# In UI, use "Sensor Input" dropdown
# Change from Camera 0 to Camera 1, etc.
# Sensor should reinitialize without crashing
```

## Common Development Tasks

### Adding a New UI Element

1. In the `build_ui()` method, create a tkinter widget:
   ```python
   new_label = tk.Label(
       self.root, 
       text="New Feature",
       fg="#00ffcc",
       bg="#030303",
       font=("Helvetica", 10)
   )
   new_label.pack(pady=10)
   ```

2. Update the `update_loop()` method to refresh its state:
   ```python
   def update_loop(self):
       # ... existing code ...
       new_label.config(text=f"Updated: {some_value}")
       self.root.after(100, self.update_loop)
   ```

### Modifying Sensor Parameters

Parameters are stored in the `GlazedSensor` class:

```python
self.sensitivity = 350           # Motion threshold
self.pz_reach = 0.7              # Zone crop percentage
self.proximity_min = 50           # Contour area floor
self.calibration_mode = True      # Overlay display
```

These are exposed as UI sliders and updated in `update_loop()`:
```python
self.sensor.pz_reach = self.reach_scale.get()
self.sensor.proximity_min = self.prox_scale.get()
```

### Adding Privacy-Respecting Logging

PZD should never log frame content. Safe logging:

```python
# ✅ GOOD - Logs metadata only
print(f"[PZD] Motion detected. Proximity: {proximity}, Confidence: {self.presence_confidence}")

# ❌ BAD - Would leak visual data
print(f"[PZD] Frame shape: {frame.shape}, data: {frame}")
```

### Testing on Different Platforms

**Windows 10/11:**
```bash
python app/main.py
# Verify: SetThreadExecutionState is called, sleep inhibition works
```

**macOS:**
```bash
# May need to install caffeinate (included in macOS)
python app/main.py
# Check Activity Monitor for caffeinate process when active
```

**Linux:**
```bash
# Note: GUI requires X11 or Wayland
python app/main.py
# Sleep inhibition may not work on all distros—document limitations
```

## Debugging

### Camera Issues

If you see "SENSOR BLOCKED OR IN USE":
1. Check other apps using camera (Teams, Zoom, Discord)
2. Try different camera index: Change "Sensor Input" dropdown
3. Verify OpenCV backend on Windows (CAP_DSHOW vs CAP_MSMF)

### High CPU Usage
- Frame size is set to 640x480 for balance
- Sensor runs at ~12 FPS (100ms updates)
- If CPU >5%, check if multiple sensor threads are running

### LED Not Pulsing
- Verify `update_loop()` is running (status text updates)
- Check `sine_wave_signaling` math in the LED color calculation
- Confirm tkinter canvas is created without hiding it

## Common Pitfalls

1. **Don't save frames to disk** - Violates Glazed Vision privacy principle
2. **Don't hardcode API keys or secrets** - Use environment variables or GitHub Secrets
3. **Don't use blocking operations in main thread** - The sensor already runs on separate thread
4. **Don't remove motion_history stabilization** - Prevents flickering between states
5. **Don't change blur kernel size below 99x99** - Risks exposing facial features

## Next Steps

- Read [CODE_STANDARDS.md](CODE_STANDARDS.md) for coding conventions
- Check [ROADMAP.md](ROADMAP.md) for planned features
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) when submitting changes
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## References

- [OpenCV Python API](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Threading in Python](https://docs.python.org/3/library/threading.html)
- [pystray](https://github.com/moses-palmer/pystray)

---

Have questions? Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open a GitHub Discussion.
