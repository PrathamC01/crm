"""
Enhanced SQLAlchemy Company model for Swayatta 4.0 - With Hot/Cold Validation System
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, Boolean, DateTime, Numeric, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from .base import BaseModel

class CompanyType(enum.Enum):
    DOMESTIC_GST = "DOMESTIC_GST"
    DOMESTIC_NONGST = "DOMESTIC_NONGST"
    NGO = "NGO"
    OVERSEAS = "OVERSEAS"

class CompanyStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class LeadStatus(enum.Enum):
    HOT = "HOT"
    COLD = "COLD"

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
    employee_count = Column(Integer, nullable=True)  # New field for validation
    
    # Identification & Compliance
    gst_number = Column(String(15), nullable=True, index=True)
    pan_number = Column(String(10), nullable=True, index=True)
    international_unique_id = Column(String(50), nullable=True, index=True)
    supporting_documents = Column(JSON, nullable=False)  # File paths/URLs
    verification_source = Column(Enum(VerificationSource), nullable=False)
    verification_date = Column(DateTime, nullable=False)
    verified_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Address Fields (Enhanced with Database Relationships)
    address = Column(Text, nullable=False)
    
    # Text-based fields (kept for backward compatibility)
    country = Column(String(100), nullable=False, default='India')
    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    pin_code = Column(String(10), nullable=False)
    
    # Database-driven geographic relationships (New)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    state_id = Column(Integer, ForeignKey('states.id'), nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    
    # Hierarchy & Linkages
    parent_child_mapping_confirmed = Column(Boolean, nullable=False, default=False)
    linked_subsidiaries = Column(JSON, nullable=True)  # Array of company IDs
    associated_channel_partner = Column(String(255), nullable=True)
    
    # System Metadata
    status = Column(Enum(CompanyStatus), nullable=False, default=CompanyStatus.ACTIVE)
    lead_status = Column(Enum(LeadStatus), nullable=False)  # New field for hot/cold classification
    change_log_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Additional fields
    website = Column(String(255))
    description = Column(Text)
    
    # Auto-tagging fields
    is_high_revenue = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    # Self-referential relationship for parent company
    parent_company = relationship("Company", remote_side="Company.id", back_populates="subsidiaries")
    subsidiaries = relationship("Company", back_populates="parent_company")
    
    # Geographic relationships (New)
    country_ref = relationship("Country", back_populates="companies")
    state_ref = relationship("State", back_populates="companies")  
    city_ref = relationship("City", back_populates="companies")
    
    # Audit relationships
    creator = relationship("User", foreign_keys="Company.created_by", back_populates="companies_created")
    updater = relationship("User", foreign_keys="Company.updated_by", back_populates="companies_updated")
    verifier = relationship("User", foreign_keys="Company.verified_by")
    
    # Related entities
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", foreign_keys="[Lead.company_id]", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, lead_status={self.lead_status})>"
    
    def auto_tag_revenue(self):
        """Auto-tag company based on revenue threshold"""
        if self.annual_revenue and self.annual_revenue > 20000000:  # ₹2 crore
            self.is_high_revenue = True
            if not self.tags:
                self.tags = []
            if "HIGH_REVENUE_COMPANY" not in self.tags:
                self.tags.append("HIGH_REVENUE_COMPANY")
    
    def validate_lead_status(self):
        """Validate and set lead status based on business criteria"""
        # Hot Industries - High business potential
        hot_industries = [
            "IT_ITeS", "BFSI", "Healthcare", "Manufacturing", 
            "Energy_Utilities", "Telecom"
        ]
        
        # Hot Sub-Industries - Specific high-value sectors
        hot_sub_industries = [
            "Software Development", "IT Services", "Cloud Services", "Cybersecurity",
            "Banking", "Financial Services", "Fintech", "Investment Banking",
            "Pharmaceuticals", "Medical Devices", "Healthcare IT",
            "Automotive", "Electronics", "Heavy Machinery",
            "Power Generation", "Renewable Energy", "Oil & Gas"
        ]
        
        score = 0
        
        # Industry scoring (40% weight)
        if self.industry in hot_industries:
            score += 40
        elif self.industry in ["Government", "Education"]:
            score += 25  # Medium potential
        else:
            score += 10  # Lower potential
        
        # Sub-industry bonus (20% weight)  
        if self.sub_industry in hot_sub_industries:
            score += 20
        else:
            score += 5
        
        # Revenue scoring (25% weight)
        if self.annual_revenue:
            if self.annual_revenue >= 100000000:  # ₹10+ crore
                score += 25
            elif self.annual_revenue >= 50000000:  # ₹5+ crore  
                score += 20
            elif self.annual_revenue >= 20000000:  # ₹2+ crore
                score += 15
            elif self.annual_revenue >= 5000000:   # ₹50+ lakh
                score += 10
            else:
                score += 5
        
        # Employee count scoring (15% weight)
        if self.employee_count:
            if self.employee_count >= 500:
                score += 15
            elif self.employee_count >= 100:
                score += 12
            elif self.employee_count >= 50:
                score += 8
            else:
                score += 3
        else:
            # If no employee count, estimate from revenue
            if self.annual_revenue and self.annual_revenue >= 50000000:
                score += 10  # Assume larger company
            else:
                score += 5
        
        # Company type bonus
        if self.company_type == CompanyType.DOMESTIC_GST:
            score += 5  # Formal business structure
        elif self.company_type == CompanyType.OVERSEAS:
            score += 8  # International presence
        
        # Set lead status based on total score
        # Score ranges: 0-100, Hot threshold: 70+
        if score >= 70:
            self.lead_status = LeadStatus.HOT
            if not self.tags:
                self.tags = []
            if "HIGH_POTENTIAL_LEAD" not in self.tags:
                self.tags.append("HIGH_POTENTIAL_LEAD")
        else:
            self.lead_status = LeadStatus.COLD
        
        return {
            "score": score,
            "status": self.lead_status.value,
            "criteria": {
                "industry_match": self.industry in hot_industries,
                "sub_industry_match": self.sub_industry in hot_sub_industries,
                "revenue_tier": self._get_revenue_tier(),
                "employee_tier": self._get_employee_tier()
            }
        }
    
    def _get_revenue_tier(self):
        """Get revenue tier for validation reporting"""
        if not self.annual_revenue:
            return "Unknown"
        elif self.annual_revenue >= 100000000:
            return "Enterprise (₹10+ Cr)"
        elif self.annual_revenue >= 50000000:
            return "Large (₹5-10 Cr)"
        elif self.annual_revenue >= 20000000:
            return "Medium (₹2-5 Cr)"
        elif self.annual_revenue >= 5000000:
            return "Small (₹50L-2 Cr)"
        else:
            return "Startup (<₹50L)"
    
    def _get_employee_tier(self):
        """Get employee tier for validation reporting"""
        if not self.employee_count:
            return "Unknown"
        elif self.employee_count >= 500:
            return "Large (500+)"
        elif self.employee_count >= 100:
            return "Medium (100-500)"
        elif self.employee_count >= 50:
            return "Small (50-100)"
        else:
            return "Startup (<50)"
    
    def get_display_name_with_status(self):
        """Get company name with lead status for dropdowns"""
        status_icon = "🔥" if self.lead_status == LeadStatus.HOT else "❄️"
        status_text = "HOT" if self.lead_status == LeadStatus.HOT else "COLD"
        return f"{self.name} ({status_icon} {status_text})"
    
    def to_dropdown_dict(self):
        """Convert to dictionary for dropdown display"""
        return {
            "id": self.id,
            "name": self.name,
            "lead_status": self.lead_status.value,
            "display_name": self.get_display_name_with_status(),
            "industry": self.industry,
            "city": self.city,
            "revenue_tier": self._get_revenue_tier()
        }