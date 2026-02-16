# PZD Roadmap

This document outlines the planned features and direction of the Presence Zone Detector project.

## Current Status (v0.1-alpha)

**Core features shipped:**
- ✅ Presence Zone detection (area-based)
- ✅ Glazed Vision (privacy-first motion detection)
- ✅ Kitten Buffer (confidence decay)
- ✅ Multi-camera support
- ✅ Calibration mode with visual feedback
- ✅ Tray icon with state indicators
- ✅ Windows + macOS support

**Known limitations:**
- No global hotkey support (manual QuitFunc only)
- No persistent audit logging
- Guardian mode (Acts I-III) not yet implemented
- Web-based lite version not started
- Linux support is experimental

---

## Short-term (Next 1-2 months)

### 🔴 Priority: Guardian Mode (Security Features)

**"Act I: Lock the Door"** [High Priority]
- Immediate workstation lock when presence confidence reaches 0
- Windows: Call `ctypes.windll.user32.LockWorkStation()`
- macOS: Call `osascript -e 'tell application "System Events" to sleep'`
- UI toggle: "Enable Guardian Mode" checkbox
- **Status:** Not started
- **Owner:** To be assigned

**"Act II: Sustain Guarded Process"** [High Priority]
- Monitor a user-selected "critical" process (render job, download, build, etc.)
- Keep SetThreadExecutionState/caffeinate active while process exists
- Allow sleep only when process completes or CPU < 1%
- UI: Dropdown to select process from task list
- **Status:** Not started
- **Owner:** To be assigned

**"Act III: Turn Out the Lights"** [Medium Priority]
- When guarded process ends, perform cleanup:
  1. (Optional) Sever network: Disable primary NIC
  2. Release sleep inhibition
  3. Allow hardware sleep (S3/S4 states)
- Requires admin/elevation for network control
- Log event timestamp for audit trail
- **Status:** Not started
- **Owner:** To be assigned

### 🟡 Priority: Global Hotkey Support

**"Panic-Kill" Global Hotkey** [Medium Priority]
- Emergency keystroke to manually lock system immediately
- Default: Ctrl+Alt+Shift+X (configurable)
- Useful when presence detection fails
- Requires `pynput` or `keyboard` library
- **Status:** Not started
- **Owner:** To be assigned

### 🟢 Priority: Code Quality & Documentation

- [ ] Add comprehensive docstrings to all classes/methods
- [ ] Add unit tests for:
  - Presence confidence decay math
  - Motion detection thresholds
  - UI state transitions
- [ ] Add integration tests for:
  - Camera initialization with different backends
  - Multi-camera switching
  - Full lifecycle (calibrate → active → locked)
- [ ] Create TESTING.md with test procedures
- [ ] Create API reference documentation for third-party integration
- **Status:** In progress (docs mostly done)
- **Owner:** Documentation lead

---

## Medium-term (2-4 months)

### 📦 Packaging & Distribution

- [ ] **PyPI Package**: Publish as `pzd-core` on PyPI for easy `pip install`
- [ ] **Executable Distribution**:
  - Windows .exe via PyInstaller/Nuitka
  - macOS .dmg with codesigning
  - Linux .deb/.rpm packages
- [ ] **Auto-update Mechanism**: Check for new versions and notify user
- [ ] **CI/CD Pipeline**:
  - GitHub Actions for matrix builds (Windows + macOS)
  - Automated testing on each release
  - Store compiled binaries as GitHub Releases

### 🌐 Web Lite Version

- [ ] **Browser-based Alternative**:
  - Single-page app (React or Vanilla JS)
  - Uses Screen Wake Lock API instead of native OS calls
  - No installation required
  - Deploy to pzdetector.com via Netlify
- [ ] **Feature Parity**:
  - Glazed Vision detection (using WebGL canvas)
  - Confidence decay
  - State indicators
- [ ] **Limitations Documentation**:
  - Browser-only, not system-wide
  - Doesn't prevent monitor sleep, only keeps browser active
  - Works with USB-connected UVC cameras only

### 📊 Audit Logging & Analytics

- [ ] **Local Event Log**:
  - Timestamp when presence confidence reaches 0 (lock event)
  - Timestamp when presence returns (unlock event)
  - Store in local SQLite database
- [ ] **Privacy-Safe Telemetry** (optional, user-controlled):
  - Aggregate stats (avg Kitten Buffer duration, daily lock count)
  - Never send identifying information or timestamps
- [ ] **"Welcome Back" Toast**:
  - Show time away, time until next lock
  - Display trending patterns (you're usually gone 15 mins, etc.)

---

## Long-term (4+ months)

### 🔐 Enterprise Features

- [ ] **Group Policy / MDM Integration**:
  - Deploy centrally managed PZD settings via Active Directory (Windows)
  - Support Mobile Device Management (MDM) for macOS
- [ ] **Compliance Reporting**:
  - Generate reports for audits
  - Prove presence policy compliance
- [ ] **Integration with Okta / Azure AD**:
  - Sync user lock policies with corporate identity

### 🤖 AI/ML Enhancements (Vision 2.0)

- [ ] **Pose Detection** (privacy-aware):
  - Detect if user is sitting/standing/lying down
  - Adjust sensitivity based on posture
  - Still respects Glazed Vision (skeleton only, no faces)
- [ ] **Activity Recognition**:
  - Distinguish typing from idle (keyboard detection)
  - Detect gestures (hand raise, arm movement)
  - Warn before locking if user appears engaged
- [ ] **Multi-Person Support**:
  - Detect multiple people in zone
  - Require majority occupancy for lock (for shared spaces)

### 🛡️ Advanced Security

- [ ] **Encrypted Audit Logs**:
  - Sign logs with private key
  - Tamper detection for compliance
- [ ] **Hardware Integration**:
  - Support for motion sensors (IR, PIR)
  - Support for custom HPD sensors via USB/serial
- [ ] **Biometric Spoofing Prevention**:
  - (Advanced) Double-check with additional sensors
  - Prevent deepfake/video replay attacks

---

## Not Planned / Out of Scope

❌ **Facial Recognition**: Would violate Glazed Vision principle  
❌ **Cloud Synchronization**: Stays local-first for privacy  
❌ **Wireless Communication**: Intentionally excludes Bluetooth, WiFi signals  
❌ **Mobile App**: Desktop-focused; web lite version is the mobile alternative  
❌ **Slack/Teams Integration**: Keep internal state private from external services  

---

## How to Contribute

We focus on items in the **Short-term** roadmap.

1. Comment on a GitHub Issue planning the feature
2. Discuss the approach in the issue thread
3. Follow [CONTRIBUTING.md](CONTRIBUTING.md) when submitting PRs
4. Ensure all changes respect Glazed Vision privacy principle
5. Update documentation as you implement features

---

## Dependencies We May Add

| Feature | Dependency | License | Why |
|---------|-----------|---------|-----|
| Global Hotkey | `pynput` or `keyboard` | MIT | For Panic-Kill feature |
| Packaging | `PyInstaller` or `Nuitka` | GPL/Apache | Build standalone .exe/.app |
| Web UI | `FastAPI` + `React` | MIT | Lite web version |
| Database | `sqlite3` (stdlib) | Public Domain | Local audit logs |

All dependencies must:
- Have permissive open-source licenses (MIT, Apache, BSD, GPL)
- Not introduce security vulnerabilities
- Not require internet connectivity
- Be actively maintained

---

## Release Schedule

- **v0.2** (Feb/Mar 2026): Guardian Mode + Global Hotkey
- **v0.3** (Apr/May 2026): Packaging + Windows/macOS executables
- **v0.4** (Jun/Jul 2026): Web lite version
- **v1.0** (Aug 2026): Stable, production-ready release

---

## Feedback

Have ideas for new features? Welcome!

1. **Open a GitHub Discussion** to brainstorm
2. **Check Privacy Impact**: Does it respect Glazed Vision?
3. **Check Scope**: Is it within the project's mission?
4. **Join the Community** to shape PZD's future

Thank you for your interest in PZD! 🎯

---

**Last Updated:** 2026-02-15  
**Maintained by:** PZD Core Team
