"""
Enhanced Opportunity schemas with Lead-based creation workflow
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class OpportunityStageEnum(str, Enum):
    L1_PROSPECT = "L1_Prospect"
    L2_NEED_ANALYSIS = "L2_Need_Analysis"
    L3_PROPOSAL = "L3_Proposal"
    WIN = "Win"
    LOSS = "Loss"


class OpportunityStatusEnum(str, Enum):
    OPEN = "Open"
    WON = "Won"
    LOST = "Lost"
    CONVERTED_FROM_LEAD = "Converted_From_Lead"


class SalesStageEnum(str, Enum):
    L1_PROSPECT = "L1_Prospect"
    L2_NEED_ANALYSIS = "L2_Need_Analysis"
    L3_PROPOSAL = "L3_Proposal"
    WIN = "Win"
    LOSS = "Loss"


class StageStatusEnum(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    SKIPPED = "Skipped"


# Sales Process Schemas
class SalesProcessBase(BaseModel):
    stage: SalesStageEnum
    status: StageStatusEnum
    stage_completion_date: Optional[date] = None
    comments: Optional[str] = None
    notes: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = []
    stage_data: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True
        use_enum_values = True


class SalesProcessCreate(SalesProcessBase):
    opportunity_id: int


class SalesProcessUpdate(BaseModel):
    status: StageStatusEnum
    completion_date: Optional[date] = None
    comments: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class SalesProcessResponse(SalesProcessBase):
    id: int
    opportunity_id: int
    stage_order: int
    completed_by: Optional[int] = None
    completion_notes: Optional[str] = None
    created_on: datetime
    updated_on: datetime
    
    # Computed properties
    stage_display_name: Optional[str] = None
    can_proceed_to_next: Optional[bool] = None
    is_final_stage: Optional[bool] = None

    class Config:
        from_attributes = True
        use_enum_values = True


# Opportunity Schemas  
class OpportunityBase(BaseModel):
    name: str
    amount: Optional[Decimal] = None
    currency: Optional[str] = "INR"
    probability: Optional[int] = 10
    close_date: Optional[date] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class OpportunityCreate(OpportunityBase):
    """
    Note: Direct opportunity creation is not allowed.
    Opportunities can only be created by converting leads.
    This schema is kept for potential internal use only.
    """
    lead_id: int  # Required - enforces Lead-based creation

    @validator('lead_id')
    def lead_id_required(cls, v):
        if not v:
            raise ValueError('Opportunities can only be created by converting a Lead')
        return v


class OpportunityResponse(BaseModel):
    id: int
    pot_id: str
    lead_id: int
    name: str
    company_id: int
    contact_id: Optional[int] = None
    current_stage: OpportunityStageEnum
    status: OpportunityStatusEnum
    amount: Optional[Decimal] = None
    currency: str = "INR"
    probability: int = 10
    close_date: Optional[date] = None
    conversion_date: datetime
    
    # Lead data preservation
    lead_data: Optional[Dict[str, Any]] = {}
    partner_involved: bool = False
    partners_data: Optional[List[Dict[str, Any]]] = []
    products_services: Optional[List[str]] = []
    tender_details: Optional[Dict[str, Any]] = {}
    competitors: Optional[List[Dict[str, Any]]] = []
    documents: Optional[List[Dict[str, Any]]] = []
    notes: Optional[str] = None
    
    # Conversion tracking
    converted_by: int
    approval_status: str = "Approved"
    approved_by: Optional[int] = None
    approved_date: Optional[datetime] = None
    
    # Sales process tracking
    l1_completed: bool = False
    l1_completion_date: Optional[date] = None
    l2_completed: bool = False
    l2_completion_date: Optional[date] = None
    l3_completed: bool = False
    l3_completion_date: Optional[date] = None
    
    # Final outcome
    won_date: Optional[date] = None
    lost_date: Optional[date] = None
    lost_reason: Optional[str] = None
    win_reason: Optional[str] = None
    
    # Timestamps
    created_on: datetime
    updated_on: datetime
    
    # Relationships (basic info only to avoid circular references)
    company_name: Optional[str] = None
    lead_name: Optional[str] = None
    contact_name: Optional[str] = None
    converted_by_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    
    # Computed properties
    stage_percentage: Optional[int] = None
    can_create_quotations: Optional[bool] = None
    quotations_count: Optional[int] = None
    active_quotations_count: Optional[int] = None
    
    # Related data
    sales_processes: Optional[List[SalesProcessResponse]] = []

    class Config:
        from_attributes = True
        use_enum_values = True


class OpportunityListItem(BaseModel):
    id: int
    pot_id: str
    name: str
    company_name: Optional[str] = None
    current_stage: OpportunityStageEnum
    status: OpportunityStatusEnum
    amount: Optional[Decimal] = None
    currency: str = "INR"
    probability: int = 10
    close_date: Optional[date] = None
    conversion_date: datetime
    converted_by_name: Optional[str] = None
    stage_percentage: Optional[int] = None
    quotations_count: Optional[int] = None
    created_on: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class OpportunityListResponse(BaseModel):
    opportunities: List[OpportunityListItem]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class OpportunityStats(BaseModel):
    total_opportunities: int = 0
    won_opportunities: int = 0
    lost_opportunities: int = 0
    open_opportunities: int = 0
    stage_breakdown: Dict[str, int] = {}
    total_value: Decimal = Decimal('0')
    win_rate: float = 0.0

    class Config:
        from_attributes = True


class LeadConversionEligibility(BaseModel):
    can_convert: bool
    requires_approval: bool = False
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class ConvertLeadRequest(BaseModel):
    conversion_notes: Optional[str] = None

    class Config:
        from_attributes = True