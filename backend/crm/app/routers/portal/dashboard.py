"""
Dashboard API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from ...schemas.auth import StandardResponse
from ...services.dashboard_service import get_dashboard_service, DashboardService
from ...dependencies.database import get_postgres_db
from ...dependencies.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/sales", response_model=StandardResponse)
async def get_sales_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get sales dashboard data"""
    try:
        data = await dashboard_service.get_sales_dashboard_data(
            user_id=current_user["id"],
            department_id=current_user.get("department_id")
        )
        return StandardResponse(
            status=True,
            message="Sales dashboard data retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/presales", response_model=StandardResponse)
async def get_presales_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get presales dashboard data"""
    try:
        data = await dashboard_service.get_presales_dashboard_data(
            user_id=current_user["id"],
            department_id=current_user.get("department_id")
        )
        return StandardResponse(
            status=True,
            message="Presales dashboard data retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product", response_model=StandardResponse)
async def get_product_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get product dashboard data"""
    try:
        data = await dashboard_service.get_product_dashboard_data(
            user_id=current_user["id"],
            department_id=current_user.get("department_id")
        )
        return StandardResponse(
            status=True,
            message="Product dashboard data retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview", response_model=StandardResponse)
async def get_default_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get default dashboard overview"""
    try:
        data = await dashboard_service.get_default_dashboard_data(
            user_id=current_user["id"],
            department_id=current_user.get("department_id")
        )
        return StandardResponse(
            status=True,
            message="Dashboard overview retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=StandardResponse)
async def get_dashboard_metrics(
    dashboard_type: str = "default",
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get dashboard metrics based on type"""
    try:
        if dashboard_type == "sales":
            data = await dashboard_service.get_sales_dashboard_data(
                user_id=current_user["id"],
                department_id=current_user.get("department_id")
            )
        elif dashboard_type == "presales":
            data = await dashboard_service.get_presales_dashboard_data(
                user_id=current_user["id"],
                department_id=current_user.get("department_id")
            )
        elif dashboard_type == "product":
            data = await dashboard_service.get_product_dashboard_data(
                user_id=current_user["id"],
                department_id=current_user.get("department_id")
            )
        else:
            data = await dashboard_service.get_default_dashboard_data(
                user_id=current_user["id"],
                department_id=current_user.get("department_id")
            )
        
        return StandardResponse(
            status=True,
            message=f"{dashboard_type.title()} dashboard metrics retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))