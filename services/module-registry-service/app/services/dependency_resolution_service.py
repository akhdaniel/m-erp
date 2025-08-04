"""
Enhanced dependency resolution and conflict detection service
"""
import asyncio
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.module import Module, ModuleStatus
from app.models.installation import ModuleInstallation, InstallationStatus
from app.framework.manifest import ModuleManifest
from app.framework.validator import DependencyValidator
import logging

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Types of dependency conflicts"""
    VERSION_MISMATCH = "version_mismatch"
    CIRCULAR_DEPENDENCY = "circular_dependency" 
    MISSING_DEPENDENCY = "missing_dependency"
    INCOMPATIBLE_DEPENDENCY = "incompatible_dependency"
    RESOURCE_CONFLICT = "resource_conflict"


@dataclass
class DependencyConflict:
    """Represents a dependency conflict"""
    conflict_type: ConflictType
    module_name: str
    conflicting_module: Optional[str]
    description: str
    severity: str  # "critical", "major", "minor"
    resolution_suggestions: List[str]


@dataclass
class DependencyNode:
    """Node in dependency graph"""
    name: str
    version: str
    module_id: int
    dependencies: List[str]
    optional_dependencies: List[str]
    conflicts_with: List[str]
    provides: List[str]


@dataclass
class ResolutionPlan:
    """Plan for resolving dependencies"""
    install_order: List[int]  # Module IDs in installation order
    conflicts: List[DependencyConflict]
    warnings: List[str]
    is_resolvable: bool


class DependencyResolutionService:
    """Service for resolving module dependencies and detecting conflicts"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dependency_validator = DependencyValidator()
    
    async def analyze_module_dependencies(
        self, 
        module_id: int, 
        company_id: int,
        target_modules: Optional[List[int]] = None
    ) -> ResolutionPlan:
        """
        Analyze dependencies for a module and create resolution plan
        
        Args:
            module_id: Module to analyze
            company_id: Company context for dependency resolution
            target_modules: Additional modules being considered for installation
        """
        logger.info(f"Analyzing dependencies for module {module_id} in company {company_id}")
        
        # Build dependency graph
        dependency_graph = await self._build_dependency_graph(company_id, target_modules or [])
        
        # Get target module
        target_module = await self.db.get(Module, module_id)
        if not target_module:
            return ResolutionPlan([], [DependencyConflict(
                ConflictType.MISSING_DEPENDENCY,
                "unknown",
                None,
                f"Module {module_id} not found",
                "critical",
                ["Verify module exists"]
            )], [], False)
        
        # Add target module to graph
        target_node = await self._create_dependency_node(target_module)
        dependency_graph[target_module.name] = target_node
        
        # Detect conflicts
        conflicts = await self._detect_conflicts(dependency_graph, target_module.name, company_id)
        
        # Generate installation order
        install_order = []
        warnings = []
        
        if not any(c.severity == "critical" for c in conflicts):
            try:
                install_order = await self._generate_install_order(
                    dependency_graph, target_module.name, company_id
                )
            except Exception as e:
                logger.error(f"Failed to generate install order: {e}")
                conflicts.append(DependencyConflict(
                    ConflictType.CIRCULAR_DEPENDENCY,
                    target_module.name,
                    None,
                    f"Could not resolve installation order: {e}",
                    "critical",
                    ["Review module dependencies for circular references"]
                ))
        
        return ResolutionPlan(
            install_order=install_order,
            conflicts=conflicts,
            warnings=warnings,
            is_resolvable=len([c for c in conflicts if c.severity == "critical"]) == 0
        )
    
    async def detect_installation_conflicts(
        self, 
        module_ids: List[int], 
        company_id: int
    ) -> List[DependencyConflict]:
        """Detect conflicts when installing multiple modules"""
        logger.info(f"Detecting conflicts for modules {module_ids} in company {company_id}")
        
        dependency_graph = await self._build_dependency_graph(company_id, module_ids)
        all_conflicts = []
        
        # Check each module for conflicts
        for module_id in module_ids:
            module = await self.db.get(Module, module_id)
            if module and module.name in dependency_graph:
                conflicts = await self._detect_conflicts(dependency_graph, module.name, company_id)
                all_conflicts.extend(conflicts)
        
        # Check for cross-module conflicts
        cross_conflicts = await self._detect_cross_module_conflicts(dependency_graph, module_ids)
        all_conflicts.extend(cross_conflicts)
        
        return all_conflicts
    
    async def suggest_dependency_resolution(
        self, 
        conflicts: List[DependencyConflict]
    ) -> Dict[str, List[str]]:
        """Suggest resolutions for dependency conflicts"""
        suggestions = {}
        
        for conflict in conflicts:
            module_suggestions = []
            
            if conflict.conflict_type == ConflictType.VERSION_MISMATCH:
                module_suggestions.extend([
                    "Update to compatible version",
                    "Use version pinning in manifest",
                    "Check for alternative modules"
                ])
            
            elif conflict.conflict_type == ConflictType.CIRCULAR_DEPENDENCY:
                module_suggestions.extend([
                    "Refactor module to remove circular dependency",
                    "Extract common functionality to separate module",
                    "Use event-driven communication instead of direct dependency"
                ])
            
            elif conflict.conflict_type == ConflictType.MISSING_DEPENDENCY:
                module_suggestions.extend([
                    "Install missing dependency first",
                    "Mark dependency as optional if not critical",
                    "Find alternative module providing same functionality"
                ])
            
            elif conflict.conflict_type == ConflictType.RESOURCE_CONFLICT:
                module_suggestions.extend([
                    "Configure modules to use different resources",
                    "Use shared resource management",
                    "Install modules in different environments"
                ])
            
            suggestions[conflict.module_name] = module_suggestions + conflict.resolution_suggestions
        
        return suggestions
    
    async def validate_upgrade_compatibility(
        self, 
        module_id: int, 
        new_version: str, 
        company_id: int
    ) -> List[DependencyConflict]:
        """Validate if module upgrade would cause conflicts"""
        logger.info(f"Validating upgrade compatibility for module {module_id} to version {new_version}")
        
        conflicts = []
        
        # Get current installation
        current_installation = await self._get_module_installation(module_id, company_id)
        if not current_installation:
            return [DependencyConflict(
                ConflictType.MISSING_DEPENDENCY,
                f"module_{module_id}",
                None,
                "Module not currently installed",
                "critical",
                ["Install module before upgrading"]
            )]
        
        # Get modules that depend on this one
        dependent_modules = await self._get_dependent_modules(module_id, company_id)
        
        # Check if upgrade would break dependent modules
        for dependent in dependent_modules:
            # TODO: Implement semantic version compatibility checking
            # For now, just warn about potential issues
            conflicts.append(DependencyConflict(
                ConflictType.VERSION_MISMATCH,
                dependent.module.name,
                current_installation.module.name,
                f"Module {dependent.module.name} depends on {current_installation.module.name}. Upgrade compatibility needs verification.",
                "minor",
                [
                    "Test dependent module with new version",
                    "Update dependent module if needed",
                    "Use version constraints in dependencies"
                ]
            ))
        
        return conflicts
    
    # Private helper methods
    
    async def _build_dependency_graph(
        self, 
        company_id: int, 
        additional_modules: List[int]
    ) -> Dict[str, DependencyNode]:
        """Build dependency graph for installed and target modules"""
        graph = {}
        
        # Get installed modules
        installed_modules = await self._get_installed_modules(company_id)
        
        # Get additional modules being considered
        if additional_modules:
            additional = await self._get_modules_by_ids(additional_modules)
            installed_modules.extend(additional)
        
        # Create nodes for each module
        for module in installed_modules:
            node = await self._create_dependency_node(module)
            graph[module.name] = node
        
        return graph
    
    async def _create_dependency_node(self, module: Module) -> DependencyNode:
        """Create dependency node from module"""
        manifest = ModuleManifest(**module.manifest)
        
        dependencies = []
        optional_dependencies = []
        conflicts_with = []
        provides = [module.name]
        
        for dep in manifest.dependencies or []:
            if dep.type == "module":
                if dep.optional:
                    optional_dependencies.append(dep.name)
                else:
                    dependencies.append(dep.name)
        
        # Extract conflicts and provides from manifest
        if "conflicts" in module.manifest:
            conflicts_with = module.manifest["conflicts"]
        
        if "provides" in module.manifest:
            provides.extend(module.manifest["provides"])
        
        return DependencyNode(
            name=module.name,
            version=module.version,
            module_id=module.id,
            dependencies=dependencies,
            optional_dependencies=optional_dependencies,
            conflicts_with=conflicts_with,
            provides=provides
        )
    
    async def _detect_conflicts(
        self, 
        dependency_graph: Dict[str, DependencyNode], 
        target_module: str,
        company_id: int
    ) -> List[DependencyConflict]:
        """Detect various types of conflicts"""
        conflicts = []
        
        if target_module not in dependency_graph:
            return conflicts
        
        node = dependency_graph[target_module]
        
        # Check for missing dependencies
        for dep_name in node.dependencies:
            if dep_name not in dependency_graph:
                conflicts.append(DependencyConflict(
                    ConflictType.MISSING_DEPENDENCY,
                    target_module,
                    dep_name,
                    f"Required dependency '{dep_name}' is not available",
                    "critical",
                    [f"Install module '{dep_name}' first"]
                ))
        
        # Check for conflicts with existing modules
        for module_name, existing_node in dependency_graph.items():
            if module_name == target_module:
                continue
                
            # Check if modules explicitly conflict
            if target_module in existing_node.conflicts_with or module_name in node.conflicts_with:
                conflicts.append(DependencyConflict(
                    ConflictType.INCOMPATIBLE_DEPENDENCY,
                    target_module,
                    module_name,
                    f"Module '{target_module}' conflicts with '{module_name}'",
                    "critical",
                    [f"Uninstall '{module_name}' before installing '{target_module}'"]
                ))
        
        # Check for circular dependencies
        if self._has_circular_dependency(dependency_graph, target_module, set()):
            conflicts.append(DependencyConflict(
                ConflictType.CIRCULAR_DEPENDENCY,
                target_module,
                None,
                f"Circular dependency detected involving '{target_module}'",
                "critical",
                ["Refactor modules to remove circular dependency"]
            ))
        
        return conflicts
    
    def _has_circular_dependency(
        self, 
        graph: Dict[str, DependencyNode], 
        node_name: str, 
        visited: Set[str]
    ) -> bool:
        """Check for circular dependencies using DFS"""
        if node_name in visited:
            return True
        
        if node_name not in graph:
            return False
        
        visited.add(node_name)
        
        for dep in graph[node_name].dependencies:
            if self._has_circular_dependency(graph, dep, visited.copy()):
                return True
        
        return False
    
    async def _detect_cross_module_conflicts(
        self, 
        dependency_graph: Dict[str, DependencyNode], 
        module_ids: List[int]
    ) -> List[DependencyConflict]:
        """Detect conflicts between multiple modules being installed"""
        conflicts = []
        
        # Get modules by ID
        modules = await self._get_modules_by_ids(module_ids)
        module_names = [m.name for m in modules if m.name in dependency_graph]
        
        # Check for resource conflicts (same API endpoints, etc.)
        for i, module_a in enumerate(module_names):
            for module_b in module_names[i+1:]:
                node_a = dependency_graph[module_a]
                node_b = dependency_graph[module_b]
                
                # Check if both provide same functionality
                common_provides = set(node_a.provides) & set(node_b.provides)
                if common_provides:
                    conflicts.append(DependencyConflict(
                        ConflictType.RESOURCE_CONFLICT,
                        module_a,
                        module_b,
                        f"Modules '{module_a}' and '{module_b}' both provide: {', '.join(common_provides)}",
                        "major",
                        [
                            "Choose one module over the other",
                            "Configure modules to avoid conflicts",
                            "Use different deployment environments"
                        ]
                    ))
        
        return conflicts
    
    async def _generate_install_order(
        self, 
        dependency_graph: Dict[str, DependencyNode], 
        target_module: str,
        company_id: int
    ) -> List[int]:
        """Generate optimal installation order using topological sort"""
        install_order = []
        visited = set()
        visiting = set()
        
        def visit(module_name: str):
            if module_name in visiting:
                raise ValueError(f"Circular dependency detected involving {module_name}")
            if module_name in visited:
                return
            
            if module_name not in dependency_graph:
                return
            
            visiting.add(module_name)
            node = dependency_graph[module_name]
            
            # Visit dependencies first
            for dep_name in node.dependencies:
                visit(dep_name)
            
            visiting.remove(module_name)
            visited.add(module_name)
            install_order.append(node.module_id)
        
        visit(target_module)
        return install_order
    
    async def _get_installed_modules(self, company_id: int) -> List[Module]:
        """Get modules installed for company"""
        result = await self.db.execute(
            select(Module)
            .join(ModuleInstallation)
            .where(
                and_(
                    ModuleInstallation.company_id == company_id,
                    ModuleInstallation.status == InstallationStatus.INSTALLED
                )
            )
        )
        return list(result.scalars().all())
    
    async def _get_modules_by_ids(self, module_ids: List[int]) -> List[Module]:
        """Get modules by IDs"""
        if not module_ids:
            return []
        
        result = await self.db.execute(
            select(Module).where(Module.id.in_(module_ids))
        )
        return list(result.scalars().all())
    
    async def _get_module_installation(
        self, 
        module_id: int, 
        company_id: int
    ) -> Optional[ModuleInstallation]:
        """Get module installation"""
        result = await self.db.execute(
            select(ModuleInstallation)
            .options(selectinload(ModuleInstallation.module))
            .where(
                and_(
                    ModuleInstallation.module_id == module_id,
                    ModuleInstallation.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def _get_dependent_modules(
        self, 
        module_id: int, 
        company_id: int
    ) -> List[ModuleInstallation]:
        """Get modules that depend on the given module"""
        # Get the module name
        module = await self.db.get(Module, module_id)
        if not module:
            return []
        
        # Find installations that have this module as dependency
        result = await self.db.execute(
            select(ModuleInstallation)
            .options(selectinload(ModuleInstallation.module))
            .join(Module)
            .where(
                and_(
                    ModuleInstallation.company_id == company_id,
                    ModuleInstallation.status == InstallationStatus.INSTALLED,
                    # This is a simplified check - would need proper JSON querying
                    Module.manifest.contains({"dependencies": [{"name": module.name}]})
                )
            )
        )
        return list(result.scalars().all())