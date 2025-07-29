"""
Password policy endpoints - provides password policy information and validation.
"""

from typing import Dict, Optional, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.password_service import PasswordService
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter()


class PasswordValidationRequest(BaseModel):
    """Password validation request."""
    password: str = Field(..., min_length=1, max_length=128)
    user_context: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional user context for personal info checks"
    )


class PasswordValidationResponse(BaseModel):
    """Password validation response."""
    is_valid: bool
    score: int
    feedback: list[str]
    strength: str
    violations: list[str]
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_special: bool
    unique_chars: int
    length: int


class PasswordPolicyInfoResponse(BaseModel):
    """Password policy information response."""
    requirements: Dict[str, Any]
    guidelines: list[str]
    forbidden: list[str]


class GeneratePasswordRequest(BaseModel):
    """Generate password request."""
    length: int = Field(default=12, ge=8, le=64)


class GeneratePasswordResponse(BaseModel):
    """Generate password response."""
    password: str
    validation: PasswordValidationResponse


@router.get("/policy", response_model=PasswordPolicyInfoResponse)
async def get_password_policy():
    """
    Get current password policy requirements and guidelines.
    
    Returns comprehensive information about password requirements,
    guidelines for creating strong passwords, and forbidden patterns.
    """
    policy_info = PasswordService.get_password_policy_info()
    return PasswordPolicyInfoResponse(**policy_info)


@router.post("/validate", response_model=PasswordValidationResponse)
async def validate_password(request: PasswordValidationRequest):
    """
    Validate a password against the current policy.
    
    Provides comprehensive validation including:
    - Policy compliance checking
    - Strength scoring (0-100)
    - Detailed feedback for improvement
    - Pattern detection (sequential, repeated chars, etc.)
    - Personal information checking (if context provided)
    """
    try:
        validation_result = PasswordService.validate_password_policy(
            password=request.password,
            user_context=request.user_context
        )
        
        return PasswordValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {str(e)}"
        )


@router.post("/validate-for-user", response_model=PasswordValidationResponse)
async def validate_password_for_user(
    request: PasswordValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a password for the current authenticated user.
    
    Includes all standard validation plus:
    - Password history checking (prevents reuse)
    - User-specific context (email, name) for personal info detection
    """
    try:
        # Prepare user context for personal info checking
        user_context = {
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "name": current_user.full_name
        }
        
        # Merge with any additional context provided
        if request.user_context:
            user_context.update(request.user_context)
        
        # Validate password policy
        validation_result = PasswordService.validate_password_policy(
            password=request.password,
            user_context=user_context
        )
        
        # Check password history if validation passes
        if validation_result["is_valid"]:
            history_ok = await PasswordService.check_password_history(
                db=db,
                user_id=current_user.id,
                new_password=request.password
            )
            
            if not history_ok:
                validation_result["is_valid"] = False
                validation_result["violations"].append("password_reuse")
                validation_result["feedback"].append(
                    "Password has been used recently. Please choose a different password."
                )
        
        return PasswordValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {str(e)}"
        )


@router.post("/generate", response_model=GeneratePasswordResponse)
async def generate_secure_password(request: GeneratePasswordRequest):
    """
    Generate a secure password that meets all policy requirements.
    
    Returns a randomly generated password with:
    - Specified length (minimum 8, default 12)
    - All character types (uppercase, lowercase, digits, special)
    - No forbidden patterns
    - High entropy and strength score
    """
    try:
        # Generate secure password
        password = PasswordService.generate_secure_password(length=request.length)
        
        # Validate the generated password to provide stats
        validation_result = PasswordService.validate_password_policy(password)
        
        return GeneratePasswordResponse(
            password=password,
            validation=PasswordValidationResponse(**validation_result)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password generation failed: {str(e)}"
        )


@router.get("/strength/{password}")
async def check_password_strength(password: str):
    """
    Quick password strength check (for client-side validation).
    
    Note: This endpoint should be used sparingly and only for
    client-side feedback. Passwords should not be sent in URLs
    in production. Use POST /validate instead.
    """
    if len(password) > 128:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long for URL parameter"
        )
    
    try:
        validation_result = PasswordService.validate_password_policy(password)
        
        return {
            "strength": validation_result["strength"],
            "score": validation_result["score"],
            "is_valid": validation_result["is_valid"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strength check failed: {str(e)}"
        )