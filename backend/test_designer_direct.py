#!/usr/bin/env python3
"""Direct test of designer agent"""
from app.agents.designer_agent import DesignerAgent

print("Loading designer agent...")
d = DesignerAgent()

print("Generating from prompt...")
result = d.generate('Create E series, D series, and C series VMs')

print(f"IaC keys: {list(result.keys())}")
main_tf = result['main.tf']

import re
vms = re.findall(r'resource "azurerm_windows_virtual_machine"', main_tf)
print(f"VM Resources: {len(vms)}")

sizes = re.findall(r'vm_size = "([^"]+)"', main_tf)
print(f"VM Sizes: {sizes}")
