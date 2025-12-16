#!/usr/bin/env python3
"""Test complete pricing with all Azure resources"""

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

response = requests.post(
    "http://localhost:8001/api/v1/pricing/calculate-pricing",
    json={
        "terraform_code": terraform_code,
        "include_breakdown": True
    }
)

data = response.json()
print("="*60)
print("PRICING AFTER FIX")
print("="*60)
print(f"\nAzure Total: ${data['total_costs']['azure']:.2f}/month")
print("\nBreakdown:")
for resource in data['breakdown']['azure']:
    print(f"  - {resource['name']}: ${resource['cost']:.2f}")
    print(f"    Type: {resource['type']}")
    print(f"    Details: {resource['description']}\n")
