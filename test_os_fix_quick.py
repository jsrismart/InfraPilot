#!/usr/bin/env python3
"""Test the Linux VM generation with enhanced OS detection - Quick Test"""

import requests
import json

# Test: Linux VM prompt
linux_prompt = "create 3 azure linux vm in centralus region at D series size"

print("Testing Linux VM generation with shorter prompt...")
print(f"Request: {linux_prompt}")
print()

try:
    response = requests.post(
        "http://localhost:8000/api/v1/infra/generate-iac",
        json={"prompt": linux_prompt},
        timeout=180  # 3 minutes max
    )

    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 200:
        data = response.json()
        
        # Check if main.tf contains Linux VM
        main_tf = data.get("main.tf", "")
        
        print("Generated Terraform Code (first 1500 chars):")
        print("-" * 80)
        print(main_tf[:1500])
        print()
        print("=" * 80)
        print("QUICK ANALYSIS:")
        print("=" * 80)
        
        # Check for Linux vs Windows indicators
        linux_vm = "azurerm_linux_virtual_machine" in main_tf
        windows_vm = "azurerm_windows_virtual_machine" in main_tf
        canonical = '"Canonical"' in main_tf or "'Canonical'" in main_tf
        msft_windows = '"MicrosoftWindowsServer"' in main_tf or "'MicrosoftWindowsServer'" in main_tf
        
        print(f"✓ Linux VM: {linux_vm}")
        print(f"✗ Windows VM: {windows_vm}")
        print(f"✓ Canonical Publisher: {canonical}")
        print(f"✗ MicrosoftWindowsServer: {msft_windows}")
        
        if linux_vm and not windows_vm and canonical and not msft_windows:
            print("\n✅ SUCCESS: Linux VMs generated correctly!")
        else:
            print("\n❌ ISSUE: OS type mismatch detected")
            
    else:
        print(f"ERROR {response.status_code}: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 180 seconds")
except Exception as e:
    print(f"❌ Error: {e}")
