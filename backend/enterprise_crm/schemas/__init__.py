# Enterprise CRM Schemas
from .masters import *
from .leads import *
from .opportunities import *
from .dashboard import *
from .common import *

__all__ = [
    # Common Schemas
    'StandardResponse',
    'PaginatedResponse',
    'ApprovalRequest',
    # Master Schemas
    'ProductMasterCreate',
    'ProductMasterUpdate',
    'ProductMasterResponse',
    'UOMCreate',
    'UOMResponse',
    'PriceListCreate',
    'PriceListResponse',
    'UserMasterCreate',
    'UserMasterResponse',
    # Lead Schemas
    'ContactCreate',
    'ContactResponse',
    'CompanyCreate',
    'CompanyResponse', 
    'LeadCreate',
    'LeadResponse',
    # Opportunity Schemas
    'OpportunityCreate',
    'OpportunityResponse',
    'QuotationCreate',
    'QuotationResponse',
    # Dashboard Schemas
    'DashboardConfigResponse',
    'WidgetConfigResponse',
]