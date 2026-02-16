# PZD Code Standards

This document defines coding conventions and best practices for the PZD project.

## Core Principles

### 1. Privacy First (Glazed Vision)

**Rule: Never process, save, or transmit raw video frames.**

✅ **Allowed:**
```python
# Blur and downsample the frame
small = cv2.resize(cropped, (20, 15), interpolation=cv2.INTER_LINEAR)
glazed = cv2.resize(small, (320, 240), interpolation=cv2.INTER_NEAREST)
blurred = cv2.GaussianBlur(glazed, (99, 99), 0)
```

❌ **Not Allowed:**
```python
# Don't save frames to disk
cv2.imwrite("debug_frame.jpg", frame)

# Don't send frames over network
requests.post("https://api.example.com/analyze", data=frame)

# Don't process facial features
face_cascade = cv2.CascadeClassifier(...)
faces = face_cascade.detectMultiScale(frame)
```

### 2. Efficiency

- **Sensor Thread FPS:** Target 10-15 FPS (~66-100ms per frame)
- **UI Update Rate:** 100ms updates for responsiveness
- **Memory:** Avoid storing large frame buffers
- **CPU:** Monitor processor usage; typical should be <5% when idle

### 3. Naming Conventions

Use pzd/hpd terminology consistently:

| Term | Definition | Example Usage |
|------|-----------|---|
| **PZ** | Presence Zone—the active detection area | `pz_reach`, `in_pz` |
| **HPD** | Human Presence Detection | `HPDManager`, `hpd_state` |
| **Motion** | Frame-to-frame change detection | `is_motion`, `motion_history` |
| **Proximity** | Distance metric (contour area) | `current_proximity`, `proximity_min` |
| **Confidence** | Presence certainty (0.0-1.0) | `presence_confidence`, `confidence_decay` |
| **Glazed** | Blurred/downsampled vision | `glazed_frame`, `glaze()` |
| **Kitten Buffer** | Decay grace period | `buffer_scale`, `decay_rate` |

### 4. Code Style

#### Python Version
- **Target:** Python 3.8+
- **Use f-strings:** `f"Status: {status}"` not `"Status: {}".format(status)`
- **Type hints (preferred but optional):** `def process_frame(frame: np.ndarray) -> bool:`

#### Formatting
- **Indentation:** 4 spaces (never tabs)
- **Line length:** 100 characters preferred, 120 maximum
- **Imports:** Group standard library, third-party, local
  ```python
  import time
  import threading
  import sys
  
  import cv2
  import numpy as np
  
  from my_module import helper_function
  ```

#### Naming
```python
# Classes: PascalCase
class HPDManager:
    pass

class GlazedSensor(threading.Thread):
    pass

# Functions/Methods: snake_case
def calculate_proximity():
    pass

def on_sensor_data(self):
    pass

# Constants: UPPER_SNAKE_CASE
BLUR_KERNEL_SIZE = (99, 99)
SENSITIVITY_THRESHOLD = 350
DEFAULT_CAMERA_INDEX = 0

# Private members: _leading_underscore
self._internal_state = False
self._cache = None
```

## Docstring Standards

### Class Docstrings

```python
class GlazedSensor(threading.Thread):
    """
    Background thread for privacy-first motion detection.
    
    Captures frames from webcam, applies Glazed Vision (blur+downsample),
    and detects motion using frame differencing.
    
    Attributes:
        callback (callable): Function to call with sensor data (frame, motion, proximity)
        camera_index (int): Webcam index (0, 1, 2, etc.)
        sensitivity (int): Motion detection threshold (default 350)
        pz_reach (float): Presence Zone size as % of frame (0.1-1.0)
        proximity_min (int): Minimum contour area to register proximity
        calibration_mode (bool): Display zone overlay if True
    """
    pass
```

### Method Docstrings

```python
def inhibit_sleep(self) -> None:
    """
    Prevent OS from locking or sleeping.
    
    Windows: Calls SetThreadExecutionState() to inhibit display sleep.
    macOS: Spawns caffeinate subprocess.
    
    Should only be called when presence confidence > 0.5.
    """
    pass

def on_sensor_data(self, frame, motion: bool, proximity: float, error: str = None) -> None:
    """
    Callback handler for sensor data.
    
    Args:
        frame (np.ndarray): Display-ready frame (320x240, RGB). None on error.
        motion (bool): True if motion detected in current frame.
        proximity (float): Contour area (0+). Larger = closer to camera.
        error (str, optional): Error message if sensor failed. None on success.
    """
    pass
```

### Functions

```python
def calculate_decay(confidence: float, buffer_seconds: float) -> float:
    """
    Calculate per-tick confidence decay.
    
    Args:
        confidence: Current confidence level (0.0 to 1.0)
        buffer_seconds: Kitten Buffer duration in seconds
    
    Returns:
        Decay amount per 100ms update cycle
    """
    return 0.1 / buffer_seconds
```

## Comments

Use comments sparingly; prefer clear code + docstrings:

```python
# ✅ GOOD - Explains why
if current_proximity > proxim_min / 10:
    # Threshold scaled down because calc_small is 10x smaller than input
    if np.sum(thresh) > self.sensitivity:
        is_motion = True

# ❌ BAD - States the obvious
is_motion = True  # Set is_motion to True
```

## Error Handling

All OS-level calls should handle exceptions:

```python
def inhibit_sleep(self):
    if self.lock_inhibited:
        return
    try:
        if self.is_windows:
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000001 | 0x00000002)
        elif self.is_macos:
            self.caffeinate_process = subprocess.Popen(['caffeinate', '-i'])
        self.lock_inhibited = True
    except Exception as e:
        print(f"[HPD Error] {e}")
        # Don't crash; allow graceful degradation
```

## Testing Standards

### What Should Be Tested

1. **Sensor initialization** - Different camera indices and backends
2. **Presence confidence decay** - Verify Kitten Buffer math
3. **UI updates** - Status text, LED color, progress bar
4. **State transitions** - Active → Decaying → Empty
5. **Configuration persistence** - Settings persist across runs

### What Should NOT Be Tested

- Frame capture and processing (OpenCV library tests)
- OS-specific calls (SetThreadExecutionState, caffeinate)—document expected behavior instead

### Testing Locally

```bash
# Test calibration mode
python app/main.py
# Verify overlay appears, sliders work, status updates

# Test different camera indices
# Use dropdown to switch cameras

# Test decay
# Set buffer to 5 seconds, exit frame, watch confidence drop from 100→0
```

## No Data Logging

DO NOT:
- Log frame data: `print(frame)`
- Log pixel values: `print(pixel[0], pixel[1], pixel[2])`
- Save debug images: `cv2.imwrite()`
- Send frames over network

DO:
- Log metadata: `print(f"Proximity: {proximity}, Confidence: {confidence}")`
- Log state changes: `print(f"State: {self.status}")`
- Log errors and exceptions: `except Exception as e: print(e)`

## Configuration

Hardcoded values should be constants at the top of the file:

```python
# Sensor parameters
BLUR_KERNEL_SIZE = (99, 99)
SENSITIVITY_DEFAULT = 350
PZ_REACH_DEFAULT = 0.7
PROXIMITY_MIN_DEFAULT = 50
CALIBRATION_MODE_DEFAULT = True

# UI parameters
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 980
COLOR_ACCENT = "#00ffcc"
COLOR_BG = "#030303"
COLOR_DANGER = "#ff0000"

# Performance
SENSOR_FPS = 12
UI_UPDATE_MS = 100
```

## Git Commit Messages

Follow the conventional commits format:

```
type(scope): subject

body

footer
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (formatting, missing semicolons)
- `refactor` - Code refactoring without feature changes
- `test` - Test additions/updates
- `chore` - Build, dependencies, tooling
- `perf` - Performance improvements

**Examples:**
```
feat(sensor): implement blur-based privacy mode

perf(ui): optimize LED color calculation using lookup table

fix(calibration): resolve camera backend cycling on Windows

docs(setup): add troubleshooting guide for common issues
```

## Review Checklist

Before requesting code review, ensure:

- [ ] Code follows this style guide
- [ ] All Public methods have docstrings
- [ ] No hardcoded secrets or API keys
- [ ] No frame data logged or saved
- [ ] Application runs without errors: `python app/main.py`
- [ ] Commit messages follow conventional commits
- [ ] No unnecessary dependencies added
- [ ] Changes respect Glazed Vision privacy principle

---

**Questions?** See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup and examples.
