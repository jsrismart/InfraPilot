#!/usr/bin/env python3
"""
Test SQL pricing
"""

import requests

url = 'https://prices.azure.com/api/retail/prices'

# Get any SQL Database items
params = {
    '$filter': "contains(skuName, 'SQL Database')",
    '$top': 10
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    items = data.get('Items', [])
    print(f'Found {len(items)} SQL Database items')
    if items:
        for i, item in enumerate(items[:5]):
            print(f'{i+1}. {item.get("skuName")} = ${item.get("retailPrice")}')
else:
    print(f'Error: {response.text[:200]}')
