# Phase 01 — right-facing movement source

Create one coherent 4×4 sprite-sheet animation containing exactly 16 ordered frames.

Use case: stylized-concept
Asset type: Clawd on Desk right-facing free-roam and drag animation source

Input images:

- `pet-build/references/canonical-base.png`: authoritative character identity, face, proportions, palette, star hair ornament, small wings, clothing and handheld device.
- `pet-build/decoded/running-right.png`: motion-family reference only; preserve the character identity from the canonical base.

Visual requirements:

- The same chibi sticker-style pink-haired winged girl in every frame.
- She faces and travels toward screen-right while holding the same device securely.
- Show one continuous, cyclic airborne travel gait: anticipation, forward push, alternating leg/wing motion, recovery, then a final pose that flows naturally back to frame 1.
- Frames are ordered left-to-right, top-to-bottom: 01–04, 05–08, 09–12, 13–16.
- Every neighboring frame is one small equal-time motion step; no pose jump, reversal, duplicated frame or unrelated action.
- Keep head size, body proportions, device shape, hair ornament, wings, palette, line width and rendering style identical across all 16 frames.
- Keep a stable apparent scale and stable center/baseline. The character must remain fully inside each cell with generous padding.
- Each cell contains exactly one complete pose. Poses must not overlap cell boundaries.

Backdrop and production constraints:

- Perfectly flat solid `#00FF00` chroma-key background across the entire sheet.
- No grid lines, borders, labels, numbers, text, scenery or checkerboard.
- No cast shadow, floor shadow, speed line, motion trail, blur, dust, glow or detached effect.
- Do not use `#00FF00` in the character.
- The sheet must be a clean square 4×4 layout suitable for deterministic equal-cell extraction.

