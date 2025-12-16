#!/usr/bin/env python3
"""
Test Azure Retail Prices API connectivity
"""

import requests

def test_azure_pricing():
    url = 'https://prices.azure.com/api/retail/prices'
    
    print("=" * 60)
    print("Testing Azure Retail Prices API")
    print("=" * 60)
    
    # Test 1: List available SKUs
    print("\n[TEST 1] Fetch available VM SKUs")
    params = {
        '$filter': "contains(skuName, 'Standard_B1')",
        '$top': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('Items', [])
            print(f"Found {len(items)} items")
            
            if items:
                print(f"\nFirst Item Details:")
                for key in ['skuName', 'retailPrice', 'unitPrice', 'armSkuName', 'location']:
                    if key in items[0]:
                        print(f"  {key}: {items[0][key]}")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get SQL Database pricing
    print("\n[TEST 2] Fetch Azure SQL Database pricing")
    params = {
        '$filter': "contains(skuName, 'SQL Database') and contains(skuName, 'Basic')",
        '$top': 2
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('Items', [])
            print(f"Found {len(items)} items")
            
            if items:
                print(f"\nFirst Item Details:")
                for key in ['skuName', 'retailPrice', 'unitPrice', 'location']:
                    if key in items[0]:
                        print(f"  {key}: {items[0][key]}")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Try different VM SKU name
    print("\n[TEST 3] Fetch with different filter (Standard_D2s)")
    params = {
        '$filter': "contains(skuName, 'Standard_D2s')",
        '$top': 2
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('Items', [])
            print(f"Found {len(items)} items")
            
            if items:
                print(f"\nFirst Item Details:")
                for key in ['skuName', 'retailPrice', 'unitPrice', 'location']:
                    if key in items[0]:
                        print(f"  {key}: {items[0][key]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Test via Azure Fetcher
    print("\n[TEST 4] Test via AzurePricingFetcher")
    from real_time_pricing_fetcher import AzurePricingFetcher
    
    fetcher = AzurePricingFetcher()
    print(f"Fetcher Enabled: {fetcher.enabled}")
    
    if fetcher.enabled:
        print("\nTesting VM pricing fetch:")
        price = fetcher.get_vm_pricing('Standard_B1', 'eastus')
        print(f"  Standard_B1 price: {price}")
        
        if not price:
            print("\nTrying Standard_D2s instead:")
            price = fetcher.get_vm_pricing('Standard_D2s')
            print(f"  Standard_D2s price: {price}")
        
        print("\nTesting SQL pricing fetch:")
        price = fetcher.get_sql_db_pricing('S0')
        print(f"  SQL S0 price: {price}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_azure_pricing()
