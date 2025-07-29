"""
Password history model for tracking password reuse prevention.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class PasswordHistory(Base):
    """Password history model for preventing password reuse."""
    
    __tablename__ = "password_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="password_history")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_password_history_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<PasswordHistory(user_id={self.user_id}, created_at={self.created_at})>"