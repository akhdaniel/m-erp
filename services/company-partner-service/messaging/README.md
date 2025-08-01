# M-ERP Redis Message Queue System

A comprehensive messaging system for M-ERP microservices built on Redis Streams and Pub/Sub for reliable inter-service communication and event-driven architecture.

## Features

- **Redis Streams** for reliable message delivery and event sourcing
- **Redis Pub/Sub** for real-time notifications
- **Event-driven architecture** with business event publishing
- **Command/Response patterns** for inter-service communication
- **Notification system** for UI updates
- **Automatic consumer groups** and message acknowledgment
- **Type-safe message schemas** with Pydantic validation
- **Correlation ID support** for request tracing
- **Health monitoring** integration

## Architecture

### Message Types

1. **Events**: Business events (user created, company updated, etc.)
2. **Commands**: Inter-service commands (create user, validate token, etc.)  
3. **Notifications**: UI notifications and real-time updates
4. **Health Checks**: Service health monitoring messages

### Redis Usage

- **Streams**: `events`, `commands`, `notifications`, `health`
- **Consumer Groups**: One per service for load balancing
- **Pub/Sub**: Real-time notifications and user-specific updates
- **TTL**: 24-hour message retention by default

## Quick Start

### 1. Publisher Usage

```python
from messaging import MessagePublisher, EventType

# Initialize publisher
publisher = MessagePublisher("my-service")
await publisher.connect()

# Publish an event
await publisher.publish_event(
    event_type=EventType.USER_CREATED,
    entity_type="user",
    entity_id=123,
    company_id=1,
    after_data={"email": "user@example.com"},
    metadata={"source": "registration"}
)

# Publish a notification
await publisher.publish_notification(
    notification_type=NotificationType.SUCCESS,
    title="Welcome!",
    message="Account created successfully",
    target_user_id=123
)

await publisher.disconnect()
```

### 2. Consumer Usage

```python
from messaging import MessageConsumer, EventType
from messaging.schemas import Event

# Initialize consumer
consumer = MessageConsumer("my-service")
await consumer.connect()

# Register event handlers
async def handle_user_created(event: Event):
    print(f"User {event.entity_id} was created!")
    # Process the event...

consumer.register_event_handler(EventType.USER_CREATED, handle_user_created)

# Start consuming
await consumer.start_consuming()

# Stop when done
await consumer.stop_consuming()
await consumer.disconnect()
```

### 3. Service Integration

```python
# In your service startup
from messaging_service import init_messaging, shutdown_messaging

async def startup():
    await init_messaging()
    
async def shutdown():
    await shutdown_messaging()

# In your business logic
from messaging_service import get_messaging_service

async def create_user(user_data):
    # ... create user logic ...
    
    # Publish event
    messaging_service = await get_messaging_service()
    if messaging_service:
        await messaging_service.publish_user_created(
            user_id=user.id,
            user_data=user_data
        )
```

## Message Schemas

### Event Message
```python
{
    "id": "uuid4-string",
    "timestamp": "2025-01-15T10:30:00Z",
    "source_service": "user-auth-service",
    "type": "event",
    "event_type": "user.created",
    "entity_type": "user",
    "entity_id": 123,
    "company_id": 1,
    "user_id": 456,  # Who triggered the event
    "after_data": {"email": "user@example.com"},
    "correlation_id": "request-uuid",
    "metadata": {"source": "registration"}
}
```

### Command Message
```python
{
    "id": "uuid4-string",
    "timestamp": "2025-01-15T10:30:00Z",
    "source_service": "api-gateway",
    "type": "command", 
    "command_type": "validate_token",
    "target_service": "user-auth-service",
    "payload": {"token": "jwt-token"},
    "reply_to": "api-gateway-responses",
    "timeout": 30
}
```

### Notification Message
```python
{
    "id": "uuid4-string", 
    "timestamp": "2025-01-15T10:30:00Z",
    "source_service": "user-auth-service",
    "type": "notification",
    "notification_type": "success",
    "title": "Welcome!",
    "message": "Account created successfully", 
    "target_user_id": 123,
    "channel": "auth",
    "priority": 2
}
```

## Event Types

### User Events
- `user.created` - New user registered
- `user.updated` - User profile updated
- `user.deleted` - User account deleted
- `user.logged_in` - User login
- `user.logged_out` - User logout
- `user.password_changed` - Password updated
- `user.locked` - Account locked
- `user.unlocked` - Account unlocked

### Company Events
- `company.created` - New company created
- `company.updated` - Company details updated
- `company.activated` - Company activated
- `company.deactivated` - Company deactivated

### Partner Events
- `partner.created` - New partner created
- `partner.updated` - Partner details updated
- `partner.address_added` - Partner address added
- `partner.contact_added` - Partner contact added

### Currency Events
- `currency.rate_updated` - Exchange rate updated

### System Events
- `service.started` - Service startup
- `service.stopped` - Service shutdown
- `security.violation` - Security incident
- `audit.log_created` - Audit log entry

## Configuration

Environment variables:

```bash
# Redis connection
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Connection settings
REDIS_MAX_CONNECTIONS=20
REDIS_CONNECTION_TIMEOUT=5
REDIS_SOCKET_TIMEOUT=5

# Stream settings
STREAM_MAX_LENGTH=10000
STREAM_BLOCK_TIME=1000
CONSUMER_GROUP_SUFFIX=workers

# Message settings
MESSAGE_TTL=86400
MESSAGE_MAX_RETRIES=3
MESSAGE_RETRY_DELAY=60

# Service settings
SERVICE_NAME=my-service
ENVIRONMENT=development
```

## Best Practices

### 1. Event Design
- Events are immutable facts about what happened
- Include both before/after data for updates
- Use correlation IDs for request tracing
- Add meaningful metadata

### 2. Error Handling
- Always handle messaging failures gracefully
- Don't fail business operations if messaging fails
- Log messaging errors for monitoring

### 3. Performance
- Use appropriate message batching
- Configure stream max length for your use case
- Monitor consumer lag

### 4. Security
- Include company_id for multi-tenant isolation
- Validate all incoming messages
- Use correlation IDs for audit trails

## Testing

Run the test script to verify messaging functionality:

```bash
cd shared/messaging
python test_messaging.py
```

The test will:
1. Connect to Redis
2. Publish various message types
3. Consume and verify messages
4. Test event handlers
5. Verify health checks

## Integration Examples

### User Authentication Service
```python
# On user registration
await messaging_service.publish_user_created(
    user_id=user.id,
    user_data={
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
)

# On user login
await messaging_service.publish_user_logged_in(
    user_id=user.id,
    login_data={
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
)
```

### Company Partner Service
```python
# On partner creation
await messaging_service.publish_partner_created(
    partner_id=partner.id,
    partner_data=partner_dict,
    company_id=partner.company_id,
    created_by_user_id=current_user.id
)

# On currency rate update
await messaging_service.publish_currency_rate_updated(
    currency_code="USD",
    rate_data={"rate": 1.0, "updated_at": datetime.utcnow()},
    company_id=company_id
)
```

## Monitoring

The messaging system provides:
- Health check messages for service monitoring
- Automatic message acknowledgment tracking
- Consumer group lag monitoring
- Error logging and alerting

Monitor Redis streams with:
```bash
# Check stream info
redis-cli XINFO STREAM events

# Check consumer groups  
redis-cli XINFO GROUPS events

# Check pending messages
redis-cli XPENDING events my-service-workers
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check Redis host/port configuration
   - Verify Redis is running and accessible
   - Check network connectivity

2. **Messages Not Consumed**
   - Verify consumer groups are created
   - Check consumer is subscribed to correct streams
   - Monitor consumer group lag

3. **Memory Usage**
   - Configure appropriate stream max length
   - Monitor Redis memory usage
   - Set up message expiration

4. **Performance Issues**
   - Tune consumer batch sizes
   - Monitor network latency
   - Consider Redis clustering

### Debug Commands

```bash
# List all streams
redis-cli --scan --pattern "*"

# Check stream length
redis-cli XLEN events

# View recent messages
redis-cli XRANGE events - + COUNT 10

# Check consumer group status
redis-cli XINFO CONSUMERS events my-service-workers
```

## Future Enhancements

- Dead letter queue for failed messages
- Message encryption for sensitive data  
- Cross-service transaction support
- Message replay functionality
- Advanced routing and filtering
- Metrics and dashboards
- Multi-environment message isolation