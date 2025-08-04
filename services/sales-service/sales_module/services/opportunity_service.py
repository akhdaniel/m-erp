"""
Opportunity service for managing sales pipeline and opportunities.

Provides business logic for opportunity management including
pipeline tracking, activities, forecasting, and conversion.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from .base_service import BaseService
from sales_module.models import (
    SalesOpportunity, OpportunityStage, OpportunityActivity,
    OpportunitySource, OpportunityPriority, ActivityType, ActivityOutcome
)


class OpportunityService(BaseService):
    """
    Opportunity service for comprehensive sales pipeline management.
    
    Handles opportunity lifecycle, activity tracking, pipeline management,
    forecasting, and conversion to quotes/orders.
    """
    
    def __init__(self, db_session=None):
        """Initialize opportunity service."""
        super().__init__(db_session)
        self.model_class = SalesOpportunity
    
    def create_opportunity(self, opportunity_data: Dict[str, Any], user_id: int = None,
                          company_id: int = None) -> SalesOpportunity:
        """
        Create new sales opportunity.
        
        Args:
            opportunity_data: Opportunity information
            user_id: ID of user creating the opportunity
            company_id: Company ID for multi-company isolation
            
        Returns:
            Created opportunity instance
        """
        # Generate opportunity number if not provided
        if 'opportunity_number' not in opportunity_data or not opportunity_data['opportunity_number']:
            opportunity_data['opportunity_number'] = self.generate_opportunity_number()
        
        # Set sales rep if not provided
        if 'sales_rep_user_id' not in opportunity_data:
            opportunity_data['sales_rep_user_id'] = user_id
        
        # Set first contact date if not provided
        if 'first_contact_date' not in opportunity_data:
            opportunity_data['first_contact_date'] = datetime.utcnow()
        
        # Calculate weighted value
        if 'estimated_value' in opportunity_data and 'probability_percentage' in opportunity_data:
            estimated_value = Decimal(str(opportunity_data['estimated_value']))
            probability = Decimal(str(opportunity_data['probability_percentage']))
            opportunity_data['weighted_value'] = (estimated_value * probability) / 100
        
        # Create opportunity
        opportunity = self.create(opportunity_data, user_id, company_id)
        
        return opportunity
    
    def advance_opportunity_stage(self, opportunity_id: int, new_stage_id: int,
                                user_id: int = None, company_id: int = None) -> Optional[SalesOpportunity]:
        """
        Advance opportunity to next stage in pipeline.
        
        Args:
            opportunity_id: Opportunity ID
            new_stage_id: New stage ID to advance to
            user_id: ID of user advancing the stage
            company_id: Company ID for isolation
            
        Returns:
            Updated opportunity instance or None if not found
        """
        opportunity = self.get_by_id(opportunity_id, company_id)
        if not opportunity:
            return None
        
        opportunity.advance_stage(new_stage_id, user_id)
        return opportunity
    
    def mark_opportunity_won(self, opportunity_id: int, actual_value: Decimal,
                           close_reason: str = None, user_id: int = None,
                           company_id: int = None) -> Optional[SalesOpportunity]:
        """
        Mark opportunity as won.
        
        Args:
            opportunity_id: Opportunity ID
            actual_value: Actual won value
            close_reason: Reason for winning
            user_id: ID of user marking as won
            company_id: Company ID for isolation
            
        Returns:
            Updated opportunity instance or None if not found
        """
        opportunity = self.get_by_id(opportunity_id, company_id)
        if not opportunity:
            return None
        
        opportunity.mark_won(actual_value, close_reason, user_id)
        return opportunity
    
    def mark_opportunity_lost(self, opportunity_id: int, close_reason: str,
                            competitor_won: str = None, user_id: int = None,
                            company_id: int = None) -> Optional[SalesOpportunity]:
        """
        Mark opportunity as lost.
        
        Args:
            opportunity_id: Opportunity ID
            close_reason: Reason for losing
            competitor_won: Competitor who won (if applicable)
            user_id: ID of user marking as lost
            company_id: Company ID for isolation
            
        Returns:
            Updated opportunity instance or None if not found
        """
        opportunity = self.get_by_id(opportunity_id, company_id)
        if not opportunity:
            return None
        
        opportunity.mark_lost(close_reason, competitor_won, user_id)
        return opportunity
    
    def update_bant_qualification(self, opportunity_id: int, budget_confirmed: bool = None,
                                authority_confirmed: bool = None, need_confirmed: bool = None,
                                timeline_confirmed: bool = None, user_id: int = None,
                                company_id: int = None) -> Optional[SalesOpportunity]:
        """
        Update BANT (Budget, Authority, Need, Timeline) qualification.
        
        Args:
            opportunity_id: Opportunity ID
            budget_confirmed: Budget confirmation status
            authority_confirmed: Authority confirmation status
            need_confirmed: Need confirmation status
            timeline_confirmed: Timeline confirmation status
            user_id: ID of user updating qualification
            company_id: Company ID for isolation
            
        Returns:
            Updated opportunity instance or None if not found
        """
        opportunity = self.get_by_id(opportunity_id, company_id)
        if not opportunity:
            return None
        
        update_data = {}
        if budget_confirmed is not None:
            update_data['budget_confirmed'] = budget_confirmed
        if authority_confirmed is not None:
            update_data['authority_confirmed'] = authority_confirmed
        if need_confirmed is not None:
            update_data['need_confirmed'] = need_confirmed
        if timeline_confirmed is not None:
            update_data['timeline_confirmed'] = timeline_confirmed
        
        if update_data:
            self.update(opportunity_id, update_data, user_id, company_id)
        
        return opportunity
    
    def add_opportunity_activity(self, opportunity_id: int, activity_data: Dict[str, Any],
                               user_id: int = None, company_id: int = None) -> Optional[OpportunityActivity]:
        """
        Add activity to opportunity.
        
        Args:
            opportunity_id: Opportunity ID
            activity_data: Activity information
            user_id: ID of user adding activity
            company_id: Company ID for isolation
            
        Returns:
            Created activity instance or None if opportunity not found
        """
        opportunity = self.get_by_id(opportunity_id, company_id)
        if not opportunity:
            return None
        
        # Set opportunity relationship
        activity_data['opportunity_id'] = opportunity_id
        activity_data['company_id'] = company_id
        activity_data['created_by_user_id'] = user_id
        
        # Set activity date if not provided
        if 'activity_date' not in activity_data:
            activity_data['activity_date'] = datetime.utcnow()
        
        # Create activity
        activity = OpportunityActivity(**activity_data)
        activity.save(self.db_session, user_id)
        
        # Update opportunity's last activity date
        opportunity.last_activity_date = datetime.utcnow()
        opportunity.save(self.db_session, user_id)
        
        return activity
    
    def complete_activity(self, activity_id: int, outcome: ActivityOutcome = None,
                         outcome_description: str = None, user_id: int = None,
                         company_id: int = None) -> Optional[OpportunityActivity]:
        """
        Mark activity as completed with outcome.
        
        Args:
            activity_id: Activity ID
            outcome: Activity outcome
            outcome_description: Description of outcome
            user_id: ID of user completing activity
            company_id: Company ID for isolation
            
        Returns:
            Updated activity instance or None if not found
        """
        # In production, would fetch activity from database
        print(f"Opportunity Service: Completing activity {activity_id}")
        
        # Would mark activity as completed and update opportunity
        return None  # Would return actual activity
    
    def schedule_follow_up(self, activity_id: int, follow_up_date: datetime,
                          notes: str = None, user_id: int = None,
                          company_id: int = None) -> Optional[OpportunityActivity]:
        """
        Schedule follow-up for activity.
        
        Args:
            activity_id: Activity ID
            follow_up_date: Date for follow-up
            notes: Follow-up notes
            user_id: ID of user scheduling follow-up
            company_id: Company ID for isolation
            
        Returns:
            Updated activity instance or None if not found
        """
        # In production, would fetch activity and schedule follow-up
        print(f"Opportunity Service: Scheduling follow-up for activity {activity_id}")
        
        return None  # Would return actual activity
    
    def get_pipeline_summary(self, sales_rep_id: int = None, stage_id: int = None,
                           company_id: int = None) -> Dict[str, Any]:
        """
        Get sales pipeline summary with filtering.
        
        Args:
            sales_rep_id: Filter by sales rep (optional)
            stage_id: Filter by stage (optional)
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with pipeline summary
        """
        # In production, would query opportunities with filters
        return {
            "summary": {
                "total_opportunities": 0,
                "total_value": 0.0,
                "weighted_value": 0.0,
                "average_deal_size": 0.0,
                "qualified_leads": 0
            },
            "by_stage": [
                # Would include actual stage breakdowns
            ],
            "by_source": {
                "website": 0,
                "referral": 0,
                "cold_call": 0,
                "email_campaign": 0,
                "trade_show": 0,
                "social_media": 0,
                "partner": 0,
                "existing_customer": 0,
                "other": 0
            },
            "by_priority": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "urgent": 0
            },
            "overdue_opportunities": [],
            "top_opportunities": []
        }
    
    def get_sales_forecast(self, forecast_period: str = "quarter", 
                          sales_rep_id: int = None, company_id: int = None) -> Dict[str, Any]:
        """
        Get sales forecast based on pipeline.
        
        Args:
            forecast_period: Forecast period (month, quarter, year)
            sales_rep_id: Filter by sales rep (optional)
            company_id: Company ID for isolation
            
        Returns:
            Dictionary with forecast data
        """
        # In production, would calculate forecasts based on:
        # - Opportunity probability percentages
        # - Historical close rates by stage
        # - Sales rep performance
        # - Seasonal trends
        
        return {
            "period": forecast_period,
            "forecast_categories": {
                "commit": {
                    "count": 0,
                    "value": 0.0,
                    "description": "90%+ probability"
                },
                "best_case": {
                    "count": 0,
                    "value": 0.0,
                    "description": "70-89% probability"
                },
                "pipeline": {
                    "count": 0,
                    "value": 0.0,
                    "description": "50-69% probability"
                },
                "upside": {
                    "count": 0,
                    "value": 0.0,
                    "description": "<50% probability"
                }
            },
            "total_forecast": 0.0,
            "weighted_forecast": 0.0,
            "historical_accuracy": 0.0,  # Percentage accuracy of past forecasts
            "trend_analysis": {
                "vs_previous_period": 0.0,  # Percentage change
                "velocity": 0.0  # Deals moving through pipeline speed
            }
        }
    
    def get_opportunity_analytics(self, company_id: int = None,
                                date_range: Dict[str, datetime] = None) -> Dict[str, Any]:
        """
        Get opportunity analytics and metrics.
        
        Args:
            company_id: Company ID for isolation
            date_range: Date range for analytics
            
        Returns:
            Dictionary with analytics data
        """
        # In production, would query aggregated data
        return {
            "summary": {
                "total_opportunities": 0,
                "won_opportunities": 0,
                "lost_opportunities": 0,
                "active_opportunities": 0
            },
            "conversion_metrics": {
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "average_sales_cycle": 0,  # days
                "conversion_by_stage": {}
            },
            "financial_metrics": {
                "total_pipeline_value": 0.0,
                "won_value": 0.0,
                "lost_value": 0.0,
                "average_deal_size": 0.0
            },
            "activity_metrics": {
                "total_activities": 0,
                "activities_per_opportunity": 0.0,
                "most_effective_activities": []
            },
            "source_performance": {
                # Win rates and values by source
            },
            "rep_performance": {
                # Performance metrics by sales rep
            },
            "trends": {
                "monthly_pipeline": [],
                "win_rate_trend": [],
                "cycle_time_trend": []
            }
        }
    
    def get_rep_performance(self, sales_rep_id: int, company_id: int = None,
                          date_range: Dict[str, datetime] = None) -> Dict[str, Any]:
        """
        Get sales rep performance metrics.
        
        Args:
            sales_rep_id: Sales rep user ID
            company_id: Company ID for isolation
            date_range: Date range for metrics
            
        Returns:
            Dictionary with rep performance data
        """
        return {
            "rep_id": sales_rep_id,
            "summary": {
                "active_opportunities": 0,
                "total_pipeline_value": 0.0,
                "weighted_pipeline": 0.0,
                "activities_this_week": 0
            },
            "performance_metrics": {
                "win_rate": 0.0,
                "average_deal_size": 0.0,
                "average_sales_cycle": 0,  # days
                "quota_attainment": 0.0,  # percentage
                "activity_score": 0.0  # based on activity frequency/quality
            },
            "pipeline_health": {
                "qualification_score": 0.0,  # Average BANT score
                "stage_progression": 0.0,  # How quickly deals move through stages
                "overdue_followups": 0
            },
            "recent_wins": [],
            "recent_losses": [],
            "upcoming_activities": []
        }
    
    def create_opportunity_from_lead(self, lead_data: Dict[str, Any], user_id: int = None,
                                   company_id: int = None) -> SalesOpportunity:
        """
        Convert lead to qualified opportunity.
        
        Args:
            lead_data: Lead information to convert
            user_id: ID of user converting lead
            company_id: Company ID for isolation
            
        Returns:
            Created opportunity instance
        """
        # Convert lead fields to opportunity fields
        opportunity_data = {
            'name': lead_data.get('company_name', 'Unnamed Opportunity'),
            'customer_id': lead_data.get('customer_id'),
            'source': lead_data.get('source', OpportunitySource.OTHER),
            'estimated_value': lead_data.get('estimated_budget', 0),
            'expected_close_date': lead_data.get('expected_close_date', 
                                                datetime.utcnow() + timedelta(days=90)),
            'description': lead_data.get('description', ''),
            'products_interested': lead_data.get('products_interested', []),
            'solution_requirements': lead_data.get('requirements', ''),
            'stage_id': self.get_initial_stage_id(company_id)
        }
        
        return self.create_opportunity(opportunity_data, user_id, company_id)
    
    # Utility methods
    
    def generate_opportunity_number(self, prefix: str = "OPP") -> str:
        """Generate unique opportunity number."""
        return self.generate_number(prefix, "opportunity_sequence")
    
    def get_initial_stage_id(self, company_id: int) -> int:
        """Get initial stage ID for new opportunities."""
        # In production, would query for first stage in pipeline
        return 1  # Would return actual stage ID
    
    # Validation overrides
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate opportunity creation data."""
        required_fields = ['name', 'customer_id', 'estimated_value', 'expected_close_date']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Field '{field}' is required for opportunity creation")
        
        # Validate estimated value is positive
        if data['estimated_value'] <= 0:
            raise ValueError("Estimated value must be positive")
        
        # Validate expected close date is in future
        if data['expected_close_date'] <= datetime.utcnow():
            raise ValueError("Expected close date must be in the future")
    
    def validate_update_data(self, data: Dict[str, Any], opportunity: SalesOpportunity) -> None:
        """Validate opportunity update data."""
        # Don't allow changing opportunity number
        if 'opportunity_number' in data and data['opportunity_number'] != opportunity.opportunity_number:
            raise ValueError("Opportunity number cannot be changed after creation")
        
        # Don't allow editing closed opportunities
        if opportunity.is_closed and 'actual_close_date' not in data:
            raise ValueError("Cannot edit closed opportunities except to update close date")