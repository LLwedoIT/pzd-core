"""
HID Input Monitor - Stage 1 of Waterfall Presence Detection

Monitors keyboard and mouse input for idle time detection.
Uses Windows GetLastInputInfo API to track system-wide input.

Cost: Negligible (~0.01% CPU)
Benefit: Instant detection of user activity, prevent false locks during typing
"""

import ctypes
import time
from typing import Optional


class HIDMonitor:
    """
    Monitors keyboard and mouse input idle time.
    
    Uses Windows GetLastInputInfo() API to detect when user was last active.
    This is Stage 1 of the waterfall - the cheapest and most immediate sensor.
    """
    
    # Win32 API structures
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    
    # Import GetLastInputInfo from user32.dll
    _GetLastInputInfo = ctypes.windll.user32.GetLastInputInfo
    
    def __init__(self):
        """Initialize the HID monitor."""
        self.is_enabled = False
        self.initialized = False
        self._initialize()
    
    def _initialize(self) -> bool:
        """
        Initialize the HID monitor by testing the API.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Test that we can call the API
            _ = self.get_idle_seconds()
            self.is_enabled = True
            self.initialized = True
            return True
        except Exception as e:
            print(f"[HIDMonitor] Failed to initialize: {e}")
            self.is_enabled = False
            self.initialized = False
            return False
    
    def get_idle_seconds(self) -> float:
        """
        Get seconds since last keyboard or mouse input.
        
        Returns:
            float: Seconds since last HID activity (0 if error)
        """
        try:
            if not self.initialized:
                return 0.0
            
            # Create LASTINPUTINFO structure
            lii = self.LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(self.LASTINPUTINFO)
            
            # Call GetLastInputInfo
            if not self._GetLastInputInfo(ctypes.byref(lii)):
                # API call failed, return 0 (assume active)
                return 0.0
            
            # GetTickCount returns milliseconds since system start
            current_tick = ctypes.windll.kernel32.GetTickCount()
            idle_ms = current_tick - lii.dwTime
            
            # Handle wrap-around (GetTickCount wraps every ~49.7 days)
            if idle_ms < 0:
                idle_ms = 0
            
            # Convert to seconds
            return idle_ms / 1000.0
        
        except Exception as e:
            # Log error and return 0 (safe default: assume user is active)
            print(f"[HIDMonitor] Error getting idle time: {e}")
            return 0.0
    
    def is_active(self, threshold_seconds: float = 1.0) -> bool:
        """
        Check if user is currently active (recent input).
        
        Args:
            threshold_seconds: Consider user active if activity within this many seconds
        
        Returns:
            bool: True if user was active recently
        """
        idle = self.get_idle_seconds()
        return idle < threshold_seconds
    
    def is_idle(self, threshold_seconds: float = 60.0) -> bool:
        """
        Check if user has been idle for at least this long.
        
        Args:
            threshold_seconds: Consider idle if no activity for at least this many seconds
        
        Returns:
            bool: True if user idle for threshold time
        """
        idle = self.get_idle_seconds()
        return idle >= threshold_seconds
