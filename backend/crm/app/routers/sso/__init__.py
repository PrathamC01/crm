"""
SSO/Authentication API routes
"""
from .auth import router as auth_router
from .dashboard import router as dashboard_router

# Re-export for convenience
auth = auth_router
dashboard = dashboard_router