"""
Dashboard API endpoints for purchasing module.

Provides dashboard metrics, charts, and analytics for purchasing.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from decimal import Decimal
import random
import logging

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# Dependencies
def get_current_company_id() -> int:
    """Get current company ID from context."""
    return 1


@router.get("/metrics")
async def get_dashboard_metrics(
    company_id: int = Depends(get_current_company_id)
):
    """Get key purchasing metrics for dashboard."""
    try:
        # Import here to avoid circular dependency
        from purchasing_module.api.purchase_order_api import mock_purchase_orders_db
        from purchasing_module.api.supplier_api import mock_suppliers_db
        
        company_orders = [po for po in mock_purchase_orders_db if po.get('company_id') == company_id]
        company_suppliers = [s for s in mock_suppliers_db if s.get('company_id') == company_id]
        
        # Calculate metrics
        total_orders = len(company_orders)
        pending_approval = len([po for po in company_orders if po.get('approval_status') == 'requires_approval'])
        active_suppliers = len([s for s in company_suppliers if s.get('status') == 'active'])
        
        # Calculate total spend
        total_spend = sum(Decimal(po.get('total_amount', 0)) for po in company_orders)
        
        # Calculate this month's spend
        current_month = datetime.now().month
        month_orders = [
            po for po in company_orders 
            if po.get('order_date') and datetime.fromisoformat(po['order_date']).month == current_month
        ]
        month_spend = sum(Decimal(po.get('total_amount', 0)) for po in month_orders)
        
        return {
            "total_orders": total_orders,
            "pending_approval": pending_approval,
            "active_suppliers": active_suppliers,
            "total_spend": str(total_spend),
            "month_spend": str(month_spend),
            "average_order_value": str(total_spend / total_orders) if total_orders > 0 else "0",
            "top_category": "Office Supplies",  # Mock data
            "savings_ytd": "45,230"  # Mock data
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/spending-trend")
async def get_spending_trend(
    company_id: int = Depends(get_current_company_id)
):
    """Get spending trend data for charts."""
    try:
        # Generate mock data for last 6 months
        months = []
        spending = []
        
        for i in range(6, 0, -1):
            date = datetime.now() - timedelta(days=i*30)
            months.append(date.strftime("%B"))
            spending.append(random.randint(50000, 150000))
        
        return {
            "labels": months,
            "datasets": [{
                "label": "Monthly Spending",
                "data": spending,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)"
            }]
        }
        
    except Exception as e:
        logger.error(f"Error getting spending trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/supplier-distribution")
async def get_supplier_distribution(
    company_id: int = Depends(get_current_company_id)
):
    """Get supplier distribution by category."""
    try:
        categories = ["Technology", "Office Supplies", "Services", "Raw Materials", "Equipment"]
        values = [random.randint(5, 30) for _ in categories]
        
        return {
            "labels": categories,
            "datasets": [{
                "data": values,
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 206, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(153, 102, 255, 0.8)"
                ]
            }]
        }
        
    except Exception as e:
        logger.error(f"Error getting supplier distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent/orders")
async def get_recent_orders(
    limit: int = 5,
    company_id: int = Depends(get_current_company_id)
):
    """Get recent purchase orders."""
    try:
        from purchasing_module.api.purchase_order_api import mock_purchase_orders_db
        
        company_orders = [po for po in mock_purchase_orders_db if po.get('company_id') == company_id]
        
        # Sort by date (most recent first)
        company_orders.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        
        # Return limited list
        recent = company_orders[:limit]
        
        return {
            "orders": [
                {
                    "id": po['id'],
                    "po_number": po['po_number'],
                    "supplier": po.get('supplier_name'),
                    "amount": po['total_amount'],
                    "status": po['status'],
                    "date": po['order_date']
                }
                for po in recent
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting recent orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/top-suppliers")
async def get_top_suppliers_analytics(
    limit: int = 5,
    company_id: int = Depends(get_current_company_id)
):
    """Get top suppliers by spend."""
    try:
        from purchasing_module.api.supplier_api import mock_suppliers_db
        
        company_suppliers = [s for s in mock_suppliers_db if s.get('company_id') == company_id]
        
        # Sort by total spend (mock data)
        for supplier in company_suppliers:
            if not supplier.get('total_spend'):
                supplier['total_spend'] = str(random.randint(10000, 500000))
        
        company_suppliers.sort(key=lambda x: float(x.get('total_spend', 0)), reverse=True)
        
        top_suppliers = company_suppliers[:limit]
        
        return {
            "suppliers": [
                {
                    "id": s['id'],
                    "name": s['name'],
                    "spend": s['total_spend'],
                    "orders": s.get('total_orders', random.randint(5, 50)),
                    "rating": s.get('performance_rating', 5.0)
                }
                for s in top_suppliers
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting top suppliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-approvals/summary")
async def get_pending_approvals_summary(
    company_id: int = Depends(get_current_company_id)
):
    """Get summary of pending approvals."""
    try:
        from purchasing_module.api.purchase_order_api import mock_purchase_orders_db
        
        pending = [
            po for po in mock_purchase_orders_db 
            if po.get('company_id') == company_id and po.get('approval_status') == 'requires_approval'
        ]
        
        # Group by urgency (mock logic)
        urgent = len([po for po in pending if float(po.get('total_amount', 0)) > 10000])
        normal = len(pending) - urgent
        
        total_value = sum(Decimal(po.get('total_amount', 0)) for po in pending)
        
        return {
            "total_pending": len(pending),
            "urgent": urgent,
            "normal": normal,
            "total_value": str(total_value),
            "oldest_days": random.randint(1, 10)  # Mock data
        }
        
    except Exception as e:
        logger.error(f"Error getting pending approvals summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))