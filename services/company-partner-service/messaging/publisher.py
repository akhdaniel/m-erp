"""
Message Publisher for M-ERP messaging system.
Handles publishing messages to Redis Streams and Pub/Sub channels.
"""
import json
import uuid
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, Union
import redis.asyncio as redis
from redis.asyncio import Redis
import logging

from .config import MessagingConfig
from .schemas import Message, Event, Command, Notification, HealthCheckMessage
from .events import MessageType, EventType, CommandType, NotificationType


logger = logging.getLogger(__name__)


class MessagePublisher:
    """Publishes messages to Redis streams and pub/sub channels."""
    
    def __init__(self, service_name: str, redis_url: Optional[str] = None):
        """
        Initialize the message publisher.
        
        Args:
            service_name: Name of the service publishing messages
            redis_url: Redis connection URL (uses config default if not provided)
        """
        self.service_name = service_name
        self.redis_url = redis_url or MessagingConfig.get_redis_url()
        self.redis_client: Optional[Redis] = None
        self.stream_names = MessagingConfig.get_stream_names()
        self.pubsub_channels = MessagingConfig.get_pubsub_channels()
        
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                max_connections=MessagingConfig.REDIS_MAX_CONNECTIONS,
                socket_connect_timeout=MessagingConfig.REDIS_CONNECTION_TIMEOUT,
                socket_timeout=MessagingConfig.REDIS_SOCKET_TIMEOUT,
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info(f"Message publisher connected to Redis for service: {self.service_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
            
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info(f"Message publisher disconnected for service: {self.service_name}")
    
    async def publish_event(
        self, 
        event_type: EventType,
        entity_type: str,
        entity_id: Union[str, int],
        company_id: Optional[Union[str, int]] = None,
        user_id: Optional[Union[str, int]] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        changes: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish a business event.
        
        Args:
            event_type: Type of event
            entity_type: Type of entity (user, company, partner, etc.)
            entity_id: ID of the affected entity
            company_id: Company context for multi-tenant operations
            user_id: User who triggered the event
            before_data: Entity state before the event
            after_data: Entity state after the event
            changes: Changed fields and their new values
            correlation_id: Correlation ID for tracking
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        event = Event(
            id=str(uuid.uuid4()),
            source_service=self.service_name,
            correlation_id=correlation_id,
            metadata=metadata or {},
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            company_id=company_id,
            user_id=user_id,
            before_data=before_data,
            after_data=after_data,
            changes=changes
        )
        
        return await self._publish_to_stream(self.stream_names["events"], event.dict())
    
    async def publish_command(
        self,
        command_type: CommandType,
        target_service: str,
        payload: Dict[str, Any],
        reply_to: Optional[str] = None,
        timeout: Optional[int] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish a command message.
        
        Args:
            command_type: Type of command
            target_service: Service that should execute the command
            payload: Command parameters
            reply_to: Channel to send response to
            timeout: Command timeout in seconds
            correlation_id: Correlation ID for tracking
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        command = Command(
            id=str(uuid.uuid4()),
            source_service=self.service_name,
            correlation_id=correlation_id,
            metadata=metadata or {},
            command_type=command_type,
            target_service=target_service,
            payload=payload,
            reply_to=reply_to,
            timeout=timeout
        )
        
        return await self._publish_to_stream(self.stream_names["commands"], command.dict())
    
    async def publish_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        target_user_id: Optional[Union[str, int]] = None,
        target_company_id: Optional[Union[str, int]] = None,
        channel: str = "general",
        priority: int = 1,
        expires_at: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish a notification message.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            target_user_id: Specific user to notify
            target_company_id: Company users to notify
            channel: Notification channel
            priority: Priority level (1=low, 2=medium, 3=high)
            expires_at: When notification expires
            correlation_id: Correlation ID for tracking
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        notification = Notification(
            id=str(uuid.uuid4()),
            source_service=self.service_name,
            correlation_id=correlation_id,
            metadata=metadata or {},
            notification_type=notification_type,
            title=title,
            message=message,
            target_user_id=target_user_id,
            target_company_id=target_company_id,
            channel=channel,
            priority=priority,
            expires_at=expires_at
        )
        
        # Publish to both stream (for persistence) and pub/sub (for real-time)
        message_id = await self._publish_to_stream(self.stream_names["notifications"], notification.dict())
        
        # Publish to pub/sub for real-time notifications
        channel_name = f"notifications:{channel}"
        if target_user_id:
            channel_name = f"notifications:user:{target_user_id}"
        elif target_company_id:
            channel_name = f"notifications:company:{target_company_id}"
            
        await self._publish_to_pubsub(channel_name, notification.dict())
        
        return message_id
    
    async def publish_health_check(
        self,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        uptime_seconds: Optional[int] = None,
        version: Optional[str] = None
    ) -> str:
        """
        Publish a health check message.
        
        Args:
            status: Service status (healthy, unhealthy, unknown)
            details: Additional health details
            uptime_seconds: Service uptime in seconds
            version: Service version
            
        Returns:
            Message ID
        """
        health_message = HealthCheckMessage(
            service_name=self.service_name,
            status=status,
            details=details or {},
            uptime_seconds=uptime_seconds,
            version=version
        )
        
        return await self._publish_to_stream(self.stream_names["health"], health_message.dict())
    
    async def publish_generic_message(
        self,
        message_type: MessageType,
        subject: str,
        payload: Dict[str, Any],
        target_service: Optional[str] = None,
        reply_to: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish a generic message.
        
        Args:
            message_type: Type of message
            subject: Subject/topic of the message
            payload: Message payload data
            target_service: Target service (for commands)
            reply_to: Reply channel for response messages
            correlation_id: Correlation ID for tracking
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        message = Message(
            id=str(uuid.uuid4()),
            source_service=self.service_name,
            correlation_id=correlation_id,
            metadata=metadata or {},
            type=message_type,
            subject=subject,
            payload=payload,
            target_service=target_service,
            reply_to=reply_to
        )
        
        # Determine which stream to use based on message type
        if message_type == MessageType.EVENT:
            stream_name = self.stream_names["events"]
        elif message_type == MessageType.COMMAND:
            stream_name = self.stream_names["commands"]
        elif message_type == MessageType.NOTIFICATION:
            stream_name = self.stream_names["notifications"]
        else:
            stream_name = self.stream_names["events"]  # Default to events
            
        return await self._publish_to_stream(stream_name, message.dict())
    
    async def _publish_to_stream(self, stream_name: str, message_data: Dict[str, Any]) -> str:
        """
        Publish message to Redis stream.
        
        Args:
            stream_name: Name of the Redis stream
            message_data: Message data to publish
            
        Returns:
            Message ID from Redis
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            # Convert datetime objects to ISO strings for JSON serialization
            serialized_data = self._serialize_message_data(message_data)
            
            # Add message to stream
            message_id = await self.redis_client.xadd(
                stream_name,
                serialized_data,
                maxlen=MessagingConfig.STREAM_MAX_LENGTH,
                approximate=True
            )
            
            logger.debug(f"Published message {message_id} to stream {stream_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message to stream {stream_name}: {e}")
            raise
    
    async def _publish_to_pubsub(self, channel: str, message_data: Dict[str, Any]) -> None:
        """
        Publish message to Redis pub/sub channel.
        
        Args:
            channel: Pub/sub channel name
            message_data: Message data to publish
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            # Convert message data to JSON
            message_json = json.dumps(self._serialize_message_data(message_data), default=str)
            
            # Publish to channel
            await self.redis_client.publish(channel, message_json)
            
            logger.debug(f"Published message to pub/sub channel {channel}")
            
        except Exception as e:
            logger.error(f"Failed to publish message to pub/sub channel {channel}: {e}")
            raise
    
    def _serialize_message_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Serialize message data for Redis storage.
        
        Args:
            data: Message data dictionary
            
        Returns:
            Serialized data with string values
        """
        serialized = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                serialized[key] = json.dumps(value, default=str)
            else:
                serialized[key] = str(value) if value is not None else ""
        return serialized
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()