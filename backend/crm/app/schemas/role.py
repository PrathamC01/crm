"""
Role related schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Role name must be at least 2 characters long')
        return v.strip().lower().replace(' ', '_')

    class Config:
        from_attributes = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v or len(v.strip()) < 2:
                raise ValueError('Role name must be at least 2 characters long')
            return v.strip().lower().replace(' ', '_')
        return v

    class Config:
        from_attributes = True


class RoleResponse(RoleBase):
    id: int
    created_on: datetime
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True