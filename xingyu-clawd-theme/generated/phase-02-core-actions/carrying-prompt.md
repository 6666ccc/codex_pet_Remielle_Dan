# Carrying 动画生成提示

Create one coherent 4×4 animation spritesheet with exactly 16 frames, read left-to-right and top-to-bottom.

Character: match the supplied canonical Remiel/蕾米埃尔 chibi reference exactly: pink hair, pink spiral eyes, white wing accessories, white-and-lavender outfit, and the same compact white device styling. Keep identity, proportions, line weight, colors, scale, and baseline stable.

Action semantics: this is worktree creation—carrying a new isolated work bundle into place. Show the character crouch beside one compact white-and-lavender archive box, grip it with both hands, lift it visibly, carry it with a few weighty in-place steps, carefully set it onto a small destination pad beside her device, then return to the starting crouch for a seamless loop. The action must read as搬运/携带物品, not context cleaning, typing, ordinary walking, juggling, or celebration.

Animation requirements:

- Exactly 16 distinct chronological frames in a clean 4×4 grid.
- One continuous sequence: establish box → grip → lift → weighty carry → set down → return.
- The same single box must remain spatially coherent, attached to both hands while lifted, and move through adjacent positions. It must never duplicate, teleport, float, vanish, or change design.
- Stable centered registration, consistent apparent size and baseline; no facing-direction changes.
- Use body lean, bent knees, and small wing motion to show weight without detached sweat, dust, speed lines, sparkles, shadows, or other effects.
- No readable words, letters, numbers, UI text, captions, panel borders, frame numbers, grid lines, or gutters.
- Flat solid chroma-key green background close to #00FF00 in every cell.
- No transparency in the generated source.
- The final frame must restore the starting box placement and crouched pose closely enough to loop into frame 1.

## Mandatory temporal repair constraints

- Use at least three consecutive frames for the pickup: hands contact the floor box, the same box tilts slightly while rising, then reaches the chest-held pose.
- Use at least three consecutive frames for the set-down: the chest-held box lowers while keeping the same size and perspective, tilts toward the floor, then rests flat.
- The box may not switch instantly between horizontal floor orientation and vertical held orientation.
- Both hands must visibly stay in contact throughout pickup, carry, and set-down.
- Preserve the clear middle carrying section, but make the box's scale, perspective, position, and handle details continuous on both sides of it.
