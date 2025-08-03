"""
Portal API routes
"""
from .users import router as users_router
from .companies import router as companies_router
from .contacts import router as contacts_router
from .leads import router as leads_router
from .opportunities import router as opportunities_router

__all__ = [
    "users_router", 
    "companies_router", 
    "contacts_router", 
    "leads_router", 
    "opportunities_router"
]