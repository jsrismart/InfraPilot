#!/usr/bin/env pwsh
<#
.SYNOPSIS
    InfraPilot Quick Start
    
.DESCRIPTION
    Starts all required services for InfraPilot:
    1. Ollama (if available)
    2. Backend server
    3. Frontend dev server
    
.EXAMPLE
    .\start-all.ps1
#>

Write-Host ""
Write-Host "🚀 InfraPilot Quick Start" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check Ollama status
Write-Host "1️⃣  Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 1 -ErrorAction SilentlyContinue
    Write-Host "✅ Ollama is already running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not running. Please start it in a separate terminal:" -ForegroundColor Yellow
    Write-Host "   ollama serve" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue without Ollama? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

Write-Host ""
Write-Host "2️⃣  Starting Backend on port 8001..." -ForegroundColor Yellow

$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8001" -PassThru
Write-Host "✅ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
Write-Host "   URL: http://localhost:8001" -ForegroundColor Gray

Write-Host ""
Write-Host "3️⃣  Starting Frontend on port 3001..." -ForegroundColor Yellow

$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\frontend'; npm run dev" -PassThru
Write-Host "✅ Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host "   URL: http://localhost:3001" -ForegroundColor Gray

Write-Host ""
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "✨ All services started!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Open in browser: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop all services, close these windows or press Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Keep this script running
Read-Host "Press Enter to continue..."
