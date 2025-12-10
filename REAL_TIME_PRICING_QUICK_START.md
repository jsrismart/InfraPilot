# Real-Time Pricing - Quick Start Guide

## 5-Minute Setup

### For AWS Users

```bash
# 1. Install packages
cd backend
pip install boto3 requests -q

# 2. Configure AWS
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1)

# 3. Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 4. Test
curl http://localhost:8001/api/v1/pricing/pricing-formats
```

### For Azure Users

```bash
# 1. Install packages
cd backend
pip install azure-identity requests -q

# 2. Login to Azure
az login
az account list
az account set --subscription "your-subscription-id"

# 3. Create .env
echo 'AZURE_SUBSCRIPTION_ID=your-subscription-id' >> .env

# 4. Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 5. Test
curl http://localhost:8001/api/v1/pricing/pricing-formats
```

### For Both AWS + Azure

```bash
# 1. Install all packages
cd backend
pip install boto3 azure-identity requests -q

# 2. Configure both
aws configure           # For AWS
az login               # For Azure

# 3. Edit .env
cat > .env << 'EOF'
AWS_REGION=us-east-1
AZURE_SUBSCRIPTION_ID=your-subscription-id
PRICING_CACHE_TTL_HOURS=24
USE_FALLBACK_PRICING=true
EOF

# 4. Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 5. Test
curl http://localhost:8001/api/v1/pricing/pricing-formats | jq '.real_time_apis_available'
```

## Verify It's Working

```bash
# Check pricing source
curl http://localhost:8001/api/v1/pricing/pricing-formats | jq '.pricing_source'

# Should show: "real-time APIs with static fallback" (if configured)
```

## What Happens Now

1. **First Calculation** → Real-time API call (1-3 seconds)
2. **Result** → Cached locally (24 hours)
3. **Next Calculation** → Served from cache (<100ms)
4. **Price Changes** → Auto-fetched next day

## Expected Output

When calculating pricing with real-time enabled:

```
Backend logs will show:
✓ AWS Pricing API client initialized
✓ Azure Pricing API client initialized
✓ Cache hit for: aws_ec2_t3_micro_us-east-1
→ Using real-time pricing for aws ec2 t3.micro
```

## If Something Goes Wrong

### No Real-Time Pricing?

**Check if APIs are configured:**
```bash
# AWS
aws sts get-caller-identity

# Azure
az account show
```

**Check logs:**
```bash
# Should see "Real-time pricing fetcher imported successfully"
python -c "from real_time_pricing_fetcher import pricing_fetcher; print('OK')"
```

### Fallback to Static?

**This is normal if:**
- AWS/Azure credentials not configured
- API rate limit reached
- Network issues
- Services disabled

The system will automatically fall back to accurate static pricing.

## Full Documentation

For complete setup guide with troubleshooting:
- See `REAL_TIME_PRICING_SETUP.md` (comprehensive guide)
- See `REAL_TIME_PRICING_IMPLEMENTATION.md` (technical details)

## Next Steps

1. ✅ Install packages
2. ✅ Configure cloud credentials
3. ✅ Start backend server
4. ✅ Test with FinOps → Calculate Pricing
5. ✅ See real-time prices in results!

## Performance

- **Real-time API**: 1-3 seconds (first time)
- **Cached**: <100ms (same day)
- **Static fallback**: <50ms (if APIs fail)

That's it! You now have real-time cloud pricing integrated into InfraPilot. 🚀
