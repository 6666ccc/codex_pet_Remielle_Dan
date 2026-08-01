#Requires -Version 5.1
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$CodexPkg = Join-Path $Root 'packages\Remielle_Dan-codex-pet'
$ClawdPkg = Join-Path $Root 'packages\Remielle_Dan-clawd-theme'
$OutDir = Join-Path $Root 'dist-release'
$Forbidden = 'xing' + 'yu'

function Fail([string]$Message) {
  Write-Error $Message
  exit 1
}

if (-not (Test-Path $CodexPkg)) { Fail "Missing Codex package: $CodexPkg" }
if (-not (Test-Path $ClawdPkg)) { Fail "Missing Clawd package: $ClawdPkg" }

$petJsonPath = Join-Path $CodexPkg 'pet.json'
$sheetPath = Join-Path $CodexPkg 'spritesheet.webp'
if (-not (Test-Path $petJsonPath)) { Fail "Missing pet.json" }
if (-not (Test-Path $sheetPath)) { Fail "Missing spritesheet.webp" }

$pet = Get-Content $petJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($pet.id -ne 'Remielle_Dan') {
  Fail "pet.json id must be Remielle_Dan, got '$($pet.id)'"
}

$themePath = Join-Path $ClawdPkg 'theme.json'
if (-not (Test-Path $themePath)) { Fail "Missing theme.json" }
$themeRaw = Get-Content $themePath -Raw -Encoding UTF8
$theme = $themeRaw | ConvertFrom-Json
$version = [string]$theme.version
if ([string]::IsNullOrWhiteSpace($version)) { Fail 'theme.json missing version' }

$assetsDir = Join-Path $ClawdPkg 'assets'
$gifRefs = [regex]::Matches($themeRaw, '[A-Za-z0-9_\-]+\.gif') |
  ForEach-Object { $_.Value } |
  Sort-Object -Unique

$missing = @()
foreach ($gif in $gifRefs) {
  $path = Join-Path $assetsDir $gif
  if (-not (Test-Path $path)) { $missing += $gif }
}
if ($missing.Count -gt 0) {
  Fail ("Missing GIF assets referenced by theme.json: " + ($missing -join ', '))
}

$scanRoots = @(
  (Join-Path $Root 'packages'),
  (Join-Path $Root 'source'),
  (Join-Path $Root 'preview'),
  (Join-Path $Root 'README.md'),
  (Join-Path $Root 'CONTRIBUTING.md')
)
$publicHits = @()
foreach ($rootPath in $scanRoots) {
  if (-not (Test-Path $rootPath)) { continue }
  $files = if ((Get-Item $rootPath).PSIsContainer) {
    Get-ChildItem -Path $rootPath -Recurse -File -ErrorAction SilentlyContinue
  } else {
    @(Get-Item $rootPath)
  }
  foreach ($file in $files) {
    if ($file.Extension -match '\.(png|gif|webp|jpg|jpeg)$') { continue }
    $text = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($text -and ($text -match [regex]::Escape($Forbidden))) {
      $publicHits += $file.FullName
    }
  }
}
if ($publicHits.Count -gt 0) {
  Fail ("Forbidden legacy identifier found in:`n" + ($publicHits -join "`n"))
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$codexZip = Join-Path $OutDir ("Remielle_Dan-codex-pet-v{0}.zip" -f $version)
$clawdZip = Join-Path $OutDir ("Remielle_Dan-clawd-theme-v{0}.zip" -f $version)
if (Test-Path $codexZip) { Remove-Item -Force $codexZip }
if (Test-Path $clawdZip) { Remove-Item -Force $clawdZip }

Compress-Archive -Path (Join-Path $CodexPkg '*') -DestinationPath $codexZip
Compress-Archive -Path (Join-Path $ClawdPkg '*') -DestinationPath $clawdZip

Write-Host "OK version=$version"
Write-Host "Wrote $codexZip"
Write-Host "Wrote $clawdZip"
exit 0
