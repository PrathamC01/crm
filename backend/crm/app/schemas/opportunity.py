"""
Opportunity related schemas with enhanced stage-specific fields
"""

from pydantic import BaseModel, validator
from typing import Optional, Literal, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from ..utils.validators import (
    validate_amount_with_justification,
    validate_opportunity_stage_transition,
)


class OpportunityStage(str, Enum):
    L1_PROSPECT = "L1_Prospect"
    L1_QUALIFICATION = "L1_Qualification"
    L2_NEED_ANALYSIS = "L2_Need_Analysis"
    L3_PROPOSAL = "L3_Proposal"
    L4_NEGOTIATION = "L4_Negotiation"
    L5_WON = "L5_Won"
    L6_LOST = "L6_Lost"
    L7_DROPPED = "L7_Dropped"


class OpportunityStatus(str, Enum):
    OPEN = "Open"
    WON = "Won"
    LOST = "Lost"
    DROPPED = "Dropped"


class QualificationStatus(str, Enum):
    QUALIFIED = "Qualified"
    NOT_NOW = "Not_Now"
    DISQUALIFIED = "Disqualified"


class GoNoGoStatus(str, Enum):
    GO = "Go"
    NO_GO = "No_Go"
    PENDING = "Pending"


class ProposalStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class QuotationStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REVISION_REQUIRED = "Revision_Required"


class OpportunityBase(BaseModel):
    lead_id: Optional[int] = None
    company_id: int
    contact_id: int
    name: str
    stage: OpportunityStage = OpportunityStage.L1_PROSPECT
    amount: Optional[Decimal] = None
    scoring: int = 0
    bom_id: Optional[int] = None
    costing: Optional[Decimal] = None
    status: OpportunityStatus = OpportunityStatus.OPEN
    justification: Optional[str] = None
    close_date: Optional[date] = None
    probability: int = 10
    notes: Optional[str] = None

    # L1 - Qualification Fields
    requirement_gathering_notes: Optional[str] = None
    go_no_go_status: GoNoGoStatus = GoNoGoStatus.PENDING
    qualification_completed_by: Optional[int] = None
    qualification_status: Optional[QualificationStatus] = None
    qualification_scorecard: Optional[Dict[str, Any]] = None

    # L2 - Need Analysis / Demo Fields
    demo_completed: bool = False
    demo_date: Optional[datetime] = None
    demo_summary: Optional[str] = None
    presentation_materials: Optional[List[Dict[str, str]]] = None
    qualification_meeting_completed: bool = False
    qualification_meeting_date: Optional[datetime] = None
    qualification_meeting_notes: Optional[str] = None

    # L3 - Proposal / Bid Submission Fields
    quotation_created: bool = False
    quotation_status: QuotationStatus = QuotationStatus.DRAFT
    quotation_file_path: Optional[str] = None
    quotation_version: int = 1
    proposal_prepared: bool = False
    proposal_file_path: Optional[str] = None
    proposal_submitted: bool = False
    proposal_submission_date: Optional[datetime] = None
    poc_completed: bool = False
    poc_notes: Optional[str] = None
    solutions_team_approval_notes: Optional[str] = None

    # L4 - Negotiation Fields
    customer_discussion_notes: Optional[str] = None
    proposal_updated: bool = False
    updated_proposal_file_path: Optional[str] = None
    updated_proposal_submitted: bool = False
    negotiated_quotation_file_path: Optional[str] = None
    negotiation_rounds: int = 0
    commercial_approval_required: bool = False
    commercial_approval_status: Optional[str] = None

    # L5 - Won Fields
    kickoff_meeting_scheduled: bool = False
    kickoff_meeting_date: Optional[datetime] = None
    loi_received: bool = False
    loi_file_path: Optional[str] = None
    order_verified: bool = False
    handoff_to_delivery: bool = False
    delivery_team_assigned: Optional[int] = None

    # Lost/Dropped Fields
    lost_reason: Optional[str] = None
    competitor_name: Optional[str] = None
    follow_up_date: Optional[date] = None
    drop_reason: Optional[str] = None
    reactivate_date: Optional[date] = None

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Opportunity name must be at least 3 characters long")
        return v.strip()

    @validator("scoring")
    def validate_scoring(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Scoring must be between 0 and 100")
        return v

    @validator("probability")
    def validate_probability(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Probability must be between 0 and 100")
        return v

    @validator("amount")
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError("Amount cannot be negative")
        return v

    @validator("costing")
    def validate_costing(cls, v):
        if v is not None and v < 0:
            raise ValueError("Costing cannot be negative")
        return v

    @validator("justification", always=True)
    def validate_amount_justification(cls, v, values):
        if "amount" in values and values["amount"]:
            amount_float = float(values["amount"])
            is_valid, error_msg = validate_amount_with_justification(amount_float, v)
            if not is_valid:
                raise ValueError(error_msg)
        return v


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    lead_id: Optional[int] = None
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    name: Optional[str] = None
    stage: Optional[OpportunityStage] = None
    amount: Optional[Decimal] = None
    scoring: Optional[int] = None
    bom_id: Optional[int] = None
    costing: Optional[Decimal] = None
    status: Optional[OpportunityStatus] = None
    justification: Optional[str] = None
    close_date: Optional[date] = None
    probability: Optional[int] = None
    notes: Optional[str] = None

    # L1 - Qualification Fields
    requirement_gathering_notes: Optional[str] = None
    go_no_go_status: Optional[GoNoGoStatus] = None
    qualification_completed_by: Optional[int] = None
    qualification_status: Optional[QualificationStatus] = None
    qualification_scorecard: Optional[Dict[str, Any]] = None

    # L2 - Need Analysis / Demo Fields
    demo_completed: Optional[bool] = None
    demo_date: Optional[datetime] = None
    demo_summary: Optional[str] = None
    presentation_materials: Optional[List[Dict[str, str]]] = None
    qualification_meeting_completed: Optional[bool] = None
    qualification_meeting_date: Optional[datetime] = None
    qualification_meeting_notes: Optional[str] = None

    # L3 - Proposal / Bid Submission Fields
    quotation_created: Optional[bool] = None
    quotation_status: Optional[QuotationStatus] = None
    quotation_file_path: Optional[str] = None
    quotation_version: Optional[int] = None
    proposal_prepared: Optional[bool] = None
    proposal_file_path: Optional[str] = None
    proposal_submitted: Optional[bool] = None
    proposal_submission_date: Optional[datetime] = None
    poc_completed: Optional[bool] = None
    poc_notes: Optional[str] = None
    solutions_team_approval_notes: Optional[str] = None

    # L4 - Negotiation Fields
    customer_discussion_notes: Optional[str] = None
    proposal_updated: Optional[bool] = None
    updated_proposal_file_path: Optional[str] = None
    updated_proposal_submitted: Optional[bool] = None
    negotiated_quotation_file_path: Optional[str] = None
    negotiation_rounds: Optional[int] = None
    commercial_approval_required: Optional[bool] = None
    commercial_approval_status: Optional[str] = None

    # L5 - Won Fields
    kickoff_meeting_scheduled: Optional[bool] = None
    kickoff_meeting_date: Optional[datetime] = None
    loi_received: Optional[bool] = None
    loi_file_path: Optional[str] = None
    order_verified: Optional[bool] = None
    handoff_to_delivery: Optional[bool] = None
    delivery_team_assigned: Optional[int] = None

    # Lost/Dropped Fields
    lost_reason: Optional[str] = None
    competitor_name: Optional[str] = None
    follow_up_date: Optional[date] = None
    drop_reason: Optional[str] = None
    reactivate_date: Optional[date] = None

    @validator("scoring")
    def validate_scoring(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Scoring must be between 0 and 100")
        return v

    @validator("probability")
    def validate_probability(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Probability must be between 0 and 100")
        return v

    @validator("amount")
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class OpportunityResponse(OpportunityBase):
    id: int
    pot_id: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    lead_source: Optional[str] = None
    created_by_name: Optional[str] = None
    qualification_completer_name: Optional[str] = None
    delivery_team_member_name: Optional[str] = None
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    stage_percentage: int
    stage_display_name: str

    class Config:
        from_attributes = True
        orm_mode = True


class OpportunityListResponse(BaseModel):
    opportunities: List[OpportunityResponse]
    total: int
    skip: int
    limit: int


class OpportunityStageUpdate(BaseModel):
    """Schema for updating opportunity stage with stage-specific fields"""

    stage: OpportunityStage
    notes: Optional[str] = None
    probability: Optional[int] = None

    # Stage-specific update fields
    stage_specific_data: Optional[Dict[str, Any]] = None

    @validator("probability")
    def validate_probability(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Probability must be between 0 and 100")
        return v


class OpportunityCloseRequest(BaseModel):
    """Schema for closing opportunity"""

    status: Literal["Won", "Lost", "Dropped"]
    close_date: date
    notes: Optional[str] = None
    lost_reason: Optional[str] = None
    competitor_name: Optional[str] = None
    drop_reason: Optional[str] = None


class OpportunityPipelineSummary(BaseModel):
    """Opportunity pipeline summary"""

    total_opportunities: int
    total_value: Decimal
    avg_scoring: Optional[float] = None
    closing_stage_count: int
    stage_breakdown: List[Dict[str, Any]]


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


# Stage-specific task schemas
class QualificationTaskUpdate(BaseModel):
    requirement_gathering_notes: Optional[str] = None
    go_no_go_status: Optional[GoNoGoStatus] = None
    qualification_status: Optional[QualificationStatus] = None
    qualification_scorecard: Optional[Dict[str, Any]] = None
    completed_by: Optional[int] = None


class DemoTaskUpdate(BaseModel):
    demo_completed: Optional[bool] = None
    demo_date: Optional[datetime] = None
    demo_summary: Optional[str] = None
    presentation_materials: Optional[List[Dict[str, str]]] = None
    qualification_meeting_completed: Optional[bool] = None
    qualification_meeting_date: Optional[datetime] = None
    qualification_meeting_notes: Optional[str] = None


class ProposalTaskUpdate(BaseModel):
    quotation_created: Optional[bool] = None
    quotation_status: Optional[QuotationStatus] = None
    proposal_prepared: Optional[bool] = None
    proposal_submitted: Optional[bool] = None
    proposal_submission_date: Optional[datetime] = None
    poc_completed: Optional[bool] = None
    poc_notes: Optional[str] = None


class NegotiationTaskUpdate(BaseModel):
    customer_discussion_notes: Optional[str] = None
    proposal_updated: Optional[bool] = None
    updated_proposal_submitted: Optional[bool] = None
    negotiation_rounds: Optional[int] = None
    commercial_approval_required: Optional[bool] = None
    commercial_approval_status: Optional[str] = None


class WonTaskUpdate(BaseModel):
    kickoff_meeting_scheduled: Optional[bool] = None
    kickoff_meeting_date: Optional[datetime] = None
    loi_received: Optional[bool] = None
    order_verified: Optional[bool] = None
    handoff_to_delivery: Optional[bool] = None
    delivery_team_assigned: Optional[int] = None