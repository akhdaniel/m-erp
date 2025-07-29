"""
Audit logging router for security monitoring endpoints.
"""

from fastapi import APIRouter
from app.api.endpoints.audit import router as audit_endpoints_router

# Create the main audit router
router = APIRouter(prefix="/api/audit", tags=["audit"])

# Include all audit endpoints
router.include_router(audit_endpoints_router)