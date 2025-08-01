"""
Lead related schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Literal
from datetime import datetime, date
from enum import Enum

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

class LeadBase(BaseModel):
    company_id: str
    location: Optional[str] = None
    lead_source: LeadSource
    sales_person_id: str
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    priority: LeadPriority = LeadPriority.MEDIUM
    expected_close_date: Optional[date] = None

    @validator('location')
    def validate_location(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Location must be at least 2 characters long')
        return v.strip() if v else v

    @validator('notes')
    def validate_notes(cls, v):
        if v and len(v.strip()) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v.strip() if v else v

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    company_id: Optional[str] = None
    location: Optional[str] = None
    lead_source: Optional[LeadSource] = None
    sales_person_id: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    priority: Optional[LeadPriority] = None
    expected_close_date: Optional[date] = None

    @validator('notes')
    def validate_notes(cls, v):
        if v and len(v.strip()) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v.strip() if v else v

class LeadResponse(LeadBase):
    id: str
    company_name: Optional[str] = None
    sales_person_name: Optional[str] = None
    last_activity_date: datetime
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    leads: list[LeadResponse]
    total: int
    skip: int
    limit: int

class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status with notes"""
    status: LeadStatus
    notes: Optional[str] = None

    @validator('notes')
    def validate_notes(cls, v):
        if v and len(v.strip()) > 1000:
            raise ValueError('Notes cannot exceed 1000 characters')
        return v.strip() if v else v

class LeadConversion(BaseModel):
    """Schema for converting lead to opportunity"""
    contact_id: str  # Must be a Decision Maker
    opportunity_name: str
    amount: Optional[float] = None
    justification: Optional[str] = None
    stage: str = "L1"
    notes: Optional[str] = None

    @validator('opportunity_name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Opportunity name must be at least 3 characters long')
        return v.strip()

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

class LeadSummary(BaseModel):
    """Lead summary statistics"""
    total_leads: int
    new_leads: int
    qualified_leads: int
    closed_won: int
    closed_lost: int
    dropped: int
    conversion_rate: float
    avg_days_to_close: Optional[float] = None