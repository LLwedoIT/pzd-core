# Security & Privacy Policy for PZD

This document explains PZD's security model and privacy guarantees.

## Core Privacy Principles

### 1. Glazed Vision™ (Privacy-First Design)

PZD uses **Glazed Vision**—a privacy-by-design approach that fundamentally prevents biometric data collection:

**The Process:**
1. Raw frame: 640x480 pixels
2. Downsampled to: 20x15 pixels (extreme compression)
3. Upscaled for display: 320x240 pixels
4. Applied Gaussian blur: 99x99 kernel (heavy blur)

**Result:** Motion blobs are visible; faces, eyes, skin tones, and expressions are impossible to discern.

**What PZD detects:**
✅ Is someone in the zone? (Yes/No)  
✅ How close are they? (Proximity blob size)

**What PZD CANNOT detect:**
❌ Who the person is  
❌ Facial features or expressions  
❌ Skin tone, age, or gender  
❌ Emotions or activities beyond presence  
❌ Custom hand gestures or biometric signatures

### 2. No Frame Storage

**Guarantee:** Raw or processed frames are never written to disk.

❌ **Violations** (will not occur):
- `cv2.imwrite("debug_frame.jpg", frame)` 
- `json.dump(frame, file)`
- Frame data in log files

✅ **Allowed**:
- Metadata logging: `print(f"Proximity: {proximity}")`
- State logging: `print(f"Status: {status}")`
- Performance logging: `print(f"FPS: {frame_rate}")`

Code Review: All PRs are checked to ensure no frame data is persisted.

### 3. No Network Transmission

**Guarantee:** No video, frames, or processed data leave your machine.

- ❌ No uploading to cloud services
- ❌ No external vision APIs (AWS Rekognition, Google Cloud Vision, etc.)
- ❌ No telemetry with frame data
- ✅ Optional: Aggregate stats (daily lock count, buffer duration) with no timestamps or identifiers

## Security Model

### OS-Level Integration

PZD integrates with native OS power management—not a workaround:

**Windows:**
```python
ctypes.windll.kernel32.SetThreadExecutionState(0x80000001 | 0x00000002)
```
- Prevents display sleep
- Prevents automatic lock
- Requires Windows 10+ with appropriate user privileges

**macOS:**
```bash
caffeinate -i
```
- Spawns subprocess to inhibit sleep
- Respects macOS power preferences
- May require Terminal permissions

**Linux:**
- Uses systemd login inhibitors (when available)
- Limited support; documented limitations

### Threats PZD Mitigates

| Threat | Mitigation | Status |
|--------|-----------|--------|
| Employee unattended machine lockout ("Auto-Lock Panic") | Presence confidence decay with Kitten Buffer | ✅ Implemented |
| False triggers from pets or background motion | Configurable PZ Reach and Proximity Floor | ✅ Implemented |
| Background eavesdropping via video | Glazed Vision blur prevents facial recognition | ✅ Implemented |
| Frame data exfiltration | No frames ever saved or transmitted | ✅ Implemented |
| Unauthorized remote access | Zero-Signal Architecture (no remote protocols) | ✅ Implemented |

### Threats PZD DOES NOT Address

| Threat | Why | Alternative |
|--------|-----|-------------|
| Keylogger malware | PZD presence detection ≠ malware protection | Use antivirus software |
| Network intrusion | Different threat model | Use firewall & network segmentation |
| Physical tampering | Someone can unplug keyboard/camera | Use physical locks or CCTV |
| Screen content exposure | Presence alone doesn't prevent screen viewing | Use privacy screen filters |

## Guardian Mode Security (Planned)

Future Guardian Mode features will include:

### Act I: Workstation Lock
- Immediate lock when presence confidence = 0
- Uses native OS lock commands
- Protects screen content

### Act II: Process Protection  
- Maintain critical renders/downloads while user away
- Monitored via task list, not arbitrary code execution
- Limited to user-approved processes

### Act III: Network Severance (Optional)
- Disable NIC to prevent data exfiltration
- Requires admin privileges
- User-configurable
- Can be disabled for network-dependent workloads

### Audit Logging
- Timestamps of lock events
- Stored locally in encrypted SQLite
- Never contains frame data or activities
- User can opt-out

## Installation & Dependencies

### Python Package Safety

PZD dependencies are carefully vetted:

| Dependency | License | Security | Notes |
|-----------|---------|----------|-------|
| opencv-python | Apache 2.0 | ✅ Well-maintained | Vision/motion detection |
| numpy | BSD | ✅ Stable | Numerical computing |
| Pillow | HPND/MIT | ✅ Actively maintained | Image processing |
| pystray | MIT | ✅ Lightweight | System tray icon |

**Checking for vulnerabilities:**
```bash
pip install safety
safety check
```

### No Telemetry by Default

- PZD does not phone home
- No analytics tracking
- No usage reporting (unless explicitly enabled by user)
- No crash reports without consent

## Code Audit & Transparency

### How to Audit PZD

1. **Read the source:**
   ```bash
   # All logic is in app/main.py (~350 lines)
   wc -l app/main.py
   cat app/main.py
   ```

2. **Check dependencies:**
   ```bash
   cat app/requirements.txt
   ```

3. **Search for dangerous patterns:**
   ```bash
   grep -n "imwrite\|http\|POST\|pickle\|exec\|eval" app/main.py
   # Should return nothing
   ```

4. **Verify the Glazed Vision blur:**
   ```bash
   grep -n "GaussianBlur.*99.*99" app/main.py
   # Confirms 99x99 kernel is used
   ```

### Contributors Must Sign DCO

All contributors must sign the Developer Certificate of Origin:
```bash
git commit -s -m "feat: add new feature"
```

This certifies you wrote the code and have the authority to contribute it.

## Handling Vulnerabilities

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. **Email** [MAINTAINER_EMAIL] with:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (optional)

3. **Responsible disclosure:** Give maintainers 90 days to fix before public disclosure

## Privacy Compliance

### GDPR (EU)
- ✅ No personal data processing
- ✅ No data retention beyond session
- ✅ Local-first design
- ✅ User can audit data handling

### CCPA (California)
- ✅ No data collection for sale
- ✅ User has full access to their machine data
- ✅ No third-party data sharing

### HIPAA (Healthcare)
- ⚠️ Partial compliance
- ✅ No protected health information captured
- ❌ Not a complete HIPAA solution by itself
- Consult compliance officer before deploying in healthcare settings

### FERPA (Education)
- ✅ No student biometric data collected
- ✅ No student activity correlation possible
- ⚠️ Verify with IT/security team for institutional use

## Best Practices for Users

### Minimal Permissions

Run PZD with the least privileges necessary:

❌ **Bad:**
```bash
sudo python app/main.py  # Unnecessary root access
```

✅ **Good:**
```bash
python app/main.py  # User privileges only
# Elevated prompt appears only when needed for OS calls
```

### Camera Privacy

1. **Physical privacy:** Use a camera privacy cover when not in use
2. **Camera permissions:** Grant PZD only when you intend to use it
3. **Multiple cameras:** Disable cameras you don't use

### Regular Updates

Keep PZD updated:
```bash
git pull origin master
pip install -r app/requirements.txt --upgrade
```

### Monitor Resource Usage

Check that PZD uses reasonable resources:
- CPU: <5% idle, <10% active
- Memory: <50 MB
- Camera: Active only when running

If unusual, kill the process and investigate.

## Third-Party Integrations (Future)

When third-party integrations are added:
- Must be local-first (no cloud APIs)
- Must be user-approved before activation
- Must document all data shared
- Must respect Glazed Vision principle

## Accessibility vs. Security Trade-off

PZD must balance accessibility (easy to use) with security (hard to exploit):

| Feature | Accessibility | Security | Trade-off |
|---------|---------------|----------|-----------|
| Glazed Vision blur strength | Fixed at 99x99 | Maximum privacy | Users can't disable blur |
| Calibration mode | Easy visual setup | Reveals zone boundaries | Temporary; activates only at startup |
| Multi-camera support | Flexibility | Potential confusion | Clear labeling required |
| Guardian lock | Immediate | No grace period | Can be disabled for testing |

## Questions?

- **Privacy concern?** Email [CONTACT] or open GitHub Discussion
- **Found vulnerability?** See "Handling Vulnerabilities" above
- **Compliance question?** Consult your IT/security team in addition to PZD documentation

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-02-15 | Initial Glazed Vision implementation, local-first design |

---

**Principle:** *PZD respects user privacy first. Code is transparent. Data stays local. Presence, not surveillance.*
