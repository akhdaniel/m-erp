"""
Framework-enabled main application for Company & Partner Management Service.

This version integrates the Business Object Framework for enhanced Partner management
while maintaining compatibility with existing services.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db, get_db
from app.middleware.auth import auth_client
from app.services.messaging_service import init_messaging, shutdown_messaging

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Company & Partner Management Service (Framework Mode)...")
    logger.info("Database migrations handled by startup script")
    
    # Initialize messaging service
    try:
        await init_messaging()
        logger.info("✓ Messaging service initialized")
    except Exception as e:
        logger.error(f"Messaging service initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Company & Partner Management Service...")
    
    # Shutdown messaging service
    try:
        await shutdown_messaging()
        logger.info("✓ Messaging service shutdown complete")
    except Exception as e:
        logger.error(f"Messaging service shutdown error: {e}")
    
    await close_db()
    await auth_client.close()
    logger.info("Database connections and auth client closed")


def create_application() -> FastAPI:
    application = FastAPI(
        title=f"{settings.project_name} (Framework Edition)",
        description=f"{settings.description} - Enhanced with Business Object Framework",
        version=f"{settings.version}-framework",
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    from app.routers import companies, currencies, extensions
    
    # Framework-based routers (NEW)
    from app.routers import companies_framework, partners_framework
    
    # Original routers (non-Partner services)
    application.include_router(companies.router, prefix="/api/v1")
    application.include_router(currencies.router)
    application.include_router(extensions.router, prefix="/api/v1")
    
    # New framework-based routers (on /framework prefix for testing)
    application.include_router(companies_framework.router, prefix="/api/framework")
    application.include_router(partners_framework.router, prefix="/api/framework")
    
    # Enhanced partner management routers
    try:
        from app.routers.partner_categories import router as categories_router
        from app.routers.partner_communications import router as communications_router
        
        application.include_router(categories_router, prefix="/api/v1")
        application.include_router(communications_router, prefix="/api/v1")
        logger.info("✅ Enhanced partner management routers included")
        
    except Exception as e:
        logger.error(f"❌ Failed to include enhanced partner management routers: {e}")
    
    # Framework-based Partner routers
    try:
        from app.framework_migration.partner_router import router as framework_partner_router
        from app.framework_migration.partner_router import framework_partner_router as generated_partner_router
        
        # Include both framework router options
        application.include_router(framework_partner_router, prefix="/api/v1")
        application.include_router(generated_partner_router.router, prefix="/api/v1")
        
        logger.info("✅ Framework-based Partner routers included")
        
    except Exception as e:
        logger.error(f"❌ Failed to include framework Partner routers: {e}")
        # Fallback to original Partner router
        try:
            from app.routers.partners import router as partners_router
            application.include_router(partners_router, prefix="/api/v1")
            logger.info("⚠️ Using original Partner router as fallback")
        except Exception as fallback_error:
            logger.error(f"❌ Failed to include fallback Partner router: {fallback_error}")
    
    # Original Partner router for compatibility (at different path)
    try:
        from app.routers.partners import router as original_partner_router
        application.include_router(original_partner_router, prefix="/api/v1/partners-original", tags=["partners-original"])
        logger.info("✅ Original partner router included at /api/v1/partners-original/")
    except Exception as e:
        logger.warning(f"Could not include original partner router for compatibility: {e}")
    
    logger.info("📋 Available Partner endpoints:")
    logger.info("  • /api/v1/partners-framework/ - Custom framework router")
    logger.info("  • /api/v1/partners/ - Auto-generated framework router") 
    logger.info("  • /api/v1/partners-original/ - Original router (compatibility)")
    logger.info("  • /api/v1/partners/{id}/extensions - Custom fields")
    logger.info("  • /api/v1/partners/{id}/audit - Audit trail")
    
    return application


app = create_application()


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Company & Partner Management Service",
        "version": f"{settings.version}-framework",
        "description": f"{settings.description} - Enhanced with Business Object Framework",
        "status": "running",
        "mode": "framework",
        "features": [
            "Custom fields support",
            "Audit logging", 
            "Event publishing",
            "Bulk operations",
            "Enhanced validation",
            "Auto-generated documentation"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status."""
    from app.core.database import get_db
    
    # Basic health response
    health_data = {
        "status": "healthy",
        "service": "company-partner-service",
        "version": f"{settings.version}-framework",
        "mode": "framework",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": "unknown",
            "auth_service": "unknown",
            "framework": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            health_data["dependencies"]["database"] = "healthy"
            break
    except Exception as e:
        health_data["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    # Check auth service connectivity
    try:
        token = await auth_client.get_service_token()
        if token:
            health_data["dependencies"]["auth_service"] = "healthy"
        else:
            health_data["dependencies"]["auth_service"] = "unhealthy: failed to get token"  
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["dependencies"]["auth_service"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    # Check framework components
    try:
        from app.framework_migration.partner_service import PartnerFrameworkService
        from app.framework.services import CompanyBusinessObjectService
        health_data["dependencies"]["framework"] = "healthy"
    except Exception as e:
        health_data["dependencies"]["framework"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    return health_data


@app.get("/migration/status")
async def migration_status():
    """Get migration status information."""
    try:
        return {
            "migration_status": {
                "framework_enabled": True, 
                "implementation": "framework",
                "migration_date": datetime.utcnow().isoformat()
            },
            "available_endpoints": {
                "framework_partners": "/api/v1/partners-framework/",
                "generated_partners": "/api/v1/partners/",
                "original_partners": "/api/v1/partners-original/",
                "extensions": "/api/v1/partners/{id}/extensions",
                "audit": "/api/v1/partners/{id}/audit",
                "bulk_create": "/api/v1/partners/bulk-create",
                "statistics": "/api/v1/partners/company/{id}/statistics"
            },
            "framework_features": [
                "Custom field support with 7 field types",
                "Automatic audit logging with complete change history",
                "Event publishing to Redis Streams",
                "Bulk operations for efficient batch processing",
                "Enhanced Pydantic validation with detailed error messages",
                "Multi-company data isolation enforcement",
                "Auto-generated OpenAPI documentation",
                "Standardized error handling and response formatting"
            ],
            "api_enhancements": [
                "Advanced filtering with custom field support",
                "Full-text search across multiple fields", 
                "Comprehensive sorting and pagination",
                "Real-time audit trail access",
                "Partner statistics and reporting",
                "Type-safe operations with automatic validation"
            ]
        }
    except Exception as e:
        return {"error": f"Failed to get migration status: {e}"}


@app.get("/framework/info")
async def framework_info():
    """Get Business Object Framework information."""
    try:
        from app.framework.services import CompanyBusinessObjectService
        from app.framework.schemas import CompanyBusinessObjectSchema
        from app.framework.controllers import create_business_object_router
        
        return {
            "framework_version": "1.0.0",
            "components": {
                "services": "CompanyBusinessObjectService with CRUD operations",
                "schemas": "Pydantic v2 schemas with validation",
                "controllers": "Auto-generated FastAPI routers",
                "extensions": "Dynamic custom field system",
                "audit": "Complete change tracking system"
            },
            "capabilities": {
                "custom_fields": {
                    "supported_types": ["string", "integer", "decimal", "boolean", "date", "datetime", "json"],
                    "validators": ["required", "email", "length", "range", "pattern", "options", "custom"],
                    "query_support": True
                },
                "audit_system": {
                    "automatic_logging": True,
                    "change_tracking": True,
                    "user_attribution": True,
                    "timestamp_precision": "microsecond"
                },
                "event_system": {
                    "redis_streams": True,
                    "correlation_ids": True,
                    "automatic_publishing": True,
                    "custom_events": True
                }
            },
            "performance": {
                "bulk_operations": True,
                "query_optimization": True,
                "caching_support": True,
                "database_indexing": True
            }
        }
    except Exception as e:
        return {"error": f"Framework information unavailable: {e}"}