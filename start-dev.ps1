<#
.SYNOPSIS
    Botivate AI Workspace - Development Launcher
    Reads workspace.config.json and starts all services dynamically.

.DESCRIPTION
    This script reads the master config and launches:
    1. Each active agent's backend server
    2. Each active agent's frontend server
    3. The gateway backend
    4. The main frontend shell

    No hardcoded ports or paths - everything comes from config.

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

# -- Banner --

function Show-Banner {
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "      BOTIVATE AI WORKSPACE               " -ForegroundColor Cyan
    Write-Host "      Development Launcher                " -ForegroundColor Cyan
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
}

# -- Stop Mode --

if ($Stop) {
    Write-Host "[STOP] Stopping all Botivate services..." -ForegroundColor Yellow
    Get-Process -Name "python", "uvicorn", "node" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "   Stopping $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] All services stopped." -ForegroundColor Green
    exit 0
}

# -- Load Config --

Show-Banner

if (-not (Test-Path $ConfigPath)) {
    Write-Host "[ERROR] Config not found: $ConfigPath" -ForegroundColor Red
    exit 1
}

$Config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$WorkspaceName = $Config.workspace.name
$GatewayPort = $Config.gateway.port

Write-Host "[INFO] Workspace: $WorkspaceName v$($Config.workspace.version)" -ForegroundColor White
Write-Host "[INFO] Agents registered: $($Config.agents.Count)" -ForegroundColor White
Write-Host ""

# -- Start Agent Services --

foreach ($agent in $Config.agents) {
    if ($agent.status -ne "active") {
        Write-Host "[SKIP] '$($agent.name)' (status: $($agent.status))" -ForegroundColor DarkGray
        continue
    }

    Write-Host "[AGENT] Starting: $($agent.name)" -ForegroundColor Yellow

    # Start Backend (skip if deployed remotely)
    if ($agent.backend.deployed -eq $true) {
        Write-Host "   [CLOUD] Backend -> DEPLOYED at $($agent.backend.deployedUrl)" -ForegroundColor Cyan
    } else {
        $backendDir = Join-Path $WorkspaceRoot $agent.backend.workDir
        if (Test-Path $backendDir) {
            $backendCmd = $agent.backend.startCommand
            $venvActivate = $null
            if ($agent.backend.activateVenv) {
                $venvActivate = Join-Path $WorkspaceRoot $agent.backend.activateVenv
            }

            if ($venvActivate -and (Test-Path $venvActivate)) {
                $startScript = "Set-Location '$backendDir'; & '$venvActivate'; $backendCmd"
            } else {
                $startScript = "Set-Location '$backendDir'; $backendCmd"
            }

            Start-Process powershell -ArgumentList "-NoExit", "-Command", $startScript -WindowStyle Minimized
            Write-Host "   [OK] Backend  -> port $($agent.backend.port)" -ForegroundColor Green
        } else {
            Write-Host "   [WARN] Backend dir not found: $backendDir" -ForegroundColor DarkYellow
        }
    }

    # Start Frontend (skip if deployed or empty command)
    $frontendDir = Join-Path $WorkspaceRoot $agent.frontend.workDir
    $frontendCmd = $agent.frontend.startCommand
    if ($agent.frontend.deployed -eq $true) {
        Write-Host "   [CLOUD] Frontend -> DEPLOYED at $($agent.frontend.url)" -ForegroundColor Cyan
    } elseif (-not $frontendCmd -or $frontendCmd -eq "") {
        Write-Host "   [INFO] Frontend served by backend (unified server)" -ForegroundColor Cyan
    } elseif (Test-Path $frontendDir) {
        # Set environment variables if defined
        $envSetup = ""
        if ($agent.frontend.env) {
            $agent.frontend.env.PSObject.Properties | ForEach-Object {
                $envSetup += "`$env:$($_.Name) = '$($_.Value)'; "
            }
        }

        $frontendScript = "Set-Location '$frontendDir'; $envSetup$frontendCmd"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Minimized
        Write-Host "   [OK] Frontend -> port $($agent.frontend.port) ($($agent.frontend.url))" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Frontend dir not found: $frontendDir" -ForegroundColor DarkYellow
    }

    Write-Host ""
}

# -- Start Gateway Backend --

Write-Host "[GATEWAY] Starting Gateway Backend" -ForegroundColor Cyan
$gatewayDir = Join-Path $WorkspaceRoot "backend"
$gatewayVenv = Join-Path $gatewayDir ".venv\Scripts\Activate.ps1"

if (Test-Path $gatewayDir) {
    if (Test-Path $gatewayVenv) {
        $gatewayScript = "Set-Location '$gatewayDir'; & '$gatewayVenv'; uvicorn app.main:app --port $GatewayPort --reload"
    } else {
        $gatewayScript = "Set-Location '$gatewayDir'; uvicorn app.main:app --port $GatewayPort --reload"
    }
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $gatewayScript -WindowStyle Minimized
    Write-Host "   [OK] Gateway  -> port $GatewayPort (http://localhost:$GatewayPort/docs)" -ForegroundColor Green
} else {
    Write-Host "   [WARN] Gateway dir not found" -ForegroundColor DarkYellow
}
Write-Host ""

# -- Start Main Frontend --

Write-Host "[SHELL] Starting Main Frontend" -ForegroundColor Magenta
$frontendShellDir = Join-Path $WorkspaceRoot "frontend"
if (Test-Path (Join-Path $frontendShellDir "package.json")) {
    Write-Host "   [OK] Frontend -> port 3000 (http://localhost:3000)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "    Open http://localhost:3000 in browser  " -ForegroundColor White
    Write-Host "    Gateway: http://localhost:$GatewayPort/docs" -ForegroundColor White
    Write-Host "    Stop all: .\start-dev.ps1 -Stop       " -ForegroundColor White
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""

    Set-Location $frontendShellDir
    npm run dev
} else {
    Write-Host "   [ERROR] Frontend not initialized. Run: cd frontend; npm install" -ForegroundColor Red
}
