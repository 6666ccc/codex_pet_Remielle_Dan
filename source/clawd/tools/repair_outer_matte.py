"""Remove the legacy light outer matte from an animated GIF.

The original high-frame Clawd GIFs contain a pale two-pixel silhouette matte.
Newer generated animations place the dark line art directly on transparency.
This script removes only bright pixels connected to the transparent boundary;
interior line art, colors, animation timing, and frame registration are kept.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def boundary_stats(frame: Image.Image) -> dict[str, float | int]:
    rgba = np.asarray(frame.convert("RGBA"))
    visible = rgba[:, :, 3] > 0
    transparent = Image.fromarray((~visible).astype(np.uint8) * 255)
    near_transparency = np.asarray(
        transparent.filter(ImageFilter.MaxFilter(3))
    ) > 0
    edge = visible & near_transparency
    dark = edge & (rgba[:, :, :3].max(axis=2) < 140)
    edge_pixels = int(edge.sum())
    return {
        "edge_pixels": edge_pixels,
        "dark_edge_pixels": int(dark.sum()),
        "dark_edge_ratio": round(float(dark.sum()) / max(1, edge_pixels), 4),
    }


def remove_outer_matte(
    frame: Image.Image,
    *,
    luminance_threshold: float,
    passes: int,
) -> tuple[Image.Image, int]:
    rgba = np.array(frame.convert("RGBA"), copy=True)
    visible = rgba[:, :, 3] > 0
    removed = 0

    for _ in range(passes):
        transparent = Image.fromarray((~visible).astype(np.uint8) * 255)
        near_transparency = np.asarray(
            transparent.filter(ImageFilter.MaxFilter(3))
        ) > 0
        luminance = rgba[:, :, :3].mean(axis=2)
        matte = visible & near_transparency & (luminance >= luminance_threshold)
        removed += int(matte.sum())
        visible[matte] = False
        rgba[matte] = (0, 0, 0, 0)

    return Image.fromarray(rgba, "RGBA"), removed


def repair_gif(
    source: Path,
    output: Path,
    report_path: Path,
    *,
    luminance_threshold: float,
    passes: int,
) -> None:
    with Image.open(source) as opened:
        loop = int(opened.info.get("loop", 0))
        frames: list[Image.Image] = []
        durations: list[int] = []
        frame_reports: list[dict[str, object]] = []

        for index in range(opened.n_frames):
            opened.seek(index)
            original = opened.convert("RGBA")
            repaired, removed = remove_outer_matte(
                original,
                luminance_threshold=luminance_threshold,
                passes=passes,
            )
            frames.append(repaired)
            durations.append(int(opened.info.get("duration", 100)))
            frame_reports.append(
                {
                    "index": index,
                    "removed_pixels": removed,
                    "before": boundary_stats(original),
                    "after": boundary_stats(repaired),
                }
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.stem}.tmp{output.suffix}")
    frames[0].save(
        temporary,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=loop,
        disposal=2,
        optimize=False,
    )
    os.replace(temporary, output)

    report = {
        "source": str(source.resolve()),
        "output": str(output.resolve()),
        "frame_count": len(frames),
        "durations_ms": durations,
        "loop": loop,
        "canvas": list(frames[0].size),
        "algorithm": {
            "name": "transparent-boundary light-matte removal",
            "luminance_threshold": luminance_threshold,
            "passes": passes,
            "neighborhood": "3x3",
        },
        "total_removed_pixels": sum(
            int(frame["removed_pixels"]) for frame in frame_reports
        ),
        "frames": frame_reports,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"repaired {source.name}: {len(frames)} frames, "
        f"removed {report['total_removed_pixels']} matte pixels"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--luminance-threshold", type=float, default=140)
    parser.add_argument("--passes", type=int, default=2)
    args = parser.parse_args()

    if args.passes < 1 or args.passes > 4:
        raise SystemExit("passes must be between 1 and 4")
    repair_gif(
        args.input,
        args.output,
        args.report,
        luminance_threshold=args.luminance_threshold,
        passes=args.passes,
    )


if __name__ == "__main__":
    main()
