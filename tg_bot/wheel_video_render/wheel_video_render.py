from __future__ import annotations
import io, os, math, pathlib, random
import numpy as np
import time
from PIL import Image
from moviepy.video.VideoClip import VideoClip

from wheel_segment import segment_mid, random_angle_in_segment
from wheel_motion   import angular_motion
from wheel_draw     import draw_rotating_layer, draw_static_overlay
from wheel_helpers  import fetch_students
import wheel_config as cfg

# ------------------------------------------------------------------------
# RENDER CONSTANTS
PRE_HOLD_SEC  = 0.5
POST_HOLD_SEC = 2.0
FPS           = 60
SIZE_PX       = 640
GROUP_DEMO    = "ft-204-1"
# ---------------------------------------------------------------------------

def _extra_cw(desired_cw: float, base_final_cw: float) -> float:
    return (360.0 - desired_cw - base_final_cw) % 360.0


def render_segment_video(
    group: str,
    idx: int,
    *,
    mode: str = "random",
    seed: int | None = None,
    out_file: str | None = None,
) -> str:
    # Robust RNG: cryptographically secure when seed is None, reproducible otherwise
    if seed is None:
        rng = random.SystemRandom()
    else:
        rng = random.Random(seed)

    # Pick landing angle inside the target wedge
    if mode == "center":
        desired_cw = segment_mid(group, idx)
    else:
        desired_cw = random_angle_in_segment(group, idx, rng=rng)

    # Graphics layers
    rot_img = Image.open(io.BytesIO(draw_rotating_layer(group))).convert("RGBA")
    ovl_img = Image.open(io.BytesIO(draw_static_overlay())).convert("RGBA")

    W, H = rot_img.size

    angle_at, spin_dur = angular_motion()
    base_final_cw = math.degrees(angle_at(spin_dur))
    extra_cw = _extra_cw(desired_cw, base_final_cw)
    total_dur = PRE_HOLD_SEC + spin_dur + POST_HOLD_SEC

    def make_frame(t: float):
        if t < PRE_HOLD_SEC:
            # Show wheel already rotated by extra_cw during the initial hold
            theta_cw = extra_cw
        elif t < PRE_HOLD_SEC + spin_dur:
            theta_cw = math.degrees(angle_at(t - PRE_HOLD_SEC)) + extra_cw
        else:
            theta_cw = base_final_cw + extra_cw

        # Compose frame (Pillow: positive angle = CCW, so clockwise is -theta)
        frame = Image.new("RGBA", (W, H), "white")
        frame = Image.alpha_composite(frame, rot_img.rotate(-theta_cw, resample=Image.BICUBIC))
        frame = Image.alpha_composite(frame, ovl_img)
        return np.array(frame.convert("RGB"))

    clip = (
        VideoClip(make_frame, duration=total_dur)
        .resized(new_size=(SIZE_PX, SIZE_PX))
    )

    # -------------------------------------------------------------------
    # Write out video
    if out_file is None:
        pathlib.Path("videos").mkdir(exist_ok=True)
        out_file = os.path.join("videos", f"{group}_{idx:02d}.mp4")

    clip.write_videofile(
        out_file,
        fps=FPS,
        codec="libx264",
        preset="slow",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "faststart"],
        audio=False,
    )

    return out_file

# ---------------------------------------------------------------------------

def _generate_all(
    group: str = GROUP_DEMO,
    *,
    mode: str = "random",
):
    students = fetch_students(group)
    for idx, student in enumerate(students[:1]):
        safe_name = student["name"].replace(" ", "_")
        outfile = f"videos/{group}_{idx:02d}_{safe_name}.mp4"
        render_segment_video(
            group,
            idx,
            mode=mode,
            seed=(int(time.time())),
            out_file=outfile,
        )
        print(f"✔ {outfile}")


if __name__ == "__main__":
    start = time.time()
    pathlib.Path("videos").mkdir(exist_ok=True)
    _generate_all()
    finish = time.time()
    print(finish - start)
