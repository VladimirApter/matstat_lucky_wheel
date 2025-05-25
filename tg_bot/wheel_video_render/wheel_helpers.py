from __future__ import annotations
import colorsys

from services.student_data import fetch_students  # type: ignore[F401]  # re‑export

from . import wheel_config as cfg

__all__ = [
    "fetch_students",  # re‑exported convenience
    "weights",
    "hsl_color",
    "trim_name",
]

def weights(students: list[dict]) -> list[float]:
    inv = [1.0 / (s["score"] + 0.01) for s in students]
    total_inv = sum(inv)
    # Ensure a minimal positive probability for numerical stability
    probs = [max(v / total_inv, 0.01 / 360.0) for v in inv]
    norm = sum(probs)
    return [p / norm for p in probs]

def hsl_color(idx: int, n: int) -> tuple[float, float, float]:
    """Evenly spread HSL colours mapped to RGB tuples (0‑1 floats)."""
    return colorsys.hls_to_rgb((idx / n) % 1.0, 0.60, 0.70)

def trim_name(name: str, prob: float) -> str:
    """Hide labels on tiny wedges and truncate overly long names."""
    if prob < 0.02:  # hide very small slices
        return ""
    if len(name) <= cfg.MAX_NAME_LEN:
        return name
    return name[: cfg.MAX_NAME_LEN] + "…"
