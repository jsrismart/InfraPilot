#!/usr/bin/env python3
"""Get the full generated IaC and save it"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"

payload = {"prompt": "Create an Azure VM with D2_v3 size in East US region"}

response = requests.post(f"{BASE_URL}/infra/generate-iac", json=payload, timeout=20)
result = response.json()

iac_files = result.get('iac', {})

# Save all files combined
full_terraform = "\n\n# " + "\n# ".join([f"{name}\n{content}" for name, content in iac_files.items()])

with open("generated_terraform.tf", "w") as f:
    f.write(full_terraform)

print("Generated Terraform saved to generated_terraform.tf")
print(f"\nFiles: {list(iac_files.keys())}")

# Now test pricing on the combined code
print("\nTesting pricing on combined generated code...")

from pricing_calculator import calculate_terraform_pricing
result = calculate_terraform_pricing(full_terraform)

print(f"Total Costs: {result.get('total_costs')}")
breakdown = result.get('breakdown', {})
for provider, resources in breakdown.items():
    if resources:
        print(f"\n{provider.upper()} Resources:")
        for res in resources:
            print(f"  - {res['name']}: ${res['cost']:.2f} - {res['description']}")
