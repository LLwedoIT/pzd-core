# Camera Helper Tools

**PZDetector™** by Chair-to-Keyboard™

Two tools to help release camera resources when the LED stays on after the app closes.

## Quick Start

### Option 1: Automatic (Built-in)
When you close PZDetector™, the app automatically calls the camera helper to release the camera. **No action needed from you.**

### Option 2: Manual Release
If the LED still lingers, you can manually release the camera:

**Easiest Method:**
```powershell
# From PowerShell (run as Administrator)
powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action release
```

Or double-click `camera_helper.bat` (right-click → Run as administrator)

## Tools Included

### 1. `camera_helper.ps1` (PowerShell Script)
Uses PowerShell's device management to disable/enable the camera at the driver level.

**Actions:**
- `release` - Disable then re-enable camera (forces driver to release handle)
- `disable` - Disable camera completely
- `enable` - Re-enable camera after disabling
- `status` - Check if camera is detected and its status

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action [release|disable|enable|status]
```

### 2. `camera_helper.bat` (Batch Script Wrapper)
User-friendly batch wrapper around the PowerShell script. 

**Double-click to release camera (easiest for non-technical users)**

Or from Command Prompt:
```cmd
camera_helper.bat release
camera_helper.bat disable
camera_helper.bat enable
camera_helper.bat status
```

### 3. `camera_helper.cs` (C# Source)
Advanced C# implementation using Windows WMI and PnP APIs. Requires compilation.

** For developers who want to compile to exe:**
```cmd
csc.exe /target:exe /out:camera_helper.exe camera_helper.cs
```

Then use:
```cmd
camera_helper.exe release|disable|enable|status
```

## Why This Works

Windows DirectShow/MSMF camera drivers hold exclusive locks on the device. The camera helper:

1. **Disables** the camera device via Windows Plug & Play
2. **Re-enables** the device 
3. This forces the Windows driver to fully release the handle

The LED turns off when:
- The device is re-enabled **OR**
- The OS automatically recovers the resource (within 2-3 seconds)

## When to Use

| Situation | Solution |
|-----------|----------|
| LED stays on after closing PZDetector | App automatically runs helper; wait 1-2 seconds |
| LED still on after 2-3 seconds | Run `camera_helper.bat` or `camera_helper.ps1` |
| Need to keep camera off permanently | Run `camera_helper.bat disable` |
| Want to re-enable camera later | Run `camera_helper.bat enable` |
| Troubleshooting camera issues | Run `camera_helper.bat status` |

## Requirements

### PowerShell Script
- Windows 7+
- PowerShell 3.0+ (usually pre-installed)
- **Administrator privileges** (required to manage devices)

### Batch Script  
- Windows 7+
- PowerShell 3.0+
- **Administrator privileges** (required)

### C# Version
- .NET Framework 3.5+
- C# compiler (`csc.exe`)
- **Administrator privileges** (required)

## Troubleshooting

### "Access Denied" Error
- **Solution:** Right-click → "Run as Administrator"

### PowerShell ExecutionPolicy Error
- **Solution:** The script includes `-ExecutionPolicy Bypass` to handle this automatically

### No Camera Detected
- Your camera may not be recognized by Windows as a "Camera" device
- Try Device Manager: Devices and Printers → (look for your webcam)

### LED Stays On After Running Helper
This might indicate:
1. Your camera driver doesn't properly support device reset
2. Another application is holding the camera (check Camera Privacy Settings)
3. Camera is disabled in Windows Settings

### PowerShell ISE Won't Run the Script
Try regular PowerShell instead:
```powershell
powershell.exe -ExecutionPolicy Bypass -File camera_helper.ps1
```

## Integration with PZDetector

The Python app calls `camera_helper.ps1 -Action release` automatically during shutdown. This happens silently in the background.

You can disable this by commenting out the camera helper section in `app/main.py` quit_app() method if needed:

```python
# Try to use helper script (optional - disable this if not needed)
# try:
#     helper_path = ...
```

## Advanced: Custom Camera Device

If you have multiple cameras and want to target a specific one, edit `camera_helper.ps1`:

```powershell
# Change this line to match your exact camera name:
$cameras = Get-PnpDevice -Class Camera | Where-Object {$_.Name -match "*Your Camera Model*"}
```

## Support

For issues:
1. Run `camera_helper.bat status` to see detected devices
2. Check Windows Device Manager for camera status
3. Try right-clicking camera in Device Manager → Update Driver
4. As last resort: disable camera in Windows Settings → Privacy & Security → Camera
