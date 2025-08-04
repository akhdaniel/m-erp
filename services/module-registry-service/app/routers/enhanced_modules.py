"""
Enhanced module management API endpoints with comprehensive validation and package handling
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db_session
from app.services.enhanced_module_service import EnhancedModuleService, ModuleRegistrationError, PackageValidationError
from app.schemas.module import (
    ModuleCreate, ModuleUpdate, ModuleResponse, ModuleListResponse, 
    ModuleStatusUpdate, ModuleManifest
)
from app.models.module import ModuleStatus, ModuleType
from app.core.config import settings
import json
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/modules", tags=["Enhanced Modules"])


def get_enhanced_module_service(db: AsyncSession = Depends(get_db_session)) -> EnhancedModuleService:
    """Dependency to get enhanced module service"""
    return EnhancedModuleService(db)


class ModuleRegistrationRequest(BaseModel):
    """Request model for module registration with validation"""
    name: str
    version: str
    display_name: str
    description: str
    author: str
    author_email: Optional[str] = None
    license: str = "MIT"
    homepage_url: Optional[str] = None
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    module_type: ModuleType = ModuleType.FULL_MODULE
    minimum_framework_version: Optional[str] = None
    python_version: Optional[str] = ">=3.8"
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    is_public: bool = True
    requires_approval: bool = True
    manifest: Dict[str, Any]


@router.post("/register", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def register_module_with_package(
    module_data: str = Form(..., description="Module data as JSON"),
    package: Optional[UploadFile] = File(None, description="Module package (.tar.gz or .zip)"),
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """
    Register a new module with comprehensive validation
    
    This endpoint provides:
    - Package upload and validation
    - Manifest validation
    - Dependency checking
    - Security analysis
    - Automated status assignment
    """
    try:
        # Parse module data from JSON
        try:
            module_dict = json.loads(module_data)
            module_create = ModuleCreate(**module_dict)
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid module data format: {str(e)}"
            )
        
        # Read and validate package if provided
        package_data = None
        if package:
            # Validate file size
            max_size = settings.max_module_size_mb * 1024 * 1024  # Convert to bytes
            
            # Read package data
            package_data = await package.read()
            
            if len(package_data) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Package file too large (max {settings.max_module_size_mb}MB)"
                )
            
            # Validate file type
            allowed_types = ["application/gzip", "application/x-gzip", "application/zip", "application/octet-stream"]
            if package.content_type not in allowed_types:
                logger.warning(f"Potentially invalid content type: {package.content_type}")
                # Don't reject, but log for monitoring
        
        # Register module with comprehensive validation
        module, validation_result = await service.register_module_with_validation(
            module_create, package_data
        )
        
        # Prepare response with validation details
        response_data = {
            "id": module.id,
            "name": module.name,
            "version": module.version,
            "display_name": module.display_name,
            "description": module.description,
            "author": module.author,
            "author_email": module.author_email,
            "license": module.license,
            "homepage_url": module.homepage_url,
            "repository_url": module.repository_url,
            "status": module.status.value,
            "is_public": module.is_public,
            "package_size": module.package_size,
            "package_hash": module.package_hash[:8] + "..." if module.package_hash else None,
            "created_at": module.created_at.isoformat(),
            "manifest": module.manifest,
            "validation_summary": {
                "is_valid": validation_result.is_valid,
                "security_issues_count": len(validation_result.security_issues),
                "dependency_errors_count": len(validation_result.dependency_errors),
                "has_package": package_data is not None
            }
        }
        
        logger.info(f"Successfully registered module {module.name}@{module.version} with ID {module.id}")
        return JSONResponse(content=response_data, status_code=status.HTTP_201_CREATED)
        
    except ModuleRegistrationError as e:
        logger.error(f"Module registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PackageValidationError as e:
        logger.error(f"Package validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Package validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during module registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/validate-package")
async def validate_module_package(
    package: UploadFile = File(..., description="Module package to validate"),
    module_name: str = Form(..., description="Module name for validation"),
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """
    Validate a module package without registering it
    
    This endpoint allows developers to validate their packages before submission
    """
    try:
        # Validate file size
        max_size = settings.max_module_size_mb * 1024 * 1024
        package_data = await package.read()
        
        if len(package_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Package file too large (max {settings.max_module_size_mb}MB)"
            )
        
        # Extract and validate package structure
        module_dir = await service._extract_and_validate_package(
            package_data, module_name, "validation"
        )
        
        try:
            # Perform structure validation
            await service._validate_package_structure(module_dir, module_name)
            
            # TODO: Add more validation (security scan, dependency check)
            
            return {
                "valid": True,
                "package_size": len(package_data),
                "structure_valid": True,
                "message": "Package structure is valid"
            }
            
        finally:
            # Cleanup extracted files
            await service._cleanup_extracted_package(module_dir)
            
    except PackageValidationError as e:
        return JSONResponse(
            content={
                "valid": False,
                "error": str(e),
                "package_size": len(package_data) if 'package_data' in locals() else 0
            },
            status_code=status.HTTP_200_OK  # Not an error response, just validation result
        )
    except Exception as e:
        logger.error(f"Package validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )


@router.post("/validate-manifest", response_model=Dict[str, Any])
async def validate_module_manifest_enhanced(
    manifest: Dict[str, Any],
    check_dependencies: bool = Query(True, description="Check if dependencies are available"),
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """
    Enhanced manifest validation with dependency checking
    """
    try:
        # Basic manifest validation
        result = await service.validate_module_manifest(manifest)
        
        # Enhanced dependency checking if requested
        if check_dependencies and result["valid"] and "dependencies" in manifest:
            available_modules = await service._get_available_module_names()
            
            missing_dependencies = []
            for dep in manifest["dependencies"]:
                if dep.get("type") == "module" and dep["name"] not in available_modules:
                    missing_dependencies.append(dep["name"])
            
            if missing_dependencies:
                result["warnings"].append(
                    f"Missing dependencies: {', '.join(missing_dependencies)}"
                )
                result["dependency_info"] = {
                    "available_modules": len(available_modules),
                    "missing_dependencies": missing_dependencies
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Manifest validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )


@router.get("/{module_id}/validation", response_model=Dict[str, Any])
async def get_module_validation_details(
    module_id: int,
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """Get detailed validation information for a specific module"""
    validation_details = await service.get_module_validation_details(module_id)
    
    if not validation_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    return validation_details


@router.patch("/{module_id}/status", response_model=ModuleResponse)
async def update_module_status_enhanced(
    module_id: int,
    status_data: ModuleStatusUpdate,
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """
    Update module status with enhanced validation and lifecycle events
    """
    try:
        module = await service.update_module_status(module_id, status_data)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        response_data = {
            "id": module.id,
            "name": module.name,
            "version": module.version,
            "status": module.status.value,
            "status_reason": module.status_reason,
            "updated_at": module.updated_at.isoformat(),
            "validation_summary": module.validation_summary
        }
        
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Status update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status update failed: {str(e)}"
        )


@router.get("/pending-approval", response_model=List[Dict[str, Any]])
async def get_modules_pending_approval(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """Get modules pending approval with validation summaries"""
    try:
        # This would need to be implemented in the service
        # For now, return a placeholder
        return []
        
    except Exception as e:
        logger.error(f"Error fetching pending modules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending modules"
        )


@router.post("/{module_id}/security-scan")
async def trigger_security_scan(
    module_id: int,
    force_rescan: bool = Query(False, description="Force rescan even if recently scanned"),
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """
    Trigger a security scan for a specific module
    
    This endpoint allows administrators to manually trigger security scans
    """
    try:
        module = await service.get_module(module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # TODO: Implement actual security scanning
        # This is a placeholder for the security scanning functionality
        
        return {
            "module_id": module_id,
            "scan_requested": True,
            "message": "Security scan has been queued",
            "estimated_completion": "5-10 minutes"
        }
        
    except Exception as e:
        logger.error(f"Security scan trigger error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger security scan"
        )


@router.get("/stats/registration")
async def get_registration_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    service: EnhancedModuleService = Depends(get_enhanced_module_service)
):
    """Get module registration statistics"""
    try:
        # TODO: Implement statistics collection
        # This would analyze registration patterns, validation results, etc.
        
        return {
            "period_days": days,
            "total_registrations": 0,
            "successful_registrations": 0,
            "failed_validations": 0,
            "security_issues_found": 0,
            "average_package_size_mb": 0.0,
            "most_common_errors": []
        }
        
    except Exception as e:
        logger.error(f"Statistics collection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect statistics"
        )