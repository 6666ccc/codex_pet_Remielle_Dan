#!/usr/bin/env python3
"""Extract GIF frames into Codex pet cells and rebuild the atlas."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageSequence

CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
STANDARD_ROWS = 9
EXTENDED_ROWS = 11
ATLAS_WIDTH = COLUMNS * CELL_WIDTH
STANDARD_HEIGHT = STANDARD_ROWS * CELL_HEIGHT
EXTENDED_HEIGHT = EXTENDED_ROWS * CELL_HEIGHT

SKILL_SCRIPTS = Path.home() / ".codex" / "skills" / "hatch-pet" / "scripts"


def composite_gif_frames(path: Path) -> list[Image.Image]:
    """Decode a GIF with disposal handling into a list of RGBA frames."""
    frames: list[Image.Image] = []
    with Image.open(path) as gif:
        canvas = Image.new("RGBA", gif.size, (0, 0, 0, 0))
        for frame in ImageSequence.Iterator(gif):
            disposed = canvas.copy()
            current = frame.convert("RGBA")
            # Some paletted GIFs store transparency incorrectly after convert;
            # prefer the frame's own alpha if present.
            disposed.alpha_composite(current, (0, 0))
            frames.append(disposed.copy())

            disposal = frame.disposal_method if hasattr(frame, "disposal_method") else 0
            # Pillow exposes disposal via disposal_method on some builds; fall back
            # to info dict used by gif decoders.
            if disposal == 0:
                disposal = int(frame.info.get("disposal", 0) or 0)

            if disposal == 2:
                # Restore to background (transparent for our pets).
                canvas = Image.new("RGBA", gif.size, (0, 0, 0, 0))
            elif disposal != 3:
                # 0/1: leave in place; 3 (restore previous) approximated as leave.
                canvas = disposed
    return frames


def sample_indices(count: int, take: int) -> list[int]:
    if take <= 0:
        return []
    if count <= take:
        # Repeat last frame if short; usually not needed.
        idxs = list(range(count))
        while len(idxs) < take:
            idxs.append(count - 1)
        return idxs
    if take == 1:
        return [0]
    return [round(i * (count - 1) / (take - 1)) for i in range(take)]


def fit_to_cell(source: Image.Image) -> Image.Image:
    frame = source.convert("RGBA")
    # Crop to opaque content so empty margins don't shrink the character.
    alpha = frame.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is not None:
        frame = frame.crop(bbox)
    fitted = frame.copy()
    fitted.thumbnail((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS)
    cell = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    left = (CELL_WIDTH - fitted.width) // 2
    # Bias slightly upward so seated characters keep feet near the bottom.
    top = CELL_HEIGHT - fitted.height - max(4, (CELL_HEIGHT - fitted.height) // 8)
    top = max(0, top)
    cell.alpha_composite(fitted, (left, top))
    return clear_transparent_rgb(cell)


def clear_transparent_rgb(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    data = bytearray(rgba.tobytes())
    for index in range(0, len(data), 4):
        if data[index + 3] == 0:
            data[index] = 0
            data[index + 1] = 0
            data[index + 2] = 0
    return Image.frombytes("RGBA", rgba.size, bytes(data))


def fit_sequence_to_cells(frames: list[Image.Image]) -> list[Image.Image]:
    """Normalize a GIF sequence with one shared crop, scale, and baseline."""
    union: tuple[int, int, int, int] | None = None
    rgba_frames = [frame.convert("RGBA") for frame in frames]
    for frame in rgba_frames:
        bbox = frame.getchannel("A").getbbox()
        if bbox is None:
            continue
        if union is None:
            union = bbox
        else:
            union = (
                min(union[0], bbox[0]), min(union[1], bbox[1]),
                max(union[2], bbox[2]), max(union[3], bbox[3]),
            )
    if union is None:
        return [Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0)) for _ in frames]

    crop_width = union[2] - union[0]
    crop_height = union[3] - union[1]
    scale = min(CELL_WIDTH / crop_width, (CELL_HEIGHT - 8) / crop_height)
    target_size = (max(1, round(crop_width * scale)), max(1, round(crop_height * scale)))
    left = (CELL_WIDTH - target_size[0]) // 2
    top = CELL_HEIGHT - target_size[1] - max(4, (CELL_HEIGHT - target_size[1]) // 8)

    cells: list[Image.Image] = []
    for frame in rgba_frames:
        crop = frame.crop(union).resize(target_size, Image.Resampling.LANCZOS)
        cell = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
        cell.alpha_composite(crop, (left, max(0, top)))
        cells.append(clear_transparent_rgb(cell))
    return cells


def write_row(frames: list[Image.Image], out_dir: Path, *, stable: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):
        old.unlink()
    normalized = fit_sequence_to_cells(frames) if stable else [fit_to_cell(frame) for frame in frames]
    for index, frame in enumerate(normalized):
        path = out_dir / f"{index:02d}.png"
        frame.save(path)
        print(f"wrote {path}")


def extract_even(path: Path, take: int) -> list[Image.Image]:
    all_frames = composite_gif_frames(path)
    return [all_frames[i] for i in sample_indices(len(all_frames), take)]


def replace_status_rows(run_dir: Path) -> None:
    refs = run_dir / "references"
    frames_root = run_dir / "frames"

    # Codex status mapping requested by the user:
    # idle    -> 待机中.gif (reference-06.gif)
    # waiting -> 待机.gif   (reference-05.gif)
    # running -> 修改文件.gif (reference-01.gif)
    # review  -> 完成.gif   (reference-03.gif)
    # failed  -> keep the independently generated 8-frame blocked animation.
    write_row(extract_even(refs / "reference-06.gif", 6), frames_root / "idle")
    write_row(extract_even(refs / "reference-05.gif", 6), frames_root / "waiting")
    write_row(extract_even(refs / "reference-03.gif", 6), frames_root / "review")
    write_row(extract_even(refs / "reference-01.gif", 6), frames_root / "running", stable=True)


ROW_SPECS = {
    "idle": (0, 6),
    "waiting": (6, 6),
    "running": (7, 6),
    "review": (8, 6),
}


def paste_row_cells(atlas: Image.Image, frames_root: Path, state: str) -> None:
    row, frame_count = ROW_SPECS[state]
    for column in range(frame_count):
        path = frames_root / state / f"{column:02d}.png"
        with Image.open(path) as opened:
            cell = opened.convert("RGBA")
        if cell.size != (CELL_WIDTH, CELL_HEIGHT):
            cell = fit_to_cell(cell)
        # Clear target slot then paste, so we don't composite over old pixels.
        blank = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
        atlas.paste(blank, (column * CELL_WIDTH, row * CELL_HEIGHT))
        atlas.alpha_composite(cell, (column * CELL_WIDTH, row * CELL_HEIGHT))


def rebuild_atlases(run_dir: Path, old_extended: Path) -> None:
    """Replace only the four target rows inside the existing despilled 8x11 atlas."""
    with Image.open(old_extended) as opened:
        extended = opened.convert("RGBA")
    if extended.size != (ATLAS_WIDTH, EXTENDED_HEIGHT):
        raise SystemExit(
            f"expected 8x11 extended {ATLAS_WIDTH}x{EXTENDED_HEIGHT}, got {extended.size}"
        )

    frames_root = run_dir / "frames"
    for state in ("idle", "waiting", "running", "review"):
        paste_row_cells(extended, frames_root, state)

    # v2 atlas keeps a neutral/default look fallback in idle column 6.
    with Image.open(frames_root / "idle" / "00.png") as opened:
        neutral = opened.convert("RGBA")
    blank = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    atlas_x = 6 * CELL_WIDTH
    atlas_y = 0
    extended.paste(blank, (atlas_x, atlas_y))
    extended.alpha_composite(neutral, (atlas_x, atlas_y))

    extended = clear_transparent_rgb(extended)

    out_dir = run_dir / "final"
    out_dir.mkdir(parents=True, exist_ok=True)

    standard = extended.crop((0, 0, ATLAS_WIDTH, STANDARD_HEIGHT))
    standard_png = out_dir / "spritesheet.png"
    standard_webp = out_dir / "spritesheet.webp"
    standard.save(standard_png)
    standard.save(standard_webp, format="WEBP", lossless=True, quality=100, method=6, exact=True)
    print(f"wrote {standard_png}")
    print(f"wrote {standard_webp}")

    extended_png = out_dir / "spritesheet-extended.png"
    extended_webp = out_dir / "spritesheet-extended.webp"
    extended.save(extended_png)
    extended.save(extended_webp, format="WEBP", lossless=True, quality=100, method=6, exact=True)
    print(f"wrote {extended_png}")
    print(f"wrote {extended_webp}")


def write_extended_manifest(path: Path, atlas_name: str) -> None:
    labels = [
        "000",
        "022.5",
        "045",
        "067.5",
        "090",
        "112.5",
        "135",
        "157.5",
        "180",
        "202.5",
        "225",
        "247.5",
        "270",
        "292.5",
        "315",
        "337.5",
    ]
    manifest = {
        "spritesheetPath": atlas_name,
        "spritesheetLayout": {
            "columns": COLUMNS,
            "rows": EXTENDED_ROWS,
            "cellWidth": CELL_WIDTH,
            "cellHeight": CELL_HEIGHT,
            "lookDirectionCount": len(labels),
            "neutralLookFrame": {"rowIndex": 0, "columnIndex": 6},
        },
        "lookDirections": [
            {
                "degrees": float(label),
                "rowIndex": STANDARD_ROWS + index // COLUMNS,
                "columnIndex": index % COLUMNS,
            }
            for index, label in enumerate(labels)
        ],
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def validate(atlas_path: Path, json_out: Path) -> None:
    import subprocess
    import sys

    cmd = [
        sys.executable,
        str(SKILL_SCRIPTS / "validate_atlas.py"),
        str(atlas_path),
        "--json-out",
        str(json_out),
        "--require-v2",
    ]
    subprocess.check_call(cmd)
    print(f"validated {atlas_path}")


def render_previews(run_dir: Path) -> None:
    import subprocess
    import sys

    out = run_dir / "qa" / "previews"
    out.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SKILL_SCRIPTS / "render_animation_previews.py"),
        "--frames-root",
        str(run_dir / "frames"),
        "--output-dir",
        str(out),
    ]
    subprocess.check_call(cmd)


def sync_packages(
    run_dir: Path,
    deliverable_dir: Path,
    install_dir: Path,
) -> None:
    src_webp = run_dir / "final" / "spritesheet-extended.webp"
    src_validation = run_dir / "final" / "validation-extended.json"

    # Sync pet-build final tree.
    pet_build_final = deliverable_dir / "pet-build" / "final"
    pet_build_final.mkdir(parents=True, exist_ok=True)
    for name in [
        "spritesheet.png",
        "spritesheet.webp",
        "spritesheet-extended.png",
        "spritesheet-extended.webp",
        "spritesheet-extended.json",
        "validation-extended.json",
    ]:
        src = run_dir / "final" / name
        if src.exists():
            shutil.copy2(src, pet_build_final / name)

    # Sync frames for the four replaced rows into pet-build.
    for state in ("idle", "waiting", "running", "review"):
        dst = deliverable_dir / "pet-build" / "frames" / state
        src = run_dir / "frames" / state
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    # Package for Codex.
    for package_dir in (deliverable_dir / "codex-pet", install_dir):
        package_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_webp, package_dir / "spritesheet.webp")
        shutil.copy2(src_validation, package_dir / "validation.json")
        pet_json = package_dir / "pet.json"
        if not pet_json.exists():
            # Prefer existing deliverable pet.json.
            source_pet = deliverable_dir / "codex-pet" / "pet.json"
            if source_pet.exists() and package_dir != source_pet.parent:
                shutil.copy2(source_pet, pet_json)
        print(f"updated package {package_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        default=str(Path(__file__).resolve().parents[1]),
    )
    parser.add_argument(
        "--deliverable-dir",
        default=str(Path(__file__).resolve().parents[2] / "codex蕾米埃尔"),
    )
    parser.add_argument(
        "--install-dir",
        default=str(Path.home() / ".codex" / "pets" / "xingyu"),
    )
    parser.add_argument("--skip-extract", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    deliverable_dir = Path(args.deliverable_dir).expanduser().resolve()
    install_dir = Path(args.install_dir).expanduser().resolve()

    old_extended = run_dir / "final" / "spritesheet-extended.webp"
    if not old_extended.exists():
        raise SystemExit(f"missing existing extended atlas: {old_extended}")

    # Keep a backup of look rows source before overwrite.
    backup = run_dir / "final" / "spritesheet-extended.before-gif-replace.webp"
    if not backup.exists():
        shutil.copy2(old_extended, backup)
        print(f"backed up {backup}")

    if not args.skip_extract:
        replace_status_rows(run_dir)

    rebuild_atlases(run_dir, backup if backup.exists() else old_extended)
    write_extended_manifest(
        run_dir / "final" / "spritesheet-extended.json",
        "spritesheet-extended.webp",
    )
    validate(
        run_dir / "final" / "spritesheet-extended.webp",
        run_dir / "final" / "validation-extended.json",
    )
    render_previews(run_dir)
    sync_packages(run_dir, deliverable_dir, install_dir)
    print("done")


if __name__ == "__main__":
    main()
