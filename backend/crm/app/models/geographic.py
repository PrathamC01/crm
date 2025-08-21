"""
SQLAlchemy models for geographic data (Countries, States, Cities)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Country(Base):
    """Country model with states relationship"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(3), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    states = relationship("State", back_populates="country", cascade="all, delete-orphan")


class State(Base):
    """State model with country and cities relationships"""
    __tablename__ = "states"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    country = relationship("Country", back_populates="states")
    cities = relationship("City", back_populates="state", cascade="all, delete-orphan")


class City(Base):
    """City model with state relationship"""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    state = relationship("State", back_populates="cities")
    companies = relationship("Company", back_populates="city")