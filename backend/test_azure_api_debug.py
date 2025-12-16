#!/usr/bin/env python
"""Debug Azure pricing API"""
import requests

url = "https://prices.azure.com/api/retail/prices"

# Test 1: D2s_v4 without region
print("Test 1: D2s_v4 ALL regions")
params = {'$filter': "armSkuName eq 'Standard_D2s_v4'", '$top': 10}
r = requests.get(url, params=params, timeout=10)
data = r.json()
print(f"Found: {data.get('Count', 0)} total")
if data.get('Items'):
    print("\nChecking regions and prices:")
    us_east_items = []
    for item in data['Items']:
        region = item.get('armRegionName', '')
        if 'US East' in region or 'eastus' in region.lower():
            us_east_items.append(item)
            print(f"  ✓ {region} - Meter: {item.get('meterName')[:40]} - ${item.get('retailPrice')}")
    
    if not us_east_items:
        print("  No US East items found. Showing all:")
        for item in data['Items'][:5]:
            print(f"    {item.get('armRegionName')} - {item.get('meterName')[:30]} - ${item.get('retailPrice')}")

# Test 2: What armRegionName values actually exist
print("\n\nTest 2: Sample armRegionName values for D2s_v4")
params = {'$filter': "armSkuName eq 'Standard_D2s_v4'", '$top': 20}
r = requests.get(url, params=params, timeout=10)
data = r.json()
regions_seen = set()
for item in data['Items']:
    region = item.get('armRegionName', '')
    if region and region not in regions_seen:
        regions_seen.add(region)
        meter = item.get('meterName', '')
        print(f"  {region:25} - {meter[:40]:40} - ${item.get('retailPrice')}")
        if len(regions_seen) >= 5:
            break
