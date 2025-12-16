"""
API routes for pricing calculations
Supports both real-time cloud APIs and static pricing fallback
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pricing_calculator import calculate_terraform_pricing, CloudPricingCalculator

# Try to import real-time pricing status
try:
    from real_time_pricing_fetcher import pricing_fetcher
    REAL_TIME_PRICING_AVAILABLE = True
except ImportError:
    REAL_TIME_PRICING_AVAILABLE = False

# Try to import enhanced pricing response
try:
    from enhanced_pricing_response import EnhancedPricingResponse
    ENHANCED_PRICING_AVAILABLE = True
except ImportError:
    ENHANCED_PRICING_AVAILABLE = False
    print("Warning: Enhanced pricing response not available")

router = APIRouter()

class PricingRequest(BaseModel):
    """Request model for pricing calculation"""
    terraform_code: str
    include_breakdown: bool = True
    include_comparison: bool = True

class ResourcePricing(BaseModel):
    """Pricing for a single resource"""
    name: str
    type: str
    cost: float
    description: str

class PricingResponse(BaseModel):
    """Response model for pricing calculation"""
    success: bool
    total_costs: dict
    breakdown: dict
    comparison: dict
    monthly_estimate: dict

@router.post("/calculate-pricing")
def calculate_pricing(request: PricingRequest) -> PricingResponse:
    """
    Calculate and compare cloud infrastructure pricing across AWS, Azure, and GCP
    
    Analyzes Terraform code and provides:
    - Monthly and annual cost estimates per provider
    - Detailed cost breakdown by resource
    - Provider cost comparison and savings potential
    
    Note: Uses real-time cloud APIs if available, falls back to static pricing
    """
    if not request.terraform_code or not request.terraform_code.strip():
        raise HTTPException(status_code=400, detail="Terraform code cannot be empty")
    
    try:
        results = calculate_terraform_pricing(request.terraform_code)
        
        return PricingResponse(
            success=True,
            total_costs=results['total_costs'],
            breakdown=results['breakdown'],
            comparison=results['comparison'],
            monthly_estimate={
                'aws': results['total_costs'].get('aws', 0),
                'azure': results['total_costs'].get('azure', 0),
                'gcp': results['total_costs'].get('gcp', 0),
                'average': sum(results['total_costs'].values()) / len(results['total_costs'])
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate pricing: {str(e)}"
        )

@router.get("/pricing-formats")
def get_pricing_info() -> dict:
    """Get pricing calculation information and supported cloud providers"""
    return {
        "pricing_source": "real-time APIs with static fallback" if REAL_TIME_PRICING_AVAILABLE else "static pricing",
        "real_time_apis_available": {
            "aws": True if REAL_TIME_PRICING_AVAILABLE else False,
            "azure": True if REAL_TIME_PRICING_AVAILABLE else False,
            "gcp": False,  # GCP pricing API requires additional setup
        },
        "providers": [
            {
                "name": "AWS",
                "id": "aws",
                "description": "Amazon Web Services",
                "region": "US East 1 (N. Virginia)",
                "real_time_pricing": True if REAL_TIME_PRICING_AVAILABLE else False,
                "supported_services": [
                    "EC2", "RDS", "S3", "DynamoDB", "Lambda", 
                    "ALB/NLB", "NAT Gateway", "CloudFront"
                ]
            },
            {
                "name": "Azure",
                "id": "azure",
                "description": "Microsoft Azure",
                "region": "East US",
                "real_time_pricing": True if REAL_TIME_PRICING_AVAILABLE else False,
                "supported_services": [
                    "Virtual Machines", "SQL Database", "Storage Account",
                    "App Service", "Functions", "Application Gateway", "VNet"
                ]
            },
            {
                "name": "GCP",
                "id": "gcp",
                "description": "Google Cloud Platform",
                "region": "US Multi-region",
                "real_time_pricing": False,
                "supported_services": [
                    "Compute Engine", "Cloud SQL", "Cloud Storage",
                    "Firestore", "Cloud Functions", "Cloud Load Balancing"
                ]
            }
        ],
        "features": [
            "Multi-cloud cost comparison",
            "Real-time pricing API integration (AWS, Azure)",
            "Static pricing fallback",
            "Automatic pricing caching",
            "Monthly and annual estimates",
            "Resource-level pricing breakdown",
            "Savings analysis and recommendations",
            "Instance type pricing",
            "Storage and data transfer costs"
        ],
        "limitations": [
            "Real-time APIs require cloud credentials setup",
            "GCP requires manual setup for pricing data",
            "Prices updated based on provider public pricing (subject to change)",
            "Does not include discounts (reserved instances, spot pricing)",
            "Data transfer costs between regions not included"
        ],
        "setup_instructions": {
            "aws": "Configure AWS credentials: export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY",
            "azure": "Run: az login or set AZURE_SUBSCRIPTION_ID",
            "gcp": "Download service account key and set GOOGLE_APPLICATION_CREDENTIALS"
        }
    }

@router.post("/compare-pricing")
def compare_multi_provider_pricing(request: PricingRequest) -> dict:
    """
    Detailed cost comparison across all three cloud providers
    """
    if not request.terraform_code or not request.terraform_code.strip():
        raise HTTPException(status_code=400, detail="Terraform code cannot be empty")
    
    try:
        results = calculate_terraform_pricing(request.terraform_code)
        
        costs = results['total_costs']
        comparison = results['comparison']
        
        # Generate detailed comparison matrix
        providers = ['aws', 'azure', 'gcp']
        sorted_by_cost = sorted(costs.items(), key=lambda x: x[1])
        
        comparison_matrix = {
            "providers_ranked": [
                {
                    "rank": i + 1,
                    "provider": provider.upper(),
                    "monthly_cost": f"${cost:.2f}",
                    "annual_cost": f"${cost * 12:.2f}",
                    "percentage": f"{(cost / sum(costs.values()) * 100):.1f}%"
                }
                for i, (provider, cost) in enumerate(sorted_by_cost)
            ],
            "cost_breakdown": results['breakdown'],
            "savings_analysis": comparison.get('savings_potential', {}),
            "recommendation": {
                "cheapest": comparison['cheapest_provider'].upper(),
                "reason": f"Lowest monthly cost at ${costs[comparison['cheapest_provider']]:.2f}",
                "monthly_budget": costs[comparison['cheapest_provider']],
                "annual_budget": costs[comparison['cheapest_provider']] * 12
            }
        }
        
        return {
            "success": True,
            "comparison": comparison_matrix,
            "metadata": {
                "calculation_date": "2025-12-03",
                "region": "US (primary)",
                "currency": "USD"
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare pricing: {str(e)}"
        )

