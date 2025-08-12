"""
Contact management service using SQLAlchemy ORM
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from ..models import Contact, Company, User, RoleType


class ContactService:
    def __init__(self, db: Session):
        self.db = db

    def create_contact(
        self, contact_data: dict, created_by: Optional[int] = None
    ) -> Contact:
        """Create a new contact"""

        db_contact = Contact(
            salutation=contact_data.get("salutation"),
            first_name=contact_data.get("first_name"),
            middle_name=contact_data.get("middle_name"),
            last_name=contact_data.get("last_name"),
            designation=contact_data.get("designation"),
            email=contact_data.get("email"),
            primary_phone=contact_data.get("primary_phone"),
            decision_maker=contact_data.get("decision_maker", False),
            decision_maker_percentage=contact_data.get("decision_maker_percentage"),
            comments=contact_data.get("comments"),
            company_id=contact_data.get("company_id"),
            created_by=created_by,
        )

        self.db.add(db_contact)
        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact

    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """Get contact by ID with company details"""
        return (
            self.db.query(Contact)
            .options(joinedload(Contact.company))
            .filter(
                and_(
                    Contact.id == contact_id,
                    Contact.is_active == True,
                    Contact.deleted_on.is_(None),
                )
            )
            .first()
        )

    def get_contact_by_email(self, email: str) -> Optional[Contact]:
        """Get contact by email"""
        return (
            self.db.query(Contact)
            .filter(
                and_(
                    Contact.email == email,
                    Contact.is_active == True,
                    Contact.deleted_on.is_(None),
                )
            )
            .first()
        )

    def update_contact(
        self, contact_id: int, contact_data: dict, updated_by: Optional[int] = None
    ) -> Optional[Contact]:
        """Update contact information"""
        db_contact = self.get_contact_by_id(contact_id)
        if not db_contact:
            return None

        for field, value in contact_data.items():
            if field not in ["id", "created_on", "created_by"] and value is not None:
                setattr(db_contact, field, value)

        if updated_by:
            db_contact.updated_by = updated_by

        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact

    def delete_contact(self, contact_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete contact"""
        db_contact = self.get_contact_by_id(contact_id)
        if not db_contact:
            return False

        db_contact.is_active = False
        db_contact.deleted_on = datetime.utcnow()
        if deleted_by:
            db_contact.deleted_by = deleted_by

        self.db.commit()
        return True

    def get_contacts(
        self, skip: int = 0, limit: int = 100, search: str = None
    ) -> List[Contact]:
        """Get all contacts with pagination and search"""
        query = (
            self.db.query(Contact)
            .options(joinedload(Contact.company))
            .filter(and_(Contact.is_active == True, Contact.deleted_on.is_(None)))
        )

        if search:
            search_term = f"%{search}%"
            query = query.join(Company).filter(
                or_(
                    Contact.first_name.ilike(search_term),
                    Contact.email.ilike(search_term),
                    Contact.designation.ilike(search_term),
                    Company.name.ilike(search_term),
                )
            )

        return query.order_by(Contact.first_name).offset(skip).limit(limit).all()

    def get_contacts_by_company(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        """Get contacts by company"""
        return (
            self.db.query(Contact)
            .options(joinedload(Contact.company))
            .filter(
                and_(
                    Contact.company_id == company_id,
                    Contact.is_active == True,
                    Contact.deleted_on.is_(None),
                )
            )
            .order_by(Contact.first_name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_decision_makers(self, company_id: int) -> List[Contact]:
        """Get decision makers for a company"""
        return (
            self.db.query(Contact)
            .filter(
                and_(
                    Contact.company_id == company_id,
                    Contact.decision_maker == True,
                    Contact.is_active == True,
                    Contact.deleted_on.is_(None),
                )
            )
            .order_by(Contact.first_name)
            .all()
        )

    def get_contact_count(self, search: str = None) -> int:
        """Get total count of contacts"""
        query = self.db.query(Contact).filter(
            and_(Contact.is_active == True, Contact.deleted_on.is_(None))
        )

        if search:
            search_term = f"%{search}%"
            query = query.join(Company).filter(
                or_(
                    Contact.first_name.ilike(search_term),
                    Contact.last_name.ilike(search_term),
                    Contact.middle_name.ilike(search_term),
                    Contact.email.ilike(search_term),
                    Contact.designation.ilike(search_term),
                    Company.name.ilike(search_term),
                )
            )

        return query.count()
