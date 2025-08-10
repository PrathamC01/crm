"""
Leads Module Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

from .common import BaseResponseSchema

# Enums
class LeadStatusEnum(str, Enum):
    NEW = "New"
    ACTIVE = "Active"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"
    CONVERTED = "Converted"
    REJECTED = "Rejected"

class LeadSourceEnum(str, Enum):
    REFERRAL = "Referral"
    DIRECT_MARKETING = "Direct Marketing"
    ADVERTISEMENT = "Advertisement"
    WEBSITE = "Website"
    COLD_CALLING = "Cold Calling"
    TRADE_SHOW = "Trade Show"
    SOCIAL_MEDIA = "Social Media"

class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

# Contact Schemas
class ContactCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    designation: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone_number: Optional[str] = Field(None, max_length=20)
    company_id: int
    decision_maker: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    designation: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone_number: Optional[str] = Field(None, max_length=20)
    decision_maker: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class ContactResponse(BaseResponseSchema):
    full_name: str
    designation: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_id: int
    company_name: str
    decision_maker: Optional[str] = None
    notes: Optional[str] = None

# Company Schemas
class CompanyCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    industry_id: Optional[int] = None
    gst_number: Optional[str] = Field(None, max_length=15)
    pan_number: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    website: Optional[str] = Field(None, max_length=255)
    annual_revenue: Optional[float] = Field(None, ge=0)
    employee_count: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry_id: Optional[int] = None
    gst_number: Optional[str] = Field(None, max_length=15)
    pan_number: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    website: Optional[str] = Field(None, max_length=255)
    annual_revenue: Optional[float] = Field(None, ge=0)
    employee_count: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class CompanyResponse(BaseResponseSchema):
    company_name: str
    industry_id: Optional[int] = None
    industry_name: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city_id: Optional[int] = None
    city_name: Optional[str] = None
    state_id: Optional[int] = None
    state_name: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    description: Optional[str] = None
    contacts: List[ContactResponse] = []

# Lead Schemas
class LeadCreate(BaseModel):
    lead_title: str = Field(..., min_length=1, max_length=200)
    company_id: int
    primary_contact_id: Optional[int] = None
    lead_source: LeadSourceEnum
    status: LeadStatusEnum = LeadStatusEnum.NEW
    priority: PriorityEnum = PriorityEnum.MEDIUM
    estimated_value: Optional[float] = Field(None, ge=0)
    estimated_close_date: Optional[date] = None
    probability: Optional[float] = Field(None, ge=0, le=100)
    assigned_to: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    lead_title: Optional[str] = Field(None, min_length=1, max_length=200)
    primary_contact_id: Optional[int] = None
    status: Optional[LeadStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    estimated_value: Optional[float] = Field(None, ge=0)
    estimated_close_date: Optional[date] = None
    probability: Optional[float] = Field(None, ge=0, le=100)
    assigned_to: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    status: LeadStatusEnum
    notes: Optional[str] = None

class LeadAssignment(BaseModel):
    assigned_to: int
    notes: Optional[str] = None

class LeadConversion(BaseModel):
    opportunity_title: str = Field(..., min_length=1, max_length=200)
    estimated_value: Optional[float] = Field(None, ge=0)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None

class LeadResponse(BaseResponseSchema):
    lead_title: str
    company_id: int
    company_name: str
    primary_contact_id: Optional[int] = None
    primary_contact_name: Optional[str] = None
    lead_source: str
    status: str
    priority: str
    estimated_value: Optional[float] = None
    estimated_close_date: Optional[date] = None
    probability: Optional[float] = None
    assigned_to: Optional[int] = None
    assigned_user_name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None