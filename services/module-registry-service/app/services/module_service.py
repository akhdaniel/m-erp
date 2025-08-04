"""
Module service for CRUD operations
"""
import hashlib
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.models.module import Module, ModuleStatus, ModuleType
from app.models.dependency import ModuleDependency, DependencyType
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleStatusUpdate


class ModuleService:
    """Service for module management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_module(self, module_data: ModuleCreate, package_data: Optional[bytes] = None) -> Module:
        """Create a new module"""
        # Calculate package hash if package provided
        package_hash = None
        package_size = None
        if package_data:
            package_hash = hashlib.sha256(package_data).hexdigest()
            package_size = len(package_data)
        
        # Create module
        module = Module(
            name=module_data.name,
            display_name=module_data.display_name,
            description=module_data.description,
            version=module_data.version,
            author=module_data.author,
            author_email=module_data.author_email,
            license=module_data.license,
            homepage_url=module_data.homepage_url,
            documentation_url=module_data.documentation_url,
            repository_url=module_data.repository_url,
            module_type=module_data.module_type,
            minimum_framework_version=module_data.minimum_framework_version,
            python_version=module_data.python_version,
            manifest=module_data.manifest,
            config_schema=module_data.config_schema,
            default_config=module_data.default_config,
            is_public=module_data.is_public,
            requires_approval=module_data.requires_approval,
            package_data=package_data,
            package_size=package_size,
            package_hash=package_hash,
            status=ModuleStatus.REGISTERED
        )
        
        self.db.add(module)
        await self.db.flush()  # Get ID
        
        # Create dependencies from manifest
        if "dependencies" in module_data.manifest:
            for dep in module_data.manifest["dependencies"]:
                dependency = ModuleDependency(
                    module_id=module.id,
                    dependency_type=DependencyType(dep.get("type", "module")),
                    dependency_name=dep["name"],
                    version_constraint=dep.get("version"),
                    is_optional=dep.get("optional", False),
                    description=dep.get("description")
                )
                self.db.add(dependency)
        
        await self.db.commit()
        await self.db.refresh(module)
        return module
    
    async def get_module(self, module_id: int) -> Optional[Module]:
        """Get module by ID"""
        result = await self.db.execute(
            select(Module)
            .options(
                selectinload(Module.dependencies),
                selectinload(Module.installations)
            )
            .where(Module.id == module_id)
        )
        return result.scalar_one_or_none()
    
    async def get_module_by_name_version(self, name: str, version: str) -> Optional[Module]:
        """Get module by name and version"""
        result = await self.db.execute(
            select(Module)
            .options(
                selectinload(Module.dependencies),
                selectinload(Module.installations)
            )
            .where(and_(Module.name == name, Module.version == version))
        )
        return result.scalar_one_or_none()
    
    async def list_modules(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ModuleStatus] = None,
        module_type: Optional[ModuleType] = None,
        search: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> tuple[List[Module], int]:
        """List modules with filtering and pagination"""
        query = select(Module).options(
            selectinload(Module.dependencies),
            selectinload(Module.installations)
        )
        
        # Apply filters
        if status:
            query = query.where(Module.status == status)
        
        if module_type:
            query = query.where(Module.module_type == module_type)
        
        if is_public is not None:
            query = query.where(Module.is_public == is_public)
        
        if search:
            search_filter = or_(
                Module.name.ilike(f"%{search}%"),
                Module.display_name.ilike(f"%{search}%"),
                Module.description.ilike(f"%{search}%"),
                Module.author.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(Module)
        if status:
            count_query = count_query.where(Module.status == status)
        if module_type:
            count_query = count_query.where(Module.module_type == module_type)
        if is_public is not None:
            count_query = count_query.where(Module.is_public == is_public)
        if search:
            count_query = count_query.where(search_filter)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Module.created_at.desc())
        
        result = await self.db.execute(query)
        modules = result.scalars().all()
        
        return list(modules), total
    
    async def update_module(self, module_id: int, module_data: ModuleUpdate) -> Optional[Module]:
        """Update module"""
        module = await self.get_module(module_id)
        if not module:
            return None
        
        # Update fields
        update_data = module_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(module, field, value)
        
        await self.db.commit()
        await self.db.refresh(module)
        return module
    
    async def update_module_status(self, module_id: int, status_data: ModuleStatusUpdate) -> Optional[Module]:
        """Update module status"""
        module = await self.get_module(module_id)
        if not module:
            return None
        
        module.status = status_data.status
        if status_data.validation_errors:
            module.validation_errors = status_data.validation_errors
        
        await self.db.commit()
        await self.db.refresh(module)
        return module
    
    async def delete_module(self, module_id: int) -> bool:
        """Delete module (soft delete by setting is_active=False)"""
        module = await self.get_module(module_id)
        if not module:
            return False
        
        # Check if module has active installations
        if module.is_installed:
            raise ValueError("Cannot delete module with active installations")
        
        module.is_active = False
        await self.db.commit()
        return True
    
    async def get_module_dependencies(self, module_id: int) -> List[ModuleDependency]:
        """Get module dependencies"""
        result = await self.db.execute(
            select(ModuleDependency)
            .where(ModuleDependency.module_id == module_id)
            .order_by(ModuleDependency.dependency_name)
        )
        return list(result.scalars().all())
    
    async def get_module_dependents(self, module_id: int) -> List[ModuleDependency]:
        """Get modules that depend on this module"""
        result = await self.db.execute(
            select(ModuleDependency)
            .where(ModuleDependency.dependency_id == module_id)
            .order_by(ModuleDependency.module_id)
        )
        return list(result.scalars().all())
    
    async def validate_module_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module manifest"""
        errors = {}
        
        # Required fields
        required_fields = ["name", "version", "description", "author"]
        for field in required_fields:
            if field not in manifest:
                errors[field] = f"Required field '{field}' is missing"
        
        # Validate entry points
        if "entry_points" in manifest:
            entry_points = manifest["entry_points"]
            if not isinstance(entry_points, dict):
                errors["entry_points"] = "Entry points must be a dictionary"
        
        # Validate endpoints
        if "endpoints" in manifest:
            endpoints = manifest["endpoints"]
            if not isinstance(endpoints, list):
                errors["endpoints"] = "Endpoints must be a list"
            else:
                for i, endpoint in enumerate(endpoints):
                    if not isinstance(endpoint, dict):
                        errors[f"endpoints[{i}]"] = "Endpoint must be a dictionary"
                    elif "path" not in endpoint or "method" not in endpoint:
                        errors[f"endpoints[{i}]"] = "Endpoint must have 'path' and 'method' fields"
        
        # Validate dependencies
        if "dependencies" in manifest:
            dependencies = manifest["dependencies"]
            if not isinstance(dependencies, list):
                errors["dependencies"] = "Dependencies must be a list"
            else:
                for i, dep in enumerate(dependencies):
                    if not isinstance(dep, dict) or "name" not in dep:
                        errors[f"dependencies[{i}]"] = "Dependency must be a dictionary with 'name' field"
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    async def search_modules(self, query: str, limit: int = 10) -> List[Module]:
        """Search modules by name, description, or author"""
        search_filter = or_(
            Module.name.ilike(f"%{query}%"),
            Module.display_name.ilike(f"%{query}%"),
            Module.description.ilike(f"%{query}%"),
            Module.author.ilike(f"%{query}%")
        )
        
        result = await self.db.execute(
            select(Module)
            .where(and_(Module.is_active == True, search_filter))
            .order_by(Module.name)
            .limit(limit)
        )
        
        return list(result.scalars().all())