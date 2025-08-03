"""
Lead management service using SQLAlchemy ORM
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from ..models import Lead, Company, User, Opportunity, Contact, LeadStatus, RoleType

class LeadService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_lead(self, lead_data: dict, created_by: Optional[int] = None) -> Lead:
        """Create a new lead"""
        db_lead = Lead(
            company_id=lead_data.get('company_id'),
            location=lead_data.get('location'),
            lead_source=lead_data.get('lead_source'),
            sales_person_id=lead_data.get('sales_person_id'),
            status=lead_data.get('status', LeadStatus.NEW),
            notes=lead_data.get('notes'),
            priority=lead_data.get('priority'),
            expected_close_date=lead_data.get('expected_close_date'),
            created_by=created_by
        )
        
        self.db.add(db_lead)
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Get lead by ID with related details"""
        return self.db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.sales_person)
        ).filter(
            and_(
                Lead.id == lead_id,
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        ).first()
    
    def update_lead(self, lead_id: int, lead_data: dict, updated_by: Optional[int] = None) -> Optional[Lead]:
        """Update lead information"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return None
        
        for field, value in lead_data.items():
            if field not in ['id', 'created_on', 'created_by'] and value is not None:
                setattr(db_lead, field, value)
        
        # Update last activity date on any update
        db_lead.last_activity_date = datetime.utcnow()
        
        if updated_by:
            db_lead.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(db_lead)
        return db_lead
    
    def delete_lead(self, lead_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete lead"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            return False
        
        db_lead.is_active = False
        db_lead.deleted_on = datetime.utcnow()
        if deleted_by:
            db_lead.deleted_by = deleted_by
        
        self.db.commit()
        return True
    
    def get_leads(self, skip: int = 0, limit: int = 100, status: str = None, search: str = None) -> List[Lead]:
        """Get all leads with pagination and filtering"""
        query = self.db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.sales_person)
        ).filter(
            and_(
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        )
        
        if status:
            query = query.filter(Lead.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Company).filter(
                or_(
                    Company.name.ilike(search_term),
                    Lead.location.ilike(search_term),
                    Lead.notes.ilike(search_term)
                )
            )
        
        return query.order_by(Lead.last_activity_date.desc()).offset(skip).limit(limit).all()
    
    def get_leads_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Lead]:
        """Get leads by company"""
        return self.db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.sales_person)
        ).filter(
            and_(
                Lead.company_id == company_id,
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        ).order_by(Lead.created_on.desc()).offset(skip).limit(limit).all()
    
    def get_leads_by_salesperson(self, sales_person_id: int, skip: int = 0, limit: int = 100) -> List[Lead]:
        """Get leads by salesperson"""
        return self.db.query(Lead).options(
            joinedload(Lead.company),
            joinedload(Lead.sales_person)
        ).filter(
            and_(
                Lead.sales_person_id == sales_person_id,
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        ).order_by(Lead.last_activity_date.desc()).offset(skip).limit(limit).all()
    
    def get_lead_count(self, status: str = None, search: str = None) -> int:
        """Get total count of leads"""
        query = self.db.query(Lead).filter(
            and_(
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        )
        
        if status:
            query = query.filter(Lead.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Company).filter(
                or_(
                    Company.name.ilike(search_term),
                    Lead.location.ilike(search_term),
                    Lead.notes.ilike(search_term)
                )
            )
        
        return query.count()
    
    def convert_to_opportunity(self, lead_id: int, conversion_data: dict, created_by: int) -> dict:
        """Convert lead to opportunity"""
        db_lead = self.get_lead_by_id(lead_id)
        if not db_lead:
            raise ValueError("Lead not found")
        
        if db_lead.status != LeadStatus.QUALIFIED:
            raise ValueError("Only qualified leads can be converted to opportunities")
        
        # Validate that contact is a Decision Maker
        contact = self.db.query(Contact).filter(
            Contact.id == conversion_data['contact_id']
        ).first()
        
        if not contact or contact.role_type != RoleType.DECISION_MAKER:
            raise ValueError("Opportunity can only be created with a Decision Maker contact")
        
        # Create opportunity
        db_opportunity = Opportunity(
            lead_id=lead_id,
            company_id=db_lead.company_id,
            contact_id=conversion_data['contact_id'],
            name=conversion_data['opportunity_name'],
            stage=conversion_data.get('stage', 'L1'),
            amount=conversion_data.get('amount'),
            justification=conversion_data.get('justification'),
            notes=conversion_data.get('notes'),
            created_by=created_by
        )
        
        self.db.add(db_opportunity)
        
        # Update lead status
        db_lead.status = LeadStatus.CLOSED_WON
        db_lead.last_activity_date = datetime.utcnow()
        db_lead.updated_by = created_by
        
        self.db.commit()
        self.db.refresh(db_opportunity)
        
        return db_opportunity
    
    def get_lead_summary(self, sales_person_id: str = None) -> dict:
        """Get lead summary statistics"""
        query = self.db.query(Lead).filter(
            and_(
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        )
        
        if sales_person_id:
            query = query.filter(Lead.sales_person_id == sales_person_id)
        
        total_leads = query.count()
        new_leads = query.filter(Lead.status == LeadStatus.NEW).count()
        qualified_leads = query.filter(Lead.status == LeadStatus.QUALIFIED).count()
        closed_won = query.filter(Lead.status == LeadStatus.CLOSED_WON).count()
        closed_lost = query.filter(Lead.status == LeadStatus.CLOSED_LOST).count()
        dropped = query.filter(Lead.status == LeadStatus.DROPPED).count()
        
        conversion_rate = (closed_won / total_leads * 100) if total_leads > 0 else 0
        
        return {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "qualified_leads": qualified_leads,
            "closed_won": closed_won,
            "closed_lost": closed_lost,
            "dropped": dropped,
            "conversion_rate": round(conversion_rate, 2)
        }
    
    def auto_close_inactive_leads(self, weeks: int = 4) -> int:
        """Auto-close leads inactive for specified weeks"""
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
        
        inactive_leads = self.db.query(Lead).filter(
            and_(
                Lead.last_activity_date < cutoff_date,
                Lead.status.notin_([LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST, LeadStatus.DROPPED]),
                Lead.is_active == True,
                Lead.deleted_on.is_(None)
            )
        ).all()
        
        count = 0
        for lead in inactive_leads:
            lead.status = LeadStatus.DROPPED
            lead.notes = (lead.notes or '') + ' [Auto-closed due to inactivity]'
            lead.last_activity_date = datetime.utcnow()
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count