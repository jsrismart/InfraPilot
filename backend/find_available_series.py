#!/usr/bin/env python3
"""Find available VM series in Azure API"""

import requests

url = "https://prices.azure.com/api/retail/prices"

print("=" * 80)
print("Finding available VM series in Azure API")
print("=" * 80)

# Get all VM products
params = {
    '$filter': "contains(productName, 'Virtual Machine')",
    '$top': 100,
}

response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    items = response.json().get('Items', [])
    print(f"\nFound {len(items)} items with 'Virtual Machine'")
    
    # Extract unique products
    products = set()
    for item in items:
        products.add(item.get('productName', 'Unknown'))
    
    print(f"\nUnique products ({len(products)}):")
    for p in sorted(products)[:20]:
        print(f"  - {p}")

# Now search for specific VM SKU patterns
print("\n" + "=" * 80)
print("Testing common VM series patterns")
print("=" * 80)

series_to_test = [
    ('Standard_A', 'A-series'),
    ('Standard_B', 'B-series'),
    ('Standard_D', 'D-series'),
    ('Standard_E', 'E-series'),
    ('Standard_F', 'F-series'),
    ('Standard_G', 'G-series'),
    ('Standard_H', 'H-series'),
    ('Standard_L', 'L-series'),
    ('Standard_M', 'M-series'),
    ('Standard_N', 'N-series'),
    ('Standard_C', 'C-series'),  # The problem one
]

for prefix, name in series_to_test:
    params = {
        '$filter': f"startswith(armSkuName, '{prefix}')",
        '$top': 1
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        items = response.json().get('Items', [])
        if items:
            example = items[0].get('armSkuName', '')
            print(f"✓ {name:15} - Found (example: {example})")
        else:
            print(f"✗ {name:15} - NOT FOUND")
