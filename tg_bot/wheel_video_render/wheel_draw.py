#!/usr/bin/env python3
"""Drawing functions for Lucky Wheel – rotating layer + static overlay."""

from __future__ import annotations
import io, math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import wheel_config as cfg
from wheel_helpers import fetch_students, weights, hsl_color, trim_name

# ────────────────────────────────────────────────────────────────────────────
# Internal helper: create figure/axes without margins so that (0,0) is exact
# centre for both rotating and static layers → perfect alignment.
# ────────────────────────────────────────────────────────────────────────────

def _fig_ax():
    fig, ax = plt.subplots(
        figsize=(cfg.CANVAS_PX / 100, cfg.CANVAS_PX / 100),
        subplot_kw={"aspect": "equal"},
    )
    # Remove default padding around the figure to guarantee identical extents
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.patch.set_alpha(0)
    ax.axis("off")
    return fig, ax

# ────────────────────────────────────────────────────────────────────────────
# Rotating coloured layer (sectors + labels)
# ────────────────────────────────────────────────────────────────────────────

def draw_rotating_layer(group: str) -> bytes:
    """Return transparent PNG bytes of coloured wheel that will be rotated."""
    students = fetch_students(group)
    probs    = weights(students)

    for i, s in enumerate(students):
        s["prob"], s["color"] = probs[i], hsl_color(i, len(students))

    sizes  = [s["prob"]  for s in students]
    labels = [trim_name(s["name"], s["prob"]) for s in students]
    colors = [s["color"] for s in students]

    fig, ax = _fig_ax()

    ax.pie(
        sizes,
        radius=cfg.WHEEL_R,
        labels=["" for _ in students],
        startangle=0,
        counterclock=False,
        colors=colors,
        wedgeprops={"edgecolor": "white", "linewidth": 0.8},
    )

    # Render labels along radius LABEL_R, centred on each wedge
    start_deg = 0.0
    for frac, txt in zip(sizes, labels):
        if not txt:
            start_deg += frac * 360.0
            continue
        mid = start_deg + frac * 360.0 / 2.0
        theta = -math.radians(mid)
        ax.text(
            cfg.LABEL_R * math.cos(theta),
            cfg.LABEL_R * math.sin(theta),
            txt,
            ha="center",
            va="center",
            rotation=-mid,
            rotation_mode="anchor",
            fontsize=cfg.FONT_SZ,
        )
        start_deg += frac * 360.0

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, pad_inches=0, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ────────────────────────────────────────────────────────────────────────────
# Static overlay (red pointer UNDER thin grey rim)
# ────────────────────────────────────────────────────────────────────────────

def draw_static_overlay() -> bytes:
    """Return transparent PNG bytes containing rim & pointer (non‑rotating)."""
    fig, ax = _fig_ax()

    rim_outer = cfg.WHEEL_R + cfg.RIM_OUTSET

    # Pointer first (lower z‑order) so that rim overlaps its base → crisp edge
    tip_r  = cfg.WHEEL_R - cfg.POINTER_IN
    base_r = rim_outer
    pointer = mpatches.Polygon(
        [(tip_r, 0.0), (base_r, cfg.POINTER_HALF), (base_r, -cfg.POINTER_HALF)],
        closed=True,
        color="#e74c3c",
        zorder=2,
    )
    ax.add_patch(pointer)

    # Thin grey rim on top
    rim = plt.Circle((0, 0), rim_outer, fc="none", ec=cfg.EDGE_COLOR, lw=2.2, zorder=3)
    ax.add_artist(rim)

    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, pad_inches=0, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
