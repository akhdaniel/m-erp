"""
Warehouse management services for inventory location operations.

Provides business logic for warehouses, locations, capacity management,
and warehouse-related operations with optimization features.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from inventory_module.models import Warehouse, WarehouseLocation, WarehouseType, LocationType
from inventory_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError


class WarehouseService(BaseService):
    """
    Warehouse Service for managing warehouse facilities.
    
    Handles warehouse creation, configuration, operational settings,
    and warehouse-level inventory management.
    """
    
    def create_warehouse(self, name: str, code: str, 
                        warehouse_type: WarehouseType = WarehouseType.MAIN,
                        **kwargs) -> Warehouse:
        """Create a new warehouse."""
        # Validate warehouse code uniqueness within company
        existing = self.db.query(Warehouse).filter(
            and_(
                Warehouse.code == code,
                Warehouse.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Warehouse code '{code}' already exists")
        
        warehouse_data = {
            'name': name,
            'code': code,
            'warehouse_type': warehouse_type,
            **kwargs
        }
        
        warehouse = self.create(Warehouse, warehouse_data)
        
        # Create default locations if specified
        if kwargs.get('create_default_locations', True):
            self._create_default_locations(warehouse)
        
        return warehouse
    
    def _create_default_locations(self, warehouse: Warehouse) -> None:
        """Create default locations for a new warehouse."""
        location_service = WarehouseLocationService(self.db, self.user_id, self.company_id)
        
        default_locations = [
            {
                'name': 'Receiving Area',
                'code': 'REC-001',
                'location_type': LocationType.STAGING,
                'level': 0
            },
            {
                'name': 'Shipping Area', 
                'code': 'SHIP-001',
                'location_type': LocationType.STAGING,
                'level': 0
            },
            {
                'name': 'General Storage',
                'code': 'STOR-001', 
                'location_type': LocationType.ZONE,
                'level': 0
            }
        ]
        
        for location_data in default_locations:
            location_data['warehouse_id'] = warehouse.id
            location_service.create_location(**location_data)
        
        # Set default receiving and shipping locations
        receiving_location = location_service.get_location_by_code(warehouse.id, 'REC-001')
        shipping_location = location_service.get_location_by_code(warehouse.id, 'SHIP-001')
        
        if receiving_location:
            warehouse.default_receiving_location_id = receiving_location.id
        if shipping_location:
            warehouse.default_shipping_location_id = shipping_location.id
    
    def get_company_warehouses(self, active_only: bool = True) -> List[Warehouse]:
        """Get all warehouses for the company."""
        query = self.db.query(Warehouse)
        query = self._apply_company_filter(query, Warehouse)
        
        if active_only:
            query = query.filter(Warehouse.is_active == True)
        
        query = query.order_by(Warehouse.name)
        return query.all()
    
    def get_warehouse_by_code(self, code: str) -> Optional[Warehouse]:
        """Get warehouse by code."""
        query = self.db.query(Warehouse).filter(Warehouse.code == code)
        query = self._apply_company_filter(query, Warehouse)
        return query.first()
    
    def get_primary_warehouse(self) -> Optional[Warehouse]:
        """Get the primary warehouse for the company."""
        query = self.db.query(Warehouse).filter(
            Warehouse.is_primary == True
        )
        query = self._apply_company_filter(query, Warehouse)
        return query.first()
    
    def set_primary_warehouse(self, warehouse_id: int) -> Warehouse:
        """Set a warehouse as the primary warehouse."""
        # Clear existing primary warehouse
        self.db.query(Warehouse).filter(
            and_(
                Warehouse.is_primary == True,
                Warehouse.company_id == self.company_id
            )
        ).update({'is_primary': False})
        
        # Set new primary warehouse
        warehouse = self.get_by_id_or_raise(Warehouse, warehouse_id)
        warehouse.is_primary = True
        
        warehouse.log_audit_trail("set_as_primary", self.user_id)
        warehouse.publish_event("warehouse.set_primary", {
            "warehouse_id": warehouse.id,
            "warehouse_code": warehouse.code
        })
        
        return warehouse
    
    def update_warehouse_capabilities(self, warehouse_id: int, 
                                    capabilities: List[str]) -> Warehouse:
        """Update warehouse capabilities."""
        warehouse = self.get_by_id_or_raise(Warehouse, warehouse_id)
        
        old_capabilities = warehouse.capabilities or []
        warehouse.capabilities = capabilities
        
        # Log capability changes
        added = set(capabilities) - set(old_capabilities)
        removed = set(old_capabilities) - set(capabilities)
        
        if added or removed:
            warehouse.log_audit_trail("capabilities_updated", self.user_id, {
                "added": list(added),
                "removed": list(removed)
            })
        
        return warehouse
    
    def get_warehouse_utilization(self, warehouse_id: int) -> Dict[str, Any]:
        """Get warehouse utilization statistics."""
        warehouse = self.get_by_id_or_raise(Warehouse, warehouse_id)
        
        # In production, would calculate from actual location data
        return {
            'total_locations': warehouse.location_count,
            'active_locations': warehouse.active_location_count,
            'storage_utilization_percentage': warehouse.storage_utilization_percentage,
            'total_stock_value': warehouse.total_stock_value,
            'total_area_sqm': warehouse.total_area_sqm,
            'storage_area_sqm': warehouse.storage_area_sqm
        }
    
    def get_warehouses_by_capability(self, capability: str) -> List[Warehouse]:
        """Get warehouses that have a specific capability."""
        # In production, would use JSON operators for capability search
        warehouses = self.get_company_warehouses()
        
        return [w for w in warehouses if w.has_capability(capability)]
    
    def calculate_warehouse_costs(self, warehouse_id: int, 
                                 period_days: int = 30) -> Dict[str, Decimal]:
        """Calculate warehouse operational costs."""
        warehouse = self.get_by_id_or_raise(Warehouse, warehouse_id)
        
        # Basic cost calculation (would be more complex in production)
        storage_cost = Decimal('0.00')
        if warehouse.storage_area_sqm and warehouse.storage_cost_per_sqm:
            storage_cost = warehouse.storage_area_sqm * warehouse.storage_cost_per_sqm * period_days
        
        labor_cost = Decimal('0.00')
        if warehouse.labor_cost_per_hour:
            # Assume 8 hours per day operation
            labor_cost = warehouse.labor_cost_per_hour * 8 * period_days
        
        return {
            'storage_cost': storage_cost,
            'labor_cost': labor_cost,
            'total_cost': storage_cost + labor_cost,
            'period_days': period_days
        }


class WarehouseLocationService(BaseService):
    """
    Warehouse Location Service for managing storage locations.
    
    Handles location creation, hierarchy management, capacity tracking,
    and location optimization operations.
    """
    
    def create_location(self, warehouse_id: int, name: str, code: str,
                       location_type: LocationType, **kwargs) -> WarehouseLocation:
        """Create a new warehouse location."""
        # Validate warehouse exists
        warehouse = self.get_by_id_or_raise(Warehouse, warehouse_id)
        if not warehouse.is_active:
            raise ValidationError("Warehouse must be active")
        
        # Validate location code uniqueness within warehouse
        existing = self.db.query(WarehouseLocation).filter(
            and_(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.code == code
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Location code '{code}' already exists in warehouse")
        
        # Validate parent location if specified
        parent_location_id = kwargs.get('parent_location_id')
        if parent_location_id:
            parent = self.get_by_id_or_raise(WarehouseLocation, parent_location_id)
            if parent.warehouse_id != warehouse_id:
                raise ValidationError("Parent location must be in the same warehouse")
            kwargs['level'] = parent.level + 1
        else:
            kwargs.setdefault('level', 0)
        
        location_data = {
            'warehouse_id': warehouse_id,
            'name': name,
            'code': code,
            'location_type': location_type,
            **kwargs
        }
        
        location = self.create(WarehouseLocation, location_data)
        
        return location
    
    def get_warehouse_locations(self, warehouse_id: int, 
                               active_only: bool = True,
                               location_type: LocationType = None) -> List[WarehouseLocation]:
        """Get all locations for a warehouse."""
        query = self.db.query(WarehouseLocation).filter(
            WarehouseLocation.warehouse_id == warehouse_id
        )
        
        if active_only:
            query = query.filter(WarehouseLocation.is_active == True)
        
        if location_type:
            query = query.filter(WarehouseLocation.location_type == location_type)
        
        query = self._apply_company_filter(query, WarehouseLocation)
        query = query.order_by(WarehouseLocation.level, WarehouseLocation.code)
        
        return query.all()
    
    def get_location_by_code(self, warehouse_id: int, code: str) -> Optional[WarehouseLocation]:
        """Get location by code within a warehouse."""
        query = self.db.query(WarehouseLocation).filter(
            and_(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.code == code
            )
        )
        query = self._apply_company_filter(query, WarehouseLocation)
        return query.first()
    
    def get_root_locations(self, warehouse_id: int) -> List[WarehouseLocation]:
        """Get root-level locations (no parent) for a warehouse."""
        query = self.db.query(WarehouseLocation).filter(
            and_(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.parent_location_id.is_(None)
            )
        )
        query = self._apply_company_filter(query, WarehouseLocation)
        query = query.filter(WarehouseLocation.is_active == True)
        query = query.order_by(WarehouseLocation.code)
        
        return query.all()
    
    def get_child_locations(self, parent_location_id: int) -> List[WarehouseLocation]:
        """Get child locations of a parent location."""
        query = self.db.query(WarehouseLocation).filter(
            WarehouseLocation.parent_location_id == parent_location_id
        )
        query = self._apply_company_filter(query, WarehouseLocation)
        query = query.filter(WarehouseLocation.is_active == True)
        query = query.order_by(WarehouseLocation.code)
        
        return query.all()
    
    def get_location_hierarchy(self, warehouse_id: int) -> List[Dict[str, Any]]:
        """Get hierarchical location structure for a warehouse."""
        root_locations = self.get_root_locations(warehouse_id)
        
        hierarchy = []
        for location in root_locations:
            location_dict = location.to_dict()
            location_dict['children'] = self._build_location_tree(location.id)
            hierarchy.append(location_dict)
        
        return hierarchy
    
    def _build_location_tree(self, parent_id: int) -> List[Dict[str, Any]]:
        """Recursively build location tree structure."""
        children = self.get_child_locations(parent_id)
        
        tree = []
        for child in children:
            child_dict = child.to_dict()
            child_dict['children'] = self._build_location_tree(child.id)
            tree.append(child_dict)
        
        return tree
    
    def move_location(self, location_id: int, new_parent_id: int = None) -> WarehouseLocation:
        """Move location to a new parent."""
        location = self.get_by_id_or_raise(WarehouseLocation, location_id)
        
        # Validate new parent
        if new_parent_id:
            new_parent = self.get_by_id_or_raise(WarehouseLocation, new_parent_id)
            if new_parent.warehouse_id != location.warehouse_id:
                raise ValidationError("Parent location must be in the same warehouse")
            
            # Prevent circular references
            if self._would_create_circular_reference(location_id, new_parent_id):
                raise ValidationError("Moving location would create circular reference")
            
            location.level = new_parent.level + 1
        else:
            location.level = 0
        
        location.parent_location_id = new_parent_id
        
        return location
    
    def _would_create_circular_reference(self, location_id: int, new_parent_id: int) -> bool:
        """Check if moving location would create circular reference."""
        current_id = new_parent_id
        while current_id:
            if current_id == location_id:
                return True
            
            parent = self.get_by_id(WarehouseLocation, current_id)
            current_id = parent.parent_location_id if parent else None
        
        return False
    
    def update_location_capacity(self, location_id: int,
                                max_weight_kg: Decimal = None,
                                max_volume_cbm: Decimal = None,
                                max_items: int = None) -> WarehouseLocation:
        """Update location capacity limits."""
        location = self.get_by_id_or_raise(WarehouseLocation, location_id)
        
        update_data = {}
        if max_weight_kg is not None:
            update_data['max_weight_kg'] = max_weight_kg
        if max_volume_cbm is not None:
            update_data['max_volume_cbm'] = max_volume_cbm
        if max_items is not None:
            update_data['max_items'] = max_items
        
        return self.update(location, update_data)
    
    def get_available_locations(self, warehouse_id: int,
                               weight_kg: Decimal = None,
                               volume_cbm: Decimal = None,
                               items: int = None,
                               location_type: LocationType = None) -> List[WarehouseLocation]:
        """Get locations that can accommodate specified requirements."""
        query = self.db.query(WarehouseLocation).filter(
            and_(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.is_active == True,
                WarehouseLocation.is_blocked == False
            )
        )
        
        if location_type:
            query = query.filter(WarehouseLocation.location_type == location_type)
        
        query = self._apply_company_filter(query, WarehouseLocation)
        locations = query.all()
        
        # Filter by capacity requirements
        available_locations = []
        for location in locations:
            if location.can_accommodate(weight_kg, volume_cbm, items):
                available_locations.append(location)
        
        return available_locations
    
    def get_locations_at_capacity(self, warehouse_id: int, 
                                 threshold_percentage: float = 95.0) -> List[WarehouseLocation]:
        """Get locations at or near capacity."""
        locations = self.get_warehouse_locations(warehouse_id)
        
        at_capacity = []
        for location in locations:
            if location.is_at_capacity:
                at_capacity.append(location)
        
        return at_capacity
    
    def block_location(self, location_id: int, reason: str,
                      blocked_until: datetime = None) -> WarehouseLocation:
        """Block a location from use."""
        location = self.get_by_id_or_raise(WarehouseLocation, location_id)
        
        location.block_location(reason, blocked_until)
        
        location.log_audit_trail("location_blocked", self.user_id, {
            "reason": reason,
            "blocked_until": blocked_until.isoformat() if blocked_until else None
        })
        
        location.publish_event("warehouse_location.blocked", {
            "location_id": location.id,
            "warehouse_id": location.warehouse_id,
            "reason": reason
        })
        
        return location
    
    def unblock_location(self, location_id: int) -> WarehouseLocation:
        """Unblock a location."""
        location = self.get_by_id_or_raise(WarehouseLocation, location_id)
        
        if not location.is_blocked:
            raise ValidationError("Location is not blocked")
        
        location.unblock_location()
        
        location.log_audit_trail("location_unblocked", self.user_id)
        location.publish_event("warehouse_location.unblocked", {
            "location_id": location.id,
            "warehouse_id": location.warehouse_id
        })
        
        return location
    
    def optimize_putaway_locations(self, warehouse_id: int, 
                                  product_id: int,
                                  quantity: Decimal,
                                  weight_kg: Decimal = None,
                                  volume_cbm: Decimal = None) -> List[Dict[str, Any]]:
        """Get optimized putaway location suggestions."""
        available_locations = self.get_available_locations(
            warehouse_id, weight_kg, volume_cbm, int(quantity)
        )
        
        # Simple optimization: prefer locations with better pick sequence
        optimized = []
        for location in available_locations:
            score = self._calculate_putaway_score(location, product_id)
            optimized.append({
                'location': location,
                'score': score,
                'available_capacity': location.available_capacity
            })
        
        # Sort by score (higher is better)
        optimized.sort(key=lambda x: x['score'], reverse=True)
        
        return optimized[:10]  # Return top 10 suggestions
    
    def _calculate_putaway_score(self, location: WarehouseLocation, 
                                product_id: int) -> float:
        """Calculate putaway optimization score for a location."""
        score = 0.0
        
        # Prefer locations with better putaway sequence
        if location.putaway_sequence:
            score += (1000 - location.putaway_sequence) / 1000.0
        
        # Prefer locations with available capacity
        weight_util = location.weight_utilization_percentage or 0
        volume_util = location.volume_utilization_percentage or 0
        item_util = location.item_utilization_percentage or 0
        
        avg_utilization = (weight_util + volume_util + item_util) / 3
        score += (100 - avg_utilization) / 100.0  # Lower utilization = higher score
        
        # Prefer locations without restrictions
        if not location.restricted_access:
            score += 0.5
        
        return score