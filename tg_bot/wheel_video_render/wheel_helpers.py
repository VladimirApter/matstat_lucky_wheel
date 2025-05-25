#!/usr/bin/env python3
"""wheel_helpers – colour, probability & string utilities for Lucky Wheel.

NOTE: All student‑fetching logic has been *moved* to :pymod:`student_data` to
eliminate previous duplication between this file and *main.py*.
Import :pyfunc:`student_data.fetch_students` if you need raw data – this module
keeps only the helper functions that are genuinely wheel‑specific (probability
weights, colour palette, label trimming).
"""

from __future__ import annotations
import colorsys

# Publicly re‑export so downstream code that previously did
# ``from wheel_helpers import fetch_students`` keeps working unchanged.
from services.student_data import fetch_students  # type: ignore[F401]  # re‑export

import wheel_config as cfg

__all__ = [
    "fetch_students",  # re‑exported convenience
    "weights",
    "hsl_color",
    "trim_name",
]

# ---------------------------------------------------------------------------
# Probability helpers
# ---------------------------------------------------------------------------

def weights(students: list[dict]) -> list[float]:
    """Return *normalised* inverse‑score probabilities for *students*.

    * Low scores ⇒ higher chance (inverse relation).
    * Add 0.01 guard to avoid div/0 when score is 0.
    * Clamp very small slices so wedges never fully disappear (< 0.01°).
    """
    inv = [1.0 / (s["score"] + 0.01) for s in students]
    total_inv = sum(inv)
    # Ensure a minimal positive probability for numerical stability
    probs = [max(v / total_inv, 0.01 / 360.0) for v in inv]
    norm = sum(probs)
    return [p / norm for p in probs]

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def hsl_color(idx: int, n: int) -> tuple[float, float, float]:
    """Evenly spread HSL colours mapped to RGB tuples (0‑1 floats)."""
    return colorsys.hls_to_rgb((idx / n) % 1.0, 0.60, 0.70)

# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------

def trim_name(name: str, prob: float) -> str:
    """Hide labels on tiny wedges and truncate overly long names."""
    if prob < 0.02:  # hide very small slices
        return ""
    if len(name) <= cfg.MAX_NAME_LEN:
        return name
    return name[: cfg.MAX_NAME_LEN] + "…"
