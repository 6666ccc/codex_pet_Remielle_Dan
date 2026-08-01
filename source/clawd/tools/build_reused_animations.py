"""Build Clawd animations from the approved Codex pet atlas.

The source project is read-only. All derived GIFs are written into this
independent Clawd theme on a shared 360x360 transparent canvas.
"""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ATLAS_CANDIDATES = [
    ROOT.parent / "codex-pet" / "spritesheet.webp",
    ROOT.parent / "codex-pet" / "spritesheet.webp",
]
ATLAS_PATH = next(
    (candidate for candidate in ATLAS_CANDIDATES if candidate.exists()),
    ATLAS_CANDIDATES[0],
)
ERROR_SOURCE = ROOT / "generated" / "error-alpha.png"
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
    """Static error pose — no shake / hair-flash multi-frame loop."""
    with Image.open(ERROR_SOURCE) as opened:
        source = opened.convert("RGBA")
    bbox = source.getbbox()
    if not bbox:
        raise SystemExit("error-alpha.png is empty")
    subject = source.crop(bbox)
    scale = min(300 / subject.width, 300 / subject.height)
    size = (round(subject.width * scale), round(subject.height * scale))
    subject = subject.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CANVAS)
    x = (CANVAS[0] - subject.width) // 2
    y = CANVAS[1] - subject.height - 24
    canvas.alpha_composite(subject, (x, y))
    save_gif("error.gif", [canvas], [1000])


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    # Locomotion is built by build_movement_animations.py.
    # Double-click / annoyed reactions are deferred; do not regenerate those assets.
    if ERROR_SOURCE.exists():
        build_error_animation()


if __name__ == "__main__":
    main()
