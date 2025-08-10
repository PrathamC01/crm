"""
Dashboard Configuration Models
"""
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class WidgetTypeEnum(str, enum.Enum):
    KPI_CARD = "kpi_card"
    CHART = "chart"
    TABLE = "table"
    APPROVAL_LIST = "approval_list"
    ACTIVITY_FEED = "activity_feed"

# Dashboard Configuration
class DashboardConfig(BaseModel):
    __tablename__ = "dashboard_config"
    
    dashboard_name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey('department_master.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('user_master.id'), nullable=True)
    is_default = Column(Boolean, default=False)
    layout_config = Column(JSON, comment="Dashboard layout configuration")
    
    # Relationships
    department = relationship("DepartmentMaster")
    user = relationship("UserMaster")
    widgets = relationship("DashboardWidget", back_populates="dashboard")

# Dashboard Widgets
class DashboardWidget(BaseModel):
    __tablename__ = "dashboard_widgets"
    
    dashboard_id = Column(Integer, ForeignKey('dashboard_config.id'), nullable=False)
    widget_name = Column(String(100), nullable=False)
    widget_type = Column(String(50), nullable=False)  # kpi_card, chart, table, etc.
    
    # Position and Size
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=1)
    height = Column(Integer, default=1)
    
    # Configuration
    data_source = Column(String(100), nullable=False)  # SQL query, API endpoint, etc.
    config = Column(JSON, comment="Widget-specific configuration")
    refresh_interval = Column(Integer, default=300, comment="Refresh interval in seconds")
    
    # Relationships
    dashboard = relationship("DashboardConfig", back_populates="widgets")