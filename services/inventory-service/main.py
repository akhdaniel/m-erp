"""
Inventory Service Main Application.

FastAPI application for the inventory management module providing
comprehensive inventory operations including products, stock, warehouses,
and receiving functionality.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import logging

from inventory_module.api import (
    products_router,
    stock_router,
    warehouses_router,
    receiving_router
)
from inventory_module.api.ui_schemas import router as ui_schemas_router
from inventory_module.ui_definitions import INVENTORY_UI_PACKAGE

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="XERPIUM Inventory Service",
    description="Comprehensive inventory management service providing product catalog, stock management, warehouse operations, and receiving functionality",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(products_router, prefix="/api/v1")
app.include_router(stock_router, prefix="/api/v1")
app.include_router(warehouses_router, prefix="/api/v1")
app.include_router(receiving_router, prefix="/api/v1")
app.include_router(ui_schemas_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": "XERPIUM Inventory Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "Comprehensive inventory management service",
        "endpoints": {
            "products": "/api/v1/products",
            "stock": "/api/v1/stock",
            "warehouses": "/api/v1/warehouses",
            "receiving": "/api/v1/receiving",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "inventory-service",
        "timestamp": "2025-01-04T12:00:00Z"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    # Schedule menu and UI registration to run in background
    asyncio.create_task(initialize_menus_and_ui())


async def initialize_menus_and_ui():
    """Initialize menus and UI components in background"""
    await asyncio.sleep(5)  # Give time for other services to start
    
    try:
        # Register menus
        from inventory_module.menu_init import initialize_inventory_menus
        await initialize_inventory_menus()
        logger.info("Menu initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize menus: {e}")
    
    # Register UI components
    try:
        from shared.ui_registration_client import register_service_ui
        import httpx
        
        register_service_ui("inventory-service", INVENTORY_UI_PACKAGE)
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
                dashboard_response = await client.get("http://localhost:8005/api/v1/ui-schemas/dashboard")
                if dashboard_response.status_code == 200:
                    dashboard_config = dashboard_response.json()
                    logger.info(f"Got dashboard config: {dashboard_config.get('title', 'Unknown')}")
                    
                    # Register with UI Registry
                    logger.info("Registering dashboard with UI Registry...")
                    registry_response = await client.post(
                        "http://ui-registry-service:8010/api/v1/services/inventory/dashboard",
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
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )