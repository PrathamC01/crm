"""
Company management service using SQLAlchemy ORM
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from datetime import datetime
from ..models import Company, User

class CompanyService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_company(self, company_data: dict, created_by: Optional[str] = None) -> Company:
        """Create a new company"""
        db_company = Company(
            name=company_data.get('name'),
            gst_number=company_data.get('gst_number'),
            pan_number=company_data.get('pan_number'),
            parent_company_id=company_data.get('parent_company_id'),
            industry_category=company_data.get('industry_category'),
            address=company_data.get('address'),
            city=company_data.get('city'),
            state=company_data.get('state'),
            country=company_data.get('country', 'India'),
            postal_code=company_data.get('postal_code'),
            website=company_data.get('website'),
            description=company_data.get('description'),
            created_by=created_by
        )
        
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company
    
    def get_company_by_id(self, company_id: str) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(
            and_(
                Company.id == company_id,
                Company.is_active == True,
                Company.deleted_on.is_(None)
            )
        ).first()
    
    def get_company_by_name(self, name: str) -> Optional[Company]:
        """Get company by name"""
        return self.db.query(Company).filter(
            and_(
                Company.name == name,
                Company.is_active == True,
                Company.deleted_on.is_(None)
            )
        ).first()
    
    def update_company(self, company_id: str, company_data: dict, updated_by: Optional[str] = None) -> Optional[Company]:
        """Update company information"""
        db_company = self.get_company_by_id(company_id)
        if not db_company:
            return None
        
        for field, value in company_data.items():
            if field not in ['id', 'created_on', 'created_by'] and value is not None:
                setattr(db_company, field, value)
        
        if updated_by:
            db_company.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(db_company)
        return db_company
    
    def delete_company(self, company_id: str, deleted_by: Optional[str] = None) -> bool:
        """Soft delete company"""
        db_company = self.get_company_by_id(company_id)
        if not db_company:
            return False
        
        db_company.is_active = False
        db_company.deleted_on = datetime.utcnow()
        if deleted_by:
            db_company.deleted_by = deleted_by
        
        self.db.commit()
        return True
    
    def get_companies(self, skip: int = 0, limit: int = 100, search: str = None) -> List[Company]:
        """Get all companies with pagination and search"""
        query = self.db.query(Company).filter(
            and_(
                Company.is_active == True,
                Company.deleted_on.is_(None)
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.industry_category.ilike(search_term),
                    Company.city.ilike(search_term)
                )
            )
        
        return query.order_by(Company.name).offset(skip).limit(limit).all()
    
    def get_company_count(self, search: str = None) -> int:
        """Get total count of companies"""
        query = self.db.query(Company).filter(
            and_(
                Company.is_active == True,
                Company.deleted_on.is_(None)  
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.industry_category.ilike(search_term),
                    Company.city.ilike(search_term)
                )
            )
        
        return query.count()