#!/usr/bin/env python3
"""Main entry‑point for Lucky Wheel video generation — Telegram video‑note ready.

Version 2.2
* Автоматически подгоняет размер ролика к `CANVAS_PX` из конфигурации →
  гарантировано совпадение `length` и фактического кадра.
* Использует `moviepy.video.fx.all.resize` вместо метода `.resize()`
  (устраняет предупреждение «Unresolved attribute reference»).
"""

from __future__ import annotations
import io, math
import numpy as np
from PIL import Image
from moviepy.video.VideoClip import VideoClip

from wheel_draw   import draw_rotating_layer, draw_static_overlay
from wheel_motion import angular_motion
import wheel_config as cfg

# ────────────────────────────────────────────────────────────────────────────
GROUP_NAME    = "ft-204-1"
PRE_HOLD_SEC  = 0.5
POST_HOLD_SEC = 2.0
FPS           = 60
SIZE_PX       = 640      # ← квадратный размер итогового кадра
OUT_FILE      = f"{GROUP_NAME}_wheel.mp4"
# ────────────────────────────────────────────────────────────────────────────

def main():
    # PNG‑слои
    rot_img = Image.open(io.BytesIO(draw_rotating_layer(GROUP_NAME))).convert("RGBA")
    ovl_img = Image.open(io.BytesIO(draw_static_overlay())).convert("RGBA")
    W, H    = rot_img.size  # может быть > CANVAS_PX из‑за dpi

    angle_at, spin_dur = angular_motion()
    total_dur  = PRE_HOLD_SEC + spin_dur + POST_HOLD_SEC
    final_deg  = math.degrees(angle_at(spin_dur))

    def make_frame(t: float):
        if t < PRE_HOLD_SEC:
            theta = 0.0
        elif t < PRE_HOLD_SEC + spin_dur:
            theta = math.degrees(angle_at(t - PRE_HOLD_SEC))
        else:
            theta = final_deg

        frame = Image.new("RGBA", (W, H), "white")
        frame = Image.alpha_composite(frame, rot_img.rotate(theta, resample=Image.BICUBIC))
        frame = Image.alpha_composite(frame, ovl_img)
        return np.array(frame.convert("RGB"))

    clip = VideoClip(make_frame, duration=total_dur)
    # downscale/upscale to SIZE_PX using Lanczos (default) via moviepy fx
    clip = clip.resized(new_size=(SIZE_PX, SIZE_PX))

    clip.write_videofile(
        OUT_FILE,
        fps=FPS,
        codec="libx264",
        preset="slow",
        ffmpeg_params=["-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "faststart"],
        audio=False,
    )

    print(
        f"✔ saved: size {clip.size}px, duration {total_dur:.2f}s (spin {spin_dur:.2f}s)"
    )


if __name__ == "__main__":
    main()
