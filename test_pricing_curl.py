#!/usr/bin/env python3
"""Test pricing API directly"""
import requests
import json

# Terraform code for E series VM
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

  vm_size = "Standard_E4s_v3"
}

output "deployment_id" {
  value = var.project_name
}
'''

# Send pricing request
url = "http://127.0.0.1:8001/api/v1/pricing/calculate-pricing"
payload = {
    "terraform_code": terraform_code,
    "include_breakdown": True,
    "include_comparison": True
}

print("Sending pricing request...")
print(f"Terraform code size: {len(terraform_code)} characters")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Response received!")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
