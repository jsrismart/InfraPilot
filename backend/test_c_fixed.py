#!/usr/bin/env python3
"""Test C-series VM pricing directly through the pricing calculator"""

import sys
sys.path.insert(0, '.')

from pricing_calculator import CloudPricingCalculator
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
    calculator = CloudPricingCalculator()
    result = calculator.calculate_pricing(terraform_code, include_breakdown=True)
    
    print("\n[SUCCESS]")
    azure_cost = result.get('total_costs', {}).get('azure', 0)
    print("Total Azure Cost: ${:.2f}/month".format(azure_cost))
    
    print("\nResource Breakdown:")
    for resource in result.get('breakdown', {}).get('azure', []):
        print("\n  Name: {}".format(resource['name']))
        print("  Type: {}".format(resource['type']))
        print("  Cost: ${:.2f}/month".format(resource['cost']))
        print("  Description: {}".format(resource['description']))
        
except Exception as e:
    print("\n[ERROR]: {}".format(e))
    import traceback
    traceback.print_exc()
