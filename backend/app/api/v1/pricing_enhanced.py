"""
Enhanced Pricing API Routes
Provides detailed specifications and recommendations
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from enhanced_pricing_response import EnhancedPricingResponse
    ENHANCED_PRICING_AVAILABLE = True
except ImportError:
    ENHANCED_PRICING_AVAILABLE = False

router = APIRouter()

class ResourceDetailsRequest(BaseModel):
    """Request model for resource details"""
    provider: str  # 'azure', 'aws', 'gcp'
    instance_type: str  # VM size
    region: str = 'eastus'
    quantity: int = 1

class VMComparisonRequest(BaseModel):
    """Request model for VM comparison"""
    provider: str = 'azure'
    region: str = 'eastus'
    series: Optional[str] = None  # 'D', 'E', 'B', etc.

class VMRecommendationRequest(BaseModel):
    """Request model for VM recommendation"""
    budget: float
    workload_type: str  # 'dev', 'test', 'web', 'app', 'compute', 'memory', 'hpc'
    region: str = 'eastus'

@router.post("/resource-details")
def get_resource_details(request: ResourceDetailsRequest) -> dict:
    """
    Get detailed specifications and pricing for a specific resource
    
    Includes:
    - Current pricing (hourly, monthly, annual)
    - VM specifications (vCPU, RAM, Disk, Network)
    - Performance metrics (cost per vCPU, cost per RAM GB)
    - Use case recommendations
    """
    if not ENHANCED_PRICING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced pricing service not available")
    
    try:
        details = EnhancedPricingResponse.get_resource_details(
            provider=request.provider,
            resource_type=f'{request.provider}_virtual_machine',
            instance_type=request.instance_type,
            region=request.region,
            quantity=request.quantity
        )
        
        return {
            'success': True,
            'data': details
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource details: {str(e)}"
        )

@router.post("/vm-comparison")
def compare_vm_sizes(request: VMComparisonRequest) -> dict:
    """
    Compare pricing and specs of different VM sizes in a series
    
    Returns:
    - List of VMs sorted by cost
    - Specifications (vCPU, RAM, Disk)
    - Cost metrics (cost per vCPU, cost per RAM)
    - Best value recommendations
    """
    if not ENHANCED_PRICING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced pricing service not available")
    
    try:
        comparison = EnhancedPricingResponse.compare_vm_sizes(
            provider=request.provider,
            region=request.region,
            series=request.series
        )
        
        if not comparison:
            raise HTTPException(
                status_code=400,
                detail=f"No VMs found for series {request.series}"
            )
        
        # Add analysis
        min_cost = min(vm['monthly_cost'] for vm in comparison)
        max_cost = max(vm['monthly_cost'] for vm in comparison)
        
        analysis = {
            'series': request.series or 'All',
            'region': request.region,
            'count': len(comparison),
            'price_range': {
                'minimum': f'${min_cost:.2f}/mo',
                'maximum': f'${max_cost:.2f}/mo'
            },
            'best_value': comparison[0]['size'] if comparison else None,
            'vms': comparison
        }
        
        return {
            'success': True,
            'data': analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare VMs: {str(e)}"
        )

@router.post("/vm-recommendation")
def recommend_vm(request: VMRecommendationRequest) -> dict:
    """
    Get VM recommendation based on budget and workload type
    
    Workload Types:
    - 'dev': Development/Test environments (B-series preferred)
    - 'test': Testing environments (B2s, B2ms, D-series)
    - 'web': Web applications (D2/D4 series)
    - 'app': Application servers (D4/D8 series)
    - 'compute': Compute-intensive (C-series)
    - 'memory': Memory-intensive (E-series)
    - 'hpc': High-performance computing (Large E-series)
    """
    if not ENHANCED_PRICING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced pricing service not available")
    
    try:
        recommendation = EnhancedPricingResponse.get_vm_recommendation(
            budget=request.budget,
            workload_type=request.workload_type,
            region=request.region
        )
        
        return {
            'success': 'recommended_vm' in recommendation,
            'data': recommendation
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendation: {str(e)}"
        )

@router.get("/vm-series-list")
def get_vm_series(series: Optional[str] = Query(None)) -> dict:
    """
    Get list of available VM sizes, optionally filtered by series
    
    Query Parameters:
    - series: Filter by series ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    """
    if not ENHANCED_PRICING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced pricing service not available")
    
    try:
        from vm_specifications import get_all_vm_sizes, get_series_info
        
        if series:
            vms = get_series_info(series.upper())
            return {
                'success': True,
                'series': series.upper(),
                'count': len(vms),
                'data': vms
            }
        else:
            all_vms = get_all_vm_sizes()
            return {
                'success': True,
                'total_vms': len(all_vms),
                'series_available': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
                'data': all_vms
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get VM list: {str(e)}"
        )

@router.get("/regions-list")
def get_available_regions() -> dict:
    """
    Get list of supported Azure regions
    """
    regions = {
        'US': ['eastus', 'westus', 'centralus', 'northcentralus', 'southcentralus'],
        'Europe': ['northeurope', 'westeurope', 'uksouth', 'ukwest'],
        'Asia': ['southeastasia', 'eastasia', 'japaneast', 'japanwest', 'australiaeast', 'australiasoutheast', 'southindia', 'centralindia', 'westindia', 'westasia'],
        'Americas': ['canadaeast', 'canadacentral', 'brazilsouth']
    }
    
    return {
        'success': True,
        'total_regions': sum(len(v) for v in regions.values()),
        'data': regions
    }

@router.get("/pricing-status")
def get_pricing_status() -> dict:
    """
    Get current status of pricing integration
    """
    return {
        'success': True,
        'services': {
            'enhanced_pricing': {
                'available': ENHANCED_PRICING_AVAILABLE,
                'features': [
                    'Resource details with specifications',
                    'VM comparison and analysis',
                    'Budget-based recommendations',
                    'Cost per vCPU/RAM metrics',
                    'Workload-optimized suggestions'
                ] if ENHANCED_PRICING_AVAILABLE else []
            },
            'real_time_pricing': {
                'available': True,
                'description': 'Azure Retail Prices API'
            },
            'vm_specifications': {
                'available': True,
                'total_vm_sizes': 43,
                'series_supported': ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            }
        }
    }
