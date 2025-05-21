#!/usr/bin/env python3
"""Main entry‑point for Lucky Wheel video generation.

Version 2.1 (2025‑05‑22)
───────────────────────
* **Белый фон** — совпадает с веб‑версией.
* **Качество** — CRF 16 / preset slow, 40 fps → минимальные артефакты.
* **Длины пауз**:
  * 0.5 с статичное колесо в начале;
  * вращение по расчётной траектории;
  * 2 с статичное колесо в конце.
"""

from __future__ import annotations
import io, math
import numpy as np
from PIL import Image
from moviepy.video.VideoClip import VideoClip

from wheel_draw   import draw_rotating_layer, draw_static_overlay
from wheel_motion import angular_motion

# ────────────────────────────────────────────────────────────────────────────
GROUP_NAME      = "ft-204-1"   # какую группу рендерим
PRE_HOLD_SEC    = 0.5          # пауза до старта вращения
POST_HOLD_SEC   = 2.0          # пауза после остановки
FPS             = 40           # кадров в секунду
OUT_FILE        = f"{GROUP_NAME}_wheel_anim.mp4"
# ────────────────────────────────────────────────────────────────────────────

def main():
    # PNG‑слои
    rot_png = draw_rotating_layer(GROUP_NAME)
    ovl_png = draw_static_overlay()

    rot_img = Image.open(io.BytesIO(rot_png)).convert("RGBA")
    ovl_img = Image.open(io.BytesIO(ovl_png)).convert("RGBA")
    W, H    = rot_img.size

    angle_at, spin_dur = angular_motion()           # функция и длительность вращения
    total_dur = PRE_HOLD_SEC + spin_dur + POST_HOLD_SEC
    final_angle = math.degrees(angle_at(spin_dur))   # угол при полной остановке

    def make_frame(t: float):
        # три фазы: до вращения, вращение, после вращения
        if t < PRE_HOLD_SEC:
            theta = 0.0
        elif t < PRE_HOLD_SEC + spin_dur:
            theta = math.degrees(angle_at(t - PRE_HOLD_SEC))
        else:
            theta = final_angle

        # белый фон → без чёрных промежутков
        frame = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        frame = Image.alpha_composite(frame, rot_img.rotate(theta, resample=Image.BICUBIC))
        frame = Image.alpha_composite(frame, ovl_img)
        return np.array(frame.convert("RGB"))

    clip = VideoClip(make_frame, duration=total_dur)
    clip.write_videofile(
        OUT_FILE,
        fps=FPS,
        codec="libx264",
        preset="slow",
        ffmpeg_params=["-crf", "16", "-pix_fmt", "yuv420p"],
        audio=False,
    )

    print(
        f"✔ saved: {OUT_FILE}  (pre {PRE_HOLD_SEC}s  spin {spin_dur:.2f}s  post {POST_HOLD_SEC}s  = {total_dur:.2f}s)"
    )


main()
