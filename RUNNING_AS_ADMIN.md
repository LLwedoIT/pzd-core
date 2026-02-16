# Running PZDetector™ with Admin Privileges

**PZDetector™** by Chair-to-Keyboard™

## Why Admin is Needed

The camera helper (`camera_helper.bat`) requires administrator privileges to:
- Disable and re-enable camera devices
- Access Windows Device Manager APIs
- Force driver-level resource release

Without admin privileges, the LED will stay on longer.

## Option 1: Command Line (Easiest)

Run from Power Shell as Administrator:

```powershell
# Open PowerShell as Administrator
# Navigate to the project directory
cd C:\Users\LukeLockhart\pzd-core

# Run the app
python -u app/main.py
```

When you close the app, the camera helper will automatically run with the same admin context.

## Option 2: Create Admin Shortcut (Best for Regular Use)

### Step 1: Create a Batch Launcher
Create a file called `run_pzdetector.bat` in the project root:

```batch
@echo off
REM PZDetector Launcher - Runs with Admin Privileges
cd /d "%~dp0"
python -u app/main.py
pause
```

### Step 2: Create a Shortcut with Admin Rights

1. Right-click on `run_pzdetector.bat`
2. Select "Send to" → "Desktop (create shortcut)"
3. Right-click the shortcut on Desktop
4. Select "Properties"
5. Click "Advanced..."
6. Check "Run as administrator"
7. Click "OK" twice

### Step 3: Run from Your Desktop

Now you can double-click the shortcut and it will:
- Run PZDetector with admin privileges
- Automatically release camera on close
- LED turns off properly

## Option 3: Via Task Scheduler

For automated/scheduled use:

1. Open **Task Scheduler**
2. Create New Task
3. General tab:
   - Name: "PZDetector"
   - Check "Run with highest privileges"
4. Triggers tab:
   - Set schedule (or leave for manual trigger)
5. Actions tab:
   - Action: "Start a program"
   - Program: `python`
   - Arguments: `-u app/main.py`
   - Start in: `C:\Users\LukeLockhart\pzd-core\app`

## Option 4: Always Run as Admin (Registry)

For .py files to always run as admin:

1. Right-click `.py` file → "Run with administrator privileges"
2. Check "Always use this app to open .py files"
3. Future `.py` files will respect this

## Verify Admin Status

The app will display admin status in the console:

```
[PZDetector] Running with admin privileges
[Camera Helper] Can manage devices
```

Or check manually:

```powershell
# In PowerShell
[bool]([Security.Principal.WindowsIdentity]::GetCurrent().Groups -match "S-1-5-32-544")
```

Value of `True` = Running as Admin

## If LED Still Stays On

Even with admin, if the LED stays on:

1. **Immediately after closing:**
   - Normal Windows behavior (2-3 second delay)
   - LED will turn off automatically

2. **After 2-3 seconds:**
   - Run `camera_helper.bat` manually
   - Right-click → "Run as administrator"

3. **Persistent:**
   - Check Device Manager for camera
   - Try disabling/enabling camera manually
   - Restart computer if needed

## Troubleshooting

### "Access Denied" When Running Shortcut
- Right-click shortcut → Properties → Advanced → Check "Run as administrator"

### Batch File Opens But Closes Immediately  
- Add `pause` at the end of `run_pzdetector.bat` to see any error messages

### App Closes Without Releasing Camera
- Ensure you're running the shortcut (with admin), not the .py file directly
- Check Windows Defender/antivirus isn't blocking access

### My App Already Runs as Admin
No action needed! The camera helper will work automatically.

## Summary

| Method | Ease | Reliability |
|--------|------|-------------|
| PowerShell as Admin | Medium | ⭐⭐⭐⭐⭐ |
| Desktop Shortcut | Easy | ⭐⭐⭐⭐⭐ |
| Task Scheduler | Medium | ⭐⭐⭐⭐ |
| Registry Change | Hard | ⭐⭐⭐ |

**Recommended:** Create desktop shortcut with admin privileges for easiest daily use.
