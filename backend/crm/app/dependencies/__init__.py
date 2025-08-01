"""
Dependency injection for CRM application
"""
from .auth import get_current_user, get_auth_service, get_user_service
from .database import get_postgres_pool, get_mongo_db

__all__ = ["get_current_user", "get_auth_service", "get_user_service", "get_postgres_pool", "get_mongo_db"]