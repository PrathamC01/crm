"""
Base Models for Enterprise CRM
"""
import uuid
import random
import string
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime
import enum

# Create Base class
Base = declarative_base()

class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

def generate_code(prefix: str, length: int = 16) -> str:
    """Generate alphanumeric code with prefix"""
    remaining_length = length - len(prefix)
    if remaining_length <= 0:
        remaining_length = 6
    
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(characters, k=remaining_length))
    return f"{prefix}{random_part}"

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

class ApprovalBaseModel(BaseModel):
    """Base model for entities requiring approval"""
    __abstract__ = True
    
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    @hybrid_property
    def is_approved(self):
        return self.approval_status == ApprovalStatusEnum.APPROVED