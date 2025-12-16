"""
Enhanced Pricing Response with Specifications
Provides detailed cost analysis with VM specifications
"""

from typing import Dict, Any, Optional
from pricing_calculator import CloudPricingCalculator
from vm_specifications import get_vm_specifications, get_all_vm_sizes

class EnhancedPricingResponse:
    """Generate enhanced pricing responses with detailed specifications"""
    
    @staticmethod
    def get_resource_details(provider: str, resource_type: str, 
                            instance_type: str, region: str, 
                            quantity: int = 1) -> Dict[str, Any]:
        """
        Get comprehensive resource details including cost and specifications
        
        Args:
            provider: 'azure', 'aws', 'gcp'
            resource_type: 'azurerm_virtual_machine', 'aws_instance', etc.
            instance_type: VM size (e.g., 'Standard_D2s_v3')
            region: Region name
            quantity: Number of instances
            
        Returns:
            Dictionary with pricing, specifications, and metadata
        """
        calc = CloudPricingCalculator()
        
        # Build resource dict for calculator
        resource = {
            'type': resource_type,
            'provider': provider,
            'instance_type': instance_type,
            'quantity': quantity,
            'config': {'region': region}
        }
        
        # Get cost
        cost, description = calc.calculate_resource_cost(resource)
        monthly_cost = cost
        annual_cost = cost * 12
        
        # Get VM specifications if available
        specs = get_vm_specifications(instance_type) if provider == 'azure' else {}
        
        # Build normalized names
        normalized_vm = calc.normalize_azure_vm_size(instance_type) if provider == 'azure' else instance_type
        normalized_region = calc.normalize_azure_region(region) if provider == 'azure' else region
        
        return {
            'provider': provider,
            'resource_type': resource_type,
            'instance_type': instance_type,
            'normalized_type': normalized_vm,
            'region': region,
            'normalized_region': normalized_region,
            'quantity': quantity,
            'pricing': {
                'unit_cost_monthly': monthly_cost / quantity if quantity > 0 else 0,
                'total_cost_monthly': monthly_cost,
                'total_cost_annual': annual_cost,
                'currency': 'USD',
                'source': description
            },
            'specifications': {
                'vCPU': specs.get('vCPU', 0),
                'RAM_GB': specs.get('RAM_GB', 0),
                'Disk_GB': specs.get('Disk_GB', 0),
                'Network_Mbps': specs.get('Network_Mbps', 0),
                'Series': specs.get('Series', ''),
                'Use_Case': specs.get('Use_Case', '')
            },
            'performance': {
                'cost_per_vcpu_monthly': (monthly_cost / specs.get('vCPU', 1)) if specs.get('vCPU', 0) > 0 else 0,
                'cost_per_gb_ram_monthly': (monthly_cost / specs.get('RAM_GB', 1)) if specs.get('RAM_GB', 0) > 0 else 0,
                'total_compute_units': specs.get('vCPU', 0) + specs.get('RAM_GB', 0)
            }
        }
    
    @staticmethod
    def compare_vm_sizes(provider: str, region: str, series: Optional[str] = None) -> list:
        """
        Compare costs of different VM sizes in a series
        
        Args:
            provider: 'azure', 'aws', 'gcp'
            region: Region name
            series: VM series ('D', 'E', 'B', etc.) - optional
            
        Returns:
            List of VMs with costs and specs, sorted by cost
        """
        vm_sizes = get_all_vm_sizes(series) if series else []
        if not vm_sizes:
            return []
        
        comparison = []
        for vm_size in vm_sizes:
            details = EnhancedPricingResponse.get_resource_details(
                provider=provider,
                resource_type='azurerm_virtual_machine',
                instance_type=vm_size,
                region=region,
                quantity=1
            )
            comparison.append({
                'size': vm_size,
                'monthly_cost': details['pricing']['total_cost_monthly'],
                'vCPU': details['specifications']['vCPU'],
                'RAM_GB': details['specifications']['RAM_GB'],
                'cost_per_vcpu': details['performance']['cost_per_vcpu_monthly'],
                'cost_per_ram_gb': details['performance']['cost_per_gb_ram_monthly']
            })
        
        # Sort by monthly cost
        return sorted(comparison, key=lambda x: x['monthly_cost'])
    
    @staticmethod
    def get_vm_recommendation(budget: float, workload_type: str, 
                             region: str = 'eastus') -> Dict[str, Any]:
        """
        Get VM recommendation based on budget and workload
        
        Args:
            budget: Maximum monthly budget in USD
            workload_type: 'dev', 'test', 'web', 'app', 'compute', 'memory', 'hpc'
            region: Azure region
            
        Returns:
            Recommended VM size with details
        """
        workload_mapping = {
            'dev': ['B1s', 'B1ms', 'B2s'],
            'test': ['B2s', 'B2ms', 'Standard_D2s_v3'],
            'web': ['Standard_D2s_v3', 'Standard_D4s_v3'],
            'app': ['Standard_D4s_v3', 'Standard_D8s_v3'],
            'compute': ['Standard_C4s_v3', 'Standard_C8s_v3'],
            'memory': ['Standard_E4s_v3', 'Standard_E8s_v3'],
            'hpc': ['Standard_E16s_v3', 'Standard_E32s_v3']
        }
        
        candidates = workload_mapping.get(workload_type, ['Standard_D2s_v3'])
        
        # Find best match within budget
        best_vm = None
        best_details = None
        max_cost = 0
        
        for vm_size in candidates:
            details = EnhancedPricingResponse.get_resource_details(
                provider='azure',
                resource_type='azurerm_virtual_machine',
                instance_type=vm_size,
                region=region,
                quantity=1
            )
            
            monthly_cost = details['pricing']['total_cost_monthly']
            if monthly_cost <= budget and monthly_cost > max_cost:
                best_vm = vm_size
                best_details = details
                max_cost = monthly_cost
        
        if best_vm:
            return {
                'recommended_vm': best_vm,
                'details': best_details,
                'budget_remaining': budget - max_cost
            }
        
        return {
            'error': f'No VM found within ${budget} budget for {workload_type} workload',
            'suggestions': [
                f'Increase budget to at least ${max_cost:.2f}',
                f'Consider serverless options',
                f'Check available VMs in {workload_type} category'
            ]
        }

if __name__ == '__main__':
    # Test the enhanced response
    print("✓ Enhanced Pricing Response Module Loaded\n")
    
    # Example 1: Get D2s_v3 details
    print("[Example 1] Standard_D2s_v3 in eastus:")
    details = EnhancedPricingResponse.get_resource_details(
        provider='azure',
        resource_type='azurerm_virtual_machine',
        instance_type='Standard_D2s_v3',
        region='eastus',
        quantity=1
    )
    print(f"  vCPU: {details['specifications']['vCPU']}")
    print(f"  RAM: {details['specifications']['RAM_GB']}GB")
    print(f"  Monthly: ${details['pricing']['total_cost_monthly']:.2f}")
    print(f"  Cost/vCPU: ${details['performance']['cost_per_vcpu_monthly']:.2f}\n")
    
    # Example 2: Compare D-series
    print("[Example 2] D-Series Comparison in eastus:")
    comparison = EnhancedPricingResponse.compare_vm_sizes('azure', 'eastus', 'D')
    for vm in comparison[:3]:
        print(f"  {vm['size']:20} ${vm['monthly_cost']:8.2f}/mo  {vm['vCPU']}vCPU  {vm['RAM_GB']}GB RAM")
    print()
    
    # Example 3: VM recommendation
    print("[Example 3] Recommend VM for $200/mo web workload:")
    rec = EnhancedPricingResponse.get_vm_recommendation(200, 'web', 'eastus')
    if 'recommended_vm' in rec:
        print(f"  VM: {rec['recommended_vm']}")
        print(f"  Cost: ${rec['details']['pricing']['total_cost_monthly']:.2f}/mo")
        print(f"  Budget Remaining: ${rec['budget_remaining']:.2f}")
    else:
        print(f"  {rec['error']}")
