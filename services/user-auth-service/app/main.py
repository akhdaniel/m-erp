import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db
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


@asynccontextmanager
async def lifespan(app: FastAPI):
  # Startup
  logger.info("Starting up User Authentication Service...")
  logger.info("Database migrations handled by startup script")
  yield
  # Shutdown
  logger.info("Shutting down User Authentication Service...")
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