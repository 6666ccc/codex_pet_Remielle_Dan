# 贡献指南

感谢关注「蕾米埃尔 / Remielle_Dan」宠物资源仓库。

## 反馈方式

- 使用问题：请开 [Issue](https://github.com/6666ccc/codex_pet_Remielle_Dan/issues)
- 版权投诉：请在 Issue 中说明权属，或发送邮件至 liuchang12322@outlook.com

## 提交改动前请注意

1. 本仓库采用 **CC BY-NC 4.0**（非商业、需署名）。请勿提交主要用于商业用途的衍生内容。
2. 角色形象与原始官方素材的著作权归原权利人；请勿引入可能侵权的第三方素材。
3. **不要**在公开路径中使用任何旧内部代号；统一使用 `Remielle_Dan`。
4. 可安装产物放在 `packages/`；构建脚本与提示词放在 `source/`；大体量 QA / 生成中间图不要推进主树（见 `.gitignore`）。
5. 修改动画时，请在 PR / Issue 中说明：
   - 对应平台（Codex 或 Clawd on Desk）
   - 触发条件
   - 画布尺寸、帧数、每帧时长（如适用）

## 建议工作流

1. Fork 并创建分支
2. 本地验证：`packages/` 配置引用完整；可运行 `scripts/package-release.ps1`
3. 打开 Pull Request，简述动机与验证步骤
