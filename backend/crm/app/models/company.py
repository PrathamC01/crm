"""
Enhanced SQLAlchemy Company model for Swayatta 4.0
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean, DateTime, Numeric, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum
from .base import BaseModel

class CompanyType(enum.Enum):
    DOMESTIC_GST = "DOMESTIC_GST"
    DOMESTIC_NONGST = "DOMESTIC_NONGST"
    NGO = "NGO"
    OVERSEAS = "OVERSEAS"

class ApprovalStage(enum.Enum):
    DRAFT = "DRAFT"
    L1_PENDING = "L1_PENDING"
    ADMIN_PENDING = "ADMIN_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class CompanyStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"  
    PENDING_APPROVAL = "PENDING_APPROVAL"

class VerificationSource(enum.Enum):
    GST = "GST"
    MCA = "MCA"
    PAN_NSDL = "PAN_NSDL"
    DIGILOCKER = "DIGILOCKER"
    GARTNER = "GARTNER"
    MANUAL = "MANUAL"

class Company(BaseModel):
    __tablename__ = 'companies'
    
    # Basic Information
    name = Column(String(255), unique=True, nullable=False, index=True)
    parent_company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    company_type = Column(Enum(CompanyType), nullable=False)
    industry = Column(String(100), nullable=False)
    sub_industry = Column(String(100), nullable=False)
    annual_revenue = Column(Numeric(15, 2), nullable=False)
    
    # Identification & Compliance
    gst_number = Column(String(15), nullable=True, index=True)
    pan_number = Column(String(10), nullable=True, index=True)
    international_unique_id = Column(String(50), nullable=True, index=True)
    supporting_documents = Column(JSON, nullable=False)  # File paths/URLs
    verification_source = Column(Enum(VerificationSource), nullable=False)
    verification_date = Column(DateTime, nullable=False)
    verified_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Registered Address (all mandatory)
    address = Column(Text, nullable=False)
    country = Column(String(100), nullable=False, default='India')
    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    pin_code = Column(String(10), nullable=False)
    
    # Hierarchy & Linkages
    parent_child_mapping_confirmed = Column(Boolean, nullable=False, default=False)
    linked_subsidiaries = Column(ARRAY(Integer), nullable=True)  # Array of company IDs
    associated_channel_partner = Column(String(255), nullable=True)
    
    # System Metadata
    approval_stage = Column(Enum(ApprovalStage), nullable=False, default=ApprovalStage.DRAFT)
    status = Column(Enum(CompanyStatus), nullable=False, default=CompanyStatus.PENDING_APPROVAL)
    change_log_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    
    # Additional fields
    website = Column(String(255))
    description = Column(Text)
    
    # Auto-tagging fields
    is_high_revenue = Column(Boolean, default=False)
    tags = Column(ARRAY(String), nullable=True)
    
    # Approval workflow tracking
    l1_approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    l1_approved_date = Column(DateTime, nullable=True)
    admin_approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    admin_approved_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Go/No-Go checklist
    go_nogo_checklist_completed = Column(Boolean, default=False)
    checklist_items = Column(ARRAY(String), nullable=True)  # Completed checklist items
    
    # SLA tracking
    sla_breach_date = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, default=0)
    
    # Self-referential relationship for parent company
    parent_company = relationship("Company", remote_side="Company.id", back_populates="subsidiaries")
    subsidiaries = relationship("Company", back_populates="parent_company")
    
    # Audit relationships
    creator = relationship("User", foreign_keys="Company.created_by", back_populates="companies_created")
    updater = relationship("User", foreign_keys="Company.updated_by", back_populates="companies_updated")
    verifier = relationship("User", foreign_keys="Company.verified_by")
    l1_approver = relationship("User", foreign_keys="Company.l1_approved_by")
    admin_approver = relationship("User", foreign_keys="Company.admin_approved_by")
    
    # Related entities
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", foreign_keys="[Lead.company_id]", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, type={self.company_type})>"
    
    def auto_tag_revenue(self):
        """Auto-tag company based on revenue threshold"""
        if self.annual_revenue and self.annual_revenue > 20000000:  # ₹2 crore
            self.is_high_revenue = True
            if not self.tags:
                self.tags = []
            if "HIGH_REVENUE_COMPANY" not in self.tags:
                self.tags.append("HIGH_REVENUE_COMPANY")
    
    def check_sla_breach(self):
        """Check if SLA has been breached for verification"""
        if self.approval_stage in [ApprovalStage.L1_PENDING, ApprovalStage.ADMIN_PENDING]:
            hours_since_creation = (datetime.utcnow() - self.created_on).total_seconds() / 3600
            if hours_since_creation > 48:  # 48 hours SLA
                self.sla_breach_date = datetime.utcnow()
                self.escalation_level = min(self.escalation_level + 1, 3)