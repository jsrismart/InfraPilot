#!/usr/bin/env python3
"""
Deep dive into Azure pricing API response
"""

import requests
import json

url = "https://prices.azure.com/api/retail/prices"

# Region mapping and validation
import os, re
REGION_MAP = {
    "eastus": "East US",
    "eastus2": "East US 2",
    "westeurope": "West Europe",
    # add others as needed
}

region = os.environ.get("PRICING_REGION", "eastus")
if not region or "azurerm_resource_group" in region or not re.match(r'^[a-z0-9-]+$', region):
    raise SystemExit("Invalid region value: " + repr(region))

api_region = REGION_MAP.get(region, region)
print(f"Using region for API call: {api_region}")

params = {
    'region': api_region,
    '$filter': "serviceFamily eq 'Virtual Machines'",
    '$top': 3
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data.get('Items', []))} items:\n")
    for i, item in enumerate(data.get('Items', [])[:3]):
        print(f"{i+1}. {item.get('skuName')}")
        print(f"   Retail Price: ${item.get('retailPrice')}")
        print(f"   Unit: {item.get('unitOfMeasure')}")
        print(f"   Product: {item.get('productName')}")
        print(f"   Meter: {item.get('meterName')}")
        print(f"   Location: {item.get('location')}")
        print()
