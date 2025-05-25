#!/usr/bin/env python3
"""student_data – centralised Google Sheets loader for MatStat Lucky Wheel.

This module is the *only* place in the codebase that knows how to download,
clean and prepare the student lists that power the wheel.  Any component that
needs raw data should import :pyfunc:`fetch_students` instead of duplicating
spreadsheet logic.

Key points
----------
* Skips the first row of every sheet (headers).
* Stops reading the moment it encounters the first blank *name* cell – the
  sheets place a single empty row after the last student.
* Aggregates scores across the columns listed in :pydata:`PRACTICE_COLUMNS`.
* Names present in :pydata:`EXCLUDED` are silently skipped.
* Results are memoised with :pyfunc:`functools.lru_cache` (one cache entry per
  group).
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Dict

import pandas as pd

# ---------------------------------------------------------------------------
# Spreadsheet metadata
# ---------------------------------------------------------------------------

SHEET_ID: str = "1QyIvnpMN1H3v6Ywj6QGl59KsdRbeUrtHXcAlE45sasY"

# Public *gid* of each subgroup worksheet inside the master sheet
GROUPS: dict[str, str] = {
    "ft-201-1": "0",
    "ft-201-2": "313135890",
    "ft-202-1": "429115037",
    "ft-202-2": "1499384932",
    "ft-203-1": "1434241927",
    "ft-203-2": "101485156",
    "ft-204-1": "1801994266",
    "ft-204-2": "2063966210",
    "kn": "393945752",
}

# Students that must be excluded from the wheel regardless of their scores
EXCLUDED: set[str] = {
    "Бутовой Владислав",
    "Гальянов Фёдор",
    "Бархатова Алёна",
    "Пузынин Георгий",
    "Сидорова Алёна",
    "Одайкина Елизавета",
    "Юдин Николай",
    "Артемьев Тимофей",
    "Колесников Захар",
    "Печников Георгий",
    "Сахбиев Марат",
    "Суставов Данил Сергеевич",
}

# Zero‑based column indices that hold practice work scores
PRACTICE_COLUMNS: list[int] = [9, 11, 13, 15, 17, 20, 24, 26, 29, 31, 33, 35]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_numeric(val) -> float:
    """Convert strings like ``'4,5'`` / ``'4.5'`` to *float*.

    Anything that cannot be converted cleanly (including *NaN*) yields ``0.0``.
    """
    try:
        s = str(val).strip().replace(",", ".")
        return float(s) if s and s.replace(".", "", 1).isdigit() else 0.0
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def fetch_students(group: str) -> List[Dict[str, float]]:  # noqa: D401 – short name OK
    """Return a list of ``{"name", "score"}`` dicts for *group*.

    Parameters
    ----------
    group:
        Human‑friendly group identifier (e.g. ``"ft-202-1"``).  Must exist in
        :pydata:`GROUPS`.
    """
    if group not in GROUPS:
        raise KeyError(f"Unknown group '{group}'. Available: {list(GROUPS)}")

    gid = GROUPS[group]
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/"
        f"export?format=csv&gid={gid}"
    )
    df = pd.read_csv(url)

    students: list[dict[str, float]] = []

    # Start at row 1 to skip headers; continue until we hit the first empty name
    for idx in range(len(df)):
        name = str(df.iloc[idx, 0]).strip()
        if name is None or "nan" in name:
            break  # End of the student list
        if name in EXCLUDED:
            continue

        row = df.iloc[idx]
        score = sum(_parse_numeric(row.iloc[col]) for col in PRACTICE_COLUMNS)

        if score > 0:  # Ignore students without a single completed practice
            students.append({"name": name, "score": round(score, 2)})

    return students


__all__ = ["GROUPS", "EXCLUDED", "fetch_students"]
