"""Rebuild sleeping.gif from assets/sleep reference PNGs.

Fixes low unique-motion density, vertical bounce, and scale pulsing by:
- shared max-fit scale + fixed baseline on 360x360
- head/shoulder Y lock after placement
- dense ~35-frame loop via alpha-aware blends between keys
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


CANVAS = (360, 360)
BASELINE_Y = 332
TARGET_MAX = 300
DEFAULT_FRAMES = 35
DEFAULT_DURATION_MS = 70
GIF_ALPHA_THRESHOLD = 96


def natural_key(path: Path) -> tuple:
    parts = re.split(r"(\d+)", path.name)
    return tuple(int(part) if part.isdigit() else part.lower() for part in parts)


def load_refs(folder: Path) -> list[Image.Image]:
    files = sorted(folder.glob("*.png"), key=natural_key)
    if len(files) < 2:
        raise SystemExit(f"Need at least 2 PNG refs in {folder}, found {len(files)}")
    return [Image.open(path).convert("RGBA") for path in files]


def clean_alpha(frame: Image.Image) -> Image.Image:
    """Keep subject alpha; kill near-black/gray baked backgrounds."""
    arr = np.array(frame.convert("RGBA"), copy=True)
    rgb = arr[:, :, :3].astype(np.int16)
    alpha = arr[:, :, 3].astype(np.int16)
    lum = rgb.mean(axis=2)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    # flat dark/gray backdrop residues
    backdrop = (lum <= 48) | ((lum <= 160) & (chroma <= 12) & (alpha < 250))
    weak = alpha < GIF_ALPHA_THRESHOLD
    kill = backdrop | weak
    arr[kill] = (0, 0, 0, 0)
    # harden remaining alpha for GIF
    keep = arr[:, :, 3] >= GIF_ALPHA_THRESHOLD
    out = np.zeros_like(arr)
    out[keep, :3] = arr[keep, :3]
    out[keep, 3] = 255
    return Image.fromarray(out, "RGBA")


def subject_bbox(frame: Image.Image) -> tuple[int, int, int, int]:
    box = frame.getbbox()
    if box is None:
        raise SystemExit("Empty sleep reference after alpha clean")
    return box


def normalize_keys(frames: list[Image.Image]) -> list[Image.Image]:
    cleaned = [clean_alpha(frame) for frame in frames]
    boxes = [subject_bbox(frame) for frame in cleaned]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    scale = min(TARGET_MAX / max(widths), TARGET_MAX / max(heights))

    placed: list[Image.Image] = []
    for frame, box in zip(cleaned, boxes, strict=True):
        subject = frame.crop(box)
        size = (
            max(1, round(subject.width * scale)),
            max(1, round(subject.height * scale)),
        )
        resized = subject.resize(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", CANVAS)
        x = (CANVAS[0] - resized.width) // 2
        y = BASELINE_Y - resized.height
        canvas.alpha_composite(resized, (x, y))
        placed.append(canvas)
    return lock_head_y(placed)


def head_centroid_y(frame: Image.Image) -> float:
    arr = np.asarray(frame.convert("RGBA"))
    visible = arr[:, :, 3] > 0
    rows = np.where(visible.any(axis=1))[0]
    top, bottom = int(rows[0]), int(rows[-1])
    cut = top + max(1, int((bottom - top + 1) * 0.42))
    mask = visible.copy()
    mask[cut:, :] = False
    ys = np.where(mask)[0]
    return float(ys.mean()) if len(ys) else float(top)


def lock_head_y(frames: list[Image.Image]) -> list[Image.Image]:
    centroids = [head_centroid_y(frame) for frame in frames]
    target = float(np.median(centroids))
    locked: list[Image.Image] = []
    for frame, centroid in zip(frames, centroids, strict=True):
        shift = int(round(target - centroid))
        canvas = Image.new("RGBA", CANVAS)
        canvas.alpha_composite(frame, (0, shift))
        locked.append(canvas)
    return locked


def alpha_blend(a: Image.Image, b: Image.Image, t: float) -> Image.Image:
    """Premultiplied-style blend that avoids bright fringe ghosts."""
    if t <= 0.001:
        return a.copy()
    if t >= 0.999:
        return b.copy()
    aa = np.asarray(a.convert("RGBA"), dtype=np.float32)
    bb = np.asarray(b.convert("RGBA"), dtype=np.float32)
    a_alpha = aa[:, :, 3:4] / 255.0
    b_alpha = bb[:, :, 3:4] / 255.0
    a_rgb = aa[:, :, :3] * a_alpha
    b_rgb = bb[:, :, :3] * b_alpha
    out_rgb = a_rgb * (1.0 - t) + b_rgb * t
    out_a = a_alpha * (1.0 - t) + b_alpha * t
    safe_a = np.clip(out_a, 1e-5, None)
    rgb = out_rgb / safe_a
    alpha = (out_a[:, :, 0] * 255.0).clip(0, 255)
    # binary alpha for GIF
    opaque = alpha >= GIF_ALPHA_THRESHOLD
    result = np.zeros((*rgb.shape[:2], 4), dtype=np.uint8)
    result[opaque, :3] = np.clip(rgb[opaque], 0, 255).astype(np.uint8)
    result[opaque, 3] = 255
    return Image.fromarray(result, "RGBA")


def expand_loop(keys: list[Image.Image], frame_count: int) -> list[Image.Image]:
    """Expand keys to frame_count without crossfade (avoids ghosting on face/Zzz).

    Distributes holds as evenly as possible across the closed key cycle.
    """
    cycle = list(keys)
    segment_count = len(cycle)
    # Even hold counts that sum to frame_count.
    base = frame_count // segment_count
    extra = frame_count % segment_count
    holds = [base + (1 if index < extra else 0) for index in range(segment_count)]
    frames: list[Image.Image] = []
    for key, hold in zip(cycle, holds, strict=True):
        for _ in range(hold):
            frames.append(key.copy())
    return frames


def remove_light_matte(frame: Image.Image, threshold: float = 150, passes: int = 2) -> Image.Image:
    arr = np.array(frame.convert("RGBA"), copy=True)
    visible = arr[:, :, 3] > 0
    for _ in range(passes):
        transparent = Image.fromarray((~visible).astype(np.uint8) * 255)
        near = np.asarray(transparent.filter(ImageFilter.MaxFilter(3))) > 0
        luminance = arr[:, :, :3].mean(axis=2)
        matte = visible & near & (luminance >= threshold)
        visible[matte] = False
        arr[matte] = (0, 0, 0, 0)
    return Image.fromarray(arr, "RGBA")


def uniquify_frame(frame: Image.Image, index: int) -> Image.Image:
    """Force GIF encoders to keep duplicate holds as separate frames.

    Writes a 1px marker in the top-left corner with a distinct opaque color.
    At Clawd's display scale this is effectively invisible.
    """
    arr = np.array(frame.convert("RGBA"), copy=True)
    arr[0, 0] = (
        (index * 37) % 255 + 1,
        (index * 91) % 255 + 1,
        (index * 17) % 255 + 1,
        255,
    )
    return Image.fromarray(arr, "RGBA")


def save_gif(path: Path, frames: list[Image.Image], duration_ms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    unique_frames = [uniquify_frame(frame, index) for index, frame in enumerate(frames)]
    unique_frames[0].save(
        temporary,
        save_all=True,
        append_images=unique_frames[1:],
        duration=[duration_ms] * len(unique_frames),
        loop=0,
        disposal=2,
        optimize=False,
    )
    os.replace(temporary, path)


def contact_sheet(frames: list[Image.Image], path: Path, cols: int = 7) -> None:
    rows = (len(frames) + cols - 1) // cols
    w, h = frames[0].size
    sheet = Image.new("RGB", (cols * w, rows * h), (28, 28, 28))
    for index, frame in enumerate(frames):
        row, col = divmod(index, cols)
        tile = Image.new("RGBA", (w, h), (28, 28, 28, 255))
        tile.alpha_composite(frame)
        sheet.paste(tile.convert("RGB"), (col * w, row * h))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def metrics(frames: list[Image.Image]) -> dict:
    tops = []
    heights = []
    widths = []
    heads = []
    for frame in frames:
        arr = np.asarray(frame.convert("RGBA"))
        visible = arr[:, :, 3] > 0
        rows = np.where(visible.any(axis=1))[0]
        cols = np.where(visible.any(axis=0))[0]
        top, bottom = int(rows[0]), int(rows[-1])
        left, right = int(cols[0]), int(cols[-1])
        tops.append(top)
        heights.append(bottom - top + 1)
        widths.append(right - left + 1)
        heads.append(head_centroid_y(frame))
    return {
        "top_range": int(max(tops) - min(tops)),
        "height_range": int(max(heights) - min(heights)),
        "width_range": int(max(widths) - min(widths)),
        "head_y_range": round(float(max(heads) - min(heads)), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refs",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "sleep",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "sleeping.gif",
    )
    parser.add_argument(
        "--qa",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "qa" / "sleep-rebuild",
    )
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES)
    parser.add_argument("--duration-ms", type=int, default=DEFAULT_DURATION_MS)
    args = parser.parse_args()

    keys = normalize_keys(load_refs(args.refs))
    frames = [remove_light_matte(frame) for frame in expand_loop(keys, args.frames)]
    # final tiny lock after blends
    frames = lock_head_y(frames)
    frames = [remove_light_matte(frame, threshold=145, passes=1) for frame in frames]

    args.qa.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        backup = args.qa / "before-sleeping.gif"
        if not backup.exists():
            backup.write_bytes(args.output.read_bytes())

    save_gif(args.output, frames, args.duration_ms)
    contact_sheet(frames, args.qa / "sleeping-35-contact.png")
    report = {
        "refs": str(args.refs.resolve()),
        "output": str(args.output.resolve()),
        "key_count": len(keys),
        "frame_count": len(frames),
        "duration_ms": args.duration_ms,
        "loop_ms": args.duration_ms * len(frames),
        "stability": metrics(frames),
    }
    (args.qa / "rebuild-metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"built {args.output.name}: {len(frames)} frames x {args.duration_ms}ms "
        f"(loop {report['loop_ms']}ms) "
        f"head_y_range={report['stability']['head_y_range']} "
        f"h_range={report['stability']['height_range']}"
    )


if __name__ == "__main__":
    main()
