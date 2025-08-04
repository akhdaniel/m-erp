"""
Module management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.module_service import ModuleService
from app.schemas.module import (
    ModuleCreate, ModuleUpdate, ModuleResponse, ModuleListResponse, 
    ModuleStatusUpdate, ModuleManifest
)
from app.models.module import ModuleStatus, ModuleType
import io


router = APIRouter(prefix="/modules", tags=["Modules"])


def get_module_service(db: AsyncSession = Depends(get_db_session)) -> ModuleService:
    """Dependency to get module service"""
    return ModuleService(db)


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    package: Optional[UploadFile] = File(None),
    service: ModuleService = Depends(get_module_service)
):
    """Create a new module"""
    try:
        # Read package data if provided
        package_data = None
        if package:
            package_data = await package.read()
            
            # Validate file size (50MB limit)
            if len(package_data) > 50 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Package file too large (max 50MB)"
                )
        
        # Validate manifest
        validation_result = await service.validate_module_manifest(module_data.manifest)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Invalid module manifest",
                    "errors": validation_result["errors"]
                }
            )
        
        # Check if module already exists
        existing = await service.get_module_by_name_version(module_data.name, module_data.version)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Module {module_data.name}@{module_data.version} already exists"
            )
        
        module = await service.create_module(module_data, package_data)
        return module
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=ModuleListResponse)
async def list_modules(
    skip: int = Query(0, ge=0, description="Number of modules to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of modules to return"),
    status: Optional[ModuleStatus] = Query(None, description="Filter by module status"),
    module_type: Optional[ModuleType] = Query(None, description="Filter by module type"),
    search: Optional[str] = Query(None, description="Search modules by name, description, or author"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private modules"),
    service: ModuleService = Depends(get_module_service)
):
    """List modules with filtering and pagination"""
    try:
        modules, total = await service.list_modules(
            skip=skip,
            limit=limit,
            status=status,
            module_type=module_type,
            search=search,
            is_public=is_public
        )
        
        return ModuleListResponse(
            modules=modules,
            total=total,
            page=skip // limit + 1,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service)
):
    """Get module by ID"""
    module = await service.get_module(module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
    return module


@router.get("/by-name/{name}/versions/{version}", response_model=ModuleResponse)
async def get_module_by_name_version(
    name: str,
    version: str,
    service: ModuleService = Depends(get_module_service)
):
    """Get module by name and version"""
    module = await service.get_module_by_name_version(name, version)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module {name}@{version} not found"
        )
    
    return module


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    service: ModuleService = Depends(get_module_service)
):
    """Update module"""
    try:
        module = await service.update_module(module_id, module_data)
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
        
        return module
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{module_id}/status", response_model=ModuleResponse)
async def update_module_status(
    module_id: int,
    status_data: ModuleStatusUpdate,
    service: ModuleService = Depends(get_module_service)
):
    """Update module status (approve/reject/deprecate)"""
    try:
        module = await service.update_module_status(module_id, status_data)
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
        
        return module
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    service: ModuleService = Depends(get_module_service)
):
    """Delete module (soft delete)"""
    try:
        success = await service.delete_module(module_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{module_id}/package")
async def download_module_package(
    module_id: int,
    service: ModuleService = Depends(get_module_service)
):
    """Download module package"""
    module = await service.get_module(module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
    if not module.package_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module package not available"
        )
    
    # Create streaming response for file download
    package_stream = io.BytesIO(module.package_data)
    
    return StreamingResponse(
        io.BytesIO(module.package_data),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={module.name}-{module.version}.tar.gz"
        }
    )


@router.get("/{module_id}/dependencies")
async def get_module_dependencies(
    module_id: int,
    service: ModuleService = Depends(get_module_service)
):
    """Get module dependencies"""
    dependencies = await service.get_module_dependencies(module_id)
    return {"dependencies": [dep.to_dict() for dep in dependencies]}


@router.get("/{module_id}/dependents")
async def get_module_dependents(
    module_id: int,
    service: ModuleService = Depends(get_module_service)
):
    """Get modules that depend on this module"""
    dependents = await service.get_module_dependents(module_id)
    return {"dependents": [dep.to_dict() for dep in dependents]}


@router.post("/validate-manifest")
async def validate_module_manifest(
    manifest: ModuleManifest,
    service: ModuleService = Depends(get_module_service)
):
    """Validate a module manifest"""
    try:
        result = await service.validate_module_manifest(manifest.dict())
        return result
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/{query}")
async def search_modules(
    query: str,
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    service: ModuleService = Depends(get_module_service)
):
    """Search modules"""
    try:
        modules = await service.search_modules(query, limit)
        return {"modules": [module.to_dict() for module in modules]}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))