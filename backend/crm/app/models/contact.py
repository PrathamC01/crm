from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Contact(BaseModel):
    __tablename__ = "contacts"

    salutation = Column(String(10))
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    designation = Column(String(100))
    email = Column(String(255), unique=True, nullable=False, index=True)
    primary_phone = Column(String(20))
    decision_maker = Column(Boolean, default=False)
    decision_maker_percentage = Column(String(10))
    comments = Column(String(500))

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Relationships
    company = relationship(
        "Company", foreign_keys="Contact.company_id", back_populates="contacts"
    )
    creator = relationship(
        "User", foreign_keys="Contact.created_by", back_populates="contacts_created"
    )
    updater = relationship(
        "User", foreign_keys="Contact.updated_by", back_populates="contacts_updated"
    )

    opportunities = relationship("Opportunity", back_populates="contact")

    def __repr__(self):
        return f"<Contact(id={self.id}, full_name={self.first_name} {self.last_name}, company_name={self.company.name})>"
