<#
    Claude RTL — one-command updater.

    Downloads the latest release and installs it over the existing copy.
    Settings and history live in %APPDATA%\ClaudeRTL and are never touched.

    Usage:
        irm https://raw.githubusercontent.com/sadekdesign/claude-rtl/master/update.ps1 | iex
#>

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo    = 'sadekdesign/claude-rtl'
$AppId   = '{E3A7F2D1-8B4C-4D5E-9F6A-1C2D3E4F5A6B}_is1'
$AppName = 'Claude RTL'

function Say($msg)  { Write-Host "  $msg" }
function Warn($msg) { Write-Host "  $msg" -ForegroundColor Yellow }
function Die($msg)  { Write-Host "  $msg" -ForegroundColor Red; exit 1 }

Write-Host ''
Write-Host "  $AppName — update" -ForegroundColor Cyan
Write-Host ''

# ── 1. what is installed now ──────────────────────────────────────────────
$installed = $null
$installDir = $null
foreach ($root in 'HKCU:', 'HKLM:') {
    $key = "$root\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppId"
    if (Test-Path $key) {
        $info = Get-ItemProperty $key
        $installed = $info.DisplayVersion
        $installDir = $info.InstallLocation
        break
    }
}
if ($installed) { Say "installed: v$installed" } else { Say 'installed: not found (fresh install)' }

# ── 2. what is available ──────────────────────────────────────────────────
Say 'checking for a new release...'
try {
    $release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest" `
        -Headers @{ 'User-Agent' = 'ClaudeRTL-Updater' }
} catch {
    Die "could not reach GitHub: $($_.Exception.Message)"
}

$latest = ($release.tag_name -replace '^v', '')
$asset = $release.assets | Where-Object { $_.name -like '*.exe' } | Select-Object -First 1
if (-not $asset) { Die "release $($release.tag_name) has no .exe attached" }

Say "latest:    v$latest"

# لو أي من الرقمين شكله غريب، كمّل وحدّث بدل ما توقف
$upToDate = $false
if ($installed) {
    try {
        $have = [version](($installed -replace '[^\d.]', '').Trim('.'))
        $want = [version](($latest    -replace '[^\d.]', '').Trim('.'))
        $upToDate = ($have -ge $want)
    } catch {
        $upToDate = $false
    }
}
if ($upToDate) {
    Write-Host ''
    Say 'already up to date.'
    Write-Host ''
    exit 0
}

# ── 3. download ───────────────────────────────────────────────────────────
$setup = Join-Path $env:TEMP $asset.name
Say "downloading $($asset.name) ($([math]::Round($asset.size / 1MB, 1)) MB)..."
$progress = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'   # الشريط بيبطّأ التنزيل جداً
try {
    Invoke-WebRequest $asset.browser_download_url -OutFile $setup -UseBasicParsing
} catch {
    Die "download failed: $($_.Exception.Message)"
} finally {
    $ProgressPreference = $progress
}

# ── 4. close the running copy ─────────────────────────────────────────────
$running = Get-Process ClaudeRTL -ErrorAction SilentlyContinue
if ($running) {
    Say 'closing the running copy...'
    $running | Stop-Process -Force
    Start-Sleep -Milliseconds 600
}

# ── 5. install over the old one ───────────────────────────────────────────
Say 'installing...'
$proc = Start-Process $setup -ArgumentList '/SILENT', '/NORESTART', '/SUPPRESSMSGBOXES' -Wait -PassThru
if ($proc.ExitCode -ne 0) { Die "installer exited with code $($proc.ExitCode)" }
Remove-Item $setup -ErrorAction SilentlyContinue

# ── 6. start it again ─────────────────────────────────────────────────────
if (-not $installDir) {
    foreach ($root in 'HKCU:', 'HKLM:') {
        $key = "$root\Software\Microsoft\Windows\CurrentVersion\Uninstall\$AppId"
        if (Test-Path $key) { $installDir = (Get-ItemProperty $key).InstallLocation; break }
    }
}
$exe = if ($installDir) { Join-Path $installDir 'ClaudeRTL.exe' } else { $null }
if ($exe -and (Test-Path $exe)) {
    Start-Process $exe
    Say 'started.'
} else {
    Warn 'installed, but could not find the exe to start it — launch it from the Start menu.'
}

Write-Host ''
Write-Host "  done — now on v$latest" -ForegroundColor Green
Write-Host '  Settings and history were kept (%APPDATA%\ClaudeRTL).'
Write-Host ''
