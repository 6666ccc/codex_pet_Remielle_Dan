<p align="center">
  <img src="packages/Remielle_Dan-clawd-theme/assets/idle-loop.gif" width="190" alt="蕾米埃尔待机动画" />
</p>

<h1 align="center">蕾米埃尔 · Remielle Dan</h1>

<p align="center">
  一个会陪你写代码、思考和等待的粉色小天使。
  <br />
  同时提供 Codex v2 宠物包与 Clawd on Desk 动态主题。
</p>

<p align="center">
  <a href="#动态预览">动态预览</a> ·
  <a href="#安装">安装</a> ·
  <a href="#项目结构">项目结构</a> ·
  <a href="#素材与版权">素材与版权</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Codex-pet%20v2-8b5cf6?style=flat-square" alt="Codex pet v2" />
  <img src="https://img.shields.io/badge/Clawd%20on%20Desk-theme%20v0.5.5-ec4899?style=flat-square" alt="Clawd on Desk theme v0.5.5" />
  <img src="https://img.shields.io/badge/GIF-animated-f97316?style=flat-square" alt="Animated GIF" />
</p>

## 动态预览

所有预览图都直接引用仓库内的 GIF。打开 GitHub 仓库页面即可看到自动播放的动画。

<table>
  <tr>
    <td align="center" width="33%">
      <img src="packages/Remielle_Dan-clawd-theme/assets/idle-loop.gif" width="140" alt="待机" /><br />
      <strong>待机 · Idle</strong><br />
      <sub>安静陪伴，循环播放</sub>
    </td>
    <td align="center" width="33%">
      <img src="packages/Remielle_Dan-clawd-theme/assets/thinking.gif" width="140" alt="思考" /><br />
      <strong>思考 · Thinking</strong><br />
      <sub>遇到问题时认真思考</sub>
    </td>
    <td align="center" width="33%">
      <img src="packages/Remielle_Dan-clawd-theme/assets/editing.gif" width="140" alt="工作" /><br />
      <strong>工作 · Working</strong><br />
      <sub>编辑文件时专注行动</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="packages/Remielle_Dan-clawd-theme/assets/attention.gif" width="140" alt="提醒" /><br />
      <strong>提醒 · Attention</strong><br />
      <sub>有新消息需要你注意</sub>
    </td>
    <td align="center">
      <img src="packages/Remielle_Dan-clawd-theme/assets/carrying.gif" width="140" alt="搬运" /><br />
      <strong>搬运 · Carrying</strong><br />
      <sub>执行搬运或整理任务</sub>
    </td>
    <td align="center">
      <img src="packages/Remielle_Dan-clawd-theme/assets/error.gif" width="140" alt="错误" /><br />
      <strong>错误 · Error</strong><br />
      <sub>发现问题时的反馈动画</sub>
    </td>
  </tr>
</table>

### 交互动作

<p align="center">
  <img src="packages/Remielle_Dan-clawd-theme/assets/drag-left.gif" width="150" alt="向左拖拽" />
  <img src="packages/Remielle_Dan-clawd-theme/assets/drag-right.gif" width="150" alt="向右拖拽" />
</p>

<p align="center"><sub>向左拖拽 · 向右拖拽 · roam 漫游动画</sub></p>

## 你将得到什么

| 资源 | 用途 | 关键规格 |
| --- | --- | --- |
| [`Remielle_Dan-codex-pet/`](packages/Remielle_Dan-codex-pet/) | 安装到 Codex 桌面端 | `spriteVersionNumber: 2`、8 × 11 精灵图、1536 × 2288 |
| [`Remielle_Dan-clawd-theme/`](packages/Remielle_Dan-clawd-theme/) | 安装到 Clawd on Desk | 10 个 GIF、状态映射、拖拽反馈、睡眠流程 |
| [`preview/codex-pet.html`](preview/codex-pet.html) | 本地查看 Codex 动作 | 支持点击切换 6 组参考动画 |

## 安装

### Codex v2 宠物包

将 [`packages/Remielle_Dan-codex-pet/`](packages/Remielle_Dan-codex-pet/) 中的 `pet.json` 与 `spritesheet.webp` 放入 Codex 的宠物目录，并确保两个文件位于同一层级：

```text
%USERPROFILE%\.codex\pets\Remielle_Dan\
├── pet.json
└── spritesheet.webp
```

完成后完全退出并重新启动 Codex。

### Clawd on Desk 主题

将 [`packages/Remielle_Dan-clawd-theme/`](packages/Remielle_Dan-clawd-theme/) 整个目录复制到 Clawd on Desk 的主题目录：

```text
%APPDATA%\clawd-on-desk\themes\Remielle_Dan-clawd-theme\
├── theme.json
└── assets\
    ├── idle-loop.gif
    ├── thinking.gif
    ├── editing.gif
    └── ...
```

重新启动 Clawd on Desk，然后在「设置 → Theme」中选择蕾米埃尔主题。

## 状态映射

Clawd 主题把桌面状态映射到独立的动图资源：

| 状态 | 动画 | 触发场景 |
| --- | --- | --- |
| `idle` | `idle-loop.gif` | 默认待机 |
| `thinking` | `thinking.gif` | 思考或等待结果 |
| `working` | `editing.gif` | 编辑文件 |
| `roam` | `roam.gif` | 自主漫游 |
| `attention` / `notification` | `attention.gif` / `notification.gif` | 提醒或新通知 |
| `carrying` | `carrying.gif` | 拖拽或搬运 |
| `error` | `error.gif` | 任务异常 |
| `drag` | `drag-left.gif` / `drag-right.gif` | 向左或向右拖拽 |

## 两个版本的动画差异

Codex v2 图集规定每个标准动作使用固定帧数，因此需要从原始高帧 GIF 中选取代表帧。Codex 版本更适合其内置宠物状态系统，但单个动作的动画帧数和节奏会受到精灵图规格限制。

Clawd on Desk 支持每个状态引用独立 GIF，因此可以保留更多原始帧，并为提醒、搬运、随机待机、工作状态和完整睡眠流程提供单独动画。

## 项目结构

```text
.
├── packages/
│   ├── Remielle_Dan-codex-pet/       # Codex v2 宠物包
│   └── Remielle_Dan-clawd-theme/     # Clawd on Desk 主题与 GIF
├── preview/codex-pet.html             # Codex 动画本地预览
├── source/codex/                      # 精灵图帧、参考 GIF 与构建素材
└── scripts/                           # 打包与发布脚本
```

### Codex 资源

- [`packages/Remielle_Dan-codex-pet/`](packages/Remielle_Dan-codex-pet/)：可直接安装的 Codex v2 宠物包，包含 `pet.json`、`spritesheet.webp` 与验证结果。
- `source/codex/frames/`：精灵图的动作帧，包括待机、移动、挥手、跳跃、失败、等待、工作和检查等状态。
- `source/codex/references/`：制作过程中使用的原始 GIF、参考图和布局指南。

### Clawd on Desk 资源

- [`packages/Remielle_Dan-clawd-theme/theme.json`](packages/Remielle_Dan-clawd-theme/theme.json)：Clawd on Desk 主题配置，当前版本为 `0.5.5`。
- [`packages/Remielle_Dan-clawd-theme/assets/`](packages/Remielle_Dan-clawd-theme/assets/)：可直接运行的 GIF 动画资源。
- `source/clawd/tools/`：移动动画、单动作、睡眠流程和接触表等构建工具。

## 功能概览

### Codex

- 使用 `spriteVersionNumber: 2` 的 8 × 11 精灵图，尺寸为 1536 × 2288。
- 包含待机、移动、挥手、跳跃、失败、等待、工作和检查等标准状态。
- 支持 16 个视线方向，并通过 `validation.json` 对透明边缘和图集单元进行检查。

### Clawd on Desk

- 保留待机、思考和编辑状态的独立高帧 GIF 动画。
- 提供左右拖拽、漫游、提醒、错误、搬运和通知反馈。
- 支持随机待机、工作状态、睡眠与唤醒等桌面陪伴流程。
- 主题当前版本为 `0.5.5`。

## 本地预览

在仓库根目录运行一个静态文件服务器：

```powershell
python -m http.server 8000
```

然后打开 <http://localhost:8000/preview/codex-pet.html>，点击宠物或按钮切换动作。

## 已知行为

部分 Codex 桌面版本在任务刚开始运行时不会立刻刷新悬浮宠物动画。可以将鼠标移入宠物区域后再移出，或收起并重新唤出宠物，让桌面端重新同步状态；这属于桌面端状态刷新行为，不是资源包的精灵图错误。

## 素材与版权

本项目中的角色形象、原始 GIF 与相关素材版权归原作者或相应权利人所有。本仓库仅用于个人学习、技术研究与非商业交流，不主张拥有原始角色形象或素材的所有权。

如果你认为仓库中的内容侵犯了合法权益，请通过 [Issue](https://github.com/6666ccc/codex_pet_Remielle_Dan/issues) 或 [邮件](mailto:liuchang12322@outlook.com) 联系维护者。收到通知后会及时核实并妥善处理。

<p align="center">
  <sub>Made with care for a calmer coding desk · Remielle Dan</sub>
</p>
