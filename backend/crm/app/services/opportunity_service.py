"""
Opportunity management service using SQLAlchemy ORM
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from ..models import Opportunity, Lead, Company, Contact, User, RoleType, OpportunityStatus

class OpportunityService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_opportunity(self, opportunity_data: dict, created_by: Optional[int] = None) -> Opportunity:
        """Create a new opportunity"""
        # Validate that contact is a Decision Maker
        contact = self.db.query(Contact).filter(
            Contact.id == opportunity_data['contact_id']
        ).first()
        
        if not contact or contact.role_type != RoleType.DECISION_MAKER:
            raise ValueError("Opportunity can only be created with a Decision Maker contact")
        
        db_opportunity = Opportunity(
            lead_id=opportunity_data.get('lead_id'),
            company_id=opportunity_data.get('company_id'),
            contact_id=opportunity_data.get('contact_id'),
            name=opportunity_data.get('name'),
            stage=opportunity_data.get('stage'),
            amount=opportunity_data.get('amount'),
            scoring=opportunity_data.get('scoring', 0),
            bom_id=opportunity_data.get('bom_id'),
            costing=opportunity_data.get('costing'),
            status=opportunity_data.get('status'),
            justification=opportunity_data.get('justification'),
            close_date=opportunity_data.get('close_date'),
            probability=opportunity_data.get('probability', 10),
            notes=opportunity_data.get('notes'),
            created_by=created_by
        )
        
        self.db.add(db_opportunity)
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity
    
    def get_opportunity_by_id(self, opportunity_id: int) -> Optional[Opportunity]:
        """Get opportunity by ID with related details"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.company),
            joinedload(Opportunity.contact),
            joinedload(Opportunity.lead),
            joinedload(Opportunity.creator)
        ).filter(
            and_(
                Opportunity.id == opportunity_id,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).first()
    
    def update_opportunity(self, opportunity_id: int, opportunity_data: dict, updated_by: Optional[int] = None) -> Optional[Opportunity]:
        """Update opportunity information"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None
        
        for field, value in opportunity_data.items():
            if field not in ['id', 'created_on', 'created_by'] and value is not None:
                setattr(db_opportunity, field, value)
        
        if updated_by:
            db_opportunity.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity
    
    def update_stage(self, opportunity_id: int, stage: str, updated_by: int, notes: str = None) -> Optional[Opportunity]:
        """Update opportunity stage"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None
        
        db_opportunity.stage = stage
        db_opportunity.updated_by = updated_by
        
        if notes:
            db_opportunity.notes = (db_opportunity.notes or '') + f"\n[Stage updated to {stage}]: {notes}"
        
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity
    
    def close_opportunity(self, opportunity_id: int, status: str, close_date: str, updated_by: int, notes: str = None) -> Optional[Opportunity]:
        """Close opportunity"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return None
        
        db_opportunity.status = status
        db_opportunity.close_date = close_date
        db_opportunity.updated_by = updated_by
        
        if notes:
            db_opportunity.notes = (db_opportunity.notes or '') + f"\n[Closed as {status}]: {notes}"
        
        self.db.commit()
        self.db.refresh(db_opportunity)
        return db_opportunity
    
    def delete_opportunity(self, opportunity_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete opportunity"""
        db_opportunity = self.get_opportunity_by_id(opportunity_id)
        if not db_opportunity:
            return False
        
        db_opportunity.is_active = False
        db_opportunity.deleted_on = datetime.utcnow()
        if deleted_by:
            db_opportunity.deleted_by = deleted_by
        
        self.db.commit()
        return True
    
    def get_opportunities(self, skip: int = 0, limit: int = 100, stage: str = None, 
                         status: str = None, search: str = None) -> List[Opportunity]:
        """Get all opportunities with pagination and filtering"""
        query = self.db.query(Opportunity).options(
            joinedload(Opportunity.company),
            joinedload(Opportunity.contact),
            joinedload(Opportunity.creator)
        ).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        )
        
        if stage:
            query = query.filter(Opportunity.stage == stage)
        
        if status:
            query = query.filter(Opportunity.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Company).join(Contact).filter(
                or_(
                    Opportunity.name.ilike(search_term),
                    Company.name.ilike(search_term),
                    Contact.full_name.ilike(search_term)
                )
            )
        
        return query.order_by(Opportunity.updated_on.desc()).offset(skip).limit(limit).all()
    
    def get_opportunities_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Get opportunities by company"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.company),
            joinedload(Opportunity.contact)
        ).filter(
            and_(
                Opportunity.company_id == company_id,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).order_by(Opportunity.created_on.desc()).offset(skip).limit(limit).all()
    
    def get_opportunities_by_lead(self, lead_id: int, skip: int = 0, limit: int = 100) -> List[Opportunity]:
        """Get opportunities by lead"""
        return self.db.query(Opportunity).options(
            joinedload(Opportunity.company),
            joinedload(Opportunity.contact)
        ).filter(
            and_(
                Opportunity.lead_id == lead_id,
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        ).order_by(Opportunity.created_on.desc()).offset(skip).limit(limit).all()
    
    def get_opportunity_count(self, stage: str = None, status: str = None, search: str = None) -> int:
        """Get total count of opportunities"""
        query = self.db.query(Opportunity).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        )
        
        if stage:
            query = query.filter(Opportunity.stage == stage)
        
        if status:
            query = query.filter(Opportunity.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Company).join(Contact).filter(
                or_(
                    Opportunity.name.ilike(search_term),
                    Company.name.ilike(search_term),
                    Contact.full_name.ilike(search_term)
                )
            )
        
        return query.count()
    
    def get_pipeline_summary(self, user_id: int = None) -> dict:
        """Get opportunity pipeline summary"""
        query = self.db.query(Opportunity).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None),
                Opportunity.status == OpportunityStatus.OPEN
            )
        )
        
        if user_id:
            query = query.filter(Opportunity.created_by == user_id)
        
        opportunities = query.all()
        
        total_opportunities = len(opportunities)
        total_value = sum(opp.amount or 0 for opp in opportunities)
        avg_scoring = sum(opp.scoring for opp in opportunities) / total_opportunities if total_opportunities > 0 else 0
        closing_stage_count = len([opp for opp in opportunities if opp.stage in ['L6', 'L7']])
        
        # Stage-wise breakdown
        stage_breakdown = {}
        for opp in opportunities:
            stage = opp.stage
            if stage not in stage_breakdown:
                stage_breakdown[stage] = {'count': 0, 'value': 0}
            stage_breakdown[stage]['count'] += 1
            stage_breakdown[stage]['value'] += opp.amount or 0
        
        stage_breakdown_list = [
            {'stage': stage, 'count': data['count'], 'value': data['value']}
            for stage, data in stage_breakdown.items()
        ]
        
        return {
            "summary": {
                "total_opportunities": total_opportunities,
                "total_value": total_value,
                "avg_scoring": round(avg_scoring, 2),
                "closing_stage_count": closing_stage_count
            },
            "stage_breakdown": stage_breakdown_list
        }
    
    def get_opportunity_metrics(self, user_id: int = None) -> dict:
        """Get opportunity metrics and analytics"""
        query = self.db.query(Opportunity).filter(
            and_(
                Opportunity.is_active == True,
                Opportunity.deleted_on.is_(None)
            )
        )
        
        if user_id:
            query = query.filter(Opportunity.created_by == user_id)
        
        opportunities = query.all()
        
        total_opportunities = len(opportunities)
        won_opportunities = len([opp for opp in opportunities if opp.status == OpportunityStatus.WON])
        lost_opportunities = len([opp for opp in opportunities if opp.status == OpportunityStatus.LOST])
        
        win_rate = (won_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0
        
        won_opps = [opp for opp in opportunities if opp.status == OpportunityStatus.WON]
        avg_deal_size = sum(opp.amount or 0 for opp in won_opps) / len(won_opps) if won_opps else 0
        
        pipeline_value = sum(opp.amount or 0 for opp in opportunities if opp.status == OpportunityStatus.OPEN)
        forecasted_revenue = sum((opp.amount or 0) * (opp.probability / 100) for opp in opportunities if opp.status == OpportunityStatus.OPEN)
        
        return {
            "total_opportunities": total_opportunities,
            "won_opportunities": won_opportunities,
            "lost_opportunities": lost_opportunities,
            "win_rate": round(win_rate, 2),
            "avg_deal_size": avg_deal_size,
            "pipeline_value": pipeline_value,
            "forecasted_revenue": forecasted_revenue
        }