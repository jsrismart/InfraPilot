#!/usr/bin/env python3
"""Test the pricing flow"""
import json
from pricing_calculator import calculate_terraform_pricing

terraform_code = '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "vm"
  location            = "East US"
  resource_group_name = "rg"
  vm_size             = "D2_v3"
}
'''

print("Testing pricing calculator with Azure VM...")
print(f"Input Terraform code:\n{terraform_code}\n")

result = calculate_terraform_pricing(terraform_code)

print("Pricing Result:")
print(json.dumps(result, indent=2))
