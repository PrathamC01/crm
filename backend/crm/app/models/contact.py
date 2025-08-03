"""
SQLAlchemy Contact model
"""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
from .base import BaseModel

class RoleType(str, Enum):
    ADMIN = "Admin"
    INFLUENCER = "Influencer"
    DECISION_MAKER = "Decision Maker"

class Contact(BaseModel):
    __tablename__ = 'contacts'
    
    full_name = Column(String(255), nullable=False)
    designation = Column(String(100))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False, index=True)
    role_type = Column(SQLEnum(RoleType), nullable=False, index=True)
    business_card_path = Column(String(500))
    
    # Relationships
    company = relationship("Company", back_populates="contacts")
    creator = relationship("User", foreign_keys="Contact.created_by", back_populates="contacts_created")
    updater = relationship("User", foreign_keys="Contact.updated_by", back_populates="contacts_updated")
    
    # Opportunities linked to this contact (only Decision Makers)
    opportunities = relationship("Opportunity", back_populates="contact")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.full_name}, role={self.role_type})>"