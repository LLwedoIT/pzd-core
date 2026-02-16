# PZDetector™ Documentation Index

**By Chair-to-Keyboard™** | *The Human Centric Software Development Company*

Welcome to PZDetector™! This index helps you find the right documentation for your needs.

PZDetector™ (software engine) manages the Presence Zone™ (proprietary presence boundary standard)—the professional HPD reference standard for defining and managing workspace presence.

## 🚀 Getting Started

**New user?** Start here:
1. [README.md](README.md) - Project overview, philosophy, and key innovations
2. [LOCAL_SETUP.md](LOCAL_SETUP.md) - Installation and basic usage in 5 minutes
3. [FEATURES.md](FEATURES.md) - Understand what PZD can do

**Want to run it right now?**
```bash
pip install -r app/requirements.txt
python app/main.py
```

---

## 📚 Documentation Map

### For End Users

| Document | Purpose |
|----------|---------|
| [FEATURES.md](FEATURES.md) | What features PZD has and how to use them |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [ROADMAP.md](ROADMAP.md) | What's coming next |

### For Developers

| Document | Purpose |
|----------|---------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Setting up dev environment, understanding the code |
| [CODE_STANDARDS.md](CODE_STANDARDS.md) | Coding conventions and best practices |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute code changes |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Project structure, monorepo design, CI/CD |

### For Contributors & Maintainers

| Document | Purpose |
|----------|---------|
| [PROMPT_FOR_IDE_AGENT.md](PROMPT_FOR_IDE_AGENT.md) | Context for IDE agents (VS Code, Cursor) |
| [GUARDIAN_SPEC.md](GUARDIAN_SPEC.md) | Feature specification for Guardian mode |
| [ROADMAP.md](ROADMAP.md) | Planned features and development timeline |

### Configuration

| File | Purpose |
|------|---------|
| [netlify.toml](netlify.toml) | Netlify deployment configuration |
| [.github/workflows/build-app.yml](.github/workflows/build-app.yml) | CI/CD pipeline for builds |
| [.github/pull_request_template.md](.github/pull_request_template.md) | PR template for contributions |

---

## 🏗️ Project Structure

```
pzd-core/
├── app/
│   ├── main.py                      Main application (all logic in one file)
│   └── requirements.txt              Python dependencies
├── web/
│   └── index.html                   Landing page (pzdetector.com)
├── .github/
│   ├── workflows/
│   │   └── build-app.yml           CI/CD pipeline
│   └── pull_request_template.md     PR template
├── README.md                        Project overview
├── ARCHITECTURE.md                  Monorepo and infrastructure
├── LOCAL_SETUP.md                   Quick start (5 min setup)
├── DEVELOPMENT.md                   Developer guide
├── CODE_STANDARDS.md                Coding conventions
├── CONTRIBUTING.md                  How to contribute
├── FEATURES.md                      Feature documentation
├── TROUBLESHOOTING.md               Common issues
├── GUARDIAN_SPEC.md                 Guardian mode specification
├── PROMPT_FOR_IDE_AGENT.md          Context for IDE agents
├── ROADMAP.md                       Planned features
├── netlify.toml                     Netlify config
└── INDEX.md                         This file
```

---

## 🔍 Quick Lookup by Task

### "I want to..."

**...use PZD**
→ [LOCAL_SETUP.md](LOCAL_SETUP.md) then [FEATURES.md](FEATURES.md)

**...understand what Glazed Vision is**
→ [FEATURES.md](FEATURES.md#2-glazed-vision-privacy-first-detection) or [README.md](README.md)

**...set up a development environment**
→ [DEVELOPMENT.md](DEVELOPMENT.md)

**...contribute code**
→ [CONTRIBUTING.md](CONTRIBUTING.md) → [CODE_STANDARDS.md](CODE_STANDARDS.md)

**...report a bug**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) → Open GitHub Issue

**...understand the architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**...see what features are planned**
→ [ROADMAP.md](ROADMAP.md)

**...fix a specific issue**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**...understand how Presence Confidence works**
→ [FEATURES.md](FEATURES.md#3-presence-confidence--kitten-buffer)

**...modify Guardian mode**
→ [GUARDIAN_SPEC.md](GUARDIAN_SPEC.md) and [ROADMAP.md](ROADMAP.md#-priority-guardian-mode-security-features)

---

## 🎯 Core Concepts

### Presence Zone (PZ)
The physical area around your workspace where you're considered "present." Configurable in the UI.
- Learn more: [FEATURES.md - Presence Zone](FEATURES.md#1-presence-zone-pz-detection)

### Glazed Vision
Privacy-first motion detection using blur and downsampling (99x99 kernel). Never captures biometrics.
- Learn more: [FEATURES.md - Glazed Vision](FEATURES.md#2-glazed-vision-privacy-first-detection)

### Kitten Buffer
"Confidence Decay"—grace period before system lock. Prevents instant lock-out during interruptions.
- Learn more: [FEATURES.md - Kitten Buffer](FEATURES.md#3-presence-confidence--kitten-buffer)

### Depth Score
Proximity measurement based on motion blob size.
- Learn more: [FEATURES.md - Depth Score](FEATURES.md#4-depth-score-proximity-measurement)

### HPD (Human Presence Detection)
OS-level detection logic for sleep inhibition (SetThreadExecutionState on Windows, caffeinate on macOS).
- Learn more: [DEVELOPMENT.md - HPDManager](DEVELOPMENT.md#core-modules-in-appmainpy)

---

## 📋 Checklists

### Before Starting Development
- [ ] Read [PROMPT_FOR_IDE_AGENT.md](PROMPT_FOR_IDE_AGENT.md) for project philosophy
- [ ] Read [DEVELOPMENT.md](DEVELOPMENT.md) to set up environment
- [ ] Read [CODE_STANDARDS.md](CODE_STANDARDS.md) for coding conventions

### Before Submitting a PR
- [ ] Code follows [CODE_STANDARDS.md](CODE_STANDARDS.md)
- [ ] Changes respect Glazed Vision privacy principle
- [ ] All public methods have docstrings
- [ ] Tested locally: `python app/main.py` works
- [ ] Commit messages follow conventional commits format
- [ ] No hardcoded secrets or API keys
- [ ] Documentation updated if needed
- See: [CONTRIBUTING.md - Pull Request Checklist](CONTRIBUTING.md#pull-request-checklist)

### Before Reporting a Bug
- [ ] Checked [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [ ] Gathered system info (OS, Python version, camera model)
- [ ] Noted when issue occurs and steps to reproduce
- [ ] Checked if issue already exists on GitHub

---

## 🔗 External Links

- **GitHub Repository:** https://github.com/LLwedoIT/pzd-core
- **Landing Page:** https://pzdetector.com (hosted on Netlify)
- **PyPI Package:** (Coming soon)
- **Issues Tracker:** https://github.com/LLwedoIT/pzd-core/issues
- **Discussions:** https://github.com/LLwedoIT/pzd-core/discussions

---

## ❓ FAQ

**Q: What's the difference between PZD and a mouse jiggler?**
A: PZD is privacy-first presence detection using Glazed Vision. It detects actual occupancy, not just preventing key presses. See [README.md](README.md).

**Q: Can PZD identify me?**
A: No. It uses extreme blur (99x99 Gaussian kernel) and only detects motion blobs, never faces or biometrics. See [FEATURES.md](FEATURES.md#2-glazed-vision-privacy-first-detection).

**Q: How does the Kitten Buffer work?**
A: It's a grace period that smoothly decays from 100% to 0% confidence. You can adjust the duration (5-600 seconds). See [FEATURES.md](FEATURES.md#3-presence-confidence--kitten-buffer).

**Q: Does PZD work offline?**
A: Yes, completely. It's local-first, no cloud or internet required. See [README.md](README.md#security--privacy).

**Q: How do I contribute?**
A: Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_STANDARDS.md](CODE_STANDARDS.md).

**Q: What camera do I need?**
A: Any USB webcam. No special hardware required. See [LOCAL_SETUP.md](LOCAL_SETUP.md#prerequisites).

**Q: Is PZD open source?**
A: Yes, fully. Source available at https://github.com/LLwedoIT/pzd-core.

---

## 📞 Support

- **Documentation Questions?** Create a GitHub Discussion
- **Found a Bug?** Open a GitHub Issue (check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first)
- **Want to Contribute?** Read [CONTRIBUTING.md](CONTRIBUTING.md)
- **Privacy Concerns?** See [README.md - Security & Privacy](README.md#security--privacy)

---

**Last Updated:** 2026-02-15  
**Version:** 0.1-alpha
