"""
Base model with common fields for all entities
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """Abstract base model with common audit fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_on = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    deleted_by = Column(Integer, ForeignKey('users.id'), nullable=True)