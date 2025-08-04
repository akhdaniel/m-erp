import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db
from app.core.service_registry_client import ServiceRegistryClient
from app.services.messaging_service import init_messaging, shutdown_messaging
from app.routers import auth, service_auth, token_validation, audit, password_policy
# from app.middleware.rate_limiting import rate_limit_middleware
from app.middleware.security_headers import security_headers_middleware, request_id_middleware
# from app.middleware.audit_middleware import audit_middleware

# Configure logging
logging.basicConfig(
  level=logging.INFO if not settings.debug else logging.DEBUG,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Global service registry client
registry_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
  global registry_client
  
  # Startup
  logger.info("Starting up User Authentication Service...")
  logger.info("Database migrations handled by startup script")
  
  # Initialize messaging service
  try:
    await init_messaging()
    logger.info("✓ Messaging service initialized")
  except Exception as e:
    logger.error(f"Messaging service initialization error: {e}")
  
  # Register with service registry
  try:
    registry_client = ServiceRegistryClient(
      service_name="user-auth-service",
      service_host="user-auth-service",
      service_port=8000,
      version="1.0.0",
      tags=["auth", "authentication", "users"],
      metadata={
        "description": "User authentication and authorization service",
        "capabilities": ["login", "registration", "jwt-tokens", "user-management"]
      }
    )
    
    success = await registry_client.register()
    if success:
      logger.info("✓ Successfully registered with service registry")
    else:
      logger.warning("✗ Failed to register with service registry")
  except Exception as e:
    logger.error(f"Service registry registration error: {e}")
  
  yield
  
  # Shutdown
  logger.info("Shutting down User Authentication Service...")
  
  # Shutdown messaging service
  try:
    await shutdown_messaging()
    logger.info("✓ Messaging service shutdown complete")
  except Exception as e:
    logger.error(f"Messaging service shutdown error: {e}")
  
  # Deregister from service registry
  if registry_client:
    try:
      await registry_client.deregister()
      await registry_client.close()
      logger.info("✓ Deregistered from service registry")
    except Exception as e:
      logger.error(f"Service registry deregistration error: {e}")
  
  await close_db()
  logger.info("Database connections closed")


def create_application() -> FastAPI:
  application = FastAPI(
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
  )
  
  # Security middleware (order is important)
  application.middleware("http")(request_id_middleware)
  application.middleware("http")(security_headers_middleware)
  # application.middleware("http")(rate_limit_middleware)
  # application.middleware("http")(audit_middleware)
  
  # CORS middleware
  application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
  
  # Include routers
  application.include_router(auth.router)
  application.include_router(auth.admin_router)
  application.include_router(service_auth.router)
  application.include_router(token_validation.router)
  application.include_router(audit.router)
  application.include_router(password_policy.router)
  
  return application


app = create_application()


@app.get("/health")
async def health_check():
  return {
    "status": "healthy",
    "service": settings.project_name,
    "version": settings.version,
    "environment": settings.environment
  }