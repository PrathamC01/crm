"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, Request
from ...schemas.auth import StandardResponse, UserResponse
from ...dependencies.auth import get_current_user, get_auth_service
from ...services.auth_service import AuthService

router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get("/dashboard", response_model=StandardResponse)
async def get_dashboard(
    request: Request,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user dashboard information"""
    try:
        user_info = await auth_service.get_user_info(current_user["id"], request)
        
        return StandardResponse(
            status=True,
            message="Dashboard data retrieved successfully",
            data={
                "id": user_info.id,
                "name": user_info.name,
                "email": user_info.email,
                "username": user_info.username,
                "role": user_info.role,
                "department": user_info.department,
                "is_active": user_info.is_active
            }
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to retrieve dashboard data",
            error=str(e)
        )