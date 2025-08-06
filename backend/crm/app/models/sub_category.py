"""
Sub Category Master Model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class SubCategory(BaseModel):
    __tablename__ = 'sub_categories'
    
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(2), nullable=False)
    description = Column(String(500), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # Optional parent category
    
    # Relationships
    category = relationship("Category", backref="sub_categories")
    products = relationship("Product", back_populates="sub_category")
    
    __table_args__ = (
        UniqueConstraint('name', 'category_id', name='uq_sub_category_name_category'),
        UniqueConstraint('abbreviation', 'category_id', name='uq_sub_category_abbreviation_category'),
    )
    
    def __repr__(self):
        return f"<SubCategory(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'is_active': self.is_active,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'updated_on': self.updated_on.isoformat() if self.updated_on else None
        }