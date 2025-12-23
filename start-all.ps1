#!/usr/bin/env pwsh
<#
.SYNOPSIS
    InfraPilot Quick Start - Unified Server
    
.DESCRIPTION
    Starts all required services for InfraPilot:
    1. Ollama (if available)
    2. Backend server (port 8000)
    3. Frontend server (port 3000)
    
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
Write-Host "2️⃣  Starting Backend on port 8000..." -ForegroundColor Yellow

$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -PassThru
Write-Host "✅ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API: http://localhost:8000/api/v1" -ForegroundColor Gray

Write-Host ""
Write-Host "3️⃣  Starting Frontend on port 3000..." -ForegroundColor Yellow

# Use Node.js server for better performance and consistency
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\SridharJayaraman\Downloads\infrapilot 2\infrapilot'; node server.js" -PassThru
Write-Host "✅ Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host "   URL: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Serving: frontend/dist directory" -ForegroundColor Gray

Write-Host ""
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "✨ All services started!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Open in browser: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 API Documentation:" -ForegroundColor Yellow
Write-Host "   Swagger UI: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 To stop all services, close these windows or press Ctrl+C" -ForegroundColor Gray
Write-Host ""

# Keep this script running
Read-Host "Press Enter to continue..."
