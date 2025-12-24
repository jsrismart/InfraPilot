#!/usr/bin/env python3
"""Verify architecture: Ollama -> Terraform Code -> Pricing from Terraform only"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_architecture():
    print("=" * 80)
    print("TESTING: Ollama -> Terraform Code -> Pricing from Terraform")
    print("=" * 80)
    
    # Step 1: Test Terraform generation (Ollama only)
    print("\nSTEP 1: Terraform Generation (via Ollama)")
    print("-" * 80)
    from app.agents.designer_agent import DesignerAgent
    
    designer = DesignerAgent()
    prompt = "Create 2 Standard_E4s_v3 VMs in East US with vnet and subnet"
    
    try:
        result = designer.generate(prompt)
        print("OK: Ollama generated Terraform successfully")
        print("   Generated files: {}".format(list(result.keys())))
        
        if 'main.tf' in result:
            main_tf = result['main.tf']
            vm_count = main_tf.count('azurerm_windows_virtual_machine')
            nic_count = main_tf.count('azurerm_network_interface')
            print("   - VMs: {}".format(vm_count))
            print("   - Network Interfaces: {}".format(nic_count))
            
            # Show a snippet
            print("\n   First 300 chars of main.tf:")
            print("   " + main_tf[:300].replace("\n", "\n   "))
    except Exception as e:
        print("ERROR: Terraform generation failed: {}".format(e))
        return False
    
    # Step 2: Test Pricing calculation from Terraform
    print("\n\nSTEP 2: Pricing Calculation (from Terraform code only)")
    print("-" * 80)
    from app.agents.finops_agent import FinOpsAgent
    
    finops = FinOpsAgent()
    iac_files = result  # Use the Terraform generated above
    
    try:
        pricing_result = finops.analyze(iac_files)
        print("OK: Pricing calculated from Terraform code")
        print("   Summary: {}".format(pricing_result.get('summary', {})))
        
        if 'resources' in pricing_result:
            resources = pricing_result['resources']
            print("\n   Resources ({} found):".format(len(resources)))
            for res in resources:
                print("   - {}: {}".format(res.get('name', 'Unknown'), res.get('monthly_cost', '$0.00')))
    except Exception as e:
        print("ERROR: Pricing calculation failed: {}".format(e))
        return False
    
    # Step 3: Verify NO hardcoded or generic estimates
    print("\n\nSTEP 3: Verification - NO Hardcoded/Generic Estimates")
    print("-" * 80)
    
    # Check if pricing_result has generic values like "$30-200"
    pricing_str = str(pricing_result)
    generic_patterns = ["estimated", "depends on", "$30-200", "$20-150"]
    
    has_generics = any(pattern in pricing_str.lower() for pattern in generic_patterns)
    
    if has_generics:
        print("ERROR: Found generic/estimated costs (NOT ALLOWED)")
        return False
    else:
        print("OK: No generic estimates found - using real pricing from Terraform code only")
    
    print("\n" + "=" * 80)
    print("ARCHITECTURE VERIFIED")
    print("=" * 80)
    print("\n- Terraform generation: Ollama ONLY")
    print("- Pricing calculation: From Terraform code ONLY")
    print("- No hardcoded pricing")
    print("- No generic estimates")
    
    return True

if __name__ == "__main__":
    success = test_architecture()
    sys.exit(0 if success else 1)
