"""
Stock management services for inventory operations.

Provides business logic for stock levels, movements, and
inventory tracking across multiple locations and warehouses.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from inventory_module.models import (
    StockLevel, StockMovement, StockMovementType,
    Product, ProductVariant, WarehouseLocation
)
from inventory_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError


class StockService(BaseService):
    """
    Stock Service for managing inventory stock levels.
    
    Handles stock level tracking, availability checks,
    reservations, and stock level maintenance operations.
    """
    
    def get_stock_level(self, product_id: int, location_id: int, 
                       product_variant_id: int = None) -> Optional[StockLevel]:
        """Get stock level for product at specific location."""
        query = self.db.query(StockLevel).filter(
            and_(
                StockLevel.product_id == product_id,
                StockLevel.warehouse_location_id == location_id
            )
        )
        
        if product_variant_id:
            query = query.filter(StockLevel.product_variant_id == product_variant_id)
        else:
            query = query.filter(StockLevel.product_variant_id.is_(None))
        
        query = self._apply_company_filter(query, StockLevel)
        return query.first()
    
    def get_stock_level_or_create(self, product_id: int, location_id: int,
                                 product_variant_id: int = None) -> StockLevel:
        """Get stock level or create if doesn't exist."""
        stock_level = self.get_stock_level(product_id, location_id, product_variant_id)
        
        if not stock_level:
            data = {
                'product_id': product_id,
                'warehouse_location_id': location_id,
                'product_variant_id': product_variant_id,
                'quantity_on_hand': Decimal('0.00'),
                'quantity_reserved': Decimal('0.00'),
                'quantity_available': Decimal('0.00'),
                'quantity_incoming': Decimal('0.00')
            }
            stock_level = self.create(StockLevel, data)
        
        return stock_level
    
    def get_product_total_stock(self, product_id: int, 
                               product_variant_id: int = None) -> Dict[str, Decimal]:
        """Get total stock across all locations for a product."""
        query = self.db.query(
            func.sum(StockLevel.quantity_on_hand).label('total_on_hand'),
            func.sum(StockLevel.quantity_reserved).label('total_reserved'),
            func.sum(StockLevel.quantity_available).label('total_available'),
            func.sum(StockLevel.quantity_incoming).label('total_incoming')
        ).filter(StockLevel.product_id == product_id)
        
        if product_variant_id:
            query = query.filter(StockLevel.product_variant_id == product_variant_id)
        else:
            query = query.filter(StockLevel.product_variant_id.is_(None))
        
        query = self._apply_company_filter(query, StockLevel)
        result = query.first()
        
        return {
            'on_hand': result.total_on_hand or Decimal('0.00'),
            'reserved': result.total_reserved or Decimal('0.00'),
            'available': result.total_available or Decimal('0.00'),
            'incoming': result.total_incoming or Decimal('0.00')
        }
    
    def get_location_stock_levels(self, location_id: int, 
                                 active_only: bool = True) -> List[StockLevel]:
        """Get all stock levels for a specific location."""
        query = self.db.query(StockLevel).filter(
            StockLevel.warehouse_location_id == location_id
        )
        
        if active_only:
            query = query.filter(StockLevel.is_active == True)
        
        query = self._apply_company_filter(query, StockLevel)
        return query.all()
    
    def check_stock_availability(self, product_id: int, quantity: Decimal,
                                location_id: int = None, 
                                product_variant_id: int = None) -> Dict[str, Any]:
        """Check if sufficient stock is available."""
        if location_id:
            # Check specific location
            stock_level = self.get_stock_level(product_id, location_id, product_variant_id)
            if not stock_level:
                return {
                    'available': False,
                    'quantity_available': Decimal('0.00'),
                    'shortage': quantity,
                    'locations': []
                }
            
            available = stock_level.quantity_available >= quantity
            shortage = max(Decimal('0.00'), quantity - stock_level.quantity_available)
            
            return {
                'available': available,
                'quantity_available': stock_level.quantity_available,
                'shortage': shortage,
                'locations': [{'location_id': location_id, 'available': stock_level.quantity_available}]
            }
        else:
            # Check across all locations
            totals = self.get_product_total_stock(product_id, product_variant_id)
            available = totals['available'] >= quantity
            shortage = max(Decimal('0.00'), quantity - totals['available'])
            
            # Get location breakdown
            query = self.db.query(StockLevel).filter(
                StockLevel.product_id == product_id,
                StockLevel.quantity_available > 0
            )
            
            if product_variant_id:
                query = query.filter(StockLevel.product_variant_id == product_variant_id)
            else:
                query = query.filter(StockLevel.product_variant_id.is_(None))
            
            query = self._apply_company_filter(query, StockLevel)
            stock_levels = query.all()
            
            locations = [
                {
                    'location_id': sl.warehouse_location_id,
                    'available': sl.quantity_available
                }
                for sl in stock_levels
            ]
            
            return {
                'available': available,
                'quantity_available': totals['available'],
                'shortage': shortage,
                'locations': locations
            }
    
    def reserve_stock(self, product_id: int, quantity: Decimal,
                     location_id: int, user_id: int = None,
                     product_variant_id: int = None, 
                     reason: str = None) -> bool:
        """Reserve stock for allocation."""
        stock_level = self.get_stock_level_or_create(product_id, location_id, product_variant_id)
        
        if not stock_level.can_reserve(quantity):
            raise ValidationError(f"Insufficient stock to reserve {quantity} units")
        
        # Reserve stock
        success = stock_level.reserve_stock(quantity, reason)
        if not success:
            raise ServiceError("Failed to reserve stock")
        
        # Log audit trail
        stock_level.log_audit_trail("stock_reserved", user_id or self.user_id, {
            "quantity": float(quantity),
            "reason": reason
        })
        
        # Publish event
        stock_level.publish_event("stock_level.reserved", {
            "product_id": product_id,
            "location_id": location_id,
            "quantity": float(quantity),
            "reserved_total": float(stock_level.quantity_reserved)
        })
        
        return True
    
    def release_reservation(self, product_id: int, quantity: Decimal,
                           location_id: int, user_id: int = None,
                           product_variant_id: int = None) -> bool:
        """Release reserved stock."""
        stock_level = self.get_stock_level(product_id, location_id, product_variant_id)
        if not stock_level:
            raise NotFoundError("Stock level not found")
        
        # Release reservation
        success = stock_level.release_reservation(quantity)
        if not success:
            raise ValidationError(f"Cannot release {quantity} units - insufficient reserved stock")
        
        # Log audit trail
        stock_level.log_audit_trail("reservation_released", user_id or self.user_id, {
            "quantity": float(quantity)
        })
        
        # Publish event
        stock_level.publish_event("stock_level.reservation_released", {
            "product_id": product_id,
            "location_id": location_id,
            "quantity": float(quantity),
            "reserved_total": float(stock_level.quantity_reserved)
        })
        
        return True
    
    def adjust_stock(self, product_id: int, quantity_change: Decimal,
                    location_id: int, movement_type: StockMovementType,
                    user_id: int = None, product_variant_id: int = None,
                    reason: str = None, unit_cost: Decimal = None) -> StockLevel:
        """Adjust stock level and create movement record."""
        stock_level = self.get_stock_level_or_create(product_id, location_id, product_variant_id)
        
        # Validate adjustment
        if quantity_change < 0 and abs(quantity_change) > stock_level.quantity_on_hand:
            if not stock_level.negative_stock_allowed:
                raise ValidationError("Adjustment would result in negative stock")
        
        # Store previous quantity for movement record
        quantity_before = stock_level.quantity_on_hand
        
        # Adjust stock level
        stock_level.adjust_stock(quantity_change, movement_type)
        
        # Create stock movement record
        movement_service = StockMovementService(self.db, user_id or self.user_id, self.company_id)
        movement_service.create_movement(
            product_id=product_id,
            location_id=location_id,
            movement_type=movement_type,
            quantity=abs(quantity_change),
            product_variant_id=product_variant_id,
            unit_cost=unit_cost,
            notes=reason,
            quantity_before=quantity_before,
            quantity_after=stock_level.quantity_on_hand
        )
        
        return stock_level
    
    def get_low_stock_items(self, warehouse_id: int = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get products with low stock levels."""
        # In production, would join with Product table and check reorder points
        query = self.db.query(StockLevel).join(Product)
        
        # Filter by warehouse if specified
        if warehouse_id:
            query = query.join(WarehouseLocation).filter(
                WarehouseLocation.warehouse_id == warehouse_id
            )
        
        query = self._apply_company_filter(query, StockLevel)
        
        # Filter for low stock (simplified - would use product reorder points)
        query = query.filter(StockLevel.quantity_available <= 10)  # Simplified threshold
        
        stock_levels = query.limit(limit).all()
        
        return [
            {
                'product_id': sl.product_id,
                'location_id': sl.warehouse_location_id,
                'quantity_available': sl.quantity_available,
                'quantity_on_hand': sl.quantity_on_hand,
                'quantity_reserved': sl.quantity_reserved
            }
            for sl in stock_levels
        ]
    
    def calculate_stock_value(self, location_id: int = None,
                             product_id: int = None) -> Dict[str, Decimal]:
        """Calculate total stock value."""
        query = self.db.query(
            func.sum(StockLevel.quantity_on_hand * StockLevel.unit_cost).label('total_value'),
            func.count(StockLevel.id).label('item_count')
        )
        
        if location_id:
            query = query.filter(StockLevel.warehouse_location_id == location_id)
        
        if product_id:
            query = query.filter(StockLevel.product_id == product_id)
        
        query = self._apply_company_filter(query, StockLevel)
        result = query.first()
        
        return {
            'total_value': result.total_value or Decimal('0.00'),
            'item_count': result.item_count or 0
        }


class StockMovementService(BaseService):
    """
    Stock Movement Service for tracking inventory transactions.
    
    Handles creation and management of stock movement records
    providing complete audit trail of inventory changes.
    """
    
    def create_movement(self, product_id: int, location_id: int,
                       movement_type: StockMovementType, quantity: Decimal,
                       product_variant_id: int = None, 
                       from_location_id: int = None,
                       to_location_id: int = None,
                       unit_cost: Decimal = None,
                       batch_number: str = None,
                       serial_numbers: List[str] = None,
                       source_document_type: str = None,
                       source_document_id: int = None,
                       source_document_number: str = None,
                       notes: str = None,
                       quantity_before: Decimal = None,
                       quantity_after: Decimal = None,
                       require_approval: bool = None) -> StockMovement:
        """Create a new stock movement record."""
        
        movement_data = {
            'product_id': product_id,
            'warehouse_location_id': location_id,
            'movement_type': movement_type,
            'quantity': quantity,
            'product_variant_id': product_variant_id,
            'from_location_id': from_location_id,
            'to_location_id': to_location_id,
            'unit_cost': unit_cost,
            'total_cost': (quantity * unit_cost) if unit_cost else None,
            'batch_number': batch_number,
            'serial_numbers': serial_numbers,
            'source_document_type': source_document_type,
            'source_document_id': source_document_id,
            'source_document_number': source_document_number,
            'notes': notes,
            'quantity_before': quantity_before,
            'quantity_after': quantity_after,
            'created_by_user_id': self.user_id
        }
        
        movement = self.create(StockMovement, movement_data)
        
        # Check if approval is required
        if require_approval is None:
            require_approval = movement.requires_approval
        
        if require_approval:
            movement.publish_event("stock_movement.approval_required", {
                "movement_id": movement.id,
                "movement_type": movement_type.value,
                "quantity": float(quantity),
                "product_id": product_id
            })
        
        return movement
    
    def approve_movement(self, movement_id: int, approver_user_id: int) -> StockMovement:
        """Approve a stock movement."""
        movement = self.get_by_id_or_raise(StockMovement, movement_id)
        
        if movement.is_approved:
            raise ValidationError("Movement is already approved")
        
        movement.approved_by_user_id = approver_user_id
        movement.approved_at = datetime.utcnow()
        
        movement.log_audit_trail("approved", approver_user_id)
        movement.publish_event("stock_movement.approved", {
            "movement_id": movement.id,
            "approver_id": approver_user_id
        })
        
        return movement
    
    def create_reversal(self, movement_id: int, user_id: int, reason: str) -> StockMovement:
        """Create a reversal movement for an existing movement."""
        original_movement = self.get_by_id_or_raise(StockMovement, movement_id)
        
        if not original_movement.can_be_reversed():
            raise ValidationError("Movement cannot be reversed")
        
        # Create reversal movement
        reversal_movement = original_movement.create_reversal_movement(user_id, reason)
        
        # Save reversal movement
        self.db.add(reversal_movement)
        self.db.flush()
        
        # Update original movement
        original_movement.reversed_by_movement_id = reversal_movement.id
        
        return reversal_movement
    
    def get_product_movements(self, product_id: int, 
                             product_variant_id: int = None,
                             location_id: int = None,
                             days_back: int = 30,
                             limit: int = 100) -> List[StockMovement]:
        """Get recent movements for a product."""
        query = self.db.query(StockMovement).filter(
            StockMovement.product_id == product_id
        )
        
        if product_variant_id:
            query = query.filter(StockMovement.product_variant_id == product_variant_id)
        
        if location_id:
            query = query.filter(StockMovement.warehouse_location_id == location_id)
        
        # Filter by date range
        since_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(StockMovement.movement_date >= since_date)
        
        query = self._apply_company_filter(query, StockMovement)
        query = query.order_by(desc(StockMovement.movement_date))
        
        return query.limit(limit).all()
    
    def get_movements_by_type(self, movement_type: StockMovementType,
                             days_back: int = 7,
                             limit: int = 100) -> List[StockMovement]:
        """Get movements by type within date range."""
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(StockMovement).filter(
            and_(
                StockMovement.movement_type == movement_type,
                StockMovement.movement_date >= since_date
            )
        )
        
        query = self._apply_company_filter(query, StockMovement)
        query = query.order_by(desc(StockMovement.movement_date))
        
        return query.limit(limit).all()
    
    def get_pending_approvals(self, limit: int = 50) -> List[StockMovement]:
        """Get movements pending approval."""
        query = self.db.query(StockMovement).filter(
            and_(
                StockMovement.approved_by_user_id.is_(None),
                StockMovement.is_reversed == False
            )
        )
        
        query = self._apply_company_filter(query, StockMovement)
        query = query.order_by(desc(StockMovement.created_at))
        
        return query.limit(limit).all()
    
    def calculate_movement_statistics(self, days_back: int = 30) -> Dict[str, Any]:
        """Calculate movement statistics for reporting."""
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(
            StockMovement.movement_type,
            func.count(StockMovement.id).label('count'),
            func.sum(StockMovement.quantity).label('total_quantity'),
            func.sum(StockMovement.total_cost).label('total_value')
        ).filter(StockMovement.movement_date >= since_date)
        
        query = self._apply_company_filter(query, StockMovement)
        query = query.group_by(StockMovement.movement_type)
        
        results = query.all()
        
        statistics = {}
        for result in results:
            statistics[result.movement_type.value] = {
                'count': result.count,
                'total_quantity': float(result.total_quantity or 0),
                'total_value': float(result.total_value or 0)
            }
        
        return statistics