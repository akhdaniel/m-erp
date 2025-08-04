"""
Audit Log model for storing all business events.
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuditLog(Base):
    """
    Audit log entry for tracking all business events in the system.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(255), nullable=False, index=True, comment="Original event ID from message queue")
    event_type = Column(String(100), nullable=False, index=True, comment="Type of event (user.created, company.updated, etc.)")
    entity_type = Column(String(50), nullable=False, index=True, comment="Type of entity affected (user, company, partner, etc.)")
    entity_id = Column(String(100), nullable=False, index=True, comment="ID of the affected entity")
    company_id = Column(Integer, nullable=True, index=True, comment="Company context for multi-tenant operations")
    user_id = Column(Integer, nullable=True, index=True, comment="User who triggered the event")
    source_service = Column(String(100), nullable=False, index=True, comment="Service that generated the event")
    correlation_id = Column(String(255), nullable=True, index=True, comment="Correlation ID for tracking related events")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True, comment="When the event occurred")
    before_data = Column(JSON, nullable=True, comment="Entity state before the event")
    after_data = Column(JSON, nullable=True, comment="Entity state after the event")
    changes = Column(JSON, nullable=True, comment="Specific fields that changed")
    event_metadata = Column(JSON, nullable=True, comment="Additional event metadata")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="When this audit log was created")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', entity_type='{self.entity_type}', entity_id='{self.entity_id}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "source_service": self.source_service,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "before_data": self.before_data,
            "after_data": self.after_data,
            "changes": self.changes,
            "metadata": self.event_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def get_action_description(self) -> str:
        """Get human-readable action description."""
        action_map = {
            "user.created": "User account created",
            "user.updated": "User profile updated",
            "user.deleted": "User account deleted",
            "user.logged_in": "User logged in",
            "user.logged_out": "User logged out",
            "user.password_changed": "Password changed",
            "user.locked": "Account locked",
            "user.unlocked": "Account unlocked",
            "company.created": "Company created",
            "company.updated": "Company details updated",
            "company.activated": "Company activated",
            "company.deactivated": "Company deactivated",
            "partner.created": "Partner created",
            "partner.updated": "Partner details updated",
            "partner.address_added": "Partner address added",
            "partner.contact_added": "Partner contact added",
            "currency.rate_updated": "Currency exchange rate updated",
            "security.violation": "Security violation detected"
        }
        return action_map.get(self.event_type, self.event_type)
    
    def get_summary(self) -> str:
        """Get one-line summary of the audit log."""
        action = self.get_action_description()
        entity_desc = f"{self.entity_type} #{self.entity_id}"
        
        if self.user_id:
            return f"{action} for {entity_desc} by user #{self.user_id}"
        else:
            return f"{action} for {entity_desc} (system)"
    
    def get_changes_summary(self) -> Optional[str]:
        """Get summary of changes made."""
        if not self.changes:
            return None
        
        if isinstance(self.changes, dict):
            change_descriptions = []
            for field, change in self.changes.items():
                if isinstance(change, dict) and 'from' in change and 'to' in change:
                    change_descriptions.append(f"{field}: '{change['from']}' → '{change['to']}'")
                else:
                    change_descriptions.append(f"{field}: {change}")
            return "; ".join(change_descriptions)
        
        return str(self.changes)