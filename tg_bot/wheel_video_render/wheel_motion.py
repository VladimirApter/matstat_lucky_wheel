#!/usr/bin/env python3
"""Angular motion profile for Lucky Wheel (accel → const → **smooth ease‑out decel**).

• Ускорение — линейное до `max_ω`.
• Константа — ровная.
• Торможение — кубический «ease‑out»: ω(t) = ω₀·(1 − p)², p ∈ [0,1].
  Это даёт более плавное замедление без резкого «дёргания» в финале.
"""

from __future__ import annotations
import math, random
import wheel_config as cfg

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def angular_motion():
    """Return (angle_at(t), duration_s) — t in seconds, angle in radians."""

    # Random middle (constant‑speed) phase length
    const_ms  = random.random() * cfg.CONST_MAX_MS

    accel_s   = cfg.ACCEL_MS / 1000.0
    const_s   = const_ms / 1000.0
    decel_s   = cfg.DECEL_MS / 1000.0
    w_max     = cfg.MAX_OMG_MS * 1000.0            # rad/s

    # Pre‑integrate segments for fast lookup
    ang_accel = 0.5 * w_max * accel_s              # θ during acceleration
    ang_const = w_max * const_s                    # θ during constant speed
    ang_decel = w_max * decel_s / 3.0              # ∫ w_max·(1−p)² dt, p=t/dec → w_max·dec/3
    duration  = accel_s + const_s + decel_s

    def angle_at(t: float) -> float:
        if t < accel_s:  # quadratic ease‑in
            return 0.5 * w_max / accel_s * t * t

        if t < accel_s + const_s:  # constant ω
            return ang_accel + w_max * (t - accel_s)

        if t < duration:  # cubic ease‑out
            td = t - accel_s - const_s           # time inside decel phase
            p  = td / decel_s                    # 0 → 1
            return ang_accel + ang_const + w_max * decel_s * (1 - (1 - p) ** 3) / 3

        # after finished (safety)
        return ang_accel + ang_const + ang_decel

    return angle_at, duration
