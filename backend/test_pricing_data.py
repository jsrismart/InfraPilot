#!/usr/bin/env python3
"""Test pricing data being returned from the API"""

import requests
import json

terraform_code = """
resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-vm"
  location            = "East US"
  resource_group_name = "example-rg"
  size                = "Standard_D2s_v4"
}

resource "azurerm_resource_group" "example" {
  name     = "example-rg"
  location = "East US"
}

resource "azurerm_virtual_network" "example" {
  name                = "example-vnet"
  location            = "East US"
  resource_group_name = "example-rg"
  address_space       = ["10.0.0.0/16"]
}
"""

url = "http://localhost:8001/api/v1/pricing/calculate-pricing"
payload = {
    "terraform_code": terraform_code,
    "include_breakdown": True,
    "include_comparison": True
}

print("Testing pricing endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)[:200]}...")
print()

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nResponse Data:")
        print(json.dumps(data, indent=2))
        
        print("\n" + "="*60)
        print("PRICING SUMMARY:")
        print("="*60)
        if 'total_costs' in data:
            for provider, cost in data['total_costs'].items():
                print(f"{provider.upper()}: ${cost:.2f}/month")
        
        print("\nBREAKDOWN (Azure):")
        if 'breakdown' in data and 'azure' in data['breakdown']:
            for resource in data['breakdown']['azure']:
                print(f"  - {resource['name']}: ${resource['cost']:.2f} ({resource['description']})")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
