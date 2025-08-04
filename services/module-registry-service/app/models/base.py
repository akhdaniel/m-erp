"""
Base model classes for Module Registry Service
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func
from app.core.database import Base


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class CompanyBaseModel(BaseModel):
    """Base model with company isolation support"""
    __abstract__ = True
    
    company_id = Column(Integer, nullable=True, index=True)  # Nullable for global modules