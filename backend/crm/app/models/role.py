"""
SQLAlchemy Role model
"""

from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))
    permissions = Column(JSON, default=list)

    # Relationships
    users = relationship("User", back_populates="role", foreign_keys="[User.role_id]")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, permissions={self.permissions})>"
