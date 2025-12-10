# Real-Time Pricing Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        InfraPilot UI                             │
│                   (React Frontend)                               │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ FinOps Tab → Pricing Calculator                         │    │
│  │ - Input Terraform Code                                  │    │
│  │ - Click "Calculate Pricing"                             │    │
│  │ - See Real-Time Prices                                  │    │
│  └──────────────────────┬──────────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP POST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                         │
│                  /api/v1/pricing/calculate-pricing               │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ pricing.py - API Routes                                 │    │
│  │ - Validates Terraform code                              │    │
│  │ - Calls pricing_calculator.py                           │    │
│  │ - Returns cost estimates                                │    │
│  └──────────────────────┬──────────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│               Pricing Calculator                                 │
│             (pricing_calculator.py)                              │
│                                                                   │
│  1. Parse Terraform code → Extract resources                    │
│  2. For each resource:                                          │
│     ├─ Determine provider (AWS/Azure/GCP)                       │
│     ├─ Get instance type                                        │
│     └─ Call _get_resource_price()                               │
│  3. Aggregate costs per provider                                │
│  4. Generate comparisons                                        │
│  5. Return results                                              │
│                                                                   │
│  └──────────────────────┬──────────────────────────────────────┘
└─────────────────────────┼───────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
  ┌─────────────┐          ┌───────────────────────────┐
  │   Try Real- │──────→  │  Real-Time Pricing        │
  │   Time API  │          │  Fetcher                  │
  │             │          │                           │
  └─────┬───────┘          │  (real_time_pricing_     │
        │                  │   fetcher.py)             │
        │                  │                           │
        │                  │  ┌──────────────────┐    │
        │                  │  │ Pricing Cache    │    │
        │                  │  │ - 24h TTL        │    │
        │                  │  │ - File-based     │    │
        │                  │  │ - JSON storage   │    │
        │                  │  └────────┬─────────┘    │
        │                  │           │              │
        │         ┌────────┴───────────┴─┐            │
        │         │                      │            │
        │    Has Cache?               No Cache?       │
        │         │                      │            │
        │  ┌──────▼─────┐         ┌──────▼──────┐   │
        │  │ Return    │         │ API Call   │   │
        │  │ Cached    │         │ to Cloud   │   │
        │  │ Price     │         │ Provider   │   │
        │  └──────┬─────┘         └──────┬──────┘   │
        │         │                      │          │
        └─────────┼──────────────────────┼──────────┘
                  │          ┌───────────┘
                  │          │
            ┌─────▼──────────▼────────┐
            │  Success?               │
            │                         │
       ┌────┴─────┐            ┌──────┴────┐
       ▼           ▼            ▼           ▼
    Success    Failure     Cache &   Fallback to
       │           │       Return    Static
       │           │       Price     Pricing
       └─────┬─────┴─────────┬────────┴────┐
             │               │              │
             ▼               ▼              ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Real-Time    │  │ Real-Time    │  │ Static       │
    │ Price from   │  │ (Cached)     │  │ Price from   │
    │ Cloud API    │  │              │  │ Fallback     │
    │              │  │              │  │ Tables       │
    │ Example:     │  │              │  │              │
    │ AWS EC2 t3   │  │              │  │ Example:     │
    │ = $0.0416/hr │  │              │  │ AWS EC2 t3   │
    │ = $30.37/mo  │  │              │  │ = $30.37/mo  │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                │
           └─────────────────┼────────────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │  Cost Aggregation              │
            │  - Sum all resource costs      │
            │  - Per provider (AWS/Azure)    │
            │  - Monthly & Annual totals     │
            └────────────┬───────────────────┘
                         │
                         ▼
            ┌────────────────────────────────┐
            │  Cost Comparison               │
            │  - Rank providers by cost      │
            │  - Calculate savings potential │
            │  - Generate recommendations    │
            └────────────┬───────────────────┘
                         │
                         ▼
            ┌────────────────────────────────┐
            │  Return Results to Frontend    │
            │  {                             │
            │    total_costs: {...},         │
            │    breakdown: {...},           │
            │    comparison: {...},          │
            │    pricing_source: "real-time  │
            │                    API"        │
            │  }                             │
            └────────────┬───────────────────┘
                         │
                         ▼
            ┌────────────────────────────────┐
            │  Display in FinOps UI          │
            │  - Monthly/Annual costs        │
            │  - Resource breakdown          │
            │  - Savings recommendations     │
            │  - Pricing source badge        │
            └────────────────────────────────┘
```

## Real-Time Pricing Components

```
┌─────────────────────────────────────────┐
│   Real-Time Pricing Fetcher             │
│   (real_time_pricing_fetcher.py)        │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ RealTimePricingFetcher          │   │
│  │ (Unified Interface)             │   │
│  │                                 │   │
│  │  - AWS Pricing Fetcher          │   │
│  │  - Azure Pricing Fetcher        │   │
│  │  - GCP Pricing Fetcher          │   │
│  │  - Caching Logic                │   │
│  │  - Error Handling               │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│    ┌──────────┼──────────┐              │
│    │          │          │              │
│    ▼          ▼          ▼              │
│  ┌────┐    ┌────┐    ┌────┐            │
│  │AWS │    │AZU│    │GCP │            │
│  │    │    │RE │    │    │            │
│  └┬───┘    └┬───┘    └┬───┘            │
│   │        │         │                │
│   ▼        ▼         ▼                │
│  EC2,    VMs,      Compute,           │
│  RDS,    SQL DB,   Cloud SQL,         │
│  S3      Storage   Cloud Storage      │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Pricing Cache                  │ │
│  │  - File-based storage           │ │
│  │  - 24-hour TTL                  │ │
│  │  - Automatic cleanup            │ │
│  │  - Hash-based keys              │ │
│  └─────────────────────────────────┘ │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Fallback Handler               │ │
│  │  - Static pricing tables        │ │
│  │  - Error recovery               │ │
│  │  - Logging                      │ │
│  └─────────────────────────────────┘ │
│                                       │
└─────────────────────────────────────────┘
```

## Data Flow: First Request vs Cached

### First Request (No Cache)
```
User Input
    │
    ▼
Check Cache ──→ Miss!
    │
    ▼
Call Cloud API
    │
    ├─ AWS: boto3.pricing.get_products()
    ├─ Azure: prices.azure.com/api/retail
    └─ GCP: (requires setup)
    │
    ▼
Parse Response
    │
    ▼
Save to Cache
    │
    ▼
Return to Frontend
    │
    ▼
Display Results
(Timing: 1-3 seconds)
```

### Subsequent Requests (Cached)
```
User Input
    │
    ▼
Check Cache ──→ Hit!
    │
    ▼
Return Cached Result
    │
    ▼
Display Results
(Timing: <100ms)
```

## API Call Sequence

```
Client Browser
    │
    ├─ POST /api/v1/pricing/calculate-pricing
    │  └─ Body: {terraform_code, include_breakdown, include_comparison}
    │
    ▼
Backend API (pricing.py)
    │
    ├─ Validate input
    └─ Call calculate_terraform_pricing()
    │
    ▼
Pricing Calculator
    │
    ├─ Parse Terraform
    ├─ Extract resources
    └─ For each resource:
    │
    ├─ Call _get_resource_price()
    │  │
    │  ▼
    │  Real-Time Pricing Fetcher
    │  │
    │  ├─ Try real-time API
    │  ├─ Check cache
    │  └─ Fallback to static
    │  │
    │  ▼
    │  Return price + source
    │
    ├─ Aggregate costs
    ├─ Generate comparisons
    └─ Build response
    │
    ▼
Return to Client
    │
    ├─ Status: 200 OK
    ├─ total_costs: {aws, azure, gcp}
    ├─ breakdown: {aws: [...], azure: [...]}
    ├─ comparison: {cheapest_provider, savings_potential}
    └─ pricing_source: "real-time API" or "static"
    │
    ▼
Frontend displays results
```

## Configuration Layers

```
.env (Environment Variables)
   │
   ├─ AWS_REGION
   ├─ AZURE_SUBSCRIPTION_ID
   ├─ GCP_PROJECT_ID
   ├─ PRICING_CACHE_TTL_HOURS
   ├─ PRICING_CACHE_DIR
   ├─ USE_FALLBACK_PRICING
   ├─ PRICING_API_RATE_LIMIT
   └─ DEFAULT_CURRENCY
   │
   ▼
pricing_config.py (Configuration Module)
   │
   ├─ AWS_CONFIG
   ├─ AZURE_CONFIG
   ├─ GCP_CONFIG
   ├─ PRICING_CACHE
   ├─ USE_FALLBACK_PRICING
   ├─ RATE_LIMIT
   └─ DEFAULT_CURRENCY
   │
   ▼
real_time_pricing_fetcher.py (Uses config)
   │
   ├─ Initialize with settings
   ├─ Connect to APIs
   └─ Apply cache policy
   │
   ▼
pricing_calculator.py (Integrated)
   │
   └─ Uses fetcher for prices
```

## Error Handling Flow

```
Real-Time API Call
    │
    ├─ Success (1-3s) ────────┐
    │                         │
    ├─ Connection Error ──┐   │
    │                     ▼   │
    ├─ API Error ────→ Log Warning
    │                     │   │
    ├─ Invalid Response   │   │
    │                     ▼   │
    ├─ Timeout ────────→ Return None
    │                     │
    └─ Auth Error        │
                         ▼
    USE_FALLBACK_PRICING = true?
         │                 │
    YES  │              NO │
         ▼                 ▼
    Use Static         Raise Error
    Pricing               │
         │                ▼
         └──────→ Cache & Return
                      Result
```

## Performance Characteristics

```
API Call Performance:
└─ First call: 1-3 seconds (real API)
   ├─ Network: 0.5-1s
   ├─ Parse: 0.1-0.5s
   └─ Cache save: 0.1s

Cached Call Performance:
└─ <100 milliseconds
   ├─ File read: <10ms
   ├─ Parse JSON: <50ms
   └─ Return: <40ms

Fallback Performance:
└─ <50 milliseconds
   ├─ Lookup table: <20ms
   └─ Return: <30ms

Total Response Time:
└─ First request: 2-4 seconds
   ├─ API call: 1-3s
   ├─ Processing: 0.5-1s
   └─ Response: <1s

└─ Cached request: 100-500ms
   ├─ Cache lookup: <100ms
   ├─ Processing: 0.2-0.4s
   └─ Response: <1s
```

This architecture ensures:
✅ Accurate real-time pricing
✅ Fast cached lookups
✅ Reliable fallback mechanism
✅ Minimal API calls
✅ Professional-grade reliability
