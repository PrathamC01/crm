"""
Configuration Master Model
"""
from sqlalchemy import Column, String, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class Configuration(BaseModel):
    __tablename__ = 'configurations'
    
    name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(2), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    config_schema = Column(Text, nullable=True)  # JSON schema for validation
    default_config = Column(Text, nullable=True)  # Default JSON configuration
    
    # Relationships
    products = relationship("Product", back_populates="configuration")
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_configuration_name'),
        UniqueConstraint('abbreviation', name='uq_configuration_abbreviation'),
    )
    
    def __repr__(self):
        return f"<Configuration(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'description': self.description,
            'config_schema': self.config_schema,
            'default_config': self.default_config,
            'is_active': self.is_active,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'updated_on': self.updated_on.isoformat() if self.updated_on else None
        }