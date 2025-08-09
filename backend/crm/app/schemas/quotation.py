"""
Quotation schemas for opportunity quotations
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class QuotationStatusEnum(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REVISED = "Revised"


class LineItem(BaseModel):
    item_id: Optional[str] = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    tax_rate: Optional[Decimal] = Decimal('0')
    discount_rate: Optional[Decimal] = Decimal('0')

    class Config:
        from_attributes = True


class QuotationBase(BaseModel):
    quotation_name: str
    quotation_date: date
    valid_until: Optional[date] = None
    amount: Decimal
    currency: str = "INR"
    description: Optional[str] = None
    terms_conditions: Optional[str] = None
    
    # Pricing details
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    tax_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    
    # Line items
    line_items: Optional[List[LineItem]] = []
    
    # File attachments
    attachments: Optional[List[Dict[str, Any]]] = []

    @validator('amount', 'subtotal', 'tax_amount', 'discount_amount', 'total_amount')
    def validate_amounts(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount values must be non-negative')
        return v

    @validator('tax_percentage', 'discount_percentage')
    def validate_percentages(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Percentage values must be between 0 and 100')
        return v

    class Config:
        from_attributes = True


class QuotationCreate(QuotationBase):
    pass


class QuotationUpdate(BaseModel):
    quotation_name: Optional[str] = None
    quotation_date: Optional[date] = None
    valid_until: Optional[date] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    terms_conditions: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    tax_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    line_items: Optional[List[LineItem]] = None
    attachments: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class QuotationResponse(BaseModel):
    id: int
    opportunity_id: int
    quotation_id: str
    quotation_name: str
    quotation_date: date
    valid_until: Optional[date] = None
    amount: Decimal
    currency: str = "INR"
    status: QuotationStatusEnum
    description: Optional[str] = None
    terms_conditions: Optional[str] = None
    
    # Pricing details
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    tax_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    
    # Line items and attachments
    line_items: Optional[List[Dict[str, Any]]] = []
    attachments: Optional[List[Dict[str, Any]]] = []
    
    # File management
    quotation_file_path: Optional[str] = None
    
    # Customer information
    customer_info: Optional[Dict[str, Any]] = {}
    
    # Workflow tracking
    submitted_date: Optional[datetime] = None
    submitted_by: Optional[int] = None
    approved_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    
    # Revision management
    parent_quotation_id: Optional[int] = None
    revision_number: int = 1
    revision_notes: Optional[str] = None
    
    # Follow-up
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None
    
    # Timestamps
    created_on: datetime
    updated_on: datetime
    
    # User relationships (names for display)
    submitted_by_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    creator_name: Optional[str] = None
    
    # Computed properties
    is_editable: Optional[bool] = None
    can_submit: Optional[bool] = None
    can_approve: Optional[bool] = None
    display_amount: Optional[str] = None
    
    # Related opportunity info (basic to avoid circular refs)
    opportunity_name: Optional[str] = None
    opportunity_pot_id: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class QuotationListItem(BaseModel):
    id: int
    quotation_id: str
    quotation_name: str
    quotation_date: date
    amount: Decimal
    currency: str = "INR"
    status: QuotationStatusEnum
    opportunity_id: int
    opportunity_name: Optional[str] = None
    opportunity_pot_id: Optional[str] = None
    submitted_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    revision_number: int = 1
    created_on: datetime
    display_amount: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class QuotationListResponse(BaseModel):
    quotations: List[QuotationListItem]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class QuotationStats(BaseModel):
    total_quotations: int = 0
    status_breakdown: Dict[str, int] = {}
    total_value: Decimal = Decimal('0')
    approval_rate: float = 0.0

    class Config:
        from_attributes = True


class QuotationSubmissionRequest(BaseModel):
    submission_notes: Optional[str] = None

    class Config:
        from_attributes = True


class QuotationApprovalRequest(BaseModel):
    approval_notes: Optional[str] = None

    class Config:
        from_attributes = True


class QuotationRejectionRequest(BaseModel):
    rejection_reason: str

    class Config:
        from_attributes = True


class QuotationRevisionRequest(BaseModel):
    revision_notes: Optional[str] = None

    class Config:
        from_attributes = True