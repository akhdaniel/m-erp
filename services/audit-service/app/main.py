"""
Audit Service - Comprehensive audit logging for M-ERP.
Stores all business events in a permanent audit database for compliance and monitoring.
"""
import sys
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

# Add shared messaging library to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

from messaging import MessageConsumer, EventType
from messaging.schemas import Event

from .core.database import get_db, create_database_tables
from .models.audit_log import AuditLog
from .schemas.audit import AuditLogCreate, AuditLogResponse, AuditLogListResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AuditService:
    """Service for comprehensive audit logging."""
    
    def __init__(self):
        self.consumer = None
        self.running = False
        
    async def start(self):
        """Start the audit service."""
        logger.info("Starting Audit Service...")
        
        # Create database tables
        await create_database_tables()
        
        # Initialize consumer
        self.consumer = MessageConsumer("audit-service")
        await self.consumer.connect()
        
        # Register event handlers for all event types
        await self._register_event_handlers()
        
        # Start consuming messages
        await self.consumer.start_consuming(streams=["events"])
        self.running = True
        
        logger.info("✓ Audit Service started successfully")
        
    async def stop(self):
        """Stop the audit service."""
        logger.info("Stopping Audit Service...")
        
        if self.consumer:
            await self.consumer.stop_consuming()
            await self.consumer.disconnect()
        
        self.running = False
        logger.info("✓ Audit Service stopped")
        
    async def _register_event_handlers(self):
        """Register handlers for all business events."""
        
        # Register a handler for all event types
        for event_type in EventType:
            self.consumer.register_event_handler(event_type, self._handle_event)
        
        logger.info("✓ Registered event handlers for comprehensive audit logging")
        
    async def _handle_event(self, event: Event):
        """Handle and store audit log entry."""
        try:
            # Convert timezone-aware datetime to UTC naive datetime for database
            event_timestamp = event.timestamp
            if event_timestamp and event_timestamp.tzinfo:
                event_timestamp = event_timestamp.astimezone().replace(tzinfo=None)
            
            # Create audit log entry
            audit_data = AuditLogCreate(
                event_id=event.id,
                event_type=event.event_type,
                entity_type=event.entity_type,
                entity_id=str(event.entity_id),
                company_id=event.company_id,
                user_id=event.user_id,
                source_service=event.source_service,
                correlation_id=event.correlation_id,
                timestamp=event_timestamp,
                before_data=event.before_data,
                after_data=event.after_data,
                changes=event.changes,
                metadata=event.metadata or {}
            )
            
            # Store in database
            async for db in get_db():
                await self._create_audit_log(db, audit_data)
                break
                
            logger.info(f"📝 Stored audit log: {event.event_type} for {event.entity_type} {event.entity_id}")
            
        except Exception as e:
            logger.error(f"Failed to store audit log for event {event.id}: {e}")
            
    async def _create_audit_log(self, db: AsyncSession, audit_data: AuditLogCreate) -> AuditLog:
        """Create an audit log entry in the database."""
        audit_log = AuditLog(**audit_data.dict())
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log


# Global service instance
audit_service = AuditService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await audit_service.start()
    yield
    # Shutdown
    await audit_service.stop()


app = FastAPI(
    title="M-ERP Audit Service",
    description="Comprehensive audit logging and compliance monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "M-ERP Audit Service",
        "version": "1.0.0",
        "status": "running",
        "consumer_running": audit_service.running
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "audit-service",
        "version": "1.0.0",
        "consumer_running": audit_service.running,
        "consumer_connected": audit_service.consumer is not None
    }


@app.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db: AsyncSession = Depends(get_db)
):
    """
    List audit log entries with filtering and pagination.
    """
    # Build query conditions
    conditions = []
    
    if entity_type:
        conditions.append(AuditLog.entity_type == entity_type)
    if entity_id:
        conditions.append(AuditLog.entity_id == entity_id)
    if company_id:
        conditions.append(AuditLog.company_id == company_id)
    if user_id:
        conditions.append(AuditLog.user_id == user_id)
    if event_type:
        conditions.append(AuditLog.event_type == event_type)
    
    # Base query
    query = select(AuditLog).order_by(desc(AuditLog.timestamp))
    count_query = select(AuditLog)
    
    # Apply filters
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # Get total count
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    return AuditLogListResponse(
        items=[AuditLogResponse.from_orm(log) for log in audit_logs],
        total=total,
        skip=skip,
        limit=limit
    )


@app.get("/audit-logs/{audit_log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    audit_log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific audit log entry.
    """
    result = await db.execute(
        select(AuditLog).where(AuditLog.id == audit_log_id)
    )
    audit_log = result.scalar_one_or_none()
    
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return AuditLogResponse.from_orm(audit_log)


@app.get("/audit-logs/entity/{entity_type}/{entity_id}", response_model=AuditLogListResponse)
async def get_entity_audit_trail(
    entity_type: str,
    entity_id: str,
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete audit trail for a specific entity.
    """
    conditions = [
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ]
    
    if company_id:
        conditions.append(AuditLog.company_id == company_id)
    
    # Get audit logs
    query = select(AuditLog).where(and_(*conditions)).order_by(desc(AuditLog.timestamp))
    count_query = select(AuditLog).where(and_(*conditions))
    
    # Get total count
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    return AuditLogListResponse(
        items=[AuditLogResponse.from_orm(log) for log in audit_logs],
        total=total,
        skip=skip,
        limit=limit
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")