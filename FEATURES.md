# PZD Features & Usage Guide

This guide explains the features of the Presence Zone Detector and how to use them.

## Core Features

### 1. Presence Zone (PZ) Detection

The centerpiece of PZD is the **Presence Zone**—a configurable area within your camera's view where the system considers you "present."

**How it works:**
- Configurable rectangular region based on % of frame width/height
- Motion detection within this zone triggers "presence confirmed"
- User presence outside the zone doesn't affect the system
- Default zone: 70% of frame (cropped from center)

**Use case:** Prevent false triggers from pets, moving curtains, or background activity

**How to adjust:**
1. Launch PZD in calibration mode
2. Adjust the **"PZ Reach"** slider (0.1 = tight, 1.0 = full frame)
3. You'll see the blue rectangle overlay shrink/grow
4. Click **"FINISH SETUP & GLAZE"** when satisfied

### 2. Glazed Vision (Privacy-First Detection)

PZD uses **Glazed Vision**—a privacy-respecting motion detection method that uses extreme blur and downsampling to detect presence without capturing any biometric data.

**The process:**
1. Frame captured from webcam (640x480)
2. Downsampled to 20x15 (blur sensitivity pass)
3. Upscaled to 320x240 for display
4. Gaussian blur applied (99x99 kernel)
5. Only motion presence is detected—no facial features, eyes, or skin tones

**Privacy guarantee:**
- ✅ Detects if someone is in the zone
- ❌ Cannot identify who or what they are
- ❌ Cannot detect emotions, expressions, or activities
- ❌ No frames are ever saved to disk or sent over network

**Use case:** Workplace monitoring that respects employee privacy

### 3. Presence Confidence & Kitten Buffer

The **Kitten Buffer** is a grace period that smoothly transitions from "Occupied" to "Empty" instead of instantly locking your system.

**Why it exists:**
- You might temporarily step out of frame (bathroom, standing up, stretching)
- You might sit still (on a phone call, thinking, petting your cat)
- An instant lock would be frustrating and create "Auto-Lock Panic"

**How it works:**

```
User present and moving → Confidence = 1.0 (100%)
                           ↓
User stops/exits frame → Confidence decays
                           1.0 → 0.9 → 0.8 → ... → 0.0
                           ↓
Confidence reaches 0.0 → System locks (or allows sleep)
```

**Decay formula:**
```
Decay per 100ms = 0.1 / buffer_time_in_seconds
Example: 45-second buffer = 0.00222% decay per 100ms cycle
```

**Adjusting the buffer:**
1. Move the **"Kitten Buffer"** slider at the bottom
2. Range: 5 seconds (instant) to 600 seconds (10 minutes)
3. Recommended: 30-60 seconds for most workflows

| Buffer Time | Use Case |
|---|---|
| 5-10s | Rapid lock for security-sensitive work |
| 30-45s | Balanced for focus work + bathroom breaks |
| 60+ | Lenient for meetings where you stay mostly still |

### 4. Depth Score (Proximity Measurement)

The **Depth Score** measures how close you are to the camera based on the size of motion detected.

**Visual indicator:** The "DEPTH SCORE" text shows a number (0+)

**How it works:**
- Larger motion blobs = higher proximity (closer to camera)
- Small motion blobs = lower proximity (further from camera)
- Uses contour area math from motion-detection frame

**Use cases:**
- Verify the sensor is actually detecting you (not background)
- Adjust "Proximity Floor" to ignore small objects (dust, insects)

**Adjusting Proximity Floor:**
1. Use the **"Proximity Floor"** slider (1-200)
2. Move around while watching the Depth Score
3. Raise floor if you see false triggers from small movements
4. Lower floor if the system misses your presence

### 5. Multi-Camera Support

PZD supports multiple cameras on the same system (if you have multiple webcams).

**How to use:**
1. Plug in additional webcams
2. In PZD UI, use the **"Sensor Input"** dropdown
3. Select "Camera 0", "Camera 1", "Camera 2", etc.
4. Sensor reinitializes automatically

**Use cases:**
- Desk mounted camera (Camera 0) for detailed detection
- Secondary wide-angle camera (Camera 1) for meetings

### 6. Calibration Mode

Calibration mode provides visual feedback to help you set up the system correctly.

**Features in Calibration Mode:**
- Blue rectangle overlay shows your Presence Zone boundaries
- Real-time preview of the camera feed (not yet blurred)
- Yellow banner with "CALIBRATION MODE" label
- Live updates as you adjust sliders

**How to calibrate:**
1. Launch PZD—it starts in calibration mode
2. Adjust sliders to define your zone:
   - **PZ Reach:** Size of the detection zone
   - **Sensitivity:** Motion detection threshold
   - **Proximity Floor:** Minimum size to register movement
3. Position yourself in the zone and move around
4. Watch the "DEPTH SCORE" to ensure detection
5. Click **"FINISH SETUP & GLAZE"** to activate

### 7. Active Operating Modes

Once setup is complete, PZD has three visual states:

**🟢 PRESENCE CONFIRMED (Green LED)**
- You're in the zone and moving
- System is inhibiting sleep/lock
- Confidence: 100%

**🟡 DECAYING (Yellow LED)**
- You've exited or stopped moving
- Confidence is slowly decreasing
- System still preventing lock (grace period)
- Percentage shows remaining confidence

**🔴 ZONE EMPTY (Red LED)**
- Confidence reached 0%
- System allows lock/sleep
- Ready for security actions

### 8. System Tray Integration

PZD minimizes to the system tray for unobtrusive operation.

**How to use:**
1. Click the X button to minimize (not quit)
2. App appears in system tray (bottom-right on Windows, top-right on Mac)
3. Click tray icon to bring window back
4. Tray icon color reflects current state (Green/Yellow/Red)

**Use case:** Monitor presence in background while working in other apps

## Future Features (Roadmap)

### Guardian Mode (Act I-III)
- **Act I:** Immediate workstation lock when confidence reaches 0
- **Act II:** Keep critical processes alive (downloads, builds, renders)
- **Act III:** Disable network and allow sleep when process completes

### Global Hotkey (Panic-Kill)
- Emergency keystroke to manually lock/exit
- Useful for unplanned presence changes

### Audit Logging
- Timestamp events (lock time, confidence state changes)
- Generate "Welcome Back" notifications

### Web-Based Lite Version
- Browser-based alternative with Screen Wake Lock API
- No installation required

## Settings Reference

### UI Controls

| Control | Range | Default | Purpose |
|---------|-------|---------|---------|
| PZ Reach | 0.1–1.0 | 0.7 | Size of detection zone (% of frame) |
| Proximity Floor | 1–200 | 50 | Minimum motion size to register |
| Kitten Buffer | 5–600s | 45s | Grace period before lock |
| Sensor Input | Camera 0–3 | Camera 0 | Select active webcam |

### Advanced Settings (in code)

If you want to modify these, edit `app/main.py`:

```python
class GlazedSensor(threading.Thread):
    def __init__(self, ...):
        self.sensitivity = 350        # Motion threshold (↑ = less sensitive)
        self.pz_reach = 0.7           # PZ size as % of frame
        self.proximity_min = 50        # Contour area floor
        self.calibration_mode = True  # Display overlay
```

## Troubleshooting

**Q: "SENSOR BLOCKED OR IN USE"**
- Close other apps using your camera (Teams, Zoom, Discord)
- Try a different camera index from the dropdown
- Restart PZD

**Q: System locks/sleeps even when I'm present**
- Increase the **Proximity Floor** to prevent false negatives
- Ensure you're within the blue zone rectangle in calibration mode
- Try increasing **PZ Reach** to capture more of the frame

**Q: System never locks even when I'm gone**
- Decrease the **Kitten Buffer** (faster lock)
- Adjust **PZ Reach** smaller to increase sensitivity
- Verify "DEPTH SCORE" shows 0 when you're out of frame

**Q: High CPU usage**
- This is unusual—report this as a bug
- Ensure only one instance of PZD is running
- Check for frozen sensor thread in Task Manager/Activity Monitor

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.

---

**Getting started?** See [LOCAL_SETUP.md](LOCAL_SETUP.md) for installation, or [DEVELOPMENT.md](DEVELOPMENT.md) if you're setting up a development environment.
