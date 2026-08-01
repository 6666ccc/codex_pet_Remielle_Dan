# Open-Source Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the Remielle_Dan pet repo into a GitHub-ready `source/` + `packages/` layout with CC BY-NC 4.0, trigger-table README, Release packaging, and zero public `xingyu` identifiers.

**Architecture:** Align Clawd `theme.json` to existing assets first; migrate installable artifacts into `packages/Remielle_Dan-*` and build tooling into `source/`; add open-source root files; provide `scripts/package-release.ps1` that validates references and zips packages.

**Tech Stack:** Git, PowerShell, JSON theme/pet configs, Markdown docs, CC BY-NC 4.0 text.

## Global Constraints

- Public identifier must be `Remielle_Dan` — no `xingyu` in README, packages, source notes, docs, scripts, preview.
- License: CC BY-NC 4.0.
- Clawd theme version after alignment: `0.5.2`.
- Sleep states share `sleeping.gif`; remove broken `react-annoyed` reaction.
- Do not auto-push or create GitHub Release.
- Do not commit `__pycache__`, large ignored QA dumps, or parent-folder duplicate zips.
- Work in repo root: `codex蕾米埃尔/` (remote `codex_pet_Remielle_Dan`). User approved working on `main`.

---

### Task 1: Align Clawd theme to runnable assets

**Files:**
- Modify: `xingyu-clawd-theme/theme.json`
- Modify: `xingyu-clawd-theme/README.md` (interim; rewritten again after move)

**Interfaces:**
- Produces: Valid `theme.json` v`0.5.2` where every referenced GIF exists under `assets/`

- [ ] **Step 1: Rewrite sleep + reaction entries**

Set:
- `version` → `"0.5.2"`
- `description` → remove claim of update-checking if asset absent
- `states.yawning|dozing|collapsing|sleeping|waking` → all `["sleeping.gif"]`
- Remove `reactions.annoyed` entirely
- Keep existing assets for idle/thinking/editing/roam/attention/notification/carrying/error/drag/double

- [ ] **Step 2: Verify every referenced file exists**

Run PowerShell to collect `.gif` strings from `theme.json` and test paths under `assets/`. Expected: zero missing.

- [ ] **Step 3: Commit**

```bash
git add xingyu-clawd-theme/theme.json xingyu-clawd-theme/README.md
git commit -m "Align Clawd theme to existing assets as v0.5.2."
```

---

### Task 2: Create target directories and migrate packages

**Files:**
- Create: `packages/Remielle_Dan-codex-pet/`, `packages/Remielle_Dan-clawd-theme/`
- Move: `codex-pet/*` → `packages/Remielle_Dan-codex-pet/`
- Move: `xingyu-clawd-theme/theme.json`, `assets/`, README → `packages/Remielle_Dan-clawd-theme/`
- Modify: `packages/Remielle_Dan-codex-pet/pet.json` (`id` → `Remielle_Dan`)

- [ ] **Step 1: Create packages dirs and git-mv installable files**

Prefer `git mv` for tracked files. Copy/move untracked assets that belong in the package.

- [ ] **Step 2: Update pet.json id to Remielle_Dan**

- [ ] **Step 3: Verify package file sets**

Codex: `pet.json`, `spritesheet.webp` present.  
Clawd: `theme.json` + all referenced GIFs under `assets/`.

- [ ] **Step 4: Commit**

```bash
git commit -m "Move installable packages under packages/Remielle_Dan-*."
```

---

### Task 3: Migrate source tooling and docs; drop bulk QA from main tree

**Files:**
- Create: `source/codex/{prompts,tools,references,frames,notes}/`, `source/clawd/{tools,generated,notes}/`
- Move: `pet-build/prompts|tools|references|frames` → `source/codex/`
- Move: `xingyu-clawd-theme/tools/*.py` → `source/clawd/tools/`
- Move: `source-images/*` → `source/codex/references/` (dedupe)
- Move: `CLAWD_ANIMATION_PLAN.md` → `docs/design/clawd-animation-plan.md`
- Move: `codex-pet.html` → `preview/codex-pet.html`
- Create: `source/clawd/generated/README.md`, `source/codex/notes/README.md`
- Remove from git tracking: `xingyu-clawd-theme/qa/`, `xingyu-clawd-theme/generated/`, `pet-build/qa/` bulky artifacts (leave untracked local copies if present)

- [ ] **Step 1: git mv source trees**
- [ ] **Step 2: Rewrite path mentions of xingyu in moved design docs**
- [ ] **Step 3: Write generated/notes README stubs**
- [ ] **Step 4: Remove leftover empty/old dirs from index**
- [ ] **Step 5: Commit**

```bash
git commit -m "Relocate build sources under source/ and design docs."
```

---

### Task 4: Add open-source root skeleton

**Files:**
- Create: `LICENSE` (CC BY-NC 4.0 full text)
- Create: `.gitignore`
- Create: `CONTRIBUTING.md`
- Create: `README.md` (full trigger tables per spec)
- Create: `packages/Remielle_Dan-clawd-theme/README.md` (short install + table)
- Optional: `.github/ISSUE_TEMPLATE/bug.yml` and `asset.yml`

`.gitignore` must include at least:

```gitignore
__pycache__/
*.pyc
.DS_Store
Thumbs.db
dist-release/
*.zip
.idea/
.vscode/
source/clawd/generated/**
!source/clawd/generated/README.md
**/qa/**
!docs/**
```

- [ ] **Step 1: Write LICENSE, .gitignore, CONTRIBUTING**
- [ ] **Step 2: Write root README with Codex + Clawd trigger tables and Remielle_Dan paths**
- [ ] **Step 3: Write package README**
- [ ] **Step 4: Commit**

```bash
git commit -m "Add LICENSE, gitignore, contributing guide, and README."
```

---

### Task 5: Release packaging script + verification

**Files:**
- Create: `scripts/package-release.ps1`
- Create: `docs/guides/packaging.md` (short how-to)

Script behavior:
1. Resolve repo root from `$PSScriptRoot`
2. Parse `packages/Remielle_Dan-clawd-theme/theme.json` for version and every `.gif` reference; fail if missing
3. Require `packages/Remielle_Dan-codex-pet/pet.json` and `spritesheet.webp`; fail if `pet.json.id` ≠ `Remielle_Dan`
4. Zip into `dist-release/Remielle_Dan-codex-pet-v{ver}.zip` and `Remielle_Dan-clawd-theme-v{ver}.zip`
5. Exit non-zero on failure

- [ ] **Step 1: Implement script**
- [ ] **Step 2: Run script; expect two zips and exit 0**
- [ ] **Step 3: Scan public tree for `xingyu` (case-insensitive); expect no hits outside this plan/spec historical migration notes if any — fix hits in public files**
- [ ] **Step 4: Commit script + guide**

```bash
git commit -m "Add Release packaging script and packaging guide."
```

---

### Task 6: Final acceptance

- [ ] **Step 1: Tree check** — `packages/`, `source/`, `docs/`, `scripts/`, `preview/` exist; old `xingyu-clawd-theme/`, `codex-pet/`, `pet-build/` gone from repo
- [ ] **Step 2: Reference check** — theme GIFs all exist; pet id `Remielle_Dan`
- [ ] **Step 3: `xingyu` scan on public paths**
- [ ] **Step 4: Report status to user (no push unless asked)**
