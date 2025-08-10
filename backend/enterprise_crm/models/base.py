"""
Base model configuration for Enterprise CRM
"""
from sqlalchemy import Column, Integer, DateTime, Boolean, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

class ApprovalBaseModel(BaseModel):
    """Base model for entities requiring approval"""
    __abstract__ = True
    
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
def generate_code(prefix: str, length: int = 16) -> str:
    """Generate alphanumeric code with prefix"""
    code = str(uuid.uuid4()).replace('-', '').upper()[:length-len(prefix)]
    return f"{prefix}{code}"