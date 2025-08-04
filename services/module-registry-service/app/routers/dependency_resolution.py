"""
Dependency resolution and conflict detection API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from app.core.database import get_db_session
from app.services.dependency_resolution_service import (
    DependencyResolutionService, DependencyConflict, ResolutionPlan, ConflictType
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dependencies", tags=["Dependency Resolution"])


# Pydantic schemas
class DependencyConflictResponse(BaseModel):
    """Response schema for dependency conflicts"""
    conflict_type: ConflictType
    module_name: str
    conflicting_module: Optional[str]
    description: str
    severity: str
    resolution_suggestions: List[str]


class ResolutionPlanResponse(BaseModel):
    """Response schema for resolution plans"""
    install_order: List[int]
    conflicts: List[DependencyConflictResponse]
    warnings: List[str]
    is_resolvable: bool


class DependencyAnalysisRequest(BaseModel):
    """Request schema for dependency analysis"""
    module_id: int = Field(..., description="Module to analyze")
    company_id: int = Field(..., description="Company context")
    target_modules: Optional[List[int]] = Field(None, description="Additional modules being considered")


class ConflictDetectionRequest(BaseModel):
    """Request schema for conflict detection"""
    module_ids: List[int] = Field(..., description="Modules to check for conflicts")
    company_id: int = Field(..., description="Company context")


class UpgradeCompatibilityRequest(BaseModel):
    """Request schema for upgrade compatibility check"""
    module_id: int = Field(..., description="Module to upgrade")
    new_version: str = Field(..., description="Target version")
    company_id: int = Field(..., description="Company context")


def get_dependency_resolution_service(db: AsyncSession = Depends(get_db_session)) -> DependencyResolutionService:
    """Dependency to get dependency resolution service"""
    return DependencyResolutionService(db)


@router.post("/analyze", response_model=ResolutionPlanResponse)
async def analyze_module_dependencies(
    request: DependencyAnalysisRequest,
    service: DependencyResolutionService = Depends(get_dependency_resolution_service)
):
    """
    Analyze dependencies for a module and create resolution plan
    
    This endpoint provides:
    - Dependency graph analysis
    - Conflict detection (circular, missing, version mismatches)
    - Installation order calculation
    - Resolution suggestions
    """
    try:
        logger.info(f"Analyzing dependencies for module {request.module_id}")
        
        resolution_plan = await service.analyze_module_dependencies(
            module_id=request.module_id,
            company_id=request.company_id,
            target_modules=request.target_modules
        )
        
        # Convert to response format
        return ResolutionPlanResponse(
            install_order=resolution_plan.install_order,
            conflicts=[
                DependencyConflictResponse(
                    conflict_type=conflict.conflict_type,
                    module_name=conflict.module_name,
                    conflicting_module=conflict.conflicting_module,
                    description=conflict.description,
                    severity=conflict.severity,
                    resolution_suggestions=conflict.resolution_suggestions
                ) for conflict in resolution_plan.conflicts
            ],
            warnings=resolution_plan.warnings,
            is_resolvable=resolution_plan.is_resolvable
        )
        
    except Exception as e:
        logger.error(f"Dependency analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dependency analysis failed: {str(e)}"
        )


@router.post("/conflicts", response_model=List[DependencyConflictResponse])
async def detect_installation_conflicts(
    request: ConflictDetectionRequest,
    service: DependencyResolutionService = Depends(get_dependency_resolution_service)
):
    """
    Detect conflicts when installing multiple modules
    
    This endpoint provides:
    - Cross-module conflict detection
    - Resource conflict identification
    - Compatibility analysis
    - Resolution recommendations
    """
    try:
        logger.info(f"Detecting conflicts for modules {request.module_ids}")
        
        conflicts = await service.detect_installation_conflicts(
            module_ids=request.module_ids,
            company_id=request.company_id
        )
        
        return [
            DependencyConflictResponse(
                conflict_type=conflict.conflict_type,
                module_name=conflict.module_name,
                conflicting_module=conflict.conflicting_module,
                description=conflict.description,
                severity=conflict.severity,
                resolution_suggestions=conflict.resolution_suggestions
            ) for conflict in conflicts
        ]
        
    except Exception as e:
        logger.error(f"Conflict detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conflict detection failed: {str(e)}"
        )


@router.post("/resolve", response_model=Dict[str, List[str]])
async def suggest_dependency_resolution(
    conflicts: List[DependencyConflictResponse],
    service: DependencyResolutionService = Depends(get_dependency_resolution_service)
):
    """
    Suggest resolutions for dependency conflicts
    
    This endpoint provides:
    - Automated resolution suggestions
    - Best practice recommendations
    - Alternative approaches
    - Step-by-step resolution guides
    """
    try:
        logger.info(f"Generating resolution suggestions for {len(conflicts)} conflicts")
        
        # Convert conflicts back to service format
        service_conflicts = [
            DependencyConflict(
                conflict_type=conflict.conflict_type,
                module_name=conflict.module_name,
                conflicting_module=conflict.conflicting_module,
                description=conflict.description,
                severity=conflict.severity,
                resolution_suggestions=conflict.resolution_suggestions
            ) for conflict in conflicts
        ]
        
        suggestions = await service.suggest_dependency_resolution(service_conflicts)
        return suggestions
        
    except Exception as e:
        logger.error(f"Resolution suggestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resolution suggestion failed: {str(e)}"
        )


@router.post("/upgrade-compatibility", response_model=List[DependencyConflictResponse])
async def validate_upgrade_compatibility(
    request: UpgradeCompatibilityRequest,
    service: DependencyResolutionService = Depends(get_dependency_resolution_service)
):
    """
    Validate if module upgrade would cause conflicts
    
    This endpoint provides:
    - Upgrade impact analysis
    - Dependent module compatibility check
    - Version constraint validation
    - Upgrade path recommendations
    """
    try:
        logger.info(f"Validating upgrade compatibility for module {request.module_id} to version {request.new_version}")
        
        conflicts = await service.validate_upgrade_compatibility(
            module_id=request.module_id,
            new_version=request.new_version,
            company_id=request.company_id
        )
        
        return [
            DependencyConflictResponse(
                conflict_type=conflict.conflict_type,
                module_name=conflict.module_name,
                conflicting_module=conflict.conflicting_module,
                description=conflict.description,
                severity=conflict.severity,
                resolution_suggestions=conflict.resolution_suggestions
            ) for conflict in conflicts
        ]
        
    except Exception as e:
        logger.error(f"Upgrade compatibility check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upgrade compatibility check failed: {str(e)}"
        )


@router.get("/graph/{company_id}", response_model=Dict[str, Any])
async def get_dependency_graph(
    company_id: int,
    include_optional: bool = Query(False, description="Include optional dependencies"),
    service: DependencyResolutionService = Depends(get_dependency_resolution_service)
):
    """
    Get dependency graph for a company's installed modules
    
    This endpoint provides:
    - Visual dependency graph data
    - Module relationships
    - Dependency chains
    - Installation order information
    """
    try:
        logger.info(f"Getting dependency graph for company {company_id}")
        
        # Build dependency graph
        dependency_graph = await service._build_dependency_graph(company_id, [])
        
        # Convert to response format
        graph_data = {
            "nodes": [],
            "edges": []
        }
        
        for module_name, node in dependency_graph.items():
            graph_data["nodes"].append({
                "id": node.module_id,
                "name": node.name,
                "version": node.version,
                "provides": node.provides,
                "conflicts_with": node.conflicts_with
            })
            
            # Add edges for dependencies
            for dep_name in node.dependencies:
                if dep_name in dependency_graph:
                    dep_node = dependency_graph[dep_name]
                    graph_data["edges"].append({
                        "from": node.module_id,
                        "to": dep_node.module_id,
                        "type": "required",
                        "dependency_name": dep_name
                    })
            
            # Add optional dependencies if requested
            if include_optional:
                for dep_name in node.optional_dependencies:
                    if dep_name in dependency_graph:
                        dep_node = dependency_graph[dep_name]
                        graph_data["edges"].append({
                            "from": node.module_id,
                            "to": dep_node.module_id,
                            "type": "optional",
                            "dependency_name": dep_name
                        })
        
        return {
            "company_id": company_id,
            "graph": graph_data,
            "statistics": {
                "total_modules": len(graph_data["nodes"]),
                "total_dependencies": len(graph_data["edges"]),
                "modules_with_dependencies": len([
                    node for node in dependency_graph.values() 
                    if node.dependencies or node.optional_dependencies
                ])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get dependency graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dependency graph: {str(e)}"
        )


@router.get("/validate/{module_id}")
async def validate_module_dependencies(
    module_id: int,
    company_id: int = Query(..., description="Company context"),
    service: DependencyResolutionService = Depends(get_dependency_resolution_service)
):
    """
    Quick validation of a single module's dependencies
    
    Returns basic dependency status without full resolution plan
    """
    try:
        logger.info(f"Validating dependencies for module {module_id}")
        
        resolution_plan = await service.analyze_module_dependencies(
            module_id=module_id,
            company_id=company_id
        )
        
        return {
            "module_id": module_id,
            "is_installable": resolution_plan.is_resolvable,
            "critical_conflicts": len([
                c for c in resolution_plan.conflicts 
                if c.severity == "critical"
            ]),
            "total_conflicts": len(resolution_plan.conflicts),
            "dependencies_resolved": len(resolution_plan.install_order) > 0
        }
        
    except Exception as e:
        logger.error(f"Dependency validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dependency validation failed: {str(e)}"
        )