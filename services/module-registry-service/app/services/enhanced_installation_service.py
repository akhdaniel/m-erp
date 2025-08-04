"""
Enhanced installation service with plugin framework integration
"""
import asyncio
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models.installation import ModuleInstallation, InstallationStatus
from app.models.module import Module, ModuleStatus
from app.schemas.installation import (
    InstallationCreate, InstallationUpdate, InstallationStatusUpdate, HealthCheckResult
)
from app.framework.loader import plugin_loader, LoadedModule, ModuleLoadError
from app.framework.events import event_manager, ModuleLifecycleEvent
from app.framework.registry import endpoint_manager, get_endpoint_manager
from app.framework.validator import DependencyValidator
from app.services.dependency_resolution_service import DependencyResolutionService
import logging

logger = logging.getLogger(__name__)


class InstallationError(Exception):
    """Error during module installation"""
    pass


class UninstallationError(Exception):
    """Error during module uninstallation"""
    pass


class EnhancedInstallationService:
    """Enhanced installation service with plugin framework integration"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dependency_validator = DependencyValidator()
        self.dependency_resolver = DependencyResolutionService(db)
    
    async def install_module(
        self, 
        installation_data: InstallationCreate, 
        installed_by: str
    ) -> Tuple[ModuleInstallation, LoadedModule]:
        """Install a module with full plugin loading and validation"""
        try:
            logger.info(f"Starting installation of module {installation_data.module_id} for company {installation_data.company_id}")
            
            # Step 1: Validate module and create installation record
            installation = await self._create_installation_record(installation_data, installed_by)
            
            try:
                # Step 2: Analyze dependencies and create resolution plan
                resolution_plan = await self.dependency_resolver.analyze_module_dependencies(
                    installation.module_id, 
                    installation.company_id
                )
                
                if not resolution_plan.is_resolvable:
                    critical_conflicts = [c for c in resolution_plan.conflicts if c.severity == "critical"]
                    error_messages = [c.description for c in critical_conflicts]
                    raise InstallationError(f"Dependency conflicts prevent installation: {'; '.join(error_messages)}")
                
                # Step 3: Load dependencies first
                await self._ensure_dependencies_loaded(installation)
                
                # Step 4: Load the module using plugin framework
                loaded_module = await self._load_module_with_framework(installation)
                
                # Step 5: Register module endpoints
                await self._register_module_endpoints(loaded_module)
                
                # Step 6: Initialize module
                await self._initialize_loaded_module(loaded_module)
                
                # Step 7: Update installation status to installed
                installation.status = InstallationStatus.INSTALLED
                installation.installation_log["loaded"] = datetime.utcnow().isoformat()
                installation.health_status = "healthy"
                
                await self.db.commit()
                
                # Step 8: Publish lifecycle events
                await event_manager.publish_module_lifecycle_event(
                    event_type=ModuleLifecycleEvent.MODULE_LOADED,
                    loaded_module=loaded_module,
                    correlation_id=f"install_{installation.id}"
                )
                
                logger.info(f"Successfully installed module {loaded_module.full_name} for company {installation.company_id}")
                return installation, loaded_module
                
            except Exception as e:
                # Rollback installation on any failure
                logger.error(f"Installation failed, rolling back: {e}")
                await self._rollback_installation(installation, str(e))
                raise InstallationError(f"Installation failed: {e}")
                
        except Exception as e:
            logger.error(f"Failed to install module: {e}")
            raise
    
    async def uninstall_module(self, installation_id: int) -> bool:
        """Uninstall a module with proper cleanup"""
        try:
            logger.info(f"Starting uninstallation of installation {installation_id}")
            
            # Step 1: Get installation
            installation = await self.get_installation(installation_id)
            if not installation:
                raise UninstallationError("Installation not found")
            
            if installation.status == InstallationStatus.UNINSTALLED:
                logger.info(f"Installation {installation_id} already uninstalled")
                return True
            
            # Step 2: Check for dependent modules using dependency resolver
            dependent_installations = await self.dependency_resolver._get_dependent_modules(
                installation.module_id, installation.company_id
            )
            if dependent_installations:
                dependent_names = [dep.module.name for dep in dependent_installations]
                raise UninstallationError(
                    f"Cannot uninstall module with active dependencies: {', '.join(dependent_names)}"
                )
            
            # Step 3: Update status to uninstalling
            installation.status = InstallationStatus.UNINSTALLING
            installation.installation_log["uninstall_started"] = datetime.utcnow().isoformat()
            await self.db.commit()
            
            try:
                # Step 4: Unload module from plugin framework
                await self._unload_module_from_framework(installation)
                
                # Step 5: Unregister endpoints
                await self._unregister_module_endpoints(installation)
                
                # Step 6: Update status to uninstalled
                installation.status = InstallationStatus.UNINSTALLED
                installation.installation_log["uninstalled"] = datetime.utcnow().isoformat()
                installation.health_status = "unloaded"
                
                await self.db.commit()
                
                # Step 7: Publish lifecycle event
                await event_manager.publish_module_lifecycle_event(
                    event_type=ModuleLifecycleEvent.MODULE_UNLOADED,
                    loaded_module=None,  # Module is no longer loaded
                    correlation_id=f"uninstall_{installation.id}"
                )
                
                logger.info(f"Successfully uninstalled module for installation {installation_id}")
                return True
                
            except Exception as e:
                # Mark as error state but don't rollback DB changes
                installation.status = InstallationStatus.ERROR
                installation.error_message = str(e)
                installation.installation_log["uninstall_error"] = datetime.utcnow().isoformat()
                await self.db.commit()
                
                logger.error(f"Uninstallation failed for installation {installation_id}: {e}")
                raise UninstallationError(f"Uninstallation failed: {e}")
                
        except Exception as e:
            logger.error(f"Failed to uninstall module: {e}")
            raise
    
    async def reload_module(self, installation_id: int) -> Tuple[ModuleInstallation, LoadedModule]:
        """Reload a module (unload and reinstall)"""
        try:
            logger.info(f"Reloading module for installation {installation_id}")
            
            installation = await self.get_installation(installation_id)
            if not installation:
                raise InstallationError("Installation not found")
            
            # Step 1: Unload current module
            await self._unload_module_from_framework(installation)
            await self._unregister_module_endpoints(installation)
            
            # Step 2: Reload module
            loaded_module = await self._load_module_with_framework(installation)
            await self._register_module_endpoints(loaded_module)
            await self._initialize_loaded_module(loaded_module)
            
            # Step 3: Update installation
            installation.installation_log["reloaded"] = datetime.utcnow().isoformat()
            installation.health_status = "healthy"
            await self.db.commit()
            
            # Step 4: Publish reload event
            await event_manager.publish_module_lifecycle_event(
                event_type=ModuleLifecycleEvent.MODULE_STARTED,
                loaded_module=loaded_module,
                correlation_id=f"reload_{installation.id}"
            )
            
            logger.info(f"Successfully reloaded module for installation {installation_id}")
            return installation, loaded_module
            
        except Exception as e:
            logger.error(f"Failed to reload module: {e}")
            raise InstallationError(f"Reload failed: {e}")
    
    async def update_module_configuration(
        self, 
        installation_id: int, 
        configuration: Dict[str, Any],
        hot_reload: bool = True
    ) -> ModuleInstallation:
        """Update module configuration with optional hot reload"""
        try:
            installation = await self.get_installation(installation_id)
            if not installation:
                raise InstallationError("Installation not found")
            
            # Validate configuration against module schema
            await self._validate_configuration(installation, configuration)
            
            # Update configuration
            old_config = installation.configuration.copy()
            installation.configuration = configuration
            installation.installation_log["config_updated"] = datetime.utcnow().isoformat()
            
            if hot_reload and installation.status == InstallationStatus.INSTALLED:
                # Hot reload with new configuration
                try:
                    await self._hot_reload_configuration(installation, old_config)
                    installation.installation_log["config_hot_reloaded"] = datetime.utcnow().isoformat()
                except Exception as e:
                    logger.warning(f"Hot reload failed, will require manual reload: {e}")
                    installation.installation_log["config_hot_reload_failed"] = str(e)
            
            await self.db.commit()
            
            logger.info(f"Updated configuration for installation {installation_id}")
            return installation
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise
    
    async def perform_health_check(self, installation_id: int) -> HealthCheckResult:
        """Perform comprehensive health check on installation"""
        try:
            installation = await self.get_installation(installation_id)
            if not installation:
                raise ValueError("Installation not found")
            
            health_result = HealthCheckResult(
                installation_id=installation_id,
                status="unknown",
                checks={},
                last_check=datetime.utcnow(),
                response_time_ms=0,
                errors=[]
            )
            
            start_time = datetime.utcnow()
            
            try:
                # Check 1: Installation status
                health_result.checks["installation_active"] = installation.status == InstallationStatus.INSTALLED
                
                # Check 2: Module loaded in framework
                module_loaded = plugin_loader.is_module_loaded(installation.module_id)
                health_result.checks["module_loaded"] = module_loaded
                
                if module_loaded:
                    # Check 3: Module health check
                    module_health = await plugin_loader.health_check_module(installation.module_id)
                    health_result.checks["module_health"] = module_health.get("status") == "healthy"
                    
                    # Check 4: Endpoints responding (if module has endpoints)
                    endpoint_manager_instance = get_endpoint_manager()
                    endpoints = endpoint_manager_instance.get_module_endpoints(installation.module_id)
                    health_result.checks["endpoints_registered"] = len(endpoints) > 0
                    
                    # Check 5: Dependencies available
                    dependencies_ok = await self._check_dependencies_health(installation)
                    health_result.checks["dependencies_available"] = dependencies_ok
                    
                else:
                    health_result.checks["module_health"] = False
                    health_result.checks["endpoints_registered"] = False
                    health_result.checks["dependencies_available"] = False
                    health_result.errors.append("Module not loaded in framework")
                
                # Determine overall status
                all_critical_checks = [
                    health_result.checks["installation_active"],
                    health_result.checks["module_loaded"],
                    health_result.checks["dependencies_available"]
                ]
                
                if all(all_critical_checks):
                    health_result.status = "healthy"
                elif health_result.checks["installation_active"]:
                    health_result.status = "degraded"
                else:
                    health_result.status = "unhealthy"
                
            except Exception as e:
                health_result.status = "error"
                health_result.errors.append(f"Health check failed: {str(e)}")
            
            # Calculate response time
            end_time = datetime.utcnow()
            health_result.response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update installation health status
            installation.health_status = health_result.status
            installation.last_health_check = health_result.last_check
            await self.db.commit()
            
            return health_result
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    # Private helper methods
    
    async def _create_installation_record(
        self, 
        installation_data: InstallationCreate, 
        installed_by: str
    ) -> ModuleInstallation:
        """Create installation database record with validation"""
        # Verify module exists and is approved
        module = await self.db.get(Module, installation_data.module_id)
        if not module:
            raise ValueError("Module not found")
        
        if module.status not in [ModuleStatus.APPROVED, ModuleStatus.PUBLISHED]:
            raise ValueError("Module must be approved before installation")
        
        # Check if module is already installed for this company
        existing = await self._get_installation_by_module_company(
            installation_data.module_id, 
            installation_data.company_id
        )
        if existing and existing.status not in [InstallationStatus.UNINSTALLED, InstallationStatus.ERROR]:
            raise ValueError("Module is already installed for this company")
        
        # Create installation record
        installation = ModuleInstallation(
            module_id=installation_data.module_id,
            company_id=installation_data.company_id,
            installed_version=module.version,
            installed_by=installed_by,
            configuration=installation_data.configuration or {},
            status=InstallationStatus.PENDING,
            installation_log={"created": datetime.utcnow().isoformat()}
        )
        
        self.db.add(installation)
        await self.db.flush()  # Get ID
        return installation
    
    async def _ensure_dependencies_loaded(self, installation: ModuleInstallation) -> None:
        """Ensure all module dependencies are loaded"""
        module = await self.db.get(Module, installation.module_id)
        
        if "dependencies" in module.manifest:
            for dep in module.manifest["dependencies"]:
                if dep.get("type") == "module" and not dep.get("optional", False):
                    # Check if dependency is installed for this company
                    dep_installation = await self._get_installation_by_module_name_company(
                        dep["name"], installation.company_id
                    )
                    
                    if not dep_installation or dep_installation.status != InstallationStatus.INSTALLED:
                        raise InstallationError(
                            f"Required dependency '{dep['name']}' is not installed for this company"
                        )
    
    async def _load_module_with_framework(self, installation: ModuleInstallation) -> LoadedModule:
        """Load module using the plugin framework"""
        module = await self.db.get(Module, installation.module_id)
        
        try:
            loaded_module = await plugin_loader.load_module(module, installation)
            
            installation.installation_log["framework_loaded"] = datetime.utcnow().isoformat()
            return loaded_module
            
        except ModuleLoadError as e:
            raise InstallationError(f"Failed to load module with framework: {e}")
    
    async def _register_module_endpoints(self, loaded_module: LoadedModule) -> None:
        """Register module endpoints with API gateway"""
        try:
            endpoint_manager_instance = get_endpoint_manager()
            success = await endpoint_manager_instance.on_module_loaded(loaded_module)
            
            if not success:
                raise InstallationError("Failed to register module endpoints")
                
        except Exception as e:
            raise InstallationError(f"Endpoint registration failed: {e}")
    
    async def _initialize_loaded_module(self, loaded_module: LoadedModule) -> None:
        """Initialize the loaded module"""
        try:
            success = await plugin_loader.initialize_module(loaded_module)
            if not success:
                raise InstallationError("Module initialization failed")
                
        except Exception as e:
            raise InstallationError(f"Module initialization failed: {e}")
    
    async def _unload_module_from_framework(self, installation: ModuleInstallation) -> None:
        """Unload module from plugin framework"""
        try:
            await plugin_loader.unload_module(installation.module_id)
            installation.installation_log["framework_unloaded"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.warning(f"Failed to unload module from framework: {e}")
            # Don't raise exception, log warning and continue
    
    async def _unregister_module_endpoints(self, installation: ModuleInstallation) -> None:
        """Unregister module endpoints"""
        try:
            endpoint_manager_instance = get_endpoint_manager()
            await endpoint_manager_instance.on_module_unloaded(installation.module_id)
            
        except Exception as e:
            logger.warning(f"Failed to unregister endpoints: {e}")
    
    async def _rollback_installation(self, installation: ModuleInstallation, error_message: str) -> None:
        """Rollback failed installation"""
        try:
            installation.status = InstallationStatus.ERROR
            installation.error_message = error_message
            installation.installation_log["rollback"] = datetime.utcnow().isoformat()
            
            # Try to cleanup any partially loaded resources
            try:
                await self._unload_module_from_framework(installation)
                await self._unregister_module_endpoints(installation)
            except Exception as cleanup_error:
                logger.warning(f"Cleanup during rollback failed: {cleanup_error}")
            
            await self.db.commit()
            
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {rollback_error}")
    
    async def _get_dependent_installations(self, installation: ModuleInstallation) -> List[ModuleInstallation]:
        """Get installations that depend on this module"""
        module = await self.db.get(Module, installation.module_id)
        
        # Find modules that depend on this one
        result = await self.db.execute(
            select(ModuleInstallation)
            .join(Module)
            .where(
                and_(
                    ModuleInstallation.company_id == installation.company_id,
                    ModuleInstallation.status == InstallationStatus.INSTALLED,
                    # This is simplified - would need proper JSON query for dependencies
                    Module.manifest.contains({"dependencies": [{"name": module.name}]})
                )
            )
        )
        return list(result.scalars().all())
    
    async def _validate_configuration(self, installation: ModuleInstallation, configuration: Dict[str, Any]) -> None:
        """Validate configuration against module schema"""
        module = await self.db.get(Module, installation.module_id)
        
        if module.config_schema:
            # TODO: Implement JSON schema validation
            # For now, just check that required fields are present
            if "required" in module.config_schema:
                for required_field in module.config_schema["required"]:
                    if required_field not in configuration:
                        raise ValueError(f"Required configuration field missing: {required_field}")
    
    async def _hot_reload_configuration(self, installation: ModuleInstallation, old_config: Dict[str, Any]) -> None:
        """Hot reload module with new configuration"""
        # This would trigger module-specific configuration update
        # For now, just log the change
        logger.info(f"Hot reloading configuration for installation {installation.id}")
        
        # In a full implementation, this would:
        # 1. Call module's configuration update handler
        # 2. Restart specific module components
        # 3. Validate that the module still works with new config
    
    async def _check_dependencies_health(self, installation: ModuleInstallation) -> bool:
        """Check health of module dependencies"""
        module = await self.db.get(Module, installation.module_id)
        
        if "dependencies" in module.manifest:
            for dep in module.manifest["dependencies"]:
                if dep.get("type") == "module" and not dep.get("optional", False):
                    dep_installation = await self._get_installation_by_module_name_company(
                        dep["name"], installation.company_id
                    )
                    
                    if not dep_installation or dep_installation.status != InstallationStatus.INSTALLED:
                        return False
                    
                    # Check if dependency module is loaded
                    if not plugin_loader.is_module_loaded(dep_installation.module_id):
                        return False
        
        return True
    
    async def _get_installation_by_module_company(self, module_id: int, company_id: int) -> Optional[ModuleInstallation]:
        """Get installation by module and company"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .where(
                and_(
                    ModuleInstallation.module_id == module_id,
                    ModuleInstallation.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_installation_by_module_name_company(self, module_name: str, company_id: int) -> Optional[ModuleInstallation]:
        """Get installation by module name and company"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .join(Module)
            .where(
                and_(
                    Module.name == module_name,
                    ModuleInstallation.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    # Inherit basic CRUD methods from original service
    async def get_installation(self, installation_id: int) -> Optional[ModuleInstallation]:
        """Get installation by ID"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .options(
                selectinload(ModuleInstallation.module)
            )
            .where(ModuleInstallation.id == installation_id)
        )
        return result.scalar_one_or_none()
    
    async def list_installations(
        self,
        company_id: Optional[int] = None,
        module_id: Optional[int] = None,
        status: Optional[InstallationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ModuleInstallation], int]:
        """List installations with filtering"""
        query = select(ModuleInstallation).options(
            selectinload(ModuleInstallation.module)
        )
        
        # Apply filters
        conditions = []
        if company_id:
            conditions.append(ModuleInstallation.company_id == company_id)
        if module_id:
            conditions.append(ModuleInstallation.module_id == module_id)
        if status:
            conditions.append(ModuleInstallation.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(ModuleInstallation)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(ModuleInstallation.installed_at.desc())
        
        result = await self.db.execute(query)
        installations = list(result.scalars().all())
        
        return installations, total