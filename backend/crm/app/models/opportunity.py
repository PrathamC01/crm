"""
SQLAlchemy Opportunity model with enhanced stage-specific fields
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
    CheckConstraint,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship
from enum import Enum
import uuid
import random
from datetime import datetime
from .base import BaseModel


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


class Opportunity(BaseModel):
    __tablename__ = "opportunities"

    # Core fields with POT-{4digit} ID
    pot_id = Column(String(10), unique=True, nullable=False, index=True)  # POT-1234 format
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    stage = Column(
        SQLEnum(OpportunityStage),
        default=OpportunityStage.L1_PROSPECT,
        nullable=False,
        index=True,
    )
    amount = Column(DECIMAL(15, 2))
    scoring = Column(Integer, default=0)
    bom_id = Column(Integer)  # Bill of Materials ID (future reference)
    costing = Column(DECIMAL(15, 2))
    status = Column(
        SQLEnum(OpportunityStatus),
        default=OpportunityStatus.OPEN,
        nullable=False,
        index=True,
    )
    justification = Column(Text)
    close_date = Column(Date)
    probability = Column(Integer, default=10)
    notes = Column(Text)

    # L1 - Qualification Stage Fields (15%)
    requirement_gathering_notes = Column(Text)
    go_no_go_status = Column(SQLEnum(GoNoGoStatus), default=GoNoGoStatus.PENDING)
    qualification_completed_by = Column(Integer, ForeignKey("users.id"))
    qualification_status = Column(SQLEnum(QualificationStatus))
    qualification_scorecard = Column(JSON)  # BANT/CHAMP scores

    # L2 - Need Analysis / Demo Stage Fields (40%)
    demo_completed = Column(Boolean, default=False)
    demo_date = Column(DateTime)
    demo_summary = Column(Text)
    presentation_materials = Column(JSON)  # File paths/URLs
    qualification_meeting_completed = Column(Boolean, default=False)
    qualification_meeting_date = Column(DateTime)
    qualification_meeting_notes = Column(Text)

    # L3 - Proposal / Bid Submission Stage Fields (60%)
    quotation_created = Column(Boolean, default=False)
    quotation_status = Column(SQLEnum(QuotationStatus), default=QuotationStatus.DRAFT)
    quotation_file_path = Column(String(500))
    quotation_version = Column(Integer, default=1)
    proposal_prepared = Column(Boolean, default=False)
    proposal_file_path = Column(String(500))
    proposal_submitted = Column(Boolean, default=False)
    proposal_submission_date = Column(DateTime)
    poc_completed = Column(Boolean, default=False)
    poc_notes = Column(Text)
    solutions_team_approval_notes = Column(Text)

    # L4 - Negotiation Stage Fields (80%)
    customer_discussion_notes = Column(Text)
    proposal_updated = Column(Boolean, default=False)
    updated_proposal_file_path = Column(String(500))
    updated_proposal_submitted = Column(Boolean, default=False)
    negotiated_quotation_file_path = Column(String(500))
    negotiation_rounds = Column(Integer, default=0)
    commercial_approval_required = Column(Boolean, default=False)
    commercial_approval_status = Column(String(50))

    # L5 - Won Stage Fields (100%)
    kickoff_meeting_scheduled = Column(Boolean, default=False)
    kickoff_meeting_date = Column(DateTime)
    loi_received = Column(Boolean, default=False)
    loi_file_path = Column(String(500))
    order_verified = Column(Boolean, default=False)
    handoff_to_delivery = Column(Boolean, default=False)
    delivery_team_assigned = Column(Integer, ForeignKey("users.id"))

    # Lost/Dropped Stage Fields
    lost_reason = Column(String(255))
    competitor_name = Column(String(255))
    follow_up_date = Column(Date)
    drop_reason = Column(String(255))
    reactivate_date = Column(Date)

    __table_args__ = (
        CheckConstraint("scoring >= 0 AND scoring <= 100", name="check_scoring_range"),
        CheckConstraint(
            "probability >= 0 AND probability <= 100", name="check_probability_range"
        ),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        CheckConstraint("costing >= 0", name="check_costing_positive"),
        CheckConstraint(
            "(amount < 1000000 AND justification IS NULL) OR (amount >= 1000000 AND justification IS NOT NULL AND length(trim(justification)) > 0)",
            name="check_amount_justification",
        ),
    )

    # Relationships
    lead = relationship("Lead", back_populates="opportunities")
    company = relationship("Company", back_populates="opportunities")
    contact = relationship("Contact", back_populates="opportunities")
    qualification_completer = relationship(
        "User", 
        foreign_keys=[qualification_completed_by],
        backref="qualifications_completed"
    )
    delivery_team_member = relationship(
        "User", 
        foreign_keys=[delivery_team_assigned],
        backref="opportunities_assigned"
    )
    creator = relationship(
        "User",
        foreign_keys="Opportunity.created_by",
        back_populates="opportunities_created",
    )
    updater = relationship(
        "User",
        foreign_keys="Opportunity.updated_by",
        back_populates="opportunities_updated",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.pot_id:
            self.pot_id = self._generate_pot_id()

    @staticmethod
    def _generate_pot_id():
        """Generate unique POT-{4digit} ID"""
        return f"POT-{random.randint(1000, 9999)}"

    # Properties
    @property
    def company_name(self):
        return self.company.name if self.company else None

    @property
    def lead_name(self):
        return self.lead.name if self.lead else None

    @property
    def contact_name(self):
        return self.contact.full_name if self.contact else None

    @property
    def creator_name(self):
        return self.creator.full_name if self.creator else None

    @property
    def updater_name(self):
        return self.updater.full_name if self.updater else None

    @property
    def stage_percentage(self):
        """Return percentage based on stage"""
        stage_percentages = {
            OpportunityStage.L1_PROSPECT: 5,
            OpportunityStage.L1_QUALIFICATION: 15,
            OpportunityStage.L2_NEED_ANALYSIS: 40,
            OpportunityStage.L3_PROPOSAL: 60,
            OpportunityStage.L4_NEGOTIATION: 80,
            OpportunityStage.L5_WON: 100,
            OpportunityStage.L6_LOST: 0,
            OpportunityStage.L7_DROPPED: 0,
        }
        return stage_percentages.get(self.stage, 0)

    @property
    def stage_display_name(self):
        """Return user-friendly stage name"""
        stage_names = {
            OpportunityStage.L1_PROSPECT: "L1 - Prospect",
            OpportunityStage.L1_QUALIFICATION: "L1 - Qualification (15%)",
            OpportunityStage.L2_NEED_ANALYSIS: "L2 - Need Analysis / Demo (40%)",
            OpportunityStage.L3_PROPOSAL: "L3 - Proposal / Bid Submission (60%)",
            OpportunityStage.L4_NEGOTIATION: "L4 - Negotiation (80%)",
            OpportunityStage.L5_WON: "L5 - Won (100%)",
            OpportunityStage.L6_LOST: "L6 - Lost",
            OpportunityStage.L7_DROPPED: "L7 - Dropped",
        }
        return stage_names.get(self.stage, self.stage.value)

    def __repr__(self):
        return f"<Opportunity(pot_id={self.pot_id}, name={self.name}, stage={self.stage}, status={self.status})>"