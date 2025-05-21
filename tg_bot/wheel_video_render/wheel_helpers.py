#!/usr/bin/env python3
"""Data‑handling and probability helpers for Lucky Wheel."""

from __future__ import annotations
import colorsys
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Group → GID mappings (from Google Sheets)
# ---------------------------------------------------------------------------
GROUPS = {
    "ft-201-1": "0",           "ft-201-2": "313135890",
    "ft-202-1": "429115037",  "ft-202-2": "1499384932",
    "ft-203-1": "1434241927", "ft-203-2": "101485156",
    "ft-204-1": "1801994266", "ft-204-2": "2063966210",
    "kn":       "393945752",
}
GROUPS_COUNT = {
    "0": 14, "313135890": 14, "429115037": 15, "1499384932": 15,
    "1434241927": 13, "101485156": 13, "1801994266": 13, "2063966210": 14,
    "393945752": 4,
}
# Students excluded from the wheel entirely
EXCLUDED: set[str] = {
    "Бутовой Владислав", "Гальянов Фёдор", "Бархатова Алёна",
    "Пузынин Георгий",   "Сидорова Алёна", "Одайкина Елизавета",
    "Юдин Николай",      "Артемьев Тимофей", "Колесников Захар",
    "Печников Георгий",  "Сахбиев Марат",  "Суставов Данил Сергеевич",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_students(group: str) -> list[dict]:
    """Return a list of {'name': str, 'score': float} for the given group."""
    gid = GROUPS[group]
    url = (
        "https://docs.google.com/spreadsheets/d/"
        "1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY/"
        f"export?format=csv&gid={gid}"
    )
    df = pd.read_csv(url)
    cols = [9, 11, 13, 15, 17, 20, 24, 26, 29, 31, 33, 35]

    students: list[dict] = []
    for i in range(GROUPS_COUNT[gid]):
        name = str(df.iloc[i, 0]).strip()
        if not name or name in EXCLUDED:
            continue
        score = sum(
            float(str(df.iloc[i, c]).replace(",", "."))
            if str(df.iloc[i, c]).replace(",", ".").replace(".", "", 1).isdigit()
            else 0
            for c in cols
        )
        if score > 0:
            students.append({"name": name, "score": score})
    return students


def weights(students: list[dict]) -> list[float]:
    """Inverse‑score weights, normalised to 1."""
    inv = [1 / (s["score"] + 0.01) for s in students]
    probs = [max(v / sum(inv), 0.01 / 360) for v in inv]
    s = sum(probs)
    return [v / s for v in probs]


def hsl_color(i: int, n: int) -> tuple[float, float, float]:
    """Evenly‑spaced HSL → RGB triplet."""
    return colorsys.hls_to_rgb((i / n) % 1.0, 0.60, 0.70)


def trim_name(name: str, prob: float) -> str:
    if prob < 0.02:
        return ""
    return name if len(name) <= 24 else name[:24] + "…"
