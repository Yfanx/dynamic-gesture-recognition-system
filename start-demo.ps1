$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$LogDir = Join-Path $Root ".logs"
$BackendLog = Join-Path $LogDir "backend.log"
$FrontendLog = Join-Path $LogDir "frontend.log"
$BackendUrl = "http://127.0.0.1:8000"
$FrontendUrl = "http://127.0.0.1:5173"

function Write-Step {
    param([string]$Message)
    Write-Host "[dynamic-gesture] $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-PortOpen {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return [bool]$connection
}

function Wait-Http {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3 | Out-Null
            return $true
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (-not (Test-Path $BackendDir)) {
    throw "Backend directory not found: $BackendDir"
}
if (-not (Test-Path $FrontendDir)) {
    throw "Frontend directory not found: $FrontendDir"
}
if (-not (Test-Command "uv")) {
    throw "uv was not found. Install it with Scoop first: scoop install uv"
}
if (-not (Test-Command "pnpm.cmd")) {
    throw "pnpm.cmd was not found. Enable pnpm/corepack or install pnpm first."
}

Write-Step "Checking backend dependencies"
Push-Location $BackendDir
try {
    uv sync | Tee-Object -FilePath $BackendLog
} finally {
    Pop-Location
}

Write-Step "Checking frontend dependencies"
Push-Location $FrontendDir
try {
    if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
        pnpm.cmd install | Tee-Object -FilePath $FrontendLog
    }
} finally {
    Pop-Location
}

if (Test-PortOpen 8000) {
    Write-Step "Backend already listening on $BackendUrl"
} else {
    Write-Step "Starting backend on $BackendUrl"
    Start-Process -WindowStyle Hidden `
        -FilePath "uv" `
        -ArgumentList @("run", "python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $BackendDir `
        -RedirectStandardOutput $BackendLog `
        -RedirectStandardError $BackendLog
}

if (Test-PortOpen 5173) {
    Write-Step "Frontend already listening on $FrontendUrl"
} else {
    Write-Step "Starting frontend on $FrontendUrl"
    Start-Process -WindowStyle Hidden `
        -FilePath "pnpm.cmd" `
        -ArgumentList @("run", "dev") `
        -WorkingDirectory $FrontendDir `
        -RedirectStandardOutput $FrontendLog `
        -RedirectStandardError $FrontendLog
}

Write-Step "Waiting for backend"
if (-not (Wait-Http "$BackendUrl/api/model" 60)) {
    Write-Warning "Backend did not become ready in time. Check $BackendLog"
}

Write-Step "Waiting for frontend"
if (-not (Wait-Http $FrontendUrl 60)) {
    Write-Warning "Frontend did not become ready in time. Check $FrontendLog"
}

Write-Step "Opening $FrontendUrl"
Start-Process $FrontendUrl

Write-Host ""
Write-Host "Demo is starting." -ForegroundColor Green
Write-Host "Frontend: $FrontendUrl"
Write-Host "Backend:  $BackendUrl"
Write-Host "Logs:     $LogDir"
Write-Host ""
Write-Host "Press any key to close this window. Services keep running in the background."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
