"""
Enhanced Company schemas for Swayatta 4.0 with comprehensive validation
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from ..utils.validators import (
    validate_gst_number,
    validate_pan_number,
    sanitize_gst_number,
    sanitize_pan_number,
)

class CompanyType(str, Enum):
    DOMESTIC_GST = "DOMESTIC_GST"
    DOMESTIC_NONGST = "DOMESTIC_NONGST"
    NGO = "NGO"
    OVERSEAS = "OVERSEAS"

class ApprovalStage(str, Enum):
    DRAFT = "DRAFT"
    L1_PENDING = "L1_PENDING"
    ADMIN_PENDING = "ADMIN_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class CompanyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING_APPROVAL = "PENDING_APPROVAL"

class VerificationSource(str, Enum):
    GST = "GST"
    MCA = "MCA"
    PAN_NSDL = "PAN_NSDL"
    DIGILOCKER = "DIGILOCKER"
    GARTNER = "GARTNER"
    MANUAL = "MANUAL"

class IndustryType(str, Enum):
    BFSI = "BFSI"
    GOVERNMENT = "Government"
    IT_ITES = "IT_ITeS"
    MANUFACTURING = "Manufacturing"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    TELECOM = "Telecom"
    ENERGY_UTILITIES = "Energy_Utilities"
    RETAIL_CPG = "Retail_CPG"
    LOGISTICS = "Logistics"
    MEDIA_ENTERTAINMENT = "Media_Entertainment"

class CompanyBase(BaseModel):
    # Basic Information (All Required)
    name: str = Field(..., min_length=2, max_length=255, description="Company name")
    parent_company_name: Optional[str] = Field(None, description="Parent company name or 'Create New'")
    company_type: CompanyType = Field(..., description="Company type")
    industry: IndustryType = Field(..., description="Industry category")
    sub_industry: str = Field(..., min_length=1, max_length=100, description="Sub-industry")
    annual_revenue: float = Field(..., ge=0, description="Annual revenue in INR")
    
    # Identification & Compliance (Conditionally Required)
    gst_number: Optional[str] = Field(None, description="GST number for domestic GST companies")
    pan_number: Optional[str] = Field(None, description="PAN number")
    international_unique_id: Optional[str] = Field(None, description="International unique identifier")
    supporting_documents: List[str] = Field(..., min_items=1, description="Supporting document file paths")
    verification_source: VerificationSource = Field(..., description="Verification source")
    verification_date: datetime = Field(..., description="Verification date")
    verified_by: str = Field(..., description="Admin who verified")
    
    # Registered Address (All Required)
    address: str = Field(..., min_length=10, max_length=500, description="Complete registered address")
    country: str = Field(default="India", description="Country")
    state: str = Field(..., min_length=2, max_length=100, description="State")
    city: str = Field(..., min_length=2, max_length=100, description="City")
    pin_code: str = Field(..., pattern=r"^[0-9]{6}$", description="PIN code")
    
    # Hierarchy & Linkages (All Required)
    parent_child_mapping_confirmed: bool = Field(..., description="Parent-child mapping confirmation")
    linked_subsidiaries: List[str] = Field(default=["None"], description="Linked subsidiaries or 'None'")
    associated_channel_partner: Optional[str] = Field(None, description="Associated channel partner")
    
    # Optional fields
    website: Optional[str] = Field(None, description="Company website")
    description: Optional[str] = Field(None, description="Company description")

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters long")
        if not v.replace(" ", "").replace("&", "").replace(".", "").replace("-", "").isalnum():
            raise ValueError("Company name contains invalid characters")
        return v.strip()

    @validator("gst_number")
    def validate_gst(cls, v, values):
        if values.get("company_type") == CompanyType.DOMESTIC_GST:
            if not v:
                raise ValueError("GST number is required for Domestic GST companies")
            v = sanitize_gst_number(v)
            if not validate_gst_number(v):
                raise ValueError("Invalid GST number format. Expected: 22AAAAA0000A1Z5")
        return v

    @validator("pan_number")
    def validate_pan(cls, v, values):
        company_type = values.get("company_type")
        if company_type in [CompanyType.DOMESTIC_GST, CompanyType.DOMESTIC_NONGST]:
            if not v:
                raise ValueError("PAN number is required for domestic companies")
            v = sanitize_pan_number(v)
            if not validate_pan_number(v):
                raise ValueError("Invalid PAN number format. Expected: AAAAA0000A")
        return v

    @validator("international_unique_id")
    def validate_international_id(cls, v, values):
        if values.get("company_type") == CompanyType.OVERSEAS:
            if not v:
                raise ValueError("International unique identifier is required for overseas companies")
            if not v.replace("-", "").isalnum() or len(v) < 5 or len(v) > 20:
                raise ValueError("Invalid international unique identifier format")
        return v

    @validator("supporting_documents")
    def validate_documents(cls, v, values):
        if not v or len(v) < 1:
            raise ValueError("At least one supporting document is required")
        
        company_type = values.get("company_type")
        required_docs = {
            CompanyType.DOMESTIC_GST: ["GST_CERTIFICATE", "PAN_CARD"],
            CompanyType.DOMESTIC_NONGST: ["PAN_CARD", "MCA_CERTIFICATE"],
            CompanyType.NGO: ["NGO_REGISTRATION", "PAN_CARD"],
            CompanyType.OVERSEAS: ["INTERNATIONAL_ID", "INCORPORATION_CERTIFICATE"]
        }
        
        if company_type and company_type in required_docs:
            required = required_docs[company_type]
            provided_types = [doc.split("_")[0] for doc in v]  # Extract document types
            # This is a simplified check - in real implementation, check actual document types
        
        return v

    @validator("website")
    def validate_website(cls, v):
        if v and not v.startswith(("http://", "https://")):
            v = "https://" + v
        return v

    @validator("annual_revenue")
    def validate_revenue(cls, v):
        if v < 0:
            raise ValueError("Annual revenue cannot be negative")
        return v

class CompanyCreate(CompanyBase):
    """Schema for creating a new company"""
    pass

class CompanyUpdate(BaseModel):
    """Schema for updating company - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    parent_company_name: Optional[str] = None
    company_type: Optional[CompanyType] = None
    industry: Optional[IndustryType] = None
    sub_industry: Optional[str] = Field(None, min_length=1, max_length=100)
    annual_revenue: Optional[float] = Field(None, ge=0)
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    international_unique_id: Optional[str] = None
    supporting_documents: Optional[List[str]] = None
    verification_source: Optional[VerificationSource] = None
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    address: Optional[str] = Field(None, min_length=10, max_length=500)
    country: Optional[str] = None
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    pin_code: Optional[str] = Field(None, pattern=r"^[0-9]{6}$")
    parent_child_mapping_confirmed: Optional[bool] = None
    linked_subsidiaries: Optional[List[str]] = None
    associated_channel_partner: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    # Apply same validators as CompanyBase but for optional fields
    @validator("gst_number")
    def validate_gst(cls, v):
        if v:
            v = sanitize_gst_number(v)
            if not validate_gst_number(v):
                raise ValueError("Invalid GST number format")
        return v

    @validator("pan_number")
    def validate_pan(cls, v):
        if v:
            v = sanitize_pan_number(v)
            if not validate_pan_number(v):
                raise ValueError("Invalid PAN number format")
        return v

class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    parent_company_name: Optional[str] = None
    
    # Workflow fields
    approval_stage: ApprovalStage
    status: CompanyStatus
    change_log_id: Optional[str] = None  # Convert UUID to string
    
    # Auto-tagging
    is_high_revenue: bool = False
    tags: Optional[List[str]] = None
    
    # Approval tracking - convert user IDs to usernames
    l1_approved_by: Optional[str] = None
    l1_approved_date: Optional[datetime] = None
    admin_approved_by: Optional[str] = None
    admin_approved_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # SLA tracking
    sla_breach_date: Optional[datetime] = None
    escalation_level: int = 0

    class Config:
        from_attributes = True
        
    @classmethod
    def from_db_model(cls, company_model):
        """Create response from database model with proper conversions"""
        data = {
            **company_model.__dict__,
            'change_log_id': str(company_model.change_log_id) if company_model.change_log_id else None,
            'verified_by': getattr(company_model.verifier, 'username', None) if hasattr(company_model, 'verifier') and company_model.verifier else str(company_model.verified_by),
            'l1_approved_by': getattr(company_model.l1_approver, 'username', None) if hasattr(company_model, 'l1_approver') and company_model.l1_approver else None,
            'admin_approved_by': getattr(company_model.admin_approver, 'username', None) if hasattr(company_model, 'admin_approver') and company_model.admin_approver else None,
            'linked_subsidiaries': company_model.linked_subsidiaries or []
        }
        return cls(**data)

class CompanyListResponse(BaseModel):
    """Schema for company list response"""
    companies: List[CompanyResponse]
    total: int
    skip: int
    limit: Optional[int] = None

    class Config:
        from_attributes = True

class CompanyApprovalRequest(BaseModel):
    """Schema for approval actions"""
    action: str = Field(..., pattern="^(APPROVE|REJECT|SEND_BACK)$")
    reason: Optional[str] = Field(None, description="Reason for rejection or send back")
    checklist_items: Optional[List[str]] = Field(None, description="Completed checklist items")

class CompanyStats(BaseModel):
    """Schema for company statistics"""
    total_companies: int = 0
    active_companies: int = 0
    pending_approval: int = 0
    high_revenue_companies: int = 0
    companies_by_type: dict = {}
    companies_by_industry: dict = {}
    sla_breached: int = 0

    class Config:
        from_attributes = True

class DuplicateCheckResult(BaseModel):
    """Schema for duplicate check result"""
    is_duplicate: bool
    match_type: str = Field(..., pattern="^(EXACT|FUZZY|NONE)$")
    matched_companies: List[dict] = []
    similarity_score: Optional[float] = None
    can_override: bool = False
    requires_admin_approval: bool = False