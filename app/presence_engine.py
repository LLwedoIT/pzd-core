"""
Presence Engine - Core State Machine for Multi-Sensor Waterfall Detection

Orchestrates the three-stage sensor fusion waterfall:
1. HID (keyboard/mouse) - Always running, negligible CPU
2. Camera (motion) - Only when HID suggests absence
3. Network/locks - Only when all sensors confirm absence

State machine:
  ACTIVE (Green)    -> Countdown > 10s, HID only
  WARNING (Yellow)  -> Countdown 1-10s, HID + Camera
  LOCKING (Red)     -> Instant, executing lock
  PAUSED (Gray)     -> User paused detection
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Optional
from dataclasses import dataclass


class PresenceState(Enum):
    """Presence detection state."""
    ACTIVE = "active"
    WARNING = "warning"
    LOCKING = "locking"
    PAUSED = "paused"


@dataclass
class StateChangeEvent:
    """Event fired when state changes."""
    old_state: PresenceState
    new_state: PresenceState
    timestamp: datetime


class PresenceEngine:
    """
    Core orchestrator for presence detection using waterfall pattern.
    
    Manages state transitions and coordinates HID, camera, and lock sensors.
    """
    
    # Default configuration
    DEFAULT_LOCK_TIMEOUT_SECONDS = 60
    WARNING_THRESHOLD_SECONDS = 10
    
    def __init__(
        self,
        hid_monitor,
        camera_sensor,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS
    ):
        """
        Initialize the Presence Engine.
        
        Args:
            hid_monitor: HIDMonitor instance
            camera_sensor: GlazedSensor or similar camera sensor instance
            lock_timeout_seconds: Seconds until lock if idle
        """
        self.hid_monitor = hid_monitor
        self.camera_sensor = camera_sensor
        self.lock_timeout_seconds = lock_timeout_seconds
        
        # State management
        self._current_state = PresenceState.ACTIVE
        self._seconds_remaining = lock_timeout_seconds
        self._pause_until: Optional[datetime] = None
        self._state_entered_at = datetime.now()
        
        # Event handlers
        self._state_changed_handlers = []
        self._lock_triggered_handlers = []
        self._grace_period_started_handlers = []
    
    @property
    def current_state(self) -> PresenceState:
        """Get current state."""
        return self._current_state
    
    @property
    def seconds_remaining(self) -> int:
        """Get seconds until lock."""
        return self._seconds_remaining
    
    @property
    def is_paused(self) -> bool:
        """Check if detection is paused."""
        return self._current_state == PresenceState.PAUSED
    
    def on_state_changed(self, handler: Callable[[StateChangeEvent], None]):
        """Register handler for state changes."""
        self._state_changed_handlers.append(handler)
    
    def on_lock_triggered(self, handler: Callable[[], None]):
        """Register handler for lock triggered."""
        self._lock_triggered_handlers.append(handler)
    
    def on_grace_period_started(self, handler: Callable[[], None]):
        """Register handler for grace period started."""
        self._grace_period_started_handlers.append(handler)
    
    def tick(self):
        """
        Called every second to update presence detection.
        Implements the waterfall pattern with proper state transitions.
        """
        # Handle pause mode
        if self._current_state == PresenceState.PAUSED:
            if self._pause_until and datetime.now() >= self._pause_until:
                self._set_state(PresenceState.ACTIVE)
                self._seconds_remaining = self.lock_timeout_seconds
            return
        
        # Stage 1: HID Check (always active, negligible cost)
        idle_seconds = self.hid_monitor.get_idle_seconds()
        
        if idle_seconds < 1.0:
            # User is active - reset timer
            if self._seconds_remaining != self.lock_timeout_seconds:
                self._seconds_remaining = self.lock_timeout_seconds
                if self._current_state != PresenceState.ACTIVE:
                    self._set_state(PresenceState.ACTIVE)
            return
        
        # User has been idle, decrement countdown
        self._seconds_remaining -= 1
        
        # Check for state transitions
        if self._seconds_remaining <= 0:
            # Time to lock!
            self._set_state(PresenceState.LOCKING)
            self._trigger_lock()
            # Reset after lock
            self._seconds_remaining = self.lock_timeout_seconds
            self._set_state(PresenceState.ACTIVE)
        
        elif self._seconds_remaining <= self.WARNING_THRESHOLD_SECONDS:
            # Entering warning state - time for expensive sensor checks
            if self._current_state == PresenceState.ACTIVE:
                self._set_state(PresenceState.WARNING)
                self._trigger_grace_period()
                # Stage 2/3: Poll camera if in warning state
                self._check_camera_presence()
        
        elif self._current_state == PresenceState.WARNING and self._seconds_remaining > self.WARNING_THRESHOLD_SECONDS:
            # Activity detected, return to active
            self._set_state(PresenceState.ACTIVE)
    
    def _check_camera_presence(self):
        """
        Stage 2/3: Check camera for actual presence.
        Only called if HID suggests absence.
        """
        if not self.camera_sensor:
            return
        
        try:
            # Get recent motion confidence from camera
            # This is a lightweight check (one frame)
            confidence = getattr(self.camera_sensor, 'motion_confidence', 0.0)
            
            # If camera detects motion, reset timer
            if confidence > 0.3:  # Threshold: 30% confidence
                self._seconds_remaining = self.lock_timeout_seconds
                self._set_state(PresenceState.ACTIVE)
        except Exception as e:
            print(f"[PresenceEngine] Error checking camera presence: {e}")
    
    def pause(self, duration_minutes: int = 60):
        """
        Pause presence detection for specified duration.
        
        Args:
            duration_minutes: How long to pause (default 60)
        """
        self._pause_until = datetime.now() + timedelta(minutes=duration_minutes)
        self._set_state(PresenceState.PAUSED)
    
    def resume(self):
        """Resume presence detection."""
        self._pause_until = None
        self._seconds_remaining = self.lock_timeout_seconds
        self._set_state(PresenceState.ACTIVE)
    
    def _set_state(self, new_state: PresenceState):
        """
        Set new state and fire state changed event.
        
        Args:
            new_state: New state to transition to
        """
        if new_state == self._current_state:
            return
        
        old_state = self._current_state
        self._current_state = new_state
        self._state_entered_at = datetime.now()
        
        # Fire event
        event = StateChangeEvent(old_state, new_state, self._state_entered_at)
        for handler in self._state_changed_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[PresenceEngine] Error in state changed handler: {e}")
    
    def _trigger_grace_period(self):
        """Fire grace period started event."""
        for handler in self._grace_period_started_handlers:
            try:
                handler()
            except Exception as e:
                print(f"[PresenceEngine] Error in grace period handler: {e}")
    
    def _trigger_lock(self):
        """Fire lock triggered event."""
        for handler in self._lock_triggered_handlers:
            try:
                handler()
            except Exception as e:
                print(f"[PresenceEngine] Error in lock triggered handler: {e}")
    
    def get_state_display(self) -> str:
        """
        Get human-readable state display for UI.
        
        Returns:
            str: E.g., "ACTIVE - 45s" or "WARNING - 5s" or "LOCKED" or "PAUSED - 30 min"
        """
        if self._current_state == PresenceState.ACTIVE:
            return f"ACTIVE - {self._seconds_remaining}s"
        elif self._current_state == PresenceState.WARNING:
            return f"WARNING - {self._seconds_remaining}s"
        elif self._current_state == PresenceState.LOCKING:
            return "LOCKED"
        elif self._current_state == PresenceState.PAUSED:
            if self._pause_until:
                remaining = self._pause_until - datetime.now()
                minutes = int(remaining.total_seconds() / 60)
                return f"PAUSED - {minutes} min"
            return "PAUSED"
        return str(self._current_state.value).upper()
