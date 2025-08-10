"""
Dashboard Service - Business logic for dashboard operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import Depends

from ..models.dashboard import DashboardConfig, DashboardWidget, DashboardMetric, AlertConfig
from ..models.lead import Lead, LeadStatus
from ..models.opportunity import Opportunity, OpportunityStatus
from ..models.quotation import Quotation, QuotationStatus
from ..models.user import User
from ..models.department import Department
from ..models.masters import ProductMaster, ProductPricingMaster
from ..dependencies.database import get_postgres_db

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_sales_dashboard_data(self, user_id: Optional[int] = None, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Get sales dashboard data"""
        
        # Total leads - fix join issues
        leads_query = self.db.query(Lead)
        if department_id:
            leads_query = leads_query.join(User, Lead.sales_person_id == User.id).filter(User.department_id == department_id)
        
        total_leads = leads_query.count()
        active_leads = leads_query.filter(Lead.status.in_([LeadStatus.NEW, LeadStatus.ACTIVE, LeadStatus.CONTACTED])).count()
        converted_leads = leads_query.filter(Lead.status == LeadStatus.CONVERTED).count()
        
        # Total opportunities - fix join issues
        opps_query = self.db.query(Opportunity)
        if department_id:
            opps_query = opps_query.join(User, Opportunity.created_by == User.id).filter(User.department_id == department_id)
        
        total_opportunities = opps_query.count()
        open_opportunities = opps_query.filter(Opportunity.status.in_([OpportunityStatus.PROSPECTING, OpportunityStatus.QUALIFICATION])).count()
        won_opportunities = opps_query.filter(Opportunity.status == OpportunityStatus.WON).count()
        
        # Revenue calculations - fix attribute name
        revenue_query = self.db.query(func.sum(Opportunity.amount)).filter(Opportunity.status == OpportunityStatus.WON)
        if department_id:
            revenue_query = revenue_query.join(User, Opportunity.created_by == User.id).filter(User.department_id == department_id)
        
        total_revenue = revenue_query.scalar() or 0
        
        # This month's revenue
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = self.db.query(func.sum(Opportunity.amount)).filter(
            and_(
                Opportunity.status == OpportunityStatus.WON,
                Opportunity.updated_on >= current_month_start
            )
        ).scalar() or 0
        
        # Assignment overview - fix join issues
        assignment_data = self.db.query(
            User.name,
            func.count(Lead.id).label('lead_count'),
            func.count(Opportunity.id).label('opp_count')
        ).select_from(User).outerjoin(Lead, Lead.sales_person_id == User.id).outerjoin(Opportunity, Opportunity.created_by == User.id).group_by(User.id, User.name).all()
        
        # Approvals pending
        pending_quotes = self.db.query(func.count(Quotation.id)).filter(
            Quotation.status.in_([QuotationStatus.DRAFT, QuotationStatus.SUBMITTED])
        ).scalar() or 0
        
        # Lead status breakdown
        lead_status_data = self.db.query(
            Lead.status,
            func.count(Lead.id).label('count')
        ).group_by(Lead.status).all()
        
        # Opportunity pipeline - fix attribute name
        opp_pipeline_data = self.db.query(
            Opportunity.status,
            func.count(Opportunity.id).label('count'),
            func.sum(Opportunity.amount).label('total_value')
        ).group_by(Opportunity.status).all()
        
        return {
            "metrics": {
                "total_leads": total_leads,
                "active_leads": active_leads,
                "converted_leads": converted_leads,
                "conversion_rate": round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 2),
                "total_opportunities": total_opportunities,
                "open_opportunities": open_opportunities,
                "won_opportunities": won_opportunities,
                "win_rate": round((won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0, 2),
                "total_revenue": float(total_revenue),
                "monthly_revenue": float(monthly_revenue),
                "pending_approvals": pending_quotes
            },
            "assignment_overview": [
                {
                    "user_name": row.name,
                    "leads": row.lead_count or 0,
                    "opportunities": row.opp_count or 0
                }
                for row in assignment_data
            ],
            "lead_status_breakdown": [
                {
                    "status": row.status.value if row.status else "Unknown",
                    "count": row.count
                }
                for row in lead_status_data
            ],
            "opportunity_pipeline": [
                {
                    "status": row.status.value if row.status else "Unknown",
                    "count": row.count,
                    "total_value": float(row.total_value) if row.total_value else 0
                }
                for row in opp_pipeline_data
            ]
        }
    
    async def get_presales_dashboard_data(self, user_id: Optional[int] = None, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Get presales dashboard data"""
        
        # Solution team workload - fix join issues
        presales_users = self.db.query(User).join(Department, User.department_id == Department.id).filter(
            Department.name.ilike('%presales%')
        ).all()
        
        workload_data = []
        for user in presales_users:
            active_opportunities = self.db.query(func.count(Opportunity.id)).filter(
                and_(
                    Opportunity.assigned_to == user.id,
                    Opportunity.status.in_([OpportunityStatus.PROSPECTING, OpportunityStatus.QUALIFICATION])
                )
            ).scalar() or 0
            
            pending_quotes = self.db.query(func.count(Quotation.id)).filter(
                and_(
                    Quotation.created_by == user.id,
                    Quotation.status.in_([QuotationStatus.DRAFT, QuotationStatus.SUBMITTED])
                )
            ).scalar() or 0
            
            workload_data.append({
                "user_name": user.name,
                "active_opportunities": active_opportunities,
                "pending_quotes": pending_quotes,
                "total_workload": active_opportunities + pending_quotes
            })
        
        # Approvals pending for presales team
        presales_approvals = self.db.query(
            Quotation.status,
            func.count(Quotation.id).label('count')
        ).filter(
            Quotation.status.in_([QuotationStatus.PENDING, QuotationStatus.REVIEW])
        ).group_by(Quotation.status).all()
        
        return {
            "workload_data": workload_data,
            "approval_summary": [
                {
                    "status": row.status.value if row.status else "Unknown",
                    "count": row.count
                }
                for row in presales_approvals
            ]
        }
    
    async def get_product_dashboard_data(self, user_id: Optional[int] = None, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Get product dashboard data"""
        
        # Top-selling products (based on opportunities) - fix join and attribute
        top_products = self.db.query(
            ProductMaster.name,
            ProductMaster.cat2_category,
            func.count(Opportunity.id).label('opportunity_count'),
            func.sum(Opportunity.amount).label('total_value')
        ).select_from(ProductMaster).outerjoin(
            # This would need a proper join table in real implementation
            Opportunity, ProductMaster.id == Opportunity.id  # Placeholder
        ).group_by(
            ProductMaster.id, ProductMaster.name, ProductMaster.cat2_category
        ).order_by(desc('total_value')).limit(10).all()
        
        # Sales by product category
        category_sales = self.db.query(
            ProductMaster.cat2_category,
            func.count(ProductMaster.id).label('product_count'),
            func.avg(ProductPricingMaster.recurring_selling_price).label('avg_price')
        ).select_from(ProductMaster).outerjoin(ProductPricingMaster).group_by(
            ProductMaster.cat2_category
        ).all()
        
        return {
            "top_products": [
                {
                    "product_name": row.name,
                    "category": row.cat2_category,
                    "opportunity_count": row.opportunity_count,
                    "total_value": float(row.total_value) if row.total_value else 0
                }
                for row in top_products
            ],
            "category_performance": [
                {
                    "category": row.cat2_category,
                    "product_count": row.product_count,
                    "average_price": float(row.avg_price) if row.avg_price else 0
                }
                for row in category_sales
            ]
        }
    
    async def get_default_dashboard_data(self, user_id: Optional[int] = None, department_id: Optional[int] = None) -> Dict[str, Any]:
        """Get general overview dashboard data"""
        
        # Overall system metrics
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        total_departments = self.db.query(func.count(Department.id)).scalar() or 0
        total_leads = self.db.query(func.count(Lead.id)).scalar() or 0
        total_opportunities = self.db.query(func.count(Opportunity.id)).scalar() or 0
        total_products = self.db.query(func.count(ProductMaster.id)).scalar() or 0
        
        # Recent activities (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_leads = self.db.query(func.count(Lead.id)).filter(Lead.created_on >= week_ago).scalar() or 0
        recent_opportunities = self.db.query(func.count(Opportunity.id)).filter(Opportunity.created_on >= week_ago).scalar() or 0
        
        return {
            "system_overview": {
                "total_users": total_users,
                "total_departments": total_departments,
                "total_leads": total_leads,
                "total_opportunities": total_opportunities,
                "total_products": total_products
            },
            "recent_activity": {
                "new_leads_week": recent_leads,
                "new_opportunities_week": recent_opportunities
            }
        }
    
    async def create_dashboard_widget(self, dashboard_id: int, widget_data: Dict[str, Any], created_by: int) -> DashboardWidget:
        """Create a new dashboard widget"""
        widget = DashboardWidget(
            dashboard_id=dashboard_id,
            created_by=created_by,
            **widget_data
        )
        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)
        return widget
    
    async def get_user_dashboard_config(self, user_id: int, dashboard_type: str) -> Optional[DashboardConfig]:
        """Get user's dashboard configuration"""
        return self.db.query(DashboardConfig).filter(
            and_(
                DashboardConfig.user_id == user_id,
                DashboardConfig.dashboard_type == dashboard_type
            )
        ).first()

def get_dashboard_service(db: Session = Depends(get_postgres_db)) -> DashboardService:
    """Dependency to get dashboard service"""
    return DashboardService(db)