"""
Sub Category Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class SubCategoryBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


class SubCategoryCreate(SubCategoryBase):
    pass


class SubCategoryUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class SubCategoryResponse(SubCategoryBase):
    id: int
    category_name: Optional[str] = None
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubCategoryListResponse(BaseModel):
    status: bool = True
    message: str = "Sub categories retrieved successfully"
    data: list[SubCategoryResponse]
    total: int
    page: int
    limit: int


class SubCategoryDetailResponse(BaseModel):
    status: bool = True
    message: str = "Sub category retrieved successfully"
    data: SubCategoryResponse