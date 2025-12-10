# Quick setup script for real-time pricing
# Usage: ./setup-real-time-pricing.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Real-Time Cloud Pricing Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "backend")) {
    Write-Host "ERROR: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Install dependencies
Write-Host "Step 1: Installing required packages..." -ForegroundColor Yellow
Set-Location backend

pip install -q boto3 azure-identity azure-mgmt-consumption google-cloud-billing requests

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install packages" -ForegroundColor Red
    exit 1
}

# Step 2: Create .env file if it doesn't exist
Write-Host ""
Write-Host "Step 2: Setting up configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
    } else {
        Write-Host "! .env.example not found, creating basic .env" -ForegroundColor Yellow
        @"
# Real-Time Cloud Pricing Configuration
AWS_REGION=us-east-1
PRICING_CACHE_TTL_HOURS=24
PRICING_CACHE_DIR=./pricing_cache
USE_FALLBACK_PRICING=true
PRICING_API_RATE_LIMIT=60
DEFAULT_CURRENCY=USD
"@ | Out-File ".env" -Encoding UTF8
    }
} else {
    Write-Host "✓ .env already exists" -ForegroundColor Green
}

# Step 3: Create pricing cache directory
Write-Host ""
Write-Host "Step 3: Creating pricing cache directory..." -ForegroundColor Yellow
if (-not (Test-Path "pricing_cache")) {
    New-Item -ItemType Directory -Path "pricing_cache" -Force | Out-Null
    Write-Host "✓ Created pricing_cache directory" -ForegroundColor Green
} else {
    Write-Host "✓ pricing_cache directory already exists" -ForegroundColor Green
}

# Step 4: Test imports
Write-Host ""
Write-Host "Step 4: Verifying imports..." -ForegroundColor Yellow

$test_code = @"
try:
    import boto3
    print("✓ boto3 imported successfully")
except ImportError as e:
    print(f"✗ boto3 import failed: {e}")

try:
    from azure.identity import DefaultAzureCredential
    print("✓ Azure Identity imported successfully")
except ImportError as e:
    print(f"✗ Azure Identity import failed: {e}")

try:
    from real_time_pricing_fetcher import pricing_fetcher
    print("✓ Real-time pricing fetcher imported successfully")
except ImportError as e:
    print(f"✗ Real-time pricing fetcher import failed: {e}")
except Exception as e:
    print(f"⚠ Real-time pricing fetcher found but with warnings: {e}")
"@

python -c $test_code

# Step 5: Configuration guide
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Configure AWS credentials:"
Write-Host "   • Option A: Run 'aws configure'"
Write-Host "   • Option B: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
Write-Host ""
Write-Host "2. Configure Azure credentials:"
Write-Host "   • Option A: Run 'az login'"
Write-Host "   • Option B: Set AZURE_SUBSCRIPTION_ID in .env"
Write-Host ""
Write-Host "3. Edit backend/.env to add your credentials"
Write-Host ""
Write-Host "4. Start the backend server:"
Write-Host "   • cd backend"
Write-Host "   • python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
Write-Host ""
Write-Host "5. Documentation:"
Write-Host "   • See REAL_TIME_PRICING_SETUP.md for detailed setup"
Write-Host ""
Write-Host "Check pricing source:"
Write-Host "   curl http://localhost:8001/api/v1/pricing/pricing-formats"
Write-Host ""

Set-Location ..
