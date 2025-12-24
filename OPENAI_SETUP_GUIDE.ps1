#!/usr/bin/env pwsh
<#
  OpenAI ChatGPT Setup Guide
  Replace Ollama with ChatGPT for Terraform generation
#>

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   OpenAI ChatGPT Configuration Guide" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ System has been updated to use ChatGPT instead of Ollama!" -ForegroundColor Green
Write-Host ""

Write-Host "📋 What Changed:" -ForegroundColor Yellow
Write-Host "  1. Replaced Ollama LLM with OpenAI ChatGPT (gpt-4-turbo)"
Write-Host "  2. Updated configuration to use OPENAI_API_KEY"
Write-Host "  3. Modified designer_agent.py to use OpenAI API"
Write-Host "  4. Updated .env file with new settings"
Write-Host ""

Write-Host "🔑 Required Setup:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Step 1: Get your OpenAI API Key"
Write-Host "  → Visit: https://platform.openai.com/api-keys"
Write-Host "  → Create a new API key"
Write-Host "  → Copy the key (it starts with 'sk-')"
Write-Host ""

Write-Host "Step 2: Set the environment variable"
Write-Host "  For PowerShell:"
Write-Host "  " -NoNewline; Write-Host "`$env:OPENAI_API_KEY='sk-your-api-key-here'" -ForegroundColor Green
Write-Host ""
Write-Host "  For permanent setup (Windows):"
Write-Host "  " -NoNewline; Write-Host "setx OPENAI_API_KEY sk-your-api-key-here" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Update the .env file (optional)"
Write-Host "  Edit: backend/.env"
Write-Host "  Set: OPENAI_API_KEY=sk-your-api-key-here"
Write-Host ""

Write-Host "Step 4: Start the backend"
Write-Host "  " -NoNewline; Write-Host "`$env:OPENAI_API_KEY='sk-...'; cd backend; python -m uvicorn app.main:app --port 8000" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Starting Application:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend is running on: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend is running on: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Testing ChatGPT Integration:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open: http://localhost:3001"
Write-Host "2. Paste Terraform code or generate architecture"
Write-Host "3. Click 'Generate Architecture Diagram'"
Write-Host "4. ChatGPT will process the request"
Write-Host ""

Write-Host "⚙️  Configuration Details:" -ForegroundColor Yellow
Write-Host "  • Model: gpt-4-turbo"
Write-Host "  • Temperature: 0.2 (deterministic)"
Write-Host "  • Max Tokens: 2000"
Write-Host "  • Timeout: 60 seconds"
Write-Host ""

Write-Host "💡 Model Options:" -ForegroundColor Yellow
Write-Host "  • gpt-4-turbo (recommended) - Best quality, 128k context"
Write-Host "  • gpt-4 - High quality, smaller context"
Write-Host "  • gpt-3.5-turbo - Fastest, budget-friendly"
Write-Host ""
Write-Host "  To change model, update backend/app/core/config.py:"
Write-Host "  " -NoNewline; Write-Host "OPENAI_MODEL: str = 'gpt-4-turbo'" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Files Modified:" -ForegroundColor Yellow
Write-Host "  ✓ backend/app/core/config.py - Updated settings"
Write-Host "  ✓ backend/app/agents/designer_agent.py - ChatGPT integration"
Write-Host "  ✓ backend/.env - Configuration template"
Write-Host ""

Write-Host "❌ Troubleshooting:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Issue: 'OPENAI_API_KEY not configured'"
Write-Host "  → Make sure OPENAI_API_KEY environment variable is set"
Write-Host "  → Check: " -NoNewline; Write-Host "echo `$env:OPENAI_API_KEY" -ForegroundColor Green
Write-Host ""

Write-Host "Issue: 'Authentication error' from OpenAI"
Write-Host "  → Verify your API key is correct"
Write-Host "  → Check at: https://platform.openai.com/api-keys"
Write-Host "  → Ensure billing is set up"
Write-Host ""

Write-Host "Issue: 'Connection timeout'"
Write-Host "  → Check internet connection"
Write-Host "  → Verify OpenAI API is accessible"
Write-Host "  → Try increasing timeout in config.py"
Write-Host ""

Write-Host "✨ You're all set! ChatGPT is now powering your architecture diagrams!" -ForegroundColor Green
Write-Host ""
