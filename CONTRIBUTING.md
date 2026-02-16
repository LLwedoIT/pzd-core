# Contributing to PZD (Presence Zone Detector)

Thank you for your interest in contributing to PZD! This guide will help you get started.

## Before You Start

Please read [PROMPT_FOR_IDE_AGENT.md](PROMPT_FOR_IDE_AGENT.md) to understand the project philosophy and core principles, especially:
- **Glazed Vision**: Privacy-first detection—never save frames or process biometrics
- **Kitten Buffer**: Confidence decay logic prevents false lock-outs
- **Sine-Wave Signaling**: UI feedback uses smooth breathing patterns, not harsh states

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/LLwedoIT/pzd-core.git
   cd pzd-core
   ```

2. Set up your local environment
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r app/requirements.txt
   ```

4. Run the application
   ```bash
   python app/main.py
   ```

For detailed setup, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Code Standards

Follow the coding standards in [CODE_STANDARDS.md](CODE_STANDARDS.md). Key points:
- All changes must preserve the Glazed Vision privacy principle
- Maintain ~12 FPS for the sensor thread
- Use descriptive variable names following pzd/hpd terminology
- Add docstrings to all classes and methods

## Making Changes

### For Bug Fixes
1. Create a branch: `git checkout -b fix/bug-description`
2. Make your changes
3. Test locally: `python app/main.py`
4. Add a test case if applicable
5. Commit: `git commit -m "fix: clear description of the bug fix"`
6. Push and open a Pull Request

### For New Features
1. Check [ROADMAP.md](ROADMAP.md) to see if this aligns with project direction
2. Create a branch: `git checkout -b feature/feature-name`
3. Update docstrings and user-facing documentation
4. Test thoroughly
5. Commit: `git commit -m "feat: clear description of the feature"`
6. Push and open a Pull Request with a clear description

### For Documentation
1. Create a branch: `git checkout -b docs/what-you-are-documenting`
2. Make improvements to existing or new documentation files
3. Commit: `git commit -m "docs: clear description of changes"`

## Pull Request Checklist

Before submitting a PR, ensure:
- [ ] Code follows [CODE_STANDARDS.md](CODE_STANDARDS.md)
- [ ] All changes respect Glazed Vision privacy principles
- [ ] Docstrings are added/updated
- [ ] Code has been tested locally
- [ ] Commit messages follow the format: `type: description` (feat, fix, docs, style, refactor, test, chore)
- [ ] No hardcoded secrets or API keys
- [ ] main.py can still run without errors: `python app/main.py`

## Testing

Before submitting a PR:
```bash
# Run the app in calibration mode to test the UI
python app/main.py

# Test camera switching and sensor initialization
# Test the Kitten Buffer decay with values: 5s, 45s, 600s
```

See [TESTING.md](TESTING.md) for more detailed testing guidance.

## Commit Message Format

Use clear, concise commit messages:
```
feat: add panic-kill global hotkey support
fix: resolve camera initialization with CAP_DSHOW on Windows
docs: add troubleshooting guide for common camera issues
refactor: simplify motion detection logic in GlazedSensor
style: improve variable naming in HPDManager class
test: add unit tests for presence confidence decay
```

## Communication

- For questions or discussion, open a GitHub Discussion
- For bugs, open a GitHub Issue
- For security concerns, please email (add contact info if available) rather than using public issues

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for helping make PZD better! 🎯
