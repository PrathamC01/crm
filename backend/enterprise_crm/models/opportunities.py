"""
Opportunities Module Models
"""
from sqlalchemy import Column, Integer, String, Text, Float, Date, ForeignKey, JSON, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class OpportunityStatusEnum(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PROPOSAL_SENT = "Proposal Sent"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    ON_HOLD = "On Hold"

class QuotationStatusEnum(str, enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"

# Opportunity Master
class OpportunityMaster(BaseModel):
    __tablename__ = "opportunity_master"
    
    opportunity_title = Column(String(200), nullable=False)
    opportunity_id = Column(String(50), unique=True, nullable=False)  # Auto-generated
    
    # References
    lead_id = Column(Integer, ForeignKey('lead_master.id'), nullable=True)
    company_id = Column(Integer, ForeignKey('company_master.id'), nullable=False)
    
    # Opportunity Details
    status = Column(SQLEnum(OpportunityStatusEnum), default=OpportunityStatusEnum.OPEN)
    stage = Column(String(50))  # Qualification, Proposal, Negotiation, etc.
    
    # Financial
    estimated_value = Column(Float)
    final_value = Column(Float, nullable=True)
    probability = Column(Float, comment="Probability of closure (0-100)")
    
    # Dates
    expected_close_date = Column(Date)
    actual_close_date = Column(Date, nullable=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey('user_master.id'))
    sales_team = Column(JSON, comment="Array of user IDs in sales team")
    
    # Additional Info
    description = Column(Text)
    win_loss_reason = Column(Text, nullable=True)
    competitor_info = Column(JSON, nullable=True)
    
    # Relationships
    lead = relationship("LeadMaster", back_populates="opportunities")
    company = relationship("CompanyMaster", back_populates="opportunities")
    assigned_user = relationship("UserMaster")
    quotations = relationship("QuotationMaster", back_populates="opportunity")

# Quotation Master
class QuotationMaster(BaseModel):
    __tablename__ = "quotation_master"
    
    quotation_number = Column(String(50), unique=True, nullable=False)
    opportunity_id = Column(Integer, ForeignKey('opportunity_master.id'), nullable=False)
    price_list_id = Column(Integer, ForeignKey('price_list_master.id'), nullable=False)
    
    # Quotation Details
    version = Column(String(10), default="1.0")
    status = Column(SQLEnum(QuotationStatusEnum), default=QuotationStatusEnum.DRAFT)
    
    # Financial Summary
    subtotal = Column(Numeric(15, 2))
    tax_amount = Column(Numeric(15, 2))
    discount_amount = Column(Numeric(15, 2))
    total_amount = Column(Numeric(15, 2))
    
    # Dates
    quotation_date = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    
    # Terms & Conditions
    payment_terms = Column(Text)
    delivery_terms = Column(Text)
    warranty_terms = Column(Text)
    additional_terms = Column(Text)
    
    # Approval
    prepared_by = Column(Integer, ForeignKey('user_master.id'), nullable=False)
    approved_by = Column(Integer, ForeignKey('user_master.id'), nullable=True)
    
    # Relationships
    opportunity = relationship("OpportunityMaster", back_populates="quotations")
    price_list = relationship("PriceListMaster")
    prepared_user = relationship("UserMaster", foreign_keys=[prepared_by])
    approved_user = relationship("UserMaster", foreign_keys=[approved_by])
    line_items = relationship("QuotationLineItem", back_populates="quotation")

# Quotation Line Items
class QuotationLineItem(BaseModel):
    __tablename__ = "quotation_line_items"
    
    quotation_id = Column(Integer, ForeignKey('quotation_master.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product_master.id'), nullable=False)
    uom_id = Column(Integer, ForeignKey('uom_master.id'), nullable=False)
    
    # Quantities and Pricing
    quantity = Column(Float, nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Float, default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Additional Info
    description = Column(Text)
    specifications = Column(JSON)
    
    # Relationships
    quotation = relationship("QuotationMaster", back_populates="line_items")
    product = relationship("ProductMaster")
    uom = relationship("UOMMaster")