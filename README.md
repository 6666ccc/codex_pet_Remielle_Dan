# 蕾米埃尔宠物

基于官方公开发布的 GIF 素材制作的自定义宠物「蕾米埃尔」。

| 使用平台 | 可安装资源 | 动画形式 | 入口 |
| --- | --- | --- | --- |
| Codex | Codex v2 宠物包 | 8×11 精灵图，标准动作固定 8 帧 | [`codex-pet/`](codex-pet/) |
| Clawd on Desk | 自定义主题 v0.5.1 | 独立高帧 GIF 与状态动画 | [`xingyu-clawd-theme/`](xingyu-clawd-theme/) |

## 仓库结构

### Codex 资源

- `codex-pet/`：可直接安装的 Codex 宠物包，包含 `pet.json` 和 `spritesheet.webp`。
- `pet-build/`：Codex v2 宠物的完整构建过程，包括动作行、提示词、质量检查结果和最终图集。
- `source-images/`：制作过程中使用的原始 GIF 素材与参考图。
- `codex-pet.html`：用于查看 Codex 宠物动画的本地预览页面。

### Clawd on Desk 资源

- `xingyu-clawd-theme/theme.json`：Clawd on Desk 主题配置。
- `xingyu-clawd-theme/assets/`：可直接运行的 GIF 动画资源。
- `xingyu-clawd-theme/generated/`：动画生成源图、透明化素材和提示词。
- `xingyu-clawd-theme/qa/`：帧数、节奏、透明边缘和接触表等检查结果。
- `xingyu-clawd-theme/tools/`：移动动画、单动作、接触表和轮廓修复的构建工具。
- `CLAWD_ANIMATION_PLAN.md`：Clawd 动画开发计划、完成状态与暂缓项目。

## 功能概览

### Codex

- 使用 `spriteVersionNumber: 2` 的 1536×2288 图集。
- 包含 9 组标准状态动画和 16 个视线方向。
- 已映射待机、移动、挥手、跳跃、失败、等待、工作和检查等状态。

### Clawd on Desk

- 保留待机、思考和编辑状态的原始高帧节奏。
- 提供 16 帧、110ms/帧的左右移动动画。
- 提供独立的提醒、错误、上下文整理和工作树搬运动作。
- 提供随机张望、随机阅读和检查更新动画。
- 提供打哈欠、犯困、倒下、睡眠和醒来的完整入睡流程。
- 提供基础拖拽、点击、双击和 annoyed 反应。
- 主题当前版本为 `0.5.1`。

## 安装

### 安装到 Codex

将 `codex-pet/` 中的 `pet.json` 和 `spritesheet.webp` 复制到：

```text
%USERPROFILE%\.codex\pets\xingyu\
```

复制完成后，完全退出并重新启动 Codex。

也可以将下面的内容发送给 Codex，让它协助安装：

> 请阅读并下载 [codex_pet_Remielle_Dan](https://github.com/6666ccc/codex_pet_Remielle_Dan) 项目，将 `codex-pet` 中的 `pet.json` 和 `spritesheet.webp` 安装到 `%USERPROFILE%\.codex\pets\xingyu\`，验证文件完整后告诉我是否需要重启 Codex。

### 安装到 Clawd on Desk

将整个 `xingyu-clawd-theme/` 目录复制到：

```text
%APPDATA%\clawd-on-desk\themes\xingyu-clawd-theme\
```

重新启动 Clawd on Desk，然后在“设置 → Theme”中选择“蕾米埃尔 · Clawd”。

## 两个版本的动画差异

Codex v2 图集规定每个标准动作使用固定帧数，因此需要从原始高帧 GIF 中选取代表帧。Codex 版本更适合其内置宠物状态系统，但动画流畅度可能低于原始素材。

Clawd on Desk 支持每个状态引用独立 GIF，因此可以保留更多原始帧，并为提醒、清扫、搬运、随机待机、更新检查和完整睡眠流程提供单独动画。

## Codex 已知问题

在 Codex 桌面端 `26.721.4979.0` 中，任务开始运行后，浮动宠物窗口有时仍会继续显示普通待机动作；将鼠标移入宠物区域后再移出，窗口才会刷新为正确的运行中动作。

该现象可能与 Codex 桌面端 `avatarOverlay` 的任务状态订阅或重新渲染有关，并非本宠物包的状态映射或精灵图错误。临时可以：

- 将鼠标移入宠物区域后再移出。
- 收起宠物，然后重新唤出。
- 完全退出并重新启动 Codex。
- 等待 Codex 桌面端后续版本改进浮动窗口的状态刷新机制。

## 素材与版权说明

本项目使用的图像素材基于官方公开发布的 GIF 制作，仅供个人学习、技术研究及非商业交流使用，不收取任何费用。

原始角色形象及相关素材的著作权归原作者或相应权利人所有。本项目不主张对原始角色形象或相关素材拥有所有权。

如果您认为本项目中的内容侵犯了您的合法权益，请提供必要的权属说明并通过以下任一方式联系维护者：

- 在本仓库提交 [Issue](https://github.com/6666ccc/codex_pet_Remielle_Dan/issues)
- 发送邮件至 [liuchang12322@outlook.com](mailto:liuchang12322@outlook.com)

收到通知后，项目维护者将及时核实并妥善处理。改进建议、使用反馈或新想法也欢迎通过 Issue 或电子邮件交流。
