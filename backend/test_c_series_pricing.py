#!/usr/bin/env python3
"""Test C-series VM pricing from Azure API"""

import requests
import json

url = "https://prices.azure.com/api/retail/prices"

# Test C4c_v3
print("=" * 80)
print("Testing Standard_C4c_v3 pricing from Azure API")
print("=" * 80)

params = {
    '$filter': "armSkuName eq 'Standard_C4c_v3'",
    '$top': 50
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    items = data.get('Items', [])
    print(f"\n✓ Found {len(items)} items for Standard_C4c_v3")
    
    if items:
        print("\nAll matching items:")
        for i, item in enumerate(items[:15], 1):
            print(f"\n{i}. {item.get('skuName')}")
            print(f"   Region: {item.get('armRegionName')}")
            print(f"   Meter: {item.get('meterName')}")
            print(f"   Price: ${item.get('retailPrice')} / {item.get('unitOfMeasure')}")
            print(f"   Product: {item.get('productName')}")
    else:
        print("\n✗ No results found for Standard_C4c_v3")
else:
    print(f"✗ Error: {response.status_code}")

# Also test other C-series
print("\n" + "=" * 80)
print("Testing other C-series VMs")
print("=" * 80)

for vm in ['Standard_C2s_v3', 'Standard_C4s_v3', 'Standard_C8s_v3']:
    params = {
        '$filter': f"armSkuName eq '{vm}'",
        '$top': 5
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        items = response.json().get('Items', [])
        print(f"\n{vm}: {len(items)} items found")
        if items:
            item = items[0]
            print(f"  Price: ${item.get('retailPrice')} / {item.get('unitOfMeasure')}")
    else:
        print(f"\n{vm}: Error {response.status_code}")
