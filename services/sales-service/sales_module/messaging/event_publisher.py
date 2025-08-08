"""
Event publishing infrastructure for sales module.

Integrates with the existing Redis Streams messaging system
used throughout the XERPIUM platform for event-driven architecture.
"""

import json
import redis
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class SalesEventPublisher:
    """
    Publisher for sales-related events using Redis Streams.
    
    Integrates with the XERPIUM event-driven architecture to publish
    quote, order, and approval events for system integration.
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379,
                 redis_db: int = 0, stream_prefix: str = "sales"):
        """
        Initialize event publisher.
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            stream_prefix: Prefix for stream names
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.stream_prefix = stream_prefix
    
    def publish_quote_event(self, event_type: str, quote_data: Dict[str, Any], 
                           user_id: int = None, company_id: int = None) -> bool:
        """
        Publish quote-related event.
        
        Args:
            event_type: Type of event (created, updated, sent, etc.)
            quote_data: Quote information
            user_id: ID of user triggering the event
            company_id: Company ID for isolation
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            event = self._create_event_payload(
                event_type=f"quote.{event_type}",
                entity_type="quote",
                entity_data=quote_data,
                user_id=user_id,
                company_id=company_id
            )
            
            stream_name = f"{self.stream_prefix}:quote_events"
            message_id = self.redis_client.xadd(stream_name, event)
            
            logger.info(f"Published quote event {event_type} with ID {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish quote event {event_type}: {e}")
            return False
    
    def publish_approval_event(self, event_type: str, approval_data: Dict[str, Any],
                              user_id: int = None, company_id: int = None) -> bool:
        """
        Publish approval-related event.
        
        Args:
            event_type: Type of event (requested, approved, rejected, escalated)
            approval_data: Approval information
            user_id: ID of user triggering the event
            company_id: Company ID for isolation
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            event = self._create_event_payload(
                event_type=f"approval.{event_type}",
                entity_type="quote_approval",
                entity_data=approval_data,
                user_id=user_id,
                company_id=company_id
            )
            
            stream_name = f"{self.stream_prefix}:approval_events"
            message_id = self.redis_client.xadd(stream_name, event)
            
            logger.info(f"Published approval event {event_type} with ID {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish approval event {event_type}: {e}")
            return False
    
    def publish_inventory_event(self, event_type: str, inventory_data: Dict[str, Any],
                               user_id: int = None, company_id: int = None) -> bool:
        """
        Publish inventory-related event.
        
        Args:
            event_type: Type of event (reserved, released, validated)
            inventory_data: Inventory information
            user_id: ID of user triggering the event
            company_id: Company ID for isolation
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            event = self._create_event_payload(
                event_type=f"inventory.{event_type}",
                entity_type="inventory_operation",
                entity_data=inventory_data,
                user_id=user_id,
                company_id=company_id
            )
            
            stream_name = f"{self.stream_prefix}:inventory_events"
            message_id = self.redis_client.xadd(stream_name, event)
            
            logger.info(f"Published inventory event {event_type} with ID {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish inventory event {event_type}: {e}")
            return False
    
    def publish_analytics_event(self, event_type: str, analytics_data: Dict[str, Any],
                               user_id: int = None, company_id: int = None) -> bool:
        """
        Publish analytics-related event.
        
        Args:
            event_type: Type of event (quote_converted, target_achieved, etc.)
            analytics_data: Analytics information
            user_id: ID of user triggering the event
            company_id: Company ID for isolation
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            event = self._create_event_payload(
                event_type=f"analytics.{event_type}",
                entity_type="sales_metric",
                entity_data=analytics_data,
                user_id=user_id,
                company_id=company_id
            )
            
            stream_name = f"{self.stream_prefix}:analytics_events"
            message_id = self.redis_client.xadd(stream_name, event)
            
            logger.info(f"Published analytics event {event_type} with ID {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish analytics event {event_type}: {e}")
            return False
    
    def _create_event_payload(self, event_type: str, entity_type: str, 
                             entity_data: Dict[str, Any], user_id: int = None,
                             company_id: int = None) -> Dict[str, str]:
        """
        Create standardized event payload.
        
        Args:
            event_type: Type of event
            entity_type: Type of entity
            entity_data: Entity data
            user_id: User ID
            company_id: Company ID
            
        Returns:
            Event payload dictionary
        """
        event_payload = {
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_data": self._serialize_entity_data(entity_data),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "sales-service",
            "version": "1.0.0"
        }
        
        if user_id:
            event_payload["user_id"] = str(user_id)
        
        if company_id:
            event_payload["company_id"] = str(company_id)
        
        # Add correlation ID for tracking
        event_payload["correlation_id"] = self._generate_correlation_id()
        
        return event_payload
    
    def _serialize_entity_data(self, data: Dict[str, Any]) -> str:
        """
        Serialize entity data for Redis storage.
        
        Args:
            data: Entity data dictionary
            
        Returns:
            JSON serialized string
        """
        def decimal_serializer(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(data, default=decimal_serializer)
    
    def _generate_correlation_id(self) -> str:
        """
        Generate correlation ID for event tracking.
        
        Returns:
            Correlation ID string
        """
        import uuid
        return str(uuid.uuid4())
    
    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False


# Singleton instance for dependency injection
sales_event_publisher = SalesEventPublisher()