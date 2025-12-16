#!/usr/bin/env python3
"""
Find correct Azure VM pricing
"""

import requests

url = "https://prices.azure.com/api/retail/prices"

# Search for "Virtual Machine" or "Compute"
print("Searching for Virtual Machine pricing for B1s...\n")

params = {
    '$filter': "contains(productName, 'Virtual Machines') and contains(skuName, 'B1s')",
    '$top': 3
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data.get('Items', []))} items:\n")
    
    for i, item in enumerate(data.get('Items', [])[:3]):
        print(f"{i+1}. {item.get('skuName')}")
        print(f"   Product: {item.get('productName')}")
        print(f"   Price: ${item.get('retailPrice')} / {item.get('unitOfMeasure')}")
        print(f"   Location: {item.get('location')}")
        print()
else:
    print(f"Error: {response.status_code}")
