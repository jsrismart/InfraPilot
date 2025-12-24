#!/usr/bin/env python3
"""Test C-series pricing through the backend API"""

import requests
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

resource "azurerm_virtual_machine" "main" {
  name                  = "${var.project_name}-vm"
  location              = azurerm_resource_group.main.location
  resource_group_name   = azurerm_resource_group.main.name
  vm_size               = "Standard_C4c_v3"

  network_interface_ids = [
    azurerm_network_interface.main.id,
  ]

  storage_os_disk {
    name              = "myosdisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

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

output "vm_id" {
  value = azurerm_virtual_machine.main.id
}
'''

print("=" * 80)
print("Testing C-series VM pricing through backend API")
print("=" * 80)

payload = {
    "terraform_code": terraform_code,
    "include_breakdown": True
}

print("\nSending request to backend API...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/pricing/calculate-pricing",
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✓ Response received successfully!")
        
        print(f"\nTotal Azure Cost: ${data.get('total_costs', {}).get('azure', 0):.2f}/month")
        
        print("\nResource Breakdown:")
        for resource in data.get('breakdown', {}).get('azure', []):
            print(f"\n  Name: {resource['name']}")
            print(f"  Type: {resource['type']}")
            print(f"  Cost: ${resource['cost']:.2f}/month")
            print(f"  Description: {resource['description']}")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n✗ Exception: {e}")
