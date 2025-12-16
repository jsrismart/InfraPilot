#!/usr/bin/env python3
"""Test the full API flow"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1"

print("=" * 60)
print("TESTING INFRAPILOT API")
print("=" * 60)

# Wait for server to start
time.sleep(2)

# Test 1: Health Check
print("\n[1] Health Check")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: IaC Generation
print("\n[2] IaC Generation")
print("-" * 60)
try:
    payload = {
        "prompt": "Create an Azure VM with D2_v3 size in East US region"
    }
    response = requests.post(f"{BASE_URL}/infra/generate-iac", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"IaC files generated: {list(result.get('iac', {}).keys())}")
    
    # Check what was generated
    for filename, content in result.get('iac', {}).items():
        lines = len(content.split('\n'))
        print(f"  - {filename}: {lines} lines")
        
except Exception as e:
    print(f"Error: {e}")

# Test 3: Pricing Calculation
print("\n[3] Pricing Calculation")
print("-" * 60)
try:
    # Use a simple Terraform code
    terraform_code = '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "D2_v3"
}
'''
    payload = {
        "terraform_code": terraform_code,
        "include_breakdown": True,
        "include_comparison": True
    }
    response = requests.post(f"{BASE_URL}/pricing/calculate-pricing", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Total Costs: {result.get('total_costs')}")
    print(f"Monthly Estimate: {result.get('monthly_estimate')}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Diagram Generation
print("\n[4] Diagram Generation (ASCII)")
print("-" * 60)
try:
    terraform_code = '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "D2_v3"
}
'''
    payload = {
        "terraform_code": terraform_code,
        "diagram_type": "ascii"
    }
    response = requests.post(f"{BASE_URL}/diagram/generate-diagram", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Diagram Type: {result.get('diagram_type')}")
    if result.get('content'):
        print(f"Content Preview (first 200 chars):\n{result.get('content')[:200]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("API TESTING COMPLETE")
print("=" * 60)
