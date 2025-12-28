"""
A/B Testing Framework
Phase 5: Activate Money-Making Pipeline - Optimization & Experimentation

This module provides comprehensive A/B testing capabilities for optimizing
proposal templates, application strategies, and revenue generation approaches.
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """A/B test experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VariantType(Enum):
    """Types of A/B test variants"""
    CONTROL = "control"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"
    VARIANT_C = "variant_c"
    VARIANT_D = "variant_d"


@dataclass
class ExperimentVariant:
    """Individual variant in an A/B test"""
    id: str
    name: str
    variant_type: VariantType
    traffic_allocation: float  # 0.0 to 1.0
    config: Dict[str, Any]  # Variant-specific configuration
    description: str = ""
    is_control: bool = False


@dataclass
class ExperimentResult:
    """Results for a single variant"""
    variant_id: str
    variant_name: str

    # Traffic metrics
    total_users: int = 0
    total_conversions: int = 0
    conversion_rate: float = 0.0

    # Business metrics
    revenue_generated: float = 0.0
    avg_revenue_per_user: float = 0.0
    response_rate: float = 0.0
    acceptance_rate: float = 0.0

    # Statistical metrics
    confidence_level: float = 0.0
    statistical_significance: bool = False
    p_value: float = 1.0

    # Performance metrics
    avg_response_time_hours: float = 0.0
    client_satisfaction: float = 0.0

    # Metadata
    sample_size: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class ABExperiment:
    """A/B test experiment definition"""
    id: str
    name: str
    description: str
    hypothesis: str
    success_metric: str  # Primary metric to optimize

    # Experiment configuration
    variants: List[ExperimentVariant]
    traffic_allocation: Dict[str, float]  # variant_id -> allocation
    duration_days: int = 14
    min_sample_size: int = 100

    # Status and timing
    status: ExperimentStatus = ExperimentStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Results
    results: Dict[str, ExperimentResult] = field(default_factory=dict)
    winner_variant_id: Optional[str] = None
    confidence_level: float = 95.0

    # Metadata
    created_by: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UserAssignment:
    """User assignment to experiment variant"""
    user_id: str
    experiment_id: str
    variant_id: str
    assigned_at: datetime
    conversion_events: List[Dict[str, Any]] = field(default_factory=list)


class StatisticalAnalyzer:
    """Statistical analysis for A/B testing"""

    def __init__(self):
        self.confidence_levels = {
            90: 1.645,  # Z-score for 90% confidence
            95: 1.96,   # Z-score for 95% confidence
            99: 2.576   # Z-score for 99% confidence
        }

    def calculate_statistical_significance(
        self,
        control_conversions: int,
        control_sample_size: int,
        variant_conversions: int,
        variant_sample_size: int,
        confidence_level: float = 95.0
    ) -> Tuple[bool, float]:
        """Calculate statistical significance between control and variant"""

        if control_sample_size == 0 or variant_sample_size == 0:
            return False, 1.0

        # Calculate conversion rates
        control_rate = control_conversions / control_sample_size
        variant_rate = variant_conversions / variant_sample_size

        # Calculate pooled probability
        pooled_prob = (control_conversions + variant_conversions) / (control_sample_size + variant_sample_size)

        if pooled_prob == 0 or pooled_prob == 1:
            return False, 1.0

        # Calculate standard error
        se = math.sqrt(pooled_prob * (1 - pooled_prob) * (1/control_sample_size + 1/variant_sample_size))

        if se == 0:
            return False, 1.0

        # Calculate Z-score
        z_score = abs(control_rate - variant_rate) / se

        # Calculate p-value (two-tailed test)
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))

        # Check significance
        alpha = (100 - confidence_level) / 100
        is_significant = p_value < alpha

        return is_significant, p_value

    def _normal_cdf(self, x):
        """Approximation of the normal cumulative distribution function"""
        # Using a simple approximation - in production, use scipy.stats.norm
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def calculate_minimum_sample_size(
        self,
        baseline_rate: float,
        minimum_detectable_effect: float,
        confidence_level: float = 95.0,
        statistical_power: float = 0.8
    ) -> int:
        """Calculate minimum sample size needed for experiment"""

        if baseline_rate <= 0 or baseline_rate >= 1:
            return 1000  # Default fallback

        # Get Z-scores
        z_alpha = self.confidence_levels.get(int(confidence_level), 1.96)
        z_beta = 0.84  # For 80% power

        # Calculate effect size
        variant_rate = baseline_rate * (1 + minimum_detectable_effect)
        effect_size = abs(variant_rate - baseline_rate)

        if effect_size == 0:
            return 10000  # Large sample for no effect

        # Calculate sample size per variant
        numerator = (z_alpha + z_beta) ** 2
        denominator = effect_size ** 2
        pooled_variance = baseline_rate * (1 - baseline_rate) + variant_rate * (1 - variant_rate)

        sample_size = int(numerator * pooled_variance / denominator) + 1

        return max(sample_size, 50)  # Minimum of 50 per variant

    def calculate_confidence_interval(
        self,
        conversions: int,
        sample_size: int,
        confidence_level: float = 95.0
    ) -> Tuple[float, float]:
        """Calculate confidence interval for conversion rate"""

        if sample_size == 0:
            return 0.0, 0.0

        conversion_rate = conversions / sample_size
        z_score = self.confidence_levels.get(int(confidence_level), 1.96)

        # Calculate standard error
        se = math.sqrt(conversion_rate * (1 - conversion_rate) / sample_size)

        # Calculate confidence interval
        margin_of_error = z_score * se
        lower_bound = max(0, conversion_rate - margin_of_error)
        upper_bound = min(1, conversion_rate + margin_of_error)

        return lower_bound, upper_bound

    def calculate_lift(self, control_rate: float, variant_rate: float) -> float:
        """Calculate percentage lift of variant over control"""
        if control_rate == 0:
            return 0.0
        return ((variant_rate - control_rate) / control_rate) * 100


class ABTestingFramework:
    """Main A/B testing framework"""

    def __init__(self):
        self.experiments: Dict[str, ABExperiment] = {}
        self.user_assignments: Dict[str, List[UserAssignment]] = defaultdict(list)
        self.analyzer = StatisticalAnalyzer()

        # Framework statistics
        self.stats = {
            'total_experiments': 0,
            'running_experiments': 0,
            'completed_experiments': 0,
            'total_users_tested': 0,
            'total_conversions': 0,
            'avg_conversion_rate': 0.0,
            'significant_wins': 0
        }

        logger.info("🧪 A/B Testing Framework initialized")

    async def create_experiment(
        self,
        name: str,
        description: str,
        hypothesis: str,
        variants: List[Dict[str, Any]],
        success_metric: str = "conversion_rate",
        duration_days: int = 14,
        confidence_level: float = 95.0
    ) -> str:
        """Create a new A/B test experiment"""

        try:
            experiment_id = str(uuid.uuid4())

            # Create experiment variants
            experiment_variants = []
            total_allocation = 0.0

            for i, variant_config in enumerate(variants):
                variant_id = str(uuid.uuid4())
                allocation = variant_config.get('traffic_allocation', 1.0 / len(variants))

                variant = ExperimentVariant(
                    id=variant_id,
                    name=variant_config.get('name', f'Variant {chr(65+i)}'),  # A, B, C, etc.
                    variant_type=VariantType(variant_config.get('type', 'variant_a')),
                    traffic_allocation=allocation,
                    config=variant_config.get('config', {}),
                    description=variant_config.get('description', ''),
                    is_control=variant_config.get('is_control', i == 0)
                )

                experiment_variants.append(variant)
                total_allocation += allocation

            # Normalize allocations to sum to 1.0
            if total_allocation > 0:
                for variant in experiment_variants:
                    variant.traffic_allocation = variant.traffic_allocation / total_allocation

            # Create traffic allocation map
            traffic_allocation = {v.id: v.traffic_allocation for v in experiment_variants}

            # Create experiment
            experiment = ABExperiment(
                id=experiment_id,
                name=name,
                description=description,
                hypothesis=hypothesis,
                success_metric=success_metric,
                variants=experiment_variants,
                traffic_allocation=traffic_allocation,
                duration_days=duration_days,
                confidence_level=confidence_level
            )

            self.experiments[experiment_id] = experiment
            self.stats['total_experiments'] += 1

            logger.info(f"🧪 Created experiment: {name} ({experiment_id})")
            return experiment_id

        except Exception as e:
            logger.error(f"❌ Error creating experiment: {e}")
            return ""

    async def start_experiment(self, experiment_id: str) -> bool:
        """Start running an A/B test experiment"""

        if experiment_id not in self.experiments:
            logger.error(f"❌ Experiment not found: {experiment_id}")
            return False

        try:
            experiment = self.experiments[experiment_id]

            if experiment.status != ExperimentStatus.DRAFT:
                logger.error(f"❌ Experiment {experiment_id} is not in draft status")
                return False

            # Validate experiment configuration
            if not experiment.variants or len(experiment.variants) < 2:
                logger.error(f"❌ Experiment needs at least 2 variants")
                return False

            # Start experiment
            experiment.status = ExperimentStatus.RUNNING
            experiment.start_date = datetime.now()
            experiment.end_date = datetime.now() + timedelta(days=experiment.duration_days)
            experiment.updated_at = datetime.now()

            # Initialize results for each variant
            for variant in experiment.variants:
                experiment.results[variant.id] = ExperimentResult(
                    variant_id=variant.id,
                    variant_name=variant.name,
                    start_date=experiment.start_date
                )

            self.stats['running_experiments'] += 1

            logger.info(f"🚀 Started experiment: {experiment.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error starting experiment: {e}")
            return False

    async def assign_user_to_variant(
        self,
        user_id: str,
        experiment_id: str
    ) -> Optional[str]:
        """Assign a user to a variant in an experiment"""

        if experiment_id not in self.experiments:
            logger.error(f"❌ Experiment not found: {experiment_id}")
            return None

        experiment = self.experiments[experiment_id]

        if experiment.status != ExperimentStatus.RUNNING:
            logger.error(f"❌ Experiment {experiment_id} is not running")
            return None

        try:
            # Check if user already assigned
            existing_assignments = [a for a in self.user_assignments[user_id] if a.experiment_id == experiment_id]
            if existing_assignments:
                return existing_assignments[0].variant_id

            # Hash user ID for consistent assignment
            hash_input = f"{user_id}_{experiment_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            random_value = (hash_value % 10000) / 10000.0  # 0.0 to 1.0

            # Assign based on traffic allocation
            cumulative_allocation = 0.0
            selected_variant_id = None

            for variant in experiment.variants:
                cumulative_allocation += variant.traffic_allocation
                if random_value <= cumulative_allocation:
                    selected_variant_id = variant.id
                    break

            if not selected_variant_id:
                # Fallback to control variant
                control_variants = [v for v in experiment.variants if v.is_control]
                selected_variant_id = control_variants[0].id if control_variants else experiment.variants[0].id

            # Create assignment record
            assignment = UserAssignment(
                user_id=user_id,
                experiment_id=experiment_id,
                variant_id=selected_variant_id,
                assigned_at=datetime.now()
            )

            self.user_assignments[user_id].append(assignment)

            logger.debug(f"👤 Assigned user {user_id} to variant {selected_variant_id}")
            return selected_variant_id

        except Exception as e:
            logger.error(f"❌ Error assigning user to variant: {e}")
            return None

    async def track_conversion(
        self,
        user_id: str,
        experiment_id: str,
        conversion_type: str = "conversion",
        revenue: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track a conversion event for a user in an experiment"""

        if experiment_id not in self.experiments:
            logger.error(f"❌ Experiment not found: {experiment_id}")
            return False

        try:
            experiment = self.experiments[experiment_id]

            # Find user's assignment
            user_assignments = [a for a in self.user_assignments[user_id] if a.experiment_id == experiment_id]
            if not user_assignments:
                logger.error(f"❌ User {user_id} not assigned to experiment {experiment_id}")
                return False

            assignment = user_assignments[0]
            variant_id = assignment.variant_id

            # Record conversion event
            conversion_event = {
                'type': conversion_type,
                'timestamp': datetime.now().isoformat(),
                'revenue': revenue,
                'metadata': metadata or {}
            }

            assignment.conversion_events.append(conversion_event)

            # Update experiment results
            if variant_id in experiment.results:
                result = experiment.results[variant_id]
                result.total_conversions += 1
                result.revenue_generated += revenue

                # Recalculate metrics
                await self._update_experiment_results(experiment_id)

            self.stats['total_conversions'] += 1

            logger.debug(f"📊 Tracked conversion for user {user_id} in experiment {experiment_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error tracking conversion: {e}")
            return False

    async def _update_experiment_results(self, experiment_id: str):
        """Update statistical results for an experiment"""

        if experiment_id not in self.experiments:
            return

        try:
            experiment = self.experiments[experiment_id]

            # Count users and conversions per variant
            variant_users = defaultdict(set)
            variant_conversions = defaultdict(int)
            variant_revenues = defaultdict(float)

            for user_id, assignments in self.user_assignments.items():
                for assignment in assignments:
                    if assignment.experiment_id == experiment_id:
                        variant_users[assignment.variant_id].add(user_id)
                        variant_conversions[assignment.variant_id] += len(assignment.conversion_events)
                        variant_revenues[assignment.variant_id] += sum(
                            event.get('revenue', 0.0) for event in assignment.conversion_events
                        )

            # Update results for each variant
            control_variant = None
            for variant in experiment.variants:
                if variant.is_control:
                    control_variant = variant
                    break

            for variant in experiment.variants:
                result = experiment.results[variant.id]

                # Basic metrics
                result.total_users = len(variant_users[variant.id])
                result.total_conversions = variant_conversions[variant.id]
                result.revenue_generated = variant_revenues[variant.id]

                # Calculated metrics
                if result.total_users > 0:
                    result.conversion_rate = result.total_conversions / result.total_users
                    result.avg_revenue_per_user = result.revenue_generated / result.total_users
                else:
                    result.conversion_rate = 0.0
                    result.avg_revenue_per_user = 0.0

                result.sample_size = result.total_users

                # Statistical significance (compare to control)
                if control_variant and variant.id != control_variant.id:
                    control_result = experiment.results[control_variant.id]

                    if control_result.total_users > 0 and result.total_users > 0:
                        is_significant, p_value = self.analyzer.calculate_statistical_significance(
                            control_result.total_conversions,
                            control_result.total_users,
                            result.total_conversions,
                            result.total_users,
                            experiment.confidence_level
                        )

                        result.statistical_significance = is_significant
                        result.p_value = p_value
                        result.confidence_level = experiment.confidence_level

        except Exception as e:
            logger.error(f"❌ Error updating experiment results: {e}")

    async def get_experiment_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive results for an experiment"""

        if experiment_id not in self.experiments:
            logger.error(f"❌ Experiment not found: {experiment_id}")
            return None

        try:
            experiment = self.experiments[experiment_id]

            # Update results first
            await self._update_experiment_results(experiment_id)

            # Find control and best performing variant
            control_variant = None
            best_variant = None
            best_conversion_rate = 0.0

            for variant in experiment.variants:
                if variant.is_control:
                    control_variant = variant

                result = experiment.results[variant.id]
                if result.conversion_rate > best_conversion_rate:
                    best_conversion_rate = result.conversion_rate
                    best_variant = variant

            # Calculate overall metrics
            total_users = sum(r.total_users for r in experiment.results.values())
            total_conversions = sum(r.total_conversions for r in experiment.results.values())
            total_revenue = sum(r.revenue_generated for r in experiment.results.values())

            overall_conversion_rate = (total_conversions / total_users) if total_users > 0 else 0.0

            # Prepare results summary
            variant_results = {}
            for variant in experiment.variants:
                result = experiment.results[variant.id]

                # Calculate lift vs control
                lift = 0.0
                if control_variant and control_variant.id != variant.id:
                    control_result = experiment.results[control_variant.id]
                    if control_result.conversion_rate > 0:
                        lift = self.analyzer.calculate_lift(
                            control_result.conversion_rate,
                            result.conversion_rate
                        )

                # Calculate confidence interval
                lower_bound, upper_bound = self.analyzer.calculate_confidence_interval(
                    result.total_conversions,
                    result.total_users,
                    experiment.confidence_level
                )

                variant_results[variant.id] = {
                    'variant_name': variant.name,
                    'variant_type': variant.variant_type.value,
                    'is_control': variant.is_control,
                    'traffic_allocation': variant.traffic_allocation,
                    'total_users': result.total_users,
                    'total_conversions': result.total_conversions,
                    'conversion_rate': result.conversion_rate * 100,  # As percentage
                    'revenue_generated': result.revenue_generated,
                    'avg_revenue_per_user': result.avg_revenue_per_user,
                    'statistical_significance': result.statistical_significance,
                    'confidence_level': result.confidence_level,
                    'p_value': result.p_value,
                    'lift_vs_control': lift,
                    'confidence_interval': [lower_bound * 100, upper_bound * 100]
                }

            results_summary = {
                'experiment_id': experiment_id,
                'experiment_name': experiment.name,
                'status': experiment.status.value,
                'hypothesis': experiment.hypothesis,
                'success_metric': experiment.success_metric,
                'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
                'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
                'days_running': (datetime.now() - experiment.start_date).days if experiment.start_date else 0,
                'overall_metrics': {
                    'total_users': total_users,
                    'total_conversions': total_conversions,
                    'overall_conversion_rate': overall_conversion_rate * 100,
                    'total_revenue': total_revenue,
                    'avg_revenue_per_user': total_revenue / total_users if total_users > 0 else 0.0
                },
                'variants': variant_results,
                'winner': {
                    'variant_id': best_variant.id if best_variant else None,
                    'variant_name': best_variant.name if best_variant else None,
                    'conversion_rate': best_conversion_rate * 100
                } if best_variant else None,
                'recommendations': await self._generate_recommendations(experiment)
            }

            return results_summary

        except Exception as e:
            logger.error(f"❌ Error getting experiment results: {e}")
            return None

    async def _generate_recommendations(self, experiment: ABExperiment) -> List[str]:
        """Generate recommendations based on experiment results"""

        recommendations = []

        try:
            # Check if experiment has sufficient data
            total_users = sum(r.total_users for r in experiment.results.values())

            if total_users < experiment.min_sample_size:
                recommendations.append(f"Experiment needs more data (current: {total_users}, minimum: {experiment.min_sample_size})")
                return recommendations

            # Find control and best performer
            control_result = None
            best_result = None
            best_conversion_rate = 0.0

            for variant in experiment.variants:
                result = experiment.results[variant.id]

                if variant.is_control:
                    control_result = result

                if result.conversion_rate > best_conversion_rate:
                    best_conversion_rate = result.conversion_rate
                    best_result = result

            # Generate specific recommendations
            if control_result and best_result and best_result != control_result:

                if best_result.statistical_significance:
                    lift = self.analyzer.calculate_lift(
                        control_result.conversion_rate,
                        best_result.conversion_rate
                    )
                    recommendations.append(
                        f"Winner found! {best_result.variant_name} shows {lift:.1f}% improvement with statistical significance"
                    )
                    recommendations.append("Consider implementing the winning variant")
                else:
                    recommendations.append("Best performing variant is not statistically significant yet")
                    recommendations.append("Continue running experiment or increase traffic allocation")

            # Revenue-based recommendations
            revenue_results = sorted(
                experiment.results.values(),
                key=lambda r: r.revenue_generated,
                reverse=True
            )

            if revenue_results and revenue_results[0].revenue_generated > 0:
                top_revenue = revenue_results[0]
                recommendations.append(
                    f"{top_revenue.variant_name} generates highest revenue (${top_revenue.revenue_generated:.2f})"
                )

            # Duration recommendations
            if experiment.start_date:
                days_running = (datetime.now() - experiment.start_date).days
                if days_running < 7:
                    recommendations.append("Run experiment for at least 7 days to account for weekly patterns")
                elif days_running > 30:
                    recommendations.append("Consider concluding experiment - running for over 30 days")

        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            recommendations.append("Error generating recommendations")

        return recommendations

    async def conclude_experiment(self, experiment_id: str, winner_variant_id: Optional[str] = None) -> bool:
        """Conclude an A/B test experiment"""

        if experiment_id not in self.experiments:
            logger.error(f"❌ Experiment not found: {experiment_id}")
            return False

        try:
            experiment = self.experiments[experiment_id]

            if experiment.status != ExperimentStatus.RUNNING:
                logger.error(f"❌ Experiment {experiment_id} is not running")
                return False

            # Update final results
            await self._update_experiment_results(experiment_id)

            # Determine winner if not specified
            if not winner_variant_id:
                best_conversion_rate = 0.0
                for variant in experiment.variants:
                    result = experiment.results[variant.id]
                    if result.conversion_rate > best_conversion_rate:
                        best_conversion_rate = result.conversion_rate
                        winner_variant_id = variant.id

            # Update experiment status
            experiment.status = ExperimentStatus.COMPLETED
            experiment.end_date = datetime.now()
            experiment.winner_variant_id = winner_variant_id
            experiment.updated_at = datetime.now()

            # Update statistics
            self.stats['running_experiments'] -= 1
            self.stats['completed_experiments'] += 1

            # Check if winner is statistically significant
            if winner_variant_id:
                winner_result = experiment.results[winner_variant_id]
                if winner_result.statistical_significance:
                    self.stats['significant_wins'] += 1

            logger.info(f"🏁 Concluded experiment: {experiment.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error concluding experiment: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get A/B testing framework statistics"""

        # Calculate overall metrics
        total_users = len(self.user_assignments)
        avg_conversion_rate = 0.0

        if self.stats['total_conversions'] > 0 and total_users > 0:
            avg_conversion_rate = (self.stats['total_conversions'] / total_users) * 100

        # Update stats
        self.stats['total_users_tested'] = total_users
        self.stats['avg_conversion_rate'] = avg_conversion_rate

        return {
            'framework_stats': self.stats,
            'active_experiments': [
                {
                    'id': exp.id,
                    'name': exp.name,
                    'status': exp.status.value,
                    'days_running': (datetime.now() - exp.start_date).days if exp.start_date else 0,
                    'total_users': sum(r.total_users for r in exp.results.values())
                }
                for exp in self.experiments.values()
                if exp.status == ExperimentStatus.RUNNING
            ]
        }

    async def get_user_experiments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all experiments a user is participating in"""

        user_experiments = []

        try:
            assignments = self.user_assignments.get(user_id, [])

            for assignment in assignments:
                if assignment.experiment_id in self.experiments:
                    experiment = self.experiments[assignment.experiment_id]
                    variant = next(
                        (v for v in experiment.variants if v.id == assignment.variant_id),
                        None
                    )

                    if variant:
                        user_experiments.append({
                            'experiment_id': assignment.experiment_id,
                            'experiment_name': experiment.name,
                            'variant_id': assignment.variant_id,
                            'variant_name': variant.name,
                            'variant_config': variant.config,
                            'assigned_at': assignment.assigned_at.isoformat(),
                            'conversion_events': len(assignment.conversion_events)
                        })

        except Exception as e:
            logger.error(f"❌ Error getting user experiments: {e}")

        return user_experiments


# Singleton instance
ab_testing_framework = ABTestingFramework()


# Public API functions
async def create_ab_test(
    name: str,
    description: str,
    hypothesis: str,
    variants: List[Dict[str, Any]],
    success_metric: str = "conversion_rate",
    duration_days: int = 14
) -> str:
    """Create a new A/B test experiment"""
    return await ab_testing_framework.create_experiment(
        name, description, hypothesis, variants, success_metric, duration_days
    )


async def start_ab_test(experiment_id: str) -> bool:
    """Start an A/B test experiment"""
    return await ab_testing_framework.start_experiment(experiment_id)


async def assign_user_to_test(user_id: str, experiment_id: str) -> Optional[str]:
    """Assign user to A/B test variant"""
    return await ab_testing_framework.assign_user_to_variant(user_id, experiment_id)


async def track_ab_conversion(
    user_id: str,
    experiment_id: str,
    conversion_type: str = "conversion",
    revenue: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Track A/B test conversion"""
    return await ab_testing_framework.track_conversion(
        user_id, experiment_id, conversion_type, revenue, metadata
    )


async def get_ab_test_results(experiment_id: str) -> Optional[Dict[str, Any]]:
    """Get A/B test results"""
    return await ab_testing_framework.get_experiment_results(experiment_id)


async def conclude_ab_test(experiment_id: str, winner_variant_id: Optional[str] = None) -> bool:
    """Conclude A/B test"""
    return await ab_testing_framework.conclude_experiment(experiment_id, winner_variant_id)


def get_ab_testing_stats() -> Dict[str, Any]:
    """Get A/B testing statistics"""
    return ab_testing_framework.get_statistics()


async def get_user_ab_tests(user_id: str) -> List[Dict[str, Any]]:
    """Get user's A/B test participations"""
    return await ab_testing_framework.get_user_experiments(user_id)