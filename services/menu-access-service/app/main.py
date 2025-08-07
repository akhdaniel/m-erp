import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import close_db, get_db
from app.middleware.auth import auth_client
from app.middleware.request_auth import AuthenticationMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Menu & Access Rights Service...")
    logger.info("Database migrations handled by startup script")
    yield
    # Shutdown
    logger.info("Shutting down Menu & Access Rights Service...")
    await close_db()
    await auth_client.close()
    logger.info("Database connections and auth client closed")


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.project_name,
        description=settings.description,
        version=settings.version,
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
    
    # Authentication middleware
    application.add_middleware(AuthenticationMiddleware)
    
    # Include API routers
    from app.routers import menu
    application.include_router(menu.router, prefix="/api/v1")
    
    return application


app = create_application()


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Menu & Access Rights Service",
        "version": settings.version,
        "description": settings.description,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status."""
    # Basic health response
    health_data = {
        "status": "healthy",
        "service": "menu-access-service",
        "version": settings.version,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": "unknown",
            "auth_service": "unknown"
        }
    }
    
    # Check database connectivity
    try:
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
    
    return health_data