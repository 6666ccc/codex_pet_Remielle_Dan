"""Stabilize sleeping.gif: kill flickering white hair scars + lock horizontal drift."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image


GIF_ALPHA = 96


def load_gif(path: Path) -> tuple[list[np.ndarray], list[int], int]:
    with Image.open(path) as opened:
        loop = int(opened.info.get("loop", 0))
        frames: list[np.ndarray] = []
        durations: list[int] = []
        for index in range(opened.n_frames):
            opened.seek(index)
            frames.append(np.array(opened.convert("RGBA"), copy=True))
            durations.append(int(opened.info.get("duration", 70)))
    return frames, durations, loop


def opaque_centroid_x(frame: np.ndarray) -> float:
    visible = frame[:, :, 3] > 0
    # ignore 1px uniquify markers on the top row
    visible = visible.copy()
    visible[0, :] = False
    xs = np.where(visible.any(axis=0))[0]
    if len(xs) == 0:
        return frame.shape[1] / 2
    ys, xcoords = np.where(visible)
    return float(xcoords.mean())


def lock_x(frames: list[np.ndarray], target_x: float | None = None) -> tuple[list[np.ndarray], dict]:
    centroids = [opaque_centroid_x(frame) for frame in frames]
    target = float(np.median(centroids) if target_x is None else target_x)
    locked: list[np.ndarray] = []
    shifts: list[int] = []
    height, width = frames[0].shape[:2]
    for frame, centroid in zip(frames, centroids, strict=True):
        shift = int(round(target - centroid))
        shifts.append(shift)
        canvas = np.zeros_like(frame)
        if shift == 0:
            canvas[:] = frame
        elif shift > 0:
            canvas[:, shift:] = frame[:, : width - shift]
        else:
            canvas[:, : width + shift] = frame[:, -shift:]
        locked.append(canvas)
    after = [opaque_centroid_x(frame) for frame in locked]
    return locked, {
        "before_cx_range": round(float(max(centroids) - min(centroids)), 2),
        "after_cx_range": round(float(max(after) - min(after)), 2),
        "target_cx": round(target, 2),
        "shifts": shifts,
    }


def hair_region_mask(frame: np.ndarray) -> np.ndarray:
    """Upper body band where pink hair lives; excludes pure white outfit/wings below."""
    visible = frame[:, :, 3] > 0
    visible = visible.copy()
    visible[0, :] = False
    rows = np.where(visible.any(axis=1))[0]
    if len(rows) == 0:
        return np.zeros(visible.shape, dtype=bool)
    top, bottom = int(rows[0]), int(rows[-1])
    cut = top + max(1, int((bottom - top + 1) * 0.55))
    band = visible.copy()
    band[cut:, :] = False
    rgb = frame[:, :, :3].astype(np.int16)
    # pink / magenta hair family (not white dress)
    pinkish = (
        (rgb[:, :, 0] >= 140)
        & (rgb[:, :, 0] >= rgb[:, :, 1] + 15)
        & (rgb[:, :, 0] >= rgb[:, :, 2] - 10)
    )
    # also include dark pink shade pixels near pink
    dark_pink = (
        (rgb[:, :, 0] >= 100)
        & (rgb[:, :, 0] >= rgb[:, :, 1] + 10)
        & (rgb[:, :, 0] >= rgb[:, :, 2] - 5)
        & (rgb.mean(axis=2) < 200)
    )
    return band & (pinkish | dark_pink)


def fix_white_hair_scars(frames: list[np.ndarray]) -> tuple[list[np.ndarray], dict]:
    stack = np.stack(frames, axis=0)  # F,H,W,4
    # union hair mask across frames, then dilate slightly via neighbor max
    hair_union = np.zeros(frames[0].shape[:2], dtype=bool)
    for frame in frames:
        hair_union |= hair_region_mask(frame)

    # expand hair union by 1px
    from PIL import ImageFilter

    hair_img = Image.fromarray(hair_union.astype(np.uint8) * 255)
    hair_union = np.asarray(hair_img.filter(ImageFilter.MaxFilter(3))) > 0

    # temporal median RGB where hair
    rgb_stack = stack[:, :, :, :3].astype(np.float32)
    median_rgb = np.median(rgb_stack, axis=0)
    median_lum = median_rgb.mean(axis=2)
    max_lum = rgb_stack.max(axis=3)

    lum_stack = rgb_stack.mean(axis=3)
    std_lum = lum_stack.std(axis=0)
    max_frame_lum = lum_stack.max(axis=0)
    min_frame_lum = lum_stack.min(axis=0)
    flicker_zone = (
        hair_union
        & (std_lum >= 12)
        & (max_frame_lum >= 195)
        & ((max_frame_lum - min_frame_lum) >= 25)
    )

    repaired = 0
    out_frames: list[np.ndarray] = []
    for index, frame in enumerate(frames):
        arr = frame.copy()
        lum = arr[:, :, :3].astype(np.float32).mean(axis=2)
        # Force temporally unstable bright hair zones to the median color.
        if flicker_zone.any():
            repaired += int(flicker_zone.sum())
            arr[flicker_zone, :3] = np.clip(median_rgb[flicker_zone], 0, 255).astype(
                np.uint8
            )
            arr[flicker_zone, 3] = 255
        # scar: in hair, much brighter than temporal median, and near-white
        scar = (
            hair_union
            & (arr[:, :, 3] > 0)
            & (lum >= median_lum + 28)
            & (lum >= 200)
            & (arr[:, :, :3].min(axis=2) >= 170)
        )
        # also kill bright outliers even if not pure white
        outlier = (
            hair_union
            & (arr[:, :, 3] > 0)
            & (lum >= median_lum + 40)
            & (max_lum[index] >= median_lum + 45)
        )
        fix = scar | outlier
        repaired += int(fix.sum())
        if fix.any():
            arr[fix, :3] = np.clip(median_rgb[fix], 0, 255).astype(np.uint8)
            arr[fix, 3] = 255
        # final clamp: no near-white inside pink hair median zone
        still_white = (
            hair_union
            & (arr[:, :, 3] > 0)
            & (arr[:, :, :3].mean(axis=2) >= 205)
            & (median_lum < 195)
        )
        repaired += int(still_white.sum())
        if still_white.any():
            arr[still_white, :3] = np.clip(median_rgb[still_white], 0, 255).astype(
                np.uint8
            )
        out_frames.append(arr)

    return out_frames, {
        "hair_pixels": int(hair_union.sum()),
        "flicker_zone_pixels": int(flicker_zone.sum()),
        "repaired_pixels": repaired,
    }


def uniquify(frame: np.ndarray, index: int) -> np.ndarray:
    arr = frame.copy()
    arr[0, 0] = (
        (index * 37) % 255 + 1,
        (index * 91) % 255 + 1,
        (index * 17) % 255 + 1,
        255,
    )
    return arr


def save_gif(path: Path, frames: list[np.ndarray], durations: list[int], loop: int) -> None:
    images = [Image.fromarray(uniquify(frame, index), "RGBA") for index, frame in enumerate(frames)]
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    images[0].save(
        temporary,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=loop,
        disposal=2,
        optimize=False,
    )
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()

    frames, durations, loop = load_gif(args.input)
    frames, x_report = lock_x(frames)
    frames, hair_report = fix_white_hair_scars(frames)
    # re-lock x after edits (should be noop-ish)
    frames, x_report2 = lock_x(frames)

    args.qa.mkdir(parents=True, exist_ok=True)
    sidecar = args.output.with_name("sleeping.stabilized.gif")
    save_gif(sidecar, frames, durations, loop)
    data = sidecar.read_bytes()
    try:
        if args.output.exists():
            args.output.unlink()
        sidecar.replace(args.output)
    except OSError:
        args.output.write_bytes(data)

    # verify
    cxs = [opaque_centroid_x(frame) for frame in frames]
    report = {
        "input": str(args.input.resolve()),
        "output": str(args.output.resolve()),
        "frames": len(frames),
        "x_lock": x_report,
        "x_lock_final": x_report2,
        "hair_scar_fix": hair_report,
        "final_cx_range": round(float(max(cxs) - min(cxs)), 2),
    }
    (args.qa / "stabilize-metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"stabilized sleeping: cx {x_report['before_cx_range']}px -> "
        f"{report['final_cx_range']}px; repaired {hair_report['repaired_pixels']} hair pixels"
    )


if __name__ == "__main__":
    main()
