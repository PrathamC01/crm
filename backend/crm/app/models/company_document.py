"""
SQLAlchemy Company Document model
"""
from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class CompanyDocument(BaseModel):
    __tablename__ = 'company_documents'
    
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    filename = Column(String(255), nullable=False)  # Generated filename
    original_filename = Column(String(255), nullable=False)  # Original filename
    file_path = Column(String(500), nullable=False)  # Full file path
    file_size = Column(Integer, nullable=False)  # File size in bytes
    document_type = Column(String(50), nullable=False)  # Type of document (GST, PAN, etc.)
    mime_type = Column(String(100), nullable=True)  # MIME type
    uploaded_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<CompanyDocument(id={self.id}, company_id={self.company_id}, filename={self.filename})>"