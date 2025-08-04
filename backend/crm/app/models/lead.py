"""
SQLAlchemy Lead model
"""
from sqlalchemy import Column, String, Text, ForeignKey, Date, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from .base import BaseModel

class LeadSource(str, Enum):
    WEB = "Web"
    PARTNER = "Partner"
    CAMPAIGN = "Campaign"
    REFERRAL = "Referral"
    COLD_CALL = "Cold Call"
    EVENT = "Event"

class LeadStatus(str, Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL = "Proposal"
    NEGOTIATION = "Negotiation"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"
    DROPPED = "Dropped"

class LeadPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class Lead(BaseModel):
    __tablename__ = 'leads'
    
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    location = Column(String(255))
    lead_source = Column(SQLEnum(LeadSource), nullable=False)
    sales_person_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    notes = Column(Text)
    priority = Column(SQLEnum(LeadPriority), default=LeadPriority.MEDIUM)
    expected_close_date = Column(Date)
    last_activity_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    company = relationship("Company", back_populates="leads")
    sales_person = relationship("User", foreign_keys="Lead.sales_person_id", back_populates="leads_assigned")
    creator = relationship("User", foreign_keys="Lead.created_by", back_populates="leads_created")
    updater = relationship("User", foreign_keys="Lead.updated_by", back_populates="leads_updated")
    
    # Opportunities created from this lead
    opportunities = relationship("Opportunity", back_populates="lead")
    
    def __repr__(self):
        return f"<Lead(id={self.id}, company={self.company.name if self.company else 'N/A'}, status={self.status})>"