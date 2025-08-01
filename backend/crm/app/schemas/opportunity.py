"""
Opportunity related schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from ..utils.validators import validate_amount_with_justification, validate_opportunity_stage_transition

class OpportunityStage(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"

class OpportunityStatus(str, Enum):
    OPEN = "Open"
    WON = "Won"
    LOST = "Lost"
    DROPPED = "Dropped"

class OpportunityBase(BaseModel):
    lead_id: str
    company_id: str
    contact_id: str
    name: str
    stage: OpportunityStage = OpportunityStage.L1
    amount: Optional[Decimal] = None
    scoring: int = 0
    bom_id: Optional[str] = None
    costing: Optional[Decimal] = None
    status: OpportunityStatus = OpportunityStatus.OPEN
    justification: Optional[str] = None
    close_date: Optional[date] = None
    probability: int = 10
    notes: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Opportunity name must be at least 3 characters long')
        return v.strip()

    @validator('scoring')
    def validate_scoring(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Scoring must be between 0 and 100')
        return v

    @validator('probability')
    def validate_probability(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Probability must be between 0 and 100')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

    @validator('costing')
    def validate_costing(cls, v):
        if v is not None and v < 0:
            raise ValueError('Costing cannot be negative')
        return v

    @validator('justification', always=True)
    def validate_amount_justification(cls, v, values):
        if 'amount' in values and values['amount']:
            amount_float = float(values['amount'])
            is_valid, error_msg = validate_amount_with_justification(amount_float, v)
            if not is_valid:
                raise ValueError(error_msg)
        return v

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    lead_id: Optional[str] = None
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    name: Optional[str] = None
    stage: Optional[OpportunityStage] = None
    amount: Optional[Decimal] = None
    scoring: Optional[int] = None
    bom_id: Optional[str] = None
    costing: Optional[Decimal] = None
    status: Optional[OpportunityStatus] = None
    justification: Optional[str] = None
    close_date: Optional[date] = None
    probability: Optional[int] = None
    notes: Optional[str] = None

    @validator('scoring')
    def validate_scoring(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Scoring must be between 0 and 100')
        return v

    @validator('probability')
    def validate_probability(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Probability must be between 0 and 100')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

class OpportunityResponse(OpportunityBase):
    id: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    lead_source: Optional[str] = None
    created_by_name: Optional[str] = None
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True

class OpportunityListResponse(BaseModel):
    opportunities: list[OpportunityResponse]
    total: int
    skip: int
    limit: int

class OpportunityStageUpdate(BaseModel):
    """Schema for updating opportunity stage"""
    stage: OpportunityStage
    notes: Optional[str] = None
    probability: Optional[int] = None

    @validator('probability')
    def validate_probability(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Probability must be between 0 and 100')
        return v

class OpportunityCloseRequest(BaseModel):
    """Schema for closing opportunity"""
    status: Literal["Won", "Lost", "Dropped"]
    close_date: date
    notes: Optional[str] = None

class OpportunityPipelineSummary(BaseModel):
    """Opportunity pipeline summary"""
    total_opportunities: int
    total_value: Decimal
    avg_scoring: Optional[float] = None
    closing_stage_count: int
    stage_breakdown: list[dict]

class OpportunityMetrics(BaseModel):
    """Opportunity metrics and analytics"""
    total_opportunities: int
    won_opportunities: int
    lost_opportunities: int
    win_rate: float
    avg_deal_size: Optional[Decimal] = None
    avg_sales_cycle: Optional[float] = None  # in days
    pipeline_value: Decimal
    forecasted_revenue: Decimal