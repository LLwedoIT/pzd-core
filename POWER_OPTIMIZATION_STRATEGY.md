# Power Efficiency Strategy for PZDetector™

**By Chair-to-Keyboard™** | *The Human Centric Software Development Company*

## Current Power Profile (UNOPTIMIZED)
- **GlazedSensor**: 16.7 FPS continuous (60ms intervals)
- **update_loop**: 10 Hz GUI refresh (100ms) even when idle
- **Motion detection**: Full OpenCV processing every frame
- **LED animation**: Constant canvas redraws
- **Estimated battery life**: 2-3 hours on laptop

## Core Problem: Polling Architecture
Current design:
```
while app_running:
    capture_frame()          # Always running
    process_frame()          # Always running
    update_ui()              # Always running
    sleep(60ms + processing_time)
```

This burns power continuously regardless of actual motion or need.

## Better Architecture: Event-Driven + Lazy Processing

### Strategy 1: Adaptive Frame Rate (Biggest Win - ~60% power reduction)

**Concept**: Vary capture rate based on motion likelihood

```python
# Instead of fixed 16.7 FPS:
class AdaptiveFrameRate:
    IDLE_FPS = 1          # 1 FPS (~1000ms) - nothing happening
    LOW_FPS = 5           # 5 FPS (200ms) - some motion detected
    HIGH_FPS = 16.7       # 16.7 FPS (60ms) - active motion detected
    
    current_fps = IDLE_FPS
    
    def adjust_based_on_confidence(self, presence_confidence):
        if presence_confidence < 0.1:
            current_fps = IDLE_FPS      # No motion for 10+ frames
        elif presence_confidence < 0.5:
            current_fps = LOW_FPS       # Moderate motion
        else:
            current_fps = HIGH_FPS      # Active motion
```

**Implementation**: 
- Track motion stability (keep count of "motion-free" frames)
- Once 30+ frames without motion → drop to 1 FPS
- When motion detected → jump back to 16.7 FPS
- Smooth transitions (5 FPS in between)

**Power impact**: 1 FPS vs 16.7 FPS = **94% reduction in frame processing**

---

### Strategy 2: Early Exit Motion Detection (Skip Full Processing)

**Concept**: Quick pre-check before expensive operations

```python
# Frame 1 (cheap check, ~2ms):
simple_diff = compare_with_prev_frame()  # Just pixel delta
if simple_diff < MOTION_THRESHOLD:
    skip_full_processing()
    return early

# Only if motion detected, do expensive stuff:
gaussian_blur()      # ~5ms
contour_analysis()   # ~3ms
proximity_calc()     # ~1ms
```

**How it works**:
- Every frame: Fast pixel-difference check (2-3ms)
- Only if change detected: Run full OpenCV pipeline
- Reduces per-frame cost by ~70% on static scenes

**Power impact**: Eliminates most processing on idle backgrounds

---

### Strategy 3: Smart Pause Mechanism (When Not Needed)

**Concept**: Stop sensor when window hidden or Guardian Mode active

```python
def hide_window(self):
    self.root.withdraw()
    self.sensor.pause()  # Stop continuous capture
    # Only wake sensor if:
    # - Window shown again, OR
    # - Guardian Mode enabled, OR
    # - Hotkey pressed

def on_guardian_enabled(self):
    if self.sensor.paused:
        self.sensor.resume()  # Resume at LOW_FPS only
```

**Scenarios**:
- **Minimized**: Pause completely (CPU ~0%)
- **Guardian Mode**: Resume at 5 FPS (low continuous monitor)
- **Active calibration**: Full 16.7 FPS

**Power impact**: Eliminates ~80% of power when app is minimized

---

### Strategy 4: Motion History Optimization

**Current waste**: 
```python
# Keeps 3 frames in memory
self.motion_history = [True, False, True]
```

**Better approach**:
```python
# Just keep counters, not frames
self.motion_free_frames = 0
self.motion_frames = 0

# Instead of appending/popping:
if is_motion:
    self.motion_frames += 1
    self.motion_free_frames = 0
else:
    self.motion_free_frames += 1
    self.motion_frames = 0
```

**Power impact**: Reduces memory thrashing, ~5% CPU reduction

---

### Strategy 5: Batch UI Updates (Not Every 100ms)

**Current approach**:
```python
# Updates UI every 100ms even if nothing changed
self.root.after(100, self.update_loop)
```

**Better approach**:
```python
# Only update when data changes
def update_loop(self):
    if self.presence_confidence != self.last_displayed_confidence:
        self.led_canvas.itemconfig(self.led_dot, fill=color)
        self.last_displayed_confidence = self.presence_confidence
    
    # Adjust loop frequency based on activity
    next_interval = 100 if is_motion else 500
    self.root.after(next_interval, self.update_loop)
```

**Power impact**: Reduces UI thread wakeups by ~70%

---

### Strategy 6: Resolution-Aware Processing

**Current**: Always resize to 320x240 for display

**Better**: Process at resolution matching FPS
```python
if adaptive_fps == IDLE_FPS:       # 1 FPS
    process_at = (160, 120)        # Half resolution
elif adaptive_fps == LOW_FPS:      # 5 FPS
    process_at = (240, 180)        # 2/3 resolution
else:                               # 16.7 FPS
    process_at = (320, 240)        # Full resolution
```

**Power impact**: ~40% reduction in processing power at low FPS

---

## Expected Power Profile After Optimization

| Scenario | FPS | CPU | Battery Life |
|----------|-----|-----|-----|
| **BEFORE** (unoptimized) | 16.7 | ~45% | 2-3 hours |
| **AFTER** (idle) | 1 | ~5% | 20+ hours |
| **AFTER** (low motion) | 5 | ~12% | 12+ hours |
| **AFTER** (active) | 16.7 | ~35% | 4-5 hours |

---

## Implementation Priority

### Phase 1 (Mandatory - Do First)
1. **Adaptive Frame Rate** - 60% power reduction, moderate complexity
2. **Smart Pause** - 80% reduction when minimized, easy
3. **Early Exit Detection** - 70% reduction in processing, simple

**Expected result**: ~4x battery life improvement

### Phase 2 (Nice to Have)
1. **Batch UI Updates** - Minor improvement
2. **Motion History Optimization** - Hygiene improvement
3. **Resolution Scaling** - Additional 30-40% at low FPS

---

## Architectural Changes Required

### In `GlazedSensor` class:
- Add `self.target_fps` and `self.idle_timer` 
- Implement sleep time calculation based on adaptive FPS
- Add early exit before full processing
- Add pause/resume methods

### In `App` class:
- Add `sensor.pause()` on window minimize
- Add `sensor.resume()` on window show
- Track Guardian Mode and adjust sensor accordingly
- Batch UI updates instead of every 100ms

### New configuration:
```python
POWER_PROFILE = {
    "aggressive": {
        "idle_fps": 0.5,      # Even lower
        "low_fps": 2,
        "high_fps": 8,        # Never full speed
    },
    "balanced": {
        "idle_fps": 1,
        "low_fps": 5,
        "high_fps": 16.7,     # Our current target
    },
    "responsive": {
        "idle_fps": 5,
        "low_fps": 10,
        "high_fps": 30,       # Max responsiveness
    }
}
```

---

## Testing Before/After

**Measurement method**:
```powershell
# Monitor power usage
Get-Process python | Measure-Object -Property WorkingSet | Sum
Get-Counter "Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 60
```

**Scenarios to test**:
1. App minimized for 5 minutes
2. Static scene (no motion) for 5 minutes
3. Continuous motion for 5 minutes
4. Guardian Mode enabled

---

## Why This Matters

A presence detection app running 24/7 on a laptop:
- **Current**: Laptop dies in 2-3 hours, **unusable**
- **After optimization**: Survive 8+ hours idle, **practical**
- **Use case**: Leave app running during work day, plugged in

The difference between a hobby project and a real utility.

---

## Decision Point

These strategies are **not mutually exclusive**. We should implement ALL of Phase 1 because:
1. Relatively contained changes
2. Massive power benefit (4x improvement)
3. No loss of accuracy in important scenarios
4. Improves user experience (faster UI response in active mode)

Recommendation: **Implement Phase 1 strategies before releasing v1.0**
