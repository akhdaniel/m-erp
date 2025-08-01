"""
Simple test script for Redis messaging system.
"""
import asyncio
import logging
from datetime import datetime

from publisher import MessagePublisher
from consumer import MessageConsumer
from events import EventType, NotificationType
from schemas import Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_messaging():
    """Test basic publish/consume functionality."""
    print("🧪 Testing Redis Message Queue System")
    
    # Initialize publisher
    publisher = MessagePublisher("test-service")
    await publisher.connect()
    print("✓ Publisher connected")
    
    # Initialize consumer
    consumer = MessageConsumer("test-service")
    await consumer.connect()
    print("✓ Consumer connected")
    
    # Test event publishing
    print("\n📤 Publishing test events...")
    
    # Publish user created event
    await publisher.publish_event(
        event_type=EventType.USER_CREATED,
        entity_type="user",
        entity_id=123,
        company_id=1,
        after_data={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        },
        metadata={"test": True}
    )
    print("✓ Published USER_CREATED event")
    
    # Publish notification
    await publisher.publish_notification(
        notification_type=NotificationType.SUCCESS,
        title="Welcome!",
        message="Welcome to M-ERP system",
        target_user_id=123,
        priority=2
    )
    print("✓ Published notification")
    
    # Test message consumption
    print("\n📥 Consuming messages...")
    
    # Consume from events stream
    event_message = await consumer.consume_single_message("events", timeout=2000)
    if event_message:
        print(f"✓ Consumed event: {event_message.get('event_type')} for entity {event_message.get('entity_id')}")
    else:
        print("❌ No event message received")
    
    # Consume from notifications stream
    notification_message = await consumer.consume_single_message("notifications", timeout=2000)
    if notification_message:
        print(f"✓ Consumed notification: {notification_message.get('title')}")
    else:
        print("❌ No notification message received")
    
    # Health check
    await publisher.publish_health_check(
        status="healthy",
        details={"version": "1.0.0", "test": True},
        uptime_seconds=3600
    )
    print("✓ Published health check")
    
    # Cleanup
    await consumer.disconnect()
    await publisher.disconnect()
    print("\n✅ Test completed successfully!")


async def test_event_handler():
    """Test event handler registration."""
    print("\n🎯 Testing event handlers...")
    
    consumer = MessageConsumer("test-handler-service")
    await consumer.connect()
    
    # Register an event handler
    async def handle_user_created(event: Event):
        print(f"🎉 Handler received USER_CREATED event for user {event.entity_id}")
        print(f"   Email: {event.after_data.get('email') if event.after_data else 'N/A'}")
    
    consumer.register_event_handler(EventType.USER_CREATED, handle_user_created)
    print("✓ Registered event handler")
    
    # Start consuming (for a short time)
    await consumer.start_consuming()
    print("✓ Started consuming messages")
    
    # Let it run for a few seconds to process any existing messages
    await asyncio.sleep(3)
    
    await consumer.stop_consuming()
    await consumer.disconnect()
    print("✓ Stopped consuming and disconnected")


if __name__ == "__main__":
    async def main():
        try:
            await test_basic_messaging()
            await test_event_handler()
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise
    
    asyncio.run(main())