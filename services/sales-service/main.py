"""
FastAPI application entry point for Sales Service.

This is the main application file that sets up the FastAPI server
with all routes, middleware, and configuration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

# Add the sales_module to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import API routers
from sales_module.api.quote_api import router as quote_router
from sales_module.api.order_api import router as order_router
from sales_module.api.pricing_api import router as pricing_router

# Import UI definitions
from sales_module.ui_definitions import SALES_UI_PACKAGE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="M-ERP Sales Service",
    description="Sales management microservice for M-ERP platform",
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
app.include_router(quote_router)
app.include_router(order_router)
app.include_router(pricing_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "sales-service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "quotes": "/api/v1/quotes",
            "orders": "/orders",
            "pricing": "/pricing",
            "docs": "/api/docs",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "sales-service",
        "version": "1.0.0"
    }

# Startup event to initialize menus
@app.on_event("startup")
async def startup_event():
    """Initialize service components on startup."""
    import asyncio
    logger.info("Starting sales service...")
    
    # Initialize menus (non-blocking, log errors but don't fail startup)
    try:
        from sales_module.menu_init import initialize_sales_menus
        await initialize_sales_menus()
        logger.info("Menu initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize menus: {e}")
        # Continue startup even if menu registration fails
    
    # Register UI components with UI Registry
    try:
        from shared.ui_registration_client import register_service_ui
        
        # Register UI package with a delay to ensure UI registry is ready
        await asyncio.sleep(5)
        register_service_ui("sales-service", SALES_UI_PACKAGE)
        logger.info("UI components registered successfully")
    except Exception as e:
        logger.error(f"Failed to register UI components: {e}")
        # Continue startup even if UI registration fails
    
    logger.info("Sales service started successfully")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")