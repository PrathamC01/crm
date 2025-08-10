"""
Common Schemas for Enterprise CRM
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime
from enum import Enum

# Generic Types
T = TypeVar('T')

# Standard Response Format
class StandardResponse(BaseModel):
    status: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    pages: int

class ApprovalRequest(BaseModel):
    decision: str = Field(..., regex="^(approved|rejected)$")
    comments: Optional[str] = None

class ApprovalResponse(BaseModel):
    is_approved: bool
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

# Filter and Sort Options
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class BaseFilter(BaseModel):
    search: Optional[str] = None
    is_active: Optional[bool] = True
    sort_by: Optional[str] = "created_at"
    sort_order: SortOrder = SortOrder.DESC
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

# Common Base Schemas
class BaseCreateSchema(BaseModel):
    pass

class BaseUpdateSchema(BaseModel):
    pass

class BaseResponseSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True