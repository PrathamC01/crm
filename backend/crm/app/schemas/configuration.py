"""
Configuration Schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ConfigurationBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    config_schema: Optional[str] = None
    default_config: Optional[str] = None


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    config_schema: Optional[str] = None
    default_config: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigurationResponse(ConfigurationBase):
    id: int
    is_active: bool
    created_on: datetime
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConfigurationListResponse(BaseModel):
    status: bool = True
    message: str = "Configurations retrieved successfully"
    data: list[ConfigurationResponse]
    total: int
    page: int
    limit: int


class ConfigurationDetailResponse(BaseModel):
    status: bool = True
    message: str = "Configuration retrieved successfully"
    data: ConfigurationResponse