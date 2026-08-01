"""Build and validate phase-01 Clawd movement animations.

The input is one approved transparent 4x4 sheet in row-major temporal order.
The script writes only roam/drag movement files to the requested output
directory, so it can be run against a staging directory before deployment.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


FRAME_COUNT = 16
GRID_SIZE = 4
CANVAS_SIZE = (360, 360)
TARGET_MAX_WIDTH = 300
TARGET_MAX_HEIGHT = 300
BASELINE_Y = 332
GIF_ALPHA_THRESHOLD = 96


def extract_cells(sheet: Image.Image) -> list[Image.Image]:
    cells: list[Image.Image] = []
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            left = round(column * sheet.width / GRID_SIZE)
            top = round(row * sheet.height / GRID_SIZE)
            right = round((column + 1) * sheet.width / GRID_SIZE)
            bottom = round((row + 1) * sheet.height / GRID_SIZE)
            cell = sheet.crop(
                (left, top, right, bottom)
            ).convert("RGBA")
            cells.append(cell)
    return cells


def normalize_cells(cells: list[Image.Image]) -> tuple[list[Image.Image], float]:
    boxes = [cell.getbbox() for cell in cells]
    if any(box is None for box in boxes):
        empty = [index for index, box in enumerate(boxes) if box is None]
        raise SystemExit(f"Empty movement cells: {empty}")

    widths = [box[2] - box[0] for box in boxes if box is not None]
    heights = [box[3] - box[1] for box in boxes if box is not None]
    scale = min(
        TARGET_MAX_WIDTH / max(widths),
        TARGET_MAX_HEIGHT / max(heights),
    )

    normalized: list[Image.Image] = []
    for cell, box in zip(cells, boxes, strict=True):
        assert box is not None
        subject = cell.crop(box)
        resized = subject.resize(
            (
                max(1, round(subject.width * scale)),
                max(1, round(subject.height * scale)),
            ),
            Image.Resampling.LANCZOS,
        )
        canvas = Image.new("RGBA", CANVAS_SIZE)
        x = (CANVAS_SIZE[0] - resized.width) // 2
        y = BASELINE_Y - resized.height
        if x < 0 or y < 0 or x + resized.width > CANVAS_SIZE[0]:
            raise SystemExit(f"Normalized frame does not fit canvas: {(x, y, *resized.size)}")
        canvas.alpha_composite(resized, (x, y))
        normalized.append(canvas)
    return normalized, scale


def sanitize_for_gif(frames: list[Image.Image]) -> list[Image.Image]:
    """Remove chroma-key edge pollution before GIF's binary transparency."""
    sanitized: list[Image.Image] = []
    for frame in frames:
        rgba = frame.convert("RGBA")
        alpha = rgba.getchannel("A")
        transparent = alpha.point(
            lambda value: 255 if value < GIF_ALPHA_THRESHOLD else 0
        )
        near_transparency = transparent.filter(ImageFilter.MaxFilter(7))
        pixels = list(rgba.get_flattened_data())
        edge_pixels = list(near_transparency.get_flattened_data())
        clean_pixels = []
        for (red, green, blue, opacity), near_edge in zip(
            pixels,
            edge_pixels,
            strict=True,
        ):
            green_spill = green >= red + 20 and green >= blue + 8
            cyan_spill = green >= red + 20 and blue >= red + 20
            if opacity < GIF_ALPHA_THRESHOLD or (
                near_edge and (green_spill or cyan_spill)
            ):
                clean_pixels.append((0, 0, 0, 0))
            else:
                clean_pixels.append((red, green, blue, 255))
        clean = Image.new("RGBA", rgba.size)
        clean.putdata(clean_pixels)
        sanitized.append(clean)
    return sanitized


def save_gif_atomic(path: Path, frames: list[Image.Image], duration_ms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.stem}.tmp{path.suffix}")
    frames[0].save(
        temp,
        save_all=True,
        append_images=frames[1:],
        duration=[duration_ms] * len(frames),
        loop=0,
        disposal=2,
        optimize=False,
    )
    os.replace(temp, path)


def frame_metrics(frames: list[Image.Image]) -> list[dict[str, object]]:
    metrics: list[dict[str, object]] = []
    for index, frame in enumerate(frames):
        box = frame.getbbox()
        if box is None:
            raise SystemExit(f"Frame {index} is empty after normalization")
        alpha = frame.getchannel("A")
        border_pixels = 0
        for x in range(frame.width):
            border_pixels += int(alpha.getpixel((x, 0)) > 0)
            border_pixels += int(alpha.getpixel((x, frame.height - 1)) > 0)
        for y in range(1, frame.height - 1):
            border_pixels += int(alpha.getpixel((0, y)) > 0)
            border_pixels += int(alpha.getpixel((frame.width - 1, y)) > 0)
        metrics.append(
            {
                "index": index,
                "bbox": list(box),
                "width": box[2] - box[0],
                "height": box[3] - box[1],
                "center_x": (box[0] + box[2]) / 2,
                "baseline_y": box[3],
                "nontransparent_pixels": (
                    frame.width * frame.height - alpha.histogram()[0]
                ),
                "border_pixels": border_pixels,
            }
        )
    return metrics


def make_contact_sheet(
    right_frames: list[Image.Image],
    left_frames: list[Image.Image],
    output: Path,
) -> None:
    thumb = 180
    label_height = 24
    columns = 8
    rows_per_direction = 2
    sheet = Image.new(
        "RGB",
        (columns * thumb, 2 * rows_per_direction * (thumb + label_height)),
        "#202124",
    )
    draw = ImageDraw.Draw(sheet)
    for direction_index, (label, frames) in enumerate(
        (("right", right_frames), ("left", left_frames))
    ):
        for index, frame in enumerate(frames):
            tile = Image.new("RGBA", (thumb, thumb), "#d7d7d7")
            preview = frame.copy()
            preview.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
            tile.alpha_composite(
                preview,
                ((thumb - preview.width) // 2, (thumb - preview.height) // 2),
            )
            column = index % columns
            local_row = index // columns
            row = direction_index * rows_per_direction + local_row
            x = column * thumb
            y = row * (thumb + label_height)
            sheet.paste(tile.convert("RGB"), (x, y))
            draw.text((x + 5, y + thumb + 4), f"{label} #{index:02d}", fill="white")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def make_edge_review_sheet(frames: list[Image.Image], output: Path) -> None:
    """Render every frame on black and gray to expose chroma-key halos."""
    thumb = 180
    columns = 8
    rows = 4
    backgrounds = ("#000000", "#808080")
    sheet = Image.new("RGB", (columns * thumb, rows * thumb), "#202124")
    for background_index, background in enumerate(backgrounds):
        for index, frame in enumerate(frames):
            tile = Image.new("RGBA", (thumb, thumb), background)
            preview = frame.copy()
            preview.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
            tile.alpha_composite(
                preview,
                ((thumb - preview.width) // 2, (thumb - preview.height) // 2),
            )
            column = index % columns
            row = background_index * 2 + index // columns
            sheet.paste(tile.convert("RGB"), (column * thumb, row * thumb))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha-sheet", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--duration-ms", type=int, default=110)
    args = parser.parse_args()

    if not 95 <= args.duration_ms <= 120:
        raise SystemExit("duration-ms must stay within the approved 95-120ms range")

    with Image.open(args.alpha_sheet) as opened:
        sheet = opened.convert("RGBA")
    if sheet.mode != "RGBA":
        raise SystemExit("Movement source must be RGBA")

    source_cells = extract_cells(sheet)
    right_frames, scale = normalize_cells(source_cells)
    right_frames = sanitize_for_gif(right_frames)
    left_frames = [ImageOps.mirror(frame) for frame in right_frames]

    save_gif_atomic(args.output_dir / "roam.gif", right_frames, args.duration_ms)
    save_gif_atomic(args.output_dir / "drag-right.gif", right_frames, args.duration_ms)
    save_gif_atomic(args.output_dir / "drag-left.gif", left_frames, args.duration_ms)

    args.qa_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "ok": True,
        "source": str(args.alpha_sheet.resolve()),
        "frame_count": len(right_frames),
        "duration_ms": args.duration_ms,
        "loop_duration_ms": args.duration_ms * len(right_frames),
        "canvas": list(CANVAS_SIZE),
        "normalization": {
            "shared_scale": scale,
            "baseline_y": BASELINE_Y,
            "target_max_width": TARGET_MAX_WIDTH,
            "target_max_height": TARGET_MAX_HEIGHT,
            "gif_alpha_threshold": GIF_ALPHA_THRESHOLD,
        },
        "right_frames": frame_metrics(right_frames),
        "left_frames": frame_metrics(left_frames),
    }
    metrics["ok"] = all(
        frame["border_pixels"] == 0
        for frame in metrics["right_frames"] + metrics["left_frames"]
    )
    (args.qa_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    make_contact_sheet(
        right_frames,
        left_frames,
        args.qa_dir / "movement-contact-sheet.png",
    )
    make_edge_review_sheet(
        right_frames,
        args.qa_dir / "movement-edge-review.png",
    )
    print(
        f"Built {len(right_frames)} movement frames at {args.duration_ms}ms "
        f"into {args.output_dir}"
    )


if __name__ == "__main__":
    main()
