# PZDetector™ Guardian: Service Specification

**By Chair-to-Keyboard™** | *The Human Centric Software Development Company*

This document defines the "Three-Act" handover logic that transforms PZDetector™ from a jiggler-alternative into a professional security service.

## Act I: "Locks the Door" (Immediate Secure)

**Constraint:** Must occur immediately when pzdConfidence reaches 0.0.

Logic: Call ctypes.windll.user32.LockWorkStation() (Windows) or the equivalent system lock.

Goal: Prevent UI tampering by anyone in the room while the user is away.

Act II: "Finishes the Job" (Hardware Sustenance)

Constraint: Only active if a "Guarded Process" is selected.

Logic: Maintain a SetThreadExecutionState or caffeinate inhibition while the process exists in the task list.

Target Tasks: Renders, Large Downloads, Windows Updates, Code Builds.

Act III: "Turns out the Lights" (Final Exit)

Constraint: Triggers the millisecond the Guarded Process vanishes or its CPU usage drops below 1%.

Action Sequence:

Sever Network: Disable the Primary NIC to prevent remote data exfiltration after the asset is rendered.

Release Vitality: End the sleep inhibition.

Hardware Sleep: Allow the machine to enter S3/S4 power states.

VS Code Agent Implementation Priority

Admin Helper: Build a small sub-module that requests elevation so Act III can actually disable the Wi-Fi/Ethernet.

Tray Icon: Move the main PZD window into a system tray icon (Green/Yellow/Red indicators).

Audit Log: Save the timestamp of Act III events so they can be shown to the user in a "Welcome Back" toast.