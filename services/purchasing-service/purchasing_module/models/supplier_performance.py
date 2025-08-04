"""
Supplier Performance models for tracking and evaluating supplier metrics
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
import enum

from purchasing_module.framework.base import CompanyBusinessObject, BaseModel


class PerformanceMetricType(str, enum.Enum):
    """Types of performance metrics"""
    DELIVERY_TIME = "delivery_time"
    QUALITY_RATING = "quality_rating"
    PRICE_COMPETITIVENESS = "price_competitiveness"
    COMMUNICATION = "communication"
    COMPLIANCE = "compliance"
    OVERALL_SATISFACTION = "overall_satisfaction"


class PerformanceRating(str, enum.Enum):
    """Performance rating scale"""
    EXCELLENT = "excellent"      # 5 stars
    GOOD = "good"               # 4 stars
    SATISFACTORY = "satisfactory"  # 3 stars
    NEEDS_IMPROVEMENT = "needs_improvement"  # 2 stars
    POOR = "poor"               # 1 star


class SupplierPerformance(CompanyBusinessObject):
    """
    Supplier Performance tracking model.
    
    Tracks performance metrics for suppliers across multiple dimensions
    to enable data-driven supplier selection and management.
    """
    
    __tablename__ = "supplier_performance"
    
    # Supplier reference (Partner integration)
    supplier_id = Column(
        Integer,
        ForeignKey("partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Performance period
    evaluation_period_start = Column(DateTime, nullable=False)
    evaluation_period_end = Column(DateTime, nullable=False)
    
    # Overall metrics
    total_orders = Column(Integer, nullable=False, default=0)
    total_value = Column(Numeric(15, 2), nullable=False, default=0.0)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Delivery performance
    on_time_deliveries = Column(Integer, nullable=False, default=0)
    late_deliveries = Column(Integer, nullable=False, default=0)
    average_delivery_days = Column(Numeric(5, 2), nullable=True)
    delivery_rating = Column(Enum(PerformanceRating), nullable=True)
    
    # Quality metrics
    quality_issues_count = Column(Integer, nullable=False, default=0)
    return_rate_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    quality_rating = Column(Enum(PerformanceRating), nullable=True)
    
    # Price competitiveness
    price_variance_percentage = Column(Numeric(8, 4), nullable=True)  # vs market average
    cost_savings_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    price_rating = Column(Enum(PerformanceRating), nullable=True)
    
    # Communication and service
    response_time_hours = Column(Numeric(6, 2), nullable=True)
    communication_rating = Column(Enum(PerformanceRating), nullable=True)
    
    # Compliance and documentation
    compliance_issues_count = Column(Integer, nullable=False, default=0)
    documentation_complete_percentage = Column(Numeric(5, 2), nullable=False, default=100.0)
    compliance_rating = Column(Enum(PerformanceRating), nullable=True)
    
    # Overall assessment
    overall_rating = Column(Enum(PerformanceRating), nullable=True)
    overall_score = Column(Numeric(3, 2), nullable=True)  # 1.0 to 5.0
    
    # Evaluation details
    evaluator_user_id = Column(Integer, nullable=True)
    evaluation_date = Column(DateTime, nullable=True)
    evaluation_notes = Column(Text)
    
    # Recommendations
    recommended_for_future = Column(Boolean, nullable=False, default=True)
    improvement_areas = Column(JSON)  # List of areas needing improvement
    strengths = Column(JSON)  # List of supplier strengths
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships - these would be proper relationships in production
    # supplier = relationship("Partner", back_populates="performance_records")
    # performance_metrics = relationship("PerformanceMetric", back_populates="performance_record", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of supplier performance."""
        period = f"{self.evaluation_period_start.strftime('%Y-%m')} to {self.evaluation_period_end.strftime('%Y-%m')}"
        return f"Supplier {self.supplier_id} Performance: {period} - {self.overall_rating.value if self.overall_rating else 'Not Rated'}"
    
    def __repr__(self):
        """Detailed representation of supplier performance."""
        return (
            f"SupplierPerformance(id={self.id}, supplier_id={self.supplier_id}, "
            f"period='{self.evaluation_period_start.date()}:{self.evaluation_period_end.date()}', "
            f"overall_rating='{self.overall_rating.value if self.overall_rating else None}')"
        )
    
    @property
    def on_time_delivery_percentage(self) -> float:
        """Calculate on-time delivery percentage."""
        total_deliveries = self.on_time_deliveries + self.late_deliveries
        if total_deliveries == 0:
            return 0.0
        return (self.on_time_deliveries / total_deliveries) * 100
    
    @property
    def average_order_value(self) -> Decimal:
        """Calculate average order value."""
        if self.total_orders == 0:
            return Decimal('0.00')
        return self.total_value / self.total_orders
    
    @property
    def performance_summary(self) -> Dict[str, Any]:
        """Get performance summary dictionary."""
        return {
            "supplier_id": self.supplier_id,
            "evaluation_period": {
                "start": self.evaluation_period_start.isoformat(),
                "end": self.evaluation_period_end.isoformat()
            },
            "overall_rating": self.overall_rating.value if self.overall_rating else None,
            "overall_score": float(self.overall_score) if self.overall_score else None,
            "total_orders": self.total_orders,
            "total_value": float(self.total_value),
            "on_time_delivery_percentage": self.on_time_delivery_percentage,
            "quality_issues_count": self.quality_issues_count,
            "return_rate_percentage": float(self.return_rate_percentage),
            "recommended_for_future": self.recommended_for_future
        }
    
    def calculate_overall_score(self) -> float:
        """
        Calculate overall performance score based on individual ratings.
        
        Returns:
            float: Overall score from 1.0 to 5.0
        """
        ratings = [
            self.delivery_rating,
            self.quality_rating,
            self.price_rating,
            self.communication_rating,
            self.compliance_rating
        ]
        
        # Filter out None values
        valid_ratings = [r for r in ratings if r is not None]
        
        if not valid_ratings:
            return 0.0
        
        # Convert ratings to numeric scores
        rating_scores = {
            PerformanceRating.EXCELLENT: 5.0,
            PerformanceRating.GOOD: 4.0,
            PerformanceRating.SATISFACTORY: 3.0,
            PerformanceRating.NEEDS_IMPROVEMENT: 2.0,
            PerformanceRating.POOR: 1.0
        }
        
        total_score = sum(rating_scores[rating] for rating in valid_ratings)
        average_score = total_score / len(valid_ratings)
        
        # Update the overall score and rating
        self.overall_score = Decimal(str(round(average_score, 2)))
        
        # Determine overall rating based on score
        if average_score >= 4.5:
            self.overall_rating = PerformanceRating.EXCELLENT
        elif average_score >= 3.5:
            self.overall_rating = PerformanceRating.GOOD
        elif average_score >= 2.5:
            self.overall_rating = PerformanceRating.SATISFACTORY
        elif average_score >= 1.5:
            self.overall_rating = PerformanceRating.NEEDS_IMPROVEMENT
        else:
            self.overall_rating = PerformanceRating.POOR
        
        return float(average_score)
    
    def add_performance_data(
        self,
        orders_count: int,
        orders_value: Decimal,
        on_time_count: int,
        late_count: int,
        quality_issues: int = 0,
        return_rate: float = 0.0
    ) -> None:
        """
        Add performance data for the evaluation period.
        
        Args:
            orders_count: Number of orders in period
            orders_value: Total value of orders
            on_time_count: Number of on-time deliveries
            late_count: Number of late deliveries
            quality_issues: Number of quality issues
            return_rate: Return rate percentage
        """
        self.total_orders = orders_count
        self.total_value = orders_value
        self.on_time_deliveries = on_time_count
        self.late_deliveries = late_count
        self.quality_issues_count = quality_issues
        self.return_rate_percentage = Decimal(str(return_rate))
        
        # Auto-assign ratings based on performance
        self._auto_assign_delivery_rating()
        self._auto_assign_quality_rating()
    
    def _auto_assign_delivery_rating(self) -> None:
        """Auto-assign delivery rating based on on-time percentage."""
        on_time_pct = self.on_time_delivery_percentage
        
        if on_time_pct >= 95:
            self.delivery_rating = PerformanceRating.EXCELLENT
        elif on_time_pct >= 85:
            self.delivery_rating = PerformanceRating.GOOD
        elif on_time_pct >= 70:
            self.delivery_rating = PerformanceRating.SATISFACTORY
        elif on_time_pct >= 50:
            self.delivery_rating = PerformanceRating.NEEDS_IMPROVEMENT
        else:
            self.delivery_rating = PerformanceRating.POOR
    
    def _auto_assign_quality_rating(self) -> None:
        """Auto-assign quality rating based on return rate and issues."""
        return_rate = float(self.return_rate_percentage)
        
        if return_rate <= 1.0 and self.quality_issues_count == 0:
            self.quality_rating = PerformanceRating.EXCELLENT
        elif return_rate <= 3.0 and self.quality_issues_count <= 2:
            self.quality_rating = PerformanceRating.GOOD
        elif return_rate <= 5.0 and self.quality_issues_count <= 5:
            self.quality_rating = PerformanceRating.SATISFACTORY
        elif return_rate <= 10.0:
            self.quality_rating = PerformanceRating.NEEDS_IMPROVEMENT
        else:
            self.quality_rating = PerformanceRating.POOR
    
    def finalize_evaluation(self, evaluator_user_id: int, notes: str = None) -> None:
        """
        Finalize the performance evaluation.
        
        Args:
            evaluator_user_id: ID of user performing evaluation
            notes: Optional evaluation notes
        """
        self.evaluator_user_id = evaluator_user_id
        self.evaluation_date = datetime.utcnow()
        if notes:
            self.evaluation_notes = notes
        
        # Calculate overall score
        self.calculate_overall_score()
        
        # Set recommendation based on overall rating
        if self.overall_rating in [PerformanceRating.EXCELLENT, PerformanceRating.GOOD]:
            self.recommended_for_future = True
        elif self.overall_rating == PerformanceRating.SATISFACTORY:
            self.recommended_for_future = True  # With improvements
        else:
            self.recommended_for_future = False


class PerformanceMetric(BaseModel):
    """
    Individual performance metric for detailed tracking.
    
    Allows for custom metrics beyond the standard performance categories.
    """
    
    __tablename__ = "performance_metrics"
    
    # Link to performance record
    performance_record_id = Column(
        Integer,
        ForeignKey("supplier_performance.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Metric definition
    metric_type = Column(Enum(PerformanceMetricType), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_description = Column(Text)
    
    # Metric value
    numeric_value = Column(Numeric(15, 4))
    text_value = Column(String(255))
    boolean_value = Column(Boolean)
    json_value = Column(JSON)
    
    # Metric metadata
    unit_of_measure = Column(String(50))
    target_value = Column(Numeric(15, 4))
    weight = Column(Numeric(3, 2), default=1.0)  # Weight in overall score
    
    # Evaluation
    meets_target = Column(Boolean)
    performance_impact = Column(Text)
    
    # Relationships
    # performance_record = relationship("SupplierPerformance", back_populates="performance_metrics")
    
    def __str__(self):
        """String representation of performance metric."""
        value = self.numeric_value or self.text_value or self.boolean_value
        return f"{self.metric_name}: {value} {self.unit_of_measure or ''}".strip()
    
    def __repr__(self):
        """Detailed representation of performance metric."""
        return (
            f"PerformanceMetric(id={self.id}, type='{self.metric_type.value}', "
            f"name='{self.metric_name}', value={self.numeric_value or self.text_value})"
        )