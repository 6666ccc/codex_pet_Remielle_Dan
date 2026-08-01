"""Build sleeping.gif from a chroma-keyed sleep sprite sheet toward attention fluency."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


CANVAS = (360, 360)
BASELINE_Y = 332
TARGET_MAX = 300
GIF_ALPHA = 96


def extract_grid(sheet: Image.Image, cols: int, rows: int) -> list[Image.Image]:
    cells: list[Image.Image] = []
    for row in range(rows):
        for col in range(cols):
            left = round(col * sheet.width / cols)
            top = round(row * sheet.height / rows)
            right = round((col + 1) * sheet.width / cols)
            bottom = round((row + 1) * sheet.height / rows)
            cells.append(sheet.crop((left, top, right, bottom)).convert("RGBA"))
    return cells


def harden_alpha(frame: Image.Image) -> Image.Image:
    arr = np.array(frame.convert("RGBA"), copy=True)
    keep = arr[:, :, 3] >= GIF_ALPHA
    # kill residual green spill
    rgb = arr[:, :, :3].astype(np.int16)
    green_spill = (rgb[:, :, 1] >= rgb[:, :, 0] + 20) & (rgb[:, :, 1] >= rgb[:, :, 2] + 8)
    keep = keep & (~green_spill)
    out = np.zeros_like(arr)
    out[keep, :3] = arr[keep, :3]
    out[keep, 3] = 255
    return Image.fromarray(out, "RGBA")


def body_bbox(frame: Image.Image) -> tuple[int, int, int, int]:
    """Ignore sparse sleep-Z marks above the main body mass."""
    arr = np.asarray(frame.convert("RGBA"))
    visible = arr[:, :, 3] > 0
    rows = np.where(visible.any(axis=1))[0]
    cols = np.where(visible.any(axis=0))[0]
    if len(rows) == 0:
        raise SystemExit("empty cell")
    # row occupancy; keep dense body band
    occ = visible.sum(axis=1)
    threshold = max(8, int(occ.max() * 0.12))
    dense = np.where(occ >= threshold)[0]
    if len(dense) == 0:
        dense = rows
    top, bottom = int(dense[0]), int(dense[-1])
    band = visible[top : bottom + 1, :]
    band_cols = np.where(band.any(axis=0))[0]
    left, right = int(band_cols[0]), int(band_cols[-1])
    return left, top, right + 1, bottom + 1


def normalize(cells: list[Image.Image]) -> list[Image.Image]:
    cleaned = [harden_alpha(cell) for cell in cells]
    boxes = [body_bbox(cell) for cell in cleaned]
    widths = [b[2] - b[0] for b in boxes]
    heights = [b[3] - b[1] for b in boxes]
    scale = min(TARGET_MAX / max(widths), TARGET_MAX / max(heights))
    placed: list[Image.Image] = []
    for cell, box in zip(cleaned, boxes, strict=True):
        subject = cell.crop(box)
        size = (max(1, round(subject.width * scale)), max(1, round(subject.height * scale)))
        resized = subject.resize(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", CANVAS)
        x = (CANVAS[0] - resized.width) // 2
        y = BASELINE_Y - resized.height
        canvas.alpha_composite(resized, (x, y))
        placed.append(canvas)
    return lock_head(placed)


def head_y(frame: Image.Image) -> float:
    arr = np.asarray(frame.convert("RGBA"))
    visible = arr[:, :, 3] > 0
    rows = np.where(visible.any(axis=1))[0]
    top, bottom = int(rows[0]), int(rows[-1])
    cut = top + max(1, int((bottom - top + 1) * 0.42))
    mask = visible.copy()
    mask[cut:, :] = False
    ys = np.where(mask)[0]
    return float(ys.mean()) if len(ys) else float(top)


def lock_head(frames: list[Image.Image]) -> list[Image.Image]:
    centers = [head_y(frame) for frame in frames]
    target = float(np.median(centers))
    out: list[Image.Image] = []
    for frame, center in zip(frames, centers, strict=True):
        shift = int(round(target - center))
        canvas = Image.new("RGBA", CANVAS)
        canvas.alpha_composite(frame, (0, shift))
        out.append(canvas)
    return out


def harvest_palette(path: Path, colors: int = 56) -> Image.Image:
    samples: list[Image.Image] = []
    with Image.open(path) as opened:
        step = max(1, opened.n_frames // 8)
        for index in range(0, opened.n_frames, step):
            opened.seek(index)
            rgba = opened.convert("RGBA")
            bg = Image.new("RGB", rgba.size, (128, 128, 128))
            bg.paste(rgba, mask=rgba.split()[-1])
            samples.append(bg)
    sheet = Image.new("RGB", (samples[0].width, samples[0].height * len(samples)))
    for index, sample in enumerate(samples):
        sheet.paste(sample, (0, index * samples[0].height))
    return sheet.quantize(colors=colors, method=Image.Quantize.MEDIANCUT).convert("P")


def clean_like_attention(frame: Image.Image, palette: Image.Image) -> Image.Image:
    arr = np.array(frame.convert("RGBA"), copy=True)
    # matte
    visible = arr[:, :, 3] > 0
    for _ in range(2):
        transparent = Image.fromarray((~visible).astype(np.uint8) * 255)
        near = np.asarray(transparent.filter(ImageFilter.MaxFilter(3))) > 0
        lum = arr[:, :, :3].mean(axis=2)
        matte = visible & near & (lum >= 140)
        visible[matte] = False
        arr[matte] = (0, 0, 0, 0)
    # denoise interior
    rgb = Image.fromarray(arr[:, :, :3], "RGB").filter(ImageFilter.MedianFilter(3))
    filtered = np.asarray(rgb)
    opaque = arr[:, :, 3] >= GIF_ALPHA
    transparent = Image.fromarray((arr[:, :, 3] < GIF_ALPHA).astype(np.uint8) * 255)
    near_edge = np.asarray(transparent.filter(ImageFilter.MaxFilter(3))) > 0
    replace = opaque & (~near_edge)
    arr[replace, :3] = filtered[replace]
    # palette remap
    mapped = (
        Image.fromarray(arr[:, :, :3], "RGB")
        .quantize(palette=palette, dither=Image.Dither.NONE)
        .convert("RGB")
    )
    mapped_arr = np.asarray(mapped)
    out = np.zeros_like(arr)
    keep = arr[:, :, 3] >= GIF_ALPHA
    out[keep, :3] = mapped_arr[keep]
    out[keep, 3] = 255
    # outline toward attention navy
    dark = keep & (out[:, :, :3].max(axis=2) < 55)
    out[dark, :3] = (37, 40, 85)
    return Image.fromarray(out, "RGBA")


def save_gif(path: Path, frames: list[Image.Image], duration_ms: int) -> None:
    # uniquify with corner marker so holds (if any) survive
    unique = []
    for index, frame in enumerate(frames):
        arr = np.array(frame.convert("RGBA"), copy=True)
        arr[0, 0] = ((index * 37) % 255 + 1, (index * 91) % 255 + 1, (index * 17) % 255 + 1, 255)
        unique.append(Image.fromarray(arr, "RGBA"))
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    unique[0].save(
        temporary,
        save_all=True,
        append_images=unique[1:],
        duration=[duration_ms] * len(unique),
        loop=0,
        disposal=2,
        optimize=False,
    )
    os.replace(temporary, path)


def metrics(frames: list[Image.Image]) -> dict:
    tops, heights, heads = [], [], []
    for frame in frames:
        arr = np.asarray(frame.convert("RGBA"))
        visible = arr[:, :, 3] > 0
        rows = np.where(visible.any(axis=1))[0]
        top, bottom = int(rows[0]), int(rows[-1])
        tops.append(top)
        heights.append(bottom - top + 1)
        heads.append(head_y(frame))
    return {
        "top_range": int(max(tops) - min(tops)),
        "height_range": int(max(heights) - min(heights)),
        "head_y_range": round(float(max(heads) - min(heads)), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, required=True)
    parser.add_argument("--attention", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--cols", type=int, default=4)
    parser.add_argument("--rows", type=int, default=6)
    parser.add_argument("--duration-ms", type=int, default=70)
    args = parser.parse_args()

    with Image.open(args.sheet) as opened:
        sheet = opened.convert("RGBA")
    cells = extract_grid(sheet, args.cols, args.rows)
    frames = normalize(cells)
    palette = harvest_palette(args.attention, colors=56)
    frames = [clean_like_attention(frame, palette) for frame in frames]
    frames = lock_head(frames)

    args.qa.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        backup = args.qa / "before-sheet-rebuild-sleeping.gif"
        if not backup.exists():
            backup.write_bytes(args.output.read_bytes())

    # write via sidecar then replace to avoid locks
    sidecar = args.output.with_name("sleeping.sheetbuild.gif")
    save_gif(sidecar, frames, args.duration_ms)
    data = sidecar.read_bytes()
    try:
        if args.output.exists():
            args.output.unlink()
        sidecar.replace(args.output)
    except OSError:
        args.output.write_bytes(data)

    report = {
        "sheet": str(args.sheet.resolve()),
        "grid": [args.cols, args.rows],
        "frames": len(frames),
        "duration_ms": args.duration_ms,
        "loop_ms": args.duration_ms * len(frames),
        "stability": metrics(frames),
        "target": "attention-like unique poses + flat palette",
    }
    (args.qa / "sheet-rebuild-metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # contact
    cols = 6
    rows = (len(frames) + cols - 1) // cols
    w, h = frames[0].size
    contact = Image.new("RGB", (cols * w, rows * h), (28, 28, 28))
    for index, frame in enumerate(frames):
        r, c = divmod(index, cols)
        tile = Image.new("RGBA", (w, h), (28, 28, 28, 255))
        tile.alpha_composite(frame)
        contact.paste(tile.convert("RGB"), (c * w, r * h))
    contact.save(args.qa / "sleeping-sheet-contact.png")
    print(
        f"built {args.output.name}: {len(frames)} unique frames x {args.duration_ms}ms "
        f"head_range={report['stability']['head_y_range']} "
        f"h_range={report['stability']['height_range']}"
    )


if __name__ == "__main__":
    main()
