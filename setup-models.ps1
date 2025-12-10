#!/usr/bin/env pwsh
<#
.SYNOPSIS
    InfraPilot Model Setup Script
    
.DESCRIPTION
    Downloads and configures Ollama models for optimal performance.
    
.EXAMPLE
    .\setup-models.ps1
#>

Write-Host "🚀 InfraPilot Model Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is running
$ollamaRunning = $null
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    $ollamaRunning = $true
}
catch {
    $ollamaRunning = $false
}

if (-not $ollamaRunning) {
    Write-Host "⚠️  Ollama is not running!" -ForegroundColor Yellow
    Write-Host "Please start Ollama first: ollama serve" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Ollama is running" -ForegroundColor Green
Write-Host ""

# Model options
$models = @(
    @{
        Name = "1"
        Model = "phi"
        Time = "20-30s"
        Accuracy = "⭐"
        Desc = "Fastest - Best for development"
    },
    @{
        Name = "2"
        Model = "neural-chat"
        Time = "30-45s"
        Accuracy = "⭐⭐"
        Desc = "Fast & Balanced (RECOMMENDED)"
    },
    @{
        Name = "3"
        Model = "mistral"
        Time = "45-60s"
        Accuracy = "⭐⭐⭐"
        Desc = "Balanced accuracy"
    },
    @{
        Name = "4"
        Model = "qwen2.5-coder"
        Time = "2-3min"
        Accuracy = "⭐⭐⭐⭐"
        Desc = "Most accurate - slower"
    }
)

Write-Host "Available Models:" -ForegroundColor Cyan
Write-Host ""
foreach ($model in $models) {
    Write-Host "$($model.Name). $($model.Model)" -ForegroundColor White
    Write-Host "   Time: $($model.Time) | Accuracy: $($model.Accuracy) | $($model.Desc)" -ForegroundColor Gray
}
Write-Host ""

$choice = Read-Host "Select model to download (1-4, default: 2)"
if ([string]::IsNullOrEmpty($choice)) { $choice = "2" }

$selectedModel = $models | Where-Object { $_.Name -eq $choice }
if (-not $selectedModel) {
    Write-Host "Invalid choice!" -ForegroundColor Red
    exit 1
}

$modelName = $selectedModel.Model

Write-Host ""
Write-Host "⏳ Downloading $modelName..." -ForegroundColor Cyan
Write-Host "This may take a few minutes depending on your connection..." -ForegroundColor Gray

# Download the model
ollama pull $modelName

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully downloaded $modelName!" -ForegroundColor Green
    
    # Update .env file
    $envPath = ".\backend\.env"
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath
        $envContent = $envContent -replace "OLLAMA_MODEL=.*", "OLLAMA_MODEL=$modelName"
        Set-Content $envPath $envContent
        Write-Host "✅ Updated backend/.env with OLLAMA_MODEL=$modelName" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Could not find backend/.env" -ForegroundColor Yellow
        Write-Host "Please manually set: OLLAMA_MODEL=$modelName in your .env file" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎉 Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start backend:  cd backend && uvicorn app.main:app --reload" -ForegroundColor Gray
    Write-Host "2. Start frontend: cd frontend && npm run dev" -ForegroundColor Gray
    Write-Host "3. Use Fast Mode toggle for fastest results" -ForegroundColor Gray
}
else {
    Write-Host ""
    Write-Host "❌ Failed to download model" -ForegroundColor Red
    exit 1
}
