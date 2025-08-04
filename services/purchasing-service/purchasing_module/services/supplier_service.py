"""
Supplier Service for managing supplier relationships and performance tracking.

This service integrates with the Partner model from company-partner-service
and adds purchasing-specific functionality for supplier management.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from purchasing_module.models.supplier_performance import (
    SupplierPerformance, 
    PerformanceMetric, 
    PerformanceRating,
    PerformanceMetricType
)

logger = logging.getLogger(__name__)


class SupplierService:
    """
    Service class for Supplier management and performance tracking.
    
    Integrates with the Partner management system to provide
    purchasing-specific supplier functionality.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the Supplier Service.
        
        Args:
            db_session: Database session (in production, injected via DI)
        """
        self.db_session = db_session
    
    def validate_supplier(self, supplier_id: int, company_id: int) -> bool:
        """
        Validate that a supplier exists and is active for the company.
        
        Args:
            supplier_id: ID of the supplier (Partner)
            company_id: Company ID for data isolation
            
        Returns:
            bool: True if supplier is valid and active
        """
        try:
            # In production, this would query the Partner model from company-partner-service
            # For now, simulate validation
            
            # Mock validation - in production would be:
            # partner = self.db_session.query(Partner).filter(
            #     Partner.id == supplier_id,
            #     Partner.company_id == company_id,
            #     Partner.is_supplier == True,
            #     Partner.is_active == True
            # ).first()
            # return partner is not None
            
            logger.info(f"Validating supplier {supplier_id} for company {company_id}")
            
            # Mock validation logic
            if supplier_id > 0 and company_id > 0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to validate supplier: {e}")
            return False
    
    def get_supplier_info(self, supplier_id: int, company_id: int) -> Optional[Dict[str, Any]]:
        """
        Get supplier information from the Partner system.
        
        Args:
            supplier_id: ID of the supplier
            company_id: Company ID for data isolation
            
        Returns:
            dict: Supplier information or None if not found
        """
        try:
            # In production, would query Partner model
            # For now, return mock data
            
            if not self.validate_supplier(supplier_id, company_id):
                return None
            
            # Mock supplier data
            return {
                "id": supplier_id,
                "name": f"Supplier {supplier_id}",
                "code": f"SUP{supplier_id:03d}",
                "email": f"supplier{supplier_id}@example.com",
                "phone": f"+1-555-{supplier_id:04d}",
                "address": {
                    "street": f"{supplier_id}00 Supplier Street",
                    "city": "Supply City",
                    "state": "CA",
                    "zip_code": f"{90000 + supplier_id}",
                    "country": "US"
                },
                "contact_person": f"Contact Person {supplier_id}",
                "payment_terms": "Net 30",
                "currency_code": "USD",
                "tax_id": f"TAX{supplier_id:06d}",
                "is_active": True,
                "is_supplier": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get supplier info: {e}")
            return None
    
    def get_active_suppliers(
        self,
        company_id: int,
        search_term: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get list of active suppliers for a company.
        
        Args:
            company_id: Company ID for data isolation
            search_term: Optional search term for filtering
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List[dict]: List of active suppliers
        """
        try:
            # In production, would query Partner model with filters
            # For now, return mock data
            
            mock_suppliers = []
            for i in range(1, 11):  # Generate 10 mock suppliers
                supplier = {
                    "id": i,
                    "name": f"Supplier {i}",
                    "code": f"SUP{i:03d}",
                    "email": f"supplier{i}@example.com",
                    "phone": f"+1-555-{i:04d}",
                    "contact_person": f"Contact Person {i}",
                    "payment_terms": "Net 30",
                    "is_active": True,
                    "last_order_date": (datetime.utcnow() - timedelta(days=i*5)).isoformat(),
                    "total_orders": i * 10,
                    "total_value": i * 5000.00
                }
                
                # Apply search filter if provided
                if search_term:
                    if search_term.lower() not in supplier["name"].lower():
                        continue
                
                mock_suppliers.append(supplier)
            
            # Apply pagination
            return mock_suppliers[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to get active suppliers: {e}")
            return []
    
    def create_performance_evaluation(
        self,
        supplier_id: int,
        company_id: int,
        evaluation_period_start: datetime,
        evaluation_period_end: datetime,
        evaluator_user_id: int
    ) -> Optional[SupplierPerformance]:
        """
        Create a new supplier performance evaluation.
        
        Args:
            supplier_id: ID of the supplier
            company_id: Company ID for data isolation
            evaluation_period_start: Start of evaluation period
            evaluation_period_end: End of evaluation period
            evaluator_user_id: ID of user creating evaluation
            
        Returns:
            SupplierPerformance: Created performance record or None if failed
        """
        try:
            # Validate supplier
            if not self.validate_supplier(supplier_id, company_id):
                logger.error(f"Invalid supplier {supplier_id} for company {company_id}")
                return None
            
            # Create performance record
            performance = SupplierPerformance(
                company_id=company_id,
                supplier_id=supplier_id,
                evaluation_period_start=evaluation_period_start,
                evaluation_period_end=evaluation_period_end,
                evaluator_user_id=evaluator_user_id
            )
            
            # Collect performance data for the period
            self._collect_performance_data(performance)
            
            # Save performance record
            performance.save(self.db_session, evaluator_user_id)
            
            logger.info(f"Created performance evaluation for supplier {supplier_id}")
            
            # Publish event
            performance.publish_event("supplier_performance.created", {
                "supplier_id": supplier_id,
                "evaluation_period": {
                    "start": evaluation_period_start.isoformat(),
                    "end": evaluation_period_end.isoformat()
                },
                "evaluator_user_id": evaluator_user_id
            })
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to create performance evaluation: {e}")
            return None
    
    def _collect_performance_data(self, performance: SupplierPerformance) -> None:
        """
        Collect performance data from purchase orders and deliveries.
        
        Args:
            performance: Performance record to populate
        """
        try:
            # In production, would query purchase orders and delivery data
            # For now, generate mock performance data
            
            # Mock performance data based on supplier_id
            supplier_id = performance.supplier_id
            
            # Generate realistic performance metrics
            base_performance = 0.7 + (supplier_id % 5) * 0.06  # 70-94% base performance
            
            # Order metrics
            performance.total_orders = 20 + (supplier_id % 10) * 5
            performance.total_value = Decimal(str(5000 + supplier_id * 1000))
            
            # Delivery metrics
            total_deliveries = performance.total_orders
            on_time_rate = base_performance + 0.05
            performance.on_time_deliveries = int(total_deliveries * on_time_rate)
            performance.late_deliveries = total_deliveries - performance.on_time_deliveries
            performance.average_delivery_days = Decimal(str(7 + (supplier_id % 5)))
            
            # Quality metrics
            performance.quality_issues_count = max(0, int(performance.total_orders * (0.05 - base_performance * 0.04)))
            performance.return_rate_percentage = Decimal(str(max(0, 3.0 - base_performance * 2.5)))
            
            # Price metrics
            performance.price_variance_percentage = Decimal(str((supplier_id % 3 - 1) * 2.5))  # -2.5% to +2.5%
            performance.cost_savings_amount = Decimal(str(max(0, performance.total_value * 0.02)))
            
            # Communication metrics
            performance.response_time_hours = Decimal(str(4 + (supplier_id % 3) * 2))
            
            # Compliance metrics
            performance.compliance_issues_count = max(0, int(performance.total_orders * 0.02))
            performance.documentation_complete_percentage = Decimal(str(95 + (supplier_id % 5)))
            
            # Add performance data and auto-calculate ratings
            performance.add_performance_data(
                orders_count=performance.total_orders,
                orders_value=performance.total_value,
                on_time_count=performance.on_time_deliveries,
                late_count=performance.late_deliveries,
                quality_issues=performance.quality_issues_count,
                return_rate=float(performance.return_rate_percentage)
            )
            
            # Set additional ratings based on other metrics
            self._assign_additional_ratings(performance, base_performance)
            
            logger.info(f"Collected performance data for supplier {supplier_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect performance data: {e}")
    
    def _assign_additional_ratings(self, performance: SupplierPerformance, base_performance: float) -> None:
        """
        Assign ratings for price, communication, and compliance.
        
        Args:
            performance: Performance record to update
            base_performance: Base performance factor (0.7-0.94)
        """
        # Price rating based on variance and savings
        price_variance = float(performance.price_variance_percentage or 0)
        if price_variance <= -2.0:  # Good savings
            performance.price_rating = PerformanceRating.EXCELLENT
        elif price_variance <= 0:
            performance.price_rating = PerformanceRating.GOOD
        elif price_variance <= 2.0:
            performance.price_rating = PerformanceRating.SATISFACTORY
        elif price_variance <= 5.0:
            performance.price_rating = PerformanceRating.NEEDS_IMPROVEMENT
        else:
            performance.price_rating = PerformanceRating.POOR
        
        # Communication rating based on response time
        response_hours = float(performance.response_time_hours or 24)
        if response_hours <= 4:
            performance.communication_rating = PerformanceRating.EXCELLENT
        elif response_hours <= 8:
            performance.communication_rating = PerformanceRating.GOOD
        elif response_hours <= 24:
            performance.communication_rating = PerformanceRating.SATISFACTORY
        elif response_hours <= 48:
            performance.communication_rating = PerformanceRating.NEEDS_IMPROVEMENT
        else:
            performance.communication_rating = PerformanceRating.POOR
        
        # Compliance rating based on issues and documentation
        compliance_score = base_performance
        if performance.compliance_issues_count > 0:
            compliance_score -= 0.1
        if float(performance.documentation_complete_percentage) < 95:
            compliance_score -= 0.1
        
        if compliance_score >= 0.9:
            performance.compliance_rating = PerformanceRating.EXCELLENT
        elif compliance_score >= 0.8:
            performance.compliance_rating = PerformanceRating.GOOD
        elif compliance_score >= 0.7:
            performance.compliance_rating = PerformanceRating.SATISFACTORY
        elif compliance_score >= 0.6:
            performance.compliance_rating = PerformanceRating.NEEDS_IMPROVEMENT
        else:
            performance.compliance_rating = PerformanceRating.POOR
    
    def finalize_performance_evaluation(
        self,
        performance_id: int,
        evaluator_user_id: int,
        evaluation_notes: Optional[str] = None,
        improvement_areas: Optional[List[str]] = None,
        strengths: Optional[List[str]] = None
    ) -> bool:
        """
        Finalize a supplier performance evaluation.
        
        Args:
            performance_id: ID of performance record
            evaluator_user_id: ID of user finalizing evaluation
            evaluation_notes: Optional evaluation notes
            improvement_areas: List of areas needing improvement
            strengths: List of supplier strengths
            
        Returns:
            bool: True if finalized successfully
        """
        try:
            # In production, would load from database
            performance = self._get_mock_performance_record(performance_id)
            
            if not performance:
                logger.error(f"Performance record {performance_id} not found")
                return False
            
            # Set improvement areas and strengths
            if improvement_areas:
                performance.improvement_areas = improvement_areas
            
            if strengths:
                performance.strengths = strengths
            
            # Finalize evaluation
            performance.finalize_evaluation(evaluator_user_id, evaluation_notes)
            
            # Save changes
            performance.save(self.db_session, evaluator_user_id)
            
            # Publish finalization event
            performance.publish_event("supplier_performance.finalized", {
                "performance_id": performance_id,
                "supplier_id": performance.supplier_id,
                "overall_rating": performance.overall_rating.value if performance.overall_rating else None,
                "overall_score": float(performance.overall_score) if performance.overall_score else None,
                "recommended_for_future": performance.recommended_for_future
            })
            
            logger.info(f"Finalized performance evaluation {performance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to finalize performance evaluation: {e}")
            return False
    
    def get_supplier_performance_history(
        self,
        supplier_id: int,
        company_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get performance history for a supplier.
        
        Args:
            supplier_id: ID of the supplier
            company_id: Company ID for data isolation
            limit: Maximum number of records to return
            
        Returns:
            List[dict]: List of performance records
        """
        try:
            # In production, would query SupplierPerformance table
            # For now, return mock data
            
            performance_history = []
            for i in range(1, min(limit + 1, 6)):  # Generate up to 5 mock records
                period_start = datetime.utcnow() - timedelta(days=i * 90)  # Quarterly evaluations
                period_end = period_start + timedelta(days=90)
                
                # Generate performance based on trend (improving over time)
                base_score = 3.0 + (5 - i) * 0.3  # Older records have lower scores
                
                performance_history.append({
                    "id": i,
                    "evaluation_period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    },
                    "overall_rating": self._score_to_rating(base_score).value,
                    "overall_score": round(base_score, 2),
                    "total_orders": 20 + i * 5,
                    "total_value": 5000.00 + i * 1000,
                    "on_time_delivery_percentage": 75.0 + i * 4,
                    "quality_issues_count": max(0, 5 - i),
                    "return_rate_percentage": max(0.5, 4.0 - i * 0.5),
                    "recommended_for_future": base_score >= 3.0,
                    "evaluation_date": (period_end + timedelta(days=7)).isoformat()
                })
            
            return performance_history
            
        except Exception as e:
            logger.error(f"Failed to get supplier performance history: {e}")
            return []
    
    def _score_to_rating(self, score: float) -> PerformanceRating:
        """Convert numeric score to performance rating."""
        if score >= 4.5:
            return PerformanceRating.EXCELLENT
        elif score >= 3.5:
            return PerformanceRating.GOOD
        elif score >= 2.5:
            return PerformanceRating.SATISFACTORY
        elif score >= 1.5:
            return PerformanceRating.NEEDS_IMPROVEMENT
        else:
            return PerformanceRating.POOR
    
    def get_top_suppliers(
        self,
        company_id: int,
        metric: str = "overall_score",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top-performing suppliers based on specified metric.
        
        Args:
            company_id: Company ID for data isolation
            metric: Metric to rank by (overall_score, total_value, on_time_percentage)
            limit: Maximum number of suppliers to return
            
        Returns:
            List[dict]: List of top suppliers with performance data
        """
        try:
            # In production, would query database with ranking
            # For now, return mock data
            
            top_suppliers = []
            for i in range(1, min(limit + 1, 11)):
                # Generate mock supplier performance
                base_performance = 0.95 - (i - 1) * 0.05  # Decreasing performance ranking
                
                supplier = {
                    "supplier_id": i,
                    "supplier_name": f"Top Supplier {i}",
                    "latest_performance": {
                        "overall_score": round(4.5 - (i - 1) * 0.3, 2),
                        "overall_rating": self._score_to_rating(4.5 - (i - 1) * 0.3).value,
                        "total_orders": 100 - i * 5,
                        "total_value": 50000.00 - i * 2000,
                        "on_time_delivery_percentage": round(base_performance * 100, 1),
                        "quality_issues_count": i - 1,
                        "return_rate_percentage": round((i - 1) * 0.5, 1)
                    },
                    "ranking": i,
                    "trend": "improving" if i <= 3 else "stable" if i <= 7 else "declining"
                }
                
                top_suppliers.append(supplier)
            
            return top_suppliers
            
        except Exception as e:
            logger.error(f"Failed to get top suppliers: {e}")
            return []
    
    def get_supplier_statistics(self, company_id: int) -> Dict[str, Any]:
        """
        Get supplier statistics for a company.
        
        Args:
            company_id: Company ID for data isolation
            
        Returns:
            dict: Supplier statistics
        """
        try:
            # In production, would calculate from database
            return {
                "total_suppliers": 45,
                "active_suppliers": 38,
                "inactive_suppliers": 7,
                "performance_breakdown": {
                    "excellent": 8,
                    "good": 15,
                    "satisfactory": 12,
                    "needs_improvement": 6,
                    "poor": 4
                },
                "average_performance_score": 3.6,
                "top_performing_supplier": {
                    "id": 1,
                    "name": "Top Supplier 1",
                    "score": 4.8
                },
                "monthly_evaluations": 12,
                "pending_evaluations": 3
            }
            
        except Exception as e:
            logger.error(f"Failed to get supplier statistics: {e}")
            return {}
    
    def _get_mock_performance_record(self, performance_id: int) -> Optional[SupplierPerformance]:
        """
        Mock method to simulate loading a performance record from database.
        In production, this would be a proper database query.
        """
        # Create a mock performance record for testing
        period_start = datetime.utcnow() - timedelta(days=90)
        period_end = datetime.utcnow()
        
        performance = SupplierPerformance(
            id=performance_id,
            company_id=1,
            supplier_id=1,
            evaluation_period_start=period_start,
            evaluation_period_end=period_end,
            evaluator_user_id=1
        )
        
        # Add mock performance data
        self._collect_performance_data(performance)
        
        return performance