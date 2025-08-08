"""
Notification Service - Real-time notifications via Server-Sent Events.
Consumes notification messages from Redis and serves them to connected clients.
"""
import sys
import os
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Add shared messaging library to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

from messaging import MessageConsumer, NotificationType
from messaging.schemas import Notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global client connections
connected_clients: Set[asyncio.Queue] = set()
notification_consumer = None


class NotificationStreamService:
    """Service for managing real-time notification streams."""
    
    def __init__(self):
        self.consumer = None
        self.clients: Set[asyncio.Queue] = set()
        
    async def start(self):
        """Start the notification consumer."""
        logger.info("Starting Notification Stream Service...")
        
        # Initialize consumer for notifications
        self.consumer = MessageConsumer("notification-service")
        await self.consumer.connect()
        
        # Register notification handlers
        for notification_type in NotificationType:
            self.consumer.register_notification_handler(
                notification_type, 
                self._handle_notification
            )
        
        # Start consuming from notifications stream only
        await self.consumer.start_consuming(streams=["notifications"])
        
        logger.info("✓ Notification Stream Service started")
        
    async def stop(self):
        """Stop the notification consumer."""
        logger.info("Stopping Notification Stream Service...")
        
        if self.consumer:
            await self.consumer.stop_consuming()
            await self.consumer.disconnect()
        
        # Close all client connections
        for client_queue in list(self.clients):
            await client_queue.put({"type": "close"})
            self.clients.discard(client_queue)
        
        logger.info("✓ Notification Stream Service stopped")
        
    async def add_client(self) -> asyncio.Queue:
        """Add a new client connection."""
        client_queue = asyncio.Queue(maxsize=100)
        self.clients.add(client_queue)
        logger.info(f"📡 New client connected. Total clients: {len(self.clients)}")
        return client_queue
        
    async def remove_client(self, client_queue: asyncio.Queue):
        """Remove a client connection."""
        self.clients.discard(client_queue)
        logger.info(f"📡 Client disconnected. Total clients: {len(self.clients)}")
        
    async def _handle_notification(self, notification: Notification):
        """Handle incoming notification and broadcast to all clients."""
        logger.info(f"📢 Broadcasting notification: {notification.title}")
        
        # Convert notification to JSON
        notification_data = {
            "id": notification.id,
            "type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "timestamp": notification.timestamp.isoformat(),
            "priority": notification.priority,
            "expires_at": notification.expires_at.isoformat() if notification.expires_at else None,
            "target_user_id": notification.target_user_id,
            "target_company_id": notification.target_company_id
        }
        
        # Send to all connected clients
        disconnected_clients = []
        for client_queue in self.clients:
            try:
                # Use put_nowait to avoid blocking
                client_queue.put_nowait(notification_data)
            except asyncio.QueueFull:
                logger.warning("Client queue full, dropping notification")
            except Exception as e:
                logger.error(f"Error sending notification to client: {e}")
                disconnected_clients.append(client_queue)
        
        # Remove disconnected clients
        for client_queue in disconnected_clients:
            self.clients.discard(client_queue)


# Global service instance
notification_service = NotificationStreamService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await notification_service.start()
    yield
    # Shutdown
    await notification_service.stop()


app = FastAPI(
    title="XERPIUM Notification Service",
    description="Real-time notifications via Server-Sent Events",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "XERPIUM Notification Service",
        "version": "1.0.0",
        "status": "running",
        "connected_clients": len(notification_service.clients)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0",
        "connected_clients": len(notification_service.clients),
        "consumer_connected": notification_service.consumer is not None
    }


@app.get("/notifications/stream")
async def notification_stream(request: Request, user_id: int = None):
    """
    Server-Sent Events endpoint for real-time notifications.
    
    Args:
        user_id: Optional user ID to filter notifications
    """
    
    async def event_generator():
        # Add client to service
        client_queue = await notification_service.add_client()
        
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Notification stream connected'})}\n\n"
            
            while True:
                try:
                    # Wait for notification with timeout
                    notification_data = await asyncio.wait_for(
                        client_queue.get(), 
                        timeout=30.0  # Send heartbeat every 30 seconds
                    )
                    
                    # Check if this is a close signal
                    if notification_data.get("type") == "close":
                        break
                    
                    # Filter by user_id if specified
                    if user_id and notification_data.get("target_user_id"):
                        if notification_data["target_user_id"] != user_id:
                            continue
                    
                    # Send notification
                    yield f"data: {json.dumps(notification_data)}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': asyncio.get_event_loop().time()})}\n\n"
                    
                except Exception as e:
                    logger.error(f"Error in event generator: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Event generator error: {e}")
        finally:
            # Remove client from service
            await notification_service.remove_client(client_queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.post("/notifications/test")
async def test_notification(
    title: str = "Test Notification",
    message: str = "This is a test notification",
    notification_type: str = "info",
    priority: int = 1
):
    """
    Test endpoint to send a notification (for development/testing).
    """
    from messaging import MessagePublisher
    
    # Create a test publisher
    publisher = MessagePublisher("notification-service")
    await publisher.connect()
    
    try:
        # Publish test notification
        message_id = await publisher.publish_notification(
            notification_type=NotificationType(notification_type),
            title=title,
            message=message,
            priority=priority,
            channel="test"
        )
        
        return {
            "success": True,
            "message": "Test notification sent",
            "message_id": message_id
        }
        
    finally:
        await publisher.disconnect()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")