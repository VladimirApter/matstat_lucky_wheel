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
    if rng is None:
        rng = random.SystemRandom()

    start, end = segment_bounds(group)[idx]
    span = end - start
    margin = min(margin_deg, span * margin_frac)

    if span <= 2 * margin:
        # Extremely small wedge – just fall back to its centre.
        return (start + end) / 2.0

    return rng.uniform(start + margin, end - margin)
