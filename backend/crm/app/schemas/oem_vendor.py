"""
OEM/Vendor Schemas
"""
from pydantic import BaseModel, validator, EmailStr
from typing import Optional
from datetime import datetime


class OEMVendorBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class OEMVendorCreate(OEMVendorBase):
    pass


class OEMVendorUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class OEMVendorResponse(OEMVendorBase):
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OEMVendorListResponse(BaseModel):
    status: bool = True
    message: str = "OEM/Vendors retrieved successfully"
    data: list[OEMVendorResponse]
    total: int
    page: int
    limit: int


class OEMVendorDetailResponse(BaseModel):
    status: bool = True
    message: str = "OEM/Vendor retrieved successfully"
    data: OEMVendorResponse