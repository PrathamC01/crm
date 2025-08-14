"""
Enhanced SQLAlchemy Company model for Swayatta 4.0 - Simplified without approval workflow
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean, DateTime, Numeric, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from .base import BaseModel

class CompanyType(enum.Enum):
    DOMESTIC_GST = "DOMESTIC_GST"
    DOMESTIC_NONGST = "DOMESTIC_NONGST"
    NGO = "NGO"
    OVERSEAS = "OVERSEAS"

class CompanyStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class VerificationSource(enum.Enum):
    GST = "GST"
    MCA = "MCA"
    PAN_NSDL = "PAN_NSDL"
    DIGILOCKER = "DIGILOCKER"
    GARTNER = "GARTNER"
    MANUAL = "MANUAL"

class Company(BaseModel):
    __tablename__ = 'companies'
    
    # Basic Information
    name = Column(String(255), unique=True, nullable=False, index=True)
    parent_company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    company_type = Column(Enum(CompanyType), nullable=False)
    industry = Column(String(100), nullable=False)
    sub_industry = Column(String(100), nullable=False)
    annual_revenue = Column(Numeric(15, 2), nullable=False)
    
    # Identification & Compliance
    gst_number = Column(String(15), nullable=True, index=True)
    pan_number = Column(String(10), nullable=True, index=True)
    international_unique_id = Column(String(50), nullable=True, index=True)
    supporting_documents = Column(JSON, nullable=False)  # File paths/URLs
    verification_source = Column(Enum(VerificationSource), nullable=False)
    verification_date = Column(DateTime, nullable=False)
    verified_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Registered Address (all mandatory)
    address = Column(Text, nullable=False)
    country = Column(String(100), nullable=False, default='India')
    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    pin_code = Column(String(10), nullable=False)
    
    # Hierarchy & Linkages
    parent_child_mapping_confirmed = Column(Boolean, nullable=False, default=False)
    linked_subsidiaries = Column(JSON, nullable=True)  # Array of company IDs
    associated_channel_partner = Column(String(255), nullable=True)
    
    # System Metadata
    status = Column(Enum(CompanyStatus), nullable=False, default=CompanyStatus.ACTIVE)
    change_log_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Additional fields
    website = Column(String(255))
    description = Column(Text)
    
    # Auto-tagging fields
    is_high_revenue = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    # Self-referential relationship for parent company
    parent_company = relationship("Company", remote_side="Company.id", back_populates="subsidiaries")
    subsidiaries = relationship("Company", back_populates="parent_company")
    
    # Audit relationships
    creator = relationship("User", foreign_keys="Company.created_by", back_populates="companies_created")
    updater = relationship("User", foreign_keys="Company.updated_by", back_populates="companies_updated")
    verifier = relationship("User", foreign_keys="Company.verified_by")
    
    # Related entities
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", foreign_keys="[Lead.company_id]", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, type={self.company_type})>"
    
    def auto_tag_revenue(self):
        """Auto-tag company based on revenue threshold"""
        if self.annual_revenue and self.annual_revenue > 20000000:  # ₹2 crore
            self.is_high_revenue = True
            if not self.tags:
                self.tags = []
            if "HIGH_REVENUE_COMPANY" not in self.tags:
                self.tags.append("HIGH_REVENUE_COMPANY")