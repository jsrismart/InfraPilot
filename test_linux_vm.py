#!/usr/bin/env python3
"""Test the Linux VM generation with enhanced OS detection"""

import requests
import json

# Test 1: Linux VM prompt
linux_prompt = "create 10 azure linux vm in storage account at central us region and on sub net for finance team at D series size"

response = requests.post(
    "http://localhost:8000/api/v1/infra/generate-iac",
    json={"prompt": linux_prompt},
    timeout=120
)

print("=" * 80)
print("TEST: Linux VM Generation")
print("=" * 80)
print(f"Status Code: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    
    # Check if main.tf contains Linux VM
    main_tf = data.get("main.tf", "")
    
    print("Generated Terraform Code Excerpt (first 2000 chars):")
    print("-" * 80)
    print(main_tf[:2000])
    print()
    print("=" * 80)
    print("ANALYSIS:")
    print("=" * 80)
    
    # Check for Linux vs Windows indicators
    if "azurerm_linux_virtual_machine" in main_tf:
        print("✅ PASS: Found azurerm_linux_virtual_machine")
    else:
        print("❌ FAIL: Missing azurerm_linux_virtual_machine")
    
    if "azurerm_windows_virtual_machine" in main_tf:
        print("❌ FAIL: Found azurerm_windows_virtual_machine (should be Linux!)")
    else:
        print("✅ PASS: No azurerm_windows_virtual_machine found")
    
    if '"Canonical"' in main_tf or "'Canonical'" in main_tf:
        print("✅ PASS: Found Canonical publisher (Linux correct)")
    else:
        print("❌ FAIL: Missing Canonical publisher")
    
    if '"MicrosoftWindowsServer"' in main_tf or "'MicrosoftWindowsServer'" in main_tf:
        print("❌ FAIL: Found MicrosoftWindowsServer publisher (should be Canonical!)")
    else:
        print("✅ PASS: No MicrosoftWindowsServer publisher found")
    
    if "UbuntuServer" in main_tf:
        print("✅ PASS: Found UbuntuServer offer (Linux correct)")
    else:
        print("❌ FAIL: Missing UbuntuServer offer")
    
    if "WindowsServer" in main_tf:
        print("❌ FAIL: Found WindowsServer offer (should be Ubuntu!)")
    else:
        print("✅ PASS: No WindowsServer offer found")
        
    # Count VMs
    vm_count = main_tf.count("azurerm_linux_virtual_machine") + main_tf.count("azurerm_windows_virtual_machine")
    print(f"\n📊 VM Count: {vm_count} (requested: 10)")
    
else:
    print(f"ERROR: {response.text}")
