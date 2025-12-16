#!/usr/bin/env python3
"""Test C-series VM generation and pricing"""
import sys
sys.path.insert(0, '.')

from pricing_calculator import calculate_terraform_pricing
import json

# Test with C-series prompt
terraform_code = '''provider "azurerm" {
  features {}
}

variable "project_name" {
  type    = string
  default = "myproject"
}

resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-rg"
  location = "southindia"
}

resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "${var.project_name}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_network_interface" "main" {
  name                = "${var.project_name}-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "testconfiguration1"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_windows_virtual_machine" "main" {
  name                = "${var.project_name}-vm"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  admin_username      = "adminuser"
  admin_password      = "P@ssw0rd1234!"

  network_interface_ids = [
    azurerm_network_interface.main.id,
  ]

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

  vm_size = "Standard_C4s_v3"
}

output "deployment_id" {
  value = var.project_name
}
'''

print("Testing C-series pricing...")
try:
    result = calculate_terraform_pricing(terraform_code)
    print("✅ Success!")
    
    # Extract key info
    azure_cost = result['total_costs'].get('azure', 0)
    breakdown = result['breakdown'].get('azure', [])
    
    print(f"\n💰 Total Azure Monthly Cost: ${azure_cost:.2f}")
    print(f"\n📊 Resource Breakdown:")
    for resource in breakdown:
        if resource['cost'] > 0:
            print(f"  - {resource['name']} ({resource['type']}): ${resource['cost']:.2f}/month")
            print(f"    {resource['description']}")
    
    if azure_cost == 0:
        print("\n⚠️ No pricing returned - checking details:")
        for resource in breakdown:
            print(f"  - {resource['name']}: {resource['description']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
