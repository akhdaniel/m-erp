"""
Message Consumer for M-ERP messaging system.
Handles consuming messages from Redis Streams and Pub/Sub channels.
"""
import json
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union
import redis.asyncio as redis
from redis.asyncio import Redis

from .config import MessagingConfig
from .schemas import Message, Event, Command, Notification, CommandResponse
from .events import MessageType, EventType, CommandType, NotificationType


logger = logging.getLogger(__name__)

# Type alias for message handlers
MessageHandler = Callable[[Dict[str, Any]], Awaitable[None]]
EventHandler = Callable[[Event], Awaitable[None]]
CommandHandler = Callable[[Command], Awaitable[Optional[CommandResponse]]]
NotificationHandler = Callable[[Notification], Awaitable[None]]


class MessageConsumer:
    """Consumes messages from Redis streams and pub/sub channels."""
    
    def __init__(self, service_name: str, redis_url: Optional[str] = None):
        """
        Initialize the message consumer.
        
        Args:
            service_name: Name of the service consuming messages
            redis_url: Redis connection URL (uses config default if not provided)
        """
        self.service_name = service_name
        self.redis_url = redis_url or MessagingConfig.get_redis_url()
        self.redis_client: Optional[Redis] = None
        self.stream_names = MessagingConfig.get_stream_names()
        self.pubsub_channels = MessagingConfig.get_pubsub_channels()
        self.consumer_group = MessagingConfig.get_consumer_group_name(service_name)
        
        # Message handlers
        self._event_handlers: Dict[EventType, List[EventHandler]] = {}
        self._command_handlers: Dict[CommandType, List[CommandHandler]] = {}
        self._notification_handlers: Dict[NotificationType, List[NotificationHandler]] = {}
        self._generic_handlers: Dict[str, List[MessageHandler]] = {}
        
        # Consumer tasks
        self._consumer_tasks: List[asyncio.Task] = []
        self._running = False
        
    async def connect(self) -> None:
        """Connect to Redis and create consumer groups."""
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
            
            # Create consumer groups for all streams
            await self._create_consumer_groups()
            
            logger.info(f"Message consumer connected to Redis for service: {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
            
    async def disconnect(self) -> None:
        """Disconnect from Redis and stop all consumer tasks."""
        await self.stop_consuming()
        
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info(f"Message consumer disconnected for service: {self.service_name}")
    
    def register_event_handler(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Async function to handle the event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for {event_type}")
    
    def register_command_handler(self, command_type: CommandType, handler: CommandHandler) -> None:
        """
        Register a handler for a specific command type.
        
        Args:
            command_type: Type of command to handle
            handler: Async function to handle the command
        """
        if command_type not in self._command_handlers:
            self._command_handlers[command_type] = []
        self._command_handlers[command_type].append(handler)
        logger.info(f"Registered command handler for {command_type}")
    
    def register_notification_handler(self, notification_type: NotificationType, handler: NotificationHandler) -> None:
        """
        Register a handler for a specific notification type.
        
        Args:
            notification_type: Type of notification to handle
            handler: Async function to handle the notification
        """
        if notification_type not in self._notification_handlers:
            self._notification_handlers[notification_type] = []
        self._notification_handlers[notification_type].append(handler)
        logger.info(f"Registered notification handler for {notification_type}")
    
    def register_generic_handler(self, subject: str, handler: MessageHandler) -> None:
        """
        Register a handler for generic messages with a specific subject.
        
        Args:
            subject: Message subject to handle
            handler: Async function to handle the message
        """
        if subject not in self._generic_handlers:
            self._generic_handlers[subject] = []
        self._generic_handlers[subject].append(handler)
        logger.info(f"Registered generic handler for subject: {subject}")
    
    async def start_consuming(self, streams: Optional[List[str]] = None) -> None:
        """
        Start consuming messages from Redis streams.
        
        Args:
            streams: List of stream names to consume from (default: all streams)
        """
        if self._running:
            logger.warning("Consumer is already running")
            return
            
        if not self.redis_client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        self._running = True
        
        # Default to consuming from all streams
        if streams is None:
            streams = list(self.stream_names.values())
        
        # Start consumer tasks for each stream
        for stream_name in streams:
            task = asyncio.create_task(self._consume_stream(stream_name))
            self._consumer_tasks.append(task)
        
        logger.info(f"Started consuming from streams: {streams}")
    
    async def stop_consuming(self) -> None:
        """Stop consuming messages and cancel all consumer tasks."""
        if not self._running:
            return
            
        self._running = False
        
        # Cancel all consumer tasks
        for task in self._consumer_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._consumer_tasks:
            await asyncio.gather(*self._consumer_tasks, return_exceptions=True)
        
        self._consumer_tasks.clear()
        logger.info("Stopped consuming messages")
    
    async def consume_single_message(self, stream_name: str, timeout: int = 1000) -> Optional[Dict[str, Any]]:
        """
        Consume a single message from a stream.
        
        Args:
            stream_name: Name of the stream to consume from
            timeout: Timeout in milliseconds
            
        Returns:
            Message data or None if no message available
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            # Read from stream
            result = await self.redis_client.xreadgroup(
                self.consumer_group,
                self.service_name,
                {stream_name: ">"},
                count=1,
                block=timeout
            )
            
            if result:
                stream_data = result[0][1]  # [stream_name, messages]
                if stream_data:
                    message_id, message_data = stream_data[0]
                    deserialized_data = self._deserialize_message_data(message_data)
                    deserialized_data["_message_id"] = message_id
                    deserialized_data["_stream_name"] = stream_name
                    return deserialized_data
                    
        except Exception as e:
            logger.error(f"Failed to consume message from stream {stream_name}: {e}")
            
        return None
    
    async def acknowledge_message(self, stream_name: str, message_id: str) -> None:
        """
        Acknowledge a message as processed.
        
        Args:
            stream_name: Name of the stream
            message_id: ID of the message to acknowledge
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            await self.redis_client.xack(stream_name, self.consumer_group, message_id)
            logger.debug(f"Acknowledged message {message_id} from stream {stream_name}")
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
    
    async def subscribe_to_notifications(self, channels: List[str]) -> None:
        """
        Subscribe to pub/sub channels for real-time notifications.
        
        Args:
            channels: List of channel patterns to subscribe to
        """
        if not self.redis_client:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to channels
            for channel in channels:
                await pubsub.psubscribe(channel)
            
            # Start listening task
            task = asyncio.create_task(self._listen_pubsub(pubsub))
            self._consumer_tasks.append(task)
            
            logger.info(f"Subscribed to pub/sub channels: {channels}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to channels: {e}")
            raise
    
    async def _create_consumer_groups(self) -> None:
        """Create consumer groups for all streams."""
        for stream_name in self.stream_names.values():
            try:
                await self.redis_client.xgroup_create(
                    stream_name, 
                    self.consumer_group, 
                    id="0", 
                    mkstream=True
                )
                logger.debug(f"Created consumer group {self.consumer_group} for stream {stream_name}")
            except redis.ResponseError as e:
                if "BUSYGROUP" in str(e):
                    logger.debug(f"Consumer group {self.consumer_group} already exists for stream {stream_name}")
                else:
                    logger.error(f"Failed to create consumer group for stream {stream_name}: {e}")
                    raise
    
    async def _consume_stream(self, stream_name: str) -> None:
        """
        Consume messages from a specific stream.
        
        Args:
            stream_name: Name of the stream to consume from
        """
        consumer_id = f"{self.service_name}-{id(self)}"
        
        while self._running:
            try:
                # Read messages from stream
                result = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    consumer_id,
                    {stream_name: ">"},
                    count=10,
                    block=MessagingConfig.STREAM_BLOCK_TIME
                )
                
                if result:
                    stream_data = result[0][1]  # [stream_name, messages]
                    
                    for message_id, message_data in stream_data:
                        try:
                            # Deserialize message data
                            deserialized_data = self._deserialize_message_data(message_data)
                            
                            # Process message
                            await self._process_message(stream_name, message_id, deserialized_data)
                            
                            # Acknowledge message
                            await self.acknowledge_message(stream_name, message_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")
                            # TODO: Implement retry logic or dead letter queue
                            
            except asyncio.CancelledError:
                logger.info(f"Consumer task cancelled for stream {stream_name}")
                break
            except Exception as e:
                logger.error(f"Error in consumer task for stream {stream_name}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _listen_pubsub(self, pubsub) -> None:
        """
        Listen to pub/sub messages.
        
        Args:
            pubsub: Redis pub/sub instance
        """
        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        data = json.loads(message["data"])
                        await self._process_pubsub_message(message["channel"], data)
                    except Exception as e:
                        logger.error(f"Error processing pub/sub message: {e}")
                        
        except asyncio.CancelledError:
            logger.info("Pub/sub listener cancelled")
        except Exception as e:
            logger.error(f"Error in pub/sub listener: {e}")
        finally:
            await pubsub.close()
    
    async def _process_message(self, stream_name: str, message_id: str, message_data: Dict[str, Any]) -> None:
        """
        Process a message based on its type.
        
        Args:
            stream_name: Name of the stream
            message_id: Message ID
            message_data: Deserialized message data
        """
        try:
            message_type = message_data.get("type")
            
            if message_type == MessageType.EVENT:
                await self._process_event(message_data)
            elif message_type == MessageType.COMMAND:
                await self._process_command(message_data)
            elif message_type == MessageType.NOTIFICATION:
                await self._process_notification(message_data)
            else:
                # Generic message processing
                subject = message_data.get("subject", "unknown")
                await self._process_generic_message(subject, message_data)
                
        except Exception as e:
            logger.error(f"Error processing message {message_id} from {stream_name}: {e}")
            raise
    
    async def _process_event(self, message_data: Dict[str, Any]) -> None:
        """Process an event message."""
        try:
            event = Event(**message_data)
            handlers = self._event_handlers.get(event.event_type, [])
            
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")
                    
        except Exception as e:
            logger.error(f"Error creating event object: {e}")
    
    async def _process_command(self, message_data: Dict[str, Any]) -> None:
        """Process a command message."""
        try:
            command = Command(**message_data)
            
            # Only process commands targeted at this service
            if command.target_service != self.service_name:
                return
                
            handlers = self._command_handlers.get(command.command_type, [])
            
            for handler in handlers:
                try:
                    response = await handler(command)
                    
                    # Send response if reply_to is specified
                    if command.reply_to and response:
                        await self._send_command_response(command.reply_to, response)
                        
                except Exception as e:
                    logger.error(f"Error in command handler for {command.command_type}: {e}")
                    
                    # Send error response
                    if command.reply_to:
                        error_response = CommandResponse(
                            command_id=command.id,
                            success=False,
                            error=str(e)
                        )
                        await self._send_command_response(command.reply_to, error_response)
                    
        except Exception as e:
            logger.error(f"Error creating command object: {e}")
    
    async def _process_notification(self, message_data: Dict[str, Any]) -> None:
        """Process a notification message."""
        try:
            notification = Notification(**message_data)
            handlers = self._notification_handlers.get(notification.notification_type, [])
            
            for handler in handlers:
                try:
                    await handler(notification)
                except Exception as e:
                    logger.error(f"Error in notification handler for {notification.notification_type}: {e}")
                    
        except Exception as e:
            logger.error(f"Error creating notification object: {e}")
    
    async def _process_generic_message(self, subject: str, message_data: Dict[str, Any]) -> None:
        """Process a generic message."""
        handlers = self._generic_handlers.get(subject, [])
        
        for handler in handlers:
            try:
                await handler(message_data)
            except Exception as e:
                logger.error(f"Error in generic handler for subject {subject}: {e}")
    
    async def _process_pubsub_message(self, channel: str, message_data: Dict[str, Any]) -> None:
        """Process a pub/sub message."""
        # For now, treat pub/sub messages the same as stream messages
        await self._process_message(channel, "pubsub", message_data)
    
    async def _send_command_response(self, reply_channel: str, response: CommandResponse) -> None:
        """Send a command response to the reply channel."""
        if not self.redis_client:
            return
            
        try:
            response_json = json.dumps(response.dict(), default=str)
            await self.redis_client.publish(reply_channel, response_json)
            logger.debug(f"Sent command response to {reply_channel}")
        except Exception as e:
            logger.error(f"Failed to send command response: {e}")
    
    def _deserialize_message_data(self, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Deserialize message data from Redis.
        
        Args:
            data: Raw message data from Redis
            
        Returns:
            Deserialized message data
        """
        deserialized = {}
        for key, value in data.items():
            if key.endswith('_data') or key in ['payload', 'metadata', 'changes', 'details']:
                # These are JSON-encoded fields
                try:
                    deserialized[key] = json.loads(value) if value else {}
                except (json.JSONDecodeError, TypeError):
                    deserialized[key] = value
            elif key == 'timestamp' or key.endswith('_at'):
                # These are datetime fields
                try:
                    deserialized[key] = datetime.fromisoformat(value) if value else None
                except (ValueError, TypeError):
                    deserialized[key] = value
            elif key in ['priority', 'timeout', 'uptime_seconds', 'execution_time_ms']:
                # These are numeric fields
                try:
                    deserialized[key] = int(value) if value else None
                except (ValueError, TypeError):
                    deserialized[key] = value
            elif key in ['type', 'event_type', 'command_type', 'notification_type']:
                # These are enum fields - convert back to enum
                try:
                    if key == 'type':
                        deserialized[key] = MessageType(value) if value else None
                    elif key == 'event_type':
                        deserialized[key] = EventType(value) if value else None
                    elif key == 'command_type':
                        deserialized[key] = CommandType(value) if value else None
                    elif key == 'notification_type':
                        deserialized[key] = NotificationType(value) if value else None
                except (ValueError, TypeError):
                    deserialized[key] = value
            else:
                deserialized[key] = value if value else None
                
        return deserialized
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()