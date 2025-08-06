"""
Product Master Model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class Product(BaseModel):
    __tablename__ = 'products'
    
    name = Column(String(255), nullable=False)
    sku_code = Column(String(16), nullable=False, unique=True)  # Auto-generated 16-digit alphanumeric
    description = Column(Text, nullable=True)
    
    # Foreign Keys to Category Masters
    product_type_id = Column(Integer, ForeignKey('product_types.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)  
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'), nullable=True)
    oem_vendor_id = Column(Integer, ForeignKey('oem_vendors.id'), nullable=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id'), nullable=True)
    
    # Product specific configuration (JSON)
    product_config = Column(Text, nullable=True)
    
    # Additional fields
    specifications = Column(Text, nullable=True)
    warranty_period = Column(String(50), nullable=True)
    unit_of_measure = Column(String(20), nullable=True, default='PCS')
    
    # Relationships
    product_type = relationship("ProductType", back_populates="products")
    category = relationship("Category", back_populates="products")
    sub_category = relationship("SubCategory", back_populates="products")
    oem_vendor = relationship("OEMVendor", back_populates="products")
    configuration = relationship("Configuration", back_populates="products")
    
    __table_args__ = (
        UniqueConstraint('sku_code', name='uq_product_sku_code'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku_code='{self.sku_code}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku_code': self.sku_code,
            'description': self.description,
            'product_type_id': self.product_type_id,
            'product_type_name': self.product_type.name if self.product_type else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'sub_category_id': self.sub_category_id,
            'sub_category_name': self.sub_category.name if self.sub_category else None,
            'oem_vendor_id': self.oem_vendor_id,
            'oem_vendor_name': self.oem_vendor.name if self.oem_vendor else None,
            'configuration_id': self.configuration_id,
            'configuration_name': self.configuration.name if self.configuration else None,
            'product_config': self.product_config,
            'specifications': self.specifications,
            'warranty_period': self.warranty_period,
            'unit_of_measure': self.unit_of_measure,
            'is_active': self.is_active,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'updated_on': self.updated_on.isoformat() if self.updated_on else None
        }