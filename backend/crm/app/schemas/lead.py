"""
Enhanced Lead schemas with opportunity conversion workflow
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


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


class ContactBase(BaseModel):
    designation: Optional[str] = None
    salutation: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    primary_phone: str
    decision_maker: bool = False
    decision_maker_percentage: int = 0
    comments: Optional[str] = None


class PartnerBase(BaseModel):
    partner_type: str  # Channel, Reseller, Distributor
    partner_name: str
    billing_type: str  # Client Billing, Partner Billing
    payment_terms: Optional[str] = None
    engagement_type: str  # ORC, NRC, AMC
    expected_orc: Optional[Decimal] = None


class ImportantDateBase(BaseModel):
    label: str
    key: str
    value: Optional[date] = None


class ClauseBase(BaseModel):
    clause_type: str
    criteria_description: str


class CompetitorBase(BaseModel):
    name: str
    description: Optional[str] = None


class DocumentBase(BaseModel):
    document_type: str
    quotation_name: str
    file_path: str
    description: Optional[str] = None


class LeadBase(BaseModel):
    # Basic Lead Information
    project_title: str
    lead_source: LeadSource
    lead_sub_type: LeadSubType
    tender_sub_type: TenderSubType
    products_services: List[str] = []
    
    # Company Details
    company_id: int
    sub_business_type: Optional[str] = None
    
    # End Customer Details
    end_customer_id: int
    end_customer_region: Optional[str] = None
    
    # Partner Details
    partner_involved: bool = False
    partners_data: List[PartnerBase] = []
    
    # Tender Details
    tender_fee: Optional[Decimal] = None
    currency: str = "INR"
    submission_type: Optional[SubmissionType] = None
    tender_authority: Optional[str] = None
    tender_for: Optional[str] = None
    
    # EMD Details
    emd_required: bool = False
    emd_amount: Optional[Decimal] = None
    emd_currency: str = "INR"
    
    # BG Details
    bg_required: bool = False
    bg_amount: Optional[Decimal] = None
    bg_currency: str = "INR"
    
    # Important Dates
    important_dates: List[ImportantDateBase] = []
    
    # Clauses
    clauses: List[ClauseBase] = []
    
    # Revenue and Conversion
    expected_revenue: Decimal
    revenue_currency: str = "INR"
    convert_to_opportunity_date: Optional[date] = None
    
    # Competitors
    competitors: List[CompetitorBase] = []
    
    # Documents
    documents: List[DocumentBase] = []
    
    # Lead Management
    status: LeadStatus = LeadStatus.NEW
    priority: LeadPriority = LeadPriority.MEDIUM
    qualification_notes: Optional[str] = None
    lead_score: int = 0
    
    # Contact Information
    contacts: List[ContactBase] = []

    @validator("project_title")
    def validate_project_title(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Project title must be at least 3 characters long")
        return v.strip()

    @validator("expected_revenue")
    def validate_expected_revenue(cls, v):
        if v <= 0:
            raise ValueError("Expected revenue must be greater than 0")
        return v

    @validator("contacts")
    def validate_contacts(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one contact is required")
        return v


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    project_title: Optional[str] = None
    lead_source: Optional[LeadSource] = None
    lead_sub_type: Optional[LeadSubType] = None
    tender_sub_type: Optional[TenderSubType] = None
    products_services: Optional[List[str]] = None
    company_id: Optional[int] = None
    sub_business_type: Optional[str] = None
    end_customer_id: Optional[int] = None
    end_customer_region: Optional[str] = None
    partner_involved: Optional[bool] = None
    partners_data: Optional[List[PartnerBase]] = None
    tender_fee: Optional[Decimal] = None
    currency: Optional[str] = None
    submission_type: Optional[SubmissionType] = None
    tender_authority: Optional[str] = None
    tender_for: Optional[str] = None
    emd_required: Optional[bool] = None
    emd_amount: Optional[Decimal] = None
    emd_currency: Optional[str] = None
    bg_required: Optional[bool] = None
    bg_amount: Optional[Decimal] = None
    bg_currency: Optional[str] = None
    important_dates: Optional[List[ImportantDateBase]] = None
    clauses: Optional[List[ClauseBase]] = None
    expected_revenue: Optional[Decimal] = None
    revenue_currency: Optional[str] = None
    convert_to_opportunity_date: Optional[date] = None
    competitors: Optional[List[CompetitorBase]] = None
    documents: Optional[List[DocumentBase]] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    qualification_notes: Optional[str] = None
    lead_score: Optional[int] = None
    contacts: Optional[List[ContactBase]] = None


class LeadResponse(LeadBase):
    id: int
    company_name: Optional[str] = None
    end_customer_name: Optional[str] = None
    creator_name: Optional[str] = None
    conversion_requester_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    
    # Conversion Workflow Fields
    ready_for_conversion: bool = False
    conversion_requested: bool = False
    conversion_request_date: Optional[datetime] = None
    
    # Review and Approval Fields
    reviewed: bool = False
    review_status: ReviewStatus = ReviewStatus.PENDING
    review_date: Optional[datetime] = None
    review_comments: Optional[str] = None
    
    # Conversion Tracking
    converted: bool = False
    converted_to_opportunity_id: Optional[int] = None
    conversion_date: Optional[datetime] = None
    conversion_notes: Optional[str] = None
    
    # Properties
    can_request_conversion: bool = False
    can_convert_to_opportunity: bool = False
    needs_admin_review: bool = False
    
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True


class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    skip: int
    limit: int


# Conversion Workflow Schemas
class ConversionRequestSchema(BaseModel):
    notes: Optional[str] = None


class ReviewDecisionSchema(BaseModel):
    decision: ReviewStatus  # Approved or Rejected
    comments: str
    
    @validator("comments")
    def validate_comments(cls, v, values):
        if values.get("decision") == ReviewStatus.REJECTED and (not v or len(v.strip()) == 0):
            raise ValueError("Comments are required when rejecting a conversion request")
        return v


class ConvertToOpportunitySchema(BaseModel):
    opportunity_name: Optional[str] = None
    notes: Optional[str] = None


class LeadStatsResponse(BaseModel):
    total: int = 0
    new: int = 0
    contacted: int = 0
    qualified: int = 0
    converted: int = 0
    pending_review: int = 0
    approved_for_conversion: int = 0
    total_value: Decimal = 0