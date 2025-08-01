"""
Pydantic schemas for CRM application
"""
from .auth import LoginRequest, UserResponse, StandardResponse
from .user import UserCreate, UserUpdate

__all__ = ["LoginRequest", "UserResponse", "StandardResponse", "UserCreate", "UserUpdate"]