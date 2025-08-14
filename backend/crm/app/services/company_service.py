"""
Enhanced Company management service for Swayatta 4.0 - Simplified without approval workflow
"""

from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from datetime import datetime
from difflib import SequenceMatcher
import uuid
from ..models import Company, User
from ..schemas.company import (
    CompanyCreate, 
    CompanyUpdate, 
    DuplicateCheckResult,
    CompanyType,
    CompanyStatus
)

class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def check_duplicates(self, company_data: CompanyCreate, exclude_id: Optional[int] = None) -> DuplicateCheckResult:
        """
        Check for duplicate companies using exact and fuzzy matching
        """
        query = self.db.query(Company).filter(
            and_(
                Company.is_active == True,
                Company.deleted_on.is_(None)
            )
        )
        
        if exclude_id:
            query = query.filter(Company.id != exclude_id)
        
        existing_companies = query.all()
        
        # Exact match check
        for existing in existing_companies:
            # Check exact match on name + GST (if both have GST)
            if (existing.name.lower() == company_data.name.lower() and 
                existing.gst_number and company_data.gst_number and
                existing.gst_number == company_data.gst_number):
                return DuplicateCheckResult(
                    is_duplicate=True,
                    match_type="EXACT",
                    matched_companies=[{
                        "id": existing.id,
                        "name": existing.name,
                        "gst_number": existing.gst_number,
                        "city": existing.city
                    }],
                    can_override=True,
                    requires_admin_approval=False  # No approval required anymore
                )
        
        # Fuzzy match check
        for existing in existing_companies:
            # Calculate similarity for name + country + city
            name_similarity = SequenceMatcher(None, 
                existing.name.lower(), 
                company_data.name.lower()).ratio()
            
            country_match = existing.country.lower() == company_data.country.lower()
            city_match = existing.city.lower() == company_data.city.lower()
            
            # Combined similarity score
            if country_match and city_match and name_similarity >= 0.9:
                return DuplicateCheckResult(
                    is_duplicate=True,
                    match_type="FUZZY",
                    matched_companies=[{
                        "id": existing.id,
                        "name": existing.name,
                        "country": existing.country,
                        "city": existing.city
                    }],
                    similarity_score=name_similarity,
                    can_override=True,
                    requires_admin_approval=False  # No approval required anymore
                )
        
        return DuplicateCheckResult(is_duplicate=False, match_type="NONE", matched_companies=[])

    def create_company(
        self, 
        company_data: CompanyCreate, 
        created_by: int,
        user_role: str = "SALESPERSON",
        override_duplicate: bool = False,
        override_reason: Optional[str] = None
    ) -> Company:
        """Create a new company - immediately active without approval"""
        
        # Check for duplicates unless overridden
        if not override_duplicate:
            duplicate_result = self.check_duplicates(company_data)
            if duplicate_result.is_duplicate:
                raise ValueError(f"Duplicate company found: {duplicate_result.match_type} match detected")
        
        try:
            db_company = Company(
                # Basic Information
                name=company_data.name,
                company_type=company_data.company_type,
                industry=company_data.industry,
                sub_industry=company_data.sub_industry,
                annual_revenue=company_data.annual_revenue,
                
                # Identification & Compliance
                gst_number=company_data.gst_number,
                pan_number=company_data.pan_number,
                international_unique_id=company_data.international_unique_id,
                supporting_documents=company_data.supporting_documents,
                verification_source=company_data.verification_source,
                verification_date=company_data.verification_date,
                verified_by=self._get_user_id_by_name(company_data.verified_by),
                
                # Registered Address
                address=company_data.address,
                country=company_data.country,
                state=company_data.state,
                city=company_data.city,
                pin_code=company_data.pin_code,
                
                # Hierarchy & Linkages
                parent_child_mapping_confirmed=company_data.parent_child_mapping_confirmed,
                linked_subsidiaries=self._process_subsidiaries(company_data.linked_subsidiaries),
                associated_channel_partner=company_data.associated_channel_partner,
                
                # System Metadata - Immediately ACTIVE
                status=CompanyStatus.ACTIVE,
                change_log_id=uuid.uuid4(),
                created_by=created_by,
                
                # Optional fields
                website=company_data.website,
                description=company_data.description,
            )
            
            # Auto-tag based on revenue
            db_company.auto_tag_revenue()
            
            # Set parent company if specified
            if company_data.parent_company_name and company_data.parent_company_name != "None":
                parent = self.get_company_by_name(company_data.parent_company_name)
                if parent:
                    db_company.parent_company_id = parent.id

            self.db.add(db_company)
            self.db.commit()
            self.db.refresh(db_company)
            
            # Log the creation
            self._log_company_action(db_company.id, "CREATED", created_by, 
                                   f"Company created and immediately activated")
            
            return db_company
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID with related data"""
        return (
            self.db.query(Company)
            .options(
                joinedload(Company.parent_company),
                joinedload(Company.subsidiaries),
                joinedload(Company.verifier)
            )
            .filter(
                and_(
                    Company.id == company_id,
                    Company.deleted_on.is_(None),
                )
            )
            .first()
        )

    def get_company_by_name(self, name: str) -> Optional[Company]:
        """Get company by name"""
        return (
            self.db.query(Company)
            .filter(
                and_(
                    Company.name == name,
                    Company.is_active == True,
                    Company.deleted_on.is_(None),
                )
            )
            .first()
        )

    def update_company(
        self,
        company_id: int,
        company_data: CompanyUpdate,
        updated_by: int,
        user_role: str = "admin"
    ) -> Optional[Company]:
        """Update company information"""
        
        db_company = self.get_company_by_id(company_id)
        if not db_company:
            return None
        
        # Convert Pydantic model to dict, only include fields that were provided
        company_dict = company_data.dict(exclude_unset=True)
        
        old_values = {}
        for field, value in company_dict.items():
            if field in ["id", "created_on", "created_by"]:
                continue
            
            # Store old value for audit
            old_values[field] = getattr(db_company, field, None)
            
            # Handle empty strings
            if isinstance(value, str) and value.strip() == "":
                value = None
            
            setattr(db_company, field, value)
        
        # Update metadata
        db_company.updated_by = updated_by
        db_company.change_log_id = uuid.uuid4()
        
        # Re-apply auto-tagging if revenue changed
        if 'annual_revenue' in company_dict:
            db_company.auto_tag_revenue()
        
        self.db.commit()
        self.db.refresh(db_company)
        
        # Log the update
        changes = {k: {"old": old_values[k], "new": v} for k, v in company_dict.items()}
        self._log_company_action(company_id, "UPDATED", updated_by, 
                               f"Company updated: {changes}")
        
        return db_company

    def delete_company(self, company_id: int, deleted_by: int, user_role: str = "admin") -> bool:
        """Soft delete company (Admin only)"""
        
        if user_role != "admin":
            raise ValueError("Only Admin can delete companies")
        
        db_company = self.get_company_by_id(company_id)
        if not db_company:
            return False

        db_company.is_active = False
        db_company.deleted_on = datetime.utcnow()
        db_company.deleted_by = deleted_by
        db_company.change_log_id = uuid.uuid4()

        self.db.commit()
        
        # Log the deletion
        self._log_company_action(company_id, "DELETED", deleted_by, "Company soft deleted")
        
        return True

    def get_companies(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: str = None,
        filters: Dict = None,
        user_role: str = "admin",
        user_id: int = None
    ) -> List[Company]:
        """Get all companies with pagination, search, and role-based filtering"""
        
        query = self.db.query(Company).options(
            joinedload(Company.parent_company),
            joinedload(Company.verifier)
        ).filter(Company.deleted_on.is_(None))
        
        # Role-based filtering
        if user_role == "SALESPERSON":
            # Salesperson can only see their own created companies
            query = query.filter(Company.created_by == user_id)
        
        # Apply filters
        if filters:
            if filters.get("status"):
                query = query.filter(Company.status == filters["status"])
            if filters.get("company_type"):
                query = query.filter(Company.company_type == filters["company_type"])
            if filters.get("industry"):
                query = query.filter(Company.industry == filters["industry"])
            if filters.get("is_high_revenue"):
                query = query.filter(Company.is_high_revenue == filters["is_high_revenue"])
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.industry.ilike(search_term),
                    Company.city.ilike(search_term),
                    Company.gst_number.ilike(search_term),
                    Company.pan_number.ilike(search_term)
                )
            )

        return query.order_by(Company.name).offset(skip).limit(limit).all()

    def get_company_count(
        self, 
        search: str = None, 
        filters: Dict = None,
        user_role: str = "admin",
        user_id: int = None
    ) -> int:
        """Get total count of companies with same filters as get_companies"""
        
        query = self.db.query(Company).filter(Company.deleted_on.is_(None))
        
        # Role-based filtering
        if user_role == "SALESPERSON":
            query = query.filter(Company.created_by == user_id)
        
        # Apply filters (same logic as get_companies)
        if filters:
            if filters.get("status"):
                query = query.filter(Company.status == filters["status"])
            if filters.get("company_type"):
                query = query.filter(Company.company_type == filters["company_type"])
            if filters.get("industry"):
                query = query.filter(Company.industry == filters["industry"])
            if filters.get("is_high_revenue"):
                query = query.filter(Company.is_high_revenue == filters["is_high_revenue"])
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.industry.ilike(search_term),
                    Company.city.ilike(search_term)
                )
            )

        return query.count()

    def get_company_stats(self) -> Dict:
        """Get company statistics for dashboard"""
        
        total = self.db.query(Company).filter(Company.deleted_on.is_(None)).count()
        active = self.db.query(Company).filter(
            and_(Company.status == CompanyStatus.ACTIVE, Company.deleted_on.is_(None))
        ).count()
        high_revenue = self.db.query(Company).filter(
            and_(Company.is_high_revenue == True, Company.deleted_on.is_(None))
        ).count()
        
        # Companies by type
        type_stats = self.db.query(
            Company.company_type, func.count(Company.id)
        ).filter(Company.deleted_on.is_(None)).group_by(Company.company_type).all()
        
        # Companies by industry
        industry_stats = self.db.query(
            Company.industry, func.count(Company.id)
        ).filter(Company.deleted_on.is_(None)).group_by(Company.industry).all()
        
        return {
            "total_companies": total,
            "active_companies": active,
            "high_revenue_companies": high_revenue,
            "companies_by_type": {str(type_): count for type_, count in type_stats},
            "companies_by_industry": {industry: count for industry, count in industry_stats}
        }

    def _get_user_id_by_name(self, username: str) -> Optional[int]:
        """Get user ID by username"""
        user = self.db.query(User).filter(User.username == username).first()
        return user.id if user else None

    def _process_subsidiaries(self, subsidiaries: List[str]) -> Optional[List[int]]:
        """Convert subsidiary names to IDs"""
        if not subsidiaries or subsidiaries == ["None"]:
            return None
        
        subsidiary_ids = []
        for sub_name in subsidiaries:
            sub_company = self.get_company_by_name(sub_name)
            if sub_company:
                subsidiary_ids.append(sub_company.id)
        
        return subsidiary_ids if subsidiary_ids else None

    def _log_company_action(self, company_id: int, action: str, user_id: Optional[int], details: str):
        """Log company actions for audit trail"""
        # This would integrate with your audit logging system
        # For now, we'll just print (implement proper logging as needed)
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "company_id": company_id,
            "action": action,
            "user_id": user_id,
            "details": details,
            "change_log_id": str(uuid.uuid4())
        }
        print(f"AUDIT LOG: {log_entry}")  # Replace with proper logging