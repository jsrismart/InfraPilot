#!/usr/bin/env python3
"""Test API endpoint for C4c_v3"""

import requests
import json

terraform = '''provider "azurerm" {
  features {}
}

resource "azurerm_virtual_machine" "vm3" {
  name = "vm3"
  vm_size = "Standard_C4c_v3"
  os_profile {
    computer_name = "h"
    admin_username = "a"
  }
  os_profile_windows_config {
    enable_automatic_updates = true
  }
  storage_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer = "WindowsServer"
    sku = "2019-Datacenter"
    version = "latest"
  }
}
'''

payload = {'terraform_code': terraform}

print("Calling backend API...")
response = requests.post('http://127.0.0.1:8000/api/v1/pricing/calculate-pricing', json=payload, timeout=30)
data = response.json()

azure_cost = data.get('total_costs', {}).get('azure', 0)
print("Azure Total: ${:.2f}/month".format(azure_cost))

for res in data.get('breakdown', {}).get('azure', []):
    if 'vm' in res['type'].lower():
        print("VM: {}".format(res['name']))
        print("  Cost: ${:.2f}".format(res['cost']))
        print("  Description: {}".format(res['description']))
