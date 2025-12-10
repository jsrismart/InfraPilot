#!/usr/bin/env pwsh
<#
.SYNOPSIS
    InfraPilot Dependency Checker
    
.DESCRIPTION
    Checks if all required modules and packages are installed.
    Only installs missing dependencies.
    
.EXAMPLE
    .\check-dependencies.ps1
#>

Write-Host "🔍 InfraPilot Dependency Checker" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Track results
$allOk = $true
$results = @()

# ============================================================================
# 1. Check Python Environment
# ============================================================================
Write-Host "1. Checking Python Installation..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -like "Python 3.*") {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        $results += @{Name="Python"; Status="OK"; Details=$pythonVersion}
    } else {
        throw "Python 3 not found"
    }
} catch {
    Write-Host "❌ Python not found or not in PATH" -ForegroundColor Red
    $results += @{Name="Python"; Status="MISSING"; Details="Install Python 3.8+"}
    $allOk = $false
}

# ============================================================================
# 2. Check Node.js Installation
# ============================================================================
Write-Host ""
Write-Host "2. Checking Node.js Installation..." -ForegroundColor Yellow

try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
    $results += @{Name="Node.js"; Status="OK"; Details="$nodeVersion / npm $npmVersion"}
} catch {
    Write-Host "❌ Node.js or npm not found" -ForegroundColor Red
    $results += @{Name="Node.js"; Status="MISSING"; Details="Install Node.js 16+"}
    $allOk = $false
}

# ============================================================================
# 3. Check Ollama Installation
# ============================================================================
Write-Host ""
Write-Host "3. Checking Ollama Installation..." -ForegroundColor Yellow

try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama found: $ollamaVersion" -ForegroundColor Green
    $results += @{Name="Ollama"; Status="OK"; Details=$ollamaVersion}
    
    # Check if Ollama is running
    Write-Host ""
    Write-Host "   Checking if Ollama is running..." -ForegroundColor Gray
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
        Write-Host "   ✅ Ollama service is running" -ForegroundColor Green
        $results += @{Name="Ollama Service"; Status="OK"; Details="Running on localhost:11434"}
        
        # Check installed models
        Write-Host ""
        Write-Host "   Checking installed models..." -ForegroundColor Gray
        $models = ollama list 2>&1
        if ($models -like "*qwen2.5-coder*") {
            Write-Host "   ✅ qwen2.5-coder installed" -ForegroundColor Green
            $results += @{Name="Model: qwen2.5-coder"; Status="OK"; Details="Available"}
        }
        if ($models -like "*neural-chat*") {
            Write-Host "   ✅ neural-chat installed" -ForegroundColor Green
            $results += @{Name="Model: neural-chat"; Status="OK"; Details="Available"}
        }
        if ($models -like "*mistral*") {
            Write-Host "   ✅ mistral installed" -ForegroundColor Green
            $results += @{Name="Model: mistral"; Status="OK"; Details="Available"}
        }
        if ($models -like "*phi*") {
            Write-Host "   ✅ phi installed" -ForegroundColor Green
            $results += @{Name="Model: phi"; Status="OK"; Details="Available"}
        }
        
        # Show all models
        Write-Host ""
        Write-Host "   Available models:" -ForegroundColor Gray
        $models | Select-Object -Skip 1 | ForEach-Object {
            Write-Host "     - $_" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "   ⚠️  Ollama is installed but not running" -ForegroundColor Yellow
        Write-Host "   Run: ollama serve" -ForegroundColor Yellow
        $results += @{Name="Ollama Service"; Status="NOT RUNNING"; Details="Start with 'ollama serve'"}
    }
    
} catch {
    Write-Host "❌ Ollama not found" -ForegroundColor Red
    Write-Host "   Install from: https://ollama.ai" -ForegroundColor Yellow
    $results += @{Name="Ollama"; Status="MISSING"; Details="Install from https://ollama.ai"}
    $allOk = $false
}

# ============================================================================
# 4. Check Backend Python Dependencies
# ============================================================================
Write-Host ""
Write-Host "4. Checking Backend Python Dependencies..." -ForegroundColor Yellow

$backendPath = ".\backend"
if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Backend directory not found" -ForegroundColor Red
    $allOk = $false
} else {
    $requirements = @(
        @{Name="fastapi"; Package="fastapi"}
        @{Name="uvicorn"; Package="uvicorn"}
        @{Name="pydantic"; Package="pydantic"}
        @{Name="pydantic-settings"; Package="pydantic-settings"}
        @{Name="ollama"; Package="ollama"}
        @{Name="python-dotenv"; Package="python-dotenv"}
    )
    
    $missingPackages = @()
    
    foreach ($req in $requirements) {
        try {
            $check = python -c "import $($req.Package.Replace('-', '_'))" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ $($req.Name) installed" -ForegroundColor Green
                $results += @{Name="Python: $($req.Name)"; Status="OK"; Details="Installed"}
            } else {
                Write-Host "❌ $($req.Name) NOT installed" -ForegroundColor Red
                $results += @{Name="Python: $($req.Name)"; Status="MISSING"; Details="Not installed"}
                $missingPackages += $req.Package
                $allOk = $false
            }
        } catch {
            Write-Host "❌ $($req.Name) NOT installed" -ForegroundColor Red
            $results += @{Name="Python: $($req.Name)"; Status="MISSING"; Details="Not installed"}
            $missingPackages += $req.Package
            $allOk = $false
        }
    }
    
    # Install missing packages
    if ($missingPackages.Count -gt 0) {
        Write-Host ""
        Write-Host "Installing missing Python packages..." -ForegroundColor Cyan
        
        $installCmd = "pip install $($missingPackages -join ' ')"
        Write-Host "Running: $installCmd" -ForegroundColor Gray
        
        Invoke-Expression $installCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Missing packages installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install some packages" -ForegroundColor Red
            $allOk = $false
        }
    }
}

# ============================================================================
# 5. Check Frontend Dependencies
# ============================================================================
Write-Host ""
Write-Host "5. Checking Frontend Dependencies..." -ForegroundColor Yellow

$frontendPath = ".\frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend directory not found" -ForegroundColor Red
    $allOk = $false
} else {
    $packageJsonPath = "$frontendPath\package.json"
    if (Test-Path $packageJsonPath) {
        Write-Host "✅ package.json found" -ForegroundColor Green
        
        # Check if node_modules exists
        $nodeModulesPath = "$frontendPath\node_modules"
        if (Test-Path $nodeModulesPath) {
            Write-Host "✅ node_modules exists" -ForegroundColor Green
            $results += @{Name="Frontend: node_modules"; Status="OK"; Details="Installed"}
        } else {
            Write-Host "⚠️  node_modules not found - installing..." -ForegroundColor Yellow
            Push-Location $frontendPath
            npm install
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ npm packages installed" -ForegroundColor Green
                $results += @{Name="Frontend: npm packages"; Status="OK"; Details="Installed"}
            } else {
                Write-Host "❌ Failed to install npm packages" -ForegroundColor Red
                $results += @{Name="Frontend: npm packages"; Status="FAILED"; Details="Installation failed"}
                $allOk = $false
            }
            Pop-Location
        }
    } else {
        Write-Host "❌ package.json not found" -ForegroundColor Red
        $results += @{Name="Frontend: package.json"; Status="MISSING"; Details="Not found"}
        $allOk = $false
    }
}

# ============================================================================
# 6. Check Optional Tools
# ============================================================================
Write-Host ""
Write-Host "6. Checking Optional Tools..." -ForegroundColor Yellow

$optionalTools = @(
    @{Name="Terraform"; Command="terraform --version"}
    @{Name="Checkov"; Command="checkov --version"}
    @{Name="Infracost"; Command="infracost --version"}
)

foreach ($tool in $optionalTools) {
    try {
        $version = Invoke-Expression $tool.Command 2>&1
        Write-Host "✅ $($tool.Name) found: $(($version -split "`n")[0])" -ForegroundColor Green
        $results += @{Name="Tool: $($tool.Name)"; Status="OK"; Details="Installed"}
    } catch {
        Write-Host "⚠️  $($tool.Name) not found (optional)" -ForegroundColor Gray
        $results += @{Name="Tool: $($tool.Name)"; Status="OPTIONAL"; Details="Not installed"}
    }
}

# ============================================================================
# 7. Summary
# ============================================================================
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📊 Dependency Check Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Show summary table
$results | Format-Table -Property Name, Status, Details -AutoSize

Write-Host ""
if ($allOk) {
    Write-Host "🎉 All required dependencies are installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start Ollama (if not running):  ollama serve" -ForegroundColor Gray
    Write-Host "2. Start backend:                   cd backend && python -m uvicorn app.main:app --reload" -ForegroundColor Gray
    Write-Host "3. Start frontend:                  cd frontend && npm run dev" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Some dependencies are missing" -ForegroundColor Yellow
    Write-Host "Please install missing components and run this script again" -ForegroundColor Yellow
}

Write-Host ""
