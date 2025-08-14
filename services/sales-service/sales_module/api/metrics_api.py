"""
Individual Metrics API endpoints for Sales Dashboard.

Provides granular metric endpoints for dashboard widgets that need single values.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from datetime import datetime, timedelta, date
import logging

from sales_module.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/dashboard/metrics", tags=["metrics"])


# Dependencies
def get_dashboard_service() -> DashboardService:
    """Get dashboard service instance."""
    return DashboardService()


def get_current_company_id() -> int:
    """Get current company ID from authentication."""
    # In production, would extract from JWT token or user context
    return 1


@router.get("/revenue", response_model=Dict[str, Any])
async def get_revenue_metric(
    period: Optional[str] = Query("current_month", description="Time period"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get revenue metric for dashboard widget."""
    try:
        sales_metrics = await dashboard_service.get_sales_metrics(company_id, period)
        
        return {
            "value": sales_metrics.get("total_revenue", 0),
            "label": "Monthly Revenue",
            "format": "currency",
            "trend": {
                "value": sales_metrics.get("revenue_growth_percentage", 0),
                "direction": "up" if sales_metrics.get("revenue_growth_percentage", 0) > 0 else "down",
                "label": f"{abs(sales_metrics.get('revenue_growth_percentage', 0)):.1f}% from last period"
            },
            "period": period,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting revenue metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue metric"
        )


@router.get("/quotes", response_model=Dict[str, Any])
async def get_quotes_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get active quotes metric for dashboard widget."""
    try:
        sales_metrics = await dashboard_service.get_sales_metrics(company_id)
        
        return {
            "value": sales_metrics.get("active_quotes", 0),
            "label": "Active Quotes",
            "format": "number",
            "subtitle": f"{sales_metrics.get('quotes_sent', 0)} sent this month",
            "trend": {
                "value": sales_metrics.get("quote_to_order_rate", 0),
                "label": f"{sales_metrics.get('quote_to_order_rate', 0):.1f}% conversion rate"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting quotes metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quotes metric"
        )


@router.get("/orders", response_model=Dict[str, Any])
async def get_orders_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get pending orders metric for dashboard widget."""
    try:
        sales_metrics = await dashboard_service.get_sales_metrics(company_id)
        
        return {
            "value": sales_metrics.get("pending_orders", 0),
            "label": "Pending Orders",
            "format": "number",
            "subtitle": f"{sales_metrics.get('orders_count', 0)} total this month",
            "trend": {
                "value": sales_metrics.get("average_order_value", 0),
                "label": f"${sales_metrics.get('average_order_value', 0):,.2f} avg value"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting orders metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders metric"
        )


@router.get("/conversion", response_model=Dict[str, Any])
async def get_conversion_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get conversion rate metric for dashboard widget."""
    try:
        sales_metrics = await dashboard_service.get_sales_metrics(company_id)
        
        return {
            "value": sales_metrics.get("quote_to_order_rate", 0),
            "label": "Conversion Rate",
            "format": "percentage",
            "subtitle": f"{sales_metrics.get('quotes_accepted', 0)} of {sales_metrics.get('quotes_sent', 0)} quotes converted",
            "trend": {
                "direction": "stable",
                "label": "vs last month"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting conversion metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversion metric"
        )


@router.get("/inventory", response_model=Dict[str, Any])
async def get_inventory_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get inventory value metric for dashboard widget."""
    try:
        inventory_metrics = await dashboard_service.get_inventory_metrics()
        
        return {
            "value": inventory_metrics.get("total_inventory_value", 0),
            "label": "Inventory Value",
            "format": "currency",
            "subtitle": f"{inventory_metrics.get('active_products', 0)} active products",
            "alerts": {
                "count": inventory_metrics.get("low_stock_count", 0),
                "label": f"{inventory_metrics.get('low_stock_count', 0)} low stock items",
                "severity": "warning" if inventory_metrics.get("low_stock_count", 0) > 10 else "info"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting inventory metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve inventory metric"
        )


@router.get("/customers", response_model=Dict[str, Any])
async def get_customers_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get customers metric for dashboard widget."""
    try:
        customer_metrics = await dashboard_service.get_customer_metrics()
        
        return {
            "value": customer_metrics.get("total_customers", 0),
            "label": "Total Customers",
            "format": "number",
            "subtitle": f"{customer_metrics.get('active_customers', 0)} active",
            "highlights": [
                {
                    "value": customer_metrics.get("vip_customers", 0),
                    "label": "VIP customers",
                    "icon": "star"
                },
                {
                    "value": customer_metrics.get("new_customers_this_month", 0),
                    "label": "new this month",
                    "icon": "plus"
                }
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting customers metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customers metric"
        )


@router.get("/sales-cycle", response_model=Dict[str, Any])
async def get_sales_cycle_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get average sales cycle metric for dashboard widget."""
    try:
        sales_metrics = await dashboard_service.get_sales_metrics(company_id)
        
        return {
            "value": sales_metrics.get("average_days_to_close", 18),
            "label": "Avg Sales Cycle",
            "format": "days",
            "subtitle": "from lead to close",
            "trend": {
                "direction": "down",
                "value": -2,
                "label": "2 days faster than last month"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sales cycle metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sales cycle metric"
        )


@router.get("/pipeline-value", response_model=Dict[str, Any])
async def get_pipeline_value_metric(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get total pipeline value metric for dashboard widget."""
    try:
        pipeline_data = await dashboard_service.get_sales_pipeline(company_id)
        
        return {
            "value": pipeline_data.get("total_pipeline_value", 0),
            "label": "Pipeline Value",
            "format": "currency",
            "subtitle": f"{pipeline_data.get('stages', [{}])[0].get('count', 0)} opportunities",
            "breakdown": [
                {
                    "stage": stage["label"],
                    "value": stage["value"],
                    "count": stage["count"]
                }
                for stage in pipeline_data.get("stages", [])[:3]  # Top 3 stages
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting pipeline value metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pipeline value metric"
        )