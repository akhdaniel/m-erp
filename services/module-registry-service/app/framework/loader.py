"""
Plugin loader for dynamic module import and initialization
"""
import asyncio
import importlib
import importlib.util
import sys
import os
import tempfile
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager
import logging
from app.framework.manifest import ModuleManifest, ManifestValidator
from app.models.module import Module
from app.models.installation import ModuleInstallation, InstallationStatus

logger = logging.getLogger(__name__)


class ModuleLoadError(Exception):
    """Exception raised when module loading fails"""
    pass


class ModuleValidationError(Exception):
    """Exception raised when module validation fails"""
    pass


class LoadedModule:
    """Represents a loaded module instance"""
    
    def __init__(
        self,
        module_id: int,
        module_name: str,
        module_version: str,
        manifest: ModuleManifest,
        python_module: Any,
        installation: ModuleInstallation
    ):
        self.module_id = module_id
        self.module_name = module_name
        self.module_version = module_version
        self.manifest = manifest
        self.python_module = python_module
        self.installation = installation
        self.is_initialized = False
        self.entry_points: Dict[str, Callable] = {}
        self.endpoints: List[Dict[str, Any]] = []
        self.event_handlers: Dict[str, Callable] = {}
        
    @property
    def full_name(self) -> str:
        """Get full module name with version"""
        return f"{self.module_name}@{self.module_version}"
    
    def __repr__(self):
        return f"<LoadedModule(id={self.module_id}, name='{self.full_name}', initialized={self.is_initialized})>"


class PluginLoader:
    """Plugin loader for dynamic module loading and lifecycle management"""
    
    def __init__(self, storage_path: str = "/tmp/modules"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True, parents=True)
        self.loaded_modules: Dict[int, LoadedModule] = {}
        self.module_paths: Dict[str, Path] = {}
        
    async def extract_module_package(self, module: Module) -> Path:
        """Extract module package to temporary directory"""
        if not module.package_data:
            raise ModuleLoadError(f"Module {module.name} has no package data")
        
        # Create module-specific directory
        module_dir = self.storage_path / f"{module.name}-{module.version}"
        if module_dir.exists():
            shutil.rmtree(module_dir)
        module_dir.mkdir(exist_ok=True)
        
        # Create temporary file for package data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
            tmp_file.write(module.package_data)
            tmp_file_path = tmp_file.name
        
        try:
            # Try to extract as tar.gz first
            try:
                with tarfile.open(tmp_file_path, 'r:gz') as tar:
                    tar.extractall(module_dir)
            except tarfile.TarError:
                # Try as zip file
                try:
                    with zipfile.ZipFile(tmp_file_path, 'r') as zip_file:
                        zip_file.extractall(module_dir)
                except zipfile.BadZipFile:
                    raise ModuleLoadError(f"Unsupported package format for module {module.name}")
            
            logger.info(f"Extracted module {module.name} to {module_dir}")
            return module_dir
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    def validate_module_structure(self, module_dir: Path, manifest: ModuleManifest) -> bool:
        """Validate that module directory has required structure"""
        # Check for __init__.py or main module file
        init_file = module_dir / "__init__.py"
        main_files = list(module_dir.glob("*.py"))
        
        if not init_file.exists() and not main_files:
            raise ModuleValidationError("Module must contain __init__.py or Python files")
        
        # Validate entry points exist
        for entry_point in manifest.entry_points or []:
            module_path_parts = entry_point.module_path.split('.')
            expected_file = module_dir
            for part in module_path_parts:
                expected_file = expected_file / part
            
            # Check both .py file and package directory
            py_file = expected_file.with_suffix('.py')
            package_dir = expected_file / "__init__.py"
            
            if not py_file.exists() and not package_dir.exists():
                raise ModuleValidationError(
                    f"Entry point module {entry_point.module_path} not found"
                )
        
        return True
    
    async def load_module_python(self, module_dir: Path, manifest: ModuleManifest) -> Any:
        """Load Python module dynamically"""
        module_name = manifest.name.replace('-', '_')
        
        # Add module directory to Python path temporarily
        str_module_dir = str(module_dir)
        if str_module_dir not in sys.path:
            sys.path.insert(0, str_module_dir)
        
        try:
            # Try to import the module
            if (module_dir / "__init__.py").exists():
                # Import as package
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    module_dir / "__init__.py"
                )
            else:
                # Look for main Python file
                main_files = list(module_dir.glob("*.py"))
                if not main_files:
                    raise ModuleLoadError(f"No Python files found in module {manifest.name}")
                
                main_file = main_files[0]  # Use first Python file
                spec = importlib.util.spec_from_file_location(module_name, main_file)
            
            if spec is None or spec.loader is None:
                raise ModuleLoadError(f"Could not create module spec for {manifest.name}")
            
            # Load the module
            python_module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules to support relative imports
            sys.modules[module_name] = python_module
            
            # Execute the module
            spec.loader.exec_module(python_module)
            
            logger.info(f"Successfully loaded Python module {module_name}")
            return python_module
            
        except Exception as e:
            # Clean up sys.modules on error
            if module_name in sys.modules:
                del sys.modules[module_name]
            raise ModuleLoadError(f"Failed to load Python module {manifest.name}: {e}")
        
        finally:
            # Remove from path
            if str_module_dir in sys.path:
                sys.path.remove(str_module_dir)
    
    def resolve_entry_points(self, python_module: Any, manifest: ModuleManifest) -> Dict[str, Callable]:
        """Resolve module entry points to callable functions"""
        entry_points = {}
        
        for entry_point in manifest.entry_points or []:
            try:
                # Navigate to the function
                parts = entry_point.module_path.split('.')
                current = python_module
                
                for part in parts:
                    current = getattr(current, part)
                
                function = getattr(current, entry_point.function)
                
                if not callable(function):
                    raise ModuleLoadError(f"Entry point {entry_point.name} is not callable")
                
                entry_points[entry_point.name] = function
                logger.debug(f"Resolved entry point {entry_point.name}")
                
            except AttributeError as e:
                raise ModuleLoadError(
                    f"Could not resolve entry point {entry_point.name}: {e}"
                )
        
        return entry_points
    
    def resolve_event_handlers(self, python_module: Any, manifest: ModuleManifest) -> Dict[str, Callable]:
        """Resolve module event handlers to callable functions"""
        event_handlers = {}
        
        for handler in manifest.event_handlers or []:
            try:
                # Parse handler reference (module.path:function)
                module_path, function_name = handler.handler.split(':')
                
                # Navigate to the function
                parts = module_path.split('.')
                current = python_module
                
                for part in parts:
                    current = getattr(current, part)
                
                function = getattr(current, function_name)
                
                if not callable(function):
                    raise ModuleLoadError(f"Event handler {handler.handler} is not callable")
                
                event_handlers[handler.event_pattern] = function
                logger.debug(f"Resolved event handler for {handler.event_pattern}")
                
            except (AttributeError, ValueError) as e:
                raise ModuleLoadError(
                    f"Could not resolve event handler {handler.handler}: {e}"
                )
        
        return event_handlers
    
    async def initialize_module(self, loaded_module: LoadedModule) -> bool:
        """Initialize a loaded module"""
        try:
            # Call main entry point if it exists
            if 'main' in loaded_module.entry_points:
                main_func = loaded_module.entry_points['main']
                
                # Check if it's async
                if asyncio.iscoroutinefunction(main_func):
                    await main_func(loaded_module.installation.configuration or {})
                else:
                    main_func(loaded_module.installation.configuration or {})
            
            # Call initialization hook if it exists
            if 'initialize' in loaded_module.entry_points:
                init_func = loaded_module.entry_points['initialize']
                
                if asyncio.iscoroutinefunction(init_func):
                    await init_func(loaded_module.installation.configuration or {})
                else:
                    init_func(loaded_module.installation.configuration or {})
            
            loaded_module.is_initialized = True
            logger.info(f"Successfully initialized module {loaded_module.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize module {loaded_module.full_name}: {e}")
            raise ModuleLoadError(f"Module initialization failed: {e}")
    
    async def load_module(self, module: Module, installation: ModuleInstallation) -> LoadedModule:
        """Load a module from the database"""
        try:
            # Validate manifest
            manifest = ModuleManifest(**module.manifest)
            
            # Extract package if available
            if module.package_data:
                module_dir = await self.extract_module_package(module)
                self.validate_module_structure(module_dir, manifest)
                python_module = await self.load_module_python(module_dir, manifest)
                self.module_paths[module.name] = module_dir
            else:
                # Module without package (configuration only)
                python_module = None
            
            # Create loaded module instance
            loaded_module = LoadedModule(
                module_id=module.id,
                module_name=module.name,
                module_version=module.version,
                manifest=manifest,
                python_module=python_module,
                installation=installation
            )
            
            # Resolve entry points and handlers if Python module exists
            if python_module:
                loaded_module.entry_points = self.resolve_entry_points(python_module, manifest)
                loaded_module.event_handlers = self.resolve_event_handlers(python_module, manifest)
            
            # Store in loaded modules
            self.loaded_modules[module.id] = loaded_module
            
            logger.info(f"Successfully loaded module {loaded_module.full_name}")
            return loaded_module
            
        except Exception as e:
            logger.error(f"Failed to load module {module.name}: {e}")
            raise ModuleLoadError(f"Could not load module {module.name}: {e}")
    
    async def unload_module(self, module_id: int) -> bool:
        """Unload a module"""
        if module_id not in self.loaded_modules:
            return False
        
        loaded_module = self.loaded_modules[module_id]
        
        try:
            # Call cleanup entry point if it exists
            if 'cleanup' in loaded_module.entry_points:
                cleanup_func = loaded_module.entry_points['cleanup']
                
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
            
            # Remove from Python modules if needed
            module_name = loaded_module.module_name.replace('-', '_')
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Clean up extracted files
            if loaded_module.module_name in self.module_paths:
                module_dir = self.module_paths[loaded_module.module_name]
                if module_dir.exists():
                    shutil.rmtree(module_dir)
                del self.module_paths[loaded_module.module_name]
            
            # Remove from loaded modules
            del self.loaded_modules[module_id]
            
            logger.info(f"Successfully unloaded module {loaded_module.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading module {loaded_module.full_name}: {e}")
            return False
    
    async def reload_module(self, module_id: int, new_module: Module, new_installation: ModuleInstallation) -> LoadedModule:
        """Reload a module with new version/configuration"""
        # Unload existing module
        await self.unload_module(module_id)
        
        # Load new version
        return await self.load_module(new_module, new_installation)
    
    def get_loaded_module(self, module_id: int) -> Optional[LoadedModule]:
        """Get a loaded module by ID"""
        return self.loaded_modules.get(module_id)
    
    def get_loaded_modules(self) -> List[LoadedModule]:
        """Get all loaded modules"""
        return list(self.loaded_modules.values())
    
    def is_module_loaded(self, module_id: int) -> bool:
        """Check if a module is loaded"""
        return module_id in self.loaded_modules
    
    async def health_check_module(self, module_id: int) -> Dict[str, Any]:
        """Perform health check on a loaded module"""
        if module_id not in self.loaded_modules:
            return {"status": "not_loaded", "details": "Module is not loaded"}
        
        loaded_module = self.loaded_modules[module_id]
        
        try:
            # Call health check entry point if it exists
            if 'health_check' in loaded_module.entry_points:
                health_func = loaded_module.entry_points['health_check']
                
                if asyncio.iscoroutinefunction(health_func):
                    result = await health_func()
                else:
                    result = health_func()
                
                return result if isinstance(result, dict) else {"status": "healthy", "details": result}
            
            # Default health check
            return {
                "status": "healthy",
                "initialized": loaded_module.is_initialized,
                "entry_points": len(loaded_module.entry_points),
                "event_handlers": len(loaded_module.event_handlers)
            }
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def shutdown(self):
        """Shutdown the plugin loader and unload all modules"""
        logger.info("Shutting down plugin loader...")
        
        # Unload all modules
        module_ids = list(self.loaded_modules.keys())
        for module_id in module_ids:
            await self.unload_module(module_id)
        
        # Clean up storage directory
        if self.storage_path.exists():
            try:
                shutil.rmtree(self.storage_path)
            except Exception as e:
                logger.warning(f"Could not clean up storage directory: {e}")
        
        logger.info("Plugin loader shutdown complete")


# Global plugin loader instance
plugin_loader = PluginLoader()