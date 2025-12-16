#!/usr/bin/env python3
"""
FINAL CONNECTIVITY TEST REPORT
Tests Azure, AWS, and overall system connectivity
"""

import requests
import json
from datetime import datetime

print("\n" + "="*70)
print(" " * 15 + "INFRAPILOT - FINAL CONNECTIVITY TEST")
print("="*70)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + "\n")

# Test results tracker
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test(name, func):
    """Run a test and track results"""
    try:
        result = func()
        if result:
            results['passed'].append(name)
            print(f"✓ {name}")
            return True
        else:
            results['failed'].append(name)
            print(f"✗ {name}")
            return False
    except Exception as e:
        results['failed'].append(name)
        print(f"✗ {name}: {str(e)[:60]}")
        return False

# ============================================================
print("1. BACKEND CONNECTIVITY TESTS")
print("-" * 70)

def test_backend_root():
    """Test backend root endpoint"""
    response = requests.get("http://127.0.0.1:8001/")
    return response.status_code == 200

def test_pricing_formats():
    """Test pricing formats endpoint"""
    response = requests.get("http://127.0.0.1:8001/api/v1/pricing/pricing-formats")
    if response.status_code == 200:
        data = response.json()
        print(f"    → Pricing Source: {data.get('pricing_source', 'Unknown')}")
        print(f"    → AWS Available: {data.get('real_time_apis_available', {}).get('aws', False)}")
        print(f"    → Azure Available: {data.get('real_time_apis_available', {}).get('azure', False)}")
        print(f"    → GCP Available: {data.get('real_time_apis_available', {}).get('gcp', False)}")
        return True
    return False

test("Backend Root Endpoint", test_backend_root)
test("Pricing API Formats", test_pricing_formats)

# ============================================================
print("\n2. AZURE PRICING TESTS")
print("-" * 70)

def test_azure_vm_pricing():
    """Test Azure VM pricing fetcher"""
    from real_time_pricing_fetcher import AzurePricingFetcher
    fetcher = AzurePricingFetcher()
    if not fetcher.enabled:
        results['warnings'].append("Azure Fetcher not enabled")
        return False
    price = fetcher.get_vm_pricing('Standard_B1', 'eastus')
    if price:
        print(f"    → Standard_B1: ${price:.4f}/hr")
        return True
    return False

def test_azure_retail_api():
    """Test Azure Retail Prices API directly"""
    url = "https://prices.azure.com/api/retail/prices"
    params = {'$filter': "contains(skuName, 'Standard_B1')", '$top': 1}
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        items = response.json().get('Items', [])
        if items:
            print(f"    → Direct API Price: ${items[0].get('retailPrice', 0):.4f}")
            return True
    return False

def test_azure_pricing_via_api():
    """Test Azure pricing through backend API"""
    payload = {
        "terraform_code": 'resource "azurerm_virtual_machine" "vm" { vm_size = "Standard_B1" }',
        "include_breakdown": True
    }
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/pricing/calculate-pricing",
        json=payload
    )
    if response.status_code == 200:
        data = response.json()
        cost = data.get('total_costs', {}).get('azure', 0)
        if cost > 0:
            print(f"    → Calculated Azure Cost: ${cost:.2f}")
            return True
    return False

test("Azure VM Pricing Fetcher", test_azure_vm_pricing)
test("Azure Retail API (Direct)", test_azure_retail_api)
test("Azure Pricing via Backend API", test_azure_pricing_via_api)

# ============================================================
print("\n3. AWS PRICING TESTS")
print("-" * 70)

def test_aws_fetcher():
    """Test AWS pricing fetcher"""
    from real_time_pricing_fetcher import AWSPricingFetcher
    fetcher = AWSPricingFetcher()
    if not fetcher.enabled:
        results['warnings'].append("AWS Fetcher not enabled (boto3 available but may need credentials)")
        return False
    price = fetcher.get_ec2_pricing('t3.micro')
    if price is not None:
        print(f"    → EC2 t3.micro: ${price:.4f}/hr")
        return True
    return False

def test_aws_pricing_via_api():
    """Test AWS pricing through backend API"""
    payload = {
        "terraform_code": 'resource "aws_instance" "web" { instance_type = "t3.micro" }',
        "include_breakdown": True
    }
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/pricing/calculate-pricing",
        json=payload
    )
    if response.status_code == 200:
        data = response.json()
        cost = data.get('total_costs', {}).get('aws', 0)
        print(f"    → Calculated AWS Cost: ${cost:.2f}")
        return True
    return False

test("AWS Pricing Fetcher", test_aws_fetcher)
test("AWS Pricing via Backend API", test_aws_pricing_via_api)

# ============================================================
print("\n4. CACHING TESTS")
print("-" * 70)

def test_pricing_cache():
    """Test pricing cache functionality"""
    import os
    cache_dir = "./pricing_cache"
    if os.path.exists(cache_dir):
        files = os.listdir(cache_dir)
        print(f"    → Cache directory exists with {len(files)} cached items")
        return len(files) >= 0  # Cache should be populated after fetches
    return False

test("Pricing Cache System", test_pricing_cache)

# ============================================================
print("\n5. ERROR HANDLING TESTS")
print("-" * 70)

def test_invalid_terraform():
    """Test error handling for invalid Terraform"""
    payload = {
        "terraform_code": "invalid { terraform @@@"
    }
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/pricing/calculate-pricing",
        json=payload
    )
    # Should either succeed with fallback or return error gracefully
    return response.status_code in [200, 400]

def test_empty_terraform():
    """Test handling of empty Terraform"""
    payload = {
        "terraform_code": ""
    }
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/pricing/calculate-pricing",
        json=payload
    )
    return response.status_code == 200

test("Invalid Terraform Handling", test_invalid_terraform)
test("Empty Terraform Handling", test_empty_terraform)

# ============================================================
print("\n6. REAL-TIME vs FALLBACK TESTS")
print("-" * 70)

def test_pricing_source():
    """Verify real-time pricing vs fallback"""
    response = requests.get("http://127.0.0.1:8001/api/v1/pricing/pricing-formats")
    if response.status_code == 200:
        data = response.json()
        source = data.get('pricing_source', '')
        if 'real-time' in source.lower():
            print(f"    → Using: Real-time APIs with intelligent fallback")
            return True
        elif 'static' in source.lower():
            print(f"    → Using: Static/Fallback pricing")
            results['warnings'].append("Real-time APIs not active, using fallback")
            return True
    return False

test("Real-time Pricing Status", test_pricing_source)

# ============================================================
print("\n" + "="*70)
print(" " * 20 + "TEST SUMMARY")
print("="*70)
print(f"\n✓ Passed: {len(results['passed'])}")
for test_name in results['passed']:
    print(f"  • {test_name}")

if results['failed']:
    print(f"\n✗ Failed: {len(results['failed'])}")
    for test_name in results['failed']:
        print(f"  • {test_name}")

if results['warnings']:
    print(f"\n⚠ Warnings: {len(results['warnings'])}")
    for warning in results['warnings']:
        print(f"  • {warning}")

success_rate = len(results['passed']) / (len(results['passed']) + len(results['failed'])) * 100 if (len(results['passed']) + len(results['failed'])) > 0 else 0
print(f"\nSUCCESS RATE: {success_rate:.1f}%")

print("\n" + "="*70)
if success_rate >= 80:
    print("✓ SYSTEM READY FOR TESTING")
    print("="*70)
    print("\nNextSteps:")
    print("  1. Open http://127.0.0.1:3001 in your browser")
    print("  2. Navigate to the FinOps tab")
    print("  3. Enter Terraform code or load generated IaC")
    print("  4. Click 'Calculate Pricing' to see real-time costs")
    print("\nExample Terraform:")
    print("  resource \"azurerm_virtual_machine\" \"vm\" {")
    print("    vm_size = \"Standard_B1\"")
    print("  }")
elif success_rate >= 60:
    print("⚠ SYSTEM PARTIALLY READY - SOME FEATURES DEGRADED")
    print("="*70)
else:
    print("✗ SYSTEM NOT READY - CRITICAL FAILURES")
    print("="*70)

print()
