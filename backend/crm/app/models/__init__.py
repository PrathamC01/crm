"""
Database models for CRM application
"""
from .user import User
from .role import Role
from .department import Department
from .company import Company
from .contact import Contact
from .lead import Lead
from .opportunity import Opportunity

__all__ = [
    "User", 
    "Role", 
    "Department", 
    "Company", 
    "Contact", 
    "Lead", 
    "Opportunity"
]