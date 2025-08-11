"""
SQLAlchemy Department model
"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel


class Department(BaseModel):
    __tablename__ = "departments"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))

    # Relationships
    users = relationship(
        "User", back_populates="department", foreign_keys="[User.department_id]"
    )

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name})>"
