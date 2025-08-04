"""
Module installation API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.installation_service import InstallationService
from app.schemas.installation import (
    InstallationCreate, InstallationUpdate, InstallationResponse, 
    InstallationListResponse, InstallationStatusUpdate, HealthCheckResult
)
from app.models.installation import InstallationStatus


router = APIRouter(prefix="/installations", tags=["Installations"])


def get_installation_service(db: AsyncSession = Depends(get_db_session)) -> InstallationService:
    """Dependency to get installation service"""
    return InstallationService(db)


# TODO: Add authentication and get current user
def get_current_user():
    """Get current user - placeholder for auth integration"""
    return {"id": 1, "username": "admin"}


@router.post("/", response_model=InstallationResponse, status_code=status.HTTP_201_CREATED)
async def create_installation(
    installation_data: InstallationCreate,
    current_user=Depends(get_current_user),
    service: InstallationService = Depends(get_installation_service)
):
    """Create a new module installation"""
    try:
        installation = await service.create_installation(
            installation_data, 
            installed_by=current_user["username"]
        )
        return installation
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=InstallationListResponse)
async def list_installations(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    module_id: Optional[int] = Query(None, description="Filter by module ID"),
    status: Optional[InstallationStatus] = Query(None, description="Filter by installation status"),
    skip: int = Query(0, ge=0, description="Number of installations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of installations to return"),
    service: InstallationService = Depends(get_installation_service)
):
    """List installations with filtering and pagination"""
    try:
        installations, total = await service.list_installations(
            company_id=company_id,
            module_id=module_id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return InstallationListResponse(
            installations=installations,
            total=total,
            page=skip // limit + 1,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{installation_id}", response_model=InstallationResponse)
async def get_installation(
    installation_id: int,
    service: InstallationService = Depends(get_installation_service)
):
    """Get installation by ID"""
    installation = await service.get_installation(installation_id)
    if not installation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation not found")
    
    return installation


@router.put("/{installation_id}", response_model=InstallationResponse)
async def update_installation(
    installation_id: int,
    installation_data: InstallationUpdate,
    service: InstallationService = Depends(get_installation_service)
):
    """Update installation configuration"""
    try:
        installation = await service.update_installation(installation_id, installation_data)
        if not installation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation not found")
        
        return installation
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{installation_id}/status", response_model=InstallationResponse)
async def update_installation_status(
    installation_id: int,
    status_data: InstallationStatusUpdate,
    service: InstallationService = Depends(get_installation_service)
):
    """Update installation status"""
    try:
        installation = await service.update_installation_status(installation_id, status_data)
        if not installation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation not found")
        
        return installation
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{installation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_module(
    installation_id: int,
    service: InstallationService = Depends(get_installation_service)
):
    """Uninstall module"""
    try:
        success = await service.uninstall_module(installation_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installation not found")
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{installation_id}/health-check", response_model=HealthCheckResult)
async def perform_health_check(
    installation_id: int,
    service: InstallationService = Depends(get_installation_service)
):
    """Perform health check on installation"""
    try:
        result = await service.perform_health_check(installation_id)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/company/{company_id}", response_model=List[InstallationResponse])
async def get_company_installations(
    company_id: int,
    service: InstallationService = Depends(get_installation_service)
):
    """Get all active installations for a company"""
    try:
        installations = await service.get_company_installations(company_id)
        return installations
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/module/{module_id}", response_model=List[InstallationResponse])
async def get_module_installations(
    module_id: int,
    service: InstallationService = Depends(get_installation_service)
):
    """Get all installations for a module"""
    try:
        installations = await service.get_module_installations(module_id)
        return installations
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/check/{module_id}/{company_id}")
async def check_installation_exists(
    module_id: int,
    company_id: int,
    service: InstallationService = Depends(get_installation_service)
):
    """Check if installation exists for module and company"""
    try:
        exists = await service.installation_exists(module_id, company_id)
        return {"exists": exists}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))