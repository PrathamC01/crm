"""
Authentication related schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class LoginRequest(BaseModel):
    email_or_username: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    username: str
    role_name: str
    department_name: str
    is_active: bool

class StandardResponse(BaseModel):
    status: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class TokenData(BaseModel):
    token: str

class TokenResponse(StandardResponse):
    data: Optional[TokenData] = None