@echo off
REM InfraPilot - Start All Services (Backend + Frontend)
REM This script starts both backend and frontend with auto-cleanup

setlocal enabledelayedexpansion

echo ================================
echo InfraPilot - Starting All Services
echo Backend: port 8000
echo Frontend: port 3000
echo ================================

REM Get the current directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Kill processes on specific ports
echo.
echo Clearing ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill all Python and Node processes as backup
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend Server
echo.
echo Starting Backend Server on port 8000...
start "InfraPilot-Backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul

REM Start Frontend Server
echo.
echo Starting Frontend Server on port 3000...
start "InfraPilot-Frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm run dev -- --port 3000"
timeout /t 1 /nobreak >nul

REM Display status
echo.
echo ================================
echo Services started successfully!
echo ================================
echo.
echo Access Application:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API:      http://localhost:8000/api/v1
echo.
echo Press any key to continue...
pause >nul
