"""
Company related schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, Any
from datetime import datetime
from ..utils.validators import (
    validate_gst_number,
    validate_pan_number,
    sanitize_gst_number,
    sanitize_pan_number,
)


class CompanyBase(BaseModel):
    name: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    parent_company_id: Optional[int] = None
    industry_category: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters long")
        return v.strip()

    @validator("gst_number")
    def validate_gst(cls, v):
        if v:
            v = sanitize_gst_number(v)
            if not validate_gst_number(v):
                raise ValueError(
                    "Invalid GST number format. Expected format: 22AAAAA0000A1Z5"
                )
        return v

    @validator("pan_number")
    def validate_pan(cls, v):
        if v:
            v = sanitize_pan_number(v)
            if not validate_pan_number(v):
                raise ValueError(
                    "Invalid PAN number format. Expected format: AAAAA0000A"
                )
        return v

    @validator("website")
    def validate_website(cls, v):
        if v and not v.startswith(("http://", "https://")):
            v = "https://" + v
        return v


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    parent_company_id: Optional[int] = None
    industry_category: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

    @validator("gst_number")
    def validate_gst(cls, v):
        if v:
            v = sanitize_gst_number(v)
            if not validate_gst_number(v):
                raise ValueError("Invalid GST number format")
        return v

    @validator("pan_number")
    def validate_pan(cls, v):
        if v:
            v = sanitize_pan_number(v)
            if not validate_pan_number(v):
                raise ValueError("Invalid PAN number format")
        return v


class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    parent_company_name: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True  # Crucial!


class CompanyListResponse(BaseModel):
    companies: list[CompanyResponse]
    total: int
    skip: int
    limit: Optional[int] = None

    class Config:
        orm_mode = True  # Crucial!


class CompanyStats(BaseModel):
    total_companies: int = 0
    active_companies: int = 0
    inactive_companies: int = 0
    industry_breakdown: dict = {}

    class Config:
        from_attributes = True
