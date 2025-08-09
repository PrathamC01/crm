"""
Pydantic schemas for CRM application
"""

from .user import UserResponse, UserCreate, UserUpdate, UserLogin, UserStats
from .role import RoleResponse, RoleCreate, RoleUpdate
from .department import DepartmentResponse, DepartmentCreate, DepartmentUpdate
from .company import CompanyResponse, CompanyCreate, CompanyUpdate, CompanyListResponse, CompanyStats
from .contact import ContactResponse, ContactCreate, ContactUpdate, ContactListResponse, ContactStats
from .lead import (
    LeadResponse, LeadCreate, LeadUpdate, LeadListResponse, LeadStats,
    LeadStatusUpdate, LeadConversion, LeadSummary, LeadStatsResponse
)
from .opportunity import (
    OpportunityResponse, OpportunityCreate, OpportunityListResponse, OpportunityStats,
    SalesProcessResponse, SalesProcessCreate, SalesProcessUpdate,
    LeadConversionEligibility, ConvertLeadRequest, OpportunityListItem
)
from .quotation import (
    QuotationResponse, QuotationCreate, QuotationUpdate, QuotationListResponse, QuotationStats,
    QuotationSubmissionRequest, QuotationApprovalRequest, QuotationRejectionRequest,
    QuotationRevisionRequest, QuotationListItem, LineItem
)

__all__ = [
    # User schemas
    "UserResponse", "UserCreate", "UserUpdate", "UserLogin", "UserStats",
    
    # Role schemas
    "RoleResponse", "RoleCreate", "RoleUpdate",
    
    # Department schemas
    "DepartmentResponse", "DepartmentCreate", "DepartmentUpdate",
    
    # Company schemas
    "CompanyResponse", "CompanyCreate", "CompanyUpdate", "CompanyListResponse", "CompanyStats",
    
    # Contact schemas
    "ContactResponse", "ContactCreate", "ContactUpdate", "ContactListResponse", "ContactStats",
    
    # Lead schemas
    "LeadResponse", "LeadCreate", "LeadUpdate", "LeadListResponse", "LeadStatsResponse",
    "LeadStatusUpdate", "LeadConversion", "LeadSummary",
    
    # Opportunity schemas
    "OpportunityResponse", "OpportunityCreate", "OpportunityListResponse", "OpportunityStats",
    "SalesProcessResponse", "SalesProcessCreate", "SalesProcessUpdate",
    "LeadConversionEligibility", "ConvertLeadRequest", "OpportunityListItem",
    
    # Quotation schemas
    "QuotationResponse", "QuotationCreate", "QuotationUpdate", "QuotationListResponse", "QuotationStats",
    "QuotationSubmissionRequest", "QuotationApprovalRequest", "QuotationRejectionRequest",
    "QuotationRevisionRequest", "QuotationListItem", "LineItem"
]