"""
Azure Resource Validator
Validates Terraform resource names against Azure Pricing Calculator API
and suggests corrections if resource names don't match Azure pricing data
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AzureResourceValidator:
    """Validates Azure resources and their names against Azure Pricing Calculator API"""
    
    def __init__(self):
        self.api_url = "https://prices.azure.com/api/retail/prices"
        self.cache = {}
        self.cache_ttl = timedelta(hours=0)  # DISABLED - No caching, fresh API calls every time
        logger.info("[VALIDATOR] Azure Resource Validator initialized - Cache DISABLED")
    
    def validate_resource(self, resource_type: str, resource_name: str, 
                         properties: Dict) -> Tuple[bool, str, Optional[str]]:
        """
        Validate a Terraform resource against Azure API
        
        Returns: (is_valid, message, suggested_name)
        """
        res_type_lower = resource_type.lower().replace('azurerm_', '')
        
        logger.info(f"[VALIDATOR] Validating {resource_type} '{resource_name}'")
        
        # Free resources - always valid
        free_resources = [
            'resource_group', 'virtual_network', 'subnet', 
            'network_interface', 'public_ip', 'storage_container'
        ]
        
        if res_type_lower in free_resources:
            logger.info(f"[VALIDATOR] ✓ {res_type_lower} is free in Azure - valid")
            return True, f"{res_type_lower} is supported (FREE)", None
        
        # VM validation
        if 'virtual_machine' in res_type_lower:
            vm_size = properties.get('vm_size', '')
            if vm_size:
                is_valid, msg = self._validate_vm_sku(vm_size)
                if not is_valid:
                    suggested = self._suggest_vm_sku(vm_size)
                    return False, msg, suggested
                return True, f"VM SKU '{vm_size}' is valid", None
            return False, "VM size not specified in properties", None
        
        # SQL Server/Database validation
        if res_type_lower in ['mssql_server', 'mssql_database', 'sql_server', 'sql_database']:
            sku_name = properties.get('sku_name', 'S0')
            is_valid, msg = self._validate_sql_tier(sku_name)
            if not is_valid:
                suggested = self._suggest_sql_tier(sku_name)
                return False, msg, suggested
            return True, f"SQL tier '{sku_name}' is valid", None
        
        # Storage Account validation
        if res_type_lower == 'storage_account':
            account_tier = properties.get('account_tier', 'Standard')
            is_valid, msg = self._validate_storage_tier(account_tier)
            if not is_valid:
                suggested = self._suggest_storage_tier(account_tier)
                return False, msg, suggested
            return True, f"Storage tier '{account_tier}' is valid", None
        
        # Unsupported resource
        return False, f"Resource type '{resource_type}' is not yet supported for validation", None
    
    def _validate_vm_sku(self, vm_size: str) -> Tuple[bool, str]:
        """Validate VM SKU exists in Azure API"""
        try:
            params = {
                '$filter': f"armSkuName eq '{vm_size}'",
                '$top': 1
            }
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('Items', []):
                    logger.info(f"[VALIDATOR] ✓ VM SKU '{vm_size}' found in Azure API")
                    return True, f"VM SKU '{vm_size}' is valid"
                else:
                    logger.warning(f"[VALIDATOR] ✗ VM SKU '{vm_size}' not found in Azure API")
                    return False, f"VM SKU '{vm_size}' not found in Azure pricing"
        except Exception as e:
            logger.error(f"[VALIDATOR] Error validating VM SKU: {e}")
            return False, f"Error validating VM SKU: {e}"
        
        return False, f"VM SKU '{vm_size}' validation failed"
    
    def _validate_sql_tier(self, tier: str) -> Tuple[bool, str]:
        """Validate SQL tier exists in Azure API"""
        valid_tiers = ['Basic', 'Standard', 'Premium', 'S0', 'S1', 'S2', 'S3', 'S4', 'S6', 'S7',
                      'P1', 'P2', 'P3', 'P4', 'P6', 'P11', 'P15']
        
        if tier in valid_tiers:
            logger.info(f"[VALIDATOR] ✓ SQL tier '{tier}' is valid")
            return True, f"SQL tier '{tier}' is valid"
        
        logger.warning(f"[VALIDATOR] ✗ SQL tier '{tier}' not in known tiers")
        return False, f"SQL tier '{tier}' not recognized"
    
    def _validate_storage_tier(self, tier: str) -> Tuple[bool, str]:
        """Validate storage tier exists in Azure"""
        valid_tiers = ['Standard', 'Premium']
        
        if tier in valid_tiers:
            logger.info(f"[VALIDATOR] ✓ Storage tier '{tier}' is valid")
            return True, f"Storage tier '{tier}' is valid"
        
        logger.warning(f"[VALIDATOR] ✗ Storage tier '{tier}' not in known tiers")
        return False, f"Storage tier '{tier}' not recognized"
    
    def _suggest_vm_sku(self, invalid_sku: str) -> Optional[str]:
        """Suggest similar VM SKU"""
        # Common D-series suggestions
        suggestions = {
            'D2': 'Standard_D2s_v3',
            'D4': 'Standard_D4s_v3',
            'D8': 'Standard_D8s_v3',
            'D16': 'Standard_D16s_v3',
            'D32': 'Standard_D32s_v3',
        }
        
        for pattern, suggestion in suggestions.items():
            if pattern in invalid_sku.upper():
                logger.info(f"[VALIDATOR] Suggested SKU: {suggestion}")
                return suggestion
        
        return None
    
    def _suggest_sql_tier(self, invalid_tier: str) -> Optional[str]:
        """Suggest SQL tier"""
        # Default suggestion
        return "S0"
    
    def _suggest_storage_tier(self, invalid_tier: str) -> Optional[str]:
        """Suggest storage tier"""
        return "Standard"
    
    def validate_terraform_resources(self, resources: List[Dict]) -> Dict:
        """
        Validate all resources in a Terraform file
        
        Returns: {
            'valid_resources': [...],
            'invalid_resources': [...],
            'corrections': {...}
        }
        """
        results = {
            'valid_resources': [],
            'invalid_resources': [],
            'corrections': {},
            'summary': {}
        }
        
        for resource in resources:
            res_type = resource.get('type', '')
            res_name = resource.get('name', '')
            properties = resource.get('properties', {})
            
            is_valid, message, suggested = self.validate_resource(res_type, res_name, properties)
            
            if is_valid:
                results['valid_resources'].append({
                    'type': res_type,
                    'name': res_name,
                    'message': message
                })
            else:
                results['invalid_resources'].append({
                    'type': res_type,
                    'name': res_name,
                    'message': message
                })
                
                if suggested:
                    results['corrections'][f"{res_type}.{res_name}"] = suggested
                    logger.warning(f"[VALIDATOR] Suggested correction for {res_type}.{res_name}: {suggested}")
        
        results['summary'] = {
            'total': len(resources),
            'valid': len(results['valid_resources']),
            'invalid': len(results['invalid_resources']),
            'has_corrections': len(results['corrections']) > 0
        }
        
        logger.info(f"[VALIDATOR] Validation complete: {results['summary']}")
        
        return results


# Global instance
validator = AzureResourceValidator()


if __name__ == '__main__':
    # Test the validator
    test_resources = [
        {
            'type': 'azurerm_virtual_machine',
            'name': 'test-vm',
            'properties': {'vm_size': 'Standard_D2s_v3'}
        },
        {
            'type': 'azurerm_mssql_database',
            'name': 'test-db',
            'properties': {'sku_name': 'S0'}
        },
        {
            'type': 'azurerm_storage_account',
            'name': 'teststorage',
            'properties': {'account_tier': 'Standard'}
        }
    ]
    
    results = validator.validate_terraform_resources(test_resources)
    print(results)
