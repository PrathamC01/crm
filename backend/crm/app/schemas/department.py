"""
Department related schemas
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Department name must be at least 2 characters long')
        return v.strip()

    class Config:
        from_attributes = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v or len(v.strip()) < 2:
                raise ValueError('Department name must be at least 2 characters long')
            return v.strip()
        return v

    class Config:
        from_attributes = True


class DepartmentResponse(DepartmentBase):
    id: int
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True