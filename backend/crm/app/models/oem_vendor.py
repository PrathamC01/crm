"""
OEM/Vendor Master Model
"""
from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel


class OEMVendor(BaseModel):
    __tablename__ = 'oem_vendors'
    
    name = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(2), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="oem_vendor")
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_oem_vendor_name'),
        UniqueConstraint('abbreviation', name='uq_oem_vendor_abbreviation'),
    )
    
    def __repr__(self):
        return f"<OEMVendor(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'description': self.description,
            'website': self.website,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'is_active': self.is_active,
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'updated_on': self.updated_on.isoformat() if self.updated_on else None
        }