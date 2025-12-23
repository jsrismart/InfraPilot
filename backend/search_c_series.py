#!/usr/bin/env python3
"""Search for available VMs in Azure API"""

import requests

url = "https://prices.azure.com/api/retail/prices"

print("=" * 80)
print("Searching for C-series VMs in Azure API")
print("=" * 80)

# Try different search patterns
search_patterns = [
    ("contains(skuName, 'C')", "SKU name contains 'C'"),
    ("contains(armSkuName, 'C')", "ARM SKU name contains 'C'"),
    ("productName eq 'Virtual Machines Windows'", "Windows VMs"),
    ("productName eq 'Virtual Machines Linux'", "Linux VMs"),
]

for filter_str, description in search_patterns:
    print(f"\n{description}:")
    print(f"  Filter: {filter_str}")
    
    params = {
        '$filter': filter_str,
        '$top': 5,
        '$skip': 0
    }
    
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        items = response.json().get('Items', [])
        print(f"  Found: {items and len(items) or 0} items")
        if items:
            for item in items[:3]:
                print(f"    - {item.get('skuName')} ({item.get('armSkuName')})")
    else:
        print(f"  Error: {response.status_code}")

# Now specifically test if C-series even exists
print("\n" + "=" * 80)
print("Checking if C-series exists (testing multiple names)")
print("=" * 80)

test_names = [
    'Standard_C2s_v3',
    'Standard_C4s_v3',
    'Standard_C4c_v3',
    'Standard_C8s_v3',
    'Standard_D2s_v3',  # Control - we know this works
]

for name in test_names:
    params = {
        '$filter': f"armSkuName eq '{name}'",
        '$top': 1
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        found = len(response.json().get('Items', []))
        status = "✓" if found else "✗"
        print(f"{status} {name}: {found} item(s)")
