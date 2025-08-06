"""
Product Type Master Model
"""
from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class ProductType(BaseModel):
    __tablename__ = 'product_types'
    
    name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(2), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="product_type")
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_product_type_name'),
        UniqueConstraint('abbreviation', name='uq_product_type_abbreviation'),
    )
    
    def __repr__(self):
        return f"<ProductType(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'description': self.description,
            'is_active': self.is_active,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'updated_on': self.updated_on.isoformat() if self.updated_on else None
        }