"""
Installation service for module installation operations
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models.installation import ModuleInstallation, InstallationStatus
from app.models.module import Module
from app.schemas.installation import InstallationCreate, InstallationUpdate, InstallationStatusUpdate, HealthCheckResult


class InstallationService:
    """Service for module installation management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_installation(self, installation_data: InstallationCreate, installed_by: str) -> ModuleInstallation:
        """Create a new module installation"""
        # Verify module exists and is approved
        module = await self.db.get(Module, installation_data.module_id)
        if not module:
            raise ValueError("Module not found")
        
        if module.status != "approved" and module.requires_approval:
            raise ValueError("Module must be approved before installation")
        
        # Check if module is already installed for this company
        existing = await self.get_installation_by_module_company(
            installation_data.module_id, 
            installation_data.company_id
        )
        if existing and existing.status != InstallationStatus.UNINSTALLED:
            raise ValueError("Module is already installed for this company")
        
        # Create installation
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
        await self.db.commit()
        await self.db.refresh(installation)
        return installation
    
    async def get_installation(self, installation_id: int) -> Optional[ModuleInstallation]:
        """Get installation by ID"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .options(selectinload(ModuleInstallation.module))
            .where(ModuleInstallation.id == installation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_installation_by_module_company(self, module_id: int, company_id: Optional[int]) -> Optional[ModuleInstallation]:
        """Get installation by module and company"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .options(selectinload(ModuleInstallation.module))
            .where(and_(
                ModuleInstallation.module_id == module_id,
                ModuleInstallation.company_id == company_id
            ))
            .order_by(ModuleInstallation.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def list_installations(
        self,
        company_id: Optional[int] = None,
        module_id: Optional[int] = None,
        status: Optional[InstallationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ModuleInstallation], int]:
        """List installations with filtering and pagination"""
        query = select(ModuleInstallation).options(
            selectinload(ModuleInstallation.module)
        )
        
        # Apply filters
        if company_id is not None:
            query = query.where(ModuleInstallation.company_id == company_id)
        
        if module_id:
            query = query.where(ModuleInstallation.module_id == module_id)
        
        if status:
            query = query.where(ModuleInstallation.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(ModuleInstallation)
        if company_id is not None:
            count_query = count_query.where(ModuleInstallation.company_id == company_id)
        if module_id:
            count_query = count_query.where(ModuleInstallation.module_id == module_id)
        if status:
            count_query = count_query.where(ModuleInstallation.status == status)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(ModuleInstallation.created_at.desc())
        
        result = await self.db.execute(query)
        installations = result.scalars().all()
        
        return list(installations), total
    
    async def update_installation(self, installation_id: int, installation_data: InstallationUpdate) -> Optional[ModuleInstallation]:
        """Update installation"""
        installation = await self.get_installation(installation_id)
        if not installation:
            return None
        
        # Update fields
        update_data = installation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(installation, field, value)
        
        await self.db.commit()
        await self.db.refresh(installation)
        return installation
    
    async def update_installation_status(self, installation_id: int, status_data: InstallationStatusUpdate) -> Optional[ModuleInstallation]:
        """Update installation status"""
        installation = await self.get_installation(installation_id)
        if not installation:
            return None
        
        old_status = installation.status
        installation.status = status_data.status
        
        # Update timestamps based on status
        if status_data.status == InstallationStatus.INSTALLED and old_status != InstallationStatus.INSTALLED:
            installation.installed_at = datetime.utcnow()
        elif status_data.status == InstallationStatus.UNINSTALLED:
            installation.uninstalled_at = datetime.utcnow()
            installation.is_active = False
        
        # Update error message and log
        if status_data.error_message:
            installation.error_message = status_data.error_message
        
        if status_data.installation_log:
            # Merge with existing log
            existing_log = installation.installation_log or {}
            existing_log.update(status_data.installation_log)
            installation.installation_log = existing_log
        
        await self.db.commit()
        await self.db.refresh(installation)
        return installation
    
    async def uninstall_module(self, installation_id: int) -> bool:
        """Uninstall module"""
        installation = await self.get_installation(installation_id)
        if not installation:
            return False
        
        if installation.status == InstallationStatus.UNINSTALLED:
            return True
        
        # Set status to uninstalling
        installation.status = InstallationStatus.UNINSTALLING
        await self.db.commit()
        
        # TODO: Implement actual uninstallation logic here
        # For now, just mark as uninstalled
        installation.status = InstallationStatus.UNINSTALLED
        installation.uninstalled_at = datetime.utcnow()
        installation.is_active = False
        
        await self.db.commit()
        return True
    
    async def perform_health_check(self, installation_id: int) -> HealthCheckResult:
        """Perform health check on installation"""
        installation = await self.get_installation(installation_id)
        if not installation:
            raise ValueError("Installation not found")
        
        # TODO: Implement actual health check logic
        # For now, simple status-based check
        if installation.status == InstallationStatus.INSTALLED and installation.is_enabled:
            status = "healthy"
            details = {"message": "Installation is active and enabled"}
        elif installation.status == InstallationStatus.FAILED:
            status = "unhealthy"
            details = {"message": "Installation failed", "error": installation.error_message}
        else:
            status = "unknown"
            details = {"message": f"Installation status: {installation.status}"}
        
        # Update installation health
        installation.last_health_check = datetime.utcnow()
        installation.health_status = status
        installation.health_details = details
        
        await self.db.commit()
        
        return HealthCheckResult(
            status=status,
            details=details,
            last_check=installation.last_health_check
        )
    
    async def get_company_installations(self, company_id: Optional[int]) -> List[ModuleInstallation]:
        """Get all installations for a company"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .options(selectinload(ModuleInstallation.module))
            .where(and_(
                ModuleInstallation.company_id == company_id,
                ModuleInstallation.is_active == True,
                ModuleInstallation.status == InstallationStatus.INSTALLED
            ))
            .order_by(ModuleInstallation.module_id)
        )
        return list(result.scalars().all())
    
    async def get_module_installations(self, module_id: int) -> List[ModuleInstallation]:
        """Get all installations for a module"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .where(ModuleInstallation.module_id == module_id)
            .order_by(ModuleInstallation.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def installation_exists(self, module_id: int, company_id: Optional[int]) -> bool:
        """Check if installation exists for module and company"""
        result = await self.db.execute(
            select(func.count())
            .select_from(ModuleInstallation)
            .where(and_(
                ModuleInstallation.module_id == module_id,
                ModuleInstallation.company_id == company_id,
                ModuleInstallation.status.in_([
                    InstallationStatus.INSTALLED,
                    InstallationStatus.INSTALLING,
                    InstallationStatus.PENDING
                ])
            ))
        )
        count = result.scalar()
        return count > 0