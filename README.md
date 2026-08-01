# 蕾米埃尔（Remielle_Dan）

基于官方公开发布 GIF 素材制作的自定义宠物「蕾米埃尔」。角色保留粉色头发、星形发饰、小翅膀和设备道具等主要外观特征。

本仓库同时提供两套相互独立、可以共存的资源：

| 使用平台 | 可安装资源 | 动画形式 | 入口 |
| --- | --- | --- | --- |
| Codex | Codex v2 宠物包 | 8×11 精灵图 | [`packages/Remielle_Dan-codex-pet/`](packages/Remielle_Dan-codex-pet/) |
| Clawd on Desk | 自定义主题 v0.5.2 | 独立高帧 GIF | [`packages/Remielle_Dan-clawd-theme/`](packages/Remielle_Dan-clawd-theme/) |

## 快速安装

优先从 [GitHub Releases](https://github.com/6666ccc/codex_pet_Remielle_Dan/releases) 下载 zip；也可以直接使用仓库内 `packages/`。

### 安装到 Codex

将 `packages/Remielle_Dan-codex-pet/` 中的 `pet.json` 和 `spritesheet.webp` 复制到：

```text
%USERPROFILE%\.codex\pets\Remielle_Dan\
```

完成后完全退出并重新启动 Codex。

也可以把下面内容发给 Codex 协助安装：

> 请阅读并下载 [codex_pet_Remielle_Dan](https://github.com/6666ccc/codex_pet_Remielle_Dan) 项目，将 `packages/Remielle_Dan-codex-pet` 中的 `pet.json` 和 `spritesheet.webp` 安装到 `%USERPROFILE%\.codex\pets\Remielle_Dan\`，验证文件完整后告诉我是否需要重启 Codex。

### 安装到 Clawd on Desk

将整个 `packages/Remielle_Dan-clawd-theme/` 目录复制到：

```text
%APPDATA%\clawd-on-desk\themes\Remielle_Dan-clawd-theme\
```

重新启动 Clawd on Desk，然后在「设置 → Theme」中选择「蕾米埃尔 · Clawd」。

本地打包 Release 附件：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package-release.ps1
```

## 仓库结构

| 路径 | 说明 |
| --- | --- |
| `packages/` | 可直接安装的产物 |
| `source/` | 实现代码、提示词、参考图与构建工具 |
| `docs/` | 设计说明与打包指南 |
| `scripts/` | Release 打包脚本 |
| `preview/` | 本地预览页 |

## Codex：动画行与触发说明

Codex 产物是一张 `spriteVersionNumber: 2` 的 8×11 精灵图（`spritesheet.webp`），不是每个状态一个独立 GIF。

| 行 | 状态 | 触发 / 含义 |
| --- | --- | --- |
| 0 | `idle` | 无任务、平静待机（呼吸/眨眼循环） |
| 1 | `running-right` | 向右拖拽 / 右向移动 |
| 2 | `running-left` | 向左拖拽 / 左向移动 |
| 3 | `waving` | 招呼、引起注意 |
| 4 | `jumping` | 悬停或轻快跳跃反馈 |
| 5 | `failed` | 任务失败、被阻止或取消 |
| 6 | `waiting` | 等待批准、帮助或用户输入 |
| 7 | `running` | 任务执行中 / 处理中 |
| 8 | `review` | 结果就绪或审阅完成输出 |
| 9–10 | look 16 向 | 视线跟随（顺时针 16 方向） |

构建过程与提示词见 `source/codex/`。

## Clawd on Desk：GIF 与触发逻辑

| GIF | 触发逻辑 |
| --- | --- |
| `idle-loop.gif` | 默认待机 `idle` |
| `idle-reading.gif` | 随机待机（`idleAnimations`，约 10s） |
| `thinking.gif` | 思考中 `thinking` |
| `editing.gif` | 工作中 `working`；以及 `file-editing` 显示提示（编辑文件） |
| `attention.gif` | 需要关注 `attention` |
| `notification.gif` | 通知 / 等待用户确认 `notification` |
| `carrying.gif` | 搬运 / 上下文整理类 `carrying` |
| `error.gif` | 错误 `error`（静态） |
| `roam.gif` | 漫游 `roam`；拖拽默认也可使用 |
| `drag-left.gif` / `drag-right.gif` | 向左 / 向右拖拽 |
| `react-double.gif` | 双击反应 |
| `sleeping.gif` | 入睡链共用：`yawning` / `dozing` / `collapsing` / `sleeping` / `waking` |

### 暂缓 / 未交付

以下能力不在当前 v0.5.2 安装包中（详见 [`docs/design/clawd-animation-plan.md`](docs/design/clawd-animation-plan.md)）：

- 独立 `react-annoyed`、独立 `sweeping`、`update-checking`
- SVG 视线跟随、Mini Mode、子代理分级动作

## 从源码理解实现

- Codex 提示词与帧：`source/codex/`
- Clawd 构建工具：`source/clawd/tools/`
- 动画阶段计划：`docs/design/clawd-animation-plan.md`
- 开源骨架设计：`docs/superpowers/specs/2026-08-01-open-source-skeleton-design.md`

## 两个版本的动画差异

Codex v2 图集规定每个标准动作使用固定帧数，因此需要从原始高帧 GIF 中选取代表帧。Clawd on Desk 支持每个状态引用独立 GIF，可保留更多原始帧并为提醒、搬运、随机待机与入睡流程提供单独动画。

## Codex 已知问题

在 Codex 桌面端 `26.721.4979.0` 中，任务开始运行后，浮动宠物窗口有时仍会继续显示普通待机动作；将鼠标移入宠物区域后再移出，窗口才会刷新为正确的运行中动作。

该现象可能与 Codex 桌面端 `avatarOverlay` 的任务状态订阅或重新渲染有关，并非本宠物包的状态映射或精灵图错误。临时可以：

- 将鼠标移入宠物区域后再移出
- 收起宠物，然后重新唤出
- 完全退出并重新启动 Codex
- 等待 Codex 桌面端后续版本改进浮动窗口的状态刷新机制

## 素材与许可

本项目采用 [CC BY-NC 4.0](LICENSE)（署名-非商业性使用 4.0 国际）。

图像素材基于官方公开发布的 GIF 制作，仅供个人学习、技术研究及非商业交流使用。原始角色形象及相关素材的著作权归原作者或相应权利人所有；本项目不主张对原始角色形象或相关素材拥有所有权。

如果您认为本项目中的内容侵犯了您的合法权益，请提供必要的权属说明并通过以下任一方式联系维护者：

- 在本仓库提交 [Issue](https://github.com/6666ccc/codex_pet_Remielle_Dan/issues)
- 发送邮件至 [liuchang12322@outlook.com](mailto:liuchang12322@outlook.com)

改进建议与使用反馈也欢迎通过 Issue 或电子邮件交流。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。
