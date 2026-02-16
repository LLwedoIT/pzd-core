# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Guardian Mode specification (Acts I, II, III) for advanced security
- Global hotkey support (Panic-Kill) - planned for v0.2
- Web-based lite version - planned for v0.3
- Comprehensive documentation suite:
  - INDEX.md - Documentation guide
  - DEVELOPMENT.md - Developer setup and workflow
  - CODE_STANDARDS.md - Coding conventions and best practices
  - CONTRIBUTING.md - Contributor guidelines
  - FEATURES.md - Feature documentation and usage guide
  - TROUBLESHOOTING.md - Common issues and solutions
  - ROADMAP.md - Planned features and timeline
  - SECURITY.md - Privacy and security guarantees
  - CHANGELOG.md - Project history (this file)
- Infrastructure files:
  - .github/workflows/build-app.yml - CI/CD pipeline for multi-platform builds
  - .github/pull_request_template.md - PR template with checklist
  - netlify.toml - Netlify deployment configuration
  - Enhanced .gitignore with comprehensive patterns
- Landing page (web/index.html) with project information
- Support for multiple cameras with easy switching

### Changed
- Improved documentation structure with INDEX.md as central reference
- Enhanced .gitignore to protect sensitive data

### Fixed
- Camera initialization with proper backend cycling (Windows)

## [0.1-alpha] - 2026-02-15

### Added
- Core Presence Zone Detector application (app/main.py)
- Glazed Vision privacy-first motion detection
  - 99x99 Gaussian blur to prevent biometric data capture
  - Extreme downsampling (20x15) for privacy
  - Motion detection without facial recognition
- Kitten Buffer (Confidence Decay) state machine
  - Configurable grace period (5-600 seconds)
  - Smooth transition from Occupied → Empty
  - Prevents "Auto-Lock Panic"
- HPDManager for OS-level sleep inhibition
  - Windows: SetThreadExecutionState API
  - macOS: caffeinate subprocess
- Multi-camera support
  - Dynamic camera switching
  - Detection of multiple backends (CAP_DSHOW, CAP_MSMF)
- Calibration Mode with visual zone mapping
  - Blue rectangle overlay showing PZ boundaries
  - Real-time sensitivity adjustment via sliders
  - Depth score visualization
- System tray integration
  - State indicators (Green/Yellow/Red)
  - Minimize to tray functionality
  - Cross-platform support
- Tkinter GUI with "cyber-industrial" dark theme
  - Cyan accent (#00ffcc)
  - Dark background (#030303)
  - Sine-wave LED breathing animation
  - Responsive progress bar for confidence level
- Cross-platform support
  - Windows 10/11
  - macOS 10.14+
  - Linux (experimental)
- Project documentation:
  - README.md - Philosophy and overview
  - LOCAL_SETUP.md - Quick start guide (5 minutes)
  - ARCHITECTURE.md - Monorepo and infrastructure design
  - GUARDIAN_SPEC.md - Guardian mode specification
  - PROMPT_FOR_IDE_AGENT.md - IDE agent context

### Technical Details
- Python 3.8+ required
- OpenCV 4.8+ for vision processing
- Tkinter for GUI
- pystray for system tray
- NumPy and Pillow for image processing
- ~350 lines of core application code
- ~12 FPS sensor thread for efficiency
- <5% CPU usage at idle

---

## Version Planning

| Version | Target Date | Focus |
|---------|-------------|-------|
| v0.1-alpha | 2026-02-15 | Core Glazed Vision + UI |
| v0.2 | 2026-03 | Guardian Mode + Global Hotkey |
| v0.3 | 2026-04 | Windows/macOS Executables + Web Lite |
| v0.4 | 2026-05 | Audit Logging + Enterprise Features |
| v1.0 | 2026-08 | Stable Production Release |

---

## Planned Deprecations

- No current deprecations planned
- Breaking changes will be announced one minor version in advance

---

## Security

For security vulnerabilities, please email [MAINTAINER EMAIL] instead of opening a public issue.
See [SECURITY.md](SECURITY.md) for full disclosure policy.

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Last Updated:** 2026-02-15  
**Maintained by:** PZD Core Team
