from fastapi import APIRouter
from ..api.v1.health import router as health_router
from ..api.v1.infra import router as infra_router
from ..api.v1.diagram import router as diagram_router
from ..api.v1.pricing import router as pricing_router
from ..api.v1.pricing_enhanced import router as pricing_enhanced_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(infra_router, prefix="/infra", tags=["Infra"])
api_router.include_router(diagram_router, prefix="/diagram", tags=["Diagram"])
api_router.include_router(pricing_router, prefix="/pricing", tags=["Pricing"])
api_router.include_router(pricing_enhanced_router, prefix="/pricing", tags=["Pricing Enhanced"])
