#!/usr/bin/env python3
import requests

url = 'https://prices.azure.com/api/retail/prices'

# Search for Windows Virtual Machine pricing
params = {
    '$filter': "contains(productName, 'Windows Virtual Machines')",
    '$top': 5,
    '$skip': 0
}

print("Searching for Windows Virtual Machines...\n")

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    print(f'Found {len(data.get("Items", []))} items\n')
    for i, item in enumerate(data.get('Items', [])[:5]):
        if 'B1s' in item.get('skuName', ''):
            print(f"✓ {item.get('skuName')} - ${item.get('retailPrice')} / {item.get('unitOfMeasure')}")
            print(f"  Location: {item.get('location')}\n")

# Also try Linux
print("\nSearching for Linux Virtual Machines...\n")
params['$filter'] = "contains(productName, 'Linux Virtual Machines')"

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    print(f'Found {len(data.get("Items", []))} items\n')
    for i, item in enumerate(data.get('Items', [])[:5]):
        if 'B1s' in item.get('skuName', ''):
            print(f"✓ {item.get('skuName')} - ${item.get('retailPrice')} / {item.get('unitOfMeasure')}")
            print(f"  Location: {item.get('location')}\n")
