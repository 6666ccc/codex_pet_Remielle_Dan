# 开源仓库骨架整理设计

**Date:** 2026-08-01  
**Status:** Approved (conversation)  
**Scope:** 将 `codex_pet_Remielle_Dan`（本地目录 `codex蕾米埃尔/`）整理为适合 GitHub 开源的双区结构：实现源码与思路 + 可安装产物；产物另打 Release zip。

## Goals

- 仓库骨架符合常见开源预期：`README`、`LICENSE`、`.gitignore`、`CONTRIBUTING`，目录职责清晰。
- 同仓分目录：`source/`（实现代码与思路）与 `packages/`（可安装产物）。
- 根 `README.md` 清楚展示 Codex 状态触发与 Clawd on Desk GIF 触发逻辑。
- 许可为 **CC BY-NC 4.0**，并保留角色素材著作权声明与投诉渠道。
- 先对齐「当前满意且可运行」的主题配置与资产，再迁移目录。
- 提供 Release 打包脚本；由维护者手动上传 GitHub Release。

## Non-Goals

- 不新建或改名远程仓库；不自动 `push` / 不自动创建 GitHub Release（除非用户另行要求）。
- 不重做暂缓动画（独立 `react-annoyed`、`sweeping`、`update-checking`、视线跟随、Mini Mode 等）。
- 不把父目录重复 zip / 临时 GIF / `.superpowers` 工作区提交进 git。
- 不把大体量 `qa/` 对比图、`__pycache__`、临时 before/after 资产纳入开源主树。

## Decisions (from brainstorming)

| 项 | 选择 |
| --- | --- |
| 整理范围 | 全面开源整理（骨架 + 发布精简 + 文档 + 未提交可运行对齐） |
| 许可证 | CC BY-NC 4.0 |
| 源码 vs 产物 | 双轨：开源代码与思路；产物进 `packages/`，并打包到 Release |
| 目录布局 | 同仓 `source/` + `packages/` |
| 未提交改动 | 以可运行满意状态为准，先修配置/资产一致性再重组 |

## Target tree

```text
/
  README.md
  LICENSE
  .gitignore
  CONTRIBUTING.md
  docs/
    design/                  # 计划与设计说明（含本文件所在 specs 历史）
    guides/                  # 构建与打包说明（可选）
  source/
    codex/
      prompts/
      tools/
      references/
      frames/                # 迁移已跟踪的帧目录；本次不主动删减
      notes/
    clawd/
      tools/
      generated/README.md    # 说明生成物；大体量图默认不入仓
      notes/                 # 短笔记；完整计划见 docs/design/
  packages/
    codex-pet/               # pet.json + spritesheet.webp
    xingyu-clawd-theme/      # theme.json + assets/ (+ 精简 README)
  scripts/
    package-release.ps1
  preview/
    codex-pet.html
```

可选：`.github/ISSUE_TEMPLATE/`（bug / 素材问题）。不强制 `CODE_OF_CONDUCT` / `SECURITY`。

## Migration map

| 现状 | 去向 |
| --- | --- |
| `codex-pet/` | `packages/codex-pet/` |
| `xingyu-clawd-theme/theme.json` + `assets/` | `packages/xingyu-clawd-theme/` |
| `xingyu-clawd-theme/tools/` | `source/clawd/tools/` |
| `xingyu-clawd-theme/README.md` | `packages/xingyu-clawd-theme/README.md`（精简） |
| `pet-build/prompts`、`tools`、`references` | `source/codex/` |
| `source-images/` | 并入 `source/codex/references/`（去重） |
| `CLAWD_ANIMATION_PLAN.md` | `docs/design/clawd-animation-plan.md`，并更新文内路径 |
| `codex-pet.html` | `preview/codex-pet.html` |
| 父目录有价值的设计文 | 拷入仓库 `docs/` |
| `qa/` 大图、`generated/` 大体量源图、`__pycache__` | `.gitignore`；用 README/notes 说明本地重建 |

Git 根目录保持现有仓库根（本地名可仍为 `codex蕾米埃尔/`）；不强制重命名本地文件夹。

## Runnable alignment (before move)

当前 `theme.json` 引用但 `assets/` 缺失的文件：

- `yawning.gif`
- `dozing.gif`
- `collapsing.gif`
- `waking.gif`
- `react-annoyed.gif`

对齐策略（与已满意行为一致）：

1. `yawning` / `dozing` / `collapsing` / `sleeping` / `waking` 均指向现有 `sleeping.gif`。
2. `reactions.annoyed`：无独立资产时移除该反应配置，或在 README 标为暂缓；不以缺失文件留下断引用。
3. `scripts/package-release.ps1` 与整理验收必须校验：`theme.json` 引用的每个文件在 `assets/` 中存在；`packages/codex-pet/` 含 `pet.json` 与 `spritesheet.webp`。

对齐后将 `theme.json` 的 `version` **patch bump 为 `0.5.2`**（配置去断引用、睡眠链复用 `sleeping.gif`；无新美术也需让安装者可区分）。README 与打包脚本均以该版本为准。

## README structure

根 `README.md` 大纲：

1. 项目简介（一句话 + Codex / Clawd 双平台表）
2. 快速安装（`packages/` 路径 + Release zip）
3. 仓库结构（`source/` vs `packages/`）
4. **Codex：动画行与触发说明**
5. **Clawd on Desk：GIF 与触发逻辑**
6. 从源码理解实现（链到 `docs/`、`source/`）
7. 素材与许可（CC BY-NC 4.0 + 角色权利声明）
8. 已知问题 / 反馈渠道

### Codex trigger table

Codex 产物为 8×11 精灵图，不是每状态独立 GIF。表为状态行 → 触发：

| 行 | 状态 | 触发 / 含义 |
| --- | --- | --- |
| 0 | `idle` | 无任务、平静待机 |
| 1 | `running-right` | 向右拖拽 / 右向移动 |
| 2 | `running-left` | 向左拖拽 / 左向移动 |
| 3 | `waving` | 招呼、引起注意 |
| 4 | `jumping` | 悬停或轻快跳跃反馈 |
| 5 | `failed` | 失败、阻止或取消 |
| 6 | `waiting` | 等待批准、帮助或用户输入 |
| 7 | `running` | 任务执行中 / 处理中 |
| 8 | `review` | 结果就绪或审阅输出 |
| 9–10 | look 16 向 | 视线跟随（顺时针 16 方向） |

说明：安装产物在 `packages/codex-pet/`；构建过程在 `source/codex/`。

### Clawd on Desk trigger table

| GIF | 触发逻辑 |
| --- | --- |
| `idle-loop.gif` | 默认待机 `idle` |
| `idle-reading.gif` | 随机待机（`idleAnimations`） |
| `thinking.gif` | `thinking` |
| `editing.gif` | `working`；以及 `file-editing` 显示提示 |
| `attention.gif` | `attention` |
| `notification.gif` | `notification` |
| `carrying.gif` | `carrying` |
| `error.gif` | `error`（静态） |
| `roam.gif` | `roam`；拖拽默认 |
| `drag-left.gif` / `drag-right.gif` | 向左 / 向右拖拽 |
| `react-double.gif` | 双击反应 |
| `sleeping.gif` | 入睡链共用：`yawning` / `dozing` / `collapsing` / `sleeping` / `waking` |

表下用短列表标明暂缓能力，并链到 `docs/`，避免 README 声称未交付功能。

`packages/xingyu-clawd-theme/README.md` 仅保留安装说明 + 触发表精简版。

## License and contributing

- `LICENSE`：CC BY-NC 4.0 完整文本。
- README 许可段与 LICENSE 一致：非商业、需署名；角色与原始素材权利归原权利人；投诉走 Issue 或维护者邮箱。
- `CONTRIBUTING.md`：Issue/PR 方式；非商业衍生约束；改动画需附触发说明与帧规格；避免把大体量中间产物推进主树。

## Release packaging

`scripts/package-release.ps1`：

1. 校验 Clawd `theme.json` 引用完整性。
2. 校验 Codex 包必需文件。
3. 输出到 `dist-release/`（gitignore）：
   - `codex-pet-Remielle-vX.Y.Z.zip`
   - `xingyu-clawd-theme-vX.Y.Z.zip`
4. 版本号：Clawd 读 `theme.json` 的 `version`；Codex 与同一 Release tag 对齐（或在脚本参数中传入 tag）。

维护者手动创建 GitHub Release 并上传上述 zip。README 安装区优先写 Release，并保留从 `packages/` 复制的说明。

## Implementation order

1. 对齐 `theme.json` ↔ `assets/` 可运行。
2. 创建目标目录并迁移文件（保留 git 历史可用 `git mv` 处优先用）。
3. 添加 `LICENSE`、`.gitignore`、`CONTRIBUTING.md`、根 `README.md`；更新 docs 内路径。
4. 编写并试跑 `scripts/package-release.ps1`。
5. 验收：触发表与配置一致、引用完整、安装路径正确、忽略规则生效。

## Success criteria

- 新人能只读根 README 完成 Codex 或 Clawd 安装，并理解各动画触发条件。
- `source/` 与 `packages/` 边界清晰；clone 后无需下载 qa 大图也能安装使用。
- `theme.json` 无断引用；打包脚本在资产缺失时失败退出。
- LICENSE 为 CC BY-NC 4.0，版权声明与投诉渠道完整。
- 运行打包脚本可得到两个可上传 Release 的 zip。
