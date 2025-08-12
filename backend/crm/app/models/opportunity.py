"""
SQLAlchemy Opportunity model with Lead-based creation and enhanced workflow
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
    L2_NEED_ANALYSIS = "L2_Need_Analysis"
    L3_PROPOSAL = "L3_Proposal"
    WIN = "Win"
    LOSS = "Loss"


class OpportunityStatus(str, Enum):
    OPEN = "Open"
    WON = "Won"
    LOST = "Lost"


class Opportunity(BaseModel):
    __tablename__ = "opportunities"

    # Core fields with POT-{4digit} ID
    pot_id = Column(
        String(10), unique=True, nullable=False, index=True
    )  # POT-1234 format

    # MANDATORY: Lead linkage (opportunities can only be created from leads)
    lead_id = Column(
        Integer, ForeignKey("leads.id"), nullable=False, unique=True, index=True
    )  # One-to-one mapping

    # Basic Information (copied from Lead during conversion)
    name = Column(String(255), nullable=False)  # From lead.project_title
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    contact_id = Column(
        Integer, ForeignKey("contacts.id"), nullable=True, index=True
    )  # Primary contact

    # Current Stage and Status
    current_stage = Column(
        SQLEnum(OpportunityStage),
        default=OpportunityStage.L1_PROSPECT,
        nullable=False,
        index=True,
    )
    status = Column(
        SQLEnum(OpportunityStatus),
        default=OpportunityStatus.OPEN,
        nullable=False,
        index=True,
    )

    # Financial Information
    amount = Column(DECIMAL(15, 2))  # Copied from lead.expected_revenue
    currency = Column(String(3), default="INR")
    probability = Column(Integer, default=10)  # Success probability percentage

    # Dates
    close_date = Column(Date)  # Copied from lead.convert_to_opportunity_date
    conversion_date = Column(DateTime, nullable=False)  # When converted from lead

    # Lead Data Preservation (JSON storage for complex data)
    lead_data = Column(JSON)  # Complete lead data snapshot at conversion time

    # Partner Information (copied from lead)
    partner_involved = Column(Boolean, default=False)
    partners_data = Column(JSON)  # Array of partner information

    # Products and Services (copied from lead)
    products_services = Column(JSON)  # Array of selected products/services

    # Tender Information (copied from lead)
    tender_details = Column(JSON)  # Complete tender information from lead

    # Competition Analysis (copied from lead)
    competitors = Column(JSON)  # Array of competitor objects

    # Documentation
    documents = Column(JSON)  # Array of document objects
    notes = Column(Text)

    # Approval and Conversion Tracking
    converted_by = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Who converted the lead
    approval_status = Column(
        String(50), default="Approved"
    )  # Since conversion requires approval
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_date = Column(DateTime)

    # Sales Process Completion Tracking
    l1_completed = Column(Boolean, default=False)
    l1_completion_date = Column(Date)
    l2_completed = Column(Boolean, default=False)
    l2_completion_date = Column(Date)
    l3_completed = Column(Boolean, default=False)
    l3_completion_date = Column(Date)

    # Final Outcome
    won_date = Column(Date)
    lost_date = Column(Date)
    lost_reason = Column(String(255))
    win_reason = Column(String(255))

    __table_args__ = (
        CheckConstraint(
            "probability >= 0 AND probability <= 100", name="check_probability_range"
        ),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
    )

    # Relationships
    lead = relationship("Lead", back_populates="opportunities")
    company = relationship("Company", back_populates="opportunities")
    contact = relationship("Contact", back_populates="opportunities")

    # Sales Process and Quotations
    sales_processes = relationship(
        "SalesProcess", back_populates="opportunity", cascade="all, delete-orphan"
    )
    quotations = relationship(
        "Quotation", back_populates="opportunity", cascade="all, delete-orphan"
    )

    # User relationships
    converted_by_user = relationship("User", foreign_keys=[converted_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])

    creator = relationship(
        "User",
        foreign_keys="Opportunity.created_by",
        back_populates="opportunities_created",
        overlaps="converted_by_user,approved_by_user",
    )
    updater = relationship(
        "User",
        foreign_keys="Opportunity.updated_by",
        back_populates="opportunities_updated",
    )

    def __init__(self, **kwargs):
        # Enforce that opportunities can only be created with a lead_id
        if "lead_id" not in kwargs or kwargs["lead_id"] is None:
            raise ValueError(
                "Opportunities can only be created by converting a Lead. lead_id is required."
            )

        super().__init__(**kwargs)
        if not self.pot_id:
            self.pot_id = self._generate_pot_id()
        if not self.conversion_date:
            self.conversion_date = datetime.utcnow()

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
        return self.lead.project_title if self.lead else None

    @property
    def contact_name(self):
        return self.contact.full_name if self.contact else None

    @property
    def converted_by_name(self):
        return self.converted_by_user.name if self.converted_by_user else None

    @property
    def approved_by_name(self):
        return self.approved_by_user.name if self.approved_by_user else None

    @property
    def stage_percentage(self):
        """Return percentage based on current stage"""
        stage_percentages = {
            OpportunityStage.L1_PROSPECT: 25,
            OpportunityStage.L2_NEED_ANALYSIS: 50,
            OpportunityStage.L3_PROPOSAL: 75,
            OpportunityStage.WIN: 100,
            OpportunityStage.LOSS: 0,
        }
        return stage_percentages.get(self.current_stage, 0)

    @property
    def current_sales_process(self):
        """Get the current active sales process stage"""
        if self.sales_processes:
            return next(
                (
                    sp
                    for sp in self.sales_processes
                    if sp.stage.value == self.current_stage.value
                ),
                None,
            )
        return None

    @property
    def can_create_quotations(self):
        """Check if quotations can be created (L3 stage completed)"""
        return self.l3_completed or self.current_stage in [
            OpportunityStage.L3_PROPOSAL,
            OpportunityStage.WIN,
        ]

    @property
    def quotations_count(self):
        """Get count of quotations"""
        return len(self.quotations) if self.quotations else 0

    @property
    def active_quotations_count(self):
        """Get count of active (non-rejected) quotations"""
        if not self.quotations:
            return 0
        return len([q for q in self.quotations if q.status != "Rejected"])

    @classmethod
    def create_from_lead(cls, lead, converted_by_user_id, approved_by_user_id=None):
        """Create opportunity from lead with all data preservation"""
        opportunity_data = {
            "lead_id": lead.id,
            "name": lead.project_title,
            "company_id": lead.company_id,
            "amount": lead.expected_revenue,
            "currency": lead.revenue_currency,
            "close_date": lead.convert_to_opportunity_date,
            "converted_by": converted_by_user_id,
            "approved_by": approved_by_user_id,
            "approved_date": datetime.utcnow() if approved_by_user_id else None,
            "created_by": converted_by_user_id,
            # Preserve lead data
            "lead_data": {
                "project_title": lead.project_title,
                "lead_source": lead.lead_source.value if lead.lead_source else None,
                "lead_sub_type": (
                    lead.lead_sub_type.value if lead.lead_sub_type else None
                ),
                "tender_sub_type": (
                    lead.tender_sub_type.value if lead.tender_sub_type else None
                ),
                "products_services": lead.products_services,
                "sub_business_type": lead.sub_business_type,
                "end_customer_id": lead.end_customer_id,
                "end_customer_region": lead.end_customer_region,
                "contacts": lead.contacts,
                "qualification_notes": lead.qualification_notes,
                "lead_score": lead.lead_score,
                "priority": lead.priority.value if lead.priority else None,
            },
            "partner_involved": lead.partner_involved,
            "partners_data": lead.partners_data,
            "products_services": lead.products_services,
            "competitors": lead.competitors,
            "documents": lead.documents,
            # Tender details
            "tender_details": {
                "tender_fee": float(lead.tender_fee) if lead.tender_fee else 0,
                "currency": lead.currency,
                "submission_type": (
                    lead.submission_type.value if lead.submission_type else None
                ),
                "tender_authority": lead.tender_authority,
                "tender_for": lead.tender_for,
                "emd_required": lead.emd_required,
                "emd_amount": float(lead.emd_amount) if lead.emd_amount else 0,
                "emd_currency": lead.emd_currency,
                "bg_required": lead.bg_required,
                "bg_amount": float(lead.bg_amount) if lead.bg_amount else 0,
                "bg_currency": lead.bg_currency,
                "important_dates": lead.important_dates,
                "clauses": lead.clauses,
            },
        }

        return cls(**opportunity_data)

    def __repr__(self):
        return f"<Opportunity(pot_id={self.pot_id}, name={self.name}, stage={self.current_stage}, status={self.status}, lead_id={self.lead_id})>"
