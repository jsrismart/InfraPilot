#!/usr/bin/env python
"""Direct test of the full pipeline without needing the API server"""
import sys
import os
import time
import json

# Add backend to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.designer_agent import DesignerAgent
from app.agents.finops_agent import FinOpsAgent

# Test infrastructure generation and pricing
test_prompt = "Create 3 D series Azure VMs in East US"

print("=" * 70)
print("TESTING FULL PIPELINE: Terraform Generation + Pricing Calculation")
print("=" * 70)
print(f"Prompt: {test_prompt}\n")

# 1. Generate Terraform
print("Step 1: Generating Terraform code...")
print("-" * 70)

designer = DesignerAgent()
start = time.time()
terraform_files = designer.generate(test_prompt)
gen_time = time.time() - start

if terraform_files:
    print(f"✅ Terraform generated in {gen_time:.1f}s")
    print(f"   Files: {list(terraform_files.keys())}")
    
    # Show main.tf content
    main_tf = terraform_files.get('main.tf', '')
    print(f"\n   Main.tf preview ({len(main_tf)} chars):")
    lines = main_tf.split('\n')
    for line in lines[:20]:
        print(f"   {line}")
    if len(lines) > 20:
        print(f"   ... ({len(lines) - 20} more lines)")
else:
    print(f"❌ Failed to generate Terraform after {gen_time:.1f}s")
    sys.exit(1)

# 2. Calculate pricing
print("\n" + "=" * 70)
print("Step 2: Calculating pricing from generated Terraform...")
print("-" * 70)

finops = FinOpsAgent()
start = time.time()
pricing_result = finops.analyze(terraform_files)
pricing_time = time.time() - start

if pricing_result:
    print(f"✅ Pricing calculated in {pricing_time:.1f}s")
    print(f"   Result type: {type(pricing_result)}")
    
    if isinstance(pricing_result, dict):
        print(f"   Keys: {list(pricing_result.keys())}")
        
        # Show resource costs
        if 'resources' in pricing_result:
            print(f"\n   Resources ({len(pricing_result.get('resources', []))} found):")
            for resource in pricing_result.get('resources', [])[:5]:
                print(f"     - {resource.get('type', 'unknown')}: {resource.get('cost', 'N/A')}")
        
        # Show total
        if 'total' in pricing_result:
            print(f"\n   Total Monthly Cost: {pricing_result['total']}")
else:
    print(f"❌ Failed to calculate pricing after {pricing_time:.1f}s")

print("\n" + "=" * 70)
print(f"TOTAL TIME: {gen_time + pricing_time:.1f}s (Generation: {gen_time:.1f}s + Pricing: {pricing_time:.1f}s)")
print("=" * 70)
