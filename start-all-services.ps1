# InfraPilot - Start All Services Script
# Starts both backend (port 8000) and frontend (port 3000) with auto-approval

Write-Host "================================" -ForegroundColor Cyan
Write-Host "InfraPilot - Starting All Services" -ForegroundColor Cyan
Write-Host "Backend: port 8000" -ForegroundColor Green
Write-Host "Frontend: port 3000" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Kill any existing Python and Node processes on our ports
Write-Host "`nCleaning up existing processes..." -ForegroundColor Yellow
try {
    $pythonProcs = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcs) {
        Stop-Process -Name python -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Killed existing Python processes" -ForegroundColor Green
    }
    
    $nodeProcs = Get-Process node -ErrorAction SilentlyContinue
    if ($nodeProcs) {
        Stop-Process -Name node -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Killed existing Node processes" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ No existing processes to clean up" -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

# Start Backend Server
Write-Host "`nStarting Backend Server..." -ForegroundColor Cyan
$backendPath = Join-Path $scriptDir "backend"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$backendPath'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
) -WindowStyle Normal

Write-Host "✓ Backend server started (port 8000)" -ForegroundColor Green
Write-Host "  Running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -ForegroundColor Gray

Start-Sleep -Seconds 2

# Start Frontend Server
Write-Host "`nStarting Frontend Server..." -ForegroundColor Cyan
$frontendPath = Join-Path $scriptDir "frontend"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$frontendPath'; npm run dev -- --port 3000"
) -WindowStyle Normal

Write-Host "✓ Frontend server started (port 3000)" -ForegroundColor Green
Write-Host "  Running: npm run dev -- --port 3000" -ForegroundColor Gray

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✓ All Services Started Successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "`nAccess Application:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "`nAPI Endpoint: http://localhost:8000/api/v1" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C in each terminal to stop services" -ForegroundColor Gray
