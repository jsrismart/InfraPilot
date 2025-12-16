#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test live Azure pricing integration"""

import time
import requests
import json
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Wait for backend to be ready
time.sleep(3)

print("=" * 80)
print("TESTING LIVE AZURE PRICING FROM AZURE.MICROSOFT.COM API")
print("=" * 80)
print()

# Test cases with Terraform code
test_cases = [
    {
        "name": "D32a V4 (32 vCPU, 128GB RAM)",
        "terraform": """
resource "azurerm_virtual_machine" "d32a_vm" {
  name                  = "d32a-vm"
  location              = "eastus"
  resource_group_name   = "my-rg"
  vm_size               = "Standard_D32a_v4"
  
  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
  }
}
"""
    },
    {
        "name": "Standard_B1s (1 vCPU, 1GB RAM)",
        "terraform": """
resource "azurerm_virtual_machine" "b1s_vm" {
  name                  = "b1s-vm"
  location              = "eastus"
  resource_group_name   = "my-rg"
  vm_size               = "Standard_B1s"
  
  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
  }
}
"""
    },
    {
        "name": "Standard_D2s_v4 (2 vCPU, 8GB RAM)",
        "terraform": """
resource "azurerm_virtual_machine" "d2s_vm" {
  name                  = "d2s-vm"
  location              = "eastus"
  resource_group_name   = "my-rg"
  vm_size               = "Standard_D2s_v4"
  
  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
  }
}
"""
    }
]

for test_case in test_cases:
    print(f"\n[TEST] {test_case['name']}")
    print("-" * 80)
    
    try:
        payload = {
            "terraform_code": test_case['terraform'],
            "include_breakdown": True,
            "include_comparison": True
        }
        
        response = requests.post(
            "http://localhost:8001/api/v1/pricing/calculate-pricing",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"[SUCCESS] Status: {response.status_code}")
            
            total_costs = data.get('total_costs', {})
            if 'azure' in total_costs:
                azure_cost = total_costs['azure']
                print(f"[COST] Azure Monthly: ${azure_cost:.2f}")
            
            breakdown = data.get('breakdown', {})
            if 'azure' in breakdown:
                print(f"\n[BREAKDOWN] Resources:")
                for resource in breakdown['azure']:
                    print(f"  - {resource.get('name', 'Unknown')}")
                    print(f"    Type: {resource.get('type', '')}")
                    print(f"    Cost: ${resource.get('cost', 0):.2f}/month")
                    print(f"    Details: {resource.get('description', '')}")
        else:
            print(f"[ERROR] Status {response.status_code}")
            print(f"Response: {response.text[:300]}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
    
    time.sleep(1)

print("\n" + "=" * 80)
print("TEST COMPLETE - Pricing fetched directly from Azure API")
print("=" * 80)
