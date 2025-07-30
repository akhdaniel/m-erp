"""
Service Registry FastAPI Application.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import redis_client
from app.routers import services
from app.services.registry import registry_service


# Background tasks
cleanup_task = None


async def periodic_cleanup():
    """Periodic cleanup of expired services."""
    while True:
        try:
            removed_count = await registry_service.cleanup_expired_services()
            if removed_count > 0:
                print(f"Cleanup: Removed {removed_count} expired services")
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        # Wait for next cleanup cycle
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global cleanup_task
    
    # Startup
    print("Starting Service Registry...")
    
    # Test Redis connection
    if await redis_client.ping():
        print("✓ Redis connection established")
    else:
        print("✗ Redis connection failed")
    
    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    print("✓ Background cleanup task started")
    
    yield
    
    # Shutdown
    print("Shutting down Service Registry...")
    
    # Cancel background tasks
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    
    # Close HTTP client
    await registry_service.close()
    
    print("✓ Service Registry stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="M-ERP Service Registry for automatic service discovery and health monitoring",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(services.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    try:
        redis_healthy = await redis_client.ping()
        
        if redis_healthy:
            status = "healthy"
            dependencies = {"redis": "healthy"}
        else:
            status = "degraded"
            dependencies = {"redis": "unhealthy"}
        
        return {
            "status": status,
            "service": settings.APP_NAME,
            "version": settings.VERSION,
            "dependencies": dependencies
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": settings.APP_NAME,
            "version": settings.VERSION,
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "M-ERP Service Registry",
        "endpoints": {
            "health": "/health",
            "services": "/api/v1/services",
            "register": "/api/v1/services/register",
            "discover": "/api/v1/services",
            "stats": "/api/v1/services/stats"
        }
    }