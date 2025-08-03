from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)

    @declared_attr
    def is_active(cls):
        return Column(Boolean, default=True, nullable=False)

    @declared_attr
    def created_on(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_on(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def deleted_on(cls):
        return Column(DateTime, nullable=True)

    @declared_attr
    def created_by(cls):
        return Column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def updated_by(cls):
        return Column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def deleted_by(cls):
        return Column(Integer, ForeignKey("users.id"), nullable=True)

    @declared_attr
    def creator(cls):
        return relationship("User", foreign_keys=[cls.created_by])

    @declared_attr
    def updater(cls):
        return relationship("User", foreign_keys=[cls.updated_by])

    @declared_attr
    def deleter(cls):
        return relationship("User", foreign_keys=[cls.deleted_by])
