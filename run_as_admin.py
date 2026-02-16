#!/usr/bin/env python3
"""
PZDetector Admin Launcher
Automatically requests admin privileges and runs the app
"""

import ctypes
import sys
import os
import subprocess

def is_admin():
    """Check if script is running as admin"""
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run script with admin privileges"""
    if not is_admin():
        print("[Launcher] Requesting administrator privileges...")
        # Re-run this script as admin
        ctypes.windll.shell.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

def main():
    """Run PZDetector app"""
    # Ensure we have admin privileges
    run_as_admin()
    
    print("[Launcher] Running with admin privileges")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run the main app
    try:
        subprocess.Popen([sys.executable, "-u", "app/main.py"])
    except Exception as e:
        print(f"[Error] Failed to start app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
