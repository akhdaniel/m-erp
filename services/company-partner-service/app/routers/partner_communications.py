"""
Partner Communication API endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.partner_communication_service import PartnerCommunicationService
from app.schemas.partner_communication import (
    PartnerCommunicationCreate,
    PartnerCommunicationUpdate,
    PartnerCommunicationResponse,
    PartnerCommunicationListResponse,
    PartnerCommunicationStatsResponse,
    PartnerCommunicationBulkActionRequest
)

router = APIRouter(prefix="/partner-communications", tags=["partner-communications"])
communication_service = PartnerCommunicationService()


@router.post("/", response_model=PartnerCommunicationResponse)
def create_partner_communication(
    communication_data: PartnerCommunicationCreate,
    db: Session = Depends(get_db)
):
    """Create a new partner communication record."""
    try:
        communication = communication_service.create(db, communication_data)
        return communication
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PartnerCommunicationListResponse)
def list_partner_communications(
    partner_id: Optional[int] = Query(None, description="Filter by partner ID"),
    communication_type: Optional[str] = Query(None, description="Filter by communication type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """List partner communications with filtering and pagination."""
    if partner_id:
        communications = communication_service.get_by_partner(
            db=db,
            partner_id=partner_id,
            skip=skip,
            limit=limit,
            communication_type=communication_type,
            status=status
        )
        total = len(communications)  # Simplified for partner-specific queries
    else:
        # For now, require partner_id for performance
        raise HTTPException(
            status_code=400, 
            detail="partner_id parameter is required for listing communications"
        )
    
    return PartnerCommunicationListResponse(
        communications=communications,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/pending", response_model=List[PartnerCommunicationResponse])
def get_pending_communications(
    partner_id: Optional[int] = Query(None, description="Filter by partner ID"),
    days_ahead: int = Query(7, ge=1, le=30, description="Days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get pending communications."""
    try:
        return communication_service.get_pending_communications(db, partner_id, days_ahead)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/overdue", response_model=List[PartnerCommunicationResponse])
def get_overdue_communications(
    partner_id: Optional[int] = Query(None, description="Filter by partner ID"),
    db: Session = Depends(get_db)
):
    """Get overdue communications."""
    try:
        return communication_service.get_overdue_communications(db, partner_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/follow-ups", response_model=List[PartnerCommunicationResponse])
def get_follow_ups_due(
    partner_id: Optional[int] = Query(None, description="Filter by partner ID"),
    days_ahead: int = Query(3, ge=1, le=30, description="Days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get communications requiring follow-up."""
    try:
        return communication_service.get_follow_ups_due(db, partner_id, days_ahead)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=PartnerCommunicationStatsResponse)
def get_communication_statistics(
    partner_id: Optional[int] = Query(None, description="Filter by partner ID"),
    days_back: int = Query(30, ge=1, le=365, description="Days back to analyze"),
    db: Session = Depends(get_db)
):
    """Get communication statistics."""
    try:
        return communication_service.get_statistics(db, partner_id, days_back)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{communication_id}", response_model=PartnerCommunicationResponse)
def get_partner_communication(
    communication_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific partner communication by ID."""
    communication = communication_service.get(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Partner communication not found")
    return communication


@router.put("/{communication_id}", response_model=PartnerCommunicationResponse)
def update_partner_communication(
    communication_id: int,
    update_data: PartnerCommunicationUpdate,
    db: Session = Depends(get_db)
):
    """Update a partner communication."""
    communication = communication_service.update(db, communication_id, update_data)
    if not communication:
        raise HTTPException(status_code=404, detail="Partner communication not found")
    return communication


@router.delete("/{communication_id}")
def delete_partner_communication(
    communication_id: int,
    db: Session = Depends(get_db)
):
    """Delete a partner communication."""
    success = communication_service.delete(db, communication_id)
    if not success:
        raise HTTPException(status_code=404, detail="Partner communication not found")
    
    return {"message": "Partner communication deleted successfully"}


@router.post("/{communication_id}/complete", response_model=PartnerCommunicationResponse)
def mark_communication_completed(
    communication_id: int,
    outcome: Optional[str] = Query(None, description="Communication outcome"),
    db: Session = Depends(get_db)
):
    """Mark a communication as completed."""
    communication = communication_service.mark_completed(db, communication_id, outcome)
    if not communication:
        raise HTTPException(status_code=404, detail="Partner communication not found")
    return communication


@router.post("/{communication_id}/schedule-follow-up", response_model=PartnerCommunicationResponse)
def schedule_communication_follow_up(
    communication_id: int,
    follow_up_date: datetime,
    required: bool = Query(True, description="Is follow-up required"),
    db: Session = Depends(get_db)
):
    """Schedule a follow-up for a communication."""
    communication = communication_service.schedule_follow_up(
        db, communication_id, follow_up_date, required
    )
    if not communication:
        raise HTTPException(status_code=404, detail="Partner communication not found")
    return communication


@router.post("/bulk-action")
def perform_bulk_action(
    action_request: PartnerCommunicationBulkActionRequest,
    db: Session = Depends(get_db)
):
    """Perform bulk actions on multiple communications."""
    try:
        result = communication_service.bulk_action(db, action_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/partners/{partner_id}/timeline")
def get_partner_communication_timeline(
    partner_id: int,
    days_back: int = Query(90, ge=1, le=365, description="Days back to include"),
    db: Session = Depends(get_db)
):
    """Get communication timeline for a partner."""
    try:
        timeline = communication_service.get_communication_timeline(db, partner_id, days_back)
        return {
            "partner_id": partner_id,
            "days_back": days_back,
            "timeline": timeline
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))