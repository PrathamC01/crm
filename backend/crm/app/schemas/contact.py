"""
Contact related schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime
from ..utils.validators import validate_phone_number, sanitize_phone_number

class ContactBase(BaseModel):
    full_name: str
    designation: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    company_id: int
    role_type: Literal['Admin', 'Influencer', 'Decision Maker']

    @validator('full_name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()

    @validator('phone_number')
    def validate_phone(cls, v):
        if v:
            if not validate_phone_number(v):
                raise ValueError('Invalid phone number format. Use Indian format: +91-9876543210 or 9876543210')
            v = sanitize_phone_number(v)
        return v

    @validator('role_type')
    def validate_role_type(cls, v):
        valid_roles = ['Admin', 'Influencer', 'Decision Maker']
        if v not in valid_roles:
            raise ValueError(f'Role type must be one of: {valid_roles}')
        return v

class ContactCreate(ContactBase):
    business_card_file: Optional[str] = None  # Will be file path after upload

class ContactUpdate(BaseModel):
    full_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    company_id: Optional[int] = None
    role_type: Optional[Literal['Admin', 'Influencer', 'Decision Maker']] = None
    business_card_file: Optional[str] = None

    @validator('phone_number')
    def validate_phone(cls, v):
        if v:
            if not validate_phone_number(v):
                raise ValueError('Invalid phone number format')
            v = sanitize_phone_number(v)
        return v

class ContactResponse(ContactBase):
    id: int
    business_card_path: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContactListResponse(BaseModel):
    contacts: list[ContactResponse]
    total: int
    skip: int
    limit: int

class BusinessCardUpload(BaseModel):
    """Schema for business card file upload"""
    contact_id: int
    file_name: str
    file_content: bytes
    content_type: str

    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if v not in allowed_types:
            raise ValueError(f'File type must be one of: {allowed_types}')
        return v

    @validator('file_content')
    def validate_file_size(cls, v):
        max_size = 5 * 1024 * 1024  # 5MB
        if len(v) > max_size:
            raise ValueError('File size must not exceed 5MB')
        return v


class ContactListResponse(BaseModel):
    contacts: list[ContactResponse]
    total: int
    skip: int
    limit: Optional[int] = None

    class Config:
        from_attributes = True


class ContactStats(BaseModel):
    total_contacts: int = 0
    active_contacts: int = 0
    role_breakdown: dict = {}
    company_breakdown: dict = {}

    class Config:
        from_attributes = True