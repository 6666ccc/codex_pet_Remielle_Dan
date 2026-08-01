# Release 打包

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\package-release.ps1
```

脚本会：

1. 校验 `packages/Remielle_Dan-clawd-theme/theme.json` 引用的 GIF 均存在
2. 校验 `packages/Remielle_Dan-codex-pet/` 含 `pet.json`（`id` 必须为 `Remielle_Dan`）与 `spritesheet.webp`
3. 在 `dist-release/` 生成两个 zip（该目录已 gitignore）

然后将 zip 上传到 GitHub Release。
