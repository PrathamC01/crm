"""
SQLAlchemy Company model
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class Company(BaseModel):
    __tablename__ = 'companies'
    
    name = Column(String(255), unique=True, nullable=False, index=True)
    gst_number = Column(String(15), nullable=True, index=True)
    pan_number = Column(String(10), nullable=True, index=True)
    parent_company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    industry_category = Column(String(100))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default='India')
    postal_code = Column(String(10))
    website = Column(String(255))
    description = Column(Text)
    
    # Self-referential relationship for parent company
    parent_company = relationship("Company", remote_side="Company.id", back_populates="subsidiaries")
    subsidiaries = relationship("Company", back_populates="parent_company")
    
    # Audit relationships
    creator = relationship("User", foreign_keys="Company.created_by", back_populates="companies_created")
    updater = relationship("User", foreign_keys="Company.updated_by", back_populates="companies_updated")
    
    # Related entities
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", foreign_keys="[Lead.company_id]", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")
    documents = relationship("CompanyDocument", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"