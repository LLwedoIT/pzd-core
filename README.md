PZD: Presence Zone Detector

Software-Defined Presence for the Focused Workspace.

PZD is a cross-platform utility that manages the Presence Zone (PZ)—the physical space between the user and the machine. By leveraging industry-standard Human Presence Detection (HPD) logic, PZD ensures system continuity during periods of low activity, preventing the "Auto-Lock Panic" while respecting user privacy.

The Philosophy

Traditional idle timers are binary and rigid. PZD introduces Presence Confidence, a state-based approach that understands that "presence" isn't just about moving a mouse. Whether you are petting a cat, taking a call, or deep in thought, PZD maintains system vitality.

Key Innovations

The Presence Zone (PZ): A defined radius around the workspace where the user is considered active.

Glazed Vision (Fog Mode): A privacy-first HPD method. Instead of high-definition video, PZD uses low-power, blurred "blob" detection to verify occupancy without capturing biometric data.

The Kitten Buffer (Confidence Decay): A configurable safety net that smoothly transitions from "Occupied" to "Empty." It provides the grace period needed for real-life interruptions.

Sine-Wave Signaling: Non-intrusive hardware feedback. The camera LED "breathes" using a sine-wave pattern to signal that the Zone is secured, rather than flashing or staying static.

Zero-Signal Architecture: PZD explicitly avoids Bluetooth and other high-risk wireless protocols, making it suitable for high-security environments.

PZD: Presence Zone Detector

Software-Defined Presence for the Focused Workspace.

PZD is the definitive utility for managing the Presence Zone™ (PZ)—the proprietary spatial concept defining the relationship between human proximity and system vitality. By leveraging industry-standard Human Presence Detection (HPD), PZD establishes a secure, private, and intelligent digital perimeter.

Coining the Presence Zone™

The Presence Zone (PZ) is more than an idle timer; it is a software-defined boundary. We are coining this term to move the industry away from "inactivity" and toward "spatial awareness."


Technical Architecture

PZD is built to align with native OS power management kernels:

Windows: Utilizes SetThreadExecutionState and Windows 11 Presence Sensing APIs.

macOS: Utilizes IOPMAssertionCreateWithDescription and caffeinate inhibitors.

Getting Started

Prerequisites

Python 3.8+

Tkinter (for GUI)

Hardware: Standard Webcam (for Glazed Vision) or HPD-capable sensor.

Installation

Clone the repo: git clone https://github.com/yourusername/pzd-core

Run the prototype: python pzd_app.py

Configure your Kitten Buffer in the settings.

Security & Privacy

PZD is local-first. No images are ever saved, uploaded, or processed beyond the local "Glazed" state check. It is designed to be invisible to both the user and the network.

Connected to pzdetector.com