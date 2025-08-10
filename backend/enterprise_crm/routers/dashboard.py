"""
Dashboard API Routes
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from ..schemas.common import StandardResponse
from ..schemas.dashboard import DashboardConfigResponse, WidgetConfigResponse, DashboardStatsResponse
from ..dependencies.auth import get_current_user
from ..services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/", response_model=StandardResponse)
async def get_user_dashboard(
    department: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """Get user's dashboard configuration and data"""
    try:
        dashboard_data = await dashboard_service.get_user_dashboard(
            user_id=current_user["id"],
            department=department
        )
        return StandardResponse(
            status=True,
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to retrieve dashboard data",
            error={"detail": str(e)}
        )

@router.get("/stats", response_model=StandardResponse)
async def get_dashboard_stats(
    department: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """Get department-specific dashboard statistics"""
    try:
        stats = await dashboard_service.get_dashboard_stats(
            user_id=current_user["id"],
            department=department or current_user.get("department")
        )
        return StandardResponse(
            status=True,
            message="Dashboard statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to retrieve dashboard statistics",
            error={"detail": str(e)}
        )

@router.get("/sales", response_model=StandardResponse)
async def get_sales_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """Get sales-specific dashboard data"""
    try:
        sales_data = await dashboard_service.get_sales_dashboard(
            user_id=current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Sales dashboard data retrieved successfully",
            data={
                "total_leads": sales_data["total_leads"],
                "total_opportunities": sales_data["total_opportunities"], 
                "revenue_generated": sales_data["revenue_generated"],
                "assignment_overview": sales_data["assignment_overview"],
                "approvals_pending": sales_data["approvals_pending"]
            }
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to retrieve sales dashboard data",
            error={"detail": str(e)}
        )

@router.get("/presales", response_model=StandardResponse)
async def get_presales_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """Get presales-specific dashboard data"""
    try:
        presales_data = await dashboard_service.get_presales_dashboard(
            user_id=current_user["id"]
        )
        return StandardResponse(
            status=True,
            message="Presales dashboard data retrieved successfully",
            data={
                "solution_team_workload": presales_data["solution_team_workload"],
                "approvals_pending": presales_data["approvals_pending"],
                "active_projects": presales_data["active_projects"]
            }
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to retrieve presales dashboard data",
            error={"detail": str(e)}
        )

@router.get("/product", response_model=StandardResponse)
async def get_product_dashboard(
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """Get product-specific dashboard data"""
    try:
        product_data = await dashboard_service.get_product_dashboard()
        return StandardResponse(
            status=True,
            message="Product dashboard data retrieved successfully", 
            data={
                "top_selling_products": product_data["top_selling_products"],
                "sales_by_category": product_data["sales_by_category"],
                "performance_trends": product_data["performance_trends"]
            }
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to retrieve product dashboard data",
            error={"detail": str(e)}
        )

@router.post("/widget/refresh", response_model=StandardResponse)
async def refresh_widget(
    widget_id: int,
    current_user: dict = Depends(get_current_user),
    dashboard_service: DashboardService = Depends()
):
    """Refresh specific dashboard widget"""
    try:
        widget_data = await dashboard_service.refresh_widget(widget_id)
        return StandardResponse(
            status=True,
            message="Widget refreshed successfully",
            data=widget_data
        )
    except Exception as e:
        return StandardResponse(
            status=False,
            message="Failed to refresh widget",
            error={"detail": str(e)}
        )