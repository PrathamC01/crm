"""
Master Data Schemas for CRM
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# Enums
class ProductTypeEnum(str, Enum):
    PRODUCT = "product"
    SERVICE = "service"
    OTHER = "other"

class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Standard Response Models (Using from auth schema)
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    pages: int

class BaseFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = True
    sort_by: Optional[str] = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

class ApprovalRequest(BaseModel):
    decision: str = Field(..., pattern="^(approved|rejected)$")
    comments: Optional[str] = None

# Base Response Schema
class BaseResponseSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# UOM Schemas
class UOMCreate(BaseModel):
    uom_name: str = Field(..., min_length=1, max_length=100)
    uom_code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    base_unit: Optional[str] = Field(None, max_length=50)
    conversion_factor_to_base: Optional[float] = Field(None, gt=0)

class UOMUpdate(BaseModel):
    uom_name: Optional[str] = Field(None, min_length=1, max_length=100)
    uom_code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    base_unit: Optional[str] = Field(None, max_length=50)
    conversion_factor_to_base: Optional[float] = Field(None, gt=0)

class UOMResponse(BaseResponseSchema):
    uom_name: str
    uom_code: str
    description: Optional[str] = None
    base_unit: Optional[str] = None
    conversion_factor_to_base: Optional[float] = None

# Product Schemas
class ProductMasterCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)  # Auto-generated if not provided
    cat1_type: ProductTypeEnum
    cat2_category: str = Field(..., min_length=1, max_length=100)
    cat3_sub_category: str = Field(..., min_length=1, max_length=100)
    cat4_oem: Optional[str] = Field(None, max_length=100)
    cat5_configuration: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    uom_ids: List[int] = Field(..., min_items=1)  # At least one UOM required

class ProductMasterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    cat4_oem: Optional[str] = Field(None, max_length=100)
    cat5_configuration: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    uom_ids: Optional[List[int]] = None

class ProductUOMMapResponse(BaseModel):
    uom_id: int
    uom_name: str
    uom_code: str
    conversion_factor: Optional[float] = None
    is_primary: bool
    
    class Config:
        from_attributes = True

class ProductMasterResponse(BaseResponseSchema):
    name: str
    cat1_type: str
    cat2_category: str
    cat3_sub_category: str
    cat4_oem: Optional[str] = None
    cat5_configuration: Optional[Dict[str, Any]] = None
    sku_code: str
    description: Optional[str] = None
    uoms: List[ProductUOMMapResponse] = []

# Price List Schemas
class PriceListCreate(BaseModel):
    price_list_name: str = Field(..., min_length=1, max_length=200)
    valid_upto: date = Field(..., description="Price list validity date")

class PriceListUpdate(BaseModel):
    price_list_name: Optional[str] = Field(None, min_length=1, max_length=200)
    valid_upto: Optional[date] = None

class PriceListResponse(BaseResponseSchema):
    price_list_name: str
    valid_upto: date
    approval_status: str
    approved_by: Optional[int] = None
    approved_at: Optional[date] = None

# Product Pricing Schemas
class ProductPricingCreate(BaseModel):
    price_list_id: int
    uom_id: Optional[int] = None
    group_id: Optional[int] = None
    recurring_input_price: Optional[float] = Field(None, ge=0)
    recurring_selling_price: Optional[float] = Field(None, ge=0)
    otc_input_price: Optional[float] = Field(None, ge=0)
    otc_selling_price: Optional[float] = Field(None, ge=0)
    margin_percent: Optional[float] = Field(None, ge=0, le=100)
    margin_value: Optional[float] = Field(None, ge=0)
    discount_upto_percent: Optional[float] = Field(None, ge=0, le=100)

class ProductPricingUpdate(BaseModel):
    recurring_input_price: Optional[float] = Field(None, ge=0)
    recurring_selling_price: Optional[float] = Field(None, ge=0)
    otc_input_price: Optional[float] = Field(None, ge=0)
    otc_selling_price: Optional[float] = Field(None, ge=0)
    margin_percent: Optional[float] = Field(None, ge=0, le=100)
    margin_value: Optional[float] = Field(None, ge=0)
    discount_upto_percent: Optional[float] = Field(None, ge=0, le=100)

class ProductPricingResponse(BaseResponseSchema):
    price_list_id: int
    product_id: int
    uom_id: Optional[int] = None
    group_id: Optional[int] = None
    recurring_input_price: Optional[float] = None
    recurring_selling_price: Optional[float] = None
    otc_input_price: Optional[float] = None
    otc_selling_price: Optional[float] = None
    margin_percent: Optional[float] = None
    margin_value: Optional[float] = None
    discount_upto_percent: Optional[float] = None
    approval_status: str
    approved_by: Optional[int] = None

# User Management Schemas
class UserMasterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, max_length=20)
    role_id: int
    department_id: int
    designation_id: int
    status: StatusEnum = StatusEnum.ACTIVE

class UserMasterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    status: Optional[StatusEnum] = None

class UserMasterResponse(BaseResponseSchema):
    name: str
    email: str
    phone: Optional[str] = None
    role_id: int
    role_name: Optional[str] = None
    department_id: int
    department_name: Optional[str] = None
    designation_id: int
    designation_name: Optional[str] = None
    status: str

# Lookup Schemas
class DepartmentResponse(BaseModel):
    id: int
    department_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    id: int
    role_name: str
    description: Optional[str] = None
    permissions: Optional[List[int]] = None
    
    class Config:
        from_attributes = True

class DesignationResponse(BaseModel):
    id: int
    designation_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

# State and City Schemas
class StateResponse(BaseModel):
    id: int
    state_name: str
    state_code: str
    
    class Config:
        from_attributes = True

class CityResponse(BaseModel):
    id: int
    city_name: str
    state_id: int
    state_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Industry Category Schema
class IndustryCategoryResponse(BaseModel):
    id: int
    industry_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True