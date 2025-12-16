"""
Cloud Infrastructure Pricing Calculator
Compares pricing across AWS, Azure, and GCP based on Terraform code
Supports both real-time and static pricing
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import real-time pricing fetcher
try:
    from real_time_pricing_fetcher import pricing_fetcher, USE_FALLBACK_PRICING
    REAL_TIME_PRICING_ENABLED = True
except ImportError:
    logger.warning("Real-time pricing fetcher not available, using static pricing")
    REAL_TIME_PRICING_ENABLED = False
    USE_FALLBACK_PRICING = True

# Import VM specifications
try:
    from vm_specifications import get_vm_specifications
    VM_SPECS_AVAILABLE = True
except ImportError:
    logger.warning("VM specifications not available")
    VM_SPECS_AVAILABLE = False
    def get_vm_specifications(vm_size):
        return {}

@dataclass
class PricingRate:
    """Pricing information for a resource"""
    resource_type: str
    provider: str
    unit: str
    price_per_unit: float
    description: str

class CloudPricingCalculator:
    """Calculate and compare cloud infrastructure costs across providers"""
    
    # Valid providers
    VALID_PROVIDERS = {'aws', 'azure', 'gcp'}
    
    # Azure VM size mapping - normalize various formats to Standard_XXX format
    AZURE_VM_SIZE_NORMALIZATION = {
        # D-series v3
        'D2_v3': 'Standard_D2s_v3',
        'D4_v3': 'Standard_D4s_v3',
        'D8_v3': 'Standard_D8s_v3',
        'D16_v3': 'Standard_D16s_v3',
        'D32_v3': 'Standard_D32s_v3',
        'd2_v3': 'Standard_D2s_v3',
        'd4_v3': 'Standard_D4s_v3',
        'd8_v3': 'Standard_D8s_v3',
        'd16_v3': 'Standard_D16s_v3',
        'd32_v3': 'Standard_D32s_v3',
        'D2s_v3': 'Standard_D2s_v3',
        'D4s_v3': 'Standard_D4s_v3',
        'D8s_v3': 'Standard_D8s_v3',
        'D16s_v3': 'Standard_D16s_v3',
        'D32s_v3': 'Standard_D32s_v3',
        
        # D-series v4
        'D2_v4': 'Standard_D2s_v4',
        'D4_v4': 'Standard_D4s_v4',
        'D8_v4': 'Standard_D8s_v4',
        'D16_v4': 'Standard_D16s_v4',
        'D32_v4': 'Standard_D32s_v4',
        'D2s_v4': 'Standard_D2s_v4',
        'D4s_v4': 'Standard_D4s_v4',
        'D8s_v4': 'Standard_D8s_v4',
        'D16s_v4': 'Standard_D16s_v4',
        'D32s_v4': 'Standard_D32s_v4',
        
        # B-series
        'B1s': 'Standard_B1s',
        'B2s': 'Standard_B2s',
        'B4ms': 'Standard_B4ms',
        
        # C-series
        'C2_v3': 'Standard_C2s_v3',
        'C4_v3': 'Standard_C4s_v3',
        'C8_v3': 'Standard_C8s_v3',
        'c2_v3': 'Standard_C2s_v3',
        'c4_v3': 'Standard_C4s_v3',
        'c8_v3': 'Standard_C8s_v3',
        'C2s_v3': 'Standard_C2s_v3',
        'C4s_v3': 'Standard_C4s_v3',
        'C8s_v3': 'Standard_C8s_v3',
        
        # E-series
        'E2_v3': 'Standard_E2s_v3',
        'E4_v3': 'Standard_E4s_v3',
        'E2s_v3': 'Standard_E2s_v3',
        'E4s_v3': 'Standard_E4s_v3',
    }
    
    @staticmethod
    def normalize_azure_vm_size(vm_size: str) -> str:
        """
        Normalize Azure VM size to Standard_XXX format for API lookups.
        
        Examples:
            D2_v3 -> Standard_D2s_v3
            D2s_v4 -> Standard_D2s_v4
            Standard_D2s_v4 -> Standard_D2s_v4 (already normalized)
        """
        if not vm_size:
            return 'Standard_B1s'
        
        # Check direct mapping first
        if vm_size in CloudPricingCalculator.AZURE_VM_SIZE_NORMALIZATION:
            return CloudPricingCalculator.AZURE_VM_SIZE_NORMALIZATION[vm_size]
        
        # If already has Standard_ prefix, return as-is
        if vm_size.startswith('Standard_'):
            return vm_size
        
        # Try case-insensitive lookup
        for key, value in CloudPricingCalculator.AZURE_VM_SIZE_NORMALIZATION.items():
            if key.lower() == vm_size.lower():
                return value
        
        # If not found, try to infer the pattern
        # Pattern: D2_v3 or D2s_v3 -> add Standard_ prefix and ensure 's' is present
        vm_upper = vm_size.upper()
        
        # Check if it matches common patterns
        if 'D' in vm_upper and '_V' in vm_upper:
            # Pattern like D2_v3 or D4_v4
            parts = vm_upper.split('_')
            if len(parts) == 2 and parts[0][0] == 'D':
                # Ensure 's' is in the SKU part before version
                sku = parts[0]
                if 's' not in sku.lower():
                    sku = sku[0] + sku[1:] + 's' if len(sku) > 1 else sku + 's'
                return f"Standard_{sku}{parts[1]}"
        
        # Fallback: assume it's a valid Azure SKU and add prefix
        if not vm_size.startswith('Standard_'):
            return f"Standard_{vm_size}"
        
        return vm_size
    
    @staticmethod
    def normalize_azure_region(region: str) -> str:
        """Normalize Azure region names to API format (e.g., 'East US' -> 'eastus')"""
        if not region:
            return 'eastus'
        
        # Mapping of region display names to API names
        region_mapping = {
            'east us': 'eastus',
            'eastus': 'eastus',
            'west us': 'westus',
            'westus': 'westus',
            'us east': 'eastus',
            'us west': 'westus',
            'west us 2': 'westus2',
            'westus2': 'westus2',
            'central us': 'centralus',
            'centralus': 'centralus',
            'north central us': 'northcentralus',
            'northcentralus': 'northcentralus',
            'south central us': 'southcentralus',
            'southcentralus': 'southcentralus',
            'north europe': 'northeurope',
            'northeurope': 'northeurope',
            'west europe': 'westeurope',
            'westeurope': 'westeurope',
            'southeast asia': 'southeastasia',
            'southeastasia': 'southeastasia',
            'east asia': 'eastasia',
            'eastasia': 'eastasia',
            'uk south': 'uksouth',
            'uksouth': 'uksouth',
            'uk west': 'ukwest',
            'ukwest': 'ukwest',
            'canada east': 'canadaeast',
            'canadaeast': 'canadaeast',
            'canada central': 'canadacentral',
            'canadacentral': 'canadacentral',
            'south india': 'southindia',
            'southindia': 'southindia',
            'central india': 'centralindia',
            'centralindia': 'centralindia',
            'west india': 'westindia',
            'westindia': 'westindia',
            'japan east': 'japaneast',
            'japaneast': 'japaneast',
            'japan west': 'japanwest',
            'japanwest': 'japanwest',
            'australia east': 'australiaeast',
            'australiaeast': 'australiaeast',
            'australia southeast': 'australiasoutheast',
            'australiasoutheast': 'australiasoutheast',
            'brazil south': 'brazilsouth',
            'brazilsouth': 'brazilsouth',
            'west asia': 'westasia',
            'westasia': 'westasia',
        }
        
        region_lower = region.strip().lower()
        return region_mapping.get(region_lower, region_lower.replace(' ', '').lower() or 'eastus')
    
    # AWS Pricing (US East 1 region - monthly estimates)
    # Note: Prices calculated as hourly_rate * 730 hours/month
    AWS_PRICING = {
        'ec2': {
            't2.micro': 0.0116 * 730,  # $0.0116/hr → monthly
            't2.small': 0.023 * 730,
            't2.medium': 0.0464 * 730,
            't3.micro': 0.0104 * 730,
            't3.small': 0.0208 * 730,
            't3.medium': 0.0416 * 730,
            'm5.large': 0.096 * 730,
            'm5.xlarge': 0.192 * 730,
            'm5.2xlarge': 0.384 * 730,
            'c5.large': 0.085 * 730,
            'c5.xlarge': 0.17 * 730,
            'c5.2xlarge': 0.34 * 730,
        },
        'rds': {
            'db.t2.micro': 0.017 * 730,
            'db.t2.small': 0.034 * 730,
            'db.t2.medium': 0.067 * 730,
            'db.t3.micro': 0.015 * 730,
            'db.t3.small': 0.03 * 730,
            'db.m5.large': 0.141 * 730,
            'db.m5.xlarge': 0.282 * 730,
        },
        's3': {
            'standard': 0.023,  # per GB/month
            'infrequent_access': 0.0125,
            'glacier': 0.004,
        },
        'dynamodb': {
            'write_capacity': 1.25,  # per WCU/month
            'read_capacity': 0.25,   # per RCU/month
        },
        'lambda': {
            'invocation': 0.0000002,  # per invocation
            'gb_second': 0.0000166667,  # per GB-second
        },
        'alb': {
            'hours': 0.0225 * 730,
            'lcu': 0.006,  # per LCU hour
        },
        'vpc': {
            'nat_gateway': 32 + (0.045 * 1024),  # fixed + per GB
        },
        'cloudfront': {
            'data_out': 0.085,  # per GB
        },
    }
    
    # Azure Pricing (East US region - monthly estimates)
    AZURE_PRICING = {
        'virtual_machine': {
            # B-series (burstable)
            'Standard_B1s': 0.012 * 730,
            'Standard_B2s': 0.048 * 730,
            'Standard_B4ms': 0.192 * 730,
            # D-series v3 (general purpose)
            'Standard_D2s_v3': 0.11 * 730,
            'Standard_D4s_v3': 0.22 * 730,
            'Standard_D8s_v3': 0.44 * 730,
            'Standard_D16s_v3': 0.88 * 730,
            'Standard_D32s_v3': 1.76 * 730,
            # D-series v4 (general purpose)
            'Standard_D2s_v4': 0.096 * 730,
            'Standard_D4s_v4': 0.192 * 730,
            'Standard_D8s_v4': 0.384 * 730,
            'Standard_D16s_v4': 0.768 * 730,
            'Standard_D32s_v4': 1.536 * 730,
            # D-series v5 (general purpose)
            'Standard_D2s_v5': 0.086 * 730,
            'Standard_D4s_v5': 0.172 * 730,
            'Standard_D8s_v5': 0.344 * 730,
            'Standard_D16s_v5': 0.688 * 730,
            'Standard_D32s_v5': 1.376 * 730,
            # E-series v3 (memory optimized)
            'Standard_E2s_v3': 0.126 * 730,
            'Standard_E4s_v3': 0.252 * 730,
            'Standard_E8s_v3': 0.504 * 730,
            'Standard_E16s_v3': 1.008 * 730,
            'Standard_E32s_v3': 2.016 * 730,
            # Common variants
            'Standard_D32a_v4': 1.536 * 730,  # ~$1121/month (8 vCPU, 128GB RAM)
        },
        'sql_server': {
            'S0': 0.439,  # monthly
            'S1': 2.195,
            'S2': 4.39,
            'P1': 12.5,
            'P2': 25,
        },
        'storage_account': {
            'blob_standard': 0.0184,  # per GB/month
            'blob_hot': 0.0184,
            'blob_cool': 0.01,
        },
        'app_service': {
            'B1': 10.5,
            'B2': 21,
            'B3': 42,
            'S1': 73,
            'S2': 146,
        },
        'function': {
            'execution': 0.0000002,
            'gb_second': 0.000016,
        },
        'application_gateway': {
            'hours': 0.246 * 730,
            'processed_data': 0.0161,  # per GB
        },
        'virtual_network': {
            'peering': 0.012 * 730,
        },
    }
    
    # GCP Pricing (US region - monthly estimates)
    GCP_PRICING = {
        'instance': {
            'f1-micro': 0.0076 * 730,
            'g1-small': 0.0356 * 730,
            'n1-standard-1': 0.0475 * 730,
            'n1-standard-2': 0.095 * 730,
            'n1-standard-4': 0.19 * 730,
            'n1-highmem-2': 0.1184 * 730,
            'n1-highmem-4': 0.2368 * 730,
        },
        'cloud_sql': {
            'db-f1-micro': 0.0068 * 730,
            'db-g1-small': 0.0288 * 730,
            'db-n1-standard-1': 0.0394 * 730,
            'db-n1-standard-2': 0.0788 * 730,
        },
        'cloud_storage': {
            'standard': 0.020,  # per GB/month
            'nearline': 0.010,
            'coldline': 0.004,
        },
        'firestore': {
            'read': 0.06 / 100000,  # per read
            'write': 0.18 / 100000,  # per write
        },
        'cloud_functions': {
            'invocation': 0.0000004,
            'gb_second': 0.0000025,
        },
        'cloud_load_balancing': {
            'hours': 0.035 * 730,
            'processed_data': 0.006,  # per GB
        },
    }
    
    def __init__(self):
        self.resources: List[Dict] = []
        self.pricing_breakdown: Dict = {}
    
    def add_resource(self, name: str, resource_type: str, provider: str, 
                    instance_type: Optional[str] = None, quantity: int = 1, 
                    config: Optional[Dict] = None) -> None:
        """Add a resource for pricing calculation
        
        Args:
            name: Resource name for identification
            resource_type: Type of resource (e.g., 'aws_instance', 'azurerm_virtual_machine')
            provider: Cloud provider ('aws', 'azure', 'gcp')
            instance_type: Specific instance/SKU type
            quantity: Number of instances
            config: Additional configuration parameters
            
        Raises:
            ValueError: If provider is invalid or quantity is invalid
        """
        provider_lower = provider.lower()
        
        # Validate provider
        if provider_lower not in self.VALID_PROVIDERS:
            raise ValueError(
                f"Invalid provider '{provider}'. Must be one of: {self.VALID_PROVIDERS}"
            )
        
        # Validate quantity
        if quantity < 1:
            raise ValueError(f"Quantity must be at least 1, got {quantity}")
        
        # Validate resource_type
        if not resource_type or not isinstance(resource_type, str):
            raise ValueError("Resource type must be a non-empty string")
        
        logger.info(f"Adding resource: {name} ({resource_type}) on {provider_lower}")
        
        self.resources.append({
            'name': name,
            'type': resource_type,
            'provider': provider_lower,
            'instance_type': instance_type,
            'quantity': quantity,
            'config': config or {}
        })
    
    def calculate_resource_cost(self, resource: Dict) -> Tuple[float, str]:
        """Calculate cost for a single resource
        
        Args:
            resource: Resource dictionary with provider, type, instance_type, etc.
            
        Returns:
            Tuple of (cost in USD/month, description)
        """
        provider = resource['provider']
        res_type = resource['type']
        instance_type = resource.get('instance_type')
        quantity = resource.get('quantity', 1)
        
        try:
            if provider == 'aws':
                return self._calculate_aws_cost(res_type, instance_type, quantity, resource)
            elif provider == 'azure':
                return self._calculate_azure_cost(res_type, instance_type, quantity, resource)
            elif provider == 'gcp':
                return self._calculate_gcp_cost(res_type, instance_type, quantity, resource)
        except Exception as e:
            logger.warning(f"Error calculating cost for {res_type}: {e}")
            return 0, f"Error calculating {res_type} cost"
        
        return 0, "Unknown provider"
    
    def _get_resource_price(self, provider: str, res_type: str, instance_type: str) -> Tuple[float, str]:
        """
        Get price for a resource - tries real-time API first, then fallback
        Returns: (price, source)
        """
        if REAL_TIME_PRICING_ENABLED and pricing_fetcher:
            try:
                result = pricing_fetcher.get_pricing(provider, res_type, instance_type)
                if result:
                    logger.info(f"Using real-time pricing for {provider} {res_type} {instance_type}")
                    return result['price'], "real-time API"
            except Exception as e:
                logger.warning(f"Real-time pricing failed: {e}, falling back to static pricing")
        
        # Fallback to static pricing
        return None, "static"
    
    def _calculate_aws_cost(self, res_type: str, instance_type: str, 
                           quantity: int, resource: Dict) -> Tuple[float, str]:
        """Calculate AWS resource cost - uses real-time AWS API pricing (NO STATIC FALLBACK)"""
        res_type_lower = res_type.lower().replace('aws_', '')
        
        # MANDATE: Real-time pricing is REQUIRED for AWS
        if not REAL_TIME_PRICING_ENABLED or not pricing_fetcher:
            logger.error(f"[AWS_PRICING] ✗ FATAL: Real-time AWS pricing API is NOT available - cannot calculate cost for {res_type}")
            return 0, f"{res_type} - AWS API REQUIRED BUT NOT AVAILABLE"
        
        if res_type_lower == 'instance' or res_type_lower == 'ec2':
            instance_type = instance_type or 't2.micro'
            logger.info(f"[AWS_PRICING] EC2 instance detected: {instance_type}")
            try:
                logger.info(f"[AWS_PRICING] Calling AWS API for EC2: '{instance_type}'")
                real_time_price = pricing_fetcher.get_pricing('aws', 'ec2', instance_type)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AWS_PRICING] ✓ AWS API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"EC2 {instance_type} ({quantity}x) - LIVE AWS API"
                else:
                    logger.error(f"[AWS_PRICING] ✗ AWS API returned no valid price for {instance_type}")
                    return 0, f"EC2 {instance_type} - AWS API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AWS_PRICING] ✗ Exception calling AWS API for EC2: {e}")
                return 0, f"EC2 {instance_type} - AWS API ERROR"
        
        elif res_type_lower == 'db_instance' or res_type_lower == 'rds':
            instance_type = instance_type or 'db.t2.micro'
            logger.info(f"[AWS_PRICING] RDS instance detected: {instance_type}")
            try:
                logger.info(f"[AWS_PRICING] Calling AWS API for RDS: '{instance_type}'")
                real_time_price = pricing_fetcher.get_pricing('aws', 'rds', instance_type)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AWS_PRICING] ✓ AWS API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"RDS {instance_type} ({quantity}x) - LIVE AWS API"
                else:
                    logger.error(f"[AWS_PRICING] ✗ AWS API returned no valid price for {instance_type}")
                    return 0, f"RDS {instance_type} - AWS API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AWS_PRICING] ✗ Exception calling AWS API for RDS: {e}")
                return 0, f"RDS {instance_type} - AWS API ERROR"
        
        elif res_type_lower == 's3' or res_type_lower == 'bucket':
            storage_gb = resource.get('config', {}).get('size_gb', 100)
            logger.info(f"[AWS_PRICING] S3 bucket detected: {storage_gb}GB")
            try:
                logger.info(f"[AWS_PRICING] Calling AWS API for S3")
                real_time_price = pricing_fetcher.get_pricing('aws', 's3', 'standard')
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * storage_gb * quantity
                    logger.info(f"[AWS_PRICING] ✓ AWS API returned: ${real_time_price['price']:.4f}/GB/month → Total: ${cost:.2f}/month")
                    return cost, f"S3 {storage_gb}GB ({quantity}x) - LIVE AWS API"
                else:
                    logger.error(f"[AWS_PRICING] ✗ AWS API returned no valid price for S3")
                    return 0, f"S3 {storage_gb}GB - AWS API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AWS_PRICING] ✗ Exception calling AWS API for S3: {e}")
                return 0, f"S3 {storage_gb}GB - AWS API ERROR"
        
        else:
            logger.error(f"[AWS_PRICING] ✗ UNSUPPORTED AWS resource type: {res_type}")
            return 0, f"{res_type} - UNSUPPORTED AWS RESOURCE TYPE"
    
    def _calculate_azure_cost(self, res_type: str, instance_type: str, 
                             quantity: int, resource: Dict) -> Tuple[float, str]:
        """Calculate Azure resource cost - ONLY uses real-time Azure API pricing (NO STATIC FALLBACK)"""
        res_type_lower = res_type.lower().replace('azurerm_', '')
        
        logger.info(f"[AZURE_PRICING] Calculating cost for: type={res_type}, instance_type={instance_type}, qty={quantity}")
        
        # MANDATE: Real-time pricing is REQUIRED for Azure
        if not REAL_TIME_PRICING_ENABLED or not pricing_fetcher:
            logger.error("[AZURE_PRICING] ✗ FATAL: Real-time Azure pricing API is NOT available - cannot calculate ANY cost")
            return 0, f"{res_type} - AZURE API REQUIRED BUT NOT AVAILABLE"
        
        if 'virtual_machine' in res_type_lower:
            if not instance_type:
                logger.error("[AZURE_PRICING] ✗ Instance type required for VM pricing but not provided")
                return 0, f"VM - NO INSTANCE TYPE PROVIDED"
            normalized_size = self.normalize_azure_vm_size(instance_type)
            logger.info(f"[AZURE_PRICING] Normalized VM size: '{instance_type}' → '{normalized_size}'")
            region = resource.get('config', {}).get('region', 'eastus')
            normalized_region = self.normalize_azure_region(region)
            logger.info(f"[AZURE_PRICING] Normalized region: '{region}' → '{normalized_region}'")
            os_type = resource.get('config', {}).get('os_type', 'windows').lower()
            logger.info(f"[AZURE_PRICING] OS type detected: {os_type}")
            
            try:
                logger.info(f"[AZURE_PRICING] Calling Azure API for VM: '{normalized_size}' in '{normalized_region}' (OS: {os_type})")
                real_time_price = pricing_fetcher.get_pricing('azure', 'vm', normalized_size, region=normalized_region, os_type=os_type)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AZURE_PRICING] ✓ Azure API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"VM {normalized_size} ({quantity}x) - LIVE AZURE API ({os_type})"
                else:
                    logger.error(f"[AZURE_PRICING] ✗ Azure API returned no valid price for VM {normalized_size}")
                    return 0, f"VM {normalized_size} - AZURE API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AZURE_PRICING] ✗ Exception calling Azure API for VM: {e}")
                return 0, f"VM {normalized_size} - AZURE API ERROR: {str(e)[:50]}"

        elif res_type_lower in ['sql_database', 'sql_server', 'mssql_server', 'mssql_database']:
            sql_tier = instance_type or resource.get('config', {}).get('sku_name', 'S0')
            region = resource.get('config', {}).get('region', 'eastus')
            logger.info(f"[AZURE_PRICING] SQL resource detected: tier={sql_tier}, region={region}")
            
            try:
                logger.info(f"[AZURE_PRICING] Calling Azure API for SQL: '{sql_tier}' in '{region}'")
                real_time_price = pricing_fetcher.get_pricing('azure', 'sql', sql_tier, region=region)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AZURE_PRICING] ✓ Azure API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"SQL Database {sql_tier} ({quantity}x) - LIVE AZURE API"
                else:
                    logger.error(f"[AZURE_PRICING] ✗ Azure API returned no valid price for SQL {sql_tier}")
                    return 0, f"SQL Database {sql_tier} - AZURE API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AZURE_PRICING] ✗ Exception calling Azure API for SQL: {e}")
                return 0, f"SQL Database {sql_tier} - AZURE API ERROR: {str(e)[:50]}"
        
        elif res_type_lower == 'storage_account':
            region = resource.get('config', {}).get('region', 'eastus')
            storage_gb = resource.get('config', {}).get('size_gb', 100)  # Default 100GB if not specified
            
            if storage_gb <= 0:
                storage_gb = 100
                logger.warning(f"[AZURE_PRICING] Storage size not specified, using default 100GB")
            
            logger.info(f"[AZURE_PRICING] Storage account detected: {storage_gb}GB in '{region}'")
            
            try:
                logger.info(f"[AZURE_PRICING] Calling Azure API for Storage: 'blob_standard' in '{region}'")
                real_time_price = pricing_fetcher.get_pricing('azure', 'storage', 'blob_standard', region=region)
                if real_time_price and real_time_price.get('price'):
                    # Price from API is per-GB-per-month
                    cost = real_time_price['price'] * storage_gb * quantity
                    logger.info(f"[AZURE_PRICING] ✓ Azure API returned: ${real_time_price['price']:.4f}/GB/month → Total: ${cost:.2f}/month for {storage_gb}GB")
                    return cost, f"Storage Account {storage_gb}GB ({quantity}x) - LIVE AZURE API"
                else:
                    logger.error(f"[AZURE_PRICING] ✗ Azure API returned no valid price for storage")
                    return 0, f"Storage Account {storage_gb}GB - AZURE API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AZURE_PRICING] ✗ Exception calling Azure API for Storage: {e}")
                return 0, f"Storage Account {storage_gb}GB - AZURE API ERROR: {str(e)[:50]}"
        
        elif res_type_lower == 'app_service':
            if not instance_type:
                logger.error("[AZURE_PRICING] ✗ Instance type (plan tier) required for App Service pricing")
                return 0, f"App Service - NO PLAN TIER PROVIDED"
            
            region = resource.get('config', {}).get('region', 'eastus')
            logger.info(f"[AZURE_PRICING] App Service detected: plan={instance_type}, region={region}")
            
            try:
                logger.info(f"[AZURE_PRICING] Calling Azure API for App Service: '{instance_type}' in '{region}'")
                real_time_price = pricing_fetcher.get_pricing('azure', 'app_service', instance_type, region=region)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AZURE_PRICING] ✓ Azure API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"App Service {instance_type} ({quantity}x) - LIVE AZURE API"
                else:
                    logger.error(f"[AZURE_PRICING] ✗ Azure API returned no valid price for App Service {instance_type}")
                    return 0, f"App Service {instance_type} - AZURE API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AZURE_PRICING] ✗ Exception calling Azure API for App Service: {e}")
                return 0, f"App Service {instance_type} - AZURE API ERROR: {str(e)[:50]}"
        
        elif res_type_lower == 'function_app' or res_type_lower == 'function':
            region = resource.get('config', {}).get('region', 'eastus')
            logger.info(f"[AZURE_PRICING] Function App detected: region={region}")
            
            try:
                logger.info(f"[AZURE_PRICING] Calling Azure API for Function App in '{region}'")
                real_time_price = pricing_fetcher.get_pricing('azure', 'function', 'consumption', region=region)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AZURE_PRICING] ✓ Azure API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"Function App ({quantity}x) - LIVE AZURE API"
                else:
                    logger.error(f"[AZURE_PRICING] ✗ Azure API returned no valid price for Function App")
                    return 0, f"Function App - AZURE API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AZURE_PRICING] ✗ Exception calling Azure API for Function App: {e}")
                return 0, f"Function App - AZURE API ERROR: {str(e)[:50]}"
        
        elif res_type_lower == 'application_gateway':
            region = resource.get('config', {}).get('region', 'eastus')
            logger.info(f"[AZURE_PRICING] Application Gateway detected: region={region}")
            
            try:
                logger.info(f"[AZURE_PRICING] Calling Azure API for Application Gateway in '{region}'")
                real_time_price = pricing_fetcher.get_pricing('azure', 'application_gateway', 'standard', region=region)
                if real_time_price and real_time_price.get('price'):
                    cost = real_time_price['price'] * quantity
                    logger.info(f"[AZURE_PRICING] ✓ Azure API returned: ${real_time_price['price']:.2f}/month → Total: ${cost:.2f}/month")
                    return cost, f"Application Gateway ({quantity}x) - LIVE AZURE API"
                else:
                    logger.error(f"[AZURE_PRICING] ✗ Azure API returned no valid price for Application Gateway")
                    return 0, f"Application Gateway - AZURE API RETURNED NO PRICE"
            except Exception as e:
                logger.error(f"[AZURE_PRICING] ✗ Exception calling Azure API for Application Gateway: {e}")
                return 0, f"Application Gateway - AZURE API ERROR: {str(e)[:50]}"
        
        elif res_type_lower == 'virtual_network':
            # Virtual Networks are free in Azure
            logger.info("[AZURE_PRICING] Virtual Network is FREE in Azure")
            return 0, f"Virtual Network (free)"
        
        elif res_type_lower == 'subnet':
            # Subnets are free in Azure
            logger.info("[AZURE_PRICING] Subnet is FREE in Azure")
            return 0, f"Subnet (free)"
        
        elif res_type_lower == 'network_interface':
            # Network Interfaces are free in Azure
            logger.info("[AZURE_PRICING] Network Interface is FREE in Azure")
            return 0, f"Network Interface (free)"
        
        elif res_type_lower == 'public_ip':
            # Public IPs are free when used; charged when idle
            logger.info("[AZURE_PRICING] Public IP is FREE when in-use")
            return 0, f"Public IP (free when in-use)"
        
        elif res_type_lower == 'resource_group':
            # Resource Groups are free in Azure
            logger.info("[AZURE_PRICING] Resource Group is FREE in Azure")
            return 0, f"Resource Group (free)"
        
        elif res_type_lower == 'storage_container':
            # Storage containers are free; cost is in the storage account
            logger.info("[AZURE_PRICING] Storage Container is FREE (cost included in Storage Account)")
            return 0, f"Storage Container (free - cost in Storage Account)"
        
        else:
            logger.error(f"[AZURE_PRICING] ✗ UNSUPPORTED Azure resource type: {res_type} - cannot calculate pricing")
            return 0, f"{res_type} - UNSUPPORTED AZURE RESOURCE TYPE"
    
    def _calculate_gcp_cost(self, res_type: str, instance_type: str, 
                           quantity: int, resource: Dict) -> Tuple[float, str]:
        """Calculate GCP resource cost"""
        res_type_lower = res_type.lower().replace('google_', '')
        
        if res_type_lower == 'instance' or res_type_lower == 'compute_instance':
            instance_type = instance_type or 'n1-standard-1'
            if instance_type in self.GCP_PRICING.get('instance', {}):
                cost = self.GCP_PRICING['instance'][instance_type] * quantity
                return cost, f"Compute {instance_type} ({quantity} instances)"
            return 35, f"Compute {instance_type} (estimated)"
        
        elif res_type_lower == 'cloud_sql_instance' or res_type_lower == 'cloud_sql':
            instance_type = instance_type or 'db-f1-micro'
            if instance_type in self.GCP_PRICING.get('cloud_sql', {}):
                cost = self.GCP_PRICING['cloud_sql'][instance_type] * quantity
                return cost, f"Cloud SQL {instance_type} ({quantity})"
            return 25, f"Cloud SQL (estimated)"
        
        elif res_type_lower == 'storage_bucket' or res_type_lower == 'cloud_storage':
            storage_gb = resource.get('config', {}).get('size_gb', 100)
            cost = self.GCP_PRICING['cloud_storage']['standard'] * storage_gb
            return cost, f"Cloud Storage {storage_gb}GB"
        
        elif res_type_lower == 'firestore_database' or res_type_lower == 'firestore':
            cost = 0.06  # Minimal estimate
            return cost, f"Firestore (estimate)"
        
        elif res_type_lower == 'cloudfunctions_function' or res_type_lower == 'cloud_function':
            invocations = resource.get('config', {}).get('monthly_invocations', 1000000)
            cost = invocations * self.GCP_PRICING['cloud_functions']['invocation']
            return cost, f"Cloud Functions {invocations/1e6:.1f}M invocations"
        
        elif res_type_lower == 'compute_forwarding_rule' or res_type_lower == 'load_balancer':
            cost = self.GCP_PRICING['cloud_load_balancing']['hours']
            return cost, f"Cloud Load Balancing"
        
        else:
            return 3, f"{res_type} (GCP estimate)"
    
    def calculate_total_cost(self) -> Dict:
        """Calculate total costs across all providers"""
        provider_costs = {'aws': 0, 'azure': 0, 'gcp': 0}
        provider_breakdown = {'aws': [], 'azure': [], 'gcp': []}
        
        for resource in self.resources:
            cost, description = self.calculate_resource_cost(resource)
            provider = resource['provider']
            provider_costs[provider] += cost
            provider_breakdown[provider].append({
                'name': resource['name'],
                'type': resource['type'],
                'cost': cost,
                'description': description
            })
        
        return {
            'total_costs': provider_costs,
            'breakdown': provider_breakdown,
            'comparison': self._generate_comparison(provider_costs)
        }
    
    def _generate_comparison(self, costs: Dict) -> Dict:
        """Generate cost comparison and recommendations"""
        sorted_providers = sorted(costs.items(), key=lambda x: x[1])
        cheapest = sorted_providers[0][0]
        
        comparison = {
            'cheapest_provider': cheapest,
            'monthly_costs': costs,
            'annual_costs': {k: v * 12 for k, v in costs.items()},
            'savings_potential': {}
        }
        
        for provider, cost in costs.items():
            if provider != cheapest:
                savings = cost - costs[cheapest]
                if cost > 0:
                    savings_pct = (savings / cost) * 100
                else:
                    savings_pct = 0
                comparison['savings_potential'][provider] = {
                    'monthly_savings': savings,
                    'annual_savings': savings * 12,
                    'percent_difference': savings_pct
                }
        
        return comparison


def _extract_terraform_value(terraform_code: str, reference: str) -> Optional[str]:
    """
    Extract actual value from Terraform code for a variable reference.
    Examples:
        - "azurerm_resource_group.vm.location" -> find "location = eastus" in resource
        - "${var.vm_name}" -> find "default = ..." in variable definition
    """
    if not reference or not isinstance(reference, str):
        return None
    
    reference_str = str(reference).strip()
    
    # If it's a literal value (not a reference), return as-is
    if not any(c in reference_str for c in ['.', '$', '{', '}']):
        return reference_str
    
    try:
        import re
        
        # Handle direct variable references like "azurerm_resource_group.main.location"
        if '.' in reference_str and not reference_str.startswith('$'):
            parts = reference_str.split('.')
            if len(parts) >= 3:
                resource_type = parts[0]
                resource_name = parts[1]
                property_name = '.'.join(parts[2:])
                
                # Find the resource block in Terraform code - use flexible matching
                # Pattern: resource "type" "name" { ... }
                # We need to properly match nested braces
                
                resource_body = None
                # Try to find the resource declaration first
                resource_pattern = rf'resource\s+"{re.escape(resource_type)}"\s+"{re.escape(resource_name)}"\s*\{{'
                resource_match = re.search(resource_pattern, terraform_code)
                
                if resource_match:
                    # Found resource declaration, now extract everything until matching closing brace
                    start_pos = resource_match.end() - 1  # Position of opening brace
                    brace_count = 1
                    pos = start_pos + 1
                    
                    # Scan through characters, counting braces to find the matching closing brace
                    while pos < len(terraform_code) and brace_count > 0:
                        char = terraform_code[pos]
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                        pos += 1
                    
                    if brace_count == 0:
                        # Found matching closing brace
                        resource_body = terraform_code[start_pos+1:pos-1]
                        logger.info(f"[PRICING] Found resource block for {resource_type}.{resource_name} (body length: {len(resource_body)})")
                
                if resource_body:
                    # Extract the property value - handle quoted and unquoted values
                    # Pattern: location = "eastus" or location = eastus or location = azurerm_resource_group.main.location
                    logger.info(f"[PRICING] Searching for property '{property_name}' in resource body (length: {len(resource_body)})")
                    logger.info(f"[PRICING] Resource body preview: {resource_body[:300]}...")
                    prop_patterns = [
                        rf'{property_name}\s*=\s*"([^"]*)"',  # Quoted string
                        rf'{property_name}\s*=\s*\'([^\']*)\'',  # Single quoted
                        rf'{property_name}\s*=\s*([^,\n}}]+)',  # Unquoted
                    ]
                    
                    for i, prop_pattern in enumerate(prop_patterns):
                        logger.info(f"[PRICING] Trying pattern {i+1}: {prop_pattern}")
                        prop_match = re.search(prop_pattern, resource_body)
                        if prop_match:
                            value = prop_match.group(1).strip()
                            logger.info(f"[PRICING] ✓ Pattern {i+1} matched! Resolved Terraform reference '{reference_str}' → '{value}'")
                            # Recursively resolve if value is also a reference
                            if '.' in value or '$' in value:
                                resolved = _extract_terraform_value(terraform_code, value)
                                if resolved:
                                    return resolved
                            return value
                    
                    logger.warning(f"[PRICING] ⚠️ No patterns matched for property '{property_name}' in resource body")
        
        # Handle variable references like "${var.vm_name}" or "var.vm_name"
        if reference_str.startswith('${var.') or reference_str.startswith('var.'):
            var_name = reference_str.replace('${var.', '').replace('var.', '').rstrip('}')
            pattern = rf'variable\s+"{var_name}"\s*\{{([\s\S]*?)\}}'
            match = re.search(pattern, terraform_code, re.DOTALL)
            if match:
                var_body = match.group(1)
                # Look for default value
                default_match = re.search(r'default\s*=\s*"([^"]*)"', var_body)
                if not default_match:
                    default_match = re.search(r'default\s*=\s*\'([^\']*)\'', var_body)
                if not default_match:
                    default_match = re.search(r'default\s*=\s*([^,\n}}]+)', var_body)
                
                if default_match:
                    value = default_match.group(1).strip()
                    logger.info(f"[PRICING] Resolved variable reference '{reference_str}' → '{value}'")
                    return value
    except Exception as e:
        logger.warning(f"Failed to resolve Terraform reference '{reference_str}': {e}")
    
    return None


def calculate_terraform_pricing(terraform_code: str) -> Dict:
    """
    Parse Terraform code and calculate multi-cloud pricing
    
    Args:
        terraform_code: Terraform configuration as string
        
    Returns:
        Dictionary with total costs, breakdown, and comparisons
        
    Raises:
        ImportError: If TerraformParser is not available
    """
    try:
        from diagram_generator import TerraformParser
    except ImportError as e:
        logger.error(f"Failed to import TerraformParser: {e}")
        raise ImportError(
            "TerraformParser not found. Ensure diagram_generator module is available."
        ) from e
    
    # Log the terraform code being processed for debugging
    logger.info(f"[PRICING] Processing terraform code ({len(terraform_code)} chars)")
    logger.info(f"[PRICING] Terraform preview: {terraform_code[:300]}...")
    
    try:
        parser = TerraformParser(terraform_code)
    except Exception as e:
        logger.error(f"Failed to parse Terraform code: {e}")
        raise ValueError(f"Invalid Terraform code: {e}") from e
    
    calculator = CloudPricingCalculator()
    
    for resource in parser.resources:
        # DEBUG: Log resource details
        logger.info(f"[PRICING] Processing resource: type={resource.type}, name={resource.name}")
        
        # Extract provider from resource type (e.g., aws_ec2_instance -> aws)
        parts = resource.type.split('_')
        if parts[0] in ['aws', 'azurerm', 'google']:
            provider = parts[0] if parts[0] != 'azurerm' else 'azure'
        else:
            logger.warning(f"Unknown provider for resource type: {resource.type}")
            continue
        
        # Determine instance type if available
        instance_type = None
        config = {}
        
        # Use resource.config if available, otherwise build from properties
        if hasattr(resource, 'config') and resource.config:
            config = resource.config.copy()
            logger.info(f"[PRICING] Using resource.config: {config}")
        
        if hasattr(resource, 'properties') and resource.properties:
            # Try multiple property names for instance type
            for prop_name in ['size', 'instance_type', 'machine_type', 'vm_size', 'instance_class', 'sku_name']:
                if prop_name in resource.properties:
                    instance_type = resource.properties[prop_name]
                    logger.info(f"[PRICING] Found instance_type '{instance_type}' from property '{prop_name}'")
                    break
            
            # Extract region/location
            region = resource.properties.get('location') or resource.properties.get('region')
            if region:
                logger.info(f"[PRICING] Extracted region/location from properties: '{region}'")
                # Try to resolve Terraform variable references
                if '.' in str(region) or '$' in str(region):
                    logger.info(f"[PRICING] Region contains reference, attempting to extract actual value...")
                    resolved_region = _extract_terraform_value(terraform_code, region)
                    if resolved_region:
                        region = resolved_region
                        logger.info(f"[PRICING] ✓ Resolved region reference to '{region}'")
                    else:
                        logger.warning(f"[PRICING] ⚠️ Failed to resolve region reference '{region}'")
                config['region'] = region
        
        try:
            calculator.add_resource(
                name=resource.name,
                resource_type=resource.type,
                provider=provider,
                instance_type=instance_type,
                quantity=1,
                config=config
            )
            logger.info(f"[PRICING] Added resource: {resource.name} (type={resource.type}, instance_type={instance_type})")
        except Exception as e:
            logger.warning(f"Skipping resource {resource.name}: {e}")
            continue
    
    return calculator.calculate_total_cost()


if __name__ == '__main__':
    # Example usage with error handling
    try:
        calc = CloudPricingCalculator()
        calc.add_resource('web-server', 'aws_instance', 'aws', 't2.micro')
        calc.add_resource('database', 'aws_db_instance', 'aws', 'db.t2.small')
        calc.add_resource('storage', 'aws_s3_bucket', 'aws', config={'size_gb': 500})
        
        results = calc.calculate_total_cost()
        print(json.dumps(results, indent=2, default=str))
    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
