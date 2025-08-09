"""
CRM Models initialization
"""

from .base import Base, BaseModel
from .user import User
from .role import Role, RoleType
from .department import Department
from .company import Company
from .contact import Contact
from .lead import Lead, LeadSource, LeadStatus, LeadPriority, ReviewStatus, LeadSubType, TenderSubType, SubmissionType
from .opportunity import Opportunity, OpportunityStage, OpportunityStatus
from .sales_process import SalesProcess, SalesStage, StageStatus
from .quotation import Quotation, QuotationStatus

__all__ = [
    'Base',
    'BaseModel',
    'User',
    'Role',
    'Department',
    'Company',
    'Contact',
    'RoleType',
    'Lead',
    'LeadSource',
    'LeadStatus',
    'LeadPriority',
    'ReviewStatus',
    'LeadSubType',
    'TenderSubType', 
    'SubmissionType',
    'Opportunity',
    'OpportunityStage',
    'OpportunityStatus',
    'SalesProcess',
    'SalesStage',
    'StageStatus',
    'Quotation',
    'QuotationStatus'
]