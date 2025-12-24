# QUICK START COMMANDS FOR InfraPilot

## Option 1: Run the PowerShell Script (Recommended - Auto-starts both)
```powershell
powershell -ExecutionPolicy Bypass -File start-all-services.ps1
```

## Option 2: Single PowerShell One-Liner (Auto-kills and starts both)
```powershell
taskkill /F /IM python.exe /IM node.exe 2>$null; Start-Sleep 1; $root="c:\Users\SridharJayaraman\Desktop\Reference\InfraPilot-Accelarator\Repo-Infrapilot\sridhar_branch\InfraPilot"; Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"; Start-Sleep 2; Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root\frontend'; npm run dev -- --port 3000"
```

## Option 3: Manual Commands (Run in Separate Terminals)

### Terminal 1 - Backend:
```powershell
cd "c:\Users\SridharJayaraman\Desktop\Reference\InfraPilot-Accelarator\Repo-Infrapilot\sridhar_branch\InfraPilot\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```powershell
cd "c:\Users\SridharJayaraman\Desktop\Reference\InfraPilot-Accelarator\Repo-Infrapilot\sridhar_branch\InfraPilot\frontend"
npm run dev -- --port 3000
```

## Option 4: Kill Existing Processes First (if needed)
```powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Kill all Node processes
taskkill /F /IM node.exe

# Then run the script
powershell -ExecutionPolicy Bypass -File start-all-services.ps1
```

## Access Points After Starting:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API**: http://localhost:8000/api/v1

## Troubleshooting:
If you get "Port already in use" errors, run this to clear ports:
```powershell
# Find and kill process on port 8000
$proc = netstat -ano | Select-String ":8000.*LISTENING" | % { $_.Split()[-1] }; if ($proc) { taskkill /F /PID $proc }

# Find and kill process on port 3000
$proc = netstat -ano | Select-String ":3000.*LISTENING" | % { $_.Split()[-1] }; if ($proc) { taskkill /F /PID $proc }
```
