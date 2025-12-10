# InfraPilot - Dependency Status Report

## ✅ All Required Dependencies Installed

### System Requirements
- **Python**: 3.14.0 ✅
- **Node.js**: v24.11.1 ✅
- **npm**: 11.6.2 ✅

### Core Services
- **Ollama**: 0.13.0 ✅
  - Status: **NOT RUNNING** ⚠️
  - Action: Start with `ollama serve` in a separate terminal

### Backend Python Packages
| Package | Version | Status |
|---------|---------|--------|
| fastapi | Latest | ✅ Installed |
| uvicorn | Latest | ✅ Installed |
| pydantic | Latest | ✅ Installed |
| pydantic-settings | Latest | ✅ Installed |
| ollama | Latest | ✅ Installed |
| python-dotenv | 1.2.1 | ✅ Installed |

### Frontend Packages
- **node_modules**: ✅ Installed
- **vite**: Ready
- **react**: Ready
- **typescript**: Ready
- **tailwindcss**: Ready

### Optional Tools
| Tool | Status |
|------|--------|
| Terraform | ✅ v1.14.0 |
| Checkov | ⚠️ Not installed (optional) |
| Infracost | ⚠️ Not installed (optional) |

## 🚀 Quick Start

### Option 1: Automated Start (Recommended)
```powershell
cd infrapilot
.\start-all.ps1
```

### Option 2: Manual Start

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Start Backend:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
npm run dev
```

Then open: **http://localhost:3001**

## 📋 Verification Scripts

### Check Dependencies
```powershell
.\check-dependencies.ps1
```
This will:
- ✅ Verify all required modules are installed
- 📦 Auto-install any missing packages
- 📊 Show a detailed status report

### Download Models
```powershell
.\setup-models.ps1
```
This will:
- 📥 Download faster models (optional)
- ⚙️ Configure .env file
- 📈 Improve performance

## 🔧 Configuration Files

### Backend Configuration
**File**: `backend/.env`
```env
OLLAMA_MODEL=qwen2.5-coder
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=300
```

### Frontend Configuration
**File**: `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

## 📊 Service URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3001 | 3001 |
| Backend API | http://localhost:8001 | 8001 |
| Ollama API | http://localhost:11434 | 11434 |

## 🐛 Troubleshooting

### Issue: "Ollama is not running"
**Solution:**
```bash
ollama serve
```

### Issue: "Port already in use"
**Solution:** Kill existing process:
```powershell
# For port 8001 (backend)
Get-NetTcpConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Stop-Process -Force

# For port 3001 (frontend)
Get-NetTcpConnection -LocalPort 3001 -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Issue: "Module not found"
**Solution:** Run dependency checker:
```powershell
.\check-dependencies.ps1
```

### Issue: "Model not found"
**Solution:** Download model:
```bash
ollama pull qwen2.5-coder
# or
ollama pull neural-chat
```

## 📈 Performance Tips

1. **Use Fast Mode** - Toggle in UI for 30-45 second responses
2. **Install faster model**:
   ```powershell
   .\setup-models.ps1
   # Select option 2 (neural-chat)
   ```
3. **Check Ollama is running** - `ollama serve`
4. **Free up RAM** - Close unnecessary applications

## ✨ Features Ready

- ✅ Infrastructure as Code generation (IaC)
- ✅ Terraform validation & planning
- ✅ Security scanning (with Checkov)
- ✅ Cost analysis (with Infracost)
- ✅ Parallel agent execution
- ✅ Fast Mode for quick generation
- ✅ Configurable models
- ✅ Error handling & logging

## 📚 Documentation

- `PERFORMANCE_GUIDE.md` - Detailed performance tuning
- `OPTIMIZATION_SUMMARY.md` - Quick optimization reference
- `check-dependencies.ps1` - Verify all modules
- `setup-models.ps1` - Download Ollama models
- `start-all.ps1` - Quick service startup

---

**Status**: ✅ Ready to use - Just start Ollama and run services!
