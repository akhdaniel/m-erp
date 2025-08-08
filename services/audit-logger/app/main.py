"""
Audit Logger Service - Event-driven audit logging for XERPIUM.
Demonstrates how services can consume business events for cross-cutting concerns.
"""
import sys
import os
import logging
import asyncio
from contextlib import asynccontextmanager

# Add shared messaging library to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

from messaging import MessageConsumer, EventType
from messaging.schemas import Event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AuditLoggerService:
    """Audit logger service that consumes business events."""
    
    def __init__(self):
        self.consumer = None
        self.running = False
        
    async def start(self):
        """Start the audit logger service."""
        logger.info("Starting Audit Logger Service...")
        
        # Initialize consumer
        self.consumer = MessageConsumer("audit-logger-service")
        await self.consumer.connect()
        
        # Register event handlers for all event types
        await self._register_event_handlers()
        
        # Start consuming messages
        await self.consumer.start_consuming()
        self.running = True
        
        logger.info("✓ Audit Logger Service started successfully")
        
    async def stop(self):
        """Stop the audit logger service."""
        logger.info("Stopping Audit Logger Service...")
        
        if self.consumer:
            await self.consumer.stop_consuming()
            await self.consumer.disconnect()
        
        self.running = False
        logger.info("✓ Audit Logger Service stopped")
        
    async def _register_event_handlers(self):
        """Register handlers for all business events."""
        
        # User events
        self.consumer.register_event_handler(EventType.USER_CREATED, self._log_user_event)
        self.consumer.register_event_handler(EventType.USER_UPDATED, self._log_user_event)
        self.consumer.register_event_handler(EventType.USER_DELETED, self._log_user_event)
        self.consumer.register_event_handler(EventType.USER_LOGGED_IN, self._log_login_event)
        self.consumer.register_event_handler(EventType.USER_LOGGED_OUT, self._log_login_event)
        self.consumer.register_event_handler(EventType.USER_PASSWORD_CHANGED, self._log_security_event)
        self.consumer.register_event_handler(EventType.USER_LOCKED, self._log_security_event)
        self.consumer.register_event_handler(EventType.USER_UNLOCKED, self._log_security_event)
        
        # Company events
        self.consumer.register_event_handler(EventType.COMPANY_CREATED, self._log_company_event)
        self.consumer.register_event_handler(EventType.COMPANY_UPDATED, self._log_company_event)
        self.consumer.register_event_handler(EventType.COMPANY_ACTIVATED, self._log_company_event)
        self.consumer.register_event_handler(EventType.COMPANY_DEACTIVATED, self._log_company_event)
        
        # Partner events
        self.consumer.register_event_handler(EventType.PARTNER_CREATED, self._log_partner_event)
        self.consumer.register_event_handler(EventType.PARTNER_UPDATED, self._log_partner_event)
        self.consumer.register_event_handler(EventType.PARTNER_ADDRESS_ADDED, self._log_partner_event)
        self.consumer.register_event_handler(EventType.PARTNER_CONTACT_ADDED, self._log_partner_event)
        
        # Currency events
        self.consumer.register_event_handler(EventType.CURRENCY_RATE_UPDATED, self._log_currency_event)
        
        # Security events
        self.consumer.register_event_handler(EventType.SECURITY_VIOLATION, self._log_security_event)
        
        logger.info("✓ Registered event handlers for audit logging")
        
    async def _log_user_event(self, event: Event):
        """Log user-related events."""
        action = self._get_action_from_event_type(event.event_type)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "correlation_id": event.correlation_id,
            "source_service": event.source_service,
            "action": action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "company_id": event.company_id,
            "user_id": event.user_id,
            "before_data": event.before_data,
            "after_data": event.after_data,
            "changes": event.changes,
            "metadata": event.metadata
        }
        
        logger.info(f"📝 AUDIT: User {action} - User ID: {event.entity_id}, Company: {event.company_id}")
        logger.debug(f"📝 AUDIT DETAILS: {log_entry}")
        
        # In a real implementation, this would be saved to a database
        await self._save_audit_log(log_entry)
        
    async def _log_company_event(self, event: Event):
        """Log company-related events."""
        action = self._get_action_from_event_type(event.event_type)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "correlation_id": event.correlation_id,
            "source_service": event.source_service,
            "action": action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "company_id": event.company_id,
            "user_id": event.user_id,
            "before_data": event.before_data,
            "after_data": event.after_data,
            "changes": event.changes,
            "metadata": event.metadata
        }
        
        logger.info(f"📝 AUDIT: Company {action} - Company ID: {event.entity_id}")
        logger.debug(f"📝 AUDIT DETAILS: {log_entry}")
        
        await self._save_audit_log(log_entry)
        
    async def _log_partner_event(self, event: Event):
        """Log partner-related events."""
        action = self._get_action_from_event_type(event.event_type)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "correlation_id": event.correlation_id,
            "source_service": event.source_service,
            "action": action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "company_id": event.company_id,
            "user_id": event.user_id,
            "before_data": event.before_data,
            "after_data": event.after_data,
            "changes": event.changes,
            "metadata": event.metadata
        }
        
        logger.info(f"📝 AUDIT: Partner {action} - Partner ID: {event.entity_id}, Company: {event.company_id}")
        logger.debug(f"📝 AUDIT DETAILS: {log_entry}")
        
        await self._save_audit_log(log_entry)
        
    async def _log_currency_event(self, event: Event):
        """Log currency-related events."""
        action = self._get_action_from_event_type(event.event_type)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "correlation_id": event.correlation_id,
            "source_service": event.source_service,
            "action": action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "company_id": event.company_id,
            "after_data": event.after_data,
            "metadata": event.metadata
        }
        
        logger.info(f"📝 AUDIT: Currency {action} - Currency: {event.entity_id}, Company: {event.company_id}")
        logger.debug(f"📝 AUDIT DETAILS: {log_entry}")
        
        await self._save_audit_log(log_entry)
        
    async def _log_login_event(self, event: Event):
        """Log login/logout events with special handling."""
        action = self._get_action_from_event_type(event.event_type)
        
        # Extract IP address and user agent from event data
        ip_address = None
        user_agent = None
        if event.after_data:
            ip_address = event.after_data.get("ip_address")
            user_agent = event.after_data.get("user_agent")
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "correlation_id": event.correlation_id,
            "source_service": event.source_service,
            "action": action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "company_id": event.company_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "after_data": event.after_data,
            "metadata": event.metadata
        }
        
        logger.info(f"📝 AUDIT: User {action} - User ID: {event.entity_id}, IP: {ip_address}")
        logger.debug(f"📝 AUDIT DETAILS: {log_entry}")
        
        await self._save_audit_log(log_entry)
        
    async def _log_security_event(self, event: Event):
        """Log security-related events with high priority."""
        action = self._get_action_from_event_type(event.event_type)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.id,
            "correlation_id": event.correlation_id,
            "source_service": event.source_service,
            "action": action,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "company_id": event.company_id,
            "user_id": event.user_id,
            "before_data": event.before_data,
            "after_data": event.after_data,
            "metadata": event.metadata,
            "priority": "HIGH",
            "category": "SECURITY"
        }
        
        logger.warning(f"🚨 SECURITY AUDIT: {action} - Entity: {event.entity_id}, Company: {event.company_id}")
        logger.info(f"🚨 SECURITY DETAILS: {log_entry}")
        
        await self._save_audit_log(log_entry)
        
    def _get_action_from_event_type(self, event_type: EventType) -> str:
        """Convert event type to human-readable action."""
        action_map = {
            EventType.USER_CREATED: "User Created",
            EventType.USER_UPDATED: "User Updated", 
            EventType.USER_DELETED: "User Deleted",
            EventType.USER_LOGGED_IN: "User Login",
            EventType.USER_LOGGED_OUT: "User Logout",
            EventType.USER_PASSWORD_CHANGED: "Password Changed",
            EventType.USER_LOCKED: "Account Locked",
            EventType.USER_UNLOCKED: "Account Unlocked",
            EventType.COMPANY_CREATED: "Company Created",
            EventType.COMPANY_UPDATED: "Company Updated",
            EventType.COMPANY_ACTIVATED: "Company Activated",
            EventType.COMPANY_DEACTIVATED: "Company Deactivated",
            EventType.PARTNER_CREATED: "Partner Created",
            EventType.PARTNER_UPDATED: "Partner Updated",
            EventType.PARTNER_ADDRESS_ADDED: "Partner Address Added",
            EventType.PARTNER_CONTACT_ADDED: "Partner Contact Added",
            EventType.CURRENCY_RATE_UPDATED: "Currency Rate Updated",
            EventType.SECURITY_VIOLATION: "Security Violation"
        }
        return action_map.get(event_type, str(event_type))
        
    async def _save_audit_log(self, log_entry: dict):
        """Save audit log entry to storage."""
        # In a real implementation, this would save to a database
        # For now, we just demonstrate the pattern
        
        # Simulate async database operation
        await asyncio.sleep(0.01)
        
        # Log to demonstrate the audit trail
        logger.debug(f"💾 Saved audit log: {log_entry['event_id']}")


async def main():
    """Main function to run the audit logger service."""
    service = AuditLoggerService()
    
    try:
        await service.start()
        
        # Keep the service running
        logger.info("🎯 Audit Logger Service is running. Press Ctrl+C to stop.")
        while service.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Service error: {e}")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())