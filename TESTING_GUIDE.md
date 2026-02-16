# PZDetector™ Live Testing Guide

**By Chair-to-Keyboard™** | *The Human Centric Software Development Company*

**Last Updated:** February 16, 2026  
**Version:** 2.0 (Multi-sensor waterfall + Phase 2/3 complete)

---

## Pre-Test Checklist

### Required Dependencies
```powershell
pip install opencv-python pillow psutil pystray keyboard
```

### Optional Dependencies (Phase 3b - Windows Hello)
```powershell
pip install winrt-Windows.Security.Credentials.UI
```

If you encounter install errors for winrt, Windows Hello will gracefully fall back to unavailable.

---

## Test 1: Basic Launch & Config Load

**Goal:** Verify app starts without errors and config loads correctly.

### Steps
1. Open PowerShell in `c:\Users\LukeLockhart\pzd-core`
2. Run: `python app/main.py`
3. Verify window appears with:
   - PZDetector™ header + LED indicator
   - Calibration banner (cyan, "CALIBRATION MODE: MAP YOUR ZONE")
   - Camera feed placeholder
   - Status: "WAITING..." or "CALIBRATING..."
   - Progress bar (empty initially)

### Expected Console Output
```
[Config] Loaded from config.json
[LogService] initialized
[App] PZD Application Started
[HIDMonitor] HID monitor initialized
[Sensor] Camera sensor started (index=0)
[PresenceEngine] PresenceEngine initialized
[AppAwareness] Service started
[App] Application initialization complete
```

### ✅ Pass Criteria
- Window launches
- No Python exceptions
- Console shows all services initialized
- Camera feed shows (may be blank if no motion yet)

---

## Test 2: HID Detection (Sensor Stage 1)

**Goal:** Verify keyboard/mouse input resets presence timer.

### Steps
1. Launch app (calibration mode is fine)
2. Click "FINISH SETUP & GLAZE" to exit calibration
3. Status should show: **"ACTIVE - 60s"** (or your `lockTimeoutSeconds` value)
4. Wait 5 seconds without touching keyboard/mouse
5. Status should show: **"ACTIVE - 55s"** (countdown)
6. **Press any key** or **move mouse**
7. Status should immediately reset to: **"ACTIVE - 60s"**

### ✅ Pass Criteria
- Countdown decreases when idle
- Countdown resets to max on keyboard/mouse activity
- No false countdown during active typing

---

## Test 3: Grace Period Banner (Phase 2d)

**Goal:** Verify inline grace banner appears during WARNING state.

### Steps
1. Set `lockTimeoutSeconds: 15` and `warningThresholdSeconds: 5` in [app/config.json](../app/config.json)
2. Restart app
3. Exit calibration mode
4. Go idle (no keyboard/mouse) for 10 seconds
5. Status should show: **"ACTIVE - 5s"** → **"⚠ WARNING - 5s until lock"**
6. **Grace banner should appear** below progress bar:
   - Background: dark yellow/brown (`#332200`)
   - Text: "WARNING: Locking in 5s" (countdown updates each second)

### ✅ Pass Criteria
- Banner appears when countdown <= 5s
- Banner disappears when countdown > 5s (type to reset)
- Text updates with remaining seconds

---

## Test 4: Tray Icon State Colors (Phase 2c)

**Goal:** Verify tray icon reflects PresenceEngine state.

### Steps
1. Use same config from Test 3 (15s timeout, 5s warning)
2. Exit calibration mode
3. Minimize window to tray (click X or minimize)
4. **ACTIVE (60s → 6s):** Tray icon should be **cyan** (#00ffcc)
5. **WARNING (5s → 1s):** Tray icon should turn **yellow** (#ffff00)
6. **LOCKING (0s):** Tray icon should turn **red** (#ff0000)
7. Open a meeting app (Zoom/Teams/Discord) → icon should turn **gray** (#999999, PAUSED)

### ✅ Pass Criteria
- Icon color matches state
- Color transitions are immediate (not laggy)
- PAUSED state triggered by meeting apps

---

## Test 5: App Awareness Auto-Pause (Phase 2 + existing)

**Goal:** Verify meeting app detection pauses presence.

### Steps
1. Launch app, exit calibration
2. Open Zoom/Teams/Discord/Slack (any supported app from [app/app_awareness.py](../app/app_awareness.py))
3. Status should show: **"⏸ PAUSED (meeting detected)"**
4. Tray icon should be **gray**
5. Close meeting app
6. Status should resume: **"ACTIVE - 60s"**

### Expected Console/Log Output
```
[AppAwareness] Meeting app detected - pausing presence detection
[PresenceEngine] Paused (meeting detected)
```

### ✅ Pass Criteria
- App correctly detects meeting apps
- Presence detection pauses (no countdown)
- Resumes when meeting app closed
- No false locks during meetings

---

## Test 6: Guardian Mode Act I (Lock on Idle)

**Goal:** Verify workstation locks when Guardian Mode enabled and idle.

### Steps
1. Set `enableGuardianMode: true` in [app/config.json](../app/config.json)
2. Set `lockTimeoutSeconds: 10` for quick testing
3. Restart app, exit calibration
4. **Enable Guardian Mode** checkbox in UI
5. Go idle for 10+ seconds
6. **Workstation should lock** (Windows lock screen appears)

### Expected Console Output
```
[Guardian] Guardian Mode ENABLED
[Guardian Log] ACT_I_LOCK: Workstation locked. Presence confidence: 0
[Guardian] LOCKED WORKSTATION at HH:MM:SS
```

### ✅ Pass Criteria
- Lock happens at exactly timeout seconds
- Audit log records event
- Status shows: **"🔒 LOCKED (Guardian Mode)"**

---

## Test 7: Guardian Mode Act III + Network Control (Phase 3a)

**Goal:** Verify network adapters disable on Act III (requires admin).

### Steps
1. **Run PowerShell as Administrator**
2. Set `enableNetworkWiFiControl: true` in [app/config.json](../app/config.json)
3. Set `enableGuardianMode: true`
4. Launch app: `python app/main.py`
5. Enable Guardian Mode in UI
6. Select a process from "Guarded Process" dropdown (e.g., notepad.exe)
7. Let process run and complete (or close it manually)
8. **Act III should trigger:** Network adapters disabled

### Expected Console Output
```
[Guardian Log] ACT_II_COMPLETE: Process notepad.exe (PID 1234) completed
[NetworkService] Disabled adapter: Ethernet
[NetworkService] Disabled adapter: Wi-Fi
[Guardian Log] ACT_III_NETWORK_DISABLED: Network adapters disabled
[Guardian Log] ACT_III_COMPLETE: Sleep inhibition released
```

### Verify Network State
```powershell
netsh interface show interface
```
Adapters should show **"Disabled"** in Admin State.

### ✅ Pass Criteria
- Adapters disable when guarded process completes
- Adapters re-enable when app exits
- No errors if not admin (graceful fallback)

---

## Test 8: Windows Hello Biometric (Phase 3b)

**Goal:** Verify Windows Hello prompt during WARNING state resets timer.

### Steps
1. Install winrt: `pip install winrt-Windows.Security.Credentials.UI`
2. Set `enableBiometricVerification: true` in [app/config.json](../app/config.json)
3. Set `lockTimeoutSeconds: 15`, `warningThresholdSeconds: 5`
4. Restart app, exit calibration
5. Go idle for 10 seconds (enter WARNING state)
6. **Windows Hello prompt should appear:** "Confirm you're still here"
7. **Authenticate** (PIN/fingerprint/face)
8. Timer should reset to 15s (ACTIVE state)

### Expected Console Output
```
[IdentityService] Available
[PresenceEngine] Windows Hello verification requested
[PresenceEngine] State: WARNING → ACTIVE
```

### UI Behavior
- Status shows: **"Windows Hello verification required"** during prompt
- Grace banner shows: **"Verify with Windows Hello to stay unlocked"**
- Status resets to: **"ACTIVE - 15s"** after successful auth

### ✅ Pass Criteria
- Hello prompt appears during WARNING
- Successful auth resets timer
- Failed auth continues countdown to lock
- If Hello unavailable, falls back to normal countdown

---

## Test 9: Trial/License System (Phase 3c)

**Goal:** Verify trial check and expiration flow.

### Steps
1. Delete `C:\Users\[YourUser]\AppData\Roaming\PZDetector\license.json` (if exists)
2. Set `enableLicenseCheck: true` and `trialDays: 0` in [app/config.json](../app/config.json)
3. Set `purchaseUrl: "https://pzdetector.com/buy"` (or any URL)
4. Launch app
5. **Trial expired dialog should appear:** "Your trial has expired. Open the purchase page now?"
6. Click **Yes** → browser opens purchase URL
7. App should exit

### Expected Console Output
```
[LicenseService] Trial expired; exiting
```

### ✅ Pass Criteria
- Trial check happens on startup
- Expired trial shows dialog
- Purchase URL opens in browser
- App exits gracefully

---

## Test 10: Power Optimization Validation

**Goal:** Measure CPU usage in different states.

### Tools
- Windows Task Manager
- Process Explorer (optional)

### Steps
1. Launch app, exit calibration
2. **ACTIVE (idle, no motion):** CPU should be **1-2%**
   - HID polling only (negligible)
   - Camera at 1 FPS
3. **WARNING (near lock):** CPU should be **2-5%**
   - HID + Camera motion analysis
4. **Minimized:** CPU should be **<0.5%**
   - Sensor paused
5. **Meeting app open (PAUSED):** CPU should be **<0.5%**
   - All sensors disabled

### ✅ Pass Criteria
- Idle CPU < 2% (85% reduction vs old baseline)
- WARNING CPU < 5%
- Minimized/paused CPU < 0.5%

---

## Test 11: Full Integration Smoke Test

**Goal:** Verify all features work together without conflicts.

### Steps
1. Fresh config: all features enabled except network/Hello
2. Launch app
3. Exit calibration mode
4. Open Zoom → verify pause
5. Close Zoom → verify resume
6. Enable Guardian Mode
7. Select a process (e.g., Calculator)
8. Go idle for 5s → grace banner appears
9. Type → banner disappears, timer resets
10. Close process → Act III triggers
11. Minimize window → verify tray icon color
12. Restore window
13. Quit app cleanly

### ✅ Pass Criteria
- No Python exceptions during any step
- All state transitions work
- Tray icon reflects state
- Audit log records all events
- System logs populate in `logs/pzd_YYYYMMDD.log`

---

## Common Issues & Solutions

### Issue: Camera feed shows "SENSOR BLOCKED OR IN USE"
**Solution:** Another app is using the webcam. Close Zoom/Teams/OBS and restart app.

### Issue: Windows Hello doesn't prompt
**Solution:** 
1. Check `winrt` is installed: `pip list | grep winrt`
2. Verify Windows Hello is set up in Windows Settings
3. Check console for: `[IdentityService] Available`

### Issue: Network adapters don't disable
**Solution:** 
1. Run PowerShell as Administrator
2. Check console for: `[NetworkService] Admin privileges required`
3. If using Store Python, network control may not work (requires elevated environment)

### Issue: Tray icon doesn't change color
**Solution:** 
1. Verify PresenceEngine is active (not in calibration mode)
2. Check console for state transitions: `[PresenceEngine] State: ACTIVE → WARNING`
3. Tray icon updates every 100ms (update_loop cycle)

### Issue: App exits immediately on launch
**Solution:**
1. Check trial status: `trialDays: 0` will trigger immediate exit
2. Set `enableLicenseCheck: false` to disable trial
3. Delete `%APPDATA%\PZDetector\license.json` to reset trial

---

## Performance Targets

| State | CPU Usage | Battery Impact |
|-------|-----------|----------------|
| ACTIVE (idle) | 1-2% | Negligible |
| WARNING | 2-5% | Low |
| LOCKING | <1% | None |
| PAUSED | <0.5% | None |
| Minimized | <0.5% | None |

**Expected Battery Life:** 8-12 hours (vs 2-3 hours in old version)

---

## Next Steps After Testing

1. **If all tests pass:** Commit and push to master
2. **If any test fails:** 
   - Check console/logs for errors
   - Review [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
   - File issue with logs attached
3. **Production deployment:**
   - Set `trialDays: 7` (or desired trial length)
   - Set `purchaseUrl` to actual sales page
   - Build executable: `pyinstaller --onefile --windowed app/main.py`

---

## Test Report Template

```
## PZDetector™ v2.0 Test Report

**Date:** YYYY-MM-DD
**Tester:** [Your Name]
**System:** Windows 11 Pro / Windows 10 Home
**Python:** 3.x.x

### Test Results
- [ ] Test 1: Basic Launch & Config Load
- [ ] Test 2: HID Detection
- [ ] Test 3: Grace Period Banner
- [ ] Test 4: Tray Icon State Colors
- [ ] Test 5: App Awareness Auto-Pause
- [ ] Test 6: Guardian Mode Act I
- [ ] Test 7: Act III + Network Control
- [ ] Test 8: Windows Hello Biometric
- [ ] Test 9: Trial/License System
- [ ] Test 10: Power Optimization
- [ ] Test 11: Full Integration Smoke Test

### Issues Found
[List any issues, with steps to reproduce]

### Performance Metrics
- ACTIVE CPU: X%
- WARNING CPU: X%
- Battery drain over 30min: X%

### Notes
[Any additional observations]
```
