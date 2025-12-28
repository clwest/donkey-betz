"""
ROI Measurement System
Phase 5: Activate Money-Making Pipeline - Return on Investment Analytics

This module provides comprehensive ROI analysis for the entire spider-based
revenue generation system, measuring costs, returns, and optimization opportunities.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import statistics

logger = logging.getLogger(__name__)


class ROIMetricType(Enum):
    """Types of ROI metrics"""
    SYSTEM_ROI = "system_roi"
    SPIDER_ROI = "spider_roi"
    USER_ROI = "user_roi"
    AGENT_ROI = "agent_roi"
    CAMPAIGN_ROI = "campaign_roi"


class CostCategory(Enum):
    """Categories of system costs"""
    INFRASTRUCTURE = "infrastructure"  # Server, hosting, cloud costs
    API_USAGE = "api_usage"            # External API calls
    COMPUTE = "compute"                # Processing power, CPU/memory
    STORAGE = "storage"                # Database, cache storage
    NETWORK = "network"                # Data transfer costs
    HUMAN_RESOURCES = "human_resources" # Development, maintenance
    THIRD_PARTY = "third_party"        # External services, tools


@dataclass
class CostRecord:
    """Individual cost tracking record"""
    id: str
    category: CostCategory
    description: str
    amount: Decimal
    currency: str = "USD"
    date: datetime = field(default_factory=datetime.now)
    recurring: bool = False  # Monthly recurring cost
    allocated_to: Optional[str] = None  # Spider, user, or component ID
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueRecord:
    """Revenue record (from revenue_tracker integration)"""
    id: str
    amount: Decimal
    date: datetime
    source: str  # Spider type or revenue source
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ROIAnalysis:
    """Comprehensive ROI analysis results"""
    metric_type: ROIMetricType
    time_period_days: int

    # Financial metrics
    total_revenue: Decimal = Decimal('0.00')
    total_costs: Decimal = Decimal('0.00')
    net_profit: Decimal = Decimal('0.00')
    roi_percentage: float = 0.0
    profit_margin: float = 0.0

    # Performance metrics
    revenue_per_day: Decimal = Decimal('0.00')
    cost_per_day: Decimal = Decimal('0.00')
    break_even_days: Optional[int] = None

    # Efficiency metrics
    cost_per_acquisition: Decimal = Decimal('0.00')
    revenue_per_spider: Decimal = Decimal('0.00')
    cost_per_application: Decimal = Decimal('0.00')

    # Growth metrics
    revenue_growth_rate: float = 0.0
    cost_efficiency_trend: float = 0.0

    # Analysis metadata
    analysis_date: datetime = field(default_factory=datetime.now)
    data_points_analyzed: int = 0
    confidence_score: float = 0.0


class SystemCostTracker:
    """Track all system operational costs"""

    def __init__(self):
        self.cost_records: Dict[str, CostRecord] = {}

        # Default cost estimates (per month)
        self.baseline_costs = {
            CostCategory.INFRASTRUCTURE: Decimal('200.00'),  # Server hosting
            CostCategory.API_USAGE: Decimal('150.00'),       # External APIs
            CostCategory.COMPUTE: Decimal('300.00'),         # Processing power
            CostCategory.STORAGE: Decimal('50.00'),          # Database storage
            CostCategory.NETWORK: Decimal('25.00'),          # Data transfer
            CostCategory.HUMAN_RESOURCES: Decimal('2000.00'), # Development time
            CostCategory.THIRD_PARTY: Decimal('100.00')      # Tools & services
        }

        logger.info("💰 System Cost Tracker initialized")

    async def add_cost_record(
        self,
        category: CostCategory,
        description: str,
        amount: float,
        recurring: bool = False,
        allocated_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a cost record"""

        try:
            record_id = f"cost_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            record = CostRecord(
                id=record_id,
                category=category,
                description=description,
                amount=Decimal(str(amount)).quantize(Decimal('0.01')),
                recurring=recurring,
                allocated_to=allocated_to,
                metadata=metadata or {}
            )

            self.cost_records[record_id] = record

            logger.info(f"💸 Added cost record: {description} (${amount})")
            return record_id

        except Exception as e:
            logger.error(f"❌ Error adding cost record: {e}")
            return ""

    async def get_costs_for_period(
        self,
        start_date: datetime,
        end_date: datetime,
        category: Optional[CostCategory] = None,
        allocated_to: Optional[str] = None
    ) -> List[CostRecord]:
        """Get cost records for a specific period"""

        filtered_costs = []

        for record in self.cost_records.values():
            # Date filter
            if not (start_date <= record.date <= end_date):
                continue

            # Category filter
            if category and record.category != category:
                continue

            # Allocation filter
            if allocated_to and record.allocated_to != allocated_to:
                continue

            filtered_costs.append(record)

        return filtered_costs

    async def calculate_monthly_costs(self) -> Dict[CostCategory, Decimal]:
        """Calculate estimated monthly costs"""

        monthly_costs = {}
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Get actual costs for current month
        for category in CostCategory:
            actual_costs = await self.get_costs_for_period(
                current_month_start, current_month_end, category
            )

            actual_amount = sum(r.amount for r in actual_costs)
            baseline_amount = self.baseline_costs.get(category, Decimal('0.00'))

            # Use actual if available, otherwise baseline
            monthly_costs[category] = actual_amount if actual_costs else baseline_amount

        return monthly_costs


class ROICalculator:
    """Main ROI calculation and analysis engine"""

    def __init__(self):
        self.cost_tracker = SystemCostTracker()

        # Performance metrics cache
        self.metrics_cache = {}
        self.cache_ttl = 3600  # 1 hour

        # ROI analysis history
        self.roi_history: List[ROIAnalysis] = []

        logger.info("📊 ROI Calculator initialized")

    async def calculate_system_roi(
        self,
        time_period_days: int = 30,
        include_human_costs: bool = True
    ) -> ROIAnalysis:
        """Calculate overall system ROI"""

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period_days)

            # Get revenue data (integration with revenue_tracker)
            total_revenue = await self._get_revenue_for_period(start_date, end_date)

            # Get cost data
            cost_records = await self.cost_tracker.get_costs_for_period(start_date, end_date)

            # Filter costs if needed
            if not include_human_costs:
                cost_records = [r for r in cost_records if r.category != CostCategory.HUMAN_RESOURCES]

            total_costs = sum(r.amount for r in cost_records)

            # Add prorated monthly costs
            monthly_costs = await self.cost_tracker.calculate_monthly_costs()
            monthly_cost_total = sum(monthly_costs.values())

            if not include_human_costs:
                monthly_cost_total -= monthly_costs.get(CostCategory.HUMAN_RESOURCES, Decimal('0.00'))

            # Prorate monthly costs for the period
            prorated_monthly_costs = monthly_cost_total * Decimal(str(time_period_days / 30))
            total_costs += prorated_monthly_costs

            # Calculate metrics
            net_profit = total_revenue - total_costs
            roi_percentage = float((net_profit / total_costs) * 100) if total_costs > 0 else 0.0
            profit_margin = float((net_profit / total_revenue) * 100) if total_revenue > 0 else 0.0

            # Performance metrics
            revenue_per_day = total_revenue / Decimal(str(time_period_days)) if time_period_days > 0 else Decimal('0.00')
            cost_per_day = total_costs / Decimal(str(time_period_days)) if time_period_days > 0 else Decimal('0.00')

            # Calculate break-even
            break_even_days = None
            if revenue_per_day > cost_per_day:
                break_even_days = int(total_costs / (revenue_per_day - cost_per_day))

            # Efficiency metrics
            applications_count = await self._get_applications_count(start_date, end_date)
            spiders_count = await self._get_active_spiders_count()

            cost_per_application = total_costs / applications_count if applications_count > 0 else Decimal('0.00')
            revenue_per_spider = total_revenue / spiders_count if spiders_count > 0 else Decimal('0.00')

            # Growth analysis
            revenue_growth_rate = await self._calculate_revenue_growth(time_period_days)
            cost_efficiency_trend = await self._calculate_cost_efficiency_trend(time_period_days)

            # Create analysis
            analysis = ROIAnalysis(
                metric_type=ROIMetricType.SYSTEM_ROI,
                time_period_days=time_period_days,
                total_revenue=total_revenue,
                total_costs=total_costs,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                profit_margin=profit_margin,
                revenue_per_day=revenue_per_day,
                cost_per_day=cost_per_day,
                break_even_days=break_even_days,
                cost_per_acquisition=cost_per_application,
                revenue_per_spider=revenue_per_spider,
                cost_per_application=cost_per_application,
                revenue_growth_rate=revenue_growth_rate,
                cost_efficiency_trend=cost_efficiency_trend,
                data_points_analyzed=len(cost_records) + applications_count,
                confidence_score=min(1.0, len(cost_records) / 10)  # Higher confidence with more data
            )

            # Store in history
            self.roi_history.append(analysis)

            logger.info(f"📊 Calculated system ROI: {roi_percentage:.2f}% over {time_period_days} days")
            return analysis

        except Exception as e:
            logger.error(f"❌ Error calculating system ROI: {e}")
            return ROIAnalysis(metric_type=ROIMetricType.SYSTEM_ROI, time_period_days=time_period_days)

    async def calculate_spider_roi(
        self,
        spider_type: str,
        time_period_days: int = 30
    ) -> ROIAnalysis:
        """Calculate ROI for a specific spider type"""

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period_days)

            # Get spider-specific revenue
            spider_revenue = await self._get_revenue_by_source(spider_type, start_date, end_date)

            # Get spider-allocated costs
            spider_costs = await self.cost_tracker.get_costs_for_period(
                start_date, end_date, allocated_to=spider_type
            )

            total_spider_costs = sum(r.amount for r in spider_costs)

            # Add proportional system costs
            total_spiders = await self._get_active_spiders_count()
            if total_spiders > 0:
                monthly_costs = await self.cost_tracker.calculate_monthly_costs()
                system_cost_share = sum(monthly_costs.values()) / Decimal(str(total_spiders))
                prorated_system_costs = system_cost_share * Decimal(str(time_period_days / 30))
                total_spider_costs += prorated_system_costs

            # Calculate metrics
            net_profit = spider_revenue - total_spider_costs
            roi_percentage = float((net_profit / total_spider_costs) * 100) if total_spider_costs > 0 else 0.0

            analysis = ROIAnalysis(
                metric_type=ROIMetricType.SPIDER_ROI,
                time_period_days=time_period_days,
                total_revenue=spider_revenue,
                total_costs=total_spider_costs,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                profit_margin=float((net_profit / spider_revenue) * 100) if spider_revenue > 0 else 0.0
            )

            logger.info(f"🕷️ Calculated {spider_type} spider ROI: {roi_percentage:.2f}%")
            return analysis

        except Exception as e:
            logger.error(f"❌ Error calculating spider ROI: {e}")
            return ROIAnalysis(metric_type=ROIMetricType.SPIDER_ROI, time_period_days=time_period_days)

    async def calculate_user_roi(
        self,
        user_id: str,
        time_period_days: int = 30
    ) -> ROIAnalysis:
        """Calculate ROI for a specific user"""

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period_days)

            # Get user-specific revenue
            user_revenue = await self._get_revenue_by_user(user_id, start_date, end_date)

            # Get user-allocated costs
            user_costs = await self.cost_tracker.get_costs_for_period(
                start_date, end_date, allocated_to=user_id
            )

            total_user_costs = sum(r.amount for r in user_costs)

            # Add proportional system costs
            total_users = await self._get_active_users_count()
            if total_users > 0:
                monthly_costs = await self.cost_tracker.calculate_monthly_costs()
                # Exclude human resources for per-user calculation
                relevant_monthly_costs = sum(
                    cost for category, cost in monthly_costs.items()
                    if category != CostCategory.HUMAN_RESOURCES
                )

                user_cost_share = relevant_monthly_costs / Decimal(str(total_users))
                prorated_user_costs = user_cost_share * Decimal(str(time_period_days / 30))
                total_user_costs += prorated_user_costs

            # Calculate metrics
            net_profit = user_revenue - total_user_costs
            roi_percentage = float((net_profit / total_user_costs) * 100) if total_user_costs > 0 else 0.0

            # User-specific efficiency metrics
            applications_count = await self._get_user_applications_count(user_id, start_date, end_date)
            cost_per_application = total_user_costs / applications_count if applications_count > 0 else Decimal('0.00')

            analysis = ROIAnalysis(
                metric_type=ROIMetricType.USER_ROI,
                time_period_days=time_period_days,
                total_revenue=user_revenue,
                total_costs=total_user_costs,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                profit_margin=float((net_profit / user_revenue) * 100) if user_revenue > 0 else 0.0,
                cost_per_application=cost_per_application
            )

            logger.info(f"👤 Calculated user {user_id} ROI: {roi_percentage:.2f}%")
            return analysis

        except Exception as e:
            logger.error(f"❌ Error calculating user ROI: {e}")
            return ROIAnalysis(metric_type=ROIMetricType.USER_ROI, time_period_days=time_period_days)

    async def generate_roi_report(
        self,
        time_period_days: int = 30,
        include_breakdowns: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive ROI report"""

        try:
            # Calculate system-level ROI
            system_roi = await self.calculate_system_roi(time_period_days)

            report = {
                'report_generated_at': datetime.now().isoformat(),
                'analysis_period_days': time_period_days,
                'system_roi': {
                    'total_revenue': float(system_roi.total_revenue),
                    'total_costs': float(system_roi.total_costs),
                    'net_profit': float(system_roi.net_profit),
                    'roi_percentage': system_roi.roi_percentage,
                    'profit_margin': system_roi.profit_margin,
                    'revenue_per_day': float(system_roi.revenue_per_day),
                    'cost_per_day': float(system_roi.cost_per_day),
                    'break_even_days': system_roi.break_even_days,
                    'confidence_score': system_roi.confidence_score
                },
                'efficiency_metrics': {
                    'cost_per_application': float(system_roi.cost_per_application),
                    'revenue_per_spider': float(system_roi.revenue_per_spider),
                    'revenue_growth_rate': system_roi.revenue_growth_rate,
                    'cost_efficiency_trend': system_roi.cost_efficiency_trend
                }
            }

            if include_breakdowns:
                # Spider-level ROI breakdown
                spider_types = await self._get_spider_types()
                spider_roi_breakdown = {}

                for spider_type in spider_types:
                    spider_analysis = await self.calculate_spider_roi(spider_type, time_period_days)
                    spider_roi_breakdown[spider_type] = {
                        'revenue': float(spider_analysis.total_revenue),
                        'costs': float(spider_analysis.total_costs),
                        'roi_percentage': spider_analysis.roi_percentage,
                        'profit_margin': spider_analysis.profit_margin
                    }

                report['spider_breakdown'] = spider_roi_breakdown

                # Cost breakdown by category
                monthly_costs = await self.cost_tracker.calculate_monthly_costs()
                cost_breakdown = {
                    category.value: float(amount)
                    for category, amount in monthly_costs.items()
                }
                report['cost_breakdown'] = cost_breakdown

                # Performance insights
                report['insights'] = await self._generate_roi_insights(system_roi, spider_roi_breakdown)

            return report

        except Exception as e:
            logger.error(f"❌ Error generating ROI report: {e}")
            return {'error': str(e)}

    async def _get_revenue_for_period(self, start_date: datetime, end_date: datetime) -> Decimal:
        """Get total revenue for a period (integration point with revenue_tracker)"""
        # This would integrate with the actual revenue tracking system
        # For now, return a simulated value based on time period
        days = (end_date - start_date).days
        daily_revenue = Decimal('150.00')  # Estimated daily revenue
        return daily_revenue * Decimal(str(days))

    async def _get_revenue_by_source(self, source: str, start_date: datetime, end_date: datetime) -> Decimal:
        """Get revenue from a specific source"""
        total_revenue = await self._get_revenue_for_period(start_date, end_date)
        # Simulate source-specific revenue (would use actual data)
        source_multipliers = {
            'job_spider': 0.4,     # 40% of revenue from job spiders
            'freelance_spider': 0.3, # 30% from freelance
            'financial_spider': 0.2, # 20% from financial
            'default': 0.1        # 10% for other sources
        }
        multiplier = source_multipliers.get(source, source_multipliers['default'])
        return total_revenue * Decimal(str(multiplier))

    async def _get_revenue_by_user(self, user_id: str, start_date: datetime, end_date: datetime) -> Decimal:
        """Get revenue for a specific user"""
        # Simulate user-specific revenue
        total_revenue = await self._get_revenue_for_period(start_date, end_date)
        total_users = await self._get_active_users_count()

        if total_users > 0:
            # Average revenue per user with some variation
            base_per_user = total_revenue / Decimal(str(total_users))
            # Simulate user performance variation (±50%)
            user_hash = hash(user_id) % 100
            variation = (user_hash - 50) / 100  # -0.5 to +0.5
            return base_per_user * Decimal(str(1 + variation))

        return Decimal('0.00')

    async def _get_applications_count(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of applications in period (integration with auto_apply)"""
        # Simulate application count based on period
        days = (end_date - start_date).days
        return max(1, int(days * 5))  # ~5 applications per day

    async def _get_user_applications_count(self, user_id: str, start_date: datetime, end_date: datetime) -> int:
        """Get applications count for specific user"""
        total_applications = await self._get_applications_count(start_date, end_date)
        total_users = await self._get_active_users_count()

        return max(1, total_applications // max(total_users, 1))

    async def _get_active_spiders_count(self) -> int:
        """Get count of active spiders (integration with pool_manager)"""
        return 1000  # From Phase 4 implementation

    async def _get_active_users_count(self) -> int:
        """Get count of active users"""
        return 25  # Estimated active users

    async def _get_spider_types(self) -> List[str]:
        """Get list of spider types"""
        return [
            'job_spider', 'freelance_spider', 'financial_spider',
            'news_spider', 'social_spider', 'business_spider'
        ]

    async def _calculate_revenue_growth(self, period_days: int) -> float:
        """Calculate revenue growth rate"""
        if len(self.roi_history) < 2:
            return 0.0

        # Compare with previous analysis of similar period
        previous_analysis = None
        for analysis in reversed(self.roi_history[:-1]):
            if analysis.time_period_days == period_days:
                previous_analysis = analysis
                break

        if not previous_analysis:
            return 0.0

        current_revenue = self.roi_history[-1].total_revenue
        previous_revenue = previous_analysis.total_revenue

        if previous_revenue > 0:
            growth_rate = float((current_revenue - previous_revenue) / previous_revenue * 100)
            return growth_rate

        return 0.0

    async def _calculate_cost_efficiency_trend(self, period_days: int) -> float:
        """Calculate cost efficiency trend (lower cost per dollar of revenue is better)"""
        if len(self.roi_history) < 2:
            return 0.0

        current_analysis = self.roi_history[-1]
        if current_analysis.total_revenue == 0:
            return 0.0

        current_efficiency = float(current_analysis.total_costs / current_analysis.total_revenue)

        # Find previous similar analysis
        previous_analysis = None
        for analysis in reversed(self.roi_history[:-1]):
            if analysis.time_period_days == period_days and analysis.total_revenue > 0:
                previous_analysis = analysis
                break

        if not previous_analysis:
            return 0.0

        previous_efficiency = float(previous_analysis.total_costs / previous_analysis.total_revenue)

        # Positive trend means efficiency is improving (costs are decreasing relative to revenue)
        if previous_efficiency > 0:
            efficiency_change = (previous_efficiency - current_efficiency) / previous_efficiency * 100
            return efficiency_change

        return 0.0

    async def _generate_roi_insights(
        self,
        system_roi: ROIAnalysis,
        spider_breakdown: Dict[str, Dict]
    ) -> List[str]:
        """Generate actionable ROI insights"""

        insights = []

        try:
            # ROI performance insights
            if system_roi.roi_percentage > 50:
                insights.append(f"Excellent ROI of {system_roi.roi_percentage:.1f}% - system is highly profitable")
            elif system_roi.roi_percentage > 20:
                insights.append(f"Good ROI of {system_roi.roi_percentage:.1f}% - solid performance")
            elif system_roi.roi_percentage > 0:
                insights.append(f"Positive ROI of {system_roi.roi_percentage:.1f}% - profitable but room for improvement")
            else:
                insights.append(f"Negative ROI of {system_roi.roi_percentage:.1f}% - urgent optimization needed")

            # Profit margin insights
            if system_roi.profit_margin < 10:
                insights.append("Low profit margin - consider cost reduction or pricing optimization")
            elif system_roi.profit_margin > 30:
                insights.append("Healthy profit margin - system is efficiently generating profit")

            # Break-even insights
            if system_roi.break_even_days and system_roi.break_even_days < 30:
                insights.append(f"Quick break-even in {system_roi.break_even_days} days - excellent capital efficiency")
            elif system_roi.break_even_days and system_roi.break_even_days > 90:
                insights.append(f"Long break-even period ({system_roi.break_even_days} days) - consider acceleration strategies")

            # Spider performance insights
            if spider_breakdown:
                best_spider = max(spider_breakdown.items(), key=lambda x: x[1]['roi_percentage'])
                worst_spider = min(spider_breakdown.items(), key=lambda x: x[1]['roi_percentage'])

                insights.append(f"Best performing spider: {best_spider[0]} with {best_spider[1]['roi_percentage']:.1f}% ROI")

                if worst_spider[1]['roi_percentage'] < 0:
                    insights.append(f"Consider optimizing {worst_spider[0]} spider - currently negative ROI")

                # Revenue concentration
                total_spider_revenue = sum(data['revenue'] for data in spider_breakdown.values())
                if total_spider_revenue > 0:
                    top_revenue_share = best_spider[1]['revenue'] / total_spider_revenue
                    if top_revenue_share > 0.5:
                        insights.append(f"Revenue heavily concentrated in {best_spider[0]} ({top_revenue_share*100:.1f}%) - consider diversification")

            # Growth insights
            if system_roi.revenue_growth_rate > 20:
                insights.append(f"Strong revenue growth of {system_roi.revenue_growth_rate:.1f}% - scaling effectively")
            elif system_roi.revenue_growth_rate < -10:
                insights.append(f"Revenue declining by {abs(system_roi.revenue_growth_rate):.1f}% - investigate issues")

            # Cost efficiency insights
            if system_roi.cost_efficiency_trend > 10:
                insights.append(f"Cost efficiency improving by {system_roi.cost_efficiency_trend:.1f}% - good optimization")
            elif system_roi.cost_efficiency_trend < -10:
                insights.append(f"Cost efficiency declining by {abs(system_roi.cost_efficiency_trend):.1f}% - review cost management")

        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            insights.append("Unable to generate detailed insights due to analysis error")

        return insights

    def get_statistics(self) -> Dict[str, Any]:
        """Get ROI calculator statistics"""

        recent_analyses = self.roi_history[-5:] if self.roi_history else []

        return {
            'total_analyses_performed': len(self.roi_history),
            'recent_roi_trend': [a.roi_percentage for a in recent_analyses],
            'avg_roi_last_5_analyses': statistics.mean([a.roi_percentage for a in recent_analyses]) if recent_analyses else 0.0,
            'best_roi_achieved': max([a.roi_percentage for a in self.roi_history]) if self.roi_history else 0.0,
            'total_cost_records': len(self.cost_tracker.cost_records),
            'cache_status': {
                'entries': len(self.metrics_cache),
                'ttl_seconds': self.cache_ttl
            }
        }


# Singleton instance
roi_calculator = ROICalculator()


# Public API functions
async def calculate_overall_roi(time_period_days: int = 30, include_human_costs: bool = True) -> ROIAnalysis:
    """Calculate system-wide ROI"""
    return await roi_calculator.calculate_system_roi(time_period_days, include_human_costs)


async def calculate_component_roi(component_type: str, component_id: str, time_period_days: int = 30) -> ROIAnalysis:
    """Calculate ROI for specific component (spider, user, etc.)"""
    if component_type == 'spider':
        return await roi_calculator.calculate_spider_roi(component_id, time_period_days)
    elif component_type == 'user':
        return await roi_calculator.calculate_user_roi(component_id, time_period_days)
    else:
        logger.error(f"Unknown component type: {component_type}")
        return ROIAnalysis(metric_type=ROIMetricType.SYSTEM_ROI, time_period_days=time_period_days)


async def add_system_cost(
    category: str,
    description: str,
    amount: float,
    recurring: bool = False,
    allocated_to: Optional[str] = None
) -> str:
    """Add a system cost record"""
    try:
        cost_category = CostCategory(category)
    except ValueError:
        cost_category = CostCategory.THIRD_PARTY  # Default fallback

    return await roi_calculator.cost_tracker.add_cost_record(
        cost_category, description, amount, recurring, allocated_to
    )


async def generate_comprehensive_roi_report(
    time_period_days: int = 30,
    include_breakdowns: bool = True
) -> Dict[str, Any]:
    """Generate detailed ROI report"""
    return await roi_calculator.generate_roi_report(time_period_days, include_breakdowns)


def get_roi_calculator_stats() -> Dict[str, Any]:
    """Get ROI calculator statistics"""
    return roi_calculator.get_statistics()