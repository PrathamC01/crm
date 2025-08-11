"""
API routers for CRM application
"""
from .front import health
from .sso import auth

__all__ = ["health", "auth"]