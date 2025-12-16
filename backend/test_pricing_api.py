#!/usr/bin/env python
"""Test the pricing API endpoint"""
import requests
import json

terraform_code = '''
resource "azurerm_windows_virtual_machine" "example" {
  name                = "example-vm"
  location            = "East US"
  resource_group_name = "example-rg"
  vm_size             = "Standard_D2s_v3"

  admin_username = "adminuser"
  admin_password = "P@ssw0rd1234!"

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }
}
'''

payload = {
    "terraform_code": terraform_code,
    "include_breakdown": True,
    "include_comparison": True
}

print("Testing pricing endpoint with Azure VM Terraform...")
print("URL: http://localhost:8001/api/v1/pricing/calculate-pricing")
print("\nPayload:")
print(json.dumps(payload, indent=2)[:500] + "...")

try:
    response = requests.post(
        "http://localhost:8001/api/v1/pricing/calculate-pricing",
        json=payload,
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\nError: {response.text}")
        
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
