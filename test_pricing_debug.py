#!/usr/bin/env python3
"""Debug pricing extraction"""
import sys
sys.path.insert(0, 'backend')

from app.agents.designer_agent import DesignerAgent
from pricing_calculator import CloudPricingCalculator
import json

# Test with E series prompt
prompt = "create a azure vm with E series size"

print("=" * 80)
print(f"PROMPT: {prompt}")
print("=" * 80)

# Step 1: Generate Terraform
designer = DesignerAgent()
iac_files = designer.generate(prompt)

print("\n✅ GENERATED TERRAFORM FILES:")
print("-" * 80)
for filename, content in iac_files.items():
    print(f"\n📄 {filename}:")
    print(content[:500] if len(content) > 500 else content)
    print("...\n" if len(content) > 500 else "")

# Step 2: Calculate pricing
print("\n" + "=" * 80)
print("PRICING CALCULATION:")
print("=" * 80)

calculator = CloudPricingCalculator()
pricing_data = calculator.calculate_pricing_from_terraform(iac_files)

print("\n📊 PRICING RESULT:")
print(json.dumps(pricing_data, indent=2))
