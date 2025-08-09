"""
Enhanced User related schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    username: str
    role_id: Optional[int] = None
    department_id: Optional[int] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, dots, and underscores')
        return v.strip().lower()

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserLogin(BaseModel):
    email_or_username: str
    password: str

    class Config:
        from_attributes = True

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v.strip()) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not v.replace('_', '').replace('.', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, dots, and underscores')
            return v.strip().lower()
        return v

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(UserBase):
    id: int
    role_name: Optional[str] = None
    department_name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    skip: int
    limit: int

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Role name must be at least 2 characters long')
        return v.strip().lower().replace(' ', '_')

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleResponse(RoleBase):
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    head_user_id: Optional[int] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Department name must be at least 2 characters long')
        return v.strip()

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    head_user_id: Optional[int] = None

class DepartmentResponse(DepartmentBase):
    id: int
    head_user_name: Optional[str] = None
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserPermissions(BaseModel):
    """User permissions for RBAC"""
    user_id: int
    role_name: str
    permissions: List[str]
    can_read_users: bool = False
    can_write_users: bool = False
    can_read_companies: bool = False
    can_write_companies: bool = False
    can_read_contacts: bool = False
    can_write_contacts: bool = False
    can_read_leads: bool = False
    can_write_leads: bool = False
    can_read_opportunities: bool = False
    can_write_opportunities: bool = False