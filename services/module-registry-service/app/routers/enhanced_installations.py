"""
Enhanced installation management API endpoints with plugin framework integration
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.enhanced_installation_service import (
    EnhancedInstallationService, InstallationError, UninstallationError
)
from app.schemas.installation import (
    InstallationCreate, InstallationUpdate, InstallationResponse, 
    InstallationListResponse, InstallationStatusUpdate, HealthCheckResult
)
from app.models.installation import InstallationStatus
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/installations", tags=["Enhanced Installations"])


def get_enhanced_installation_service(db: AsyncSession = Depends(get_db_session)) -> EnhancedInstallationService:
    """Dependency to get enhanced installation service"""
    return EnhancedInstallationService(db)


# TODO: Add authentication and get current user
def get_current_user():
    """Get current user - placeholder for auth integration"""
    return {"id": 1, "username": "admin"}


@router.post("/install", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def install_module_with_framework(
    installation_data: InstallationCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """
    Install a module with full plugin framework integration
    
    This endpoint provides:
    - Dependency validation and loading
    - Plugin framework integration
    - Endpoint registration
    - Module initialization
    - Comprehensive error handling and rollback
    """
    try:
        # Install module (this is a potentially long-running operation)
        installation, loaded_module = await service.install_module(
            installation_data, 
            installed_by=current_user["username"]
        )
        
        response_data = {
            "id": installation.id,
            "module_id": installation.module_id,
            "company_id": installation.company_id,
            "status": installation.status.value,
            "installed_version": installation.installed_version,
            "installed_by": installation.installed_by,
            "installed_at": installation.installed_at.isoformat(),
            "configuration": installation.configuration,
            "health_status": installation.health_status,
            "module_info": {
                "name": loaded_module.module_name,
                "version": loaded_module.module_version,
                "full_name": loaded_module.full_name,
                "initialized": loaded_module.is_initialized
            },
            "installation_log": installation.installation_log
        }
        
        logger.info(f"Successfully installed module {loaded_module.full_name} for company {installation.company_id}")
        return response_data
        
    except InstallationError as e:
        logger.error(f"Installation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Installation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected installation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Installation failed: {str(e)}"
        )


@router.delete("/{installation_id}/uninstall", status_code=status.HTTP_200_OK)
async def uninstall_module_with_framework(
    installation_id: int,
    force: bool = Query(False, description="Force uninstall even with active dependencies"),
    background_tasks: BackgroundTasks,
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """
    Uninstall a module with proper cleanup
    
    This endpoint provides:
    - Dependency validation
    - Plugin framework cleanup
    - Endpoint unregistration
    - Comprehensive error handling
    """
    try:
        # Note: force parameter is prepared for future use but not currently implemented
        if force:
            logger.warning(f"Force uninstall requested for installation {installation_id}")
        
        success = await service.uninstall_module(installation_id)
        
        if success:
            return {
                "installation_id": installation_id,
                "status": "uninstalled",
                "message": "Module uninstalled successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Uninstallation failed for unknown reason"
            )
            
    except UninstallationError as e:
        logger.error(f"Uninstallation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected uninstallation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Uninstallation failed: {str(e)}"
        )


@router.post("/{installation_id}/reload", response_model=Dict[str, Any])
async def reload_module(
    installation_id: int,
    background_tasks: BackgroundTasks,
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """
    Reload a module (hot restart)
    
    This endpoint provides:
    - Safe module unloading
    - Fresh module loading
    - Configuration preservation
    - Health verification
    """
    try:
        installation, loaded_module = await service.reload_module(installation_id)
        
        return {
            "installation_id": installation_id,
            "status": "reloaded",
            "module_info": {
                "name": loaded_module.module_name,
                "version": loaded_module.module_version,
                "initialized": loaded_module.is_initialized
            },
            "health_status": installation.health_status,
            "reload_timestamp": installation.installation_log.get("reloaded"),
            "message": "Module reloaded successfully"
        }
        
    except InstallationError as e:
        logger.error(f"Module reload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected reload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reload failed: {str(e)}"
        )


@router.put("/{installation_id}/configuration", response_model=Dict[str, Any])
async def update_module_configuration(
    installation_id: int,
    configuration: Dict[str, Any],
    hot_reload: bool = Query(True, description="Apply configuration changes immediately"),
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """
    Update module configuration with optional hot reload
    
    This endpoint provides:
    - Configuration validation against module schema
    - Hot configuration reloading
    - Rollback on failure
    - Change tracking
    """
    try:
        installation = await service.update_module_configuration(
            installation_id, 
            configuration, 
            hot_reload=hot_reload
        )
        
        return {
            "installation_id": installation_id,
            "configuration": installation.configuration,
            "hot_reload": hot_reload,
            "hot_reload_status": "success" if "config_hot_reloaded" in installation.installation_log else "skipped",
            "updated_at": installation.installation_log.get("config_updated"),
            "message": "Configuration updated successfully"
        }
        
    except InstallationError as e:
        logger.error(f"Configuration update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected configuration update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration update failed: {str(e)}"
        )


@router.post("/{installation_id}/health-check", response_model=HealthCheckResult)
async def perform_comprehensive_health_check(
    installation_id: int,
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """
    Perform comprehensive health check on installation
    
    This endpoint provides:
    - Installation status validation
    - Plugin framework health check
    - Endpoint availability check
    - Dependency health validation
    - Performance metrics
    """
    try:
        health_result = await service.perform_health_check(installation_id)
        return health_result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/{installation_id}/status", response_model=Dict[str, Any])
async def get_installation_detailed_status(
    installation_id: int,
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """Get detailed installation status including framework information"""
    try:
        installation = await service.get_installation(installation_id)
        if not installation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation not found"
            )
        
        # Get additional framework status
        from app.framework.loader import plugin_loader
        from app.framework.registry import get_endpoint_manager
        
        module_loaded = plugin_loader.is_module_loaded(installation.module_id)
        loaded_module = plugin_loader.get_loaded_module(installation.module_id) if module_loaded else None
        
        endpoint_manager_instance = get_endpoint_manager()
        registered_endpoints = endpoint_manager_instance.get_module_endpoints(installation.module_id)
        
        return {
            "id": installation.id,
            "module_id": installation.module_id,
            "company_id": installation.company_id,
            "status": installation.status.value,
            "health_status": installation.health_status,
            "installed_version": installation.installed_version,
            "installed_by": installation.installed_by,
            "installed_at": installation.installed_at.isoformat(),
            "last_health_check": installation.last_health_check.isoformat() if installation.last_health_check else None,
            "error_message": installation.error_message,
            "configuration": installation.configuration,
            "installation_log": installation.installation_log,
            "framework_status": {
                "module_loaded": module_loaded,
                "module_initialized": loaded_module.is_initialized if loaded_module else False,
                "endpoints_registered": len(registered_endpoints),
                "module_full_name": loaded_module.full_name if loaded_module else None
            },
            "module_info": {
                "name": installation.module.name,
                "version": installation.module.version,
                "display_name": installation.module.display_name
            } if installation.module else None
        }
        
    except Exception as e:
        logger.error(f"Error getting installation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get installation status"
        )


@router.get("/company/{company_id}/active", response_model=List[Dict[str, Any]])
async def get_active_company_installations(
    company_id: int,
    include_framework_status: bool = Query(True, description="Include framework status information"),
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """Get all active installations for a company with framework status"""
    try:
        installations, _ = await service.list_installations(
            company_id=company_id,
            status=InstallationStatus.INSTALLED,
            limit=1000  # Get all active installations
        )
        
        result = []
        for installation in installations:
            installation_data = {
                "id": installation.id,
                "module_id": installation.module_id,
                "status": installation.status.value,
                "health_status": installation.health_status,
                "installed_version": installation.installed_version,
                "installed_at": installation.installed_at.isoformat(),
                "module_name": installation.module.name if installation.module else None,
                "module_display_name": installation.module.display_name if installation.module else None
            }
            
            if include_framework_status:
                from app.framework.loader import plugin_loader
                module_loaded = plugin_loader.is_module_loaded(installation.module_id)
                loaded_module = plugin_loader.get_loaded_module(installation.module_id) if module_loaded else None
                
                installation_data["framework_status"] = {
                    "module_loaded": module_loaded,
                    "module_initialized": loaded_module.is_initialized if loaded_module else False
                }
            
            result.append(installation_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting company installations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get company installations"
        )


@router.get("/framework/status", response_model=Dict[str, Any])
async def get_framework_status():
    """Get overall plugin framework status"""
    try:
        from app.framework.loader import plugin_loader
        from app.framework.registry import get_endpoint_manager
        from app.framework.events import event_bus
        
        # Get framework statistics
        loaded_modules = len(plugin_loader.loaded_modules)
        
        endpoint_manager_instance = get_endpoint_manager()
        all_endpoints = endpoint_manager_instance.get_all_endpoints()
        total_endpoints = sum(len(endpoints) for endpoints in all_endpoints.values())
        
        return {
            "framework_status": "operational",
            "loaded_modules": loaded_modules,
            "registered_endpoints": total_endpoints,
            "event_bus_running": event_bus.running,
            "modules_by_id": list(plugin_loader.loaded_modules.keys()),
            "endpoints_by_module": {
                str(module_id): len(endpoints) 
                for module_id, endpoints in all_endpoints.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting framework status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get framework status"
        )


@router.post("/bulk-health-check", response_model=List[Dict[str, Any]])
async def perform_bulk_health_check(
    company_id: Optional[int] = Query(None, description="Check all installations for specific company"),
    module_id: Optional[int] = Query(None, description="Check all installations for specific module"),
    service: EnhancedInstallationService = Depends(get_enhanced_installation_service)
):
    """Perform health checks on multiple installations"""
    try:
        installations, _ = await service.list_installations(
            company_id=company_id,
            module_id=module_id,
            status=InstallationStatus.INSTALLED,
            limit=1000
        )
        
        results = []
        for installation in installations:
            try:
                health_result = await service.perform_health_check(installation.id)
                results.append({
                    "installation_id": installation.id,
                    "module_name": installation.module.name if installation.module else None,
                    "company_id": installation.company_id,
                    "health_status": health_result.status,
                    "response_time_ms": health_result.response_time_ms,
                    "error_count": len(health_result.errors)
                })
            except Exception as e:
                results.append({
                    "installation_id": installation.id,
                    "module_name": installation.module.name if installation.module else None,
                    "company_id": installation.company_id,
                    "health_status": "error",
                    "response_time_ms": 0,
                    "error_count": 1,
                    "error": str(e)
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Bulk health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk health check failed"
        )


# Add datetime import
from datetime import datetime