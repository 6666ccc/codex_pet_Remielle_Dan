"""Build Clawd animations from the approved Codex pet atlas.

The source project is read-only. All derived GIFs are written into this
independent Clawd theme on a shared 360x360 transparent canvas.
"""

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ATLAS_CANDIDATES = [
    ROOT.parent / "codex-pet" / "spritesheet.webp",
    ROOT.parent / "codex蕾米埃尔" / "codex-pet" / "spritesheet.webp",
]
ATLAS_PATH = next(
    (candidate for candidate in ATLAS_CANDIDATES if candidate.exists()),
    ATLAS_CANDIDATES[0],
)
ERROR_SOURCE = ROOT / "generated" / "error-alpha.png"
MOVE_SHEET = ROOT / "generated" / "move-16-sheet-alpha.png"
SLEEP_SHEET = ROOT / "generated" / "sleep-16-sheet-alpha.png"
ASSETS = ROOT / "assets"

CELL_W = 192
CELL_H = 208
CANVAS = (360, 360)
SCALE = 1.4


def normalized_cell(cell: Image.Image) -> Image.Image:
    source = cell.convert("RGBA")
    size = (round(source.width * SCALE), round(source.height * SCALE))
    sprite = source.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CANVAS)
    x = (CANVAS[0] - sprite.width) // 2
    y = CANVAS[1] - sprite.height - 24
    canvas.alpha_composite(sprite, (x, y))
    return canvas


def atlas_row(atlas: Image.Image, row: int, count: int) -> list[Image.Image]:
    frames = []
    for column in range(count):
        cell = atlas.crop(
            (
                column * CELL_W,
                row * CELL_H,
                (column + 1) * CELL_W,
                (row + 1) * CELL_H,
            )
        )
        frames.append(normalized_cell(cell))
    return frames


def save_gif(
    name: str,
    frames: list[Image.Image],
    durations: list[int],
) -> None:
    if len(frames) != len(durations):
        raise ValueError(f"{name}: {len(frames)} frames but {len(durations)} durations")
    output = ASSETS / name
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )
    print(f"built {output.name}: {len(frames)} frames")


def generated_sheet_frames(path: Path) -> list[Image.Image]:
    """Split an ImageGen 4x4 sheet into registered transparent animation frames."""
    with Image.open(path) as opened:
        sheet = opened.convert("RGBA")
    frames = []
    for row in range(4):
        for column in range(4):
            left = column * sheet.width // 4
            top = row * sheet.height // 4
            right = (column + 1) * sheet.width // 4
            bottom = (row + 1) * sheet.height // 4
            cell = sheet.crop((left, top, right, bottom))
            frames.append(cell.resize(CANVAS, Image.Resampling.LANCZOS))
    return frames


def build_error_animation() -> None:
    with Image.open(ERROR_SOURCE) as opened:
        source = opened.convert("RGBA")
    bbox = source.getbbox()
    if not bbox:
        raise SystemExit("error-alpha.png is empty")
    subject = source.crop(bbox)
    scale = min(300 / subject.width, 300 / subject.height)
    size = (round(subject.width * scale), round(subject.height * scale))
    subject = subject.resize(size, Image.Resampling.LANCZOS)
    frames = []
    for offset_x, offset_y in [(-2, 2), (2, 0), (-1, 2), (1, 0)]:
        canvas = Image.new("RGBA", CANVAS)
        x = (CANVAS[0] - subject.width) // 2 + offset_x
        y = CANVAS[1] - subject.height - 24 + offset_y
        canvas.alpha_composite(subject, (x, y))
        frames.append(canvas)
    save_gif("error.gif", frames, [170, 170, 170, 520])


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    with Image.open(ATLAS_PATH) as opened:
        atlas = opened.convert("RGBA")

    run_right = atlas_row(atlas, 1, 8)
    run_left = atlas_row(atlas, 2, 8)
    waving = atlas_row(atlas, 3, 4)
    jumping = atlas_row(atlas, 4, 5)
    failed = atlas_row(atlas, 5, 8)

    if MOVE_SHEET.exists():
        smooth_right = generated_sheet_frames(MOVE_SHEET)
        smooth_left = [ImageOps.mirror(frame) for frame in smooth_right]
    else:
        smooth_right = run_right
        smooth_left = run_left
    smooth_move_durations = [65] * len(smooth_right)
    save_gif("roam.gif", smooth_right, smooth_move_durations)
    save_gif("drag-right.gif", smooth_right, smooth_move_durations)
    save_gif("drag-left.gif", smooth_left, smooth_move_durations)
    save_gif("click-right.gif", smooth_right, smooth_move_durations)
    save_gif("click-left.gif", smooth_left, smooth_move_durations)
    save_gif(
        "react-double.gif",
        jumping,
        [130, 130, 130, 160, 280],
    )
    save_gif(
        "react-annoyed.gif",
        failed,
        [150, 150, 170, 180, 180, 170, 150, 260],
    )

    yawning = failed[0:3]
    save_gif("yawning.gif", yawning, [350, 450, 650])
    dozing = [failed[2], failed[3], failed[4], failed[3]]
    save_gif(
        "dozing.gif",
        dozing,
        [350, 450, 650, 450],
    )
    collapsing = failed[1:6]
    save_gif("collapsing.gif", collapsing, [220, 260, 300, 360, 600])
    if SLEEP_SHEET.exists():
        sleeping = generated_sheet_frames(SLEEP_SHEET)
    else:
        sleeping = [failed[4], failed[5], failed[4], failed[3]]
    save_gif(
        "sleeping.gif",
        sleeping,
        [100] * len(sleeping),
    )
    waking = [failed[5], failed[4], failed[3], failed[2], failed[1], failed[0]]
    save_gif(
        "waking.gif",
        waking,
        [180, 180, 180, 160, 140, 320],
    )
    if ERROR_SOURCE.exists():
        build_error_animation()


if __name__ == "__main__":
    main()
