"""
Contact related schemas
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from ..utils.validators import validate_phone_number, sanitize_phone_number


class ContactBase(BaseModel):
    salutation: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    designation: Optional[str] = None
    email: EmailStr
    primary_phone: Optional[str] = None
    company_id: int
    decision_maker: bool = False
    decision_maker_percentage: Optional[str] = None
    comments: Optional[str] = None

    @validator("first_name", "last_name")
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v.strip()

    @validator("primary_phone")
    def validate_phone(cls, v):
        if v:
            if not validate_phone_number(v):
                raise ValueError(
                    "Invalid phone number format. Use Indian format: +91-9876543210 or 9876543210"
                )
            return sanitize_phone_number(v)
        return v


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    salutation: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    company_id: Optional[int] = None
    decision_maker: Optional[bool] = None
    decision_maker_percentage: Optional[str] = None
    comments: Optional[str] = None

    @validator("primary_phone")
    def validate_phone(cls, v):
        if v:
            if not validate_phone_number(v):
                raise ValueError("Invalid phone number format")
            return sanitize_phone_number(v)
        return v


class ContactResponse(ContactBase):
    id: int
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
    limit: Optional[int] = None

    class Config:
        from_attributes = True


class ContactStats(BaseModel):
    total_contacts: int = 0
    active_contacts: int = 0
    company_breakdown: dict = {}

    class Config:
        from_attributes = True
