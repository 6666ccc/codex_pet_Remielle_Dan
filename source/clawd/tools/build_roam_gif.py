"""Build the Clawd roam animation from the approved Codex right-moving frames.

Clawd mirrors this right-facing asset automatically when the pet walks left.
The source frames are padded onto the theme's 360px square canvas so every
theme asset keeps the same logical aspect ratio and visual scale.
"""

from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ATLAS = ROOT.parent / "source/codex" / "final" / "spritesheet.png"
OUTPUT = ROOT / "assets" / "roam.gif"
DURATIONS = [120, 120, 120, 120, 120, 120, 120, 220]
CANVAS_SIZE = (360, 360)
SCALE = 1.4
CELL_SIZE = (192, 208)
RUNNING_RIGHT_ROW = 1


def normalized_frame(source: Image.Image) -> Image.Image:
    size = (round(source.width * SCALE), round(source.height * SCALE))
    sprite = source.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", CANVAS_SIZE)
    x = (CANVAS_SIZE[0] - sprite.width) // 2
    y = CANVAS_SIZE[1] - sprite.height - 24
    canvas.alpha_composite(sprite, (x, y))
    return canvas


def main() -> None:
    with Image.open(SOURCE_ATLAS) as atlas:
        expected_size = (CELL_SIZE[0] * len(DURATIONS), CELL_SIZE[1] * 9)
        if atlas.size != expected_size:
            raise SystemExit(f"Expected a {expected_size} atlas, found {atlas.size}")
        source_frames = [
            atlas.crop((
                index * CELL_SIZE[0],
                RUNNING_RIGHT_ROW * CELL_SIZE[1],
                (index + 1) * CELL_SIZE[0],
                (RUNNING_RIGHT_ROW + 1) * CELL_SIZE[1],
            )).convert("RGBA")
            for index in range(len(DURATIONS))
        ]
    frames = [normalized_frame(frame) for frame in source_frames]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=DURATIONS,
        loop=0,
        disposal=2,
        optimize=False,
    )
    print(f"Built {OUTPUT} with {len(frames)} right-facing frames.")


if __name__ == "__main__":
    main()
