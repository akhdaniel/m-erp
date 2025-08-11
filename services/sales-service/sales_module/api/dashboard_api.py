"""
Dashboard API endpoints for Sales Service.

Provides comprehensive dashboard metrics, analytics, and recent activity data
that powers the sales dashboard widgets through the service-driven UI architecture.
"""

from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from decimal import Decimal
from datetime import datetime, timedelta, date
import logging

from sales_module.services.dashboard_service import DashboardService
from sales_module.framework.database import get_db_session
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


# Dependencies
def get_dashboard_service() -> DashboardService:
    """Get dashboard service instance."""
    return DashboardService()


def get_current_company_id() -> int:
    """Get current company ID from authentication."""
    # In production, would extract from JWT token or user context
    return 1


@router.get("/metrics", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    period: Optional[str] = Query("current_month", description="Time period: current_month, last_30_days, current_year"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get comprehensive dashboard metrics including quotes, orders, and revenue data.
    
    Returns key performance indicators for dashboard widgets including:
    - Active quotes count
    - Pending orders count 
    - Monthly/period revenue
    - Quote conversion rate
    - Inventory metrics
    - Customer metrics
    """
    try:
        # Get sales metrics
        sales_metrics = await dashboard_service.get_sales_metrics(company_id, period)
        
        # Get inventory metrics
        inventory_metrics = await dashboard_service.get_inventory_metrics()
        
        # Get customer metrics
        customer_metrics = await dashboard_service.get_customer_metrics()
        
        # Combine all metrics for dashboard
        metrics = {
            # Sales metrics
            "active_quotes": sales_metrics.get("active_quotes", 0),
            "pending_orders": sales_metrics.get("pending_orders", 0),
            "current_month_revenue": sales_metrics.get("total_revenue", 0),
            "revenue_growth": sales_metrics.get("revenue_growth_percentage", 0),
            "conversion_rate": sales_metrics.get("quote_to_order_rate", 0),
            "average_order_value": sales_metrics.get("average_order_value", 0),
            "orders_this_period": sales_metrics.get("orders_count", 0),
            
            # Inventory metrics
            "total_inventory_value": inventory_metrics.get("total_inventory_value", 0),
            "low_stock_count": inventory_metrics.get("low_stock_count", 0),
            "active_products": inventory_metrics.get("active_products", 0),
            
            # Customer metrics
            "total_customers": customer_metrics.get("total_customers", 0),
            "vip_customers": customer_metrics.get("vip_customers", 0),
            "new_customers_this_month": customer_metrics.get("new_customers_this_month", 0),
            
            # Period info
            "period": period,
            "start_date": sales_metrics.get("start_date"),
            "end_date": sales_metrics.get("end_date"),
            "last_updated": datetime.utcnow().isoformat()
        }

        return metrics
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard metrics"
        )


@router.get("/charts/revenue-trend", response_model=Dict[str, Any])
async def get_revenue_trend_data(
    period: Optional[str] = Query("last_30_days", description="Time period: last_7_days, last_30_days, last_90_days"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get revenue trend data for chart widgets.
    
    Returns time-series data showing revenue trends over the specified period
    formatted for chart consumption.
    """
    try:
        # Get revenue trend from dashboard service
        trend_data = await dashboard_service.get_revenue_trend(company_id, period)
        
        # Calculate granularity
        granularity = "weekly" if period == "last_90_days" else "daily"
        
        chart_data = {
            "data": trend_data,
            "period": period,
            "granularity": granularity,
            "total_revenue": sum(item["revenue"] for item in trend_data),
            "total_orders": sum(item["orders_count"] for item in trend_data),
            "chart_config": {
                "type": "line",
                "x_field": "date", 
                "y_field": "revenue",
                "title": f"Revenue Trend ({period.replace('_', ' ').title()})",
                "color": "#10B981"
            },
            "last_updated": datetime.utcnow().isoformat()
        }

        return chart_data
        
    except Exception as e:
        logger.error(f"Error getting revenue trend data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue trend data"
        )


@router.get("/charts/sales-pipeline", response_model=Dict[str, Any])
async def get_sales_pipeline_data(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get sales pipeline data for funnel chart widgets.
    
    Returns quote status distribution data formatted for funnel chart display.
    """
    try:
        # Get pipeline data from dashboard service
        pipeline_data = await dashboard_service.get_sales_pipeline(company_id)
        
        chart_data = {
            "data": pipeline_data["stages"],
            "total_pipeline_value": pipeline_data["total_pipeline_value"],
            "average_deal_size": pipeline_data["average_deal_size"],
            "win_rate": pipeline_data["win_rate"],
            "average_sales_cycle": pipeline_data["average_sales_cycle"],
            "chart_config": {
                "type": "funnel",
                "stages": [stage["stage"] for stage in pipeline_data["stages"]],
                "title": "Sales Pipeline",
                "value_field": "count",
                "label_field": "label"
            },
            "last_updated": datetime.utcnow().isoformat()
        }

        return chart_data
        
    except Exception as e:
        logger.error(f"Error getting sales pipeline data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sales pipeline data"
        )


@router.get("/recent/orders", response_model=Dict[str, Any])
async def get_recent_orders(
    limit: int = Query(10, ge=1, le=50, description="Number of recent orders to return"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get recent orders for list widgets.
    
    Returns the most recent orders with key fields for dashboard display.
    """
    try:
        # Get recent orders from service
        # Note: Return sample data as sales_orders table doesn't exist yet
        recent_orders = []
        
        # Generate sample recent orders data
        from datetime import datetime, timedelta
        for i in range(min(limit, 5)):
            order_date = datetime.now() - timedelta(days=i)
            recent_orders.append({
                "id": 1000 + i,
                "order_number": f"ORD-2025-{1000 + i:04d}",
                "customer_name": ["TechCorp Solutions", "Global Manufacturing", "Innovation Systems", "Metro Retail", "Digital Ventures"][i % 5],
                "total_amount": 5000.00 + (i * 1500),
                "status": ["pending", "confirmed", "processing", "shipped", "completed"][i % 5],
                "order_date": order_date.isoformat(),
                "sales_rep": "John Smith",
                "priority": "normal"
            })
        
        return {
            "data": recent_orders,
            "total_count": len(recent_orders),
            "config": {
                "title": "Recent Orders",
                "columns": ["order_number", "customer_name", "total_amount", "status", "order_date"],
                "link_pattern": "/sales/orders/{id}"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Original code to use when table exists:
        # from sales_module.models import SalesOrder
        # db = order_service.db_session
        # orders = db.query(SalesOrder).filter(
        #     SalesOrder.company_id == company_id,
        #     SalesOrder.is_active == True
        # ).order_by(SalesOrder.order_date.desc()).limit(limit).all()
        #
        # recent_orders = []
        # for order in orders:
        #     recent_orders.append({
        #         "id": order.id,
        #         "order_number": order.order_number,
        #         "customer_name": order.customer_name or "Unknown Customer",
        #         "total_amount": float(order.total_amount or 0),
        #         "status": order.status.value if order.status else "unknown",
        #         "order_date": order.order_date.isoformat() if order.order_date else None,
        #         "payment_status": getattr(order, 'payment_status', 'unpaid'),
        #         "priority": getattr(order, 'priority', 'normal')
        #     })
        # 
        # return {
        #     "data": recent_orders,
        #     "total_count": len(recent_orders),
        #     "config": {
        #         "title": "Recent Orders",
        #         "columns": ["order_number", "customer_name", "total_amount", "status", "order_date"],
        #         "link_pattern": "/sales/orders/{id}"
        #     },
        #     "last_updated": datetime.utcnow().isoformat()
        # }
        
    except Exception as e:
        logger.error(f"Error getting recent orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent orders"
        )


@router.get("/analytics/top-customers", response_model=Dict[str, Any])
async def get_top_customers(
    limit: int = Query(5, ge=1, le=20, description="Number of top customers to return"),
    period: Optional[str] = Query("current_month", description="Time period for analysis"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get top customers by revenue for table widgets.
    
    Returns customer performance data ranked by total revenue.
    """
    try:
        # Get top customers from dashboard service
        top_customers = await dashboard_service.get_top_customers(company_id, limit)
        
        return {
            "data": top_customers,
            "period": period,
            "total_customers": len(top_customers),
            "config": {
                "title": f"Top Customers ({period.replace('_', ' ').title()})",
                "columns": ["customer_name", "order_count", "total_revenue", "average_order_value"],
                "sortable": True
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting top customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve top customers data"
        )


# Health check for dashboard service
@router.get("/health")
async def dashboard_health():
    """Dashboard service health check."""
    return {
        "status": "healthy",
        "service": "sales-dashboard",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/dashboard/metrics",
            "/api/v1/dashboard/charts/revenue-trend",
            "/api/v1/dashboard/charts/sales-pipeline",
            "/api/v1/dashboard/recent/orders",
            "/api/v1/dashboard/analytics/top-customers"
        ]
    }