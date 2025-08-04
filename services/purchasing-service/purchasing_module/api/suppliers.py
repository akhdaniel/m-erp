"""
Suppliers API endpoints for the Purchasing Module.

Provides REST API endpoints for managing supplier relationships,
performance tracking, and supplier-related analytics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field, validator

from purchasing_module.services.supplier_service import SupplierService
from purchasing_module.models.supplier_performance import PerformanceRating

logger = logging.getLogger(__name__)

# Create router for supplier endpoints
suppliers_router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

# Pydantic models for request/response

class PerformanceEvaluationCreate(BaseModel):
    """Schema for creating a supplier performance evaluation."""
    supplier_id: int = Field(..., gt=0, description="Supplier ID")
    evaluation_period_start: datetime = Field(..., description="Evaluation period start date")
    evaluation_period_end: datetime = Field(..., description="Evaluation period end date")
    
    @validator('evaluation_period_end')
    def end_after_start(cls, v, values):
        if 'evaluation_period_start' in values and v <= values['evaluation_period_start']:
            raise ValueError('End date must be after start date')
        return v

class PerformanceEvaluationFinalize(BaseModel):
    """Schema for finalizing a performance evaluation."""
    evaluation_notes: Optional[str] = Field(None, max_length=2000, description="Evaluation notes")
    improvement_areas: Optional[List[str]] = Field(None, description="Areas needing improvement")
    strengths: Optional[List[str]] = Field(None, description="Supplier strengths")

class SupplierResponse(BaseModel):
    """Schema for supplier responses."""
    id: int
    name: str
    code: str
    email: str
    phone: str
    contact_person: str
    payment_terms: str
    is_active: bool
    total_orders: int
    total_value: float
    last_order_date: str

# Dependency functions

async def get_supplier_service() -> SupplierService:
    """Dependency to get supplier service instance."""
    # In production, would use proper dependency injection
    return SupplierService()

async def get_current_user_id() -> int:
    """Dependency to get current user ID from authentication."""
    # In production, would extract from JWT token or session
    return 1

async def get_current_company_id() -> int:
    """Dependency to get current company ID from authentication."""
    # In production, would extract from user context
    return 1

# API Endpoints

@suppliers_router.get("/", response_model=Dict[str, Any])
async def list_suppliers(
    search: Optional[str] = Query(None, description="Search term for supplier name"),
    active_only: bool = Query(True, description="Filter to active suppliers only"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get list of suppliers for the current company.
    
    Supports searching by name and filtering by active status.
    """
    try:
        suppliers = service.get_active_suppliers(
            company_id=company_id,
            search_term=search,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": suppliers,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(suppliers)  # In production, would get actual count
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list suppliers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.get("/{supplier_id}", response_model=Dict[str, Any])
async def get_supplier(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get detailed information about a specific supplier.
    
    Returns supplier details including contact information and address.
    """
    try:
        supplier = service.get_supplier_info(supplier_id, company_id)
        
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        return {
            "success": True,
            "data": supplier
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get supplier: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.get("/{supplier_id}/performance", response_model=Dict[str, Any])
async def get_supplier_performance_history(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get performance history for a specific supplier.
    
    Returns historical performance evaluations and metrics.
    """
    try:
        # Validate supplier exists
        supplier = service.get_supplier_info(supplier_id, company_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        performance_history = service.get_supplier_performance_history(
            supplier_id=supplier_id,
            company_id=company_id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "supplier_id": supplier_id,
                "supplier_name": supplier["name"],
                "performance_history": performance_history
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get supplier performance history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.post("/performance-evaluations", response_model=Dict[str, Any])
async def create_performance_evaluation(
    evaluation: PerformanceEvaluationCreate,
    service: SupplierService = Depends(get_supplier_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create a new supplier performance evaluation.
    
    Initiates a performance evaluation for the specified supplier and period.
    """
    try:
        # Validate supplier exists
        supplier = service.get_supplier_info(evaluation.supplier_id, company_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        performance = service.create_performance_evaluation(
            supplier_id=evaluation.supplier_id,
            company_id=company_id,
            evaluation_period_start=evaluation.evaluation_period_start,
            evaluation_period_end=evaluation.evaluation_period_end,
            evaluator_user_id=user_id
        )
        
        if not performance:
            raise HTTPException(status_code=400, detail="Failed to create performance evaluation")
        
        return {
            "success": True,
            "message": "Performance evaluation created successfully",
            "data": {
                "id": performance.id,
                "supplier_id": performance.supplier_id,
                "evaluation_period": {
                    "start": performance.evaluation_period_start.isoformat(),
                    "end": performance.evaluation_period_end.isoformat()
                },
                "total_orders": performance.total_orders,
                "total_value": float(performance.total_value),
                "on_time_delivery_percentage": performance.on_time_delivery_percentage
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create performance evaluation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.put("/performance-evaluations/{evaluation_id}/finalize", response_model=Dict[str, Any])
async def finalize_performance_evaluation(
    evaluation_id: int = Path(..., gt=0, description="Performance evaluation ID"),
    finalization: PerformanceEvaluationFinalize = None,
    service: SupplierService = Depends(get_supplier_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Finalize a supplier performance evaluation.
    
    Completes the evaluation process and calculates final ratings.
    """
    try:
        evaluation_notes = finalization.evaluation_notes if finalization else None
        improvement_areas = finalization.improvement_areas if finalization else None
        strengths = finalization.strengths if finalization else None
        
        success = service.finalize_performance_evaluation(
            performance_id=evaluation_id,
            evaluator_user_id=user_id,
            evaluation_notes=evaluation_notes,
            improvement_areas=improvement_areas,
            strengths=strengths
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to finalize performance evaluation")
        
        return {
            "success": True,
            "message": "Performance evaluation finalized successfully",
            "data": {
                "evaluation_id": evaluation_id,
                "finalized_by_user_id": user_id,
                "finalized_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to finalize performance evaluation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.get("/rankings/top-performers", response_model=Dict[str, Any])
async def get_top_suppliers(
    metric: str = Query("overall_score", description="Ranking metric"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suppliers"),
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get top-performing suppliers based on specified metric.
    
    Returns ranked list of suppliers with performance data.
    """
    try:
        valid_metrics = ["overall_score", "total_value", "on_time_percentage", "quality_rating"]
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid metric. Valid options: {', '.join(valid_metrics)}"
            )
        
        top_suppliers = service.get_top_suppliers(
            company_id=company_id,
            metric=metric,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "ranking_metric": metric,
                "top_suppliers": top_suppliers
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get top suppliers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.get("/statistics/summary", response_model=Dict[str, Any])
async def get_supplier_statistics(
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get supplier statistics for the current company.
    
    Returns summary statistics including totals, performance breakdown, and key metrics.
    """
    try:
        stats = service.get_supplier_statistics(company_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get supplier statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.get("/validate/{supplier_id}", response_model=Dict[str, Any])
async def validate_supplier(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Validate that a supplier exists and is active.
    
    Returns validation status and basic supplier information.
    """
    try:
        is_valid = service.validate_supplier(supplier_id, company_id)
        
        result = {
            "success": True,
            "data": {
                "supplier_id": supplier_id,
                "is_valid": is_valid,
                "is_active": is_valid  # In this mock, valid means active
            }
        }
        
        if is_valid:
            supplier_info = service.get_supplier_info(supplier_id, company_id)
            if supplier_info:
                result["data"]["supplier_name"] = supplier_info["name"]
                result["data"]["supplier_code"] = supplier_info["code"]
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to validate supplier: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@suppliers_router.get("/performance/ratings-breakdown", response_model=Dict[str, Any])
async def get_performance_ratings_breakdown(
    service: SupplierService = Depends(get_supplier_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get breakdown of supplier performance ratings.
    
    Returns distribution of suppliers across different performance rating categories.
    """
    try:
        # In production, would calculate actual breakdown from database
        ratings_breakdown = {
            "total_evaluated_suppliers": 35,
            "rating_distribution": {
                PerformanceRating.EXCELLENT.value: {
                    "count": 8,
                    "percentage": 22.9
                },
                PerformanceRating.GOOD.value: {
                    "count": 15,
                    "percentage": 42.9
                },
                PerformanceRating.SATISFACTORY.value: {
                    "count": 8,
                    "percentage": 22.9
                },
                PerformanceRating.NEEDS_IMPROVEMENT.value: {
                    "count": 3,
                    "percentage": 8.6
                },
                PerformanceRating.POOR.value: {
                    "count": 1,
                    "percentage": 2.9
                }
            },
            "average_performance_score": 3.7,
            "evaluation_trends": {
                "improving_suppliers": 12,
                "stable_suppliers": 18,
                "declining_suppliers": 5
            }
        }
        
        return {
            "success": True,
            "data": ratings_breakdown
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance ratings breakdown: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")