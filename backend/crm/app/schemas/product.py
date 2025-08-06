"""
Product Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_type_id: int
    category_id: int
    sub_category_id: Optional[int] = None
    oem_vendor_id: Optional[int] = None
    configuration_id: Optional[int] = None
    product_config: Optional[str] = None
    specifications: Optional[str] = None
    warranty_period: Optional[str] = None
    unit_of_measure: Optional[str] = "PCS"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_type_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    oem_vendor_id: Optional[int] = None
    configuration_id: Optional[int] = None
    product_config: Optional[str] = None
    specifications: Optional[str] = None
    warranty_period: Optional[str] = None
    unit_of_measure: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    sku_code: str
    product_type_name: Optional[str] = None
    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None
    oem_vendor_name: Optional[str] = None
    configuration_name: Optional[str] = None
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    status: bool = True
    message: str = "Products retrieved successfully"
    data: list[ProductResponse]
    total: int
    page: int
    limit: int


class ProductDetailResponse(BaseModel):
    status: bool = True
    message: str = "Product retrieved successfully"
    data: ProductResponse


# Schema for creating category from within product form
class InlineCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None