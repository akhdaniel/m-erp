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
app.include_router(ui_schemas_router, prefix="/api/v1")

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
        from shared.menu_registration_client import MenuRegistrationClient
        
        client = MenuRegistrationClient(
            menu_service_url=os.getenv('MENU_SERVICE_URL', 'http://menu-access-service:8003')
        )
        
        # Define purchasing menus
        menus = [
            {
                "code": "purchasing",
                "name": "Purchasing",
                "path": "/purchasing",
                "icon": "shopping-cart",
                "sequence": 30,
                "parent_id": None,
                "permission": "purchasing.access"
            },
            {
                "code": "purchasing.orders",
                "name": "Purchase Orders",
                "path": "/purchasing/orders",
                "icon": "file-text",
                "sequence": 10,
                "parent_code": "purchasing",
                "permission": "purchasing.orders.read"
            },
            {
                "code": "purchasing.suppliers",
                "name": "Suppliers",
                "path": "/purchasing/suppliers",
                "icon": "truck",
                "sequence": 20,
                "parent_code": "purchasing",
                "permission": "purchasing.suppliers.read"
            },
            {
                "code": "purchasing.approvals",
                "name": "Approvals",
                "path": "/purchasing/approvals",
                "icon": "check-circle",
                "sequence": 30,
                "parent_code": "purchasing",
                "permission": "purchasing.approvals.read"
            },
            {
                "code": "purchasing.reports",
                "name": "Reports",
                "path": "/purchasing/reports",
                "icon": "bar-chart",
                "sequence": 40,
                "parent_code": "purchasing",
                "permission": "purchasing.reports.read"
            },
            {
                "code": "purchasing.settings",
                "name": "Settings",
                "path": "/purchasing/settings",
                "icon": "settings",
                "sequence": 50,
                "parent_code": "purchasing",
                "permission": "purchasing.settings.read"
            }
        ]
        
        # Convert menu dicts to MenuItem objects
        from shared.menu_registration_client import MenuItem, MenuPermission
        
        menu_items = []
        for menu in menus:
            menu_item = MenuItem(
                code=menu['code'],
                title=menu['name'],
                description=menu.get('name'),
                parent_code=menu.get('parent_code'),
                order_index=menu.get('sequence', 0),
                url=menu.get('path', '#'),
                icon=menu.get('icon'),
                required_permission=menu.get('permission')
            )
            menu_items.append(menu_item)
        
        # Register all menus at once
        success = await client.register_menus(menu_items)
        if success:
            logger.info(f"Registered {len(menu_items)} menus successfully")
        else:
            logger.warning("Failed to register menus")
        
        # Register permissions
        permissions = [
            MenuPermission(
                code="purchasing.access",
                name="Purchasing Management",
                description="Access to purchasing module",
                category="purchasing"
            ),
            MenuPermission(
                code="purchasing.orders.read",
                name="View Purchase Orders",
                description="View purchase orders",
                category="purchasing",
                action="read"
            ),
            MenuPermission(
                code="purchasing.orders.write",
                name="Create/Edit Purchase Orders",
                description="Create and edit purchase orders",
                category="purchasing",
                action="write"
            ),
            MenuPermission(
                code="purchasing.suppliers.read",
                name="View Suppliers",
                description="View supplier information",
                category="purchasing",
                action="read"
            ),
            MenuPermission(
                code="purchasing.suppliers.write",
                name="Manage Suppliers",
                description="Create and edit suppliers",
                category="purchasing",
                action="write"
            ),
            MenuPermission(
                code="purchasing.approvals.read",
                name="View Approvals",
                description="View approval workflows",
                category="purchasing",
                action="read"
            ),
            MenuPermission(
                code="purchasing.approvals.write",
                name="Manage Approvals",
                description="Approve or reject purchase orders",
                category="purchasing",
                action="write"
            ),
            MenuPermission(
                code="purchasing.reports.read",
                name="View Reports",
                description="View purchasing reports",
                category="purchasing",
                action="read"
            ),
            MenuPermission(
                code="purchasing.settings.read",
                name="View Settings",
                description="View purchasing settings",
                category="purchasing",
                action="read"
            ),
        ]
        
        success = await client.register_permissions(permissions)
        if success:
            logger.info(f"Registered {len(permissions)} permissions successfully")
        
        logger.info("Menu registration completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to register menus: {e}")

# UI registration with UI Registry Service
async def register_ui_components():
    """Register UI components with the UI Registry Service."""
    try:
        ui_registry_url = os.getenv('UI_REGISTRY_URL', 'http://ui-registry-service:8010')
        
        async with httpx.AsyncClient() as client:
            # Register complete UI package
            response = await client.post(
                f"{ui_registry_url}/api/v1/services/purchasing/ui-package",
                json=PURCHASING_UI_PACKAGE
            )
            
            if response.status_code == 200:
                logger.info("UI package registered successfully")
            else:
                logger.warning(f"Failed to register UI package: {response.status_code}")
        
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