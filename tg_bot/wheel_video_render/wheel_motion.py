from __future__ import annotations
import random, math
from typing import Callable, Tuple
from . import wheel_config as cfg

__all__ = ["angular_motion"]

_secure_rand = random.SystemRandom()

def angular_motion() -> Tuple[Callable[[float], float], float]:

    # ------------------------- random phase lengths -------------------------
    const_ms = _secure_rand.uniform(0.0, cfg.CONST_MAX_MS)  # ms

    # Convert to seconds for the math below
    accel_s = cfg.ACCEL_MS / 1000.0
    const_s = const_ms        / 1000.0
    decel_s = cfg.DECEL_MS / 1000.0

    # Peak angular velocity (cfg is rad/ms, convert → rad/s)
    w_max = cfg.MAX_OMG_MS * 1000.0

    # ----------------------- pre‑integrate distances ------------------------
    # θ during acceleration (∫0→acc αt dt) where α = w_max / accel_s
    ang_accel = 0.5 * w_max * accel_s

    # θ during constant speed
    ang_const = w_max * const_s

    # θ during decel (∫0→1 w_max·(1 − p)²·dec_s dp) = w_max*dec_s/3
    ang_decel = w_max * decel_s / 3.0

    duration = accel_s + const_s + decel_s

    # -------------------------- main angle func ----------------------------
    def angle_at(t: float) -> float:
        """Cumulative CW angle at time ``t`` (seconds)."""
        if t <= 0.0:
            return 0.0

        # Acceleration phase (quadratic ease‑in)
        if t < accel_s:
            return 0.5 * w_max / accel_s * t * t

        # Constant speed
        if t < accel_s + const_s:
            return ang_accel + w_max * (t - accel_s)

        # Deceleration (cubic ease‑out)
        if t < duration:
            td = t - accel_s - const_s   # time inside decel phase
            p  = td / decel_s            # normalised 0→1
            # θ = ang_accel + ang_const + w_max*dec_s * (1 - (1 - p)^3) / 3
            return ang_accel + ang_const + w_max * decel_s * (1 - (1 - p) ** 3) / 3.0

        # After finished – clamp to final angle
        return ang_accel + ang_const + ang_decel

    return angle_at, duration
