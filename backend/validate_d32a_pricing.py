#!/usr/bin/env python3
"""
Validate Azure pricing for D32a V4 instance
"""

import requests

print("="*70)
print("AZURE D32a V4 PRICING VALIDATION")
print("="*70)

# Test 1: Search Azure Retail Prices API for D32a V4
print("\n[TEST 1] Searching Azure Retail Prices API for D32a V4")
url = 'https://prices.azure.com/api/retail/prices'
params = {
    '$filter': "contains(skuName, 'D32a')",
    '$top': 10
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    items = data.get('Items', [])
    print(f"Found {len(items)} D32a variants:\n")
    
    for item in items[:5]:
        print(f"  SKU: {item.get('skuName')}")
        print(f"  Product: {item.get('productName')}")
        print(f"  Price: ${item.get('retailPrice')} / {item.get('unitOfMeasure')}")
        print(f"  Location: {item.get('location')}")
        print()

# Test 2: Search for Standard_D32s_v4 (common Windows variant)
print("\n[TEST 2] Search for Standard_D32s_v4")
params = {
    '$filter': "contains(skuName, 'Standard_D32s_v4')",
    '$top': 5
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    items = data.get('Items', [])
    if items:
        print(f"Found {len(items)} items:")
        for item in items[:2]:
            hourly = float(item.get('retailPrice'))
            monthly = hourly * 730
            print(f"  {item.get('skuName')} @ {item.get('location')}")
            print(f"  Hourly: ${hourly:.4f}")
            print(f"  Monthly: ${monthly:.2f}\n")
    else:
        print("No exact matches found. D32s_v4 might not be in public pricing API")

# Test 3: What the system should calculate
print("\n[TEST 3] Expected Pricing")
print("\nFor D32a V4 (8 vCPU, 128 GB RAM) in East US:")
print("  • Hourly rate: ~$1.56-1.92 (typical for D32 series)")
print("  • Monthly (730 hrs): ~$1,138-1,401")
print("  • Screenshot shows: $20.00 total")
print("\n  ⚠ DISCREPANCY: $20 is too low for D32a V4!")
print("     This would be valid for smaller SKUs like B2s or similar")

print("\n" + "="*70)
