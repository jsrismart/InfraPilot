#!/usr/bin/env python3
"""
Test Azure connectivity via pricing API
"""

import requests
import json

print("=" * 60)
print("Testing Real-Time Pricing with Azure")
print("=" * 60)

# Test 1: Check pricing API status
print("\n[TEST 1] Check pricing API status")
response = requests.get("http://127.0.0.1:8001/api/v1/pricing/pricing-formats")
if response.status_code == 200:
    data = response.json()
    print(f"✓ API responsive")
    print(f"  Pricing Source: {data.get('pricing_source', 'N/A')}")
    print(f"  Real-time APIs Available: {data.get('real_time_apis_available', {})}")
else:
    print(f"✗ Error: {response.status_code}")

# Test 2: Calculate Azure pricing
print("\n[TEST 2] Calculate Azure pricing")
payload = {
    "terraform_code": '''
    resource "azurerm_virtual_machine" "example" {
      vm_size = "Standard_B1"
    }
    ''',
    "include_breakdown": True
}

response = requests.post(
    "http://127.0.0.1:8001/api/v1/pricing/calculate-pricing",
    json=payload
)

if response.status_code == 200:
    data = response.json()
    print(f"✓ Pricing calculated")
    print(f"  Total Cost: ${data.get('total_costs', {}).get('azure', 0):.2f}")
    if 'breakdown' in data and 'azure' in data['breakdown']:
        breakdown = data['breakdown']['azure']
        print(f"  Breakdown items: {len(breakdown)}")
        for item in breakdown[:2]:
            print(f"    - {item.get('resource_type', 'N/A')}: ${item.get('cost', 0):.2f}")
else:
    print(f"✗ Error: {response.status_code}")
    print(f"  Response: {response.text[:200]}")

# Test 3: Compare providers
print("\n[TEST 3] Compare AWS vs Azure pricing")
payload = {
    "terraform_code": '''
    resource "aws_instance" "web" {
      instance_type = "t3.micro"
    }
    resource "azurerm_virtual_machine" "vm" {
      vm_size = "Standard_B1"
    }
    '''
}

response = requests.post(
    "http://127.0.0.1:8001/api/v1/pricing/compare-pricing",
    json=payload
)

if response.status_code == 200:
    data = response.json()
    print(f"✓ Comparison generated")
    print(f"  AWS: ${data.get('breakdown', {}).get('aws', [{}])[0].get('cost', 0):.2f}")
    print(f"  Azure: ${data.get('breakdown', {}).get('azure', [{}])[0].get('cost', 0):.2f}")
else:
    print(f"✗ Error: {response.status_code}")

print("\n" + "=" * 60)
print("✓ Azure connectivity test complete!")
print("=" * 60)
