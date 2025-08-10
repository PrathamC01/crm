"""
Leads Module Models
"""
from sqlalchemy import Column, Integer, String, Text, Float, Date, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class LeadStatusEnum(str, enum.Enum):
    NEW = "New"
    ACTIVE = "Active"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"
    CONVERTED = "Converted"
    REJECTED = "Rejected"

class LeadSourceEnum(str, enum.Enum):
    REFERRAL = "Referral"
    DIRECT_MARKETING = "Direct Marketing"
    ADVERTISEMENT = "Advertisement"
    WEBSITE = "Website"
    COLD_CALLING = "Cold Calling"
    TRADE_SHOW = "Trade Show"
    SOCIAL_MEDIA = "Social Media"

class PriorityEnum(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

# Contact Master
class ContactMaster(BaseModel):
    __tablename__ = "contact_master"
    
    full_name = Column(String(200), nullable=False)
    designation = Column(String(100))
    email = Column(String(255))
    phone_number = Column(String(20))
    company_id = Column(Integer, ForeignKey('company_master.id'), nullable=False)
    decision_maker = Column(String(50))  # Primary, Secondary, Influencer, etc.
    notes = Column(Text)
    
    # Relationships
    company = relationship("CompanyMaster", back_populates="contacts")
    leads = relationship("LeadMaster", back_populates="primary_contact")

# Company Master
class CompanyMaster(BaseModel):
    __tablename__ = "company_master"
    
    company_name = Column(String(200), nullable=False)
    industry_id = Column(Integer, ForeignKey('industry_category_master.id'))
    gst_number = Column(String(15))
    pan_number = Column(String(10))
    
    # Address
    address = Column(Text)
    city_id = Column(Integer, ForeignKey('city_master.id'))
    state_id = Column(Integer, ForeignKey('state_master.id'))
    postal_code = Column(String(10))
    
    # Additional Info
    website = Column(String(255))
    annual_revenue = Column(Float)
    employee_count = Column(Integer)
    description = Column(Text)
    
    # Relationships
    industry = relationship("IndustryCategoryMaster")
    city = relationship("CityMaster")
    state = relationship("StateMaster")
    contacts = relationship("ContactMaster", back_populates="company")
    leads = relationship("LeadMaster", back_populates="company")
    opportunities = relationship("OpportunityMaster", back_populates="company")

# Lead Master
class LeadMaster(BaseModel):
    __tablename__ = "lead_master"
    
    lead_title = Column(String(200), nullable=False)
    company_id = Column(Integer, ForeignKey('company_master.id'), nullable=False)
    primary_contact_id = Column(Integer, ForeignKey('contact_master.id'))
    
    # Lead Details
    lead_source = Column(SQLEnum(LeadSourceEnum), nullable=False)
    status = Column(SQLEnum(LeadStatusEnum), default=LeadStatusEnum.NEW)
    priority = Column(SQLEnum(PriorityEnum), default=PriorityEnum.MEDIUM)
    
    # Financial
    estimated_value = Column(Float)
    estimated_close_date = Column(Date)
    probability = Column(Float, comment="Probability of closure (0-100)")
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey('user_master.id'))
    
    # Additional Info
    description = Column(Text)
    requirements = Column(JSON, comment="Product/service requirements")
    notes = Column(Text)
    
    # Relationships
    company = relationship("CompanyMaster", back_populates="leads")
    primary_contact = relationship("ContactMaster", back_populates="leads")
    assigned_user = relationship("UserMaster")
    opportunities = relationship("OpportunityMaster", back_populates="lead")