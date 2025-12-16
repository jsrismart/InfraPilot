"""
Real-time pricing fetcher for AWS, Azure, and GCP
Handles API calls with caching and fallback mechanisms
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import hashlib

try:
    import boto3
except ImportError:
    boto3 = None

try:
    from azure.identity import DefaultAzureCredential
except ImportError:
    DefaultAzureCredential = None

try:
    from google.cloud import billing_v1
except ImportError:
    billing_v1 = None

from pricing_config import (
    AWS_CONFIG, AZURE_CONFIG, GCP_CONFIG, 
    PRICING_CACHE, USE_FALLBACK_PRICING, DEFAULT_CURRENCY
)

logger = logging.getLogger(__name__)

class PricingCache:
    """Simple file-based cache for pricing data"""
    
    def __init__(self, cache_dir: str = "./pricing_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Generate cache file path from key"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_key}.json")
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        if not PRICING_CACHE["enabled"]:
            return None
        
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if cache has expired
            cached_time = datetime.fromisoformat(data.get('cached_at', ''))
            if datetime.now() - cached_time > timedelta(hours=PRICING_CACHE["ttl_hours"]):
                os.remove(cache_path)
                return None
            
            logger.info(f"Cache hit for: {key}")
            return data.get('data')
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key: str, data: Dict) -> None:
        """Cache data with timestamp"""
        if not PRICING_CACHE["enabled"]:
            return
        
        try:
            cache_path = self._get_cache_path(key)
            cache_data = {
                'data': data,
                'cached_at': datetime.now().isoformat(),
                'key': key
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info(f"Cached data for: {key}")
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")


class AWSPricingFetcher:
    """Fetch real-time pricing from AWS Pricing API"""
    
    def __init__(self):
        self.enabled = AWS_CONFIG["enabled"] and boto3 is not None
        self.cache = PricingCache()
        if self.enabled:
            try:
                self.client = boto3.client(
                    'pricing',
                    region_name=AWS_CONFIG["region"]
                )
                logger.info("AWS Pricing API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize AWS Pricing client: {e}")
                self.enabled = False
    
    def get_ec2_pricing(self, instance_type: str, region: str = "us-east-1") -> Optional[float]:
        """Get EC2 instance pricing"""
        cache_key = f"aws_ec2_{instance_type}_{region}"
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached.get('price')
        
        if not self.enabled:
            return None
        
        try:
            response = self.client.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                    {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                    {'Type': 'TERM_MATCH', 'Field': 'licenseModel', 'Value': 'No License required'},
                ],
                MaxResults=1
            )
            
            if response['PriceList']:
                pricing_data = json.loads(response['PriceList'][0])
                # Extract on-demand pricing
                terms = pricing_data.get('terms', {}).get('OnDemand', {})
                for term_key in terms:
                    term_data = terms[term_key]
                    for price_key in term_data.get('priceDimensions', {}):
                        price_dim = term_data['priceDimensions'][price_key]
                        price = float(price_dim['pricePerUnit']['USD'])
                        
                        # Cache the result
                        self.cache.set(cache_key, {'price': price, 'timestamp': datetime.now().isoformat()})
                        return price
        
        except Exception as e:
            logger.error(f"Error fetching EC2 pricing for {instance_type}: {e}")
        
        return None
    
    def get_rds_pricing(self, instance_class: str, engine: str = "mysql") -> Optional[float]:
        """Get RDS instance pricing"""
        cache_key = f"aws_rds_{instance_class}_{engine}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached.get('price')
        
        if not self.enabled:
            return None
        
        try:
            response = self.client.get_products(
                ServiceCode='AmazonRDS',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': engine},
                    {'Type': 'TERM_MATCH', 'Field': 'instanceClass', 'Value': instance_class},
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                    {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': 'Single-AZ'},
                ],
                MaxResults=1
            )
            
            if response['PriceList']:
                pricing_data = json.loads(response['PriceList'][0])
                terms = pricing_data.get('terms', {}).get('OnDemand', {})
                for term_key in terms:
                    term_data = terms[term_key]
                    for price_key in term_data.get('priceDimensions', {}):
                        price_dim = term_data['priceDimensions'][price_key]
                        price = float(price_dim['pricePerUnit']['USD'])
                        self.cache.set(cache_key, {'price': price, 'timestamp': datetime.now().isoformat()})
                        return price
        
        except Exception as e:
            logger.error(f"Error fetching RDS pricing for {instance_class}: {e}")
        
        return None
    
    def get_s3_pricing(self, storage_class: str = "STANDARD") -> Optional[float]:
        """Get S3 storage pricing (per GB)"""
        cache_key = f"aws_s3_{storage_class}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached.get('price')
        
        if not self.enabled:
            return None
        
        try:
            response = self.client.get_products(
                ServiceCode='AmazonS3',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'storageClass', 'Value': storage_class},
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                ],
                MaxResults=1
            )
            
            if response['PriceList']:
                pricing_data = json.loads(response['PriceList'][0])
                terms = pricing_data.get('terms', {}).get('OnDemand', {})
                for term_key in terms:
                    term_data = terms[term_key]
                    for price_key in term_data.get('priceDimensions', {}):
                        price_dim = term_data['priceDimensions'][price_key]
                        price = float(price_dim['pricePerUnit']['USD'])
                        self.cache.set(cache_key, {'price': price, 'timestamp': datetime.now().isoformat()})
                        return price
        
        except Exception as e:
            logger.error(f"Error fetching S3 pricing for {storage_class}: {e}")
        
        return None


class AzurePricingFetcher:
    """Fetch real-time pricing from Azure Pricing API (direct from Azure Calculator)"""
    
    def __init__(self):
        self.enabled = AZURE_CONFIG["enabled"]
        self.cache = PricingCache()
        self.region_map = {
            'eastus': 'US East',
            'eastus2': 'US East 2',
            'westus': 'US West',
            'westus2': 'US West 2',
            'westus3': 'US West 3',
            'centralus': 'US Central',
            'northcentralus': 'US North Central',
            'southcentralus': 'US South Central',
            'northeurope': 'North Europe',
            'westeurope': 'West Europe',
            'uksouth': 'UK South',
            'ukwest': 'UK West',
            'japaneast': 'Japan East',
            'japanwest': 'Japan West',
            'australiaeast': 'Australia East',
            'australiasoutheast': 'Australia Southeast',
            'southeastasia': 'Southeast Asia',
            'eastasia': 'East Asia',
        }
        logger.info("Azure Pricing Fetcher initialized (using Azure Retail Prices API)")
    
    def _get_region_name(self, region: str) -> str:
        """Convert region code to Azure region name"""
        return self.region_map.get(region.lower(), 'US East')
    
    def get_vm_pricing(self, vm_size: str, region: str = "eastus") -> Optional[float]:
        """Get Azure VM pricing directly from Azure - returns MONTHLY price"""
        cache_key = f"azure_vm_{vm_size}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            price = cached.get('price')
            logger.info(f"Cache hit for Azure VM {vm_size} in {region}: ${price:.2f}/month")
            return price
        
        if not self.enabled:
            logger.warning("Azure pricing fetcher is disabled")
            return None
        
        try:
            import requests
            
            url = "https://prices.azure.com/api/retail/prices"
            
            # Search for the VM SKU - note: API may return results for both "eastus" and regional names
            filter_str = f"armSkuName eq '{vm_size}'"
            
            params = {
                '$filter': filter_str,
                '$top': 200  # Get more results to search through regions
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                
                logger.debug(f"Azure API returned {len(items)} items for {vm_size}")
                
                # Find the best match in the requested region
                best_price = None
                found_region = False
                
                for item in items:
                    item_region = item.get('armRegionName', '').lower()
                    meter_name = item.get('meterName', '').lower()
                    
                    # Only match the requested region
                    if item_region != region.lower() and item_region != region:
                        continue
                    
                    found_region = True
                    
                    # Skip special pricing: Low Priority, Spot, Reserved Instances, vCore
                    if any(x in meter_name for x in ['low priority', 'spot', 'reserved', 'savings', 'vcore']):
                        continue
                    
                    # Look for on-demand Linux (standard pricing)
                    if 'windows' not in meter_name:
                        price = float(item.get('retailPrice', 0))
                        if price > 0:
                            best_price = price
                            logger.debug(f"✓ Found {vm_size} in {region}: {meter_name} = ${price}/hr")
                            break
                    # Fallback to Windows if no Linux found
                    elif not best_price:
                        price = float(item.get('retailPrice', 0))
                        if price > 0:
                            best_price = price
                            logger.debug(f"✓ Found {vm_size} in {region}: {meter_name} = ${price}/hr (Windows)")
                
                if best_price:
                    monthly_price = best_price * 730
                    self.cache.set(cache_key, {
                        'price': monthly_price,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'azure_retail_api',
                        'sku': vm_size
                    })
                    logger.info(f"✓ Azure VM pricing from API: {vm_size} in {region} = "
                              f"${best_price:.4f}/hr (${monthly_price:.2f}/month)")
                    return monthly_price
                else:
                    if found_region:
                        logger.warning(f"Found {vm_size} in {region} but all prices were filtered out (Spot/Low Priority)")
                    else:
                        logger.warning(f"No pricing found for {vm_size} in region {region}")
                    return None
            
            logger.warning(f"No pricing found for Azure VM {vm_size} in {region} via API")
            return None
        
        except Exception as e:
            logger.error(f"Error fetching Azure VM pricing for {vm_size}: {e}")
        
        return None
    
    def get_sql_db_pricing(self, tier: str, region: str = "eastus") -> Optional[float]:
        """Get Azure SQL Database pricing - returns MONTHLY price"""
        cache_key = f"azure_sql_{tier}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            price = cached.get('price')
            logger.info(f"Cache hit for Azure SQL {tier} in {region}: ${price:.2f}/month")
            return price
        
        if not self.enabled:
            return None
        
        try:
            import requests
            
            url = "https://prices.azure.com/api/retail/prices"
            
            # Map Azure SQL tiers to search terms
            tier_map = {
                'Basic': 'Basic',
                'Standard': 'Standard',
                'Premium': 'Premium',
                'S0': 'Standard',
                'S1': 'Standard',
                'S2': 'Standard',
                'S3': 'Standard',
                'S4': 'Standard',
                'S6': 'Standard',
                'S7': 'Standard',
                'P1': 'Premium',
                'P2': 'Premium',
                'P3': 'Premium',
                'P4': 'Premium',
                'P6': 'Premium',
                'P11': 'Premium',
                'P15': 'Premium',
            }
            
            search_tier = tier_map.get(tier, tier)
            
            # Note: SQL Database pricing is tricky - use search in productName instead
            filter_str = f"productName eq 'SQL Database {search_tier}' or contains(productName, 'SQL Database') and contains(skuName, '{search_tier}')"
            
            params = {
                '$filter': filter_str,
                '$top': 200
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                
                logger.debug(f"Azure SQL API returned {len(items)} items for {tier}")
                
                # Find best price for this region
                best_price = None
                for item in items:
                    item_region = item.get('armRegionName', '').lower()
                    
                    # Match the requested region
                    if item_region != region.lower() and item_region != region:
                        continue
                    
                    # Look for single database pricing (not elastic pool)
                    meter_name = item.get('meterName', '').lower()
                    if 'elastic' in meter_name or 'pool' in meter_name:
                        continue
                    
                    price = float(item.get('retailPrice', 0))
                    if price > 0:
                        best_price = price
                        logger.debug(f"✓ Found SQL {tier} in {region}: {meter_name} = ${price}/hr")
                        break
                
                if best_price:
                    monthly_price = best_price * 730
                    self.cache.set(cache_key, {
                        'price': monthly_price,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'azure_retail_api'
                    })
                    logger.info(f"✓ Azure SQL pricing from API: {tier} in {region} = "
                              f"${best_price:.4f}/hr (${monthly_price:.2f}/month)")
                    return monthly_price
        
        except Exception as e:
            logger.error(f"Error fetching Azure SQL pricing for {tier}: {e}")
        
        return None
    
    def get_storage_pricing(self, storage_type: str, region: str = "eastus") -> Optional[float]:
        """Get Azure Storage pricing - returns price per GB per month"""
        cache_key = f"azure_storage_{storage_type}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            price = cached.get('price')
            logger.info(f"Cache hit for Azure Storage {storage_type} in {region}: ${price:.4f}/GB/month")
            return price
        
        if not self.enabled:
            return None
        
        try:
            import requests
            region_name = self._get_region_name(region)
            
            url = "https://prices.azure.com/api/retail/prices"
            params = {
                '$filter': f"contains(productName, 'Storage') and contains(skuName, 'Standard') and contains(meterName, 'Data Stored')",
                '$top': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                
                for item in items:
                    if region_name in item.get('armRegionName', '') and 'GB' in item.get('unit', ''):
                        price_per_gb = float(item.get('retailPrice', 0))
                        if price_per_gb > 0:
                            monthly_price = price_per_gb
                            self.cache.set(cache_key, {
                                'price': monthly_price,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'azure_retail_api'
                            })
                            logger.info(f"Azure Storage pricing from API: {storage_type} in {region} = ${monthly_price:.4f}/GB/month")
                            return monthly_price
        
        except Exception as e:
            logger.error(f"Error fetching Azure Storage pricing for {storage_type}: {e}")
        
        return None
    
    def get_app_service_pricing(self, plan_tier: str, region: str = "eastus") -> Optional[float]:
        """Get Azure App Service pricing - returns MONTHLY price"""
        cache_key = f"azure_appservice_{plan_tier}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            price = cached.get('price')
            logger.info(f"Cache hit for Azure App Service {plan_tier} in {region}: ${price:.2f}/month")
            return price
        
        if not self.enabled:
            return None
        
        try:
            import requests
            region_name = self._get_region_name(region)
            
            url = "https://prices.azure.com/api/retail/prices"
            params = {
                '$filter': f"contains(productName, 'App Service') and contains(skuName, '{plan_tier}')",
                '$top': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                
                for item in items:
                    if region_name in item.get('armRegionName', ''):
                        hourly_price = float(item.get('retailPrice', 0))
                        if hourly_price > 0:
                            monthly_price = hourly_price * 730
                            self.cache.set(cache_key, {
                                'price': monthly_price,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'azure_retail_api'
                            })
                            logger.info(f"Azure App Service pricing from API: {plan_tier} in {region} = "
                                      f"${hourly_price:.4f}/hr (${monthly_price:.2f}/month)")
                            return monthly_price
        
        except Exception as e:
            logger.error(f"Error fetching Azure App Service pricing for {plan_tier}: {e}")
        
        return None
    
    def get_function_pricing(self, plan_type: str, region: str = "eastus") -> Optional[float]:
        """Get Azure Functions pricing - returns price for consumption plan"""
        cache_key = f"azure_function_{plan_type}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            price = cached.get('price')
            logger.info(f"Cache hit for Azure Functions {plan_type} in {region}: ${price:.4f}")
            return price
        
        if not self.enabled:
            return None
        
        try:
            import requests
            region_name = self._get_region_name(region)
            
            url = "https://prices.azure.com/api/retail/prices"
            params = {
                '$filter': f"contains(productName, 'Functions') and contains(skuName, 'Execution Units')",
                '$top': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                
                for item in items:
                    if region_name in item.get('armRegionName', ''):
                        price = float(item.get('retailPrice', 0))
                        if price >= 0:
                            self.cache.set(cache_key, {
                                'price': price,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'azure_retail_api'
                            })
                            logger.info(f"Azure Functions pricing from API: {plan_type} in {region} = ${price:.4f}")
                            return price
        
        except Exception as e:
            logger.error(f"Error fetching Azure Functions pricing: {e}")
        
        return None
    
    def get_application_gateway_pricing(self, gateway_type: str, region: str = "eastus") -> Optional[float]:
        """Get Azure Application Gateway pricing - returns MONTHLY price"""
        cache_key = f"azure_appgateway_{gateway_type}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            price = cached.get('price')
            logger.info(f"Cache hit for Azure Application Gateway in {region}: ${price:.2f}/month")
            return price
        
        if not self.enabled:
            return None
        
        try:
            import requests
            region_name = self._get_region_name(region)
            
            url = "https://prices.azure.com/api/retail/prices"
            params = {
                '$filter': f"contains(productName, 'Application Gateway')",
                '$top': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get('Items', [])
                
                for item in items:
                    if region_name in item.get('armRegionName', '') and 'Capacity Unit' in item.get('meterName', ''):
                        hourly_price = float(item.get('retailPrice', 0))
                        if hourly_price > 0:
                            monthly_price = hourly_price * 730
                            self.cache.set(cache_key, {
                                'price': monthly_price,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'azure_retail_api'
                            })
                            logger.info(f"Azure Application Gateway pricing from API: {region} = "
                                      f"${hourly_price:.4f}/hr (${monthly_price:.2f}/month)")
                            return monthly_price
        
        except Exception as e:
            logger.error(f"Error fetching Azure Application Gateway pricing: {e}")
        
        return None


class GCPPricingFetcher:
    """Fetch real-time pricing from GCP Pricing API"""
    
    def __init__(self):
        self.enabled = GCP_CONFIG["enabled"] and billing_v1 is not None
        self.cache = PricingCache()
        if self.enabled and GCP_CONFIG.get("credentials_path"):
            try:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CONFIG["credentials_path"]
                logger.info("GCP Pricing API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize GCP Pricing client: {e}")
                self.enabled = False
    
    def get_compute_instance_pricing(self, machine_type: str, region: str = "us-central1") -> Optional[float]:
        """Get GCP Compute Engine pricing"""
        cache_key = f"gcp_compute_{machine_type}_{region}"
        
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached.get('price')
        
        if not self.enabled:
            return None
        
        try:
            import requests
            # Using GCP public pricing API
            url = f"https://www.googleapis.com/compute/v1/projects/{GCP_CONFIG['project_id']}/global/machineTypes/{machine_type}"
            
            # For pricing, we need to use the pricing data from public sources
            # GCP doesn't have a direct real-time pricing API like AWS
            # Alternative: Use Google Cloud Pricing Calculator API or public pricing data
            logger.warning("GCP real-time pricing requires setup of Pricing Calculator integration")
        
        except Exception as e:
            logger.error(f"Error fetching GCP pricing for {machine_type}: {e}")
        
        return None


class RealTimePricingFetcher:
    """Unified real-time pricing fetcher"""
    
    def __init__(self):
        self.aws = AWSPricingFetcher()
        self.azure = AzurePricingFetcher()
        self.gcp = GCPPricingFetcher()
        self.fallback_enabled = USE_FALLBACK_PRICING
    
    def get_pricing(self, provider: str, resource_type: str, 
                   instance_type: str, **kwargs) -> Dict:
        """
        Get pricing for a resource
        Returns: {'price': float, 'source': 'api|cache|fallback'}
        """
        try:
            if provider.lower() == 'aws':
                if resource_type.lower() == 'ec2':
                    price = self.aws.get_ec2_pricing(instance_type)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 'rds':
                    price = self.aws.get_rds_pricing(instance_type)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 's3':
                    price = self.aws.get_s3_pricing()
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
            
            elif provider.lower() == 'azure':
                region = kwargs.get('region', 'eastus')
                if resource_type.lower() == 'vm':
                    price = self.azure.get_vm_pricing(instance_type, region)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 'sql':
                    price = self.azure.get_sql_db_pricing(instance_type, region)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 'storage':
                    price = self.azure.get_storage_pricing(instance_type, region)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 'app_service':
                    price = self.azure.get_app_service_pricing(instance_type, region)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 'function':
                    price = self.azure.get_function_pricing(instance_type, region)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
                elif resource_type.lower() == 'application_gateway':
                    price = self.azure.get_application_gateway_pricing(instance_type, region)
                    if price:
                        return {'price': price, 'source': 'api', 'currency': DEFAULT_CURRENCY}
            
            elif provider.lower() == 'gcp':
                logger.warning(f"GCP real-time pricing not yet fully implemented")
        
        except Exception as e:
            logger.error(f"Error getting pricing: {e}")
        
        # If API fails and fallback is enabled, return None (will use fallback)
        return None


# Global instance
pricing_fetcher = RealTimePricingFetcher()
