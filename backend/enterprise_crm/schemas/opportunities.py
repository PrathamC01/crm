"""
Opportunities Module Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from .common import BaseResponseSchema

# Enums
class OpportunityStatusEnum(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PROPOSAL_SENT = "Proposal Sent"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    ON_HOLD = "On Hold"

class QuotationStatusEnum(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"

# Opportunity Schemas
class OpportunityCreate(BaseModel):
    opportunity_title: str = Field(..., min_length=1, max_length=200)
    lead_id: Optional[int] = None
    company_id: int
    status: OpportunityStatusEnum = OpportunityStatusEnum.OPEN
    stage: Optional[str] = Field(None, max_length=50)
    estimated_value: Optional[float] = Field(None, ge=0)
    probability: Optional[float] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    assigned_to: Optional[int] = None
    sales_team: Optional[List[int]] = None
    description: Optional[str] = None
    competitor_info: Optional[Dict[str, Any]] = None

class OpportunityUpdate(BaseModel):
    opportunity_title: Optional[str] = Field(None, min_length=1, max_length=200)
    stage: Optional[str] = Field(None, max_length=50)
    estimated_value: Optional[float] = Field(None, ge=0)
    final_value: Optional[float] = Field(None, ge=0)
    probability: Optional[float] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    assigned_to: Optional[int] = None
    sales_team: Optional[List[int]] = None
    description: Optional[str] = None
    win_loss_reason: Optional[str] = None
    competitor_info: Optional[Dict[str, Any]] = None

class OpportunityStatusUpdate(BaseModel):
    status: OpportunityStatusEnum
    win_loss_reason: Optional[str] = None
    actual_close_date: Optional[date] = None
    final_value: Optional[float] = Field(None, ge=0)

class OpportunityStageUpdate(BaseModel):
    stage: str = Field(..., max_length=50)
    notes: Optional[str] = None

class OpportunityResponse(BaseResponseSchema):
    opportunity_title: str
    opportunity_id: str
    lead_id: Optional[int] = None
    company_id: int
    company_name: str
    status: str
    stage: Optional[str] = None
    estimated_value: Optional[float] = None
    final_value: Optional[float] = None
    probability: Optional[float] = None
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    assigned_to: Optional[int] = None
    assigned_user_name: Optional[str] = None
    sales_team: Optional[List[int]] = None
    description: Optional[str] = None
    win_loss_reason: Optional[str] = None
    competitor_info: Optional[Dict[str, Any]] = None

# Quotation Schemas
class QuotationCreate(BaseModel):
    price_list_id: int
    version: str = Field(default="1.0", max_length=10)
    quotation_date: date = Field(default_factory=date.today)
    valid_until: date
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    additional_terms: Optional[str] = None

class QuotationUpdate(BaseModel):
    version: Optional[str] = Field(None, max_length=10)
    valid_until: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    additional_terms: Optional[str] = None

class QuotationResponse(BaseResponseSchema):
    quotation_number: str
    opportunity_id: int
    opportunity_title: str
    price_list_id: int
    price_list_name: str
    version: str
    status: str
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    quotation_date: date
    valid_until: date
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    additional_terms: Optional[str] = None
    prepared_by: int
    prepared_by_name: str
    approved_by: Optional[int] = None
    approved_by_name: Optional[str] = None

# Quotation Line Item Schemas
class QuotationLineItemCreate(BaseModel):
    product_id: int
    uom_id: int
    quantity: float = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Optional[float] = Field(0, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(0, ge=0)
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None

    @validator('discount_amount', always=True)
    def calculate_discount_amount(cls, v, values):
        if 'discount_percent' in values and 'unit_price' in values and 'quantity' in values:
            if values['discount_percent'] > 0:
                return (values['unit_price'] * values['quantity'] * values['discount_percent']) / 100
        return v or 0

class QuotationLineItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None

class QuotationLineItemResponse(BaseResponseSchema):
    quotation_id: int
    product_id: int
    product_name: str
    product_sku: str
    uom_id: int
    uom_name: str
    quantity: float
    unit_price: Decimal
    discount_percent: float
    discount_amount: Decimal
    line_total: Decimal
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None