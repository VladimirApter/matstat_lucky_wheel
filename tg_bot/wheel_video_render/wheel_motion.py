#!/usr/bin/env python3
"""Angular motion profile for Lucky Wheel (accel → constant → decel)."""

from __future__ import annotations
import math, random
import wheel_config as cfg

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def angular_motion():
    """Return (angle_at(t), duration_s).  Units: t → seconds, angle → radians."""
    const_ms   = random.random() * cfg.CONST_MAX_MS
    accel_s    = cfg.ACCEL_MS / 1000.0
    const_s    = const_ms / 1000.0
    decel_s    = cfg.DECEL_MS / 1000.0
    max_omg_s  = cfg.MAX_OMG_MS * 1000.0

    full_accel = 0.5 * max_omg_s * accel_s
    full_const = max_omg_s * const_s
    full_decel = max_omg_s * decel_s / cfg.DECEL_K * (1.0 - math.exp(-cfg.DECEL_K))
    duration   = accel_s + const_s + decel_s

    def angle_at(t: float) -> float:
        if t < accel_s:
            return 0.5 * max_omg_s / accel_s * t * t
        if t < accel_s + const_s:
            return full_accel + max_omg_s * (t - accel_s)
        if t < duration:
            td = t - accel_s - const_s
            return (
                full_accel
                + full_const
                + max_omg_s * decel_s / cfg.DECEL_K * (1.0 - math.exp(-cfg.DECEL_K * td / decel_s))
            )
        return full_accel + full_const + full_decel

    return angle_at, duration
