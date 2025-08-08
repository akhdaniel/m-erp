"""
Module Registry Service - Main FastAPI application
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.service_registry import service_registry_client
from app.routers import modules, installations, enhanced_modules, enhanced_installations, dependency_resolution

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variable to store heartbeat task
heartbeat_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global heartbeat_task
    
    # Startup
    logger.info("Starting Module Registry Service...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Register with service registry
        registration_success = await service_registry_client.register_service()
        if registration_success:
            # Start heartbeat task
            heartbeat_task = asyncio.create_task(service_registry_client.start_heartbeat())
            logger.info("Service registered and heartbeat started")
        else:
            logger.warning("Failed to register with service registry, continuing without registration")
        
        logger.info(f"Module Registry Service started on {settings.service_host}:{settings.service_port}")
        
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Module Registry Service...")
    
    try:
        # Cancel heartbeat task
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                logger.info("Heartbeat task cancelled")
        
        # Unregister from service registry
        await service_registry_client.unregister_service()
        
        # Close database connections
        await close_db()
        
        logger.info("Service shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Module Registry Service for XERPIUM Extension System",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(modules.router, prefix="/api/v1")
app.include_router(enhanced_modules.router, prefix="/api/v2")  # Enhanced endpoints in v2
app.include_router(installations.router, prefix="/api/v1")
app.include_router(enhanced_installations.router, prefix="/api/v2")  # Enhanced installation endpoints
app.include_router(dependency_resolution.router, prefix="/api/v2")  # Dependency resolution endpoints


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "description": "Module Registry Service for XERPIUM Extension System"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # TODO: Add database health check
        # For now, simple status response
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "modules": "/api/v1/modules",
            "enhanced_modules": "/api/v2/modules",
            "installations": "/api/v1/installations",
            "enhanced_installations": "/api/v2/installations",
            "dependency_resolution": "/api/v2/dependencies",
            "health": "/health",
            "docs": "/docs" if settings.debug else "disabled"
        },
        "configuration": {
            "max_module_size_mb": settings.max_module_size_mb,
            "module_storage_path": settings.module_storage_path
        }
    }


@app.get("/services")
async def list_services():
    """List all services in the registry (for debugging)"""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Endpoint not available in production")
    
    try:
        services = await service_registry_client.list_services()
        return {"services": services}
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve services")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )