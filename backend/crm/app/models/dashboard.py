"""
Dashboard Module Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Float, JSON, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from datetime import datetime

class DashboardTypeEnum(str, enum.Enum):
    DEFAULT = "default"
    SALES = "sales"
    PRESALES = "presales" 
    PRODUCT = "product"

class WidgetTypeEnum(str, enum.Enum):
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    LIST = "list"
    PROGRESS = "progress"

class ChartTypeEnum(str, enum.Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"

class DashboardConfig(BaseModel):
    """Dashboard configuration for different departments"""
    __tablename__ = "dashboard_configs"
    
    dashboard_name = Column(String(200), nullable=False)
    dashboard_type = Column(SQLEnum(DashboardTypeEnum), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # For personalized dashboards
    layout_config = Column(JSON, nullable=True, comment="Grid layout configuration")
    is_default = Column(Boolean, default=False)
    
    # Relationships
    widgets = relationship("DashboardWidget", back_populates="dashboard")
    department = relationship("Department", foreign_keys=[department_id])

class DashboardWidget(BaseModel):
    """Individual widgets on dashboard"""
    __tablename__ = "dashboard_widgets"
    
    dashboard_id = Column(Integer, ForeignKey('dashboard_configs.id'), nullable=False)
    widget_name = Column(String(200), nullable=False)
    widget_type = Column(SQLEnum(WidgetTypeEnum), nullable=False)
    chart_type = Column(SQLEnum(ChartTypeEnum), nullable=True)
    
    # Widget configuration
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    data_source = Column(String(200), nullable=False, comment="API endpoint or query identifier")
    refresh_interval = Column(Integer, default=300, comment="Refresh interval in seconds")
    
    # Layout properties
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    
    # Widget settings
    widget_config = Column(JSON, nullable=True, comment="Widget-specific configuration")
    filters = Column(JSON, nullable=True, comment="Default filters for widget")
    
    # Relationships
    dashboard = relationship("DashboardConfig", back_populates="widgets")

class DashboardMetric(BaseModel):
    """Pre-calculated metrics for dashboard performance"""
    __tablename__ = "dashboard_metrics"
    
    metric_name = Column(String(200), nullable=False)
    metric_key = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_data = Column(JSON, nullable=True, comment="Additional metric data")
    
    # Metadata
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    
    # For drill-down and comparison
    previous_value = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    trend = Column(String(20), nullable=True, comment="up, down, stable")

class AlertConfig(BaseModel):
    """Alert configuration for dashboard notifications"""
    __tablename__ = "alert_configs"
    
    alert_name = Column(String(200), nullable=False)
    alert_type = Column(String(50), nullable=False, comment="threshold, approval, deadline")
    metric_key = Column(String(100), nullable=False)
    
    # Alert conditions
    threshold_value = Column(Float, nullable=True)
    condition = Column(String(20), nullable=True, comment="gt, lt, eq, gte, lte")
    
    # Recipients
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    user_ids = Column(JSON, nullable=True, comment="List of user IDs to notify")
    
    # Settings
    is_email = Column(Boolean, default=True)
    is_dashboard = Column(Boolean, default=True)
    frequency = Column(String(20), default="immediate", comment="immediate, daily, weekly")
    
    last_triggered = Column(DateTime, nullable=True)