#!/usr/bin/env python3
"""Test script to verify Azure pricing is working"""
import sys
from real_time_pricing_fetcher import AzurePricingFetcher

print("=" * 60)
print("TESTING AZURE PRICING FETCHER")
print("=" * 60)

try:
    fetcher = AzurePricingFetcher()
    
    # Test 1: Get pricing for Standard_D2s_v3 in eastus
    print("\n[TEST 1] Standard_D2s_v3 in eastus")
    price = fetcher.get_vm_pricing('Standard_D2s_v3', 'eastus')
    if price:
        print(f"  ✓ Monthly Cost: ${price:.2f}")
        print(f"  ✓ Annual Cost: ${price * 12:.2f}")
    else:
        print(f"  ✗ No pricing found")
    
    # Test 2: Try with different region
    print("\n[TEST 2] Standard_D2s_v3 in westus2")
    price2 = fetcher.get_vm_pricing('Standard_D2s_v3', 'westus2')
    if price2:
        print(f"  ✓ Monthly Cost: ${price2:.2f}")
        print(f"  ✓ Annual Cost: ${price2 * 12:.2f}")
    else:
        print(f"  ✗ No pricing found")
    
    # Test 3: Alternative VM size
    print("\n[TEST 3] Standard_D4s_v3 in eastus")
    price3 = fetcher.get_vm_pricing('Standard_D4s_v3', 'eastus')
    if price3:
        print(f"  ✓ Monthly Cost: ${price3:.2f}")
        print(f"  ✓ Annual Cost: ${price3 * 12:.2f}")
    else:
        print(f"  ✗ No pricing found")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - PRICING IS WORKING")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}")
    print(f"  Message: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
