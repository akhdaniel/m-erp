"""
Partner Communication service using Business Object Framework.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app.models.partner_communication import PartnerCommunication
from app.schemas.partner_communication import (
    PartnerCommunicationCreate, 
    PartnerCommunicationUpdate, 
    PartnerCommunicationResponse,
    PartnerCommunicationStatsResponse,
    PartnerCommunicationBulkActionRequest
)


class PartnerCommunicationService:
    """
    Service for managing partner communications.
    
    Provides comprehensive communication tracking, follow-up management,
    and reporting capabilities for partner interactions.
    """
    
    def __init__(self):
        self.model = PartnerCommunication
    
    def create(self, db: Session, communication_data: PartnerCommunicationCreate) -> PartnerCommunication:
        """Create a new communication record."""
        communication = PartnerCommunication(**communication_data.dict())
        db.add(communication)
        db.commit()
        db.refresh(communication)
        return communication
    
    def get(self, db: Session, communication_id: int) -> Optional[PartnerCommunication]:
        """Get a communication by ID."""
        return db.query(PartnerCommunication).filter(
            PartnerCommunication.id == communication_id
        ).first()
    
    def get_by_partner(
        self, 
        db: Session, 
        partner_id: int, 
        skip: int = 0, 
        limit: int = 100,
        communication_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PartnerCommunication]:
        """Get communications for a specific partner with optional filtering."""
        query = db.query(PartnerCommunication).filter(
            PartnerCommunication.partner_id == partner_id
        )
        
        if communication_type:
            query = query.filter(PartnerCommunication.communication_type == communication_type)
        
        if status:
            query = query.filter(PartnerCommunication.status == status)
        
        return query.order_by(desc(PartnerCommunication.created_at)).offset(skip).limit(limit).all()
    
    def update(
        self, 
        db: Session, 
        communication_id: int, 
        update_data: PartnerCommunicationUpdate
    ) -> Optional[PartnerCommunication]:
        """Update a communication record."""
        communication = self.get(db, communication_id)
        if not communication:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(communication, field, value)
        
        communication.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(communication)
        return communication
    
    def delete(self, db: Session, communication_id: int) -> bool:
        """Delete a communication record."""
        communication = self.get(db, communication_id)
        if not communication:
            return False
        
        db.delete(communication)
        db.commit()
        return True
    
    def mark_completed(
        self, 
        db: Session, 
        communication_id: int, 
        outcome: Optional[str] = None
    ) -> Optional[PartnerCommunication]:
        """Mark communication as completed with optional outcome."""
        communication = self.get(db, communication_id)
        if not communication:
            return None
        
        communication.mark_completed(outcome)
        db.commit()
        db.refresh(communication)
        return communication
    
    def schedule_follow_up(
        self, 
        db: Session, 
        communication_id: int, 
        follow_up_date: datetime,
        required: bool = True
    ) -> Optional[PartnerCommunication]:
        """Schedule a follow-up for a communication."""
        communication = self.get(db, communication_id)
        if not communication:
            return None
        
        communication.schedule_follow_up(follow_up_date, required)
        db.commit()
        db.refresh(communication)
        return communication
    
    def get_pending_communications(
        self, 
        db: Session, 
        partner_id: Optional[int] = None,
        days_ahead: int = 7
    ) -> List[PartnerCommunication]:
        """Get pending communications, optionally filtered by partner."""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = db.query(PartnerCommunication).filter(
            PartnerCommunication.status == 'pending',
            PartnerCommunication.scheduled_at <= end_date
        )
        
        if partner_id:
            query = query.filter(PartnerCommunication.partner_id == partner_id)
        
        return query.order_by(PartnerCommunication.scheduled_at).all()
    
    def get_overdue_communications(
        self, 
        db: Session, 
        partner_id: Optional[int] = None
    ) -> List[PartnerCommunication]:
        """Get overdue communications."""
        now = datetime.utcnow()
        
        query = db.query(PartnerCommunication).filter(
            PartnerCommunication.status.in_(['pending', 'in_progress']),
            PartnerCommunication.scheduled_at < now
        )
        
        if partner_id:
            query = query.filter(PartnerCommunication.partner_id == partner_id)
        
        return query.order_by(PartnerCommunication.scheduled_at).all()
    
    def get_follow_ups_due(
        self, 
        db: Session, 
        partner_id: Optional[int] = None,
        days_ahead: int = 3
    ) -> List[PartnerCommunication]:
        """Get communications requiring follow-up."""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = db.query(PartnerCommunication).filter(
            PartnerCommunication.follow_up_required == True,
            or_(
                PartnerCommunication.follow_up_date <= end_date,
                PartnerCommunication.follow_up_date == None  # Immediate follow-up
            )
        )
        
        if partner_id:
            query = query.filter(PartnerCommunication.partner_id == partner_id)
        
        return query.order_by(PartnerCommunication.follow_up_date.nullsfirst()).all()
    
    def get_statistics(
        self, 
        db: Session, 
        partner_id: Optional[int] = None,
        days_back: int = 30
    ) -> PartnerCommunicationStatsResponse:
        """Get communication statistics for reporting."""
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        base_query = db.query(PartnerCommunication)
        if partner_id:
            base_query = base_query.filter(PartnerCommunication.partner_id == partner_id)
        
        # Basic counts
        total_communications = base_query.count()
        pending_communications = base_query.filter(PartnerCommunication.status == 'pending').count()
        completed_communications = base_query.filter(PartnerCommunication.status == 'completed').count()
        
        # Overdue and follow-ups
        now = datetime.utcnow()
        overdue_communications = base_query.filter(
            PartnerCommunication.status.in_(['pending', 'in_progress']),
            PartnerCommunication.scheduled_at < now
        ).count()
        
        follow_ups_required = base_query.filter(
            PartnerCommunication.follow_up_required == True,
            or_(
                PartnerCommunication.follow_up_date <= now,
                PartnerCommunication.follow_up_date == None
            )
        ).count()
        
        # Communications by type
        type_stats = db.query(
            PartnerCommunication.communication_type,
            func.count(PartnerCommunication.id).label('count')
        )
        if partner_id:
            type_stats = type_stats.filter(PartnerCommunication.partner_id == partner_id)
        
        communications_by_type = {
            result.communication_type: result.count 
            for result in type_stats.group_by(PartnerCommunication.communication_type).all()
        }
        
        # Communications by priority
        priority_stats = db.query(
            PartnerCommunication.priority,
            func.count(PartnerCommunication.id).label('count')
        )
        if partner_id:
            priority_stats = priority_stats.filter(PartnerCommunication.partner_id == partner_id)
        
        communications_by_priority = {
            result.priority: result.count 
            for result in priority_stats.group_by(PartnerCommunication.priority).all()
        }
        
        # Recent activity
        recent_query = base_query.filter(
            PartnerCommunication.created_at >= start_date
        ).order_by(desc(PartnerCommunication.created_at)).limit(10)
        
        recent_activity = [
            {
                'id': comm.id,
                'type': comm.communication_type,
                'subject': comm.subject,
                'status': comm.status,
                'created_at': comm.created_at.isoformat(),
                'partner_id': comm.partner_id
            }
            for comm in recent_query.all()
        ]
        
        return PartnerCommunicationStatsResponse(
            total_communications=total_communications,
            pending_communications=pending_communications,
            completed_communications=completed_communications,
            overdue_communications=overdue_communications,
            follow_ups_required=follow_ups_required,
            communications_by_type=communications_by_type,
            communications_by_priority=communications_by_priority,
            recent_activity=recent_activity
        )
    
    def bulk_action(
        self, 
        db: Session, 
        action_request: PartnerCommunicationBulkActionRequest
    ) -> Dict[str, Any]:
        """Perform bulk actions on multiple communications."""
        communication_ids = action_request.communication_ids
        action = action_request.action
        data = action_request.data or {}
        
        # Get communications
        communications = db.query(PartnerCommunication).filter(
            PartnerCommunication.id.in_(communication_ids)
        ).all()
        
        if not communications:
            return {'success': False, 'message': 'No communications found'}
        
        updated_count = 0
        
        if action == 'complete':
            outcome = data.get('outcome')
            for comm in communications:
                if comm.status != 'completed':
                    comm.mark_completed(outcome)
                    updated_count += 1
        
        elif action == 'cancel':
            for comm in communications:
                if comm.status in ['pending', 'in_progress']:
                    comm.status = 'cancelled'
                    comm.updated_at = datetime.utcnow()
                    updated_count += 1
        
        elif action == 'delete':
            for comm in communications:
                db.delete(comm)
                updated_count += 1
        
        elif action == 'update_status':
            new_status = data.get('status')
            if new_status in ['pending', 'in_progress', 'completed', 'cancelled', 'failed']:
                for comm in communications:
                    comm.status = new_status
                    comm.updated_at = datetime.utcnow()
                    updated_count += 1
        
        db.commit()
        
        return {
            'success': True,
            'action': action,
            'updated_count': updated_count,
            'total_requested': len(communication_ids)
        }
    
    def get_communication_timeline(
        self, 
        db: Session, 
        partner_id: int,
        days_back: int = 90
    ) -> List[Dict[str, Any]]:
        """Get communication timeline for a partner."""
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        communications = db.query(PartnerCommunication).filter(
            PartnerCommunication.partner_id == partner_id,
            PartnerCommunication.created_at >= start_date
        ).order_by(desc(PartnerCommunication.created_at)).all()
        
        timeline = []
        for comm in communications:
            timeline.append({
                'id': comm.id,
                'date': comm.scheduled_at or comm.created_at,
                'type': comm.communication_type,
                'subject': comm.subject,
                'status': comm.status,
                'direction': comm.direction,
                'priority': comm.priority,
                'outcome': comm.outcome,
                'contact_id': comm.partner_contact_id,
                'duration_minutes': comm.get_duration_minutes()
            })
        
        return timeline