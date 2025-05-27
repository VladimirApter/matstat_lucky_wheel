from __future__ import annotations

from collections import defaultdict
import os
import pathlib
import random
import threading
import time
from typing import Dict, Set

import telebot
from telebot import types

from services.student_data import GROUPS  # mapping: group → gid
from services.table_change_tracker import has_table_changed
from wheel_video_render.wheel_video_render import generate_group_videos
from wheel_video_render.wheel_helpers import fetch_students

# ---------------------------------------------------------------------------
# Configuration & globals
# ---------------------------------------------------------------------------
BOT_TOKEN: str = os.getenv("MATSTAT_LUCKY_WHEEL_BOT_TOKEN", "".join(
    ["777", "551", "5350:A", "AGL_P", "3-NY2ZC", "UmrEVnv6I", "x-LVZ7hVVo7uc"]
))
CHECK_INTERVAL_HOURS: int = 5
CHECK_INTERVAL_SEC: int = CHECK_INTERVAL_HOURS * 3600

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Track groups under generation → avoid duplicate jobs
_rendering: Set[str] = set()
_rendering_lock = threading.Lock()

# Cache students list per group (dict index → name) for fast lookup after spin
_students_cache: Dict[str, Dict[int, str]] = defaultdict(dict)


# ---------------------------------------------------------------------------
# Background watchdog – spreadsheet change detection / regeneration
# ---------------------------------------------------------------------------

def _regenerate_and_release(group: str):
    try:
        generate_group_videos(group)
    finally:
        with _rendering_lock:
            _rendering.discard(group)


def _watchdog_loop():
    while True:
        for group in GROUPS:
            try:
                if has_table_changed(group):
                    with _rendering_lock:
                        if group in _rendering:
                            continue
                        _rendering.add(group)
                    threading.Thread(
                        target=_regenerate_and_release, args=(group,), daemon=True
                    ).start()
            except Exception as exc:
                print(f"[watchdog] error for {group}: {exc}")
        time.sleep(CHECK_INTERVAL_SEC)


threading.Thread(target=_watchdog_loop, daemon=True).start()

# ---------------------------------------------------------------------------
# Helpers – video retrieval / student name extraction
# ---------------------------------------------------------------------------

def _ensure_videos_ready(group: str):
    """Generate missing videos synchronously if none exist yet."""
    dir_path = pathlib.Path("videos") / group
    if not dir_path.exists() or not any(dir_path.glob("*.mp4")):
        generate_group_videos(group)


def _pick_random_video(group: str) -> pathlib.Path:
    dir_path = pathlib.Path("videos") / group
    videos = [p for p in dir_path.glob("*.mp4") if not p.stem.endswith("_new")]
    if not videos:
        raise FileNotFoundError("No video found")

    weights: list[float] = []
    for p in videos:
        try:
            prob_str = p.stem.split("_")[-1]
            weights.append(float(prob_str))
        except ValueError:
            weights.append(0.0)

    if all(w <= 0 for w in weights):
        return random.choice(videos)

    return random.choices(videos, weights=weights, k=1)[0]



def _student_name_from_filename(group: str, path: pathlib.Path) -> str:
    cache = _students_cache[group]
    try:
        idx = int(path.stem.split("_")[0])
    except (ValueError, IndexError):
        return "неизвестный студент"
    if idx not in cache:
        cache.update({i: s["name"] for i, s in enumerate(fetch_students(group))})
    return cache.get(idx, "неизвестный студент")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

@bot.message_handler(commands=["start", "help"])
def _cmd_start(msg):
    bot.reply_to(
        msg,
        "Привет! Нажми /spin, чтобы крутануть колесо"
    )


@bot.message_handler(commands=["spin"])
def _cmd_spin(msg):
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text=g, callback_data=f"spin:{g}")
        for g in GROUPS.keys()
    ]
    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i+2])
    bot.send_message(msg.chat.id, "Какую группу крутить?", reply_markup=kb)



@bot.callback_query_handler(func=lambda c: c.data.startswith("spin:"))
def _cb_spin_group(call):
    group = call.data.split(":", 1)[1]
    # Delete the prompt with buttons for cleanliness
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    # Ensure we have up‑to‑date videos → may block shortly on first use
    _ensure_videos_ready(group)

    # Pick video & extract student name before sending
    try:
        video_path = _pick_random_video(group)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "Че‑то я лагаю, попробуй крутануть позже, мб оживу")
        return
    student_name = _student_name_from_filename(group, video_path)

    # Notify about upload – Telegram shows a circle in title bar / chat list
    bot.send_chat_action(call.message.chat.id, "upload_video_note")

    # Send video note (circle)
    with open(video_path, "rb") as vf:
        bot.send_video_note(call.message.chat.id, vf, length=360)

    # Pause so the user actually sees the wheel before revealing the name
    time.sleep(15)

    bot.send_message(call.message.chat.id, f"<b>→ {student_name}</b>")


print("[bot] up & running – polling …")

bot.infinity_polling()
