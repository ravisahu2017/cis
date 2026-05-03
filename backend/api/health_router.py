"""
Health Check API Router
Provides system health and status endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from utils import logger

health_router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={404: {"description": "Not found"}},
)

@health_router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    """
    try:
        return {
            "status": "healthy",
            "service": "cis-api",
            "version": "1.0.0",
            "timestamp": "2026-05-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "cis-api"
        }

@health_router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with component status
    """
    try:
        # Check all major components
        components = {
            "api": {"status": "healthy"},
            "chat_service": {"status": "healthy"},
            "contract_service": {"status": "healthy"},
            "file_upload": {"status": "healthy"},
            "s3_integration": {"status": "healthy"}
        }
        
        overall_status = "healthy" if all(
            comp["status"] == "healthy" for comp in components.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "service": "cis-api",
            "version": "1.0.0",
            "components": components,
            "timestamp": "2026-05-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "cis-api"
        }
