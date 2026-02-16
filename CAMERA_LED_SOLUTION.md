# Camera LED Fix - Complete Solution

**PZDetector™** by Chair-to-Keyboard™

## The Problem
Windows keeps the webcam LED on briefly after closing PZDetector™ because:
- Windows DirectShow/MSMF drivers hold exclusive camera handles
- Python cannot force-release these handles at the driver level
- Only admin-level device reset can force the handle release

## The Solution

We've created a **three-tier system** to handle this:

### Tier 1: Automatic (Best)
**Run PZDetector™ with admin privileges**
- App automatically releases camera on close
- LED turns off within 1-2 seconds
- No manual intervention needed

### Tier 2: Manual (Fallback)
**If LED still stays on after 2-3 seconds**
- Double-click `camera_helper.bat` (right-click → Run as Administrator)
- LED turns off immediately

### Tier 3: Nuclear (Last Resort)
**If all else fails**
- Disable camera in Device Manager
- Or check Camera Privacy Settings in Windows
- Or restart the computer

## Quick Start

### Recommended: Admin Launcher

**Option A - Python Script (automatic elevation):**
```powershell
python run_as_admin.py
```

**Option B - Batch Launcher (manual open):**
1. Right-click on `run_pzdetector_admin.bat` (create if needed)
2. Select "Run as administrator"

**Option C - PowerShell (if already admin):**
```powershell
python -u app/main.py
```

### If LED Stays On

```powershell
# Right-click camera_helper.bat
# Select "Run as administrator"
# Or from PowerShell:
powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action release
```

## Tools Reference

| File | Purpose | Requires Admin |
|------|---------|-----------------|
| `run_as_admin.py` | Auto-elevating launcher | Yes (requests) |
| `camera_helper.bat` | Interactive helper GUI | Yes (manual) |
| `camera_helper.ps1` | PowerShell backend | Yes (manual) |
| `camera_helper.cs` | C# source (optional) | Yes (if compiled) |

## How Each Tier Works

### Tier 1: Automatic Release
```
User closes PZDetector
↓
quit_app() runs cleanup
↓
Calls camera_helper.bat
↓
PowerShell disables/re-enables camera device
↓
Windows driver releases handle
↓
LED turns off (1-2 seconds)
```

### Tier 2: Manual Camera Helper
```
User double-clicks camera_helper.bat
↓
Requests admin elevation (UAC prompt)
↓
Runs camera_helper.ps1 with -Action release
↓
Disables then re-enables Integrated Webcam device
↓
LED turns off immediately
```

### Tier 3: Windows Device manager
```
Settings → Devices → Camera
Disable, then re-enable camera
↓
Forces OS-level device reset
↓
LED turns off
```

## Admin Privilege Details

### Why Admin is Required
- `Disable-PnpDevice` - PowerShell Plug & Play device management (admin-only)
- `Enable-PnpDevice` - Re-enable device after disabling (admin-only)
- Windows Device Manager - Direct device control (admin-only)

### How to Check if Running as Admin
```powershell
# PowerShell
[bool]([Security.Principal.WindowsIdentity]::GetCurrent().Groups -match "S-1-5-32-544")
```
Returns: `True` = Admin, `False` = Regular user

### UAC Elevation
When `run_as_admin.py` is executed:
1. Checks if running as admin
2. If not, requests UAC elevation
3. Windows shows UAC prompt: "Do you want to allow this app to make changes?"
4. After approval, runs with admin privileges

## Testing

### Test 1: Check Camera Detection
```powershell
powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action status
```

Should show:
```
[Camera] Checking status...
[Camera] Integrated Webcam
  Status: OK
  Device ID: USB\VID_...
```

### Test 2: Manual Release
```powershell
powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action release
```

Should show:
```
[Camera] Releasing camera resources...
[Camera] Found: Integrated Webcam
[Camera] Disabling device...
[Camera] Re-enabling device...
[Camera] Reset complete!
```

### Test 3: Run Full App with Auto-Release
```powershell
python run_as_admin.py
```

1. App starts (with admin privileges)
2. Let it run for 5 seconds
3. Close the window
4. Check if LED turns off within 2 seconds

## Troubleshooting

### Issue: UAC Prompt Appears Every Close
**Solution:** This is normal! UAC safety feature. You can suppress by:
- Creating a scheduled task (see RUNNING_AS_ADMIN.md)
- Or accepting the prompt

### Issue: "Access Denied" Error
**Solutions:**
1. Ensure running `camera_helper.bat` with "Run as administrator"
2. Check your user account has admin privileges
3. Try PowerShell instead: `powershell -ExecutionPolicy Bypass -File camera_helper.ps1 -Action release`

### Issue: LED Still On After Helper Runs
**Likely causes:**
1. Helper wasn't run with admin (check for silent failure)
2. Another app is holding camera (close all camera apps)
3. Camera driver doesn't support device reset (rare)

**Solutions:**
- Try manual Device Manager reset
- Disable camera in Settings → Privacy & Security → Camera
- Restart computer

### Issue: "PowerShell not found"
**Solution:** PowerShell is built into Windows. If truly missing:
```cmd
# Download from Microsoft or use Command Prompt instead:
cd /d C:\Users\LukeLockhart\pzd-core
run_pzdetector_admin.bat
```

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│      User Double-clicks Shortcut        │
└────────────────┬────────────────────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  run_as_admin.py     │ (requests UAC)
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │   PZDetector App     │ (runs as admin)
      │   (main.py)          │
      └──────────┬───────────┘
                 │
         (app running)
                 │
              User Closes
                 │
                 ▼
      ┌──────────────────────┐
      │   quit_app()         │
      │   Cleanup routine    │
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  camera_helper.bat   │
      │  (called by Python)  │
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │ camera_helper.ps1    │
      │ Disable → Wait → Re- │
      │ enable camera device │
      └──────────┬───────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  Windows Driver      │
      │  Reset Device Handle │
      │  Release Camera      │
      └──────────┬───────────┘
                 │
                 ▼
            🎥 LED Off ✓
```

## Files Involved

```
pzd-core/
├── run_as_admin.py              # Auto-elevating launcher (NEW)
├── camera_helper.ps1             # PowerShell helper (TESTED)
├── camera_helper.bat             # Batch wrapper  (TESTED)
├── camera_helper.cs              # C# source (optional)
├── app/main.py                   # Updated with camera_helper call
├── RUNNING_AS_ADMIN.md           # Admin privileges guide
├── CAMERA_HELPER.md              # Tool documentation
├── CAMERA_HELPER_IMPLEMENTATION.md # Technical details
└── CAMERA_LED_ISSUE.md           # Background info
```

## Recommended Workflow

### For Daily Use
1. Run `run_as_admin.py` (keeps admin context)
2. Use app normally
3. Close window
4. Camera helper automatically releases LED

### For Non-Admin Users
1. Run app normally: `python app/main.py`
2. If LED stays on, manually run:
   ```powershell
   # Right-click camera_helper.bat → Run as Administrator
   ```

### For Troubleshooting
1. Check camera status:
   ```powershell
   camera_helper.bat status
   ```
2. Manual release:
   ```powershell
   camera_helper.bat release
   ```
3. Disable if problematic:
   ```powershell
   camera_helper.bat disable
   ```

## Summary

✅ **Complete solution** for Windows camera LED issue  
✅ **Three-tier approach** (automatic, manual, nuclear)  
✅ **Admin elevation** handled automatically  
✅ **Tested and documented** with troubleshooting guides  

The LED issue is now **fully addressable** through this system. Choose the comfort level that works best for you!
