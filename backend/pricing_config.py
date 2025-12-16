"""
Configuration for real-time cloud pricing APIs
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Pricing Configuration
AWS_CONFIG = {
    "enabled": True,
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "api_version": "2017-10-15",  # AWS Pricing API version
}

# Azure Pricing Configuration
AZURE_CONFIG = {
    "enabled": True,
    "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID", ""),
    "api_version": "2023-02-01",
    "region": "eastus",
}

# GCP Pricing Configuration
GCP_CONFIG = {
    "enabled": True,
    "project_id": os.getenv("GCP_PROJECT_ID", ""),
    "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
    "region": "us-central1",
}

# Caching Configuration
PRICING_CACHE = {
    "enabled": False,  # DISABLED - Force fresh pricing calculations on every request
    "ttl_hours": int(os.getenv("PRICING_CACHE_TTL_HOURS", "0")),  # No caching
    "cache_dir": os.getenv("PRICING_CACHE_DIR", "./pricing_cache"),
}

# Fallback Configuration (use static pricing if APIs fail)
USE_FALLBACK_PRICING = os.getenv("USE_FALLBACK_PRICING", "true").lower() == "true"

# API Rate Limiting
RATE_LIMIT = {
    "enabled": True,
    "requests_per_minute": int(os.getenv("PRICING_API_RATE_LIMIT", "60")),
}

# Currency
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
