#!/usr/bin/env python3
"""Angular motion profile for Lucky Wheel (accel → const → smooth cubic decel).

Phases
------
1. **Acceleration** – quadratic ease‑in (constant angular acceleration until peak ω).
2. **Constant speed** – uniform rotation at ω_max for a random time ≤ ``cfg.CONST_MAX_MS``.
3. **Deceleration** – cubic ease‑out where ω(t) ∝ (1 − p)², giving a gentle settle.

The helper ``angular_motion()`` builds a self‑contained motion function
``angle_at(t)`` that returns the cumulative clockwise rotation **in radians** for
any time `t` ≥ 0, and the total duration of the spin.

Key implementation details
--------------------------
* **Secure randomness** – we use ``random.SystemRandom`` so results ignore any
  global ``random.seed()`` the caller might have set; each run is independent.
* **Pre‑integration** – angular distances of the three phases are pre‑computed
  to avoid run‑time branches inside the main integration.
* Module is pure‑Python and deterministic once instantiated; the heavy lifting
  is done up‑front so ``angle_at`` is extremely cheap to evaluate in render
  loops (e.g. 60 FPS × 16 000 frames).
"""

from __future__ import annotations
import random, math
from typing import Callable, Tuple
import wheel_config as cfg

__all__ = ["angular_motion"]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
_secure_rand = random.SystemRandom()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def angular_motion() -> Tuple[Callable[[float], float], float]:
    """Return ``(angle_at, duration_s)``.

    * ``angle_at(t)`` – cumulative CW rotation angle **in radians** at time `t`.
    * ``duration_s``  – total length of the spin in seconds.

    The constant‑speed phase is chosen randomly on each call using
    ``SystemRandom`` so two successive program runs never produce identical
    motion even if the caller sets the global random seed.
    """

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
