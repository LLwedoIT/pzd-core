# PZDetector™ Troubleshooting Guide

**By Chair-to-Keyboard™** | *The Human Centric Software Development Company*

Common issues and solutions for PZDetector™ and the Presence Zone™ standard.

## Installation & Setup

### "ModuleNotFoundError: No module named 'cv2'"

**Cause:** OpenCV not installed  
**Solution:**
```bash
pip install -r app/requirements.txt
```

If that fails:
```bash
pip install opencv-python numpy Pillow pystray
```

Verify installation:
```bash
python -c "import cv2; print(cv2.__version__)"
```

### "No module named 'tkinter'"

**Windows:** Tkinter is included with Python. Reinstall Python and ensure "tcl/tk" is checked.

**macOS:** Install via Homebrew:
```bash
brew install python-tk@3.11  # or your Python version
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo yum install python3-tkinter
```

### "Permission denied" on macOS

**Cause:** `caffeinate` command requires permissions  
**Solution:**
- Grant Terminal Full Disk Access (System Preferences > Security & Privacy)
- Or use `sudo python app/main.py` once to grant permissions

---

## Camera & Sensor Issues

### "SENSOR BLOCKED OR IN USE"

This is the most common issue. The camera is either:
1. Already in use by another application
2. Has exclusive hardware lock
3. Driver issue

**Solutions (in order):**

1. **Close other apps using camera:**
   - Close Teams, Zoom, Discord, OBS, or any video conferencing software
   - Close any browser tabs with webcam access (check under Firefox/Chrome settings)
   - Restart your computer if nothing works

2. **Try a different camera:**
   - In PZD UI, change "Sensor Input" dropdown to Camera 1, 2, or 3
   - If available, this might be a different physical port or USB hub
   ```bash
   # List connected cameras:
   # Windows: Use Device Manager
   # macOS: System Report > USB
   # Linux: v4l2-ctl --list-devices
   ```

3. **Restart PZD:**
   - Close completely (Quit from tray menu, not just minimize)
   - Wait 2-3 seconds
   - Relaunch

4. **Check Windows backend (Windows only):**
   - PZD tries CAP_DSHOW and CAP_MSMF automatically
   - If errors appear in console, note which backend failed
   - Some cameras prefer specific backends

5. **Update camera drivers:**
   - Windows: Device Manager > Cameras > Right-click > Update driver
   - macOS: Check for firmware updates from camera manufacturer
   - Linux: Update v4l2 drivers

6. **Try a different USB port:**
   - Unplug camera
   - Wait 5 seconds
   - Plug into different USB port
   - Restart PZD

### Camera shows grey or black feed

**Possible causes:**
- Camera not initialized yet (wait 2-3 seconds)
- Camera pointed at something dark
- Lens cap still on

**Solutions:**
1. Wait - initialization takes a moment
2. Remove lens cap
3. Point camera at bright area (window, lamp)
4. Try different camera from dropdown
5. Restart PZD

### Frame rate too low / choppy feed

**Cause:** CPU throttling or camera processing bottleneck

**Solutions:**
1. Close background applications (Chrome, Slack, etc.)
2. Disable other webcam-using apps
3. Check Task Manager/Activity Monitor for high CPU processes
4. Try a different camera (Camera 1, 2, etc.) if available

### "CAMERA_FAILED" error

**Cause:** OpenCV couldn't open camera after trying all backends

**Solutions:**
1. Verify camera is physically connected (check Device Manager/System Report)
2. Try different USB port
3. Restart your OS
4. Update OpenCV:
   ```bash
   pip install --upgrade opencv-python
   ```
5. Check camera manufacturer's software (may have own driver installer)

---

## Motion Detection Issues

### System locks even when I'm working (false negatives)

The system can't detect your presence.

**Debugging steps:**
1. In **Calibration Mode**, check:
   - Is the blue rectangle in the right position?
   - Are you within the rectangle when moving?
   - Does "DEPTH SCORE" change when you move?

2. **If DEPTH SCORE stays at 0:**
   - Your movement isn't registering
   - **Lower "Proximity Floor"** slider (to ~10)
   - **Increase "PZ Reach"** slider (to ~0.9)
   - Try moving more deliberately (larger gestures)

3. **If DEPTH SCORE updates but system still locks:**
   - Camera might be too far away
   - Reduce "Proximity Floor" further
   - Move closer to camera
   - Check lighting (better lighting = better detection)

4. **Check "Sensitivity" (code only):**
   ```python
   # In app/main.py, GlazedSensor class:
   self.sensitivity = 350  # Lower = more sensitive (try 300)
   ```

### System never locks (false positives)

The system sees presence when you're gone.

**Debugging steps:**
1. Move out of the frame completely
2. Wait 5 seconds
3. Verify "DEPTH SCORE" reaches 0
4. Verify LED turns red (confidence hits 0%)
5. Then wait—system should lock after the Kitten Buffer expires

**If still not working:**
1. **Decrease "Kitten Buffer"** (faster decay):
   - Set to 5-10 seconds for testing
   - Watch the decaying percentage count down
   - Confirm it reaches 0 and status says "ZONE EMPTY"

2. **Reduce "PZ Reach"** if background noise is triggering:
   - Set to 0.5 to focus on center of frame
   - This helps if pets, fans, or curtains cause false triggers

3. **Increase "Proximity Floor":**
   - Small movements (like a ceiling fan) shouldn't trigger
   - Try 75-100 if you have lots of background activity

### LED doesn't pulse / color stuck

**Cause:** Update loop not running or LED calculation broken

**Solutions:**
1. Check that status text updates (should refresh every 100ms)
2. Move around—LED should change colors
3. Verify you're in active mode (not calibration):
   - Click "FINISH SETUP & GLAZE"
   - Calibration banner should disappear

4. If stuck on one color, restart PZD completely

---

## System Lock & Sleep Issues

### "SetThreadExecutionState" errors (Windows)

**Cause:** Permission issue or missing WinAPI call

**Solution:**
- This requires admin privileges to fully inhibit lock
- Keep PZD running in foreground or ensure it's in focus periodically
- If errors appear but system still stays awake, this is expected behavior

### "caffeinate" errors (macOS)

**Cause:** `caffeinate` command not available or permission denied

**Solutions:**
```bash
# Check if caffeinate is available:
which caffeinate

# Grant Terminal Full Disk Access:
# System Preferences > Security & Privacy > Privacy > Full Disk Access
# Add Terminal/iTerm2 to the list
```

### System still locks despite "PRESENCE CONFIRMED"

**Cause:** Sleep inhibition is working, but system has other lock policies

**Solutions:**
1. Check System Preferences for:
   - Screen timeout settings
   - Auto-lock after idle time
   - Lock on screen sleep
2. Disable conflicting lock policies
3. Verify PZD status shows "PRESENCE CONFIRMED" (not "ZONE EMPTY")

### High CPU usage

**Cause:** Usually multiple sensor threads or busy-wait loop

**Solutions:**
1. Ensure only ONE instance of PZD is running
   ```bash
   # Windows: Check Task Manager for multiple python.exe
   # macOS: Activity Monitor for multiple Python processes
   ```

2. Restart PZD

3. If problem persists, report as a bug with:
   - System (Windows/macOS/Linux)
   - Python version: `python --version`
   - CPU usage before/after restart
   - Steps to reproduce

---

## UI & Display Issues

### Window won't appear / minimize doesn't work

**Cause:** Tray icon spawning errors

**Solutions:**
1. Try running from command line to see errors:
   ```bash
   python app/main.py
   ```

2. If you see errors about pystray:
   ```bash
   pip install --upgrade pystray
   ```

3. On Linux with no X11:
   - PZD requires X11 or Wayland with proper XDG support
   - Try: `export DISPLAY=:0 && python app/main.py`

### Colors look wrong / UI is unreadable

**Cause:** Custom color scheme may not match your theme

**Solutions:**
1. Check if your OS is in dark/light mode
2. The cyan (#00ffcc) accent is designed for dark backgrounds
3. Light theme users might need to modify colors in `app/main.py`:
   ```python
   COLOR_ACCENT = "#00ffcc"  # Change to darker color
   COLOR_BG = "#030303"      # Change to lighter color
   ```

### Text is cut off or overlapping

**Cause:** Display scaling or font unavailability

**Solutions:**
1. Update tkinter:
   ```bash
   pip install --upgrade Pillow
   ```

2. On Linux, install fonts:
   ```bash
   sudo apt-get install fonts-liberation fonts-noto
   ```

3. Check DPI scaling (Windows):
   - PZD window > Properties > Compatibility > Change high DPI settings
   - Try "Disable full-screen optimizations"

---

## Miscellaneous

### How do I view console error messages?

**Windows:**
```bash
# Run from PowerShell/Command Prompt, not by double-clicking:
python app/main.py
```

**macOS/Linux:**
```bash
python app/main.py
# Errors appear in terminal
```

### How do I report a bug?

1. Gather information:
   ```bash
   python --version
   python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
   ```

2. Note when the issue occurs:
   - During calibration or active mode?
   - With specific camera or any camera?
   - After how long?

3. Open GitHub Issue with:
   - Title: Brief description
   - System (Windows 10/11, macOS version, Linux distro)
   - Python version
   - Steps to reproduce
   - Any console error messages

### PZD still allowing sleep despite being active

**Cause:** OS lock policies override PZD inhibition

**Solutions:**
1. Check PowerSettings (Windows):
   - Settings > System > Power & sleep
   - Adjust "Screen timeout" and "Sleep"
   - Set to "Never" for testing

2. Check Energy Saver (macOS):
   - System Preferences > Energy Saver
   - Uncheck auto-sleep for AC power

3. Even with these off, some enterprise policies may override PZD
   - Contact your IT department if locked down

---

## Still Stuck?

1. **Check [FEATURES.md](FEATURES.md)** for feature explanations
2. **Check [DEVELOPMENT.md](DEVELOPMENT.md)** for setup guidance
3. **Open a GitHub Issue** with:
   - System info and Python version
   - What you were trying to do
   - Error messages or unexpected behavior
   - Steps to reproduce

---

**Last Updated:** 2026  
**Version Tested:** Python 3.8+, OpenCV 4.8+
