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

    def create_company(
        self, company_data: dict, created_by: Optional[int] = None
    ) -> Company:
        """Create a new company"""
        try:
            db_company = Company(
                name=company_data.name,
                gst_number=company_data.gst_number,
                pan_number=company_data.pan_number,
                parent_company_id=company_data.parent_company_id or None,
                industry_category=company_data.industry_category,
                address=company_data.address,
                city=company_data.city,
                state=company_data.state,
                country=company_data.country or "India",
                postal_code=company_data.postal_code,
                website=company_data.website,
                description=company_data.description,
                created_by=created_by,
            )

            self.db.add(db_company)
            self.db.commit()
            self.db.refresh(db_company)
            return db_company
        except Exception as e:
            print(f"Error creating company: {e}")
            self.db.rollback()
            raise e

    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return (
            self.db.query(Company)
            .filter(
                and_(
                    Company.id == company_id,
                    Company.is_active == True,
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
        company_data,
        updated_by: Optional[int] = None,
    ) -> Optional[Company]:
        """Update company information"""
        try:
            db_company = self.get_company_by_id(company_id)
            if not db_company:
                return None

            # Convert Pydantic model to dict, only include fields that were provided
            company_dict = company_data.dict(exclude_unset=True)

            for field, value in company_dict.items():
                if field in ["id", "created_on", "created_by"]:
                    continue

                # ✅ Treat empty string as None
                if isinstance(value, str) and value.strip() == "":
                    value = None

                setattr(db_company, field, value)

            if updated_by:
                db_company.updated_by = updated_by

            self.db.commit()
            self.db.refresh(db_company)
            return db_company
        except Exception as e:
            print(f"Error updating company: {e}")
            self.db.rollback()
            raise e

    def delete_company(self, company_id: int, deleted_by: Optional[int] = None) -> bool:
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

    def get_companies(
        self, skip: int = 0, limit: int = 100, search: str = None
    ) -> List[Company]:
        """Get all companies with pagination and search"""
        query = self.db.query(Company).filter(
            and_(Company.is_active == True, Company.deleted_on.is_(None))
        )

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.industry_category.ilike(search_term),
                    Company.city.ilike(search_term),
                )
            )

        return query.order_by(Company.name).offset(skip).limit(limit).all()

    def get_company_count(self, search: str = None) -> int:
        """Get total count of companies"""
        query = self.db.query(Company).filter(
            and_(Company.is_active == True, Company.deleted_on.is_(None))
        )

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Company.name.ilike(search_term),
                    Company.industry_category.ilike(search_term),
                    Company.city.ilike(search_term),
                )
            )

        return query.count()
