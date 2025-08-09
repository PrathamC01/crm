"""
Enhanced Lead model with opportunity conversion workflow and fixed foreign keys
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    Date,
    Integer,
    Boolean,
    Enum as SQLEnum,
    DECIMAL,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from .base import BaseModel


class LeadSource(str, Enum):
    DIRECT_MARKETING = "Direct Marketing"
    REFERRAL = "Referral"
    ADVERTISEMENT = "Advertisement"
    EVENT = "Event"
    OTHER = "Other"


class LeadStatus(str, Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"
    CONVERTED = "Converted"
    REJECTED = "Rejected"


class LeadPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class LeadSubType(str, Enum):
    PRE_TENDER = "Pre-Tender"
    POST_TENDER = "Post-Tender"


class TenderSubType(str, Enum):
    GEM_TENDER = "GeM Tender"
    LIMITED_TENDER = "Limited Tender"
    OPEN_TENDER = "Open Tender"
    SINGLE_TENDER = "Single Tender"


class SubmissionType(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    BOTH = "Both"


class ReviewStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Lead(BaseModel):
    __tablename__ = "leads"

    # Basic Lead Information
    project_title = Column(String(255), nullable=False)
    lead_source = Column(SQLEnum(LeadSource), nullable=False)
    lead_sub_type = Column(SQLEnum(LeadSubType), nullable=False)
    tender_sub_type = Column(SQLEnum(TenderSubType), nullable=False)
    products_services = Column(JSON)  # Array of selected products/services
    
    # Company Details
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    sub_business_type = Column(String(100))  # Upgrade, Downgrade, AMC
    
    # End Customer Details
    end_customer_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    end_customer_region = Column(String(50))  # North, South, East, West, Central
    
    # Partner Details
    partner_involved = Column(Boolean, default=False)
    partners_data = Column(JSON)  # Array of partner information
    
    # Tender Details
    tender_fee = Column(DECIMAL(15, 2))
    currency = Column(String(3), default="INR")
    submission_type = Column(SQLEnum(SubmissionType))
    tender_authority = Column(String(255))
    tender_for = Column(Text)
    
    # EMD Details
    emd_required = Column(Boolean, default=False)
    emd_amount = Column(DECIMAL(15, 2))
    emd_currency = Column(String(3), default="INR")
    
    # BG Details
    bg_required = Column(Boolean, default=False)
    bg_amount = Column(DECIMAL(15, 2))
    bg_currency = Column(String(3), default="INR")
    
    # Important Dates
    important_dates = Column(JSON)  # Array of date objects
    
    # Clauses
    clauses = Column(JSON)  # Array of clause objects
    
    # Revenue and Conversion
    expected_revenue = Column(DECIMAL(15, 2), nullable=False)
    revenue_currency = Column(String(3), default="INR")
    convert_to_opportunity_date = Column(Date)
    
    # Competitors
    competitors = Column(JSON)  # Array of competitor objects
    
    # Documents
    documents = Column(JSON)  # Array of document objects
    
    # Lead Management
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    priority = Column(SQLEnum(LeadPriority), default=LeadPriority.MEDIUM)
    qualification_notes = Column(Text)
    lead_score = Column(Integer, default=0)
    
    # Sales person assignment
    sales_person_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Contact Information (stored as JSON for flexibility)
    contacts = Column(JSON)  # Array of contact objects
    
    # Conversion Workflow Fields
    ready_for_conversion = Column(Boolean, default=False)
    conversion_requested = Column(Boolean, default=False)
    conversion_request_date = Column(DateTime)
    conversion_requested_by = Column(Integer, ForeignKey("users.id"))
    
    # Review and Approval Fields
    reviewed = Column(Boolean, default=False)
    review_status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    review_date = Column(DateTime)
    review_comments = Column(Text)
    
    # Conversion Tracking
    converted = Column(Boolean, default=False)
    # Remove circular dependency - will be updated when opportunity is created
    converted_to_opportunity_id = Column(String(10))  # Will store POT-ID instead of FK
    conversion_date = Column(DateTime)
    conversion_notes = Column(Text)

    # Relationships
    company = relationship("Company", foreign_keys=[company_id], back_populates="leads")
    end_customer = relationship("Company", foreign_keys=[end_customer_id])
    
    sales_person = relationship(
        "User", 
        foreign_keys=[sales_person_id],
        back_populates="leads_assigned"
    )
    conversion_requester = relationship(
        "User", 
        foreign_keys=[conversion_requested_by]
    )
    reviewer = relationship(
        "User", 
        foreign_keys=[reviewed_by]
    )
    
    creator = relationship(
        "User",
        foreign_keys="Lead.created_by",
        back_populates="leads_created",
        overlaps="conversion_requester,reviewer"
    )
    updater = relationship(
        "User",
        foreign_keys="Lead.updated_by",
        back_populates="leads_updated",
    )
    
    # One-to-many with opportunities (a lead can have multiple opportunities over time)
    opportunities = relationship("Opportunity", back_populates="lead")

    @property
    def company_name(self):
        return self.company.name if self.company else None

    @property
    def end_customer_name(self):
        return self.end_customer.name if self.end_customer else None

    @property
    def creator_name(self):
        return self.creator.full_name if self.creator and hasattr(self.creator, 'full_name') else (self.creator.name if self.creator else None)

    @property
    def sales_person_name(self):
        return self.sales_person.full_name if self.sales_person and hasattr(self.sales_person, 'full_name') else (self.sales_person.name if self.sales_person else None)

    @property
    def conversion_requester_name(self):
        return self.conversion_requester.full_name if self.conversion_requester and hasattr(self.conversion_requester, 'full_name') else (self.conversion_requester.name if self.conversion_requester else None)

    @property
    def reviewer_name(self):
        return self.reviewer.full_name if self.reviewer and hasattr(self.reviewer, 'full_name') else (self.reviewer.name if self.reviewer else None)

    @property
    def can_request_conversion(self):
        """Check if lead can request conversion"""
        return (
            self.status == LeadStatus.QUALIFIED and 
            not self.converted and 
            not self.conversion_requested
        )

    @property
    def can_convert_to_opportunity(self):
        """Check if lead can be converted to opportunity"""
        return (
            self.status == LeadStatus.QUALIFIED and
            not self.converted and
            self.reviewed and
            self.review_status == ReviewStatus.APPROVED
        )

    @property
    def needs_admin_review(self):
        """Check if lead needs admin review before conversion"""
        return (
            self.status == LeadStatus.QUALIFIED and
            self.conversion_requested and
            not self.reviewed
        )

    def __repr__(self):
        return f"<Lead(project_title={self.project_title}, status={self.status}, company={self.company_name})>"