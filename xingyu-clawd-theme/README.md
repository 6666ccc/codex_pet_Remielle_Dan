# 蕾米埃尔 · Clawd

这是一个独立的 Clawd on Desk 自定义主题，不修改 `codex蕾米埃尔` 或 `xingyu-pet-run` 中的 Codex 宠物资源。

## 设计原则

- 保留原始 GIF 的完整动画，而不是使用 Codex 精灵图中每个状态压缩后的 8 帧。
- 状态资产按 Clawd 的独立文件格式组织：GIF 待机、随机张望、阅读、思考、编辑文件、检查更新、提醒、上下文整理、工作树搬运、错误、完成、完整休眠和左右漫游。
- 支持拖拽方向动画、左右双击、连续四击和被惹恼反应。
- 为避免额外眼点和主题缓存兼容问题，待机直接使用原始 `待机中.gif`，并关闭 SVG 视线跟随。
- `file-editing` 是为 Codex 的 `apply_patch` / `Edit` / `Write` 工具预留的显示提示；启用对应 hook 细分后，文件编辑会使用 `editing.gif`。
- `idle-loop.gif`、`thinking.gif`、`editing.gif` 已移除旧素材最外层的浅白/淡蓝描边垫层，使深色细线直接贴合透明边界，与新版移动动画的轮廓结构一致；原动作帧和节奏不变。

## 安装

将整个 `xingyu-clawd-theme` 目录复制到：

`%APPDATA%\clawd-on-desk\themes\xingyu-clawd-theme\`

然后在 Clawd on Desk 的“设置 → Theme”中选择“蕾米埃尔 · Clawd”。

## 当前状态映射

| Clawd 状态 | 动画 |
| --- | --- |
| `idle` | `idle-loop.gif`（复用 `待机中.gif`，61 帧） |
| 随机待机 | `idle-look.gif`（张望）与 `idle-reading.gif`（阅读），均为 16 帧 |
| `thinking` | `thinking.gif`（41 帧） |
| `working` / 编辑文件 | `editing.gif`（17 帧） |
| 检查更新 | `update-checking.gif`（16 帧，通过 `updateVisuals.checking` 接入） |
| `attention` | `attention.gif`（31 帧） |
| `notification` | `notification.gif`（16 帧独立批准/输入提醒动作，130ms/帧） |
| `sweeping` | `sweeping.gif`（16 帧上下文清扫整理动作，140ms/帧） |
| `carrying` | `carrying.gif`（16 帧工作树物品搬运动作，140ms/帧） |
| `error` | `error.gif` |
| `yawning / dozing / collapsing / sleeping / waking` | 完整入睡流程；睡眠循环使用新制作的 16 个独立动作帧 |
| `roam` | `roam.gif`（连贯 16 帧移动循环，110ms/帧，左右方向分别提供） |
