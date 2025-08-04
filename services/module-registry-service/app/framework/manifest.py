"""
Module manifest schema and validation for the plugin/extension framework
"""
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
import re


class ModuleType(str, Enum):
    """Types of modules supported by the framework"""
    BUSINESS_OBJECT = "business_object"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    REPORT = "report"
    UI_COMPONENT = "ui_component"
    FULL_MODULE = "full_module"


class DependencyType(str, Enum):
    """Types of dependencies a module can have"""
    MODULE = "module"
    SERVICE = "service"
    PYTHON_PACKAGE = "python_package"
    SYSTEM = "system"


class EndpointMethod(str, Enum):
    """HTTP methods supported for module endpoints"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class EventType(str, Enum):
    """Types of events modules can handle"""
    MODULE_LIFECYCLE = "module_lifecycle"
    BUSINESS_OBJECT = "business_object"
    WORKFLOW = "workflow"
    USER_ACTION = "user_action"
    SYSTEM = "system"


class ModuleDependency(BaseModel):
    """Module dependency specification"""
    name: str = Field(..., description="Dependency name")
    version: Optional[str] = Field(None, description="Version constraint (e.g., '>=1.0.0,<2.0.0')")
    type: DependencyType = Field(default=DependencyType.MODULE, description="Dependency type")
    optional: bool = Field(default=False, description="Whether dependency is optional")
    description: Optional[str] = Field(None, description="Purpose of this dependency")
    
    @validator('version')
    def validate_version_constraint(cls, v):
        if v is None:
            return v
        # Basic version constraint validation
        version_pattern = r'^[>=<~!]*\d+\.\d+\.\d+([>=<,\s]*\d+\.\d+\.\d+)*$'
        if not re.match(version_pattern, v.replace(' ', '')):
            raise ValueError('Invalid version constraint format')
        return v


class ModuleEndpoint(BaseModel):
    """Module API endpoint specification"""
    path: str = Field(..., description="Endpoint path (relative to module base)")
    method: EndpointMethod = Field(..., description="HTTP method")
    handler: str = Field(..., description="Handler function reference (module.function)")
    description: Optional[str] = Field(None, description="Endpoint description")
    tags: Optional[List[str]] = Field(default=[], description="OpenAPI tags")
    requires_auth: bool = Field(default=True, description="Whether endpoint requires authentication")
    company_scoped: bool = Field(default=True, description="Whether endpoint is company-scoped")
    permissions: Optional[List[str]] = Field(default=[], description="Required permissions")
    
    @validator('path')
    def validate_path(cls, v):
        if not v.startswith('/'):
            raise ValueError('Endpoint path must start with /')
        if not re.match(r'^/[a-zA-Z0-9/_-]*$', v):
            raise ValueError('Invalid endpoint path format')
        return v
    
    @validator('handler')
    def validate_handler(cls, v):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*:[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError('Handler must be in format "module.path:function_name"')
        return v


class ModuleEventHandler(BaseModel):
    """Module event handler specification"""
    event_type: EventType = Field(..., description="Type of event to handle")
    event_pattern: str = Field(..., description="Event pattern to match (regex)")
    handler: str = Field(..., description="Handler function reference")
    description: Optional[str] = Field(None, description="Handler description")
    priority: int = Field(default=100, description="Handler priority (lower = higher priority)")
    
    @validator('event_pattern')
    def validate_event_pattern(cls, v):
        try:
            re.compile(v)
        except re.error:
            raise ValueError('Invalid regex pattern for event matching')
        return v


class ModuleConfiguration(BaseModel):
    """Module configuration schema specification"""
    schema: Dict[str, Any] = Field(..., description="JSON schema for configuration")
    default_values: Optional[Dict[str, Any]] = Field(default={}, description="Default configuration values")
    required_fields: Optional[List[str]] = Field(default=[], description="Required configuration fields")
    
    @validator('schema')
    def validate_json_schema(cls, v):
        # Basic JSON schema validation
        if not isinstance(v, dict):
            raise ValueError('Configuration schema must be a dictionary')
        if 'type' not in v:
            raise ValueError('Configuration schema must have a type field')
        return v


class ModuleEntryPoint(BaseModel):
    """Module entry point specification"""
    name: str = Field(..., description="Entry point name")
    module_path: str = Field(..., description="Python module path")
    function: str = Field(..., description="Function name")
    description: Optional[str] = Field(None, description="Entry point description")
    
    @validator('module_path')
    def validate_module_path(cls, v):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', v):
            raise ValueError('Invalid module path format')
        return v
    
    @validator('function')
    def validate_function_name(cls, v):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError('Invalid function name format')
        return v


class ModulePermission(BaseModel):
    """Module permission specification"""
    name: str = Field(..., description="Permission name")
    description: str = Field(..., description="Permission description")
    category: Optional[str] = Field(None, description="Permission category")
    default_granted: bool = Field(default=False, description="Whether granted by default")


class ModuleManifest(BaseModel):
    """Complete module manifest specification"""
    
    # Basic module information
    name: str = Field(..., description="Module name (kebab-case)")
    version: str = Field(..., description="Module version (semantic versioning)")
    description: str = Field(..., description="Module description")
    author: str = Field(..., description="Module author")
    author_email: Optional[str] = Field(None, description="Author email")
    license: Optional[str] = Field(None, description="Module license")
    homepage: Optional[str] = Field(None, description="Module homepage URL")
    repository: Optional[str] = Field(None, description="Repository URL")
    
    # Module classification
    module_type: ModuleType = Field(default=ModuleType.FULL_MODULE, description="Module type")
    keywords: Optional[List[str]] = Field(default=[], description="Module keywords for search")
    
    # Framework requirements
    minimum_framework_version: str = Field(default="1.0.0", description="Minimum framework version")
    python_version: str = Field(default=">=3.12", description="Python version requirement")
    
    # Module components
    dependencies: Optional[List[ModuleDependency]] = Field(default=[], description="Module dependencies")
    entry_points: Optional[List[ModuleEntryPoint]] = Field(default=[], description="Module entry points")
    endpoints: Optional[List[ModuleEndpoint]] = Field(default=[], description="Module API endpoints")
    event_handlers: Optional[List[ModuleEventHandler]] = Field(default=[], description="Event handlers")
    permissions: Optional[List[ModulePermission]] = Field(default=[], description="Module permissions")
    
    # Configuration
    configuration: Optional[ModuleConfiguration] = Field(None, description="Module configuration schema")
    
    # Module metadata
    supports_multi_company: bool = Field(default=True, description="Whether module supports multi-company")
    requires_database: bool = Field(default=False, description="Whether module requires database access")
    requires_redis: bool = Field(default=False, description="Whether module requires Redis")
    requires_external_services: Optional[List[str]] = Field(default=[], description="External services required")
    
    # Security and deployment
    sandbox_enabled: bool = Field(default=True, description="Whether module runs in sandbox")
    resource_limits: Optional[Dict[str, Any]] = Field(default={}, description="Resource limits for module")
    environment_variables: Optional[List[str]] = Field(default=[], description="Required environment variables")
    
    # Validation
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', v):
            raise ValueError('Module name must be lowercase kebab-case')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Module name must be between 3 and 50 characters')
        return v
    
    @validator('version')
    def validate_version(cls, v):
        # Semantic versioning validation
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$', v):
            raise ValueError('Version must follow semantic versioning (e.g., 1.0.0)')
        return v
    
    @validator('author_email')
    def validate_email(cls, v):
        if v and not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('minimum_framework_version')
    def validate_framework_version(cls, v):
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('Framework version must be in format X.Y.Z')
        return v
    
    @root_validator
    def validate_module_consistency(cls, values):
        """Validate consistency across module components"""
        module_type = values.get('module_type')
        endpoints = values.get('endpoints', [])
        entry_points = values.get('entry_points', [])
        
        # Business object modules should have specific patterns
        if module_type == ModuleType.BUSINESS_OBJECT:
            if not any(ep.name == 'main' for ep in entry_points):
                raise ValueError('Business object modules must have a "main" entry point')
        
        # UI component modules should have specific endpoints
        if module_type == ModuleType.UI_COMPONENT:
            if not any(ep.path.startswith('/ui/') for ep in endpoints):
                raise ValueError('UI component modules should have UI endpoints')
        
        # Workflow modules should have event handlers
        if module_type == ModuleType.WORKFLOW:
            event_handlers = values.get('event_handlers', [])
            if not event_handlers:
                raise ValueError('Workflow modules should have event handlers')
        
        return values
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary"""
        return self.dict(exclude_none=True)
    
    def validate_dependencies(self, available_modules: List[str]) -> List[str]:
        """Validate that all required dependencies are available"""
        missing_deps = []
        
        for dep in self.dependencies or []:
            if dep.type == DependencyType.MODULE and not dep.optional:
                if dep.name not in available_modules:
                    missing_deps.append(dep.name)
        
        return missing_deps
    
    def get_required_permissions(self) -> List[str]:
        """Get all permissions required by this module"""
        permissions = []
        
        # Add permissions from endpoints
        for endpoint in self.endpoints or []:
            permissions.extend(endpoint.permissions or [])
        
        # Add module-defined permissions
        for perm in self.permissions or []:
            permissions.append(perm.name)
        
        return list(set(permissions))


class ManifestValidator:
    """Utility class for module manifest validation"""
    
    @staticmethod
    def validate_manifest_dict(manifest_dict: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a manifest dictionary and return validation results"""
        try:
            ModuleManifest(**manifest_dict)
            return True, []
        except Exception as e:
            return False, [str(e)]
    
    @staticmethod
    def validate_manifest_yaml(manifest_yaml: str) -> tuple[bool, List[str], Optional[ModuleManifest]]:
        """Validate a YAML manifest string"""
        try:
            import yaml
            manifest_dict = yaml.safe_load(manifest_yaml)
            manifest = ModuleManifest(**manifest_dict)
            return True, [], manifest
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"], None
        except Exception as e:
            return False, [str(e)], None
    
    @staticmethod
    def check_security_requirements(manifest: ModuleManifest) -> List[str]:
        """Check security requirements and return warnings"""
        warnings = []
        
        # Check for potentially dangerous permissions
        dangerous_perms = ['admin', 'root', 'system', 'database_admin']
        for perm in manifest.permissions or []:
            if any(danger in perm.name.lower() for danger in dangerous_perms):
                warnings.append(f"Potentially dangerous permission: {perm.name}")
        
        # Check for external service requirements
        if manifest.requires_external_services:
            warnings.append("Module requires external services - review network access")
        
        # Check for sandbox bypass
        if not manifest.sandbox_enabled:
            warnings.append("Module disables sandbox - requires security review")
        
        return warnings