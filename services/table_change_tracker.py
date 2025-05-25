from __future__ import annotations

from pathlib import Path
import json
import hashlib
import datetime as _dt
import urllib.request
from typing import Dict, Any

try:
    # When the project is installed as a package
    from .student_data import GROUPS, SHEET_ID  # type: ignore
except ImportError:  # pragma: no cover – fallback for standalone runs
    from .student_data import GROUPS, SHEET_ID  # type: ignore

__all__ = ["has_table_changed"]

# ---------------------------------------------------------------------------
# persistent state file
# ---------------------------------------------------------------------------

_STATE_FILE: Path = Path(__file__).with_name(Path(__file__).stem + "_state.json")

# Ensure the file *exists* so other tools/scripts do not stumble over a missing
# path.  An empty file will simply be treated as "no state yet" by _load_state.
try:
    _STATE_FILE.touch(exist_ok=True)
except OSError:
    # Directory unwritable – we will operate in memory only (harmless but state
    # will not survive restarts).
    pass


# ---------------------------------------------------------------------------
# helpers – state I/O
# ---------------------------------------------------------------------------

def _load_state() -> Dict[str, Any]:
    """Return the stored state or an empty dict if the file is empty/corrupt."""
    try:
        raw = _STATE_FILE.read_text(encoding="utf-8")
    except OSError:
        return {}

    if not raw.strip():  # brand‑new empty file
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _save_state(state: Dict[str, Any]) -> None:
    """Atomically write *state* back to disk (best‑effort)."""
    try:
        _STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        # Non‑fatal – we will recompute next run; just log if needed.
        pass


# ---------------------------------------------------------------------------
# helpers – sheet downloading & hashing
# ---------------------------------------------------------------------------

def _csv_url(group: str) -> str:
    gid = GROUPS[group]
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    )


def _sheet_hash(group: str) -> str:
    """Return the MD5 digest of the current CSV export for *group*."""
    with urllib.request.urlopen(_csv_url(group), timeout=15) as resp:
        content = resp.read()
    return hashlib.md5(content).hexdigest()


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def has_table_changed(group: str) -> bool:  # noqa: D401
    """Return **True** iff the spreadsheet for *group* changed since last check."""
    if group not in GROUPS:
        raise KeyError(f"Unknown group '{group}'. Available: {list(GROUPS)}")

    state = _load_state()
    current_hash = _sheet_hash(group)

    record = state.get(group)
    changed = record is None or record.get("hash") != current_hash

    if changed:
        state[group] = {
            "hash": current_hash,
            "timestamp": _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        }
        _save_state(state)
    return changed
