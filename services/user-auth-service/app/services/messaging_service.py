"""
Messaging service integration for User Authentication Service.
"""
import sys
import os
import logging
from typing import Optional

# Add shared messaging library to path
sys.path.append('/app')

from messaging import MessagePublisher, MessageConsumer, EventType, NotificationType

logger = logging.getLogger(__name__)


class UserAuthMessagingService:
    """Messaging service for user authentication events."""
    
    def __init__(self, service_name: str = "user-auth-service"):
        self.service_name = service_name
        self.publisher: Optional[MessagePublisher] = None
        self.consumer: Optional[MessageConsumer] = None
        
    async def initialize(self) -> None:
        """Initialize messaging publisher and consumer."""
        try:
            # Initialize publisher
            self.publisher = MessagePublisher(self.service_name)
            await self.publisher.connect()
            
            # Initialize consumer  
            self.consumer = MessageConsumer(self.service_name)
            await self.consumer.connect()
            
            # Register event handlers
            await self._register_handlers()
            
            logger.info("User Auth messaging service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize messaging service: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown messaging connections."""
        try:
            if self.consumer:
                await self.consumer.disconnect()
            if self.publisher:
                await self.publisher.disconnect()
            logger.info("User Auth messaging service shutdown complete")
        except Exception as e:
            logger.error(f"Error during messaging service shutdown: {e}")
    
    async def _register_handlers(self) -> None:
        """Register message handlers for this service."""
        if not self.consumer:
            return
            
        # For now, we don't need to handle incoming events
        # This service primarily publishes events
        pass
    
    # Event publishing methods
    
    async def publish_user_created(
        self, 
        user_id: int, 
        user_data: dict, 
        company_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user created event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_CREATED,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                after_data=user_data,
                correlation_id=correlation_id,
                metadata={"source": "user_registration"}
            )
            logger.info(f"Published USER_CREATED event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_CREATED event: {e}")
            return None
    
    async def publish_user_updated(
        self, 
        user_id: int, 
        before_data: dict,
        after_data: dict,
        changes: dict,
        company_id: Optional[int] = None,
        updated_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user updated event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_UPDATED,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                user_id=updated_by_user_id,
                before_data=before_data,
                after_data=after_data,
                changes=changes,
                correlation_id=correlation_id,
                metadata={"source": "user_profile_update"}
            )
            logger.info(f"Published USER_UPDATED event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_UPDATED event: {e}")
            return None
    
    async def publish_user_deleted(
        self, 
        user_id: int, 
        user_data: dict,
        company_id: Optional[int] = None,
        deleted_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user deleted event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_DELETED,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                user_id=deleted_by_user_id,
                before_data=user_data,
                correlation_id=correlation_id,
                metadata={"source": "user_deletion"}
            )
            logger.info(f"Published USER_DELETED event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_DELETED event: {e}")
            return None
    
    async def publish_user_logged_in(
        self, 
        user_id: int, 
        login_data: dict,
        company_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user logged in event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_LOGGED_IN,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                after_data=login_data,
                correlation_id=correlation_id,
                metadata={"source": "user_login"}
            )
            logger.debug(f"Published USER_LOGGED_IN event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_LOGGED_IN event: {e}")
            return None
    
    async def publish_user_logged_out(
        self, 
        user_id: int, 
        logout_data: dict,
        company_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user logged out event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_LOGGED_OUT,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                after_data=logout_data,
                correlation_id=correlation_id,
                metadata={"source": "user_logout"}
            )
            logger.debug(f"Published USER_LOGGED_OUT event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_LOGGED_OUT event: {e}")
            return None
    
    async def publish_user_password_changed(
        self, 
        user_id: int, 
        company_id: Optional[int] = None,
        changed_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user password changed event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_PASSWORD_CHANGED,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                user_id=changed_by_user_id,
                correlation_id=correlation_id,
                metadata={"source": "password_change"}
            )
            logger.info(f"Published USER_PASSWORD_CHANGED event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_PASSWORD_CHANGED event: {e}")
            return None
    
    async def publish_user_locked(
        self, 
        user_id: int, 
        lock_reason: str,
        company_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user locked event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_LOCKED,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                after_data={"reason": lock_reason},
                correlation_id=correlation_id,
                metadata={"source": "account_lockout"}
            )
            logger.info(f"Published USER_LOCKED event for user {user_id}: {lock_reason}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_LOCKED event: {e}")
            return None
    
    async def publish_user_unlocked(
        self, 
        user_id: int, 
        company_id: Optional[int] = None,
        unlocked_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish user unlocked event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.USER_UNLOCKED,
                entity_type="user",
                entity_id=user_id,
                company_id=company_id,
                user_id=unlocked_by_user_id,
                correlation_id=correlation_id,
                metadata={"source": "account_unlock"}
            )
            logger.info(f"Published USER_UNLOCKED event for user {user_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish USER_UNLOCKED event: {e}")
            return None
    
    async def publish_security_violation(
        self, 
        user_id: Optional[int],
        violation_type: str,
        details: dict,
        company_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish security violation event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.SECURITY_VIOLATION,
                entity_type="security",
                entity_id=violation_type,
                company_id=company_id,
                user_id=user_id,
                after_data=details,
                correlation_id=correlation_id,
                metadata={"source": "security_monitoring"}
            )
            logger.warning(f"Published SECURITY_VIOLATION event: {violation_type}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish SECURITY_VIOLATION event: {e}")
            return None
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        target_user_id: Optional[int] = None,
        target_company_id: Optional[int] = None,
        priority: int = 1,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Send a notification message."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_notification(
                notification_type=notification_type,
                title=title,
                message=message,
                target_user_id=target_user_id,
                target_company_id=target_company_id,
                channel="auth",
                priority=priority,
                correlation_id=correlation_id
            )
            logger.debug(f"Sent notification: {title}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return None


# Global messaging service instance
messaging_service: Optional[UserAuthMessagingService] = None


async def get_messaging_service() -> Optional[UserAuthMessagingService]:
    """Get the global messaging service instance."""
    return messaging_service


async def init_messaging() -> None:
    """Initialize the global messaging service."""
    global messaging_service
    try:
        messaging_service = UserAuthMessagingService()
        await messaging_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize messaging service: {e}")
        messaging_service = None


async def shutdown_messaging() -> None:
    """Shutdown the global messaging service."""
    global messaging_service
    if messaging_service:
        await messaging_service.shutdown()
        messaging_service = None