"""
App Awareness Service - Auto-pause Detection During Meetings

Monitors running processes to detect video conferencing applications
(Zoom, Teams, Google Meet, Skype, Discord) and auto-pauses presence detection
to prevent false locks during calls.

Cost: Negligible (~1% CPU, only process list scan)
Benefit: No false locks during presentations or video calls
"""

import psutil
from typing import Set, Callable, Optional
import threading
import time


class AppAwarenessService:
    """
    Monitors for meeting applications and auto-pauses presence detection.
    
    Detects: Zoom, Teams, Google Meet, Skype, Discord, OBS, Streamlabs, etc.
    """
    
    # Process names to watch for (case-insensitive, partial match)
    MEETING_APPS = {
        "zoom.exe",
        "ZoomOpener.exe",
        "teams.exe",
        "slack.exe",
        "skype.exe",
        "discord.exe",
        "Telegram.exe",
        "chrome.exe",  # For web-based meeting tools
        "firefox.exe",
        "msedge.exe",
        "obs64.exe",
        "obs32.exe",
        "streamlabs-obs.exe",
        "bluestacks.exe",
    }
    
    def __init__(self):
        """Initialize the App Awareness service."""
        self.is_running = False
        self.is_enabled = True
        self.check_interval_seconds = 5  # Check every 5 seconds
        
        # Event handlers
        self._meeting_started_handlers = []
        self._meeting_stopped_handlers = []
        
        # State
        self._currently_meeting = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def on_meeting_started(self, handler: Callable[[], None]):
        """Register handler for when meeting detected."""
        self._meeting_started_handlers.append(handler)
    
    def on_meeting_stopped(self, handler: Callable[[], None]):
        """Register handler for when meeting ends."""
        self._meeting_stopped_handlers.append(handler)
    
    def start(self):
        """Start monitoring for meeting applications."""
        if self.is_running:
            return
        
        self.is_running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="AppAwareness"
        )
        self._monitor_thread.start()
        print("[AppAwareness] Service started")
    
    def stop(self):
        """Stop monitoring."""
        self.is_running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("[AppAwareness] Service stopped")
    
    def _monitor_loop(self):
        """Background thread that monitors for meeting apps."""
        while self.is_running:
            try:
                is_meeting = self._check_for_meeting_apps()
                
                # Fire events on state change
                if is_meeting and not self._currently_meeting:
                    self._currently_meeting = True
                    self._trigger_meeting_started()
                
                elif not is_meeting and self._currently_meeting:
                    self._currently_meeting = False
                    self._trigger_meeting_stopped()
                
                time.sleep(self.check_interval_seconds)
            
            except Exception as e:
                print(f"[AppAwareness] Error in monitor loop: {e}")
                time.sleep(self.check_interval_seconds)
    
    def _check_for_meeting_apps(self) -> bool:
        """
        Check if any meeting applications are currently running.
        
        Returns:
            bool: True if meeting app detected
        """
        try:
            running_processes = {p.name().lower() for p in psutil.process_iter(['name'])}
            
            for app in self.MEETING_APPS:
                if app.lower() in running_processes:
                    print(f"[AppAwareness] Detected: {app}")
                    return True
            
            return False
        
        except Exception as e:
            print(f"[AppAwareness] Error checking processes: {e}")
            return False
    
    def is_in_meeting(self) -> bool:
        """
        Check current meeting status without waiting for monitor loop.
        
        Returns:
            bool: True if meeting app is running
        """
        return self._check_for_meeting_apps()
    
    def _trigger_meeting_started(self):
        """Fire meeting started event."""
        for handler in self._meeting_started_handlers:
            try:
                handler()
            except Exception as e:
                print(f"[AppAwareness] Error in meeting started handler: {e}")
    
    def _trigger_meeting_stopped(self):
        """Fire meeting stopped event."""
        for handler in self._meeting_stopped_handlers:
            try:
                handler()
            except Exception as e:
                print(f"[AppAwareness] Error in meeting stopped handler: {e}")
