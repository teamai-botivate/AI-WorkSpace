<#
.SYNOPSIS
    Botivate AI Workspace — Development Startup Script

.DESCRIPTION
    Starts the backend (FastAPI) and frontend (React + Vite) for local development.
    Usage:
        .\start-dev.ps1           # Start everything
        .\start-dev.ps1 -Stop     # Stop everything

.PARAMETER Stop
    If specified, kills all running dev processes.
#>

param(
    [switch]$Stop
)

$ErrorActionPreference = "Continue"

$BACKEND_DIR = "$PSScriptRoot\backend"
$FRONTEND_DIR = "$PSScriptRoot\frontend"
$BACKEND_PORT = 8000
$FRONTEND_PORT = 3000

function Stop-DevProcesses {
    Write-Host "`n Stopping development servers..." -ForegroundColor Yellow

    # Kill Python/uvicorn processes
    Get-Process -Name "python", "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
    # Kill Node processes (Vite)
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*vite*" -or $_.CommandLine -like "*vite*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue

    Write-Host " All dev processes stopped." -ForegroundColor Green
    exit 0
}

if ($Stop) {
    Stop-DevProcesses
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  BOTIVATE AI WORKSPACE — Starting Dev Mode" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check for .env
if (-not (Test-Path "$PSScriptRoot\.env")) {
    Write-Host " No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path "$PSScriptRoot\.env.example") {
        Copy-Item "$PSScriptRoot\.env.example" "$PSScriptRoot\.env"
        Write-Host " .env created. Edit it with your API keys before running agents." -ForegroundColor Yellow
    } else {
        Write-Host " No .env.example found either. Create a .env file manually." -ForegroundColor Red
    }
}

# Start Backend
Write-Host " Starting Backend (FastAPI on port $BACKEND_PORT)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$PSScriptRoot'; `$env:PYTHONPATH='$PSScriptRoot'; uvicorn backend.app.main:app --reload --port $BACKEND_PORT --host 0.0.0.0"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# Start Frontend
Write-Host " Starting Frontend (Vite on port $FRONTEND_PORT)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$FRONTEND_DIR'; npm run dev"
) -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services started!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:$FRONTEND_PORT" -ForegroundColor White
Write-Host "  Backend:   http://localhost:$BACKEND_PORT" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:$BACKEND_PORT/docs" -ForegroundColor White
Write-Host "  Agents:    http://localhost:$BACKEND_PORT/api/agents" -ForegroundColor White
Write-Host ""
Write-Host "  To stop:   .\start-dev.ps1 -Stop" -ForegroundColor DarkGray
Write-Host ""

# Open browser
Start-Process "http://localhost:$FRONTEND_PORT"
