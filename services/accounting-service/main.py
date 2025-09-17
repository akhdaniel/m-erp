"""
Accounting Service Main Application.

FastAPI application for the accounting management module providing
comprehensive accounting operations including chart of accounts,
journal entries, bank transactions, and financial reporting.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import asyncio
import logging
import os

from accounting_module.api import (
    accounts_router,
    journal_entries_router,
    bank_router,
    reports_router
)
from accounting_module.api.ui_schemas import router as ui_schemas_router 
from accounting_module.ui_definitions import ACCOUNTING_UI_PACKAGE

logger = logging.getLogger("uvicorn")
UI_REGISTRY_URL = os.getenv("UI_REGISTRY_URL")
NOTIFICATION_URL = os.getenv("NOTIFICATION_URL")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")

logger.info(f"UI_REGISTRY_URL={UI_REGISTRY_URL}, NOTIFICATION_URL={NOTIFICATION_URL}, MENU_SERVICE_URL={MENU_SERVICE_URL}")

# Custom middleware to handle forwarded headers for reverse proxy and rewrite redirect Location headers
class ForwardedHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get the host header from the request
        host_header = request.headers.get("host", "localhost:8008")
        
        response = await call_next(request)
        
        # If it's a redirect response, rewrite the Location header
        if response.status_code in (301, 302, 303, 307, 308) and "location" in response.headers:
            location = response.headers["location"]
            
            # Check if the location points to the internal service
            if location.startswith("http://accounting-service:8008/"):
                # Rewrite to use the host header from the request
                # Extract the path from the original location
                path = location[30:]  # Remove "http://accounting-service:8008"
                
                # Use the original host header from the request
                new_location = f"http://{host_header}{path}"
                response.headers["location"] = new_location
                
        return response

# Create FastAPI application
app = FastAPI(
    title="XERPIUM Accounting Service",
    description="Comprehensive accounting management service providing chart of accounts, journal entries, bank transactions, and financial reporting",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    root_path=""  # Reset root_path
)

# Add middleware
app.add_middleware(ForwardedHeadersMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(accounts_router)
app.include_router(journal_entries_router)
app.include_router(bank_router)
app.include_router(reports_router)
app.include_router(ui_schemas_router)

@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": "XERPIUM Accounting Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "Comprehensive accounting management service",
        "endpoints": {
            "accounts": "/accounts",
            "journal-entries": "/journal-entries",
            "bank-transactions": "/bank-transactions",
            "reports": "/reports",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "accounting-service",
        "timestamp": "2025-01-04T12:00:00Z"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Initialize service on startup")
    # Schedule menu and UI registration to run in background
    asyncio.create_task(initialize_menus_and_ui())

async def initialize_menus_and_ui():
    logger.info("Initialize menus and UI components in background")
    await asyncio.sleep(5)  # Give time for other services to start
    
    try:
        # Register menus
        from accounting_module.menu_init import initialize_accounting_menus
        await initialize_accounting_menus()
        logger.info("Menu initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize menus: {e}")
    
    # Register UI components
    try:
        from shared.ui_registration_client import register_service_ui
        import httpx
        
        register_service_ui("accounting-service", ACCOUNTING_UI_PACKAGE)
        logger.info("UI components registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register UI components: {e}")
    
    # Register dashboard in background after service is fully started
    async def register_dashboard_delayed():
        await asyncio.sleep(10)  # Wait for service to be fully started
        logger.info("Attempting to register dashboard with UI Registry...")
        async with httpx.AsyncClient() as client:
            try:
                # Get dashboard schema from our own endpoint
                logger.info("Fetching dashboard schema from local endpoint...")
                dashboard_response = await client.get("http://accounting-service:8008/ui-schemas/dashboard")
                if dashboard_response.status_code == 200:
                    dashboard_config = dashboard_response.json()
                    logger.info(f"Got dashboard config: {dashboard_config.get('title', 'Unknown')}")
                    
                    # Register with UI Registry
                    logger.info("Registering dashboard with UI Registry...")
                    registry_response = await client.post(
                        UI_REGISTRY_URL + "/services/accounting/dashboard",
                        json=dashboard_config
                    )
                    if registry_response.status_code == 200:
                        logger.info("Dashboard registered with UI Registry successfully")
                    else:
                        logger.error(f"Failed to register dashboard: {registry_response.status_code} - {registry_response.text}")
                else:
                    logger.error(f"Failed to get dashboard schema: {dashboard_response.status_code} - {dashboard_response.text}")
            except Exception as e:
                logger.error(f"Exception during dashboard registration: {e}")
    
    # Run dashboard registration in background
    asyncio.create_task(register_dashboard_delayed())

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    logger.info("Starting Development server")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )