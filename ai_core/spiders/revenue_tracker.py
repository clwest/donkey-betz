"""
Revenue Tracking System
Phase 5: Activate Money-Making Pipeline - Revenue & ROI Analytics

This module tracks actual revenue generation, client payments, project completion,
and provides comprehensive ROI analysis for the entire spider-based system.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from decimal import Decimal
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class RevenueStatus(Enum):
    """Revenue lifecycle states"""
    PENDING = "pending"
    INVOICED = "invoiced"
    PARTIAL_PAID = "partial_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class ProjectPhase(Enum):
    """Project completion phases"""
    NEGOTIATION = "negotiation"
    CONTRACTED = "contracted"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    MAINTENANCE = "maintenance"


@dataclass
class RevenueRecord:
    """Individual revenue tracking record"""
    id: str
    application_id: str
    user_id: str
    client_name: str
    project_title: str

    # Financial details
    contract_value: Decimal
    paid_amount: Decimal = Decimal('0.00')
    outstanding_amount: Decimal = Decimal('0.00')
    hourly_rate: Decimal = Decimal('0.00')
    hours_worked: float = 0.0

    # Project tracking
    project_phase: ProjectPhase = ProjectPhase.NEGOTIATION
    revenue_status: RevenueStatus = RevenueStatus.PENDING

    # Timeline tracking
    contract_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None

    # Performance metrics
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    client_satisfaction: float = 0.0  # 1-10 scale
    repeat_client: bool = False

    # Metadata
    payment_terms: str = "Net 30"
    currency: str = "USD"
    payment_method: str = ""
    invoice_number: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RevenueMetrics:
    """Revenue analytics and metrics"""

    # Total revenue
    total_revenue: Decimal = Decimal('0.00')
    paid_revenue: Decimal = Decimal('0.00')
    pending_revenue: Decimal = Decimal('0.00')
    overdue_revenue: Decimal = Decimal('0.00')

    # Project metrics
    total_projects: int = 0
    completed_projects: int = 0
    active_projects: int = 0
    success_rate: float = 0.0

    # Time metrics
    total_hours_worked: float = 0.0
    avg_hourly_rate: Decimal = Decimal('0.00')
    time_to_payment: float = 0.0  # Average days

    # Client metrics
    total_clients: int = 0
    repeat_clients: int = 0
    avg_client_satisfaction: float = 0.0

    # Performance metrics
    revenue_growth_rate: float = 0.0
    monthly_recurring_revenue: Decimal = Decimal('0.00')
    client_retention_rate: float = 0.0


class RevenueAnalytics:
    """Advanced revenue analytics and insights"""

    def __init__(self):
        self.analysis_cache = {}
        self.cache_ttl = 3600  # 1 hour cache

    async def generate_revenue_insights(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Generate comprehensive revenue insights"""

        insights = {
            'summary': await self._calculate_summary_metrics(records),
            'trends': await self._analyze_trends(records),
            'client_analysis': await self._analyze_clients(records),
            'project_performance': await self._analyze_project_performance(records),
            'payment_patterns': await self._analyze_payment_patterns(records),
            'recommendations': await self._generate_recommendations(records),
            'forecasting': await self._forecast_revenue(records),
            'benchmarks': await self._calculate_benchmarks(records)
        }

        return insights

    async def _calculate_summary_metrics(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Calculate high-level summary metrics"""

        if not records:
            return {}

        total_revenue = sum(r.contract_value for r in records)
        paid_revenue = sum(r.paid_amount for r in records)
        pending_revenue = sum(r.outstanding_amount for r in records)

        completed_projects = len([r for r in records if r.project_phase == ProjectPhase.COMPLETED])
        active_projects = len([r for r in records if r.project_phase in [ProjectPhase.IN_PROGRESS, ProjectPhase.REVIEW]])

        total_hours = sum(r.actual_hours for r in records if r.actual_hours > 0)
        avg_hourly = Decimal(str(float(paid_revenue) / max(total_hours, 1))).quantize(Decimal('0.01'))

        # Payment timeline analysis
        payment_times = []
        for record in records:
            if record.payment_date and record.due_date:
                days_diff = (record.payment_date - record.due_date).days
                payment_times.append(days_diff)

        avg_payment_time = statistics.mean(payment_times) if payment_times else 0

        return {
            'total_contract_value': float(total_revenue),
            'total_paid': float(paid_revenue),
            'total_pending': float(pending_revenue),
            'collection_rate': float(paid_revenue / total_revenue * 100) if total_revenue > 0 else 0,
            'total_projects': len(records),
            'completed_projects': completed_projects,
            'active_projects': active_projects,
            'completion_rate': (completed_projects / len(records) * 100) if records else 0,
            'total_hours_worked': total_hours,
            'average_hourly_rate': float(avg_hourly),
            'average_payment_delay_days': avg_payment_time
        }

    async def _analyze_trends(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze revenue trends over time"""

        # Group by month
        monthly_data = defaultdict(lambda: {'revenue': Decimal('0.00'), 'projects': 0})

        for record in records:
            if record.contract_date:
                month_key = record.contract_date.strftime('%Y-%m')
                monthly_data[month_key]['revenue'] += record.contract_value
                monthly_data[month_key]['projects'] += 1

        # Calculate growth rates
        months = sorted(monthly_data.keys())
        growth_rates = []

        for i in range(1, len(months)):
            prev_revenue = monthly_data[months[i-1]]['revenue']
            curr_revenue = monthly_data[months[i]]['revenue']

            if prev_revenue > 0:
                growth_rate = float((curr_revenue - prev_revenue) / prev_revenue * 100)
                growth_rates.append(growth_rate)

        avg_growth_rate = statistics.mean(growth_rates) if growth_rates else 0

        return {
            'monthly_data': {month: {'revenue': float(data['revenue']), 'projects': data['projects']}
                            for month, data in monthly_data.items()},
            'average_monthly_growth': avg_growth_rate,
            'trending_up': avg_growth_rate > 5,
            'best_month': max(monthly_data.items(), key=lambda x: x[1]['revenue'])[0] if monthly_data else None,
            'total_months_active': len(months)
        }

    async def _analyze_clients(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze client patterns and relationships"""

        client_data = defaultdict(lambda: {
            'total_revenue': Decimal('0.00'),
            'projects': 0,
            'avg_satisfaction': 0.0,
            'last_project': None,
            'payment_behavior': 'good'
        })

        for record in records:
            client = record.client_name
            client_data[client]['total_revenue'] += record.contract_value
            client_data[client]['projects'] += 1

            if record.client_satisfaction > 0:
                client_data[client]['avg_satisfaction'] = (
                    client_data[client]['avg_satisfaction'] * (client_data[client]['projects'] - 1) +
                    record.client_satisfaction
                ) / client_data[client]['projects']

            if not client_data[client]['last_project'] or record.contract_date > client_data[client]['last_project']:
                client_data[client]['last_project'] = record.contract_date

            # Determine payment behavior
            if record.revenue_status == RevenueStatus.OVERDUE:
                client_data[client]['payment_behavior'] = 'poor'
            elif record.revenue_status == RevenueStatus.PAID and client_data[client]['payment_behavior'] != 'poor':
                client_data[client]['payment_behavior'] = 'excellent'

        # Find top clients
        top_clients = sorted(
            client_data.items(),
            key=lambda x: x[1]['total_revenue'],
            reverse=True
        )[:5]

        # Calculate retention metrics
        repeat_clients = len([c for c in client_data.values() if c['projects'] > 1])
        retention_rate = (repeat_clients / len(client_data) * 100) if client_data else 0

        return {
            'total_unique_clients': len(client_data),
            'repeat_clients': repeat_clients,
            'client_retention_rate': retention_rate,
            'top_clients': [
                {
                    'name': name,
                    'revenue': float(data['total_revenue']),
                    'projects': data['projects'],
                    'avg_satisfaction': data['avg_satisfaction']
                }
                for name, data in top_clients
            ],
            'avg_revenue_per_client': float(sum(d['total_revenue'] for d in client_data.values()) / len(client_data)) if client_data else 0
        }

    async def _analyze_project_performance(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze individual project performance metrics"""

        if not records:
            return {}

        # Time estimation accuracy
        estimation_accuracy = []
        for record in records:
            if record.estimated_hours > 0 and record.actual_hours > 0:
                accuracy = 1 - abs(record.estimated_hours - record.actual_hours) / record.estimated_hours
                estimation_accuracy.append(max(0, accuracy))

        avg_estimation_accuracy = statistics.mean(estimation_accuracy) if estimation_accuracy else 0

        # Project size distribution
        project_sizes = {
            'small': len([r for r in records if r.contract_value < 1000]),
            'medium': len([r for r in records if 1000 <= r.contract_value < 5000]),
            'large': len([r for r in records if r.contract_value >= 5000])
        }

        # Profitability analysis
        hourly_rates = [float(r.hourly_rate) for r in records if r.hourly_rate > 0]
        avg_hourly_rate = statistics.mean(hourly_rates) if hourly_rates else 0

        satisfaction_scores = [r.client_satisfaction for r in records if r.client_satisfaction > 0]
        avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0

        return {
            'average_estimation_accuracy': avg_estimation_accuracy * 100,
            'project_size_distribution': project_sizes,
            'average_hourly_rate': avg_hourly_rate,
            'average_client_satisfaction': avg_satisfaction,
            'most_profitable_project_type': await self._find_most_profitable_type(records),
            'project_duration_analysis': await self._analyze_project_durations(records)
        }

    async def _find_most_profitable_type(self, records: List[RevenueRecord]) -> str:
        """Find the most profitable project type based on tags"""

        type_profits = defaultdict(list)

        for record in records:
            if record.tags and record.actual_hours > 0:
                hourly_profit = float(record.paid_amount) / record.actual_hours
                for tag in record.tags:
                    type_profits[tag].append(hourly_profit)

        if not type_profits:
            return "insufficient_data"

        # Calculate average profit per hour for each type
        avg_profits = {
            tag: statistics.mean(profits)
            for tag, profits in type_profits.items()
        }

        return max(avg_profits.items(), key=lambda x: x[1])[0]

    async def _analyze_project_durations(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze project duration patterns"""

        durations = []
        for record in records:
            if record.start_date and record.completion_date:
                duration_days = (record.completion_date - record.start_date).days
                durations.append(duration_days)

        if not durations:
            return {'average_duration_days': 0, 'min_duration': 0, 'max_duration': 0}

        return {
            'average_duration_days': statistics.mean(durations),
            'min_duration_days': min(durations),
            'max_duration_days': max(durations),
            'median_duration_days': statistics.median(durations)
        }

    async def _analyze_payment_patterns(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze client payment behaviors and patterns"""

        payment_statuses = defaultdict(int)
        payment_delays = []

        for record in records:
            payment_statuses[record.revenue_status.value] += 1

            if record.payment_date and record.due_date:
                delay_days = (record.payment_date - record.due_date).days
                payment_delays.append(delay_days)

        avg_delay = statistics.mean(payment_delays) if payment_delays else 0
        on_time_payments = len([d for d in payment_delays if d <= 0])
        on_time_rate = (on_time_payments / len(payment_delays) * 100) if payment_delays else 0

        return {
            'payment_status_distribution': dict(payment_statuses),
            'average_payment_delay_days': avg_delay,
            'on_time_payment_rate': on_time_rate,
            'late_payment_rate': 100 - on_time_rate,
            'payment_reliability_score': max(0, 100 - avg_delay * 2)  # Custom scoring
        }

    async def _generate_recommendations(self, records: List[RevenueRecord]) -> List[str]:
        """Generate actionable recommendations based on data analysis"""

        recommendations = []

        if not records:
            return ["Start tracking revenue data to get personalized recommendations"]

        # Analyze collection rate
        total_revenue = sum(r.contract_value for r in records)
        paid_revenue = sum(r.paid_amount for r in records)
        collection_rate = float(paid_revenue / total_revenue * 100) if total_revenue > 0 else 0

        if collection_rate < 80:
            recommendations.append(f"Collection rate is {collection_rate:.1f}% - consider stricter payment terms")

        # Analyze hourly rates
        hourly_rates = [float(r.hourly_rate) for r in records if r.hourly_rate > 0]
        if hourly_rates:
            avg_rate = statistics.mean(hourly_rates)
            if avg_rate < 50:
                recommendations.append(f"Average hourly rate (${avg_rate:.2f}) is below market standards - consider increasing rates")

        # Analyze client diversity
        unique_clients = len(set(r.client_name for r in records))
        if unique_clients < len(records) * 0.7:
            recommendations.append("Consider diversifying client base to reduce dependency risk")

        # Analyze project completion
        completed = len([r for r in records if r.project_phase == ProjectPhase.COMPLETED])
        completion_rate = (completed / len(records) * 100) if records else 0
        if completion_rate < 90:
            recommendations.append(f"Project completion rate is {completion_rate:.1f}% - focus on delivery improvement")

        # Analyze payment delays
        overdue_count = len([r for r in records if r.revenue_status == RevenueStatus.OVERDUE])
        if overdue_count > len(records) * 0.1:
            recommendations.append("High overdue rate detected - implement automated payment reminders")

        return recommendations

    async def _forecast_revenue(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Generate revenue forecasting based on historical data"""

        if len(records) < 3:
            return {'forecast_available': False, 'reason': 'Insufficient historical data'}

        # Group by month for trend analysis
        monthly_revenue = defaultdict(Decimal)
        for record in records:
            if record.contract_date:
                month_key = record.contract_date.strftime('%Y-%m')
                monthly_revenue[month_key] += record.contract_value

        # Calculate simple linear trend
        months = sorted(monthly_revenue.keys())
        revenues = [float(monthly_revenue[month]) for month in months]

        if len(revenues) >= 3:
            # Simple linear regression for trend
            n = len(revenues)
            sum_x = sum(range(n))
            sum_y = sum(revenues)
            sum_xy = sum(i * revenues[i] for i in range(n))
            sum_x2 = sum(i * i for i in range(n))

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n

            # Forecast next 3 months
            next_3_months = [intercept + slope * (n + i) for i in range(1, 4)]

            return {
                'forecast_available': True,
                'trend_slope': slope,
                'next_3_months_forecast': next_3_months,
                'confidence_level': 'medium',
                'trend_direction': 'increasing' if slope > 0 else 'decreasing'
            }

        return {'forecast_available': False, 'reason': 'Insufficient data points for trending'}

    async def _calculate_benchmarks(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Calculate industry benchmarks and comparisons"""

        # Industry benchmarks (example values - replace with real data)
        industry_benchmarks = {
            'avg_hourly_rate': 75.0,
            'collection_rate': 95.0,
            'client_satisfaction': 8.5,
            'on_time_delivery': 85.0,
            'payment_terms_days': 30
        }

        if not records:
            return {'benchmarks_available': False}

        # Calculate our metrics
        hourly_rates = [float(r.hourly_rate) for r in records if r.hourly_rate > 0]
        our_avg_rate = statistics.mean(hourly_rates) if hourly_rates else 0

        total_revenue = sum(r.contract_value for r in records)
        paid_revenue = sum(r.paid_amount for r in records)
        our_collection_rate = float(paid_revenue / total_revenue * 100) if total_revenue > 0 else 0

        satisfaction_scores = [r.client_satisfaction for r in records if r.client_satisfaction > 0]
        our_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0

        return {
            'benchmarks_available': True,
            'comparisons': {
                'hourly_rate': {
                    'our_rate': our_avg_rate,
                    'industry_avg': industry_benchmarks['avg_hourly_rate'],
                    'performance': 'above' if our_avg_rate > industry_benchmarks['avg_hourly_rate'] else 'below'
                },
                'collection_rate': {
                    'our_rate': our_collection_rate,
                    'industry_avg': industry_benchmarks['collection_rate'],
                    'performance': 'above' if our_collection_rate > industry_benchmarks['collection_rate'] else 'below'
                },
                'client_satisfaction': {
                    'our_score': our_satisfaction,
                    'industry_avg': industry_benchmarks['client_satisfaction'],
                    'performance': 'above' if our_satisfaction > industry_benchmarks['client_satisfaction'] else 'below'
                }
            }
        }


class RevenueTracker:
    """Main revenue tracking system"""

    def __init__(self):
        self.records: Dict[str, RevenueRecord] = {}
        self.analytics = RevenueAnalytics()

        # System statistics
        self.stats = {
            'total_tracked_revenue': Decimal('0.00'),
            'total_paid_revenue': Decimal('0.00'),
            'active_projects': 0,
            'total_clients': 0,
            'avg_project_value': Decimal('0.00'),
            'collection_rate': 0.0,
            'last_updated': datetime.now()
        }

        logger.info("💰 Revenue Tracker initialized")

    async def create_revenue_record(
        self,
        application_id: str,
        user_id: str,
        client_name: str,
        project_title: str,
        contract_value: float,
        **kwargs
    ) -> str:
        """Create a new revenue tracking record"""

        try:
            record_id = str(uuid.uuid4())

            record = RevenueRecord(
                id=record_id,
                application_id=application_id,
                user_id=user_id,
                client_name=client_name,
                project_title=project_title,
                contract_value=Decimal(str(contract_value)).quantize(Decimal('0.01')),
                outstanding_amount=Decimal(str(contract_value)).quantize(Decimal('0.01')),
                **{k: v for k, v in kwargs.items() if hasattr(RevenueRecord, k)}
            )

            self.records[record_id] = record
            await self._update_stats()

            logger.info(f"💰 Created revenue record: {record_id} (${contract_value})")
            return record_id

        except Exception as e:
            logger.error(f"❌ Error creating revenue record: {e}")
            return ""

    async def update_payment(
        self,
        record_id: str,
        payment_amount: float,
        payment_date: Optional[datetime] = None
    ) -> bool:
        """Update payment information for a record"""

        if record_id not in self.records:
            logger.error(f"❌ Revenue record not found: {record_id}")
            return False

        try:
            record = self.records[record_id]
            payment_decimal = Decimal(str(payment_amount)).quantize(Decimal('0.01'))

            # Update payment amounts
            record.paid_amount += payment_decimal
            record.outstanding_amount = record.contract_value - record.paid_amount
            record.payment_date = payment_date or datetime.now()
            record.updated_at = datetime.now()

            # Update status based on payment
            if record.outstanding_amount <= 0:
                record.revenue_status = RevenueStatus.PAID
            elif record.paid_amount > 0:
                record.revenue_status = RevenueStatus.PARTIAL_PAID

            await self._update_stats()

            logger.info(f"💰 Updated payment for {record_id}: ${payment_amount} "
                       f"(${float(record.outstanding_amount)} remaining)")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating payment: {e}")
            return False

    async def update_project_status(
        self,
        record_id: str,
        project_phase: ProjectPhase,
        completion_date: Optional[datetime] = None,
        client_satisfaction: Optional[float] = None
    ) -> bool:
        """Update project status and completion information"""

        if record_id not in self.records:
            logger.error(f"❌ Revenue record not found: {record_id}")
            return False

        try:
            record = self.records[record_id]
            record.project_phase = project_phase
            record.updated_at = datetime.now()

            if completion_date:
                record.completion_date = completion_date

            if client_satisfaction is not None:
                record.client_satisfaction = max(1.0, min(10.0, client_satisfaction))

            await self._update_stats()

            logger.info(f"📊 Updated project status for {record_id}: {project_phase.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating project status: {e}")
            return False

    async def track_time(
        self,
        record_id: str,
        hours_worked: float,
        hourly_rate: Optional[float] = None
    ) -> bool:
        """Track time worked on a project"""

        if record_id not in self.records:
            logger.error(f"❌ Revenue record not found: {record_id}")
            return False

        try:
            record = self.records[record_id]
            record.actual_hours += hours_worked
            record.updated_at = datetime.now()

            if hourly_rate is not None:
                record.hourly_rate = Decimal(str(hourly_rate)).quantize(Decimal('0.01'))

            logger.info(f"⏰ Tracked {hours_worked} hours for {record_id} "
                       f"(Total: {record.actual_hours})")
            return True

        except Exception as e:
            logger.error(f"❌ Error tracking time: {e}")
            return False

    async def generate_invoice(
        self,
        record_id: str,
        invoice_number: str,
        due_date: Optional[datetime] = None
    ) -> bool:
        """Generate invoice for a project"""

        if record_id not in self.records:
            logger.error(f"❌ Revenue record not found: {record_id}")
            return False

        try:
            record = self.records[record_id]
            record.invoice_number = invoice_number
            record.revenue_status = RevenueStatus.INVOICED
            record.due_date = due_date or datetime.now() + timedelta(days=30)
            record.updated_at = datetime.now()

            logger.info(f"📄 Generated invoice {invoice_number} for {record_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error generating invoice: {e}")
            return False

    async def get_revenue_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""

        try:
            # Filter records by user if specified
            records_to_analyze = list(self.records.values())
            if user_id:
                records_to_analyze = [r for r in records_to_analyze if r.user_id == user_id]

            analytics = await self.analytics.generate_revenue_insights(records_to_analyze)

            return {
                'analytics_generated_at': datetime.now().isoformat(),
                'total_records_analyzed': len(records_to_analyze),
                'user_filter': user_id,
                **analytics
            }

        except Exception as e:
            logger.error(f"❌ Error generating revenue analytics: {e}")
            return {'error': str(e)}

    async def get_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Get all overdue invoices requiring follow-up"""

        overdue = []
        current_date = datetime.now()

        for record in self.records.values():
            if (record.revenue_status in [RevenueStatus.INVOICED, RevenueStatus.PARTIAL_PAID] and
                record.due_date and
                current_date > record.due_date):

                days_overdue = (current_date - record.due_date).days

                overdue.append({
                    'record_id': record.id,
                    'client_name': record.client_name,
                    'project_title': record.project_title,
                    'outstanding_amount': float(record.outstanding_amount),
                    'days_overdue': days_overdue,
                    'invoice_number': record.invoice_number,
                    'due_date': record.due_date.isoformat() if record.due_date else None
                })

        # Sort by days overdue (most overdue first)
        overdue.sort(key=lambda x: x['days_overdue'], reverse=True)

        return overdue

    async def _update_stats(self):
        """Update system statistics"""

        try:
            records = list(self.records.values())

            if not records:
                return

            self.stats['total_tracked_revenue'] = sum(r.contract_value for r in records)
            self.stats['total_paid_revenue'] = sum(r.paid_amount for r in records)
            self.stats['active_projects'] = len([r for r in records if r.project_phase in [ProjectPhase.IN_PROGRESS, ProjectPhase.REVIEW]])
            self.stats['total_clients'] = len(set(r.client_name for r in records))
            self.stats['avg_project_value'] = self.stats['total_tracked_revenue'] / len(records)

            if self.stats['total_tracked_revenue'] > 0:
                self.stats['collection_rate'] = float(
                    self.stats['total_paid_revenue'] / self.stats['total_tracked_revenue'] * 100
                )

            self.stats['last_updated'] = datetime.now()

        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get current system statistics"""

        return {
            'total_records': len(self.records),
            'total_tracked_revenue': float(self.stats['total_tracked_revenue']),
            'total_paid_revenue': float(self.stats['total_paid_revenue']),
            'outstanding_revenue': float(self.stats['total_tracked_revenue'] - self.stats['total_paid_revenue']),
            'active_projects': self.stats['active_projects'],
            'total_clients': self.stats['total_clients'],
            'average_project_value': float(self.stats['avg_project_value']),
            'collection_rate': self.stats['collection_rate'],
            'last_updated': self.stats['last_updated'].isoformat()
        }


# Singleton instance
revenue_tracker = RevenueTracker()


# Public API functions
async def create_project_revenue(
    application_id: str,
    user_id: str,
    client_name: str,
    project_title: str,
    contract_value: float,
    **kwargs
) -> str:
    """Create a new revenue tracking record"""
    return await revenue_tracker.create_revenue_record(
        application_id, user_id, client_name, project_title, contract_value, **kwargs
    )


async def record_payment(
    record_id: str,
    payment_amount: float,
    payment_date: Optional[datetime] = None
) -> bool:
    """Record a payment for a project"""
    return await revenue_tracker.update_payment(record_id, payment_amount, payment_date)


async def update_project_phase(
    record_id: str,
    phase: ProjectPhase,
    completion_date: Optional[datetime] = None,
    satisfaction: Optional[float] = None
) -> bool:
    """Update project phase and completion status"""
    return await revenue_tracker.update_project_status(record_id, phase, completion_date, satisfaction)


async def track_project_time(record_id: str, hours: float, rate: Optional[float] = None) -> bool:
    """Track time worked on a project"""
    return await revenue_tracker.track_time(record_id, hours, rate)


async def create_project_invoice(
    record_id: str,
    invoice_number: str,
    due_date: Optional[datetime] = None
) -> bool:
    """Create an invoice for a project"""
    return await revenue_tracker.generate_invoice(record_id, invoice_number, due_date)


async def get_revenue_insights(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get comprehensive revenue analytics"""
    return await revenue_tracker.get_revenue_analytics(user_id)


async def get_overdue_payments() -> List[Dict[str, Any]]:
    """Get all overdue invoices"""
    return await revenue_tracker.get_overdue_invoices()


def get_revenue_stats() -> Dict[str, Any]:
    """Get revenue tracking statistics"""
    return revenue_tracker.get_statistics()