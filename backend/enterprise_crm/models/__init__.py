# Enterprise CRM Models
from .base import Base
from .masters import *
from .leads import *
from .opportunities import *
from .users import *
from .dashboard import *

__all__ = [
    'Base',
    # Master Models
    'ProductMaster',
    'PriceListMaster',
    'ProductPricingMaster',
    'GroupMaster',
    'ProductGroupingMaster',
    'TaxMaster',
    'UserMaster',
    'RolesMaster',
    'DepartmentMaster',
    'DesignationMaster',
    'PermissionMaster',
    'DiscountMaster',
    'ProductCalculationMaster',
    'StateMaster',
    'CityMaster',
    'IndustryCategoryMaster',
    'UOMMaster',
    'ProductUOMMap',
    # Business Models
    'ContactMaster',
    'CompanyMaster',
    'LeadMaster',
    'OpportunityMaster',
    'QuotationMaster',
    'QuotationLineItem',
    # Dashboard Models
    'DashboardConfig',
    'DashboardWidget',
]