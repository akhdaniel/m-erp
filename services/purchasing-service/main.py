"""
FastAPI application entry point for Purchasing Service.

This is the main application file that sets up the FastAPI server
with all routes, middleware, and configuration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
import asyncio
import httpx
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import API routers
from purchasing_module.api import (
    purchase_orders_router as purchase_order_router,
    suppliers_router as supplier_router,
    approvals_router as approval_router,
    dashboard_router
)
from purchasing_module.api.ui_schemas import router as ui_schemas_router

# Import UI definitions
from purchasing_module.ui_definitions import PURCHASING_UI_PACKAGE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="XERPIUM Purchasing Service",
    description="Purchasing management microservice for XERPIUM platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(purchase_order_router)
app.include_router(supplier_router)
app.include_router(approval_router)
app.include_router(dashboard_router)
app.include_router(ui_schemas_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "purchasing-service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "purchase_orders": "/api/v1/purchase-orders",
            "suppliers": "/api/v1/suppliers",
            "approvals": "/api/v1/approvals",
            "dashboard": "/api/v1/dashboard",
            "docs": "/api/docs",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "service": "purchasing-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# Service registration with Menu Service
async def register_menus():
    """Register purchasing menus with the menu service."""
    try:
        from purchasing_module.menu_init import init_menus_on_startup
        
        # Initialize menus using the menu_init module
        success = init_menus_on_startup()
        if success:
            logger.info("Purchasing menus registered successfully")
        else:
            logger.warning("Failed to register purchasing menus")
            
    except Exception as e:
        logger.error(f"Failed to register menus: {e}")

# UI registration with UI Registry Service
async def register_ui_components():
    """Register UI components with the UI Registry Service."""
    try:
        # Import and run the register_ui script
        import subprocess
        import sys
        
        # Run the register_ui.py script
        result = subprocess.run([sys.executable, "register_ui.py"], 
                              cwd="/opt/m-erp/services/purchasing-service",
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("UI components registered successfully")
        else:
            logger.warning(f"Failed to register UI components: {result.stderr}")
        
    except Exception as e:
        logger.error(f"Failed to register UI components: {e}")

# Register dashboard with UI Registry
async def register_dashboard():
    """Register purchasing dashboard with UI Registry."""
    try:
        # Wait a bit for UI Registry to be ready
        await asyncio.sleep(10)
        
        logger.info("Attempting to register dashboard with UI Registry...")
        
        # First, try to get the dashboard schema from our local endpoint
        logger.info("Fetching dashboard schema from local endpoint...")
        async with httpx.AsyncClient() as client:
            local_response = await client.get("http://localhost:8007/api/v1/ui-schemas/dashboard")
            if local_response.status_code == 200:
                dashboard_config = local_response.json()
                logger.info(f"Got dashboard config: {dashboard_config.get('title', 'Unknown')}")
                
                # Now register with UI Registry
                logger.info("Registering dashboard with UI Registry...")
                ui_registry_url = os.getenv('UI_REGISTRY_URL', 'http://ui-registry-service:8010')
                registry_response = await client.post(
                    f"{ui_registry_url}/api/v1/services/purchasing/dashboard",
                    json=dashboard_config
                )
                
                if registry_response.status_code == 200:
                    logger.info("Dashboard registered with UI Registry successfully")
                else:
                    logger.error(f"Failed to register dashboard: {registry_response.status_code} - {registry_response.text}")
            else:
                logger.error(f"Failed to fetch dashboard schema: {local_response.status_code}")
                
    except Exception as e:
        logger.error(f"Failed to register dashboard: {e}")

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info("Starting Purchasing Service...")
    
    # Register menus
    asyncio.create_task(register_menus())
    
    # Register UI components
    asyncio.create_task(register_ui_components())
    
    # Register dashboard
    asyncio.create_task(register_dashboard())
    
    logger.info("Purchasing service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown tasks."""
    logger.info("Shutting down Purchasing Service...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)