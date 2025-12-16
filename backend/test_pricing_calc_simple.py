#!/usr/bin/env python3
"""Debug pricing calculation"""
import sys
import json
sys.path.insert(0, '.')

from pricing_calculator import calculate_terraform_pricing

terraform_code = '''resource "azurerm_windows_virtual_machine" "main" {
  name                = "vm"
  location            = "eastus"
  resource_group_name = "rg"
  vm_size = "Standard_D2s_v3"
}'''

print("Input Terraform:")
print(terraform_code)
print("\n" + "="*60)

result = calculate_terraform_pricing(terraform_code)

print("\nPricing Result:")
print(json.dumps(result, indent=2)[:1000])
