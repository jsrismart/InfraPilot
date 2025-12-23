#!/usr/bin/env python3
"""Test Terraform generation with multiple VMs"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.designer_agent import DesignerAgent

def test_multiple_vms():
    """Test generating Terraform with multiple VMs"""
    designer = DesignerAgent()
    
    # Test cases with different quantity specifications
    test_prompts = [
        "Create 2 E series VMs in East US with vnet and subnet",
        "Create two D series VMs in Central US",
        "Create 3 C series and 2 E series VMs in West US",
        "Create two Standard_E4s_v3 VMs in East US",
        "Create 2 Azure VMs with C series size in South India",
    ]
    
    for prompt in test_prompts:
        print(f"\n{'='*80}")
        print(f"📝 Prompt: {prompt}")
        print(f"{'='*80}")
        
        try:
            result = designer.generate(prompt)
            
            # Check main.tf for VM count
            if "main.tf" in result:
                main_tf = result["main.tf"]
                vm_count = main_tf.count('azurerm_windows_virtual_machine')
                nic_count = main_tf.count('azurerm_network_interface')
                
                print(f"\n✅ Generated Terraform:")
                print(f"   - Network Interfaces: {nic_count}")
                print(f"   - VMs: {vm_count}")
                print(f"\n📄 main.tf snippet:")
                print("-" * 60)
                print(main_tf[:1500])  # Print first 1500 chars
                if len(main_tf) > 1500:
                    print(f"\n... (truncated, total {len(main_tf)} chars)")
                print("-" * 60)
            
            # Show providers
            if "providers.tf" in result:
                print(f"\n📄 providers.tf:")
                print(result["providers.tf"])
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_multiple_vms()
