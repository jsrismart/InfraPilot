#!/usr/bin/env python
"""Quick test of pricing calculation with pre-generated Terraform"""
import sys
import os

# Add backend to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.finops_agent import FinOpsAgent

# Pre-generated Terraform files for 3 D-series VMs in Azure
terraform_files = {
    'providers.tf': '''provider "azurerm" {
  features {}
}''',
    'variables.tf': '''variable "vm_count" {
  type        = number
  description = "Number of VMs"
  default     = 3
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "admin_username" {
  type    = string
  default = "azureuser"
}

variable "admin_password" {
  type      = string
  default   = "P@ssw0rd1234!"
}''',
    'main.tf': '''resource "azurerm_resource_group" "example" {
  name     = "example-rg"
  location = var.location
}

resource "azurerm_windows_virtual_machine" "example" {
  for_each = toset(range(var.vm_count))

  name                  = "vm-${each.value}"
  location              = var.location
  resource_group_name   = azurerm_resource_group.example.name
  network_interface_ids = [azurerm_network_interface.example.id]
  size                  = "Standard_DS2_v2"

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }
}

resource "azurerm_express_route_circuit" "example" {
  name                  = "example-erc"
  location              = var.location
  resource_group_name   = azurerm_resource_group.example.name
  service_provider_name = "Equinix"
  peering_location      = "New York"
  bandwidth_in_mbps     = 50
}''',
    'outputs.tf': '''output "vm_ids" {
  value = [for vm in azurerm_windows_virtual_machine.example : vm.id]
}'''
}

print("=" * 70)
print("PRICING CALCULATION TEST")
print("=" * 70)
print(f"Testing with pre-generated Terraform for 3 D-series Azure VMs\n")

finops = FinOpsAgent()
pricing_result = finops.analyze(terraform_files)

if pricing_result:
    print(f"✅ Pricing calculated successfully!")
    print(f"\nKeys: {list(pricing_result.keys())}\n")
    
    if 'summary' in pricing_result:
        summary = pricing_result['summary']
        print(f"Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    if 'resources' in pricing_result:
        resources = pricing_result['resources']
        print(f"\nResources ({len(resources)} found):")
        for i, resource in enumerate(resources, 1):
            print(f"\n  {i}. {resource.get('name', 'Unknown')}")
            print(f"     Type: {resource.get('type')}")
            print(f"     Size: {resource.get('size')}")
            print(f"     Region: {resource.get('region')}")
            print(f"     Quantity: {resource.get('quantity')}")
            print(f"     Monthly Cost: {resource.get('monthly_cost')}")
            print(f"     Annual Cost: {resource.get('annual_cost')}")
            if 'cost_description' in resource:
                print(f"     Description: {resource.get('cost_description')}")
            if 'note' in resource:
                print(f"     Note: {resource.get('note')}")
else:
    print("❌ Failed to calculate pricing")
