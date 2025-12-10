# InfraPilot - Quick Reference

## 🎯 Right Now - What's Running

✅ **Backend**: http://localhost:8001  
✅ **Frontend**: http://localhost:3001  
⏳ **Ollama**: Port 11434 (start with `ollama serve` if needed)

## 🌐 Open Application

```
http://localhost:3001
```

## ⚡ Quick Commands

### Start Everything
```powershell
.\start-all.ps1
```

### Start Ollama
```bash
ollama serve
```

### Start Backend Only
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Start Frontend Only
```bash
cd frontend
npm run dev
```

### Check Dependencies
```powershell
.\check-dependencies.ps1
```

### Download Faster Models
```powershell
.\setup-models.ps1
```

## 📝 Example Usage

1. Open: http://localhost:3001
2. Enter: "AWS EC2 instance with security group"
3. Click: "Generate Infrastructure"
4. Wait: 30 seconds - 3 minutes
5. View: Generated Terraform files

## ⚙️ Configuration

### Backend `.env`
```env
OLLAMA_MODEL=qwen2.5-coder  # or neural-chat, phi, mistral
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=300
```

### Frontend `.env`
```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

## 🐛 Quick Fixes

### "Connection refused"
→ Wait 10 seconds and refresh browser

### "Model not found"
→ Start Ollama: `ollama serve`

### "Port already in use"
```powershell
Get-NetTcpConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Stop-Process -Force
```

### "Slow generation"
→ Enable "Fast Mode" toggle in UI

## 📊 Performance

| Mode | Time |
|------|------|
| Fast (IaC only) | 30-45 sec |
| Full Pipeline | 1-3 min |

## 📚 Files

```
infrapilot/
├── backend/           # Python API
├── frontend/          # React UI
├── SETUP_COMPLETE.md  # This setup guide
├── DEPENDENCY_STATUS.md
├── PERFORMANCE_GUIDE.md
├── check-dependencies.ps1
├── setup-models.ps1
└── start-all.ps1
```

## ✅ Checklist

- [x] All dependencies installed
- [x] Backend running on 8001
- [x] Frontend running on 3001
- [ ] Ollama started (`ollama serve`)
- [ ] Browser opened to http://localhost:3001
- [ ] Test prompt entered and executed

---

**You're all set! 🚀**
