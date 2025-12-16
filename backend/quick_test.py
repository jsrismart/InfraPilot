#!/usr/bin/env python3
"""Simpler test script"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1"

print("Testing API...")
time.sleep(2)

# Test pricing
print("\n=== PRICING API TEST ===")
payload = {
    "terraform_code": '''resource "azurerm_windows_virtual_machine" "example" {
  name                = "vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "D2_v3"
}''',
    "include_breakdown": True,
    "include_comparison": True
}

try:
    response = requests.post(f"{BASE_URL}/pricing/calculate-pricing", json=payload, timeout=15)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Total Costs: {data.get('total_costs')}")
    print(f"Full response:\n{json.dumps(data, indent=2)[:1000]}")
except Exception as e:
    print(f"Error: {e}")

# Test IaC generation
print("\n=== IaC GENERATION TEST ===")
payload = {"prompt": "Create an Azure VM with D2_v3 size in East US"}

try:
    response = requests.post(f"{BASE_URL}/infra/generate-iac", json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"IaC files: {list(data.get('iac', {}).keys())}")
    for name, content in data.get('iac', {}).items():
        print(f"  - {name}: {len(content)} chars")
except Exception as e:
    print(f"Error: {e}")

# Test diagram generation
print("\n=== DIAGRAM GENERATION TEST ===")
payload = {
    "terraform_code": '''resource "azurerm_windows_virtual_machine" "example" {
  name = "vm"
  vm_size = "D2_v3"
}''',
    "diagram_type": "ascii"
}

try:
    response = requests.post(f"{BASE_URL}/diagram/generate-diagram", json=payload, timeout=15)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Diagram content (first 300 chars):\n{str(data.get('content', ''))[:300]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== TESTS COMPLETE ===")
