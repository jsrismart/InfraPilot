#!/usr/bin/env python3
"""
Detailed test to see if real-time pricing is being used
"""

import requests
import json

print("="*70)
print("TESTING REAL-TIME PRICING WITH DETAILED OUTPUT")
print("="*70)

# Test 1: Check if fetcher is working
print("\n[TEST 1] Direct Fetcher Test")
from real_time_pricing_fetcher import pricing_fetcher

print(f"AWS Fetcher Enabled: {pricing_fetcher.aws.enabled}")
print(f"Azure Fetcher Enabled: {pricing_fetcher.azure.enabled}")

# Test Azure VM pricing directly
print("\n[TEST 2] Direct Azure VM Pricing via Fetcher")
result = pricing_fetcher.get_pricing('azure', 'vm', 'Standard_B1s')
print(f"Result: {result}")

# Test via API
print("\n[TEST 3] Via Backend API")
payload = {
    "terraform_code": '''resource "azurerm_virtual_machine" "example" {
      vm_size = "Standard_B1s"
    }''',
    "include_breakdown": True
}

response = requests.post(
    "http://localhost:8001/api/v1/pricing/calculate-pricing",
    json=payload
)

if response.status_code == 200:
    data = response.json()
    print(f"Status: 200 OK")
    print(f"Total Azure Cost: ${data.get('total_costs', {}).get('azure', 0):.2f}")
    print(f"Breakdown: {json.dumps(data.get('breakdown', {}), indent=2)}")
else:
    print(f"Error: {response.status_code} - {response.text}")

print("\n" + "="*70)
