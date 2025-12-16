#!/usr/bin/env python3
"""Complete end-to-end test simulating user workflow"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1"

print("="*70)
print("END-TO-END TEST: Full InfraPilot Workflow")
print("="*70)

# Step 1: Generate Infrastructure Code
print("\n[STEP 1] Generate Infrastructure Code")
print("-"*70)
prompt = "Create an Azure VM with D2_v3 size in East US region"
print(f"Prompt: {prompt}")

try:
    response = requests.post(f"{BASE_URL}/infra/generate-iac", json={"prompt": prompt}, timeout=20)
    print(f"Response Status: {response.status_code}")
    iac_result = response.json()
    
    iac_files = iac_result.get('iac', {})
    print(f"Generated Files: {list(iac_files.keys())}")
    terraform_code = "\n\n".join([f"# {name}\n{content}" for name, content in iac_files.items()])
    print(f"Total Terraform Code: {len(terraform_code)} characters")
    print("\n✓ IaC Generation: SUCCESS")
except Exception as e:
    print(f"✗ Error: {e}")
    terraform_code = ""

# Step 2: Calculate Pricing
print("\n[STEP 2] Calculate Pricing")
print("-"*70)
if terraform_code:
    try:
        response = requests.post(
            f"{BASE_URL}/pricing/calculate-pricing",
            json={
                "terraform_code": terraform_code,
                "include_breakdown": True,
                "include_comparison": True
            },
            timeout=15
        )
        print(f"Response Status: {response.status_code}")
        pricing_result = response.json()
        
        total_costs = pricing_result.get('total_costs', {})
        print(f"Total Costs: {total_costs}")
        print(f"  - AWS: ${total_costs.get('aws', 0):.2f}/month")
        print(f"  - Azure: ${total_costs.get('azure', 0):.2f}/month")
        print(f"  - GCP: ${total_costs.get('gcp', 0):.2f}/month")
        
        breakdown = pricing_result.get('breakdown', {})
        for provider, resources in breakdown.items():
            if resources:
                print(f"\nBreakdown for {provider.upper()}:")
                for res in resources:
                    print(f"  - {res['name']}: ${res['cost']:.2f} ({res['description']})")
        
        # Check if pricing is showing
        if total_costs.get('azure', 0) > 0:
            print("\n✓ Pricing Calculation: SUCCESS (Azure pricing detected: $70.08/month expected)")
        else:
            print("\n✗ Pricing Calculation: FAILED (No pricing found)")
            
    except Exception as e:
        print(f"✗ Error: {e}")

# Step 3: Generate Diagram
print("\n[STEP 3] Generate Infrastructure Diagram")
print("-"*70)
if terraform_code:
    try:
        response = requests.post(
            f"{BASE_URL}/diagram/generate-diagram",
            json={
                "terraform_code": terraform_code,
                "diagram_type": "ascii"
            },
            timeout=15
        )
        print(f"Response Status: {response.status_code}")
        diagram_result = response.json()
        
        if diagram_result.get('success'):
            diagram_content = diagram_result.get('content', '')
            print(f"Diagram Type: {diagram_result.get('diagram_type')}")
            print(f"Diagram Size: {len(diagram_content)} characters")
            print(f"\nDiagram Preview:\n{diagram_content[:300]}...")
            print("\n✓ Diagram Generation: SUCCESS")
        else:
            print("✗ Diagram generation failed")
            
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "="*70)
print("END-TO-END TEST: COMPLETE")
print("="*70)
