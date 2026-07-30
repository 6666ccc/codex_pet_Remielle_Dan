# Sweeping 动画生成提示

Create one coherent 4×4 animation spritesheet with exactly 16 frames, read left-to-right and top-to-bottom.

Character: match the supplied canonical Remiel/蕾米埃尔 chibi reference exactly: pink hair, pink spiral eyes, white wing accessories, white-and-lavender outfit, and the same compact white device. Keep identity, proportions, line weight, colors, scale, and baseline stable in all frames.

Action semantics: this is context compaction—cleaning up and organizing accumulated work before continuing. Show the character methodically gathering a few small paper/data cards beside her device, sweeping or sorting them into one neat stack, placing the tidy stack into the device/folder, giving a relieved finishing gesture, then returning to the opening pose. The action must read as “清扫/整理上下文”, not typing, ordinary thinking, moving house, celebrating, or sleeping.

Animation requirements:

- Exactly 16 distinct chronological frames in a clean 4×4 grid.
- One clear start → organize/sweep → tidy finish → return loop.
- A small hand brush or folder may be used, but its design and position must remain consistent.
- Keep all cards/items attached to the immediate action area; no floating debris, dust cloud, speed lines, detached sparkles, or separate effects.
- Stable centered registration, consistent apparent size, and no facing-direction changes.
- No readable words, letters, numbers, UI text, captions, panel borders, frame numbers, shadows, grid lines, or gutters.
- Flat solid chroma-key green background close to #00FF00 in every cell.
- No transparency in the generated source.

## Mandatory temporal repair constraints

- Frame 1 must already establish both the scattered cards and the hand brush/folder; neither may suddenly appear after the loop starts.
- Cards must move through adjacent, easy-to-follow positions: scattered → being gathered → one neat stack.
- The complete stack must then be visibly pushed or placed into an open folder/slot on the device over multiple consecutive frames. It must never teleport to the opposite side or vanish without the insertion being shown.
- Keep the brush physically connected to the character's hand whenever it is visible.
- The final frames must visibly restore the same card/tool arrangement and body pose as frame 1 so the wraparound is smooth.
