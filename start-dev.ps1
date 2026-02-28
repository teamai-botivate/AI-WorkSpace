<#
.SYNOPSIS
    Botivate AI Workspace — Development Launcher
    Reads workspace.config.json and starts all services dynamically.
    
.DESCRIPTION
    This script reads the master config and launches:
    1. Each active agent's backend server
    2. Each active agent's frontend server  
    3. The gateway backend
    4. The main frontend shell
    
    No hardcoded ports or paths — everything comes from config.

.USAGE
    .\start-dev.ps1           # Start all services
    .\start-dev.ps1 -Stop     # Stop all background services
#>

param(
    [switch]$Stop
)

$ErrorActionPreference = "Continue"
$WorkspaceRoot = $PSScriptRoot
if (-not $WorkspaceRoot) { $WorkspaceRoot = Get-Location }

$ConfigPath = Join-Path $WorkspaceRoot "config\workspace.config.json"

# ── Banner ────────────────────────────────────────────────

function Show-Banner {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║                                          ║" -ForegroundColor Cyan
    Write-Host "  ║   🚀  BOTIVATE AI WORKSPACE              ║" -ForegroundColor Cyan
    Write-Host "  ║   Development Launcher                   ║" -ForegroundColor Cyan
    Write-Host "  ║                                          ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# ── Stop Mode ─────────────────────────────────────────────

if ($Stop) {
    Write-Host "🛑 Stopping all Botivate services..." -ForegroundColor Yellow
    Get-Process -Name "python", "uvicorn", "node" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "   Stopping $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ All services stopped." -ForegroundColor Green
    exit 0
}

# ── Load Config ───────────────────────────────────────────

Show-Banner

if (-not (Test-Path $ConfigPath)) {
    Write-Host "❌ Config not found: $ConfigPath" -ForegroundColor Red
    exit 1
}

$Config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$WorkspaceName = $Config.workspace.name
$GatewayPort = $Config.gateway.port

Write-Host "📋 Workspace: $WorkspaceName v$($Config.workspace.version)" -ForegroundColor White
Write-Host "📦 Agents registered: $($Config.agents.Count)" -ForegroundColor White
Write-Host ""

# ── Start Agent Services ──────────────────────────────────

foreach ($agent in $Config.agents) {
    if ($agent.status -ne "active") {
        Write-Host "⏭️  Skipping '$($agent.name)' (status: $($agent.status))" -ForegroundColor DarkGray
        continue
    }

    Write-Host "┌─ Starting: $($agent.name)" -ForegroundColor Yellow

    # Start Backend (skip if deployed remotely)
    if ($agent.backend.deployed -eq $true) {
        Write-Host "│  ☁️  Backend  → DEPLOYED at $($agent.backend.deployedUrl)" -ForegroundColor Cyan
    } else {
        $backendDir = Join-Path $WorkspaceRoot $agent.backend.workDir
        if (Test-Path $backendDir) {
            $backendCmd = $agent.backend.startCommand
            $venvPath = if ($agent.backend.activateVenv) { 
                Join-Path $WorkspaceRoot $agent.backend.activateVenv 
            } else { $null }

            $startScript = ""
            if ($venvPath -and (Test-Path $venvPath)) {
                $startScript = "cd '$backendDir'; & '$venvPath'; $backendCmd"
            } else {
                $startScript = "cd '$backendDir'; $backendCmd"
            }

            Start-Process powershell -ArgumentList "-NoExit", "-Command", $startScript -WindowStyle Minimized
            Write-Host "│  ✅ Backend  → port $($agent.backend.port)" -ForegroundColor Green
        } else {
            Write-Host "│  ⚠️  Backend dir not found: $backendDir" -ForegroundColor DarkYellow
        }
    }

    # Start Frontend
    $frontendDir = Join-Path $WorkspaceRoot $agent.frontend.workDir
    if (Test-Path $frontendDir) {
        $frontendCmd = $agent.frontend.startCommand

        # Set environment variables if defined
        $envSetup = ""
        if ($agent.frontend.env) {
            $agent.frontend.env.PSObject.Properties | ForEach-Object {
                $envSetup += "`$env:$($_.Name) = '$($_.Value)'; "
            }
        }

        $startScript = "cd '$frontendDir'; $envSetup$frontendCmd"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $startScript -WindowStyle Minimized
        Write-Host "│  ✅ Frontend → port $($agent.frontend.port) ($($agent.frontend.url))" -ForegroundColor Green
    } else {
        Write-Host "│  ⚠️  Frontend dir not found: $frontendDir" -ForegroundColor DarkYellow
    }

    Write-Host "└─ Done" -ForegroundColor DarkGray
    Write-Host ""
}

# ── Start Gateway Backend ─────────────────────────────────

Write-Host "┌─ Starting: Gateway Backend" -ForegroundColor Cyan
$gatewayDir = Join-Path $WorkspaceRoot "backend"
if (Test-Path $gatewayDir) {
    $gatewayCmd = "cd '$gatewayDir'; uvicorn app.main:app --port $GatewayPort --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $gatewayCmd -WindowStyle Minimized
    Write-Host "│  ✅ Gateway  → port $GatewayPort (http://localhost:$GatewayPort/docs)" -ForegroundColor Green
} else {
    Write-Host "│  ⚠️  Gateway dir not found" -ForegroundColor DarkYellow
}
Write-Host "└─ Done" -ForegroundColor DarkGray
Write-Host ""

# ── Start Main Frontend ───────────────────────────────────

Write-Host "┌─ Starting: Main Frontend (Shell)" -ForegroundColor Magenta
$frontendShellDir = Join-Path $WorkspaceRoot "frontend"
if (Test-Path (Join-Path $frontendShellDir "package.json")) {
    Write-Host "│  ✅ Frontend → port 3000 (http://localhost:3000)" -ForegroundColor Green
    Write-Host "└─ Opening in this terminal..." -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  🌐  Open http://localhost:3000 in your browser" -ForegroundColor White
    Write-Host "  📡  Gateway: http://localhost:$GatewayPort/docs" -ForegroundColor White
    Write-Host "  🛑  Stop all: .\start-dev.ps1 -Stop" -ForegroundColor White
    Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    Set-Location $frontendShellDir
    npm run dev
} else {
    Write-Host "│  ❌ Frontend not initialized. Run: cd frontend; npm install" -ForegroundColor Red
    Write-Host "└─ Aborted" -ForegroundColor DarkGray
}
