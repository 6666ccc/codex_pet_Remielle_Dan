"""Build one registered GIF from an approved transparent 4x4 spritesheet."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw

from build_movement_animations import (
    CANVAS_SIZE,
    GIF_ALPHA_THRESHOLD,
    extract_cells,
    frame_metrics,
    normalize_cells,
    sanitize_for_gif,
)


def save_gif_atomic(path: Path, frames: list[Image.Image], duration_ms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.stem}.tmp{path.suffix}")
    frames[0].save(
        temporary,
        save_all=True,
        append_images=frames[1:],
        duration=[duration_ms] * len(frames),
        loop=0,
        disposal=2,
        optimize=False,
    )
    os.replace(temporary, path)


def make_review_sheet(frames: list[Image.Image], output: Path) -> None:
    thumb = 180
    columns = 8
    sheet = Image.new("RGB", (columns * thumb, 4 * thumb))
    draw = ImageDraw.Draw(sheet)
    for background_index, background in enumerate(("#000000", "#808080")):
        for index, frame in enumerate(frames):
            tile = Image.new("RGBA", (thumb, thumb), background)
            preview = frame.copy()
            preview.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
            tile.alpha_composite(
                preview,
                ((thumb - preview.width) // 2, (thumb - preview.height) // 2),
            )
            column = index % columns
            local_row = index // columns
            y_offset = background_index * 2 * thumb
            x = column * thumb
            y = y_offset + local_row * thumb
            sheet.paste(tile.convert("RGB"), (x, y))
            draw.text(
                (x + 5, y + 5),
                f"#{index:02d}",
                fill="white",
                stroke_width=2,
                stroke_fill="black",
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha-sheet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--duration-ms", type=int, required=True)
    args = parser.parse_args()

    if not 80 <= args.duration_ms <= 300:
        raise SystemExit("duration-ms must be between 80 and 300")

    with Image.open(args.alpha_sheet) as opened:
        sheet = opened.convert("RGBA")
    frames, scale = normalize_cells(extract_cells(sheet))
    frames = sanitize_for_gif(frames)
    save_gif_atomic(args.output, frames, args.duration_ms)

    args.qa_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "ok": True,
        "source": str(args.alpha_sheet.resolve()),
        "output": str(args.output.resolve()),
        "frame_count": len(frames),
        "duration_ms": args.duration_ms,
        "loop_duration_ms": len(frames) * args.duration_ms,
        "canvas": list(CANVAS_SIZE),
        "shared_scale": scale,
        "gif_alpha_threshold": GIF_ALPHA_THRESHOLD,
        "frames": frame_metrics(frames),
    }
    metrics["ok"] = all(frame["border_pixels"] == 0 for frame in metrics["frames"])
    (args.qa_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    make_review_sheet(frames, args.qa_dir / "review-sheet.png")
    print(f"Built {args.output.name}: {len(frames)} frames at {args.duration_ms}ms")


if __name__ == "__main__":
    main()
