@echo off
REM Kill all processes on ports 8000 and 3000

echo Clearing ports 8000 and 3000...

REM Kill process on port 8000
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000.*LISTENING"') do (
    echo Killing process %%a on port 8000
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill process on port 3000
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000.*LISTENING"') do (
    echo Killing process %%a on port 3000
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill all Python processes
echo Killing all Python processes...
taskkill /F /IM python.exe >nul 2>&1

REM Kill all Node processes
echo Killing all Node processes...
taskkill /F /IM node.exe >nul 2>&1

timeout /t 1 /nobreak >nul
echo Done! Ports are now clear.
