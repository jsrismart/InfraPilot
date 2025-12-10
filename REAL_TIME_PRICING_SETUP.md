# Real-Time Cloud Pricing Integration Guide

## Overview

InfraPilot now supports **real-time pricing APIs** from AWS and Azure, with intelligent fallback to static pricing when APIs are unavailable. This provides accurate, up-to-date cost estimates for your infrastructure.

## Features

✅ **Real-Time AWS Pricing** - Fetches live EC2, RDS, and S3 pricing  
✅ **Real-Time Azure Pricing** - Fetches live VM, SQL Database, and Storage pricing  
✅ **Intelligent Caching** - Caches prices for 24 hours to reduce API calls  
✅ **Automatic Fallback** - Uses static pricing if real-time APIs fail  
✅ **Rate Limiting** - Built-in rate limit protection  
✅ **Error Handling** - Graceful degradation with fallback to static pricing  

## Setup Instructions

### 1. Install Required Packages

```bash
cd backend
pip install -r requirements.txt
```

The new packages include:
- `boto3` - AWS SDK
- `azure-identity` - Azure authentication
- `azure-mgmt-consumption` - Azure pricing
- `google-cloud-billing` - GCP billing (optional)
- `requests` - HTTP library

### 2. AWS Setup

#### Option A: Using AWS CLI (Recommended)

```bash
# Install AWS CLI if not already installed
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# Configure credentials
aws configure

# Enter when prompted:
# - AWS Access Key ID: <your-access-key>
# - AWS Secret Access Key: <your-secret-key>
# - Default region: us-east-1
# - Default output format: json
```

#### Option B: Using Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

#### Option C: Using .env File

```bash
# Edit or create backend/.env
AWS_REGION=us-east-1
```

**Get AWS Credentials:**
1. Go to AWS Console → IAM → Users
2. Create new user or use existing one
3. Create access key (programmatic access)
4. Store Access Key ID and Secret Access Key securely

**Required IAM Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "pricing:GetProducts"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. Azure Setup

#### Option A: Using Azure CLI (Recommended)

```bash
# Install Azure CLI if not already installed
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "subscription-id"
```

#### Option B: Using Service Principal

```bash
# Create service principal
az ad sp create-for-rbac --name "InfraPilot"

# Note the output with credentials
# Set environment variable:
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

#### Option C: Using .env File

```bash
# Edit or create backend/.env
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

**Azure Pricing API:**
- Uses public Azure Retail Prices API (no authentication needed for basic queries)
- Supports advanced queries with Azure CLI credentials

### 4. GCP Setup (Optional - Currently Static Pricing Only)

For full GCP real-time pricing support:

```bash
# Create service account
gcloud iam service-accounts create infrapilot

# Create and download key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=infrapilot@PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-project-id"
```

### 5. Configuration

Copy `.env.example` to `.env` and update values:

```bash
cp backend/.env.example backend/.env
```

**Key Configuration Options:**

```env
# Pricing cache (24 hours default)
PRICING_CACHE_TTL_HOURS=24
PRICING_CACHE_DIR=./pricing_cache

# Fallback to static pricing if APIs fail
USE_FALLBACK_PRICING=true

# API rate limiting
PRICING_API_RATE_LIMIT=60

# Currency
DEFAULT_CURRENCY=USD
```

## Usage

### Via Frontend

1. Navigate to the **FinOps** tab
2. Enter or load Terraform code
3. Click **"Calculate Pricing"**
4. Results show real-time prices (marked as "real-time API")

### Via API

```bash
curl -X POST http://localhost:8001/api/v1/pricing/calculate-pricing \
  -H "Content-Type: application/json" \
  -d '{
    "terraform_code": "resource \"aws_instance\" \"web\" { ... }",
    "include_breakdown": true,
    "include_comparison": true
  }'
```

### Check Pricing Source

```bash
curl http://localhost:8001/api/v1/pricing/pricing-formats
```

Response includes:
- `pricing_source`: "real-time APIs with static fallback"
- `real_time_apis_available`: Shows which providers support real-time
- `setup_instructions`: How to enable for each provider

## How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│     User Input (Terraform Code)         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Terraform Parser                     │
│    (Extracts Resources)                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Real-Time Pricing Fetcher            │
│    ├─ AWS Pricing API                   │
│    ├─ Azure Pricing API                 │
│    └─ GCP Pricing API (fallback)        │
└────────────────┬────────────────────────┘
                 │
                 ▼ (with Cache)
         ┌───────┴────────┐
         │                │
    Cache Hit?        Cache Miss?
         │                │
         └─ Return       ▼
           Cached      API Call
           Price   ┌─────────────┐
                   │ Query Cloud │
                   │   Provider  │
                   └─────┬───────┘
                         │
            ┌────────────┴────────────┐
            │                         │
         Success              Fallback
            │                 to Static
            ▼                 Pricing
        Cache & Return        │
        Real-Time Price       ▼
                          Return Static
                          Price
                 │
                 ▼
    ┌─────────────────────────────────┐
    │    Cost Aggregation             │
    │    Per Provider                 │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │    Cost Comparison & Analysis   │
    │    Generate Recommendations     │
    └────────────────┬────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  Return Results │
            │  to Frontend    │
            └────────────────┘
```

### Caching Strategy

- **First Call**: Fetch from API, cache result
- **Subsequent Calls**: Serve from cache (24 hours default)
- **Cache Expiration**: Automatically re-fetch from API
- **Cache Storage**: `./pricing_cache/` directory

### Error Handling

```
Real-Time API Call
    │
    ├─ Success → Cache & Return Real-Time Price
    │
    └─ Failure → Log Warning → Use Static Pricing
                   (if enabled)
```

## Troubleshooting

### AWS Pricing API Not Working

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check permissions
aws iam list-user-policies --user-name your-user

# Enable debug logging
export AWS_DEBUG=true
```

### Azure Pricing API Not Working

```bash
# Check Azure login
az account show

# List subscriptions
az account list

# Check active subscription
az account show
```

### Cache Issues

```bash
# Clear cache
rm -rf backend/pricing_cache

# Disable cache (check fresh prices)
# Edit .env: PRICING_CACHE_TTL_HOURS=0
```

### Performance

- First request: 1-3 seconds (API call)
- Cached requests: <100ms
- Fallback static: <50ms

## API Response Format

```json
{
  "success": true,
  "total_costs": {
    "aws": 123.45,
    "azure": 145.67,
    "gcp": 98.76
  },
  "breakdown": {
    "aws": [
      {
        "name": "web-server",
        "type": "ec2",
        "cost": 50.00,
        "description": "EC2 t3.medium (real-time API)"
      }
    ]
  },
  "comparison": {
    "cheapest_provider": "gcp",
    "monthly_costs": {...},
    "annual_costs": {...},
    "savings_potential": {
      "aws": {"monthly_savings": 50, "annual_savings": 600}
    }
  }
}
```

## Limitations & Future Enhancements

### Current Limitations
- GCP pricing requires manual setup (not real-time in current version)
- Spot instances and reserved instances not included
- Data transfer costs between regions not calculated
- Discounts not applied

### Future Enhancements
1. GCP real-time pricing integration
2. Reserved instances pricing
3. Spot instance discounts
4. Data transfer cost calculations
5. Custom regional pricing
6. Bulk discount support
7. Commitment-based pricing

## Support & Debugging

Enable detailed logging:

```python
# In pricing_config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View cache contents:

```bash
ls -la backend/pricing_cache/
cat backend/pricing_cache/hash.json
```

Monitor API calls:

```bash
# Watch logs while running
tail -f backend/pricing_cache/pricing.log
```

## References

- [AWS Pricing API Documentation](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetProducts.html)
- [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices)
- [GCP Pricing Calculator API](https://cloud.google.com/architecture/automating-cost-calculation)
- [Boto3 Pricing Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html)
