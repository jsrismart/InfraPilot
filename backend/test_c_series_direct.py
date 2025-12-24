#!/usr/bin/env python3
"""Test C-series pricing directly through the pricing calculator"""

import sys
sys.path.insert(0, '.')

from pricing_calculator import calculate_terraform_pricing
import json

# Terraform code with C-series VM
terraform_code = '''provider "azurerm" {
  features {}
}

variable "project_name" {
  type    = string
  default = "myproject"
}

resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-rg"
  location = "eastus"
}

resource "azurerm_virtual_machine" "vm" {
  name                  = "${var.project_name}-vm"
  location              = azurerm_resource_group.main.location
  resource_group_name   = azurerm_resource_group.main.name
  vm_size               = "Standard_C4c_v3"

  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
  }

  os_profile_windows_config {
    enable_automatic_updates = true
  }

  storage_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }
}
'''

print("=" * 80)
print("Testing C-series VM pricing directly through pricing calculator")
print("=" * 80)

try:
    result = calculate_terraform_pricing(terraform_code, include_breakdown=True)
    
    print("\n✓ Success!")
    print(f"\nTotal Azure Cost: ${result.get('total_costs', {}).get('azure', 0):.2f}/month")
    
    print("\nResource Breakdown:")
    for resource in result.get('breakdown', {}).get('azure', []):
        print(f"\n  Name: {resource['name']}")
        print(f"  Type: {resource['type']}")
        print(f"  Cost: ${resource['cost']:.2f}/month")
        print(f"  Description: {resource['description']}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
