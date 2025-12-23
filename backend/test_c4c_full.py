#!/usr/bin/env python3
"""Test full pricing calculation for C4c_v3"""

import sys
sys.path.insert(0, '.')

from pricing_calculator import calculate_terraform_pricing
import json

terraform_code = '''provider "azurerm" {
  features {}
}

resource "azurerm_virtual_machine" "vm3" {
  name                  = "vm3"
  location              = "eastus"
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
print("Testing C4c_v3 full pricing flow")
print("=" * 80)

result = calculate_terraform_pricing(terraform_code)

print("\nResult:")
print("Total Azure Cost: ${:.2f}/month".format(result.get('total_costs', {}).get('azure', 0)))

for resource in result.get('breakdown', {}).get('azure', []):
    print("\nResource: {}".format(resource['name']))
    print("  Type: {}".format(resource['type']))
    print("  Cost: ${:.2f}/month".format(resource['cost']))
    print("  Description: {}".format(resource['description']))
