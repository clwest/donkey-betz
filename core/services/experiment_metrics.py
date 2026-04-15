"""
Session 600: Experiment Metrics Service

Gathers real metrics for experiment halt condition monitoring.
Connects to existing data sources to provide actual measurements instead of placeholders.

Metric Sources:
- error_rate: From AgentExecution and task failure tracking
- user_trust_index: From PipelineStageFeedback ratings (1-5 scale)
- bias_detection_rate: From output content analysis
- integrity_anomaly: Detects unusual patterns in quality metrics
- telemetry_kill_switch: From PilotExecution.kill_switch_triggered
"""

import logging
from datetime import timedelta
from typing import Optional

from django.db.models import Avg, Count, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExperimentMetricsService:
    """
    Gathers real-time metrics for experiment monitoring and halt condition checks.

    All metrics are gathered from actual database records to provide
    real halt condition triggers instead of hardcoded safe values.
    """

    # Time windows for metric calculations
    ERROR_RATE_WINDOW_HOURS = 1
    TRUST_INDEX_WINDOW_HOURS = 24
    BIAS_DETECTION_WINDOW_HOURS = 2
    ANOMALY_DETECTION_WINDOW_HOURS = 6

    # Session 841/855: Minimum thresholds to prevent premature halt decisions
    # Session 1023: Lowered from 20 to 5 — experiment FK rarely populated, so 20 is
    # almost never reached and the method always returns 0.0
    MIN_EXECUTIONS_FOR_ERROR_RATE = 5  # Need at least 5 executions before calculating error rate
    MIN_AGE_MINUTES = 30  # Session 855: Increased from 10 to 30 minutes grace period

    def __init__(self, experiment):
        """
        Initialize with an experiment to gather metrics for.

        Args:
            experiment: The Experiment model instance to monitor
        """
        self.experiment = experiment
        self.pilot = experiment.pilot
        self.decision = experiment.pilot.gate.decision

    def gather_all_metrics(self) -> dict:
        """
        Gather all metrics needed for halt condition checks.

        Session 841: Now checks provider health before returning metrics.
        If any provider is degraded, suppress error_rate and integrity_anomaly
        to prevent cascading halts during provider outages.

        Returns:
            dict with keys:
                - error_rate: % of failed operations in window
                - user_trust_index: Average user rating (1-5 scale)
                - bias_detection_rate: % of outputs flagged for bias
                - integrity_anomaly: Boolean if anomaly detected
                - telemetry_kill_switch: Boolean if external kill signal
        """
        try:
            # Session 841: Check provider health first
            provider_degraded = False
            try:
                from core.services.provider_health_tracker import is_any_provider_degraded
                provider_degraded = is_any_provider_degraded()
            except ImportError:
                pass  # Health tracker not available

            metrics = {
                'error_rate': self._calculate_error_rate(),
                'user_trust_index': self._calculate_user_trust_index(),
                'bias_detection_rate': self._calculate_bias_detection_rate(),
                'integrity_anomaly': self._detect_integrity_anomaly(),
                'telemetry_kill_switch': self._check_kill_switch(),
            }

            # Session 841: Suppress halt-triggering metrics during provider outages
            if provider_degraded:
                logger.warning(
                    f"[Session 841] Provider degraded - suppressing error metrics for experiment {self.experiment.id}. "
                    f"Original error_rate: {metrics['error_rate']}%, integrity_anomaly: {metrics['integrity_anomaly']}"
                )
                metrics['error_rate'] = 0.0
                metrics['integrity_anomaly'] = False
                metrics['_provider_degraded'] = True  # Flag for debugging

            logger.debug(
                f"[Session 600] Gathered metrics for experiment {self.experiment.id}: {metrics}"
            )

            return metrics

        except Exception as e:
            logger.error(f"[Session 600] Error gathering metrics: {e}")
            # Return safe defaults on error (won't trigger halt)
            return {
                'error_rate': 0.0,
                'user_trust_index': 5.0,
                'bias_detection_rate': 0.0,
                'integrity_anomaly': False,
                'telemetry_kill_switch': False,
            }

    def _calculate_error_rate(self) -> float:
        """
        Calculate error rate from agent executions and Celery task results.

        Session 841: Now scoped to THIS experiment only, not system-wide.
        Also enforces minimum sample size and age before making halt decisions.

        Looks at:
        1. Agent executions with status='failed' FOR THIS EXPERIMENT
        2. Celery task results with status='FAILURE'

        Returns:
            Error rate as percentage (0-100)
        """
        from core.models_unified_system import AgentExecution

        window_start = timezone.now() - timedelta(hours=self.ERROR_RATE_WINDOW_HOURS)
        experiment_start = self.experiment.started_at

        # Session 841: Check minimum experiment age before calculating error rate
        experiment_age_minutes = (timezone.now() - experiment_start).total_seconds() / 60
        if experiment_age_minutes < self.MIN_AGE_MINUTES:
            logger.debug(
                f"[Session 841] Experiment {self.experiment.id} is only {experiment_age_minutes:.1f} min old, "
                f"skipping error rate calculation (min: {self.MIN_AGE_MINUTES} min)"
            )
            return 0.0

        # Use the later of window_start or experiment_start
        effective_start = max(window_start, experiment_start)

        try:
            # Session 841: Filter by THIS experiment only, not all executions
            executions = AgentExecution.objects.filter(
                created_at__gte=effective_start,
                experiment=self.experiment  # Scope to this experiment
            )

            total = executions.count()

            # Session 1023: Fallback — experiment FK is rarely populated on AgentExecution,
            # so try a time-window query scoped to the experiment's lifetime instead
            if total < self.MIN_EXECUTIONS_FOR_ERROR_RATE:
                logger.debug(
                    f"[Session 1023] Experiment FK query returned only {total} rows, "
                    f"falling back to time-window query for experiment {self.experiment.id}"
                )
                executions = AgentExecution.objects.filter(
                    created_at__gte=effective_start,
                )
                total = executions.count()

            # Session 841: Require minimum sample size before calculating error rate
            if total < self.MIN_EXECUTIONS_FOR_ERROR_RATE:
                logger.debug(
                    f"[Session 841] Experiment {self.experiment.id} has only {total} executions, "
                    f"skipping error rate calculation (min: {self.MIN_EXECUTIONS_FOR_ERROR_RATE})"
                )
                return 0.0

            failed = executions.filter(status='failed').count()
            error_rate = (failed / total) * 100

            logger.debug(
                f"[Session 841] Experiment {self.experiment.id} error rate: "
                f"{failed}/{total} = {error_rate:.1f}%"
            )

            return round(error_rate, 2)

        except Exception as e:
            logger.warning(f"[Session 600] Error calculating error rate: {e}")
            return 0.0

    def _calculate_user_trust_index(self) -> float:
        """
        Calculate user trust index from feedback ratings.

        Uses PipelineStageFeedback ratings (1-5 scale) as a proxy for trust.
        Falls back to 5.0 (max) if no ratings available.

        Returns:
            Average rating (1-5 scale)
        """
        from core.models_pipeline_feedback import PipelineStageFeedback

        window_start = timezone.now() - timedelta(hours=self.TRUST_INDEX_WINDOW_HOURS)
        experiment_start = self.experiment.started_at
        effective_start = max(window_start, experiment_start)

        try:
            # Get average rating from feedback in window
            result = PipelineStageFeedback.objects.filter(
                created_at__gte=effective_start
            ).aggregate(
                avg_rating=Avg('rating')
            )

            avg_rating = result.get('avg_rating')
            if avg_rating is None:
                return 5.0  # No ratings = assume good (won't trigger halt)

            return round(float(avg_rating), 2)

        except Exception as e:
            logger.warning(f"[Session 600] Error calculating trust index: {e}")
            return 5.0

    def _calculate_bias_detection_rate(self) -> float:
        """
        Calculate bias detection rate from agent output analysis.

        Checks for:
        1. Outputs with quality issues flagged
        2. Feedback with low ratings + comments mentioning bias-related terms
        3. Content that was rejected or needed revision

        Returns:
            Bias detection rate as percentage (0-100)
        """
        from core.models_pipeline_feedback import PipelineStageFeedback, ContentOutcome

        window_start = timezone.now() - timedelta(hours=self.BIAS_DETECTION_WINDOW_HOURS)
        experiment_start = self.experiment.started_at
        effective_start = max(window_start, experiment_start)

        try:
            # Get feedback in window
            feedback_qs = PipelineStageFeedback.objects.filter(
                created_at__gte=effective_start
            )

            total_feedback = feedback_qs.count()
            if total_feedback == 0:
                return 0.0

            # Count "bias indicators":
            # 1. Low ratings (1-2) with comments
            # 2. Feedback with bias-related keywords in comments
            bias_keywords = ['bias', 'unfair', 'discriminat', 'offensive', 'inappropriate']

            bias_indicators = 0

            # Low rating with comment suggests quality issue
            low_rated = feedback_qs.filter(rating__lte=2).exclude(comment='').count()
            bias_indicators += low_rated

            # Check for bias keywords in comments
            for keyword in bias_keywords:
                keyword_matches = feedback_qs.filter(
                    comment__icontains=keyword
                ).count()
                bias_indicators += keyword_matches

            # Also check for rejected content.
            # Session 1103c: was 'except Exception: pass' with the
            # comment "ContentEngagement may not exist". The pass
            # silently undercounted bias_indicators if the model
            # import broke for any reason OTHER than the table being
            # absent (schema drift, app loading order, transient
            # import error). Now narrowly catches ImportError +
            # OperationalError and logs other exceptions.
            try:
                from core.models_pipeline_feedback import ContentEngagement
                rejected = ContentEngagement.objects.filter(
                    created_at__gte=effective_start,
                    outcome='rejected'
                ).count()
                bias_indicators += rejected
            except ImportError:
                pass  # ContentEngagement model genuinely not installed
            except Exception as e:
                logger.warning(
                    "experiment_metrics: ContentEngagement query failed "
                    "(%s: %s) — bias_rate may be undercounted",
                    type(e).__name__, e,
                )

            # Calculate rate (cap at 100%)
            bias_rate = min((bias_indicators / max(total_feedback, 1)) * 100, 100.0)

            return round(bias_rate, 2)

        except Exception as e:
            logger.warning(f"[Session 600] Error calculating bias rate: {e}")
            return 0.0

    def _detect_integrity_anomaly(self) -> bool:
        """
        Detect integrity anomalies in system metrics.

        Flags an anomaly if:
        1. Sudden spike in error rate (3x normal)
        2. Sharp drop in quality ratings
        3. Unusual execution patterns

        Returns:
            True if anomaly detected, False otherwise
        """
        from core.models_unified_system import AgentExecution
        from core.models_pipeline_feedback import PipelineStageFeedback

        window_start = timezone.now() - timedelta(hours=self.ANOMALY_DETECTION_WINDOW_HOURS)

        try:
            # Compare current hour to previous hours
            current_hour_start = timezone.now() - timedelta(hours=1)
            previous_hours_start = current_hour_start - timedelta(hours=self.ANOMALY_DETECTION_WINDOW_HOURS - 1)

            # Check for error spike
            current_errors = AgentExecution.objects.filter(
                created_at__gte=current_hour_start,
                status='failed'
            ).count()

            previous_errors = AgentExecution.objects.filter(
                created_at__gte=previous_hours_start,
                created_at__lt=current_hour_start,
                status='failed'
            ).count()

            # Normalize by time (previous is N-1 hours)
            previous_hourly_avg = previous_errors / max(self.ANOMALY_DETECTION_WINDOW_HOURS - 1, 1)

            # Session 805: Use a minimum baseline to avoid false positives
            # When previous average is 0 (overnight/low activity), use baseline of 3 errors/hour
            # This prevents normal daytime activity from triggering anomalies
            MINIMUM_BASELINE = 3.0
            comparison_baseline = max(previous_hourly_avg, MINIMUM_BASELINE)

            # 3x spike in errors = anomaly (but compared against reasonable baseline)
            # Also require at least 10 errors (not just 6) to trigger
            if current_errors > 10 and current_errors > (comparison_baseline * 3):
                logger.warning(
                    f"[Session 600] Integrity anomaly: Error spike detected "
                    f"(current: {current_errors}, baseline: {comparison_baseline:.1f})"
                )
                return True

            # Check for rating drop
            current_ratings = PipelineStageFeedback.objects.filter(
                created_at__gte=current_hour_start
            ).aggregate(avg=Avg('rating'))['avg']

            previous_ratings = PipelineStageFeedback.objects.filter(
                created_at__gte=previous_hours_start,
                created_at__lt=current_hour_start
            ).aggregate(avg=Avg('rating'))['avg']

            # 1.5+ point drop in ratings = anomaly
            if current_ratings and previous_ratings:
                if previous_ratings - current_ratings >= 1.5:
                    logger.warning(
                        f"[Session 600] Integrity anomaly: Rating drop detected "
                        f"(current: {current_ratings:.1f}, previous: {previous_ratings:.1f})"
                    )
                    return True

            return False

        except Exception as e:
            logger.warning(f"[Session 600] Error detecting anomaly: {e}")
            return False

    def _check_kill_switch(self) -> bool:
        """
        Check if the telemetry kill switch has been triggered.

        Checks:
        1. PilotExecution.kill_switch_triggered
        2. Any external kill signal stored in experiment/pilot metadata

        Returns:
            True if kill switch triggered, False otherwise
        """
        try:
            # Check pilot's kill switch
            if self.pilot.kill_switch_triggered:
                logger.info(
                    f"[Session 600] Kill switch triggered for pilot {self.pilot.id}: "
                    f"{self.pilot.kill_switch_reason}"
                )
                return True

            # Check experiment metadata for external kill signal
            if self.experiment.halt_conditions.get('external_kill_signal', False):
                return True

            return False

        except Exception as e:
            logger.warning(f"[Session 600] Error checking kill switch: {e}")
            return False

    def get_metrics_summary(self) -> dict:
        """
        Get a human-readable summary of current metrics vs thresholds.

        Returns:
            dict with metric name, current value, threshold, and status
        """
        metrics = self.gather_all_metrics()
        conditions = self.experiment.halt_conditions or {}

        return {
            'error_rate': {
                'current': metrics['error_rate'],
                'threshold': conditions.get('error_rate_max', 25.0),
                'unit': '%',
                'status': 'OK' if metrics['error_rate'] <= conditions.get('error_rate_max', 25.0) else 'ALERT'
            },
            'user_trust_index': {
                'current': metrics['user_trust_index'],
                'threshold': conditions.get('user_trust_index_min', 3.8),
                'unit': '/5',
                'status': 'OK' if metrics['user_trust_index'] >= conditions.get('user_trust_index_min', 3.8) else 'ALERT'
            },
            'bias_detection_rate': {
                'current': metrics['bias_detection_rate'],
                'threshold': conditions.get('bias_detection_rate_max', 15.0),
                'unit': '%',
                'status': 'OK' if metrics['bias_detection_rate'] <= conditions.get('bias_detection_rate_max', 15.0) else 'ALERT'
            },
            'integrity_anomaly': {
                'current': metrics['integrity_anomaly'],
                'threshold': 'No anomalies',
                'unit': '',
                'status': 'OK' if not metrics['integrity_anomaly'] else 'ALERT'
            },
            'telemetry_kill_switch': {
                'current': metrics['telemetry_kill_switch'],
                'threshold': 'Not triggered',
                'unit': '',
                'status': 'OK' if not metrics['telemetry_kill_switch'] else 'ALERT'
            }
        }


def gather_experiment_metrics(experiment) -> dict:
    """
    Convenience function to gather metrics for an experiment.

    This replaces the placeholder _gather_experiment_metrics in tasks.py.

    Args:
        experiment: Experiment model instance

    Returns:
        dict of metrics for halt condition checking
    """
    service = ExperimentMetricsService(experiment)
    return service.gather_all_metrics()
