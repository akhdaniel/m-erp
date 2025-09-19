"""
Sales Transaction API endpoints for consolidated quotations and orders.

Provides REST API endpoints for sales transaction management including
CRUD operations, workflow management, approvals, and inventory integration.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status, Body
from fastapi.responses import JSONResponse
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging
import sys

from sales_module.models import SalesTransaction, SalesTransactionLineItem, SalesTransactionState
from sales_module.framework.database import get_db_session
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/transactions", tags=["transactions"])

# In-memory storage for demo purposes
mock_transactions_db = []
next_transaction_id = 1

# Dependencies
def get_current_user_id() -> int:
    """Get current user ID from authentication."""
    # In production, would extract from JWT token
    return 1

def get_current_company_id() -> int:
    """Get current company ID from authentication."""
    # In production, would extract from JWT token or user context
    return 1

# Helper function to filter transactions by state
def filter_transactions_by_state(transactions: List[Dict], states: List[str]) -> List[Dict]:
    """Filter transactions by state."""
    if not states:
        return transactions
    return [t for t in transactions if t.get('state') in states]

# Sales Transaction CRUD endpoints
@router.get("/", response_model=Dict)
@router.get("", response_model=Dict)
async def list_sales_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    state: Optional[str] = Query(None, description="Comma-separated list of states to filter by"),
    customer_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Search in title or transaction number"),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    List sales transactions with optional filtering.
    
    Returns a list of sales transactions with pagination and filtering options.
    """
    try:
        # Parse state filter
        states = state.split(',') if state else []
        
        # For demo purposes, return mock data
        filtered_transactions = filter_transactions_by_state(mock_transactions_db, states)
        
        # Apply customer filter
        if customer_id:
            filtered_transactions = [t for t in filtered_transactions if t.get('customer_id') == customer_id]
        
        # Apply search filter
        if search:
            filtered_transactions = [
                t for t in filtered_transactions 
                if search.lower() in (t.get('title', '') + t.get('transaction_number', '')).lower()
            ]
        
        # Apply sorting
        reverse = sort_order.lower() == 'desc'
        if sort_by in ['created_at', 'updated_at', 'total_amount']:
            filtered_transactions.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
        
        # Apply pagination
        total = len(filtered_transactions)
        paginated_transactions = filtered_transactions[skip:skip+limit]
        
        return {
            "data": paginated_transactions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing sales transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=Dict, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def create_sales_transaction(
    transaction_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create new sales transaction.
    
    Creates a new sales transaction with the provided information.
    """
    try:
        global next_transaction_id
        transaction_id = next_transaction_id
        next_transaction_id += 1
        
        # Create transaction response
        created_at = datetime.utcnow().isoformat()
        transaction_response = {
            "id": transaction_id,
            "company_id": company_id,
            "created_at": created_at,
            "updated_at": created_at,
            "created_by_user_id": user_id,
            "updated_by_user_id": user_id,
            "transaction_number": f'TXN-2025-{transaction_id:03d}',
            "title": transaction_data.get('title'),
            "description": transaction_data.get('description'),
            "state": "draft",
            "customer_id": transaction_data.get('customer_id'),
            "customer_name": f"Customer {transaction_data.get('customer_id', 'N/A')}",
            "total_amount": transaction_data.get('total_amount', 0.0),
            "subtotal": transaction_data.get('total_amount', 0.0),
            "tax_amount": 0.0,
            "discount_amount": 0.0,
            "currency_code": transaction_data.get('currency_code', 'USD'),
            "payment_terms_days": transaction_data.get('payment_terms_days', 30),
            "delivery_terms": transaction_data.get('delivery_terms', "Standard delivery terms"),
            "valid_until": transaction_data.get('valid_until', (datetime.utcnow().replace(microsecond=0) + timedelta(days=30)).isoformat())
        }
        
        # Add to mock database
        mock_transactions_db.append(transaction_response)
        
        return transaction_response
        
    except Exception as e:
        logger.error(f"Error creating sales transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{transaction_id}", response_model=Dict)
async def get_sales_transaction(
    transaction_id: int = Path(..., ge=1),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get sales transaction by ID.
    
    Returns detailed information about a specific sales transaction.
    """
    try:
        # Find transaction in mock database
        transaction = next((t for t in mock_transactions_db if t.get('id') == transaction_id), None)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        # Check company access
        if transaction.get('company_id') != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Enhance transaction data with additional fields needed for detail view
        enhanced_transaction = transaction.copy()
        
        # Add customer name (mock data for demo)
        if not enhanced_transaction.get('customer_name'):
            enhanced_transaction['customer_name'] = f"Customer {enhanced_transaction.get('customer_id', 'N/A')}"
        
        # Add financial fields if not present
        if not enhanced_transaction.get('subtotal'):
            enhanced_transaction['subtotal'] = enhanced_transaction.get('total_amount', 0.0)
        if not enhanced_transaction.get('tax_amount'):
            enhanced_transaction['tax_amount'] = 0.0
        if not enhanced_transaction.get('discount_amount'):
            enhanced_transaction['discount_amount'] = 0.0
            
        # Add terms fields if not present
        if not enhanced_transaction.get('payment_terms_days'):
            enhanced_transaction['payment_terms_days'] = 30
        if not enhanced_transaction.get('delivery_terms'):
            enhanced_transaction['delivery_terms'] = "Standard delivery terms"
        if not enhanced_transaction.get('valid_until'):
            # Set valid until to 30 days from created date
            created_at_str = enhanced_transaction.get('created_at', '')
            if created_at_str:
                try:
                    from datetime import datetime, timedelta
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    valid_until = created_at + timedelta(days=30)
                    enhanced_transaction['valid_until'] = valid_until.isoformat()
                except:
                    enhanced_transaction['valid_until'] = created_at_str
            else:
                enhanced_transaction['valid_until'] = enhanced_transaction.get('created_at', '')
        
        return enhanced_transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sales transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{transaction_id}", response_model=Dict)
async def update_sales_transaction(
    transaction_id: int = Path(..., ge=1),
    transaction_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Update sales transaction.
    
    Updates an existing sales transaction with the provided information.
    """
    try:
        # Find transaction in mock database
        transaction = next((t for t in mock_transactions_db if t.get('id') == transaction_id), None)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        # Check company access
        if transaction.get('company_id') != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Update transaction fields
        for key, value in transaction_data.items():
            if key not in ['id', 'company_id', 'created_at', 'created_by_user_id']:
                transaction[key] = value
                
        # Ensure required fields are present
        if 'customer_name' not in transaction:
            transaction['customer_name'] = f"Customer {transaction.get('customer_id', 'N/A')}"
        if 'subtotal' not in transaction:
            transaction['subtotal'] = transaction.get('total_amount', 0.0)
        if 'tax_amount' not in transaction:
            transaction['tax_amount'] = 0.0
        if 'discount_amount' not in transaction:
            transaction['discount_amount'] = 0.0
        if 'payment_terms_days' not in transaction:
            transaction['payment_terms_days'] = 30
        if 'delivery_terms' not in transaction:
            transaction['delivery_terms'] = "Standard delivery terms"
        if 'valid_until' not in transaction:
            # Set valid until to 30 days from created date if not present
            created_at_str = transaction.get('created_at', '')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    valid_until = created_at + timedelta(days=30)
                    transaction['valid_until'] = valid_until.isoformat()
                except:
                    transaction['valid_until'] = created_at_str
            else:
                transaction['valid_until'] = transaction.get('created_at', '')
                
        # Update timestamps
        transaction['updated_at'] = datetime.utcnow().isoformat()
        transaction['updated_by_user_id'] = user_id
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sales transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{transaction_id}", response_model=Dict)
async def delete_sales_transaction(
    transaction_id: int = Path(..., ge=1),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Delete sales transaction.
    
    Deletes an existing sales transaction.
    """
    try:
        # Find transaction in mock database
        transaction_index = next((i for i, t in enumerate(mock_transactions_db) if t.get('id') == transaction_id), None)
        
        if transaction_index is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        transaction = mock_transactions_db[transaction_index]
            
        # Check company access
        if transaction.get('company_id') != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Remove from mock database
        deleted_transaction = mock_transactions_db.pop(transaction_index)
        
        return {"message": "Transaction deleted successfully", "deleted_transaction": deleted_transaction}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sales transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Sales Transaction State Management endpoints
@router.post("/{transaction_id}/state/{new_state}", response_model=Dict)
async def change_transaction_state(
    transaction_id: int = Path(..., ge=1),
    new_state: str = Path(...),
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Change sales transaction state.
    
    Updates the state of a sales transaction and records the change.
    """
    try:
        # Validate state
        valid_states = [s.value for s in SalesTransactionState]
        if new_state not in valid_states:
            raise HTTPException(status_code=400, detail=f"Invalid state: {new_state}")
        
        # Find transaction in mock database
        transaction = next((t for t in mock_transactions_db if t.get('id') == transaction_id), None)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        # Check company access
        if transaction.get('company_id') != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Update state
        old_state = transaction.get('state')
        transaction['state'] = new_state
        transaction['updated_at'] = datetime.utcnow().isoformat()
        transaction['updated_by_user_id'] = user_id
        
        # Add state change log (in real implementation, this would be a separate table)
        if 'state_changes' not in transaction:
            transaction['state_changes'] = []
        transaction['state_changes'].append({
            'from_state': old_state,
            'to_state': new_state,
            'changed_at': datetime.utcnow().isoformat(),
            'changed_by_user_id': user_id,
            'notes': notes
        })
        
        return {
            "message": "Transaction state updated successfully",
            "transaction": transaction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing transaction state: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Sales Transaction Line Item endpoints
@router.get("/{transaction_id}/line-items", response_model=Dict)
async def list_transaction_line_items(
    transaction_id: int = Path(..., ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    List line items for a sales transaction.
    
    Returns line items associated with a specific sales transaction.
    """
    try:
        # Find transaction in mock database
        transaction = next((t for t in mock_transactions_db if t.get('id') == transaction_id), None)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        # Check company access
        if transaction.get('company_id') != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # For demo, return empty list
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing transaction line items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{transaction_id}/line-items", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def create_transaction_line_item(
    transaction_id: int = Path(..., ge=1),
    line_item_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create line item for a sales transaction.
    
    Adds a new line item to a sales transaction.
    """
    try:
        # Find transaction in mock database
        transaction = next((t for t in mock_transactions_db if t.get('id') == transaction_id), None)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        # Check company access
        if transaction.get('company_id') != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # For demo, return mock line item
        line_item_response = {
            "id": len(mock_transactions_db) + 1,
            "transaction_id": transaction_id,
            "line_number": line_item_data.get('line_number', 1),
            "item_name": line_item_data.get('item_name'),
            "quantity_ordered": line_item_data.get('quantity_ordered', 1),
            "unit_price": line_item_data.get('unit_price', 0.0),
            "line_total": line_item_data.get('line_total', 0.0)
        }
        
        return line_item_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction line item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Sales Transaction Statistics endpoints
@router.get("/stats", response_model=Dict)
async def get_transaction_statistics(
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get sales transaction statistics.
    
    Returns statistics about sales transactions including counts by state.
    """
    try:
        # For demo, return mock statistics
        quote_states = [
            'draft', 'quote_pending_approval', 'quote_approved', 'quote_sent', 
            'quote_accepted', 'quote_rejected', 'quote_expired'
        ]
        
        order_states = [
            'order_pending', 'order_confirmed', 'order_in_production', 
            'order_ready_to_ship', 'order_partially_shipped', 'order_shipped',
            'order_delivered', 'order_completed', 'order_cancelled', 'order_on_hold'
        ]
        
        # Count transactions by type
        quotes = [t for t in mock_transactions_db if t.get('state') in quote_states]
        orders = [t for t in mock_transactions_db if t.get('state') in order_states]
        
        return {
            "total_transactions": len(mock_transactions_db),
            "total_quotes": len(quotes),
            "total_orders": len(orders),
            "quotes_by_state": {state: len([t for t in quotes if t.get('state') == state]) for state in quote_states},
            "orders_by_state": {state: len([t for t in orders if t.get('state') == state]) for state in order_states}
        }
        
    except Exception as e:
        logger.error(f"Error getting transaction statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
