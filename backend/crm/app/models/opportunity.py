"""
SQLAlchemy Opportunity model
"""
from sqlalchemy import Column, String, Text, ForeignKey, Date, Integer, Enum as SQLEnum, DECIMAL, CheckConstraint
from sqlalchemy.orm import relationship
from enum import Enum
from .base import BaseModel

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

class Opportunity(BaseModel):
    __tablename__ = 'opportunities'
    
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    stage = Column(SQLEnum(OpportunityStage), default=OpportunityStage.L1, nullable=False, index=True)
    amount = Column(DECIMAL(15, 2))
    scoring = Column(Integer, default=0)
    bom_id = Column(Integer)  # Bill of Materials ID (future reference)
    costing = Column(DECIMAL(15, 2))
    status = Column(SQLEnum(OpportunityStatus), default=OpportunityStatus.OPEN, nullable=False, index=True)
    justification = Column(Text)
    close_date = Column(Date)
    probability = Column(Integer, default=10)
    notes = Column(Text)
    
    # Add constraints
    __table_args__ = (
        CheckConstraint('scoring >= 0 AND scoring <= 100', name='check_scoring_range'),
        CheckConstraint('probability >= 0 AND probability <= 100', name='check_probability_range'),
        CheckConstraint('amount >= 0', name='check_amount_positive'),
        CheckConstraint('costing >= 0', name='check_costing_positive'),
        CheckConstraint(
            '(amount < 1000000 AND justification IS NULL) OR (amount >= 1000000 AND justification IS NOT NULL AND length(trim(justification)) > 0)',
            name='check_amount_justification'
        ),
    )
    
    # Relationships
    lead = relationship("Lead", back_populates="opportunities")
    company = relationship("Company", back_populates="opportunities")
    contact = relationship("Contact", back_populates="opportunities")
    creator = relationship("User", foreign_keys="Opportunity.created_by", back_populates="opportunities_created")
    updater = relationship("User", foreign_keys="Opportunity.updated_by", back_populates="opportunities_updated")
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, name={self.name}, stage={self.stage}, status={self.status})>"