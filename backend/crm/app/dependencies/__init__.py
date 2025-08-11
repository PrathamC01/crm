"""
Dependency injection for CRM application
"""
from .auth import get_current_user, get_auth_service, get_user_service
from .database import get_postgres_db, get_mongo_db
from .rbac import (
    require_permission, require_any_permission, require_all_permissions,
    require_users_read, require_users_write,
    require_companies_read, require_companies_write,
    require_contacts_read, require_contacts_write,
    require_leads_read, require_leads_write,
    require_opportunities_read, require_opportunities_write,
    require_admin_role, require_sales_role, require_marketing_or_sales_role,
    has_permission, has_any_permission, has_all_permissions
)

__all__ = [
    "get_current_user", "get_auth_service", "get_user_service", 
    "get_postgres_db", "get_mongo_db",
    "require_permission", "require_any_permission", "require_all_permissions",
    "require_users_read", "require_users_write",
    "require_companies_read", "require_companies_write",
    "require_contacts_read", "require_contacts_write",
    "require_leads_read", "require_leads_write",
    "require_opportunities_read", "require_opportunities_write",
    "require_admin_role", "require_sales_role", "require_marketing_or_sales_role",
    "has_permission", "has_any_permission", "has_all_permissions"
]