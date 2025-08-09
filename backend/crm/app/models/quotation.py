"""
Quotation model for opportunity quotations
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
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from .base import BaseModel


class QuotationStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REVISED = "Revised"


class Quotation(BaseModel):
    __tablename__ = "quotations"

    # Link to Opportunity
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    
    # Quotation Identification
    quotation_id = Column(String(20), unique=True, nullable=False, index=True)  # QUO-YYYY-XXXX format
    quotation_name = Column(String(255), nullable=False)
    
    # Quotation Details
    quotation_date = Column(Date, nullable=False)
    valid_until = Column(Date)
    amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    
    # Status and Approval
    status = Column(SQLEnum(QuotationStatus), default=QuotationStatus.DRAFT, nullable=False, index=True)
    
    # Quotation Content
    description = Column(Text)
    terms_conditions = Column(Text)
    
    # Line Items (stored as JSON for flexibility)
    line_items = Column(JSON)  # Array of line item objects
    
    # Pricing Details
    subtotal = Column(DECIMAL(15, 2))
    tax_amount = Column(DECIMAL(15, 2))
    tax_percentage = Column(DECIMAL(5, 2))
    discount_amount = Column(DECIMAL(15, 2))
    discount_percentage = Column(DECIMAL(5, 2))
    total_amount = Column(DECIMAL(15, 2))
    
    # File Management
    quotation_file_path = Column(String(500))  # Path to generated PDF
    attachments = Column(JSON)  # Array of attachment objects
    
    # Customer Information (copied from opportunity)
    customer_info = Column(JSON)  # Customer details at time of quotation
    
    # Approval Workflow
    submitted_date = Column(DateTime)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    approved_date = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # Revision Management
    parent_quotation_id = Column(Integer, ForeignKey("quotations.id"))
    revision_number = Column(Integer, default=1)
    revision_notes = Column(Text)
    
    # Follow-up
    follow_up_date = Column(Date)
    follow_up_notes = Column(Text)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="quotations")
    submitted_by_user = relationship("User", foreign_keys=[submitted_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    parent_quotation = relationship("Quotation", remote_side="Quotation.id")
    revisions = relationship("Quotation", cascade="all, delete-orphan")
    
    creator = relationship(
        "User",
        foreign_keys="Quotation.created_by",
        overlaps="submitted_by_user,approved_by_user"
    )
    updater = relationship(
        "User",
        foreign_keys="Quotation.updated_by"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.quotation_id:
            self.quotation_id = self._generate_quotation_id()

    @staticmethod
    def _generate_quotation_id():
        """Generate unique quotation ID in QUO-YYYY-XXXX format"""
        from datetime import datetime
        import random
        year = datetime.now().year
        random_num = random.randint(1000, 9999)
        return f"QUO-{year}-{random_num}"

    @property
    def is_editable(self):
        """Check if quotation can be edited"""
        return self.status in [QuotationStatus.DRAFT, QuotationStatus.REJECTED]

    @property
    def can_submit(self):
        """Check if quotation can be submitted"""
        return self.status == QuotationStatus.DRAFT and self.amount > 0

    @property
    def can_approve(self):
        """Check if quotation can be approved"""
        return self.status == QuotationStatus.SUBMITTED

    @property
    def display_amount(self):
        """Return formatted amount with currency"""
        return f"{self.currency} {self.amount:,.2f}"

    def __repr__(self):
        return f"<Quotation(quotation_id={self.quotation_id}, opportunity={self.opportunity_id}, status={self.status}, amount={self.amount})>"