"""
Dashboard Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from .common import BaseResponseSchema

# Dashboard Configuration Schemas
class DashboardConfigResponse(BaseResponseSchema):
    dashboard_name: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    is_default: bool
    layout_config: Optional[Dict[str, Any]] = None

class WidgetConfigResponse(BaseResponseSchema):
    dashboard_id: int
    widget_name: str
    widget_type: str
    position_x: int
    position_y: int
    width: int
    height: int
    data_source: str
    config: Optional[Dict[str, Any]] = None
    refresh_interval: int

# Dashboard Data Response Schemas
class KPICardData(BaseModel):
    title: str
    value: str
    change: Optional[str] = None
    trend: Optional[str] = None  # up, down, stable
    color: Optional[str] = None

class ChartData(BaseModel):
    type: str  # bar, line, pie, doughnut
    labels: List[str]
    datasets: List[Dict[str, Any]]

class TableData(BaseModel):
    headers: List[str]
    rows: List[List[Any]]

class ApprovalItem(BaseModel):
    id: int
    type: str  # price_list, quotation, discount, etc.
    title: str
    submitted_by: str
    submitted_date: datetime
    priority: str
    url: Optional[str] = None

class ActivityItem(BaseModel):
    id: int
    type: str  # lead_created, opportunity_won, etc.
    title: str
    description: str
    user: str
    timestamp: datetime
    url: Optional[str] = None

# Department-specific Dashboard Schemas
class SalesDashboardData(BaseModel):
    total_leads: KPICardData
    total_opportunities: KPICardData
    revenue_generated: KPICardData
    conversion_rate: KPICardData
    assignment_overview: ChartData
    approvals_pending: List[ApprovalItem]
    pipeline_chart: ChartData
    recent_activities: List[ActivityItem]

class PresalesDashboardData(BaseModel):
    active_projects: KPICardData
    pending_approvals: KPICardData
    team_workload: ChartData
    solution_approvals: List[ApprovalItem]
    project_timeline: ChartData
    resource_utilization: ChartData

class ProductDashboardData(BaseModel):
    top_selling_products: ChartData
    sales_by_category: ChartData
    performance_trends: ChartData
    inventory_alerts: List[Dict[str, Any]]
    pricing_approvals: List[ApprovalItem]
    product_performance: TableData

class DashboardStatsResponse(BaseModel):
    department: Optional[str] = None
    kpi_cards: List[KPICardData]
    charts: List[ChartData]
    tables: List[TableData]
    approvals_pending: List[ApprovalItem]
    recent_activities: List[ActivityItem]
    last_updated: datetime