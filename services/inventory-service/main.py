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

from inventory_module.api import (
    products_router,
    stock_router,
    warehouses_router,
    receiving_router
)

# Create FastAPI application
app = FastAPI(
    title="M-ERP Inventory Service",
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


@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": "M-ERP Inventory Service",
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