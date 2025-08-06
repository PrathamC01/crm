"""
Product Type Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProductTypeBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None


class ProductTypeCreate(ProductTypeBase):
    pass


class ProductTypeUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductTypeResponse(ProductTypeBase):
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductTypeListResponse(BaseModel):
    status: bool = True
    message: str = "Product types retrieved successfully"
    data: list[ProductTypeResponse]
    total: int
    page: int
    limit: int


class ProductTypeDetailResponse(BaseModel):
    status: bool = True
    message: str = "Product type retrieved successfully"
    data: ProductTypeResponse