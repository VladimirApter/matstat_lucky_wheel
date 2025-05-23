#!/usr/bin/env python3
"""wheel_segment – geometry utilities for Lucky Wheel.

This helper converts the **probability table** used by the front‑end into exact
angular bounds for every wedge, so that the back‑end (video renderer, bots,
tests) can reason about *where* each student sits on the dial.

Angle convention (same as the browser):
    0°  → pointer direction (12 o’clock)
    +CW → clockwise (i.e. mathematically negative)

Public API
----------
segment_bounds(group) -> list[(start_deg, end_deg)]
    Inclusive‑exclusive bounds for every student, clockwise degrees.
segment_mid(group, idx) -> float
    Mid‑angle of wedge #idx (CW deg).
random_angle_in_segment(group, idx, *, rng=None, margin_deg=1.0,
                        margin_frac=0.05) -> float
    Cryptographically‑secure random angle **inside** wedge idx, leaving a small
    safety margin so the pointer never lands on a boundary.

The module has **no heavyweight dependencies** – only `wheel_helpers`, so it
works fine even in minimal environments where MoviePy / Pillow are missing.
"""

from __future__ import annotations

import random
from typing import List, Tuple

from wheel_helpers import fetch_students, weights

__all__ = [
    "segment_bounds",
    "segment_mid",
    "random_angle_in_segment",
]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cumulative(fracs: List[float]) -> List[float]:
    """Return cumulative sum prepended with 0 and appended with 1."""
    acc: List[float] = [0.0]
    total = 0.0
    for f in fracs:
        total += f
        acc.append(total)
    # The probabilities coming from `weights` should sum to 1.0 but floating‑
    # point drift might produce 0.999999… Clamp the last value so we always end
    # exactly at 1 – safer downstream.
    acc[-1] = 1.0
    return acc

# ---------------------------------------------------------------------------
# Public geometry API
# ---------------------------------------------------------------------------

def segment_bounds(group: str) -> List[Tuple[float, float]]:
    """Return clockwise degree bounds for every student of *group*."""
    students = fetch_students(group)
    probs    = weights(students)  # list of fractions that sum ≈ 1.0

    cum = _cumulative(probs)
    return [(s * 360.0, e * 360.0) for s, e in zip(cum[:-1], cum[1:])]


def segment_mid(group: str, idx: int) -> float:
    """Centre angle (CW deg) of wedge *idx*."""
    start, end = segment_bounds(group)[idx]
    return (start + end) / 2.0


def random_angle_in_segment(
    group: str,
    idx: int,
    *,
    rng: random.Random | None = None,
    margin_deg: float = 1.0,
    margin_frac: float = 0.05,
) -> float:
    """Secure random angle inside wedge *idx* with a configurable margin.

    The function never returns a value closer than *margin_deg* **or**
    *margin_frac*×span (whichever is smaller) to either of the boundaries.
    This avoids ambiguous frames where the pointer appears to straddle two
    segments.
    """
    if rng is None:
        rng = random.SystemRandom()

    start, end = segment_bounds(group)[idx]
    span = end - start
    margin = min(margin_deg, span * margin_frac)

    if span <= 2 * margin:
        # Extremely small wedge – just fall back to its centre.
        return (start + end) / 2.0

    return rng.uniform(start + margin, end - margin)
