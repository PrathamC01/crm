"""
Pydantic schemas for CRM application
"""

from .auth import LoginRequest, UserResponse, StandardResponse, TokenData, TokenResponse
from .user import (
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse as EnhancedUserResponse,
    UserListResponse,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    UserPermissions,
)
from .company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
from .contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    BusinessCardUpload,
)
from .lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    # LeadConversion,
    # LeadSummary,
    LeadSource,
    LeadStatus,
    LeadPriority,
)
from .opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityListResponse,
    OpportunityStageUpdate,
    OpportunityCloseRequest,
    OpportunityPipelineSummary,
    OpportunityMetrics,
    OpportunityStage,
    OpportunityStatus,
)

__all__ = [
    # Auth schemas
    "LoginRequest",
    "UserResponse",
    "StandardResponse",
    "TokenData",
    "TokenResponse",
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserPasswordUpdate",
    "EnhancedUserResponse",
    "UserListResponse",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "UserPermissions",
    # Company schemas
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyListResponse",
    # Contact schemas
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    "ContactListResponse",
    "BusinessCardUpload",
    # Lead schemas
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadListResponse",
    # "LeadStatusUpdate",
    # "LeadConversion",
    # "LeadSummary",
    "LeadSource",
    "LeadStatus",
    "LeadPriority",
    # Opportunity schemas
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityResponse",
    "OpportunityListResponse",
    "OpportunityStageUpdate",
    "OpportunityCloseRequest",
    "OpportunityPipelineSummary",
    "OpportunityMetrics",
    "OpportunityStage",
    "OpportunityStatus",
]
