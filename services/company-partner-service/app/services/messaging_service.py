"""
Messaging service integration for Company Partner Service.
"""
import sys
import os
import logging
from typing import Optional

# Add shared messaging library to path
sys.path.append('/app')

from messaging import MessagePublisher, MessageConsumer, EventType, NotificationType

logger = logging.getLogger(__name__)


class CompanyPartnerMessagingService:
    """Messaging service for company and partner events."""
    
    def __init__(self, service_name: str = "company-partner-service"):
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
            
            logger.info("Company Partner messaging service initialized successfully")
            
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
            logger.info("Company Partner messaging service shutdown complete")
        except Exception as e:
            logger.error(f"Error during messaging service shutdown: {e}")
    
    # Company event publishing methods
    
    async def publish_company_created(
        self, 
        company_id: int, 
        company_data: dict,
        created_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish company created event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.COMPANY_CREATED,
                entity_type="company",
                entity_id=company_id,
                company_id=company_id,
                user_id=created_by_user_id,
                after_data=company_data,
                correlation_id=correlation_id,
                metadata={"source": "company_management"}
            )
            logger.info(f"Published COMPANY_CREATED event for company {company_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish COMPANY_CREATED event: {e}")
            return None
    
    async def publish_company_updated(
        self, 
        company_id: int, 
        before_data: dict,
        after_data: dict,
        changes: dict,
        updated_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish company updated event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.COMPANY_UPDATED,
                entity_type="company",
                entity_id=company_id,
                company_id=company_id,
                user_id=updated_by_user_id,
                before_data=before_data,
                after_data=after_data,
                changes=changes,
                correlation_id=correlation_id,
                metadata={"source": "company_management"}
            )
            logger.info(f"Published COMPANY_UPDATED event for company {company_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish COMPANY_UPDATED event: {e}")
            return None
    
    # Partner event publishing methods
    
    async def publish_partner_created(
        self, 
        partner_id: int, 
        partner_data: dict,
        company_id: int,
        created_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish partner created event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.PARTNER_CREATED,
                entity_type="partner",
                entity_id=partner_id,
                company_id=company_id,
                user_id=created_by_user_id,
                after_data=partner_data,
                correlation_id=correlation_id,
                metadata={"source": "partner_management"}
            )
            logger.info(f"Published PARTNER_CREATED event for partner {partner_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish PARTNER_CREATED event: {e}")
            return None
    
    async def publish_partner_updated(
        self, 
        partner_id: int, 
        before_data: dict,
        after_data: dict,
        changes: dict,
        company_id: int,
        updated_by_user_id: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish partner updated event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.PARTNER_UPDATED,
                entity_type="partner",
                entity_id=partner_id,
                company_id=company_id,
                user_id=updated_by_user_id,
                before_data=before_data,
                after_data=after_data,
                changes=changes,
                correlation_id=correlation_id,
                metadata={"source": "partner_management"}
            )
            logger.info(f"Published PARTNER_UPDATED event for partner {partner_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish PARTNER_UPDATED event: {e}")
            return None
    
    # Currency event publishing methods
    
    async def publish_currency_rate_updated(
        self, 
        currency_code: str, 
        rate_data: dict,
        company_id: int,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Publish currency rate updated event."""
        if not self.publisher:
            logger.warning("Publisher not initialized")
            return None
            
        try:
            message_id = await self.publisher.publish_event(
                event_type=EventType.CURRENCY_RATE_UPDATED,
                entity_type="currency",
                entity_id=currency_code,
                company_id=company_id,
                after_data=rate_data,
                correlation_id=correlation_id,
                metadata={"source": "currency_management"}
            )
            logger.info(f"Published CURRENCY_RATE_UPDATED event for currency {currency_code}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish CURRENCY_RATE_UPDATED event: {e}")
            return None


# Global messaging service instance
messaging_service: Optional[CompanyPartnerMessagingService] = None


async def get_messaging_service() -> Optional[CompanyPartnerMessagingService]:
    """Get the global messaging service instance."""
    return messaging_service


async def init_messaging() -> None:
    """Initialize the global messaging service."""
    global messaging_service
    try:
        messaging_service = CompanyPartnerMessagingService()
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