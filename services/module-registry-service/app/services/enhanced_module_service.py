"""
Enhanced module service with framework integration for registration, validation, and package management
"""
import asyncio
import hashlib
import json
import tempfile
import tarfile
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.models.module import Module, ModuleStatus, ModuleType
from app.models.dependency import ModuleDependency, DependencyType
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleStatusUpdate
from app.framework.validator import ModuleValidator, ModuleValidationResult
from app.framework.manifest import ModuleManifest, ManifestValidator
from app.framework.events import event_manager, ModuleLifecycleEvent
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ModuleRegistrationError(Exception):
    """Error during module registration"""
    pass


class PackageValidationError(Exception):
    """Error during package validation"""
    pass


class EnhancedModuleService:
    """Enhanced module service with framework integration"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.validator = ModuleValidator()
        self.storage_path = Path(settings.module_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def register_module_with_validation(
        self, 
        module_data: ModuleCreate, 
        package_data: Optional[bytes] = None
    ) -> Tuple[Module, ModuleValidationResult]:
        """Register a new module with comprehensive validation"""
        try:
            # Step 1: Validate manifest
            logger.info(f"Starting registration for module {module_data.name}@{module_data.version}")
            
            manifest = ModuleManifest(**module_data.manifest)
            
            # Step 2: Extract and validate package if provided
            module_directory = None
            if package_data:
                module_directory = await self._extract_and_validate_package(
                    package_data, module_data.name, module_data.version
                )
            
            # Step 3: Get available modules for dependency checking
            available_modules = await self._get_available_module_names()
            
            # Step 4: Comprehensive validation
            validation_result = await self.validator.validate_module(
                Module(
                    name=module_data.name,
                    version=module_data.version,
                    manifest=module_data.manifest
                ),
                module_directory,
                available_modules
            )
            
            # Step 5: Handle validation results
            if not validation_result.is_valid:
                raise ModuleRegistrationError(
                    f"Module validation failed: {', '.join(validation_result.errors)}"
                )
            
            # Step 6: Check for existing module
            existing = await self.get_module_by_name_version(module_data.name, module_data.version)
            if existing:
                raise ModuleRegistrationError(
                    f"Module {module_data.name}@{module_data.version} already exists"
                )
            
            # Step 7: Store package if provided
            stored_package_data = None
            if package_data:
                stored_package_data = await self._store_package(
                    package_data, module_data.name, module_data.version
                )
            
            # Step 8: Create module
            module = await self._create_module_record(
                module_data, stored_package_data, validation_result
            )
            
            # Step 9: Publish lifecycle event
            await event_manager.publish_module_lifecycle_event(
                event_type=ModuleLifecycleEvent.MODULE_LOADING,
                loaded_module=None,  # Will be set when module is actually loaded
                correlation_id=f"registration_{module.id}"
            )
            
            logger.info(f"Successfully registered module {module.name}@{module.version} with ID {module.id}")
            return module, validation_result
            
        except Exception as e:
            logger.error(f"Failed to register module {module_data.name}@{module_data.version}: {e}")
            # Cleanup on failure
            if 'module_directory' in locals() and module_directory:
                await self._cleanup_extracted_package(module_directory)
            raise
        finally:
            # Cleanup temporary extraction directory
            if 'module_directory' in locals() and module_directory:
                await self._cleanup_extracted_package(module_directory)
    
    async def _extract_and_validate_package(
        self, 
        package_data: bytes, 
        module_name: str, 
        version: str
    ) -> Path:
        """Extract and validate package structure"""
        try:
            # Create temporary directory for extraction
            temp_dir = Path(tempfile.mkdtemp(prefix=f"module_{module_name}_{version}_"))
            
            # Determine package type and extract
            if self._is_tar_package(package_data):
                await self._extract_tar_package(package_data, temp_dir)
            elif self._is_zip_package(package_data):
                await self._extract_zip_package(package_data, temp_dir)
            else:
                raise PackageValidationError("Unsupported package format. Use .tar.gz or .zip")
            
            # Validate extracted structure
            await self._validate_package_structure(temp_dir, module_name)
            
            return temp_dir
            
        except Exception as e:
            if 'temp_dir' in locals():
                await self._cleanup_extracted_package(temp_dir)
            raise PackageValidationError(f"Package extraction failed: {e}")
    
    def _is_tar_package(self, package_data: bytes) -> bool:
        """Check if package is a tar archive"""
        return package_data[:2] == b'\x1f\x8b' or package_data[:3] == b'BZh'
    
    def _is_zip_package(self, package_data: bytes) -> bool:
        """Check if package is a zip archive"""
        return package_data[:4] == b'PK\x03\x04'
    
    async def _extract_tar_package(self, package_data: bytes, extract_to: Path):
        """Extract tar.gz package"""
        def _extract():
            with tarfile.open(fileobj=io.BytesIO(package_data), mode='r:*') as tar:
                # Security check: prevent path traversal
                for member in tar.getmembers():
                    if member.name.startswith('/') or '..' in member.name:
                        raise PackageValidationError(f"Unsafe path in package: {member.name}")
                
                tar.extractall(path=extract_to)
        
        # Run extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _extract)
    
    async def _extract_zip_package(self, package_data: bytes, extract_to: Path):
        """Extract zip package"""
        def _extract():
            with zipfile.ZipFile(io.BytesIO(package_data), 'r') as zip_file:
                # Security check: prevent path traversal
                for member in zip_file.namelist():
                    if member.startswith('/') or '..' in member:
                        raise PackageValidationError(f"Unsafe path in package: {member}")
                
                zip_file.extractall(path=extract_to)
        
        # Run extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _extract)
    
    async def _validate_package_structure(self, package_dir: Path, module_name: str):
        """Validate package directory structure"""
        # Check if module directory exists (should match module name or be in subdirectory)
        possible_dirs = [
            package_dir / module_name,
            package_dir / module_name.replace('-', '_'),
            package_dir
        ]
        
        module_dir = None
        for possible_dir in possible_dirs:
            if possible_dir.exists() and possible_dir.is_dir():
                # Check for Python files
                python_files = list(possible_dir.glob('*.py'))
                if python_files or (possible_dir / '__init__.py').exists():
                    module_dir = possible_dir
                    break
        
        if not module_dir:
            raise PackageValidationError(
                f"Package must contain Python module directory named '{module_name}' or have Python files in root"
            )
        
        # Validate that required files exist
        init_file = module_dir / '__init__.py'
        if not init_file.exists():
            # Look for any Python files
            python_files = list(module_dir.glob('*.py'))
            if not python_files:
                raise PackageValidationError("Package must contain Python files")
    
    async def _store_package(self, package_data: bytes, module_name: str, version: str) -> bytes:
        """Store package data and return it (placeholder for future file storage)"""
        # For now, just return the package data
        # In production, this would store to S3 or filesystem
        
        # Calculate and verify hash
        package_hash = hashlib.sha256(package_data).hexdigest()
        package_size = len(package_data)
        
        logger.info(f"Storing package for {module_name}@{version}: {package_size} bytes, hash: {package_hash[:8]}...")
        
        # TODO: Implement actual storage (filesystem, S3, etc.)
        # For now, store in database
        return package_data
    
    async def _create_module_record(
        self, 
        module_data: ModuleCreate, 
        package_data: Optional[bytes],
        validation_result: ModuleValidationResult
    ) -> Module:
        """Create module database record"""
        # Calculate package metadata
        package_hash = None
        package_size = None
        if package_data:
            package_hash = hashlib.sha256(package_data).hexdigest()
            package_size = len(package_data)
        
        # Determine status based on validation
        status = ModuleStatus.REGISTERED
        if validation_result.security_issues:
            status = ModuleStatus.SECURITY_REVIEW
        elif module_data.requires_approval:
            status = ModuleStatus.PENDING_APPROVAL
        
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
            status=status,
            validation_summary={
                "security_issues_count": len(validation_result.security_issues),
                "dependency_errors_count": len(validation_result.dependency_errors),
                "validation_timestamp": validation_result.validation_timestamp.isoformat() if validation_result.validation_timestamp else None
            }
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
    
    async def _get_available_module_names(self) -> List[str]:
        """Get list of available module names for dependency validation"""
        result = await self.db.execute(
            select(Module.name).where(Module.status.in_([
                ModuleStatus.APPROVED,
                ModuleStatus.PUBLISHED
            ]))
        )
        return [row[0] for row in result.fetchall()]
    
    async def _cleanup_extracted_package(self, package_dir: Path):
        """Clean up extracted package directory"""
        import shutil
        try:
            if package_dir.exists():
                shutil.rmtree(package_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup package directory {package_dir}: {e}")
    
    async def validate_module_manifest(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module manifest"""
        try:
            is_valid, errors = ManifestValidator.validate_manifest_dict(manifest_data)
            
            if is_valid:
                manifest = ModuleManifest(**manifest_data)
                warnings = ManifestValidator.check_security_requirements(manifest)
                
                return {
                    "valid": True,
                    "errors": [],
                    "warnings": warnings
                }
            else:
                return {
                    "valid": False,
                    "errors": errors,
                    "warnings": []
                }
                
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    async def get_module_validation_details(self, module_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed validation information for a module"""
        module = await self.get_module(module_id)
        if not module:
            return None
        
        return {
            "module_id": module_id,
            "validation_summary": module.validation_summary,
            "status": module.status.value,
            "package_hash": module.package_hash,
            "package_size": module.package_size,
            "created_at": module.created_at.isoformat(),
            "dependencies": [
                {
                    "name": dep.dependency_name,
                    "type": dep.dependency_type.value,
                    "version_constraint": dep.version_constraint,
                    "is_optional": dep.is_optional
                }
                for dep in module.dependencies
            ]
        }
    
    # Inherit other methods from original ModuleService
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
    
    async def update_module_status(self, module_id: int, status_data: ModuleStatusUpdate) -> Optional[Module]:
        """Update module status"""
        module = await self.get_module(module_id)
        if not module:
            return None
        
        # Validate status transition
        valid_transitions = {
            ModuleStatus.REGISTERED: [ModuleStatus.PENDING_APPROVAL, ModuleStatus.SECURITY_REVIEW, ModuleStatus.REJECTED],
            ModuleStatus.SECURITY_REVIEW: [ModuleStatus.PENDING_APPROVAL, ModuleStatus.REJECTED],
            ModuleStatus.PENDING_APPROVAL: [ModuleStatus.APPROVED, ModuleStatus.REJECTED],
            ModuleStatus.APPROVED: [ModuleStatus.PUBLISHED, ModuleStatus.DEPRECATED],
            ModuleStatus.PUBLISHED: [ModuleStatus.DEPRECATED],
            ModuleStatus.DEPRECATED: [ModuleStatus.PUBLISHED]
        }
        
        new_status = ModuleStatus(status_data.status)
        if new_status not in valid_transitions.get(module.status, []):
            raise ValueError(f"Invalid status transition from {module.status.value} to {new_status.value}")
        
        module.status = new_status
        module.status_reason = status_data.reason
        
        await self.db.commit()
        await self.db.refresh(module)
        
        # Publish lifecycle event
        event_type = {
            ModuleStatus.APPROVED: ModuleLifecycleEvent.MODULE_STARTED,
            ModuleStatus.PUBLISHED: ModuleLifecycleEvent.MODULE_STARTED,
            ModuleStatus.REJECTED: ModuleLifecycleEvent.MODULE_ERROR,
            ModuleStatus.DEPRECATED: ModuleLifecycleEvent.MODULE_STOPPED
        }.get(new_status)
        
        if event_type:
            await event_manager.publish_module_lifecycle_event(
                event_type=event_type,
                loaded_module=None,  # Module not loaded yet
                correlation_id=f"status_update_{module.id}"
            )
        
        return module


# Import BytesIO for package extraction
import io