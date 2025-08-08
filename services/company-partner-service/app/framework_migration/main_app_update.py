"""
Updated main application with framework-based Partner endpoints.

This demonstrates how to integrate the framework-based Partner service
into the main FastAPI application.
"""

from fastapi import FastAPI
from app.framework_migration.partner_router import router as framework_partner_router
from app.framework_migration.partner_router import framework_partner_router as generated_partner_router

# Add to existing FastAPI app
def include_framework_partner_routes(app: FastAPI):
    """Include framework-based Partner routes in the application."""
    
    # Option 1: Custom router with business logic
    app.include_router(framework_partner_router, prefix="/api/v1")
    
    # Option 2: Auto-generated framework router
    app.include_router(generated_partner_router.router, prefix="/api/v1")
    
    print("✅ Framework-based Partner routes included")
    print("📋 Available endpoints:")
    print("  • /api/v1/partners-framework/ - Custom framework router")
    print("  • /api/v1/partners/ - Auto-generated framework router")
    print("  • Both routers include extension and audit endpoints")


# Example usage in main.py:
"""
from app.framework_migration.main_app_update import include_framework_partner_routes

app = FastAPI(title="XERPIUM", version="2.0.0")

# Include framework routes
include_framework_partner_routes(app)
"""