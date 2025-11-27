"""
A/B Testing Service for Session 211

Provides a complete framework for running A/B experiments on style recommendations,
UI variations, and other features. Includes:
- Experiment creation and management
- Consistent user assignment (sticky bucketing)
- Conversion tracking
- Statistical significance calculation
"""

import logging
import hashlib
import math
import random
from typing import Dict, Any, Optional, List
from datetime import timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExperimentVariant:
    """Represents a variant assignment for a user."""
    experiment_id: str
    experiment_name: str
    variant_id: str
    variant_name: str
    config: Dict[str, Any]
    is_control: bool


class ABTestingService:
    """
    A/B Testing Service for running experiments.

    Features:
    - Create and manage experiments
    - Assign users to variants (consistent/sticky)
    - Track conversions
    - Calculate statistical significance
    """

    def __init__(self):
        self._cache = {}  # In-memory cache for assignments

    # ==================== Experiment Management ====================

    def create_experiment(
        self,
        name: str,
        description: str = '',
        experiment_type: str = 'recommendation',
        domain: str = 'style_recommendations',
        traffic_percentage: int = 100,
        variants: List[Dict] = None,
        config: Dict = None,
        created_by_id: int = None,
    ) -> Dict[str, Any]:
        """
        Create a new A/B experiment.

        Args:
            name: Experiment name
            description: What this experiment tests
            experiment_type: recommendation, ui, feature, algorithm
            domain: Area of the app being tested
            traffic_percentage: % of users to include (0-100)
            variants: List of variant configs [{"name": "control", "is_control": True, "weight": 50, "config": {...}}]
            config: Additional experiment configuration
            created_by_id: User ID of creator

        Returns:
            Created experiment details
        """
        from django.utils import timezone
        from core.models_unified_system import ABExperiment, ABVariant

        try:
            # Create experiment
            experiment = ABExperiment.objects.create(
                name=name,
                description=description,
                experiment_type=experiment_type,
                domain=domain,
                traffic_percentage=traffic_percentage,
                config=config or {},
                created_by_id=created_by_id,
                status='draft',
            )

            # Create variants
            if not variants:
                # Default to 50/50 split
                variants = [
                    {'name': 'control', 'is_control': True, 'weight': 50, 'config': {}},
                    {'name': 'variant_a', 'is_control': False, 'weight': 50, 'config': {}},
                ]

            created_variants = []
            for v in variants:
                variant = ABVariant.objects.create(
                    experiment=experiment,
                    name=v.get('name', 'variant'),
                    description=v.get('description', ''),
                    is_control=v.get('is_control', False),
                    weight=v.get('weight', 50),
                    config=v.get('config', {}),
                )
                created_variants.append({
                    'id': str(variant.id),
                    'name': variant.name,
                    'is_control': variant.is_control,
                    'weight': variant.weight,
                    'config': variant.config,
                })

            logger.info(f"Created experiment '{name}' with {len(created_variants)} variants")

            return {
                'id': str(experiment.id),
                'name': experiment.name,
                'status': experiment.status,
                'variants': created_variants,
                'traffic_percentage': experiment.traffic_percentage,
            }

        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            raise

    def start_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Start an experiment (set status to 'running')."""
        from django.utils import timezone
        from core.models_unified_system import ABExperiment

        try:
            experiment = ABExperiment.objects.get(id=experiment_id)
            experiment.status = 'running'
            experiment.start_date = timezone.now()
            experiment.save()

            logger.info(f"Started experiment '{experiment.name}'")
            return {'id': str(experiment.id), 'status': 'running', 'started_at': str(experiment.start_date)}

        except ABExperiment.DoesNotExist:
            raise ValueError(f"Experiment {experiment_id} not found")

    def stop_experiment(self, experiment_id: str, status: str = 'completed') -> Dict[str, Any]:
        """Stop an experiment."""
        from django.utils import timezone
        from core.models_unified_system import ABExperiment

        try:
            experiment = ABExperiment.objects.get(id=experiment_id)
            experiment.status = status
            experiment.end_date = timezone.now()
            experiment.save()

            logger.info(f"Stopped experiment '{experiment.name}' with status '{status}'")
            return {'id': str(experiment.id), 'status': status, 'ended_at': str(experiment.end_date)}

        except ABExperiment.DoesNotExist:
            raise ValueError(f"Experiment {experiment_id} not found")

    def get_active_experiments(self, domain: str = None) -> List[Dict]:
        """Get all currently running experiments."""
        from core.models_unified_system import ABExperiment

        qs = ABExperiment.objects.filter(status='running')
        if domain:
            qs = qs.filter(domain=domain)

        return [
            {
                'id': str(e.id),
                'name': e.name,
                'domain': e.domain,
                'experiment_type': e.experiment_type,
                'traffic_percentage': e.traffic_percentage,
                'start_date': str(e.start_date) if e.start_date else None,
            }
            for e in qs
        ]

    # ==================== User Assignment ====================

    def get_variant_for_user(
        self,
        experiment_id: str,
        user_id: int = None,
        session_id: str = None,
    ) -> Optional[ExperimentVariant]:
        """
        Get the variant assignment for a user.

        Uses consistent hashing for sticky assignment - user always gets same variant.

        Args:
            experiment_id: Experiment to check
            user_id: Authenticated user ID
            session_id: Session ID for anonymous users

        Returns:
            ExperimentVariant or None if not in experiment
        """
        from core.models_unified_system import ABExperiment, ABAssignment, ABVariant

        try:
            experiment = ABExperiment.objects.get(id=experiment_id)

            if not experiment.is_active:
                return None

            # Check if user is in traffic sample
            if not self._is_in_traffic_sample(experiment, user_id, session_id):
                return None

            # Check for existing assignment
            assignment = self._get_existing_assignment(experiment, user_id, session_id)

            if assignment:
                return ExperimentVariant(
                    experiment_id=str(experiment.id),
                    experiment_name=experiment.name,
                    variant_id=str(assignment.variant.id),
                    variant_name=assignment.variant.name,
                    config=assignment.variant.config,
                    is_control=assignment.variant.is_control,
                )

            # Create new assignment
            variant = self._assign_variant(experiment, user_id, session_id)

            return ExperimentVariant(
                experiment_id=str(experiment.id),
                experiment_name=experiment.name,
                variant_id=str(variant.id),
                variant_name=variant.name,
                config=variant.config,
                is_control=variant.is_control,
            )

        except ABExperiment.DoesNotExist:
            logger.warning(f"Experiment {experiment_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting variant for user: {e}")
            return None

    def _is_in_traffic_sample(self, experiment, user_id: int, session_id: str) -> bool:
        """Check if user is in the traffic sample for this experiment."""
        if experiment.traffic_percentage >= 100:
            return True

        # Use consistent hash to determine if in sample
        identifier = str(user_id) if user_id else session_id
        hash_input = f"{experiment.id}:{identifier}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        bucket = hash_value % 100

        return bucket < experiment.traffic_percentage

    def _get_existing_assignment(self, experiment, user_id: int, session_id: str):
        """Get existing assignment if one exists."""
        from core.models_unified_system import ABAssignment

        if user_id:
            return ABAssignment.objects.filter(
                experiment=experiment,
                user_id=user_id
            ).select_related('variant').first()
        elif session_id:
            return ABAssignment.objects.filter(
                experiment=experiment,
                session_id=session_id
            ).select_related('variant').first()
        return None

    def _assign_variant(self, experiment, user_id: int, session_id: str):
        """Assign a user to a variant based on weights."""
        from core.models_unified_system import ABAssignment, ABVariant

        # Get all variants with weights
        variants = list(experiment.variants.all())
        total_weight = sum(v.weight for v in variants)

        # Use consistent hash for deterministic assignment
        identifier = str(user_id) if user_id else session_id
        hash_input = f"{experiment.id}:variant:{identifier}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        bucket = hash_value % total_weight

        # Find which variant this bucket falls into
        cumulative = 0
        selected_variant = variants[0]
        for variant in variants:
            cumulative += variant.weight
            if bucket < cumulative:
                selected_variant = variant
                break

        # Create assignment
        assignment = ABAssignment.objects.create(
            experiment=experiment,
            variant=selected_variant,
            user_id=user_id or 0,
            session_id=session_id,
        )

        logger.debug(f"Assigned user to variant '{selected_variant.name}' in experiment '{experiment.name}'")
        return selected_variant

    def mark_exposure(self, experiment_id: str, user_id: int = None, session_id: str = None):
        """Mark that a user has been exposed to their variant (seen it)."""
        from django.utils import timezone
        from core.models_unified_system import ABExperiment, ABAssignment

        try:
            experiment = ABExperiment.objects.get(id=experiment_id)
            assignment = self._get_existing_assignment(experiment, user_id, session_id)

            if assignment and not assignment.exposed:
                assignment.exposed = True
                assignment.exposed_at = timezone.now()
                assignment.save()
                logger.debug(f"Marked exposure for experiment '{experiment.name}'")

        except Exception as e:
            logger.error(f"Error marking exposure: {e}")

    # ==================== Conversion Tracking ====================

    def track_conversion(
        self,
        experiment_id: str,
        conversion_type: str,
        user_id: int = None,
        session_id: str = None,
        value: float = 1.0,
        metadata: Dict = None,
    ) -> bool:
        """
        Track a conversion for an experiment.

        Args:
            experiment_id: The experiment
            conversion_type: click, apply, download, share, purchase, signup, engagement
            user_id: User ID
            session_id: Session ID for anonymous users
            value: Numeric value of conversion (default 1.0)
            metadata: Additional conversion data

        Returns:
            True if conversion was recorded
        """
        from core.models_unified_system import ABExperiment, ABAssignment, ABConversion

        try:
            experiment = ABExperiment.objects.get(id=experiment_id)
            assignment = self._get_existing_assignment(experiment, user_id, session_id)

            if not assignment:
                logger.warning(f"No assignment found for conversion tracking")
                return False

            # Create conversion
            ABConversion.objects.create(
                assignment=assignment,
                conversion_type=conversion_type,
                value=value,
                metadata=metadata or {},
            )

            logger.debug(f"Recorded conversion '{conversion_type}' for experiment '{experiment.name}'")
            return True

        except ABExperiment.DoesNotExist:
            logger.warning(f"Experiment {experiment_id} not found for conversion")
            return False
        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
            return False

    # ==================== Results & Statistics ====================

    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get comprehensive results for an experiment.

        Includes per-variant stats and statistical significance.
        """
        from core.models_unified_system import (
            ABExperiment, ABVariant, ABAssignment, ABConversion
        )
        from django.db.models import Count, Sum, Avg

        try:
            experiment = ABExperiment.objects.get(id=experiment_id)

            # Get stats per variant
            variant_stats = {}
            control_rate = None

            for variant in experiment.variants.all():
                assignments = ABAssignment.objects.filter(variant=variant)
                total_assignments = assignments.count()
                total_exposures = assignments.filter(exposed=True).count()

                conversions = ABConversion.objects.filter(assignment__variant=variant)
                total_conversions = conversions.count()
                total_value = conversions.aggregate(total=Sum('value'))['total'] or 0

                conversion_rate = total_conversions / max(1, total_exposures)

                variant_stats[str(variant.id)] = {
                    'name': variant.name,
                    'is_control': variant.is_control,
                    'assignments': total_assignments,
                    'exposures': total_exposures,
                    'conversions': total_conversions,
                    'conversion_rate': round(conversion_rate, 4),
                    'total_value': round(total_value, 2),
                    'avg_value': round(total_value / max(1, total_conversions), 2),
                }

                if variant.is_control:
                    control_rate = conversion_rate

            # Calculate statistical significance
            significance = self._calculate_significance(variant_stats, control_rate)

            # Find winner
            winner = None
            lift = None
            if significance.get('is_significant') and control_rate is not None:
                best_variant = max(
                    [(vid, vs) for vid, vs in variant_stats.items() if not vs['is_control']],
                    key=lambda x: x[1]['conversion_rate'],
                    default=(None, None)
                )
                if best_variant[0] and best_variant[1]['conversion_rate'] > control_rate:
                    winner = best_variant[1]['name']
                    lift = ((best_variant[1]['conversion_rate'] - control_rate) / max(0.001, control_rate)) * 100

            total_sample = sum(v['exposures'] for v in variant_stats.values())

            return {
                'experiment_id': str(experiment.id),
                'experiment_name': experiment.name,
                'status': experiment.status,
                'variant_stats': variant_stats,
                'is_significant': significance.get('is_significant', False),
                'confidence_level': significance.get('confidence_level', 0),
                'p_value': significance.get('p_value'),
                'winner': winner,
                'lift_percentage': round(lift, 2) if lift else None,
                'sample_size': total_sample,
            }

        except ABExperiment.DoesNotExist:
            raise ValueError(f"Experiment {experiment_id} not found")

    def _calculate_significance(
        self,
        variant_stats: Dict,
        control_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate statistical significance using z-test for proportions.

        Returns dict with is_significant, confidence_level, p_value.
        """
        if control_rate is None:
            return {'is_significant': False, 'confidence_level': 0, 'p_value': None}

        # Find best treatment variant
        treatment_stats = [
            vs for vs in variant_stats.values()
            if not vs['is_control'] and vs['exposures'] > 0
        ]

        if not treatment_stats:
            return {'is_significant': False, 'confidence_level': 0, 'p_value': None}

        # Get the variant with highest conversion rate
        best_treatment = max(treatment_stats, key=lambda x: x['conversion_rate'])

        control_stats = next(
            (vs for vs in variant_stats.values() if vs['is_control']),
            None
        )

        if not control_stats or control_stats['exposures'] < 10 or best_treatment['exposures'] < 10:
            return {'is_significant': False, 'confidence_level': 0, 'p_value': None, 'reason': 'Insufficient sample size'}

        # Z-test for two proportions
        n1 = control_stats['exposures']
        n2 = best_treatment['exposures']
        p1 = control_stats['conversion_rate']
        p2 = best_treatment['conversion_rate']

        # Pooled proportion
        p_pooled = (p1 * n1 + p2 * n2) / (n1 + n2)

        # Standard error
        if p_pooled == 0 or p_pooled == 1:
            return {'is_significant': False, 'confidence_level': 0, 'p_value': None}

        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

        if se == 0:
            return {'is_significant': False, 'confidence_level': 0, 'p_value': None}

        # Z-score
        z = (p2 - p1) / se

        # P-value (two-tailed)
        p_value = 2 * (1 - self._normal_cdf(abs(z)))

        # Confidence level
        confidence = 1 - p_value

        return {
            'is_significant': p_value < 0.05,
            'confidence_level': round(confidence, 4),
            'p_value': round(p_value, 4),
            'z_score': round(z, 4),
        }

    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF using error function approximation."""
        # Approximation using the error function
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ==================== Pre-built Experiments ====================

def create_style_recommendation_experiment(service: ABTestingService = None) -> Dict:
    """
    Create a pre-built experiment for testing style recommendation strategies.
    """
    if service is None:
        service = ABTestingService()

    return service.create_experiment(
        name='Style Recommendation Strategy Test',
        description='Test which recommendation source provides better engagement',
        experiment_type='recommendation',
        domain='style_recommendations',
        traffic_percentage=100,
        variants=[
            {
                'name': 'control_balanced',
                'is_control': True,
                'weight': 33,
                'config': {
                    'strategy': 'balanced',
                    'sources': ['personal', 'temporal', 'trending'],
                    'description': 'Balanced mix of all sources'
                }
            },
            {
                'name': 'temporal_first',
                'is_control': False,
                'weight': 33,
                'config': {
                    'strategy': 'temporal_first',
                    'sources': ['temporal', 'personal', 'trending'],
                    'description': 'Prioritize time-based recommendations'
                }
            },
            {
                'name': 'trending_first',
                'is_control': False,
                'weight': 34,
                'config': {
                    'strategy': 'trending_first',
                    'sources': ['trending', 'personal', 'temporal'],
                    'description': 'Prioritize trending styles'
                }
            },
        ],
        config={
            'min_sample_size': 100,
            'confidence_level': 0.95,
        }
    )


# Singleton instance
_ab_testing_service = None


def get_ab_testing_service() -> ABTestingService:
    """Get singleton instance of ABTestingService."""
    global _ab_testing_service
    if _ab_testing_service is None:
        _ab_testing_service = ABTestingService()
    return _ab_testing_service
