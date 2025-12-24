#!/usr/bin/env python3
"""Debug what the API returns"""
import requests
import re

url = "http://127.0.0.1:8000/api/v1/infra/generate-iac"
payload = {"prompt": "Create E series, D series, and C series VMs"}

response = requests.post(url, json=payload)
data = response.json()
main_tf = data['iac']['main.tf']

# Count VMs
vm_count = len(re.findall(r'resource "azurerm_windows_virtual_machine"', main_tf))
print(f"VM Resources: {vm_count}")

# Count NICs
nic_count = len(re.findall(r'resource "azurerm_network_interface"', main_tf))
print(f"NIC Resources: {nic_count}")

# Show sizes
sizes = re.findall(r'vm_size = "([^"]+)"', main_tf)
print(f"VM Sizes: {sizes}")

print("\n=== FIRST 2000 chars of main.tf ===")
print(main_tf[:2000])
