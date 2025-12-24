# ChatGPT Integration - Quick Reference

## ✅ Changes Made

Ollama has been completely replaced with **OpenAI ChatGPT**:

### Files Updated:
1. **backend/app/core/config.py**
   - Replaced `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_TIMEOUT`
   - Added `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TIMEOUT`

2. **backend/app/agents/designer_agent.py**
   - Replaced `ollama` import with `openai`
   - Changed `_generate_with_ollama()` → `_generate_with_chatgpt()`
   - Now uses OpenAI ChatGPT API with gpt-4-turbo model

3. **backend/.env**
   - Removed all Ollama settings
   - Added OpenAI configuration template

## 🔑 Required API Key

Get your OpenAI API key from: https://platform.openai.com/api-keys

## 🚀 Starting the Application

```powershell
# Set API key (replace with your actual key)
$env:OPENAI_API_KEY = "sk-your-api-key-here"
$env:LUCIDCHART_API_KEY = "key-..."

# Start backend
cd "backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, start frontend
cd "frontend"
npm run dev -- --port 3001
```

## 🎯 How It Works

1. User enters Terraform code or describes architecture
2. Backend sends request to OpenAI ChatGPT
3. ChatGPT generates optimized Terraform IaC
4. Result displayed with Lucidchart diagram export

## ⚙️ Configuration

**Model Options:**
- `gpt-4-turbo` - Best quality (default, $0.01-$0.03 per request)
- `gpt-4` - High quality ($0.03-$0.06 per request)
- `gpt-3.5-turbo` - Fast & cheap ($0.0005-$0.0015 per request)

**To change model:**
Edit `backend/app/core/config.py`:
```python
OPENAI_MODEL: str = "gpt-4-turbo"
```

## 💰 Cost Estimate

- gpt-4-turbo: ~$0.01 per Terraform generation
- gpt-3.5-turbo: ~$0.0005 per generation

## ✨ Features

✅ Uses OpenAI's most advanced ChatGPT model  
✅ Auto-generates Terraform IaC from descriptions  
✅ Creates architecture diagrams in Lucidchart  
✅ Exports to SVG format  
✅ No local LLM needed (cloud-based)  
✅ Faster than Ollama  

## 🔗 Useful Links

- OpenAI API: https://platform.openai.com/
- API Keys: https://platform.openai.com/api-keys
- API Documentation: https://platform.openai.com/docs/api-reference
- Pricing: https://openai.com/pricing

## ⚠️ Important Notes

- API key is required - without it, Terraform generation will fail
- Ensure billing is set up on your OpenAI account
- Each API call incurs a small cost
- Keep your API key secure - never commit to version control
