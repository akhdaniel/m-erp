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
import httpx

from sales_module.models import SalesTransaction, SalesTransactionLineItem, SalesTransactionState
from sales_module.framework.database import get_db_session
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

logger = logging.getLogger('uvicorn')

# Create API router
router = APIRouter(prefix="/transactions", tags=["transactions"])

# Dependencies
def get_current_user_id() -> int:
    """Get current user ID from authentication."""
    # In production, would extract from JWT token
    return 1

def get_current_company_id() -> int:
    """Get current company ID from authentication."""
    # In production, would extract from JWT token or user context
    return 1

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
        # Build query
        query = db.query(SalesTransaction).filter(SalesTransaction.company_id == company_id)
        
        # Apply state filter
        if state:
            states = state.split(',')
            state_enums = []
            for s in states:
                try:
                    # Try to get enum by value (lowercase string)
                    state_enums.append(SalesTransactionState(s))
                except ValueError:
                    # If that fails, try to find enum by iterating through values
                    for state_enum in SalesTransactionState:
                        if state_enum.value == s.lower():
                            state_enums.append(state_enum)
                            break
            if state_enums:
                query = query.filter(SalesTransaction.state.in_(state_enums))
        
        # Apply customer filter
        if customer_id:
            query = query.filter(SalesTransaction.customer_id == customer_id)
        
        # Apply search filter
        if search:
            search_filter = or_(
                SalesTransaction.title.ilike(f"%{search}%"),
                SalesTransaction.transaction_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply sorting
        if sort_by == "created_at":
            query = query.order_by(SalesTransaction.created_at.desc() if sort_order.lower() == 'desc' else SalesTransaction.created_at.asc())
        elif sort_by == "updated_at":
            query = query.order_by(SalesTransaction.updated_at.desc() if sort_order.lower() == 'desc' else SalesTransaction.updated_at.asc())
        elif sort_by == "total_amount":
            query = query.order_by(SalesTransaction.total_amount.desc() if sort_order.lower() == 'desc' else SalesTransaction.total_amount.asc())
        else:
            query = query.order_by(SalesTransaction.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        transactions = query.offset(skip).limit(limit).all()
        
        # Convert to dictionary format
        transaction_data = [transaction.to_dict() for transaction in transactions]
        
        return {
            "data": transaction_data,
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
        logger.info(f"transaction_data={transaction_data}")
        # Set default values
        if 'transaction_number' not in transaction_data or not transaction_data['transaction_number']:
            # Generate transaction number
            import time
            timestamp = int(time.time())
            transaction_data['transaction_number'] = f"TXN{timestamp:08d}"
        
        if 'state' not in transaction_data:
            transaction_data['state'] = SalesTransactionState.DRAFT.value
        
        if 'valid_from' not in transaction_data:
            transaction_data['valid_from'] = datetime.utcnow()
        
        if 'valid_until' not in transaction_data:
            transaction_data['valid_until'] = datetime.utcnow() + timedelta(days=30)
        
        if 'payment_terms_days' not in transaction_data:
            transaction_data['payment_terms_days'] = 30
        
        if 'currency_code' not in transaction_data:
            transaction_data['currency_code'] = 'USD'
        
        if 'subtotal' not in transaction_data:
            transaction_data['subtotal'] = transaction_data.get('total_amount', 0.0)
        
        if 'tax_amount' not in transaction_data:
            transaction_data['tax_amount'] = 0.0
            
        if 'discount_amount' not in transaction_data:
            transaction_data['discount_amount'] = 0.0
            
        if 'prepared_by_user_id' not in transaction_data:
            transaction_data['prepared_by_user_id'] = user_id
        
        # Set company info
        transaction_data['company_id'] = company_id
        
        # Debug logging
        logger.info(f"Transaction data: {transaction_data}")
        if 'state' in transaction_data:
            logger.info(f"State value: {transaction_data['state']}, type: {type(transaction_data['state'])}")
            # Convert state string to enum if needed
            if isinstance(transaction_data['state'], str):
                logger.info(f"Converting state string: {transaction_data['state']}")
                try:
                    # Try to get enum by value (lowercase string)
                    state_enum = SalesTransactionState(transaction_data['state'])
                    logger.info(f"Got enum by value: {state_enum}, value: {state_enum.value}")
                    # Use the enum value (lowercase) instead of the enum itself
                    transaction_data['state'] = state_enum.value
                    logger.info(f"Set state to enum value: {transaction_data['state']}")
                except ValueError:
                    # If that fails, try to find enum by iterating through values
                    logger.info("ValueError, trying iteration")
                    for state_enum in SalesTransactionState:
                        if state_enum.value == transaction_data['state'].lower():
                            logger.info(f"Found enum by iteration: {state_enum}, value: {state_enum.value}")
                            # Use the enum value (lowercase) instead of the enum itself
                            transaction_data['state'] = state_enum.value
                            logger.info(f"Set state to enum value: {transaction_data['state']}")
                            break
                    else:
                        # If still not found, use default
                        logger.info("Using default state")
                        transaction_data['state'] = SalesTransactionState.DRAFT.value
                        logger.info(f"Set state to default value: {transaction_data['state']}")
        
        # Create transaction
        transaction = SalesTransaction(**transaction_data)
        logger.info(f"Transaction state after creation: {transaction.state}, type: {type(transaction.state)}")
        logger.info(f"Transaction state value: {transaction.state.value if hasattr(transaction.state, 'value') else 'no value attr'}")
        logger.info(f"Final transaction_data state: {transaction_data['state']}")
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction.to_dict()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales transaction: {e}", exc_info=True)
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
        # Fetch transaction from database with line items using eager loading
        transaction = db.query(SalesTransaction).options(joinedload(SalesTransaction.line_items)).filter(
            SalesTransaction.id == transaction_id,
            SalesTransaction.company_id == company_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Convert transaction to dictionary - this should already include line items
        transaction_data = transaction.to_dict()
        
        # Ensure line items keys exist in the response
        if 'line_items' not in transaction_data:
            transaction_data['line_items'] = []
        if 'items' not in transaction_data:
            transaction_data['items'] = []
        
        # Fetch customer information from partner service
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Use the Kong API gateway endpoint for the partner service
                partner_url = f"http://kong:8000/api/v1/base/partners/{transaction.customer_id}"
                logger.info(f"Fetching customer data from: {partner_url}")
                response = await client.get(partner_url)
                logger.info(f"Customer API response status: {response.status_code}")
                if response.status_code == 200:
                    partner_data = response.json()
                    logger.info(f"Customer data fetched: {partner_data.get('name', 'Unknown')}")
                    # Add customer name to transaction data for Autocomplete component
                    transaction_data["customer_name"] = partner_data.get("name", "")
                else:
                    logger.warning(f"Failed to fetch customer data, status code: {response.status_code}")
                    transaction_data["customer_name"] = ""
        except Exception as customer_error:
            logger.warning(f"Failed to fetch customer data for transaction {transaction_id}: {customer_error}")
            # Even if we can't fetch customer data, we still return the transaction
            transaction_data["customer_name"] = ""
        
        return transaction_data
        
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

        # logger.info(f"transaction_data={transaction_data}")
        # Fetch transaction from database
        transaction = db.query(SalesTransaction).filter(
            SalesTransaction.id == transaction_id,
            SalesTransaction.company_id == company_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Update transaction fields
        for key, value in transaction_data.items():
            if hasattr(transaction, key) and key not in ['id', 'company_id', 'created_at', 'created_by_user_id']:
                setattr(transaction, key, value)
        
        # Update timestamps and user info
        transaction.updated_at = datetime.utcnow()
        transaction.updated_by_user_id = user_id
        
        db.commit()
        db.refresh(transaction)
        
        return transaction.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
        # Fetch transaction from database
        transaction = db.query(SalesTransaction).filter(
            SalesTransaction.id == transaction_id,
            SalesTransaction.company_id == company_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Delete transaction
        db.delete(transaction)
        db.commit()
        
        return {"message": "Transaction deleted successfully", "deleted_transaction": transaction.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
        try:
            state_enum = SalesTransactionState(new_state)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid state: {new_state}")
        
        # Fetch transaction from database
        transaction = db.query(SalesTransaction).filter(
            SalesTransaction.id == transaction_id,
            SalesTransaction.company_id == company_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Store old state
        old_state = transaction.state
        
        # Update state
        transaction.state = state_enum
        transaction.updated_at = datetime.utcnow()
        transaction.updated_by_user_id = user_id
        
        # In a real implementation, we would log this to a separate state change table
        # For now, we'll just update the transaction
        
        db.commit()
        db.refresh(transaction)
        
        return {
            "message": "Transaction state updated successfully",
            "transaction": transaction.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
        # Verify transaction exists and belongs to company
        transaction = db.query(SalesTransaction).filter(
            SalesTransaction.id == transaction_id,
            SalesTransaction.company_id == company_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Fetch line items
        query = db.query(SalesTransactionLineItem).filter(
            SalesTransactionLineItem.transaction_id == transaction_id,
            SalesTransactionLineItem.company_id == company_id
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        line_items = query.offset(skip).limit(limit).all()
        
        # Convert to dictionary format
        line_item_data = [item.to_dict() for item in line_items]
        
        return {
            "items": line_item_data,
            "total": total,
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
        # Verify transaction exists and belongs to company
        transaction = db.query(SalesTransaction).filter(
            SalesTransaction.id == transaction_id,
            SalesTransaction.company_id == company_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Set transaction and company info
        line_item_data['transaction_id'] = transaction_id
        line_item_data['company_id'] = company_id
        
        # Set default values for required fields if not provided
        if 'discount_amount' not in line_item_data:
            line_item_data['discount_amount'] = 0.0
        if 'tax_percentage' not in line_item_data:
            line_item_data['tax_percentage'] = 0.0
        if 'unit_of_measure' not in line_item_data:
            line_item_data['unit_of_measure'] = 'each'
        if 'quantity_shipped' not in line_item_data:
            line_item_data['quantity_shipped'] = 0.0
        if 'quantity_cancelled' not in line_item_data:
            line_item_data['quantity_cancelled'] = 0.0
        if 'quantity_backordered' not in line_item_data:
            line_item_data['quantity_backordered'] = 0.0
        if 'reserved_quantity' not in line_item_data:
            line_item_data['reserved_quantity'] = 0.0
        if 'allocated_quantity' not in line_item_data:
            line_item_data['allocated_quantity'] = 0.0
        if 'is_backordered' not in line_item_data:
            line_item_data['is_backordered'] = False
        if 'is_dropship' not in line_item_data:
            line_item_data['is_dropship'] = False
        if 'requires_special_handling' not in line_item_data:
            line_item_data['requires_special_handling'] = False
        if 'is_active' not in line_item_data:
            line_item_data['is_active'] = True
        
        # Set line number if not provided
        if 'line_number' not in line_item_data:
            # Get next line number
            max_line_number = db.query(
                SalesTransactionLineItem.line_number
            ).filter(
                SalesTransactionLineItem.transaction_id == transaction_id
            ).order_by(SalesTransactionLineItem.line_number.desc()).first()
            
            line_item_data['line_number'] = (max_line_number[0] + 1) if max_line_number else 1
        
        # Create line item
        line_item = SalesTransactionLineItem(**line_item_data)
        # Calculate line total and other computed fields
        line_item.calculate_line_total()
        db.add(line_item)
        db.commit()
        db.refresh(line_item)
        
        return line_item.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
        # Get total transactions
        total_transactions = db.query(SalesTransaction).filter(
            SalesTransaction.company_id == company_id
        ).count()
        
        # Count quotes (quotation states)
        quote_states = [
            SalesTransactionState.DRAFT.value,
            SalesTransactionState.QUOTE_PENDING_APPROVAL.value,
            SalesTransactionState.QUOTE_APPROVED.value,
            SalesTransactionState.QUOTE_SENT.value,
            SalesTransactionState.QUOTE_ACCEPTED.value,
            SalesTransactionState.QUOTE_REJECTED.value,
            SalesTransactionState.QUOTE_EXPIRED.value
        ]
        
        total_quotes = db.query(SalesTransaction).filter(
            SalesTransaction.company_id == company_id,
            SalesTransaction.state.in_(quote_states)
        ).count()
        
        # Count orders (order states)
        order_states = [
            SalesTransactionState.ORDER_PENDING.value,
            SalesTransactionState.ORDER_CONFIRMED.value,
            SalesTransactionState.ORDER_IN_PRODUCTION.value,
            SalesTransactionState.ORDER_READY_TO_SHIP.value,
            SalesTransactionState.ORDER_PARTIALLY_SHIPPED.value,
            SalesTransactionState.ORDER_SHIPPED.value,
            SalesTransactionState.ORDER_DELIVERED.value,
            SalesTransactionState.ORDER_COMPLETED.value,
            SalesTransactionState.ORDER_CANCELLED.value,
            SalesTransactionState.ORDER_ON_HOLD.value
        ]
        
        total_orders = db.query(SalesTransaction).filter(
            SalesTransaction.company_id == company_id,
            SalesTransaction.state.in_(order_states)
        ).count()
        
        # Get counts by state
        quotes_by_state = {}
        for state in quote_states:
            count = db.query(SalesTransaction).filter(
                SalesTransaction.company_id == company_id,
                SalesTransaction.state == state
            ).count()
            quotes_by_state[state.value] = count
        
        orders_by_state = {}
        for state in order_states:
            count = db.query(SalesTransaction).filter(
                SalesTransaction.company_id == company_id,
                SalesTransaction.state == state
            ).count()
            orders_by_state[state.value] = count
        
        return {
            "total_transactions": total_transactions,
            "total_quotes": total_quotes,
            "total_orders": total_orders,
            "quotes_by_state": quotes_by_state,
            "orders_by_state": orders_by_state
        }
        
    except Exception as e:
        logger.error(f"Error getting transaction statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
