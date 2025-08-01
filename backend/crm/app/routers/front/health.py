"""
Health check endpoints
"""
from fastapi import APIRouter
from ...schemas.auth import StandardResponse

router = APIRouter(tags=["health"])

@router.get("/", response_model=StandardResponse)
async def root():
    """Root health check endpoint"""
    return StandardResponse(
        status=True,
        message="CRM Authentication API is running",
        data=None,
        error=None
    )

@router.get("/api/", response_model=StandardResponse)
async def api_root():
    """API health check endpoint"""
    return StandardResponse(
        status=True,
        message="CRM Authentication API is running",
        data=None,
        error=None
    )

@router.get("/health", response_model=StandardResponse)
async def health_check():
    """Detailed health check endpoint"""
    return StandardResponse(
        status=True,
        message="CRM API is healthy",
        data={"service": "crm-api", "version": "1.0.0"},
        error=None
    )