"""
Password policy router - handles password policy endpoints.
"""

from fastapi import APIRouter
from app.api.endpoints.password_policy import router as password_policy_router

router = APIRouter(
    prefix="/api/password-policy",
    tags=["password-policy"],
    responses={404: {"description": "Not found"}}
)

# Include password policy endpoints
router.include_router(password_policy_router)