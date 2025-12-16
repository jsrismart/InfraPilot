#!/usr/bin/env python3
import requests

url = 'https://prices.azure.com/api/retail/prices'
params = {
    '$filter': "contains(skuName, 'Standard_B1')",
    '$top': 1
}

response = requests.get(url, params=params, timeout=10)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    items = data.get('Items', [])
    print(f'Found {len(items)} items')
    if items:
        print(f'Price: ${items[0].get("retailPrice")} / {items[0].get("unitOfMeasure")}')
        print(f'SKU: {items[0].get("skuName")}')
        hourly = float(items[0].get('retailPrice'))
        monthly = hourly * 730
        print(f'Monthly: ${monthly:.2f}')
else:
    print(f'Error: {response.text}')
