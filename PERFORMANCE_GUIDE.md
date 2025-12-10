# Performance Optimization Guide for InfraPilot

## Quick Start - Fastest Setup

### 1. Use a Faster Model
Edit `backend/.env`:
```env
OLLAMA_MODEL=neural-chat
```

**Model Comparison:**
| Model | Speed | Accuracy | Size | Time |
|-------|-------|----------|------|------|
| phi | ⚡⚡⚡ | ⭐ | 2.7GB | ~20s |
| neural-chat | ⚡⚡ | ⭐⭐ | 3.3GB | ~30-45s |
| mistral | ⚡⚡ | ⭐⭐⭐ | 4.1GB | ~45-60s |
| qwen2.5-coder | ⚡ | ⭐⭐⭐⭐ | 3.3GB | 2-3min |
| llama2 | ⚡ | ⭐⭐⭐ | 3.8GB | 2-3min |

### 2. Pre-download Models (One-time Setup)
This prevents download delays on first use:

```bash
# Download faster model (recommended)
ollama pull neural-chat

# Or other models
ollama pull phi
ollama pull mistral
```

### 3. Enable Fast Mode in UI
- Toggle "Fast Mode (IaC only)" in navbar
- Skips Terraform, Checkov, and Infracost
- **Fastest option: ~20-45 seconds total**

## Performance Breakdown

### Time Spent in Each Stage:

**Full Pipeline (without Fast Mode):**
- IaC Generation (Ollama): 30-120 seconds (depends on model)
- Terraform Plan: 20-30 seconds
- Checkov Security Scan: 10-20 seconds
- Infracost Analysis: 10-15 seconds
- **Total: 70-185 seconds (with parallel execution)**

**Fast Mode:**
- IaC Generation (Ollama): 30-120 seconds
- **Total: 30-120 seconds** ✅

## Recommendations by Use Case

### For Development/Testing (Fastest)
```env
OLLAMA_MODEL=phi
```
- Use Fast Mode toggle
- **Expected time: 20-30 seconds**

### For Production (Balanced)
```env
OLLAMA_MODEL=neural-chat
```
- Full pipeline with parallel execution
- **Expected time: 60-90 seconds**

### For High Accuracy (Slower but Better)
```env
OLLAMA_MODEL=qwen2.5-coder
```
- Full pipeline with parallel execution
- **Expected time: 120-200 seconds**

## Memory & System Requirements

### Minimum (Basic Operations)
- RAM: 8GB (with 4GB allocated to Ollama)
- CPU: 4 cores
- Disk: 10GB free

### Recommended (Smooth Operation)
- RAM: 16GB (with 8GB allocated to Ollama)
- CPU: 8+ cores
- Disk: 20GB free

### Optimal (Best Performance)
- RAM: 32GB+
- CPU: 16+ cores
- GPU: NVIDIA with 6GB+ VRAM (if available)

## Ollama GPU Acceleration (Advanced)

### For NVIDIA GPUs:
```bash
# Install CUDA (if not already installed)
# Then restart Ollama

# Verify GPU is being used:
ollama ps
```

### For Apple Silicon (M1/M2/M3):
Ollama uses Metal acceleration automatically - no extra setup needed!

## Monitoring & Debugging

### Check Which Model is Running:
```bash
ollama ps
```

### View Ollama Logs:
```bash
# On Windows
Get-Content $env:LOCALAPPDATA\Ollama\logs\server.log -Tail 50

# On macOS/Linux
tail -f ~/.ollama/logs/server.log
```

### Performance Profiling:
Check the backend logs for timing info:
```python
# In backend/app/utils/logger.py
# Add timing logs to see where delays are
```

## Tips for Faster Generation

1. **Keep prompts concise** - Shorter prompts = faster processing
2. **Use Fast Mode first** - Get IaC quickly, add analysis later if needed
3. **Cache results** - Consider caching similar requests
4. **Use a local GPU** - GPU acceleration can speed up Ollama 5-10x
5. **Monitor system resources** - Free up RAM before running

## Troubleshooting Slow Performance

### Problem: IaC generation taking 5+ minutes
**Solution:** Check if Ollama is using CPU instead of GPU
```bash
ollama ps  # Check utilization
```

### Problem: Getting timeouts
**Solution:** 
- Use Fast Mode
- Switch to a faster model (phi or neural-chat)
- Increase OLLAMA_TIMEOUT in `.env`

### Problem: Tools running sequentially instead of parallel
**Solution:** Verify `ENABLE_PARALLEL_AGENTS=True` in config.py

## Environment Variables Summary

```env
# Model Configuration
OLLAMA_MODEL=neural-chat        # Change to phi for fastest
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=300              # Seconds

# Performance Tuning
SKIP_TOOLS_BY_DEFAULT=False     # Set True to skip Terraform/etc by default
```

---

**Expected Results After Optimization:**
- Fast Mode: **20-45 seconds** ✅
- Full Pipeline: **60-90 seconds** (vs 2-5 min before)
- **2-5x speed improvement overall**
