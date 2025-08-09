"""
SQLAlchemy User model with fixed foreign key relationships
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    department_id = Column(
        Integer, ForeignKey("departments.id"), nullable=True, index=True
    )
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users", foreign_keys=[role_id])
    department = relationship(
        "Department", back_populates="users", foreign_keys=[department_id]
    )

    # Companies created by this user
    companies_created = relationship(
        "Company", foreign_keys="Company.created_by", back_populates="creator"
    )
    companies_updated = relationship(
        "Company", foreign_keys="Company.updated_by", back_populates="updater"
    )

    # Contacts created by this user
    contacts_created = relationship(
        "Contact", foreign_keys="Contact.created_by", back_populates="creator"
    )
    contacts_updated = relationship(
        "Contact", foreign_keys="Contact.updated_by", back_populates="updater"
    )

    # Leads created by this user
    leads_created = relationship(
        "Lead", foreign_keys="Lead.created_by", back_populates="creator"
    )
    leads_updated = relationship(
        "Lead", foreign_keys="Lead.updated_by", back_populates="updater"
    )
    leads_assigned = relationship(
        "Lead", foreign_keys="Lead.sales_person_id", back_populates="sales_person"
    )

    # Opportunities created by this user
    opportunities_created = relationship(
        "Opportunity", foreign_keys="Opportunity.created_by", back_populates="creator"
    )
    opportunities_updated = relationship(
        "Opportunity", foreign_keys="Opportunity.updated_by", back_populates="updater"
    )

    @property
    def full_name(self):
        return self.name

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email}), role={self.role}, department={self.department})>"