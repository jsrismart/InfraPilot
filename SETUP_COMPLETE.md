# 🎉 InfraPilot - Setup Complete!

## ✅ System Status

### Running Services:
- ✅ **Backend Server**: http://localhost:8001
- ✅ **Frontend Application**: http://localhost:3001
- ✅ **Ollama Service**: Required (start with `ollama serve`)

### Verified Components:
- ✅ Python 3.14.0
- ✅ Node.js v24.11.1
- ✅ All Python packages installed
- ✅ All Node packages installed
- ✅ Terraform available (optional tools)

## 🚀 Quick Start

### 1. Open the Application
Open your browser and go to:
```
http://localhost:3001
```

### 2. Start Ollama (if not already running)
```bash
ollama serve
```

### 3. Generate Infrastructure
1. Enter a prompt like:
   ```
   AWS VPC with 2 subnets, EC2 instance, security groups
   ```

2. Click "Generate Infrastructure"

3. Wait for results:
   - **Fast Mode** (IaC only): 30-45 seconds
   - **Full Mode** (with analysis): 1-3 minutes

## 📋 What You Can Do

### Generate IaC
- Terraform configuration files
- AWS, Azure, GCP infrastructure
- Custom resource definitions

### Full Pipeline (Optional)
- ✅ Generate Terraform code
- ✅ Validate with Terraform plan
- ✅ Security scanning with Checkov
- ✅ Cost analysis with Infracost

### Performance Options
- **Fast Mode**: Skip expensive tools for quick results
- **Full Mode**: Complete analysis with all tools
- **Model Selection**: Use faster models for quicker response

## 🔧 Configuration Files

### Backend (`.env`)
Located: `backend/.env`
```env
OLLAMA_MODEL=qwen2.5-coder
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=300
```

### Frontend (`.env`)
Located: `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

## 📊 Performance Tips

1. **Use Fast Mode** for quick IaC generation (30-45 sec)
2. **Install faster model**:
   ```powershell
   .\setup-models.ps1
   # Select phi or neural-chat for faster results
   ```

3. **Free up system RAM** before running

4. **Check Ollama is using GPU** for acceleration

## 🆘 Troubleshooting

### Issue: "Connection refused" to backend
**Solution**: Backend might still be starting. Wait 10 seconds and refresh.

### Issue: "Model not found" error
**Solution**: Start Ollama:
```bash
ollama serve
```

### Issue: Very slow generation (5+ minutes)
**Solution**:
- Use Fast Mode toggle
- Switch to faster model: `ollama pull phi`
- Update `backend/.env` with faster model

### Issue: Port already in use
**Solution**: Kill existing process:
```powershell
# For port 8001 (backend)
Get-NetTcpConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Stop-Process -Force

# For port 3001 (frontend)
Get-NetTcpConnection -LocalPort 3001 -ErrorAction SilentlyContinue | Stop-Process -Force
```

## 📚 Available Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `check-dependencies.ps1` | Verify all modules installed | `.\check-dependencies.ps1` |
| `start-all.ps1` | Start all services | `.\start-all.ps1` |
| `setup-models.ps1` | Download faster Ollama models | `.\setup-models.ps1` |

## 📖 Documentation

- `PERFORMANCE_GUIDE.md` - Detailed performance tuning
- `OPTIMIZATION_SUMMARY.md` - Quick optimization tips
- `DEPENDENCY_STATUS.md` - Full dependency report

## 🎯 Example Prompts

Try these infrastructure descriptions:

1. **AWS Web Server**
   ```
   AWS EC2 instance with security group, EBS volume, elastic IP
   ```

2. **Kubernetes Cluster**
   ```
   AWS EKS cluster with 3 worker nodes, IAM roles, VPC
   ```

3. **Database Setup**
   ```
   RDS MySQL instance with read replica, security group, parameter group
   ```

4. **Microservices**
   ```
   AWS VPC with private and public subnets, NAT gateway, load balancer, EC2 instances
   ```

## ✨ Next Steps

1. ✅ Services are running
2. ⏭️ Open http://localhost:3001
3. ⏭️ Start Ollama: `ollama serve`
4. ⏭️ Enter your infrastructure description
5. ⏭️ Click "Generate Infrastructure"
6. ⏭️ Review the generated Terraform code

---

**Status**: 🟢 **Ready to Use**

All dependencies installed and services running!
