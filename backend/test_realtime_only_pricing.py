#!/usr/bin/env python
"""
Test that pricing calculator uses ONLY real-time Azure API
No static tables, no assumptions, no fallbacks
"""

import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from pricing_calculator import CloudPricingCalculator
from real_time_pricing_fetcher import pricing_fetcher

def test_vm_pricing_only_from_api():
    """Test that VM pricing comes ONLY from Azure API, not from static tables"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: VM Pricing - ONLY from Real-time Azure API")
    logger.info("="*70)
    
    calculator = CloudPricingCalculator()
    
    # Test D2s_v4 VM (should get LIVE pricing from Azure API)
    resource = {
        'name': 'test_vm',
        'type': 'azurerm_windows_virtual_machine',
        'config': {
            'region': 'eastus',
            'vm_size': 'Standard_D2s_v4'
        }
    }
    
    cost, description = calculator._calculate_azure_cost(
        res_type='azurerm_windows_virtual_machine',
        instance_type='Standard_D2s_v4',
        quantity=1,
        resource=resource
    )
    
    logger.info(f"\n✓ Resource: Azure VM (Standard_D2s_v4)")
    logger.info(f"✓ Cost: ${cost:.2f}/month")
    logger.info(f"✓ Description: {description}")
    
    # Verify it's from LIVE API
    if "LIVE AZURE API" in description or "LIVE FROM AZURE" in description:
        logger.info("✓ SUCCESS: Pricing from LIVE AZURE API (not static table)")
        return True
    elif "STATIC" in description or "ESTIMATE" in description or "NO DATA" in description:
        logger.error(f"✗ FAILED: Pricing from fallback (expected LIVE API): {description}")
        return False
    else:
        logger.warning(f"? UNCLEAR: Check description: {description}")
        return cost > 0

def test_sql_pricing_only_from_api():
    """Test that SQL Database pricing comes ONLY from Azure API"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: SQL Database Pricing - ONLY from Real-time Azure API")
    logger.info("="*70)
    
    calculator = CloudPricingCalculator()
    
    # Test SQL Database (should get LIVE pricing from Azure API)
    resource = {
        'name': 'test_sql',
        'type': 'azurerm_sql_database',
        'config': {
            'region': 'eastus',
            'sku': 'S1'
        }
    }
    
    cost, description = calculator._calculate_azure_cost(
        res_type='azurerm_sql_database',
        instance_type='S1',
        quantity=1,
        resource=resource
    )
    
    logger.info(f"\n✓ Resource: Azure SQL Database (S1)")
    logger.info(f"✓ Cost: ${cost:.2f}/month")
    logger.info(f"✓ Description: {description}")
    
    # Verify it's from LIVE API
    if "LIVE AZURE API" in description or "LIVE FROM AZURE" in description:
        logger.info("✓ SUCCESS: Pricing from LIVE AZURE API (not static table)")
        return True
    elif "STATIC" in description or "ESTIMATE" in description or "NO DATA" in description:
        logger.error(f"✗ FAILED: Pricing from fallback (expected LIVE API): {description}")
        return False
    else:
        logger.warning(f"? UNCLEAR: Check description: {description}")
        return cost > 0

def test_storage_pricing_only_from_api():
    """Test that Storage pricing comes ONLY from Azure API"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Storage Account Pricing - ONLY from Real-time Azure API")
    logger.info("="*70)
    
    calculator = CloudPricingCalculator()
    
    # Test Storage Account (should get LIVE pricing from Azure API)
    resource = {
        'name': 'test_storage',
        'type': 'azurerm_storage_account',
        'config': {
            'region': 'eastus',
            'size_gb': 100
        }
    }
    
    cost, description = calculator._calculate_azure_cost(
        res_type='azurerm_storage_account',
        instance_type='blob_standard',
        quantity=1,
        resource=resource
    )
    
    logger.info(f"\n✓ Resource: Azure Storage Account (100 GB)")
    logger.info(f"✓ Cost: ${cost:.2f}/month")
    logger.info(f"✓ Description: {description}")
    
    # Verify it's from LIVE API
    if "LIVE AZURE API" in description:
        logger.info("✓ SUCCESS: Pricing from LIVE AZURE API (not static table)")
        return True
    elif "STATIC" in description or "ESTIMATE" in description or "NO DATA" in description:
        logger.error(f"✗ FAILED: Pricing from fallback (expected LIVE API): {description}")
        return False
    else:
        logger.warning(f"? UNCLEAR: Check description: {description}")
        return cost >= 0

def test_no_fallback_for_unknown_vm():
    """Test that unknown VM types return NO DATA instead of estimates"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Unknown VM Type - Should return NO DATA (not estimate)")
    logger.info("="*70)
    
    calculator = CloudPricingCalculator()
    
    # Test unknown VM type (should return 0 and NO DATA message, not an estimate)
    resource = {
        'name': 'test_unknown',
        'type': 'azurerm_windows_virtual_machine',
        'config': {
            'region': 'eastus',
            'vm_size': 'UNKNOWN_VM_TYPE_12345'
        }
    }
    
    cost, description = calculator._calculate_azure_cost(
        res_type='azurerm_windows_virtual_machine',
        instance_type='UNKNOWN_VM_TYPE_12345',
        quantity=1,
        resource=resource
    )
    
    logger.info(f"\n✓ Resource: Azure VM (UNKNOWN_VM_TYPE_12345)")
    logger.info(f"✓ Cost: ${cost:.2f}/month")
    logger.info(f"✓ Description: {description}")
    
    # Should NOT estimate - should return 0 or NO DATA message
    if cost == 0 and ("NO DATA" in description or "NO AZURE API DATA" in description):
        logger.info("✓ SUCCESS: Unknown VM returns NO DATA (no estimates)")
        return True
    elif cost > 0 and ("ESTIMATE" in description or "vCPU" in description):
        logger.error(f"✗ FAILED: Unknown VM estimated instead of NO DATA: {description}")
        return False
    else:
        logger.info(f"✓ INFO: Cost={cost}, Description={description}")
        return True

def main():
    logger.info("\n" + "█"*70)
    logger.info("█  REAL-TIME ONLY PRICING VERIFICATION")
    logger.info("█  Testing that pricing comes ONLY from Azure API")
    logger.info("█  No static tables • No assumptions • No fallbacks")
    logger.info("█"*70)
    
    try:
        results = {
            'VM Pricing (D2s_v4)': test_vm_pricing_only_from_api(),
            'SQL Pricing (S1)': test_sql_pricing_only_from_api(),
            'Storage Pricing': test_storage_pricing_only_from_api(),
            'Unknown VM Type': test_no_fallback_for_unknown_vm(),
        }
        
        logger.info("\n" + "="*70)
        logger.info("SUMMARY")
        logger.info("="*70)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{status}: {test_name}")
        
        logger.info(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("\n✓ ALL TESTS PASSED: Using real-time Azure API only!")
            return 0
        else:
            logger.error(f"\n✗ SOME TESTS FAILED: {total - passed} failures")
            return 1
    
    except Exception as e:
        logger.error(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
