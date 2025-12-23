@echo off
REM InfraPilot - Jenkins-Compatible Startup
REM Starts backend and frontend sequentially (good for CI/CD)

setlocal enabledelayedexpansion

echo ================================
echo InfraPilot - Jenkins Auto-Start
echo ================================

REM Get the root directory
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

REM Kill any existing processes on the ports
echo Clearing ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill all Python and Node processes as backup
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend (background)
echo.
echo Starting Backend on port 8000...
cd /d "%ROOT_DIR%backend"
start /B python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
timeout /t 3 /nobreak >nul

REM Start Frontend (background)
echo Starting Frontend on port 3000...
cd /d "%ROOT_DIR%frontend"
start /B npm run dev -- --port 3000
timeout /t 3 /nobreak >nul

echo.
echo ✓ Both services started
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo.
