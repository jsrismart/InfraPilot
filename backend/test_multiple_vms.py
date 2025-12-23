#!/usr/bin/env python3
"""Test if designer agent generates multiple VMs"""
import re
from app.agents.designer_agent import DesignerAgent

d = DesignerAgent()
result = d.generate('Create E series, D series, and C series VMs')

# Count VMs
vms = re.findall(r'resource "azurerm_windows_virtual_machine"', result['main.tf'])
print(f'Found {len(vms)} VM resources')

# Count NICs
nics = re.findall(r'resource "azurerm_network_interface"', result['main.tf'])
print(f'Found {len(nics)} NIC resources')

# Extract VM sizes
sizes = re.findall(r'vm_size = "([^"]+)"', result['main.tf'])
print(f'VM Sizes: {sizes}')

# Show the terraform code
print("\n=== TERRAFORM MAIN.TF ===")
print(result['main.tf'])
