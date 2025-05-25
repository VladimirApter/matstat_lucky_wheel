from __future__ import annotations

import io
import math
import os
import pathlib
import random
import time
from typing import List

import numpy as np
from PIL import Image
from moviepy.video.VideoClip import VideoClip

from .wheel_segment import segment_mid, random_angle_in_segment
from .wheel_motion import angular_motion
from .wheel_draw import draw_rotating_layer, draw_static_overlay
from .wheel_helpers import fetch_students

# ---------------------------------------------------------------------------
# Render constants (keep identical across functions)
# ---------------------------------------------------------------------------
PRE_HOLD_SEC: float = 0.5
POST_HOLD_SEC: float = 2.0
FPS: int = 60
SIZE_PX: int = 640  # square frame (Telegram video‑note prefers ≤640px)

__all__ = [
    "render_segment_video",
    "generate_group_videos",
]

# ---------------------------------------------------------------------------
# Internal helper – clockwise offset needed so the pointer lands in the wedge
# ---------------------------------------------------------------------------

def _extra_cw(desired_cw: float, base_final_cw: float) -> float:
    return (360.0 - desired_cw - base_final_cw) % 360.0


# ---------------------------------------------------------------------------
# Public – render *one* video where pointer lands on wedge *idx*
# ---------------------------------------------------------------------------

def render_segment_video(
    group: str,
    idx: int,
    *,
    mode: str = "random",  # random point inside wedge | centre
    seed: int | None = None,
    out_file: str | pathlib.Path | None = None,
) -> str:
    """Render a single MP4 for *group*/segment *idx* and return its path."""

    rng: random.Random | random.SystemRandom
    if seed is None:
        rng = random.SystemRandom()
    else:
        rng = random.Random(seed)

    # Pick landing angle inside the target wedge
    desired_cw: float
    if mode == "center":
        desired_cw = segment_mid(group, idx)
    else:
        desired_cw = random_angle_in_segment(group, idx, rng=rng)

    # PNG layers → Pillow images (RGBA)
    rot_img = Image.open(io.BytesIO(draw_rotating_layer(group))).convert("RGBA")
    ovl_img = Image.open(io.BytesIO(draw_static_overlay())).convert("RGBA")

    W, H = rot_img.size

    angle_at, spin_dur = angular_motion()
    base_final_cw = math.degrees(angle_at(spin_dur))
    extra_cw = _extra_cw(desired_cw, base_final_cw)
    total_dur = PRE_HOLD_SEC + spin_dur + POST_HOLD_SEC

    def make_frame(t: float):
        if t < PRE_HOLD_SEC:
            theta_cw = extra_cw
        elif t < PRE_HOLD_SEC + spin_dur:
            theta_cw = math.degrees(angle_at(t - PRE_HOLD_SEC)) + extra_cw
        else:
            theta_cw = base_final_cw + extra_cw

        frame = Image.new("RGBA", (W, H), "white")
        frame = Image.alpha_composite(frame, rot_img.rotate(-theta_cw, resample=Image.BICUBIC))
        frame = Image.alpha_composite(frame, ovl_img)
        return np.array(frame.convert("RGB"))

    clip = VideoClip(make_frame, duration=total_dur).resized(new_size=(SIZE_PX, SIZE_PX))

    # Default output path: videos/<group>/<idx>.mp4
    if out_file is None:
        dest_dir = pathlib.Path("videos") / group
        dest_dir.mkdir(parents=True, exist_ok=True)
        out_file = dest_dir / f"{idx:02d}.mp4"
    else:
        out_file = pathlib.Path(out_file)
        out_file.parent.mkdir(parents=True, exist_ok=True)

    clip.write_videofile(
        str(out_file),
        fps=FPS,
        codec="libx264",
        preset="slow",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "faststart"],
        audio=False,
    )

    return str(out_file)


# ---------------------------------------------------------------------------
# Public – render *all* wedges for a group with zero‑downtime replacement
# ---------------------------------------------------------------------------

def generate_group_videos(group: str, *, mode: str = "random") -> List[str]:
    dest_dir = pathlib.Path("videos") / group
    dest_dir.mkdir(parents=True, exist_ok=True)

    tmp_suffix = "_new"
    students = fetch_students(group)

    print(f"[wheel] rendering {len(students)} videos for {group} → {dest_dir}/")

    rendered_tmp: List[pathlib.Path] = []
    for idx, student in enumerate(students):
        safe_name = student["name"].replace(" ", "_")
        tmp_path = dest_dir / f"{idx:02d}_{safe_name}{tmp_suffix}.mp4"
        render_segment_video(
            group,
            idx,
            mode=mode,
            seed=int(time.time()) + idx,
            out_file=tmp_path,
        )
        rendered_tmp.append(tmp_path)

    # Step 2 – delete outdated videos (those *without* _new suffix)
    for old in dest_dir.glob("*.mp4"):
        if not old.name.endswith(f"{tmp_suffix}.mp4"):
            try:
                old.unlink()
            except OSError:
                pass  # best‑effort

    # Step 3 – rename new files → final names (strip suffix)
    final_paths: List[str] = []
    for tmp in rendered_tmp:
        final_path = tmp.with_name(tmp.stem.replace(tmp_suffix, "") + ".mp4")
        try:
            tmp.rename(final_path)
            final_paths.append(str(final_path))
        except OSError:
            # If rename fails leave tmp file in place (still usable).
            final_paths.append(str(tmp))

    print(f"[wheel] finished {group}: {len(final_paths)} files updated")
    return final_paths


# ---------------------------------------------------------------------------
# CLI helper – demo regeneration when executed directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render Lucky Wheel videos for GROUP.")
    parser.add_argument("group", help="student group id (e.g. ft-204-1)")
    parser.add_argument("--mode", choices=["random", "center"], default="random")
    args = parser.parse_args()

    generate_group_videos(args.group, mode=args.mode)
