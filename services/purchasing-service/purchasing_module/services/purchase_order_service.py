"""
Purchase Order Service for managing the complete purchase order lifecycle.

This service provides business logic for creating, managing, and processing
purchase orders within the XERPIUM purchasing module.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from purchasing_module.models.purchase_order import PurchaseOrder, PurchaseOrderLineItem, PurchaseOrderStatus
from purchasing_module.services.approval_service import ApprovalService
from purchasing_module.services.supplier_service import SupplierService

logger = logging.getLogger(__name__)


class PurchaseOrderService:
    """
    Service class for Purchase Order management.
    
    Handles the complete purchase order lifecycle including creation,
    approval workflows, supplier management, and status tracking.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the Purchase Order Service.
        
        Args:
            db_session: Database session (in production, injected via DI)
        """
        self.db_session = db_session
        self.approval_service = ApprovalService(db_session)
        self.supplier_service = SupplierService(db_session)
        
    def create_purchase_order(
        self,
        company_id: int,
        supplier_id: int,
        line_items: List[Dict[str, Any]],
        created_by_user_id: int,
        delivery_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        currency_code: str = "USD"
    ) -> Optional[PurchaseOrder]:
        """
        Create a new purchase order with line items.
        
        Args:
            company_id: Company ID for multi-company isolation
            supplier_id: ID of the supplier
            line_items: List of line item dictionaries
            created_by_user_id: ID of user creating the order
            delivery_date: Expected delivery date
            notes: Optional order notes
            currency_code: Currency for the order
            
        Returns:
            PurchaseOrder: Created purchase order or None if failed
        """
        try:
            # Validate supplier exists and is active
            if not self.supplier_service.validate_supplier(supplier_id, company_id):
                logger.error(f"Invalid supplier {supplier_id} for company {company_id}")
                return None
            
            # Generate PO number
            po_number = self._generate_po_number(company_id)
            
            # Create purchase order
            purchase_order = PurchaseOrder(
                company_id=company_id,
                po_number=po_number,
                supplier_id=supplier_id,
                status=PurchaseOrderStatus.DRAFT,
                order_date=datetime.utcnow(),
                expected_delivery_date=delivery_date,
                currency_code=currency_code,
                notes=notes,
                created_by_user_id=created_by_user_id
            )
            
            # Add line items
            total_amount = Decimal('0.00')
            for item_data in line_items:
                line_item = self._create_line_item(purchase_order, item_data)
                if line_item:
                    # In production, would add to session
                    # purchase_order.line_items.append(line_item)
                    total_amount += line_item.line_total
            
            # Set total amount
            purchase_order.total_amount = total_amount
            
            # Save purchase order
            purchase_order.save(self.db_session, created_by_user_id)
            
            logger.info(f"Created purchase order {po_number} for supplier {supplier_id}")
            
            # Publish creation event
            purchase_order.publish_event("purchase_order.created", {
                "po_number": po_number,
                "supplier_id": supplier_id,
                "total_amount": float(total_amount),
                "currency_code": currency_code,
                "line_items_count": len(line_items)
            })
            
            return purchase_order
            
        except Exception as e:
            logger.error(f"Failed to create purchase order: {e}")
            return None
    
    def _generate_po_number(self, company_id: int) -> str:
        """
        Generate a unique purchase order number.
        
        Args:
            company_id: Company ID for scoping
            
        Returns:
            str: Unique PO number
        """
        # In production, this would query the database for the last PO number
        # and increment it, ensuring uniqueness within the company
        
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        sequence = "001"  # Would be calculated from database
        
        return f"PO-{company_id}-{timestamp}-{sequence}"
    
    def _create_line_item(
        self,
        purchase_order: PurchaseOrder,
        item_data: Dict[str, Any]
    ) -> Optional[PurchaseOrderLineItem]:
        """
        Create a purchase order line item.
        
        Args:
            purchase_order: Parent purchase order
            item_data: Line item data dictionary
            
        Returns:
            PurchaseOrderLineItem: Created line item or None if failed
        """
        try:
            required_fields = ['product_name', 'quantity', 'unit_price']
            for field in required_fields:
                if field not in item_data:
                    logger.error(f"Missing required field '{field}' in line item data")
                    return None
            
            line_item = PurchaseOrderLineItem(
                company_id=purchase_order.company_id,
                purchase_order_id=purchase_order.id,
                line_number=item_data.get('line_number', 1),
                product_code=item_data.get('product_code'),
                product_name=item_data['product_name'],
                description=item_data.get('description', ''),
                quantity=Decimal(str(item_data['quantity'])),
                unit_price=Decimal(str(item_data['unit_price'])),
                unit_of_measure=item_data.get('unit_of_measure', 'each'),
                expected_delivery_date=item_data.get('expected_delivery_date'),
                notes=item_data.get('notes')
            )
            
            # Calculate line total
            line_item.calculate_line_total()
            
            return line_item
            
        except Exception as e:
            logger.error(f"Failed to create line item: {e}")
            return None
    
    def submit_for_approval(
        self,
        purchase_order_id: int,
        submitted_by_user_id: int,
        approval_notes: Optional[str] = None
    ) -> bool:
        """
        Submit a purchase order for approval.
        
        Args:
            purchase_order_id: ID of purchase order to submit
            submitted_by_user_id: ID of user submitting
            approval_notes: Optional submission notes
            
        Returns:
            bool: True if submitted successfully
        """
        try:
            # In production, would load from database
            # purchase_order = self.db_session.query(PurchaseOrder).get(purchase_order_id)
            purchase_order = self._get_mock_purchase_order(purchase_order_id)
            
            if not purchase_order:
                logger.error(f"Purchase order {purchase_order_id} not found")
                return False
            
            if purchase_order.status != PurchaseOrderStatus.DRAFT:
                logger.error(f"Purchase order {purchase_order_id} is not in draft status")
                return False
            
            # Determine approval workflow based on amount
            workflow_config = self._determine_approval_workflow(purchase_order.total_amount)
            
            # Create approval workflow
            workflow_created = self.approval_service.create_approval_workflow(
                purchase_order_id=purchase_order_id,
                submitted_by_user_id=submitted_by_user_id,
                workflow_config=workflow_config,
                submission_notes=approval_notes
            )
            
            if not workflow_created:
                logger.error(f"Failed to create approval workflow for PO {purchase_order_id}")
                return False
            
            # Update purchase order status
            purchase_order.status = PurchaseOrderStatus.PENDING_APPROVAL
            purchase_order.submitted_for_approval_at = datetime.utcnow()
            purchase_order.submitted_by_user_id = submitted_by_user_id
            
            # Save changes
            purchase_order.save(self.db_session, submitted_by_user_id)
            
            # Publish submission event
            purchase_order.publish_event("purchase_order.submitted_for_approval", {
                "po_number": purchase_order.po_number,
                "total_amount": float(purchase_order.total_amount),
                "submitted_by_user_id": submitted_by_user_id,
                "workflow_type": workflow_config.get("name", "standard")
            })
            
            logger.info(f"Purchase order {purchase_order.po_number} submitted for approval")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit purchase order for approval: {e}")
            return False
    
    def _determine_approval_workflow(self, total_amount: Decimal) -> Dict[str, Any]:
        """
        Determine the appropriate approval workflow based on purchase order amount.
        
        Args:
            total_amount: Total amount of the purchase order
            
        Returns:
            dict: Workflow configuration
        """
        amount = float(total_amount)
        
        if amount < 1000:
            return {
                "name": "manager_approval",
                "description": "Manager approval for small purchases",
                "steps": [
                    {
                        "name": "Manager Approval",
                        "type": "manager",
                        "required": True,
                        "amount_limit": 1000
                    }
                ]
            }
        elif amount < 10000:
            return {
                "name": "director_approval", 
                "description": "Director approval for medium purchases",
                "steps": [
                    {
                        "name": "Manager Approval",
                        "type": "manager", 
                        "required": True,
                        "amount_limit": 1000
                    },
                    {
                        "name": "Director Approval",
                        "type": "director",
                        "required": True,
                        "amount_limit": 10000
                    }
                ]
            }
        else:
            return {
                "name": "executive_approval",
                "description": "Executive approval for large purchases", 
                "steps": [
                    {
                        "name": "Manager Approval",
                        "type": "manager",
                        "required": True,
                        "amount_limit": 1000
                    },
                    {
                        "name": "Director Approval", 
                        "type": "director",
                        "required": True,
                        "amount_limit": 10000
                    },
                    {
                        "name": "Executive Approval",
                        "type": "executive",
                        "required": True,
                        "amount_limit": None
                    }
                ]
            }
    
    def approve_purchase_order(
        self,
        purchase_order_id: int,
        approved_by_user_id: int,
        approval_notes: Optional[str] = None
    ) -> bool:
        """
        Approve a purchase order (complete approval process).
        
        Args:
            purchase_order_id: ID of purchase order to approve
            approved_by_user_id: ID of user approving
            approval_notes: Optional approval notes
            
        Returns:
            bool: True if approved successfully
        """
        try:
            # In production, would load from database
            purchase_order = self._get_mock_purchase_order(purchase_order_id)
            
            if not purchase_order:
                logger.error(f"Purchase order {purchase_order_id} not found")
                return False
            
            if purchase_order.status != PurchaseOrderStatus.PENDING_APPROVAL:
                logger.error(f"Purchase order {purchase_order_id} is not pending approval")
                return False
            
            # Update status
            purchase_order.status = PurchaseOrderStatus.APPROVED
            purchase_order.approved_at = datetime.utcnow()
            purchase_order.approved_by_user_id = approved_by_user_id
            
            if approval_notes:
                purchase_order.approval_notes = approval_notes
            
            # Save changes
            purchase_order.save(self.db_session, approved_by_user_id)
            
            # Publish approval event
            purchase_order.publish_event("purchase_order.approved", {
                "po_number": purchase_order.po_number,
                "total_amount": float(purchase_order.total_amount),
                "approved_by_user_id": approved_by_user_id
            })
            
            logger.info(f"Purchase order {purchase_order.po_number} approved")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve purchase order: {e}")
            return False
    
    def reject_purchase_order(
        self,
        purchase_order_id: int,
        rejected_by_user_id: int,
        rejection_reason: str
    ) -> bool:
        """
        Reject a purchase order.
        
        Args:
            purchase_order_id: ID of purchase order to reject
            rejected_by_user_id: ID of user rejecting
            rejection_reason: Reason for rejection
            
        Returns:
            bool: True if rejected successfully
        """
        try:
            # In production, would load from database
            purchase_order = self._get_mock_purchase_order(purchase_order_id)
            
            if not purchase_order:
                logger.error(f"Purchase order {purchase_order_id} not found")
                return False
            
            if purchase_order.status not in [PurchaseOrderStatus.PENDING_APPROVAL, PurchaseOrderStatus.DRAFT]:
                logger.error(f"Purchase order {purchase_order_id} cannot be rejected in current status")
                return False
            
            # Update status
            purchase_order.status = PurchaseOrderStatus.REJECTED
            purchase_order.rejected_at = datetime.utcnow()
            purchase_order.rejected_by_user_id = rejected_by_user_id
            purchase_order.rejection_reason = rejection_reason
            
            # Save changes
            purchase_order.save(self.db_session, rejected_by_user_id)
            
            # Publish rejection event
            purchase_order.publish_event("purchase_order.rejected", {
                "po_number": purchase_order.po_number,
                "total_amount": float(purchase_order.total_amount),
                "rejected_by_user_id": rejected_by_user_id,
                "rejection_reason": rejection_reason
            })
            
            logger.info(f"Purchase order {purchase_order.po_number} rejected")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject purchase order: {e}")
            return False
    
    def send_to_supplier(
        self,
        purchase_order_id: int,
        sent_by_user_id: int,
        delivery_method: str = "email"
    ) -> bool:
        """
        Send approved purchase order to supplier.
        
        Args:
            purchase_order_id: ID of purchase order to send
            sent_by_user_id: ID of user sending
            delivery_method: Method of delivery (email, fax, etc.)
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # In production, would load from database
            purchase_order = self._get_mock_purchase_order(purchase_order_id)
            
            if not purchase_order:
                logger.error(f"Purchase order {purchase_order_id} not found")
                return False
            
            if purchase_order.status != PurchaseOrderStatus.APPROVED:
                logger.error(f"Purchase order {purchase_order_id} is not approved")
                return False
            
            # Update status
            purchase_order.status = PurchaseOrderStatus.SENT_TO_SUPPLIER
            purchase_order.sent_to_supplier_at = datetime.utcnow()
            purchase_order.sent_by_user_id = sent_by_user_id
            
            # Save changes
            purchase_order.save(self.db_session, sent_by_user_id)
            
            # In production, would integrate with email/notification service
            logger.info(f"Purchase order {purchase_order.po_number} sent to supplier via {delivery_method}")
            
            # Publish sent event
            purchase_order.publish_event("purchase_order.sent_to_supplier", {
                "po_number": purchase_order.po_number,
                "supplier_id": purchase_order.supplier_id,
                "delivery_method": delivery_method,
                "sent_by_user_id": sent_by_user_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send purchase order to supplier: {e}")
            return False
    
    def update_delivery_status(
        self,
        purchase_order_id: int,
        status: PurchaseOrderStatus,
        updated_by_user_id: int,
        delivery_notes: Optional[str] = None
    ) -> bool:
        """
        Update delivery status of purchase order.
        
        Args:
            purchase_order_id: ID of purchase order
            status: New delivery status
            updated_by_user_id: ID of user updating
            delivery_notes: Optional delivery notes
            
        Returns:
            bool: True if updated successfully
        """
        try:
            # In production, would load from database
            purchase_order = self._get_mock_purchase_order(purchase_order_id)
            
            if not purchase_order:
                logger.error(f"Purchase order {purchase_order_id} not found")
                return False
            
            valid_delivery_statuses = [
                PurchaseOrderStatus.PARTIALLY_RECEIVED,
                PurchaseOrderStatus.RECEIVED,
                PurchaseOrderStatus.COMPLETED
            ]
            
            if status not in valid_delivery_statuses:
                logger.error(f"Invalid delivery status: {status}")
                return False
            
            # Update status
            old_status = purchase_order.status
            purchase_order.status = status
            
            if status == PurchaseOrderStatus.RECEIVED:
                purchase_order.received_at = datetime.utcnow()
            elif status == PurchaseOrderStatus.COMPLETED:
                purchase_order.completed_at = datetime.utcnow()
            
            if delivery_notes:
                purchase_order.delivery_notes = delivery_notes
            
            # Save changes
            purchase_order.save(self.db_session, updated_by_user_id)
            
            # Publish status update event
            purchase_order.publish_event("purchase_order.status_updated", {
                "po_number": purchase_order.po_number,
                "old_status": old_status.value,
                "new_status": status.value,
                "updated_by_user_id": updated_by_user_id
            })
            
            logger.info(f"Purchase order {purchase_order.po_number} status updated to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update purchase order delivery status: {e}")
            return False
    
    def get_purchase_orders_by_company(
        self,
        company_id: int,
        status_filter: Optional[PurchaseOrderStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get purchase orders for a company with optional filtering.
        
        Args:
            company_id: Company ID for data isolation
            status_filter: Optional status filter
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[dict]: List of purchase order summaries
        """
        try:
            # In production, would query database with proper filtering
            # This is a mock implementation
            
            mock_orders = [
                {
                    "id": 1,
                    "po_number": f"PO-{company_id}-20250801-001",
                    "supplier_id": 1,
                    "status": PurchaseOrderStatus.DRAFT.value,
                    "total_amount": 1500.00,
                    "currency_code": "USD",
                    "order_date": datetime.utcnow().isoformat(),
                    "created_by_user_id": 1
                },
                {
                    "id": 2,
                    "po_number": f"PO-{company_id}-20250801-002",
                    "supplier_id": 2,
                    "status": PurchaseOrderStatus.APPROVED.value,
                    "total_amount": 2500.00,
                    "currency_code": "USD",
                    "order_date": datetime.utcnow().isoformat(),
                    "created_by_user_id": 1
                }
            ]
            
            # Apply status filter if provided
            if status_filter:
                mock_orders = [
                    order for order in mock_orders 
                    if order["status"] == status_filter.value
                ]
            
            # Apply pagination
            return mock_orders[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to get purchase orders: {e}")
            return []
    
    def _get_mock_purchase_order(self, purchase_order_id: int) -> Optional[PurchaseOrder]:
        """
        Mock method to simulate loading a purchase order from database.
        In production, this would be a proper database query.
        """
        # Create a mock purchase order for testing
        mock_po = PurchaseOrder(
            id=purchase_order_id,
            company_id=1,
            po_number=f"PO-1-20250801-{purchase_order_id:03d}",
            supplier_id=1,
            status=PurchaseOrderStatus.DRAFT,
            order_date=datetime.utcnow(),
            total_amount=Decimal('1500.00'),
            currency_code="USD",
            created_by_user_id=1
        )
        
        return mock_po
    
    def get_purchase_order_statistics(self, company_id: int) -> Dict[str, Any]:
        """
        Get purchase order statistics for a company.
        
        Args:
            company_id: Company ID for data isolation
            
        Returns:
            dict: Statistics summary
        """
        try:
            # In production, would calculate from database
            return {
                "total_orders": 150,
                "total_value": 75000.00,
                "average_order_value": 500.00,
                "status_breakdown": {
                    "draft": 12,
                    "pending_approval": 8,
                    "approved": 15,
                    "sent_to_supplier": 20,
                    "partially_received": 10,
                    "received": 45,
                    "completed": 35,
                    "cancelled": 3,
                    "rejected": 2
                },
                "monthly_trend": {
                    "current_month": 25,
                    "previous_month": 18,
                    "growth_percentage": 38.9
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get purchase order statistics: {e}")
            return {}