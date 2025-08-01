"""
Mixins for Business Object Framework.

Provides core functionality that can be mixed into business objects:
- BusinessObjectMixin: Common fields and base functionality
- AuditableMixin: Automatic audit logging integration
- EventPublisherMixin: Automatic event publishing integration
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.asyncio import AsyncSession

# Import existing messaging system
from messaging import MessagePublisher, EventType


class BusinessObjectMixin:
    """
    Core business object functionality mixin.
    
    Provides common fields and methods that all business objects should have:
    - Standard ID field
    - Created/updated timestamps
    - Framework version tracking
    - String representation methods
    """
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    framework_version = Column(String(20), default="1.0.0", nullable=False, server_default="1.0.0")
    
    def __str__(self) -> str:
        """String representation showing model name and key fields."""
        class_name = self.__class__.__name__
        
        # Try to find a name or title field for display
        display_value = None
        for attr_name in ['name', 'title', 'code', 'email']:
            if hasattr(self, attr_name) and getattr(self, attr_name):
                display_value = getattr(self, attr_name)
                break
        
        if display_value:
            return f"{class_name}(id={self.id}, name='{display_value}')"
        else:
            return f"{class_name}(id={self.id})"
    
    def __repr__(self) -> str:
        """Detailed representation showing model name and ID."""
        return f"{self.__class__.__name__}(id={self.id})"


class AuditableMixin:
    """
    Automatic audit logging integration mixin.
    
    Provides methods to automatically capture state changes and send
    them to the audit service for compliance and tracking purposes.
    """
    
    def _capture_before_state(self) -> Dict[str, Any]:
        """
        Capture the current state of the object before changes.
        
        Returns:
            Dictionary containing current field values
        """
        state = {}
        
        # Get all column names from the model
        for column in self.__table__.columns:
            column_name = column.name
            value = getattr(self, column_name, None)
            
            # Convert complex types to serializable format
            if isinstance(value, datetime):
                state[column_name] = value.isoformat()
            elif value is not None:
                state[column_name] = value
        
        return state
    
    def _capture_after_state(self) -> Dict[str, Any]:
        """
        Capture the state of the object after changes.
        
        Returns:
            Dictionary containing current field values
        """
        # Same implementation as before state - captures current values
        return self._capture_before_state()
    
    def _get_changed_fields(self, before_state: Dict[str, Any], after_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare before and after states to identify changed fields.
        
        Args:
            before_state: State before changes
            after_state: State after changes
            
        Returns:
            Dictionary of changed fields with from/to values
        """
        changes = {}
        
        # Find all fields that exist in either state
        all_fields = set(before_state.keys()) | set(after_state.keys())
        
        for field in all_fields:
            before_value = before_state.get(field)
            after_value = after_state.get(field)
            
            # Skip if values are the same
            if before_value == after_value:
                continue
            
            # Record the change
            changes[field] = {
                'from': before_value,
                'to': after_value
            }
        
        return changes
    
    async def _send_audit_log(
        self,
        event_type: str,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Send audit log entry to the audit service.
        
        Args:
            event_type: Type of event (e.g., "partner.created")
            before_data: State before the change
            after_data: State after the change
            changes: Dictionary of specific changes
            user_id: ID of user who made the change
            correlation_id: Correlation ID for tracking
        """
        try:
            # Create message publisher instance
            publisher = MessagePublisher("business-object-framework")
            await publisher.connect()
            
            try:
                # Extract entity information
                entity_type = self.__class__.__name__
                entity_id = str(getattr(self, 'id', 'unknown'))
                company_id = getattr(self, 'company_id', None)
                
                # Publish audit event using existing messaging system
                await publisher.publish_event(
                    event_type=event_type,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    company_id=company_id,
                    user_id=user_id,
                    before_data=before_data,
                    after_data=after_data,
                    changes=changes,
                    correlation_id=correlation_id
                )
            finally:
                await publisher.disconnect()
            
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send audit log for {entity_type}:{entity_id}: {e}")


class EventPublisherMixin:
    """
    Automatic event publishing integration mixin.
    
    Provides methods to automatically publish business events for
    CRUD operations using the existing Redis Streams messaging system.
    """
    
    def _get_entity_type(self) -> str:
        """
        Get the entity type name from the model class.
        
        Returns:
            Entity type string
        """
        return self.__class__.__name__
    
    def _get_event_type_for_operation(self, operation: str) -> str:
        """
        Generate event type string for the given operation.
        
        Args:
            operation: Operation type (CREATE, UPDATE, DELETE)
            
        Returns:
            Event type string (e.g., "partner.created")
        """
        entity_name = self.__class__.__name__.lower()
        
        operation_map = {
            'CREATE': 'created',
            'UPDATE': 'updated', 
            'DELETE': 'deleted'
        }
        
        operation_suffix = operation_map.get(operation, operation.lower())
        return f"{entity_name}.{operation_suffix}"
    
    async def _publish_event(
        self,
        operation: str,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Publish business event for the operation.
        
        Args:
            operation: Type of operation (CREATE, UPDATE, DELETE)
            before_data: State before the change
            after_data: State after the change
            changes: Dictionary of specific changes
            user_id: ID of user who made the change
            correlation_id: Correlation ID for tracking
        """
        try:
            # Create message publisher instance
            publisher = MessagePublisher("business-object-framework")
            await publisher.connect()
            
            try:
                # Generate event type
                event_type = self._get_event_type_for_operation(operation)
                
                # Extract entity information
                entity_type = self._get_entity_type()
                entity_id = getattr(self, 'id', None)
                company_id = getattr(self, 'company_id', None)
                
                # Publish event using existing messaging system
                await publisher.publish_event(
                    event_type=event_type,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    company_id=company_id,
                    user_id=user_id,
                    before_data=before_data,
                    after_data=after_data,
                    changes=changes,
                    correlation_id=correlation_id
                )
            finally:
                await publisher.disconnect()
            
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to publish event for {self._get_entity_type()}:{getattr(self, 'id', 'unknown')}: {e}")