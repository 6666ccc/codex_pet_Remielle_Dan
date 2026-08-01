"""Create a compact first-frame contact sheet for theme QA."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "qa" / "theme-contact-sheet.png"
MOTION_OUTPUT = ROOT / "qa" / "motion-samples.png"
FILES = [
    "idle-loop.gif",
    "thinking.gif",
    "editing.gif",
    "notification.gif",
    "carrying.gif",
    "error.gif",
    "attention.gif",
    "roam.gif",
    "drag-left.gif",
    "drag-right.gif",
]


def main() -> None:
    thumb_size = 180
    label_height = 24
    columns = 4
    rows = (len(FILES) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (columns * thumb_size, rows * (thumb_size + label_height)),
        "#202124",
    )
    draw = ImageDraw.Draw(sheet)

    for index, filename in enumerate(FILES):
        with Image.open(ASSETS / filename) as opened:
            frame = opened.convert("RGBA")
        frame.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
        tile = Image.new("RGBA", (thumb_size, thumb_size), "#d7d7d7")
        x = (thumb_size - frame.width) // 2
        y = (thumb_size - frame.height) // 2
        tile.alpha_composite(frame, (x, y))
        column = index % columns
        row = index // columns
        left = column * thumb_size
        top = row * (thumb_size + label_height)
        sheet.paste(tile.convert("RGB"), (left, top))
        draw.text((left + 6, top + thumb_size + 5), filename, fill="white")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT)
    print(f"wrote {OUTPUT}")

    motion_files = [
        "roam.gif",
        "drag-left.gif",
        "error.gif",
        "notification.gif",
        "carrying.gif",
    ]
    sample_count = 6
    motion_sheet = Image.new(
        "RGB",
        (sample_count * thumb_size, len(motion_files) * (thumb_size + label_height)),
        "#202124",
    )
    motion_draw = ImageDraw.Draw(motion_sheet)
    for row, filename in enumerate(motion_files):
        with Image.open(ASSETS / filename) as opened:
            sample_indices = [
                round(index * (opened.n_frames - 1) / (sample_count - 1))
                for index in range(sample_count)
            ]
            for column, frame_index in enumerate(sample_indices):
                opened.seek(frame_index)
                frame = opened.convert("RGBA")
                frame.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
                tile = Image.new("RGBA", (thumb_size, thumb_size), "#d7d7d7")
                x = (thumb_size - frame.width) // 2
                y = (thumb_size - frame.height) // 2
                tile.alpha_composite(frame, (x, y))
                left = column * thumb_size
                top = row * (thumb_size + label_height)
                motion_sheet.paste(tile.convert("RGB"), (left, top))
            motion_draw.text(
                (6, row * (thumb_size + label_height) + thumb_size + 5),
                filename,
                fill="white",
            )

    MOTION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    motion_sheet.save(MOTION_OUTPUT)
    print(f"wrote {MOTION_OUTPUT}")


if __name__ == "__main__":
    main()
