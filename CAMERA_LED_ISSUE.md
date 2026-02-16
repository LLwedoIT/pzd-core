# Camera LED Issue - Known Windows DirectShow Limitation

**PZDetector™** by Chair-to-Keyboard™

## Problem
On Windows systems, the webcam LED remains on briefly after closing the PZDetector™ application.

## Root Cause
This is a known limitation of Windows DirectShow/MSMF (Media Foundation) camera drivers:
- Once a Python application opens a camera via these drivers, the OS maintains an exclusive lock on the device
- Python's OpenCV wrapper cannot completely release this handle to the driver
- The handle only fully releases when the entire Python process is terminated at the OS level

## What We Tried
✓ Explicit `cap.release()` with nested exception handling  
✓ Setting camera properties to 0 before release  
✓ `gc.collect()` garbage collection forcing  
✓ Increased sleep delays (up to 1 second)  
✓ Forced `root.destroy()` before `sys.exit(0)`  
✗ Non-daemon threads with timeout joins (caused terminal hangs)  
✗ `cv2.destroyAllWindows()` (not applicable - no GUI windows)  
✗ `subprocess.Popen().kill()` (caused Tkinter crashes)  

## Temporary Workarounds

### 1. Disable Camera in Settings (Within App)
Once the app starts, if you don't need real-time detection, switch to manual pose selection rather than camera calibration.

### 2. Close Completely and Wait
The LED typically dims within 1-2 seconds even if technically "on" - Windows eventually releases the resource.

### 3. Disable Camera in Device Manager
- Windows Settings → Devices → Camera
- Toggle camera off to force driver release

### 4. Use Task Manager to Kill Process
If the LED stays on persistently:
```powershell
Get-Process python | Stop-Process -Force
```

## Why This Happens
Windows maintains camera resources at a lower level than Python can access. Unlike iOS/macOS which provide APIs to explicitly release camera access, Windows' DirectShow keeps the resource locked until:
1. The application thread that opened it exits
2. The entire process terminates
3. The system forcibly reclaims the resource (can take several seconds)

## Future Solutions
_These would require non-Python approaches:_
- Use a separate C++/C# helper executable that controls the camera
- Implement platform-specific Windows API calls via ctypes
- Use a media server (like ffmpeg subprocess) as intermediary

For now, this is documented as a cosmetic issue rather than a functional one.
