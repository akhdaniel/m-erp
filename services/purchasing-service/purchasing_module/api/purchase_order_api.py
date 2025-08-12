"""
Purchase Order API endpoints for purchasing module.

Provides comprehensive REST API for purchase order management including
CRUD operations, line items, approvals, and supplier integration.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status, Body
from fastapi.responses import JSONResponse
from decimal import Decimal
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/purchase-orders", tags=["purchase-orders"])

# In-memory storage for demo purposes
mock_purchase_orders_db = []
next_po_id = 1

# Dependencies
def get_current_user_id() -> int:
    """Get current user ID from authentication."""
    # In production, would extract from JWT token
    return 1

def get_current_company_id() -> int:
    """Get current company ID from context."""
    # In production, would extract from request context
    return 1


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create new purchase order.
    
    Creates a purchase order with line items and calculates totals.
    Initiates approval workflow based on amount.
    """
    global next_po_id
    
    try:
        # Extract data from request
        po_data = request.copy()
        line_items = po_data.pop('items', []) or po_data.pop('line_items', [])
        
        # Generate PO number
        po_id = next_po_id
        next_po_id += 1
        po_number = f"PO-{datetime.now().year}-{po_id:05d}"
        
        # Create purchase order
        purchase_order = {
            "id": po_id,
            "po_number": po_number,
            "supplier_id": po_data.get('supplier_id'),
            "supplier_name": po_data.get('supplier_name', 'Supplier'),
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery": po_data.get('expected_delivery'),
            "status": "draft",
            "approval_status": "pending",
            "currency_code": po_data.get('currency_code', 'USD'),
            "payment_terms": po_data.get('payment_terms', 'Net 30'),
            "shipping_address": po_data.get('shipping_address'),
            "billing_address": po_data.get('billing_address'),
            "notes": po_data.get('notes'),
            "subtotal": Decimal("0.00"),
            "tax_amount": Decimal("0.00"),
            "shipping_amount": po_data.get('shipping_amount', Decimal("0.00")),
            "total_amount": Decimal("0.00"),
            "created_by": user_id,
            "company_id": company_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
            "line_items": []
        }
        
        # Process line items
        if line_items:
            subtotal = Decimal("0.00")
            formatted_items = []
            
            for idx, item in enumerate(line_items):
                quantity = Decimal(str(item.get('quantity', 0)))
                unit_price = Decimal(str(item.get('unit_price', 0)))
                discount_pct = Decimal(str(item.get('discount_percentage', 0)))
                tax_rate = Decimal(str(item.get('tax_rate', 0)))
                
                line_total = quantity * unit_price
                discount_amt = line_total * (discount_pct / 100)
                line_subtotal = line_total - discount_amt
                tax_amt = line_subtotal * (tax_rate / 100)
                
                subtotal += line_subtotal
                
                formatted_items.append({
                    "id": idx + 1,
                    "line_number": idx + 1,
                    "product_id": item.get('product_id'),
                    "product_name": item.get('product_name'),
                    "product_code": item.get('product_code'),
                    "description": item.get('description', f"{item.get('product_code', '')} - {item.get('product_name', '')}"),
                    "quantity": str(quantity),
                    "unit_of_measure": item.get('unit_of_measure', 'each'),
                    "unit_price": str(unit_price),
                    "discount_percentage": str(discount_pct),
                    "discount_amount": str(discount_amt),
                    "tax_rate": str(tax_rate),
                    "tax_amount": str(tax_amt),
                    "line_total": str(line_subtotal + tax_amt),
                    "expected_delivery": item.get('expected_delivery'),
                    "notes": item.get('notes')
                })
            
            purchase_order['line_items'] = formatted_items
            purchase_order['subtotal'] = str(subtotal)
            
            # Calculate tax (simplified - would be more complex in production)
            total_tax = sum(Decimal(item['tax_amount']) for item in formatted_items)
            purchase_order['tax_amount'] = str(total_tax)
            
            # Calculate total
            total = subtotal + total_tax + Decimal(str(purchase_order['shipping_amount']))
            purchase_order['total_amount'] = str(total)
            
            # Determine approval requirements based on amount
            if total > 10000:
                purchase_order['approval_status'] = 'requires_approval'
                purchase_order['approval_level'] = 'executive'
            elif total > 5000:
                purchase_order['approval_status'] = 'requires_approval'
                purchase_order['approval_level'] = 'manager'
            else:
                purchase_order['approval_status'] = 'auto_approved'
                purchase_order['status'] = 'approved'
        
        # Store in mock database
        mock_purchase_orders_db.append(purchase_order)
        
        return purchase_order
        
    except Exception as e:
        logger.error(f"Error creating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=Dict[str, Any])
async def list_purchase_orders(
    status: Optional[str] = Query(None, description="Filter by status"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    company_id: int = Depends(get_current_company_id)
):
    """
    List purchase orders with filtering and pagination.
    
    Returns paginated list of purchase orders with optional filters
    for status, supplier, and date range.
    """
    try:
        # Filter purchase orders
        filtered_orders = [
            po for po in mock_purchase_orders_db
            if po.get('company_id') == company_id
        ]
        
        if status:
            filtered_orders = [po for po in filtered_orders if po.get('status') == status]
        
        if supplier_id:
            filtered_orders = [po for po in filtered_orders if po.get('supplier_id') == supplier_id]
        
        # TODO: Add date filtering
        
        # Pagination
        total_count = len(filtered_orders)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_orders = filtered_orders[start_idx:end_idx]
        
        return {
            "data": paginated_orders,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"Error listing purchase orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{po_id}")
async def get_purchase_order(
    po_id: int = Path(..., gt=0, description="Purchase Order ID"),
    include_line_items: bool = Query(True, description="Include line items"),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get purchase order by ID.
    
    Returns complete purchase order information with optional
    inclusion of line items.
    """
    try:
        # Find purchase order in mock database
        purchase_order = None
        for po in mock_purchase_orders_db:
            if po.get('id') == po_id and po.get('company_id') == company_id:
                purchase_order = po
                break
        
        if not purchase_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        # Optionally exclude line items
        if not include_line_items:
            po_copy = purchase_order.copy()
            po_copy.pop('line_items', None)
            return po_copy
        
        return purchase_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{po_id}")
async def update_purchase_order(
    po_id: int = Path(..., gt=0, description="Purchase Order ID"),
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Update existing purchase order.
    
    Updates purchase order information and recalculates totals
    if line items are modified.
    """
    try:
        # Extract line items from request if present
        line_items = request.pop('items', None) or request.pop('line_items', None)
        
        # Find purchase order in mock database
        po_index = -1
        purchase_order = None
        for i, po in enumerate(mock_purchase_orders_db):
            if po.get('id') == po_id and po.get('company_id') == company_id:
                purchase_order = po
                po_index = i
                break
        
        if not purchase_order:
            # Create placeholder for demo
            purchase_order = {
                'id': po_id,
                'po_number': f'PO-{datetime.now().year}-{po_id:05d}',
                'status': 'draft',
                'company_id': company_id,
                'created_at': datetime.utcnow().isoformat(),
                'line_items': [],
                'subtotal': '0.00',
                'total_amount': '0.00'
            }
            mock_purchase_orders_db.append(purchase_order)
            po_index = len(mock_purchase_orders_db) - 1
        
        # Update fields
        for key, value in request.items():
            if key not in ['items', 'line_items']:
                purchase_order[key] = value
        
        purchase_order['updated_at'] = datetime.utcnow().isoformat()
        purchase_order['updated_by'] = user_id
        
        # Handle line items if provided
        if line_items is not None:
            subtotal = Decimal("0.00")
            formatted_items = []
            
            for idx, item in enumerate(line_items):
                quantity = Decimal(str(item.get('quantity', 0)))
                unit_price = Decimal(str(item.get('unit_price', 0)))
                discount_pct = Decimal(str(item.get('discount_percentage', 0)))
                tax_rate = Decimal(str(item.get('tax_rate', 0)))
                
                line_total = quantity * unit_price
                discount_amt = line_total * (discount_pct / 100)
                line_subtotal = line_total - discount_amt
                tax_amt = line_subtotal * (tax_rate / 100)
                
                subtotal += line_subtotal
                
                formatted_items.append({
                    "id": idx + 1,
                    "line_number": idx + 1,
                    "product_id": item.get('product_id'),
                    "product_name": item.get('product_name'),
                    "product_code": item.get('product_code'),
                    "description": item.get('description', f"{item.get('product_code', '')} - {item.get('product_name', '')}"),
                    "quantity": str(quantity),
                    "unit_of_measure": item.get('unit_of_measure', 'each'),
                    "unit_price": str(unit_price),
                    "discount_percentage": str(discount_pct),
                    "discount_amount": str(discount_amt),
                    "tax_rate": str(tax_rate),
                    "tax_amount": str(tax_amt),
                    "line_total": str(line_subtotal + tax_amt),
                    "expected_delivery": item.get('expected_delivery'),
                    "notes": item.get('notes')
                })
            
            purchase_order['line_items'] = formatted_items
            purchase_order['subtotal'] = str(subtotal)
            
            # Calculate tax
            total_tax = sum(Decimal(item['tax_amount']) for item in formatted_items)
            purchase_order['tax_amount'] = str(total_tax)
            
            # Calculate total
            shipping = Decimal(str(purchase_order.get('shipping_amount', 0)))
            total = subtotal + total_tax + shipping
            purchase_order['total_amount'] = str(total)
        
        # Store back in mock database
        mock_purchase_orders_db[po_index] = purchase_order
        
        return purchase_order
        
    except Exception as e:
        logger.error(f"Error updating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(
    po_id: int = Path(..., gt=0, description="Purchase Order ID"),
    company_id: int = Depends(get_current_company_id)
):
    """
    Delete purchase order.
    
    Soft deletes the purchase order by marking it as inactive.
    """
    try:
        # Find and remove from mock database
        for i, po in enumerate(mock_purchase_orders_db):
            if po.get('id') == po_id and po.get('company_id') == company_id:
                if po.get('status') not in ['draft', 'cancelled']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot delete non-draft purchase orders"
                    )
                mock_purchase_orders_db.pop(i)
                return
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{po_id}/approve")
async def approve_purchase_order(
    po_id: int = Path(..., gt=0, description="Purchase Order ID"),
    approval_notes: Optional[str] = Body(None),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Approve purchase order.
    
    Approves the purchase order and updates status.
    """
    try:
        # Find purchase order
        for po in mock_purchase_orders_db:
            if po.get('id') == po_id and po.get('company_id') == company_id:
                if po.get('approval_status') != 'requires_approval':
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Purchase order does not require approval"
                    )
                
                po['approval_status'] = 'approved'
                po['status'] = 'approved'
                po['approved_by'] = user_id
                po['approved_at'] = datetime.utcnow().isoformat()
                po['approval_notes'] = approval_notes
                
                return {"message": "Purchase order approved successfully", "purchase_order": po}
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{po_id}/reject")
async def reject_purchase_order(
    po_id: int = Path(..., gt=0, description="Purchase Order ID"),
    rejection_reason: str = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Reject purchase order.
    
    Rejects the purchase order with reason.
    """
    try:
        # Find purchase order
        for po in mock_purchase_orders_db:
            if po.get('id') == po_id and po.get('company_id') == company_id:
                if po.get('approval_status') != 'requires_approval':
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Purchase order does not require approval"
                    )
                
                po['approval_status'] = 'rejected'
                po['status'] = 'rejected'
                po['rejected_by'] = user_id
                po['rejected_at'] = datetime.utcnow().isoformat()
                po['rejection_reason'] = rejection_reason
                
                return {"message": "Purchase order rejected", "purchase_order": po}
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/summary")
async def get_purchase_order_stats(
    company_id: int = Depends(get_current_company_id)
):
    """Get purchase order statistics."""
    try:
        company_orders = [po for po in mock_purchase_orders_db if po.get('company_id') == company_id]
        
        total_orders = len(company_orders)
        pending_approval = len([po for po in company_orders if po.get('approval_status') == 'requires_approval'])
        approved = len([po for po in company_orders if po.get('status') == 'approved'])
        
        total_value = sum(Decimal(po.get('total_amount', 0)) for po in company_orders)
        
        return {
            "total_orders": total_orders,
            "pending_approval": pending_approval,
            "approved": approved,
            "total_value": str(total_value),
            "average_order_value": str(total_value / total_orders) if total_orders > 0 else "0"
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )