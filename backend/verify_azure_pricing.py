#!/usr/bin/env python3
"""
Verify Azure pricing accuracy against real Azure Retail Prices API
"""

import requests
import json
from real_time_pricing_fetcher import AzurePricingFetcher

print("="*70)
print("AZURE PRICING VERIFICATION")
print("="*70)

# Test data from the screenshot
test_cases = [
    {
        'name': 'VM Standard_B1s',
        'sku': 'Standard_B1s',
        'expected_monthly': 8.76,  # From screenshot
    },
    {
        'name': 'Subnet (Azure estimate)',
        'resource': 'azurerm_subnet',
        'expected_monthly': 4.00,
    },
    {
        'name': 'Public IP (Azure estimate)',
        'resource': 'azurerm_public_ip',
        'expected_monthly': 4.00,
    },
]

print("\n1. DIRECT AZURE API VERIFICATION")
print("-"*70)

# Get pricing directly from Azure API
url = "https://prices.azure.com/api/retail/prices"

print("\nVM Standard_B1s:")
params = {
    '$filter': "contains(skuName, 'Standard_B1')",
    '$top': 1
}
response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
    items = response.json().get('Items', [])
    if items:
        hourly_price = float(items[0]['retailPrice'])
        monthly_price = hourly_price * 730  # 730 hours/month average
        print(f"  Hourly: ${hourly_price:.4f}")
        print(f"  Monthly: ${monthly_price:.2f}")
        print(f"  Screenshot shows: $8.76/month")
        if abs(monthly_price - 8.76) < 0.5:
            print("  ✓ MATCHES - Pricing is correct!")
        else:
            print(f"  ⚠ DISCREPANCY - {abs(monthly_price - 8.76):.2f} difference")

print("\n2. FETCHER VERIFICATION")
print("-"*70)

fetcher = AzurePricingFetcher()
if fetcher.enabled:
    print("\nFetching VM pricing via AzurePricingFetcher...")
    price = fetcher.get_vm_pricing('Standard_B1s', 'eastus')
    if price:
        monthly = price * 730
        print(f"  Hourly: ${price:.4f}")
        print(f"  Monthly: ${monthly:.2f}")
        print("  ✓ Fetcher working correctly")
else:
    print("✗ Azure fetcher not enabled")

print("\n3. BACKEND API VERIFICATION")
print("-"*70)

payload = {
    "terraform_code": '''
    resource "azurerm_virtual_machine" "vm" {
      vm_size = "Standard_B1s"
    }
    ''',
    "include_breakdown": True
}

print("\nCalling backend pricing API...")
response = requests.post(
    "http://localhost:8001/api/v1/pricing/calculate-pricing",
    json=payload
)

if response.status_code == 200:
    data = response.json()
    
    print("\nResponse from Backend:")
    print(f"  Total Azure Cost: ${data.get('total_costs', {}).get('azure', 0):.2f}")
    
    if 'breakdown' in data and 'azure' in data['breakdown']:
        print(f"\n  Breakdown ({len(data['breakdown']['azure'])} items):")
        for item in data['breakdown']['azure']:
            print(f"    - {item.get('resource_name', 'N/A')}")
            print(f"      Type: {item.get('resource_type', 'N/A')}")
            print(f"      Cost: ${item.get('cost', 0):.2f}/month")
    
    # Verify against screenshot
    backend_cost = data.get('total_costs', {}).get('azure', 0)
    screenshot_cost = 8.76
    
    print(f"\n  Backend calculates: ${backend_cost:.2f}")
    print(f"  Screenshot shows: ${screenshot_cost:.2f}")
    
    if abs(backend_cost - screenshot_cost) < 0.5:
        print("  ✓ PRICING VERIFIED - Costs match!")
    else:
        print(f"  ⚠ DISCREPANCY - Difference: ${abs(backend_cost - screenshot_cost):.2f}")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)

print("\n4. PRICING SOURCE VERIFICATION")
print("-"*70)

response = requests.get("http://localhost:8001/api/v1/pricing/pricing-formats")
if response.status_code == 200:
    data = response.json()
    print(f"\nPricing Source: {data.get('pricing_source', 'Unknown')}")
    print(f"Real-time APIs Available:")
    for provider, available in data.get('real_time_apis_available', {}).items():
        status = "✓ Available" if available else "✗ Unavailable"
        print(f"  - {provider.upper()}: {status}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70 + "\n")
