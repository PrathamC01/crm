"""
Category Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    status: bool = True
    message: str = "Categories retrieved successfully"
    data: list[CategoryResponse]
    total: int
    page: int
    limit: int


class CategoryDetailResponse(BaseModel):
    status: bool = True
    message: str = "Category retrieved successfully"
    data: CategoryResponse