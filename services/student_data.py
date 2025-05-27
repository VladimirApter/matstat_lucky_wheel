from __future__ import annotations

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
PRACTICE_COLUMNS: list[int] = [9, 11, 13, 15, 17, 20, 22, 24, 26, 29, 31, 33, 35]


def _parse_numeric(val) -> float:
    try:
        s = str(val).strip().replace(",", ".")
        return float(s) if s and s.replace(".", "", 1).isdigit() else 0.0
    except (ValueError, TypeError):
        return 0.0


def fetch_students(group: str) -> List[Dict[str, float]]:
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

        if score == 0:
            score += 0.25   # чтобы сегмент этого студента не занимал все колесо

        students.append({"name": name, "score": round(score, 2)})

    return students


__all__ = ["GROUPS", "EXCLUDED", "fetch_students"]
