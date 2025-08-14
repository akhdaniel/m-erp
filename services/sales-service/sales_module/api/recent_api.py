"""
Recent Data API endpoints for Sales Dashboard.

Provides recent activity data for dashboard widgets.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from datetime import datetime, timedelta
import random
import logging

from sales_module.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/dashboard/recent", tags=["recent"])


# Dependencies
def get_dashboard_service() -> DashboardService:
    """Get dashboard service instance."""
    return DashboardService()


def get_current_company_id() -> int:
    """Get current company ID from authentication."""
    return 1


@router.get("/quotes", response_model=Dict[str, Any])
async def get_recent_quotes(
    limit: int = Query(5, ge=1, le=20, description="Number of quotes to return"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get recent quotes for dashboard widgets."""
    try:
        # Generate sample recent quotes
        customer_names = [
            "TechCorp Solutions", "Global Manufacturing", "Innovation Systems",
            "Metro Retail", "Digital Ventures", "Enterprise Holdings"
        ]
        
        quotes = []
        for i in range(min(limit, len(customer_names))):
            quote_date = datetime.now() - timedelta(days=random.randint(0, 7))
            total = random.uniform(5000, 25000)
            
            quotes.append({
                "id": 1000 + i,
                "quote_number": f"QT-2025-{1000 + i:04d}",
                "customer_name": customer_names[i],
                "total_amount": round(total, 2),
                "status": random.choice(["draft", "sent", "viewed"]),
                "quote_date": quote_date.date().isoformat(),
                "valid_until": (quote_date + timedelta(days=30)).date().isoformat(),
                "items_count": random.randint(1, 5)
            })
        
        return {
            "data": quotes,
            "total": len(quotes),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent quotes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent quotes"
        )


@router.get("/activities", response_model=Dict[str, Any])
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get recent sales activities for dashboard widgets."""
    try:
        activities = []
        activity_types = [
            ("quote_sent", "Quote sent to {customer}", "file-text", "blue"),
            ("order_received", "New order from {customer}", "shopping-bag", "green"),
            ("payment_received", "Payment received from {customer}", "dollar-sign", "green"),
            ("quote_viewed", "Quote viewed by {customer}", "eye", "purple"),
            ("follow_up", "Follow-up scheduled with {customer}", "calendar", "orange"),
            ("quote_accepted", "Quote accepted by {customer}", "check-circle", "green"),
            ("inventory_alert", "Low stock alert for {product}", "alert-triangle", "yellow")
        ]
        
        customer_names = ["TechCorp", "Global Inc", "Innovation Labs", "Metro Systems", "Digital Co"]
        product_names = ["Enterprise License", "Cloud Storage", "Security Suite"]
        
        for i in range(limit):
            activity_type = random.choice(activity_types)
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 48))
            
            if "product" in activity_type[1]:
                description = activity_type[1].format(product=random.choice(product_names))
            else:
                description = activity_type[1].format(customer=random.choice(customer_names))
            
            activities.append({
                "id": i + 1,
                "type": activity_type[0],
                "description": description,
                "icon": activity_type[2],
                "color": activity_type[3],
                "timestamp": timestamp.isoformat(),
                "user": random.choice(["John Smith", "Jane Doe", "System"])
            })
        
        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "data": activities,
            "total": len(activities),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent activities"
        )


@router.get("/notifications", response_model=Dict[str, Any])
async def get_recent_notifications(
    limit: int = Query(5, ge=1, le=20, description="Number of notifications to return"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    company_id: int = Depends(get_current_company_id)
):
    """Get recent notifications for dashboard widgets."""
    try:
        notifications = []
        notification_types = [
            ("low_stock", "Low stock alert", "{count} products below reorder point", "warning"),
            ("quote_expiring", "Quote expiring soon", "{count} quotes expiring this week", "info"),
            ("payment_overdue", "Payment overdue", "{count} invoices past due date", "error"),
            ("target_achieved", "Sales target achieved", "Monthly target exceeded by {percent}%", "success"),
            ("new_lead", "New lead assigned", "{count} new leads require attention", "info")
        ]
        
        for i in range(limit):
            notif_type = random.choice(notification_types)
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
            is_read = False if unread_only else random.choice([True, False])
            
            message = notif_type[2].format(
                count=random.randint(1, 10),
                percent=random.randint(5, 25)
            )
            
            notifications.append({
                "id": i + 1,
                "type": notif_type[0],
                "title": notif_type[1],
                "message": message,
                "severity": notif_type[3],
                "timestamp": timestamp.isoformat(),
                "is_read": is_read,
                "action_url": f"/sales/{notif_type[0].replace('_', '-')}"
            })
        
        # Filter unread if requested
        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]
        
        # Sort by timestamp (most recent first)
        notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "data": notifications[:limit],
            "total": len(notifications),
            "unread_count": sum(1 for n in notifications if not n["is_read"]),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent notifications"
        )