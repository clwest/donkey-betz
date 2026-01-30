"""
Session 874: Threshold Sandbox for Experiment Halt Calibration

Empirical analysis of experiment halt thresholds to minimize false positives (unnecessary halts)
and false negatives (missed failures).

This service:
1. Analyzes historical experiment outcomes
2. Replays experiments with different threshold settings
3. Computes FPR/FNR for each threshold combination
4. Recommends calibrated threshold settings

Usage:
    from core.services.threshold_sandbox import ThresholdSandbox

    sandbox = ThresholdSandbox()
    report = sandbox.run_calibration()
    print(report['recommendations'])
"""

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from django.db.models import Avg, Count, Q, F
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class ThresholdConfig:
    """Configuration for a single threshold test."""
    error_rate_max: float = 35.0
    min_executions: int = 20
    min_age_minutes: int = 30
    user_trust_min: float = 3.8
    bias_rate_max: float = 15.0


@dataclass
class CalibrationResult:
    """Result of a single threshold configuration test."""
    config: ThresholdConfig
    true_positives: int = 0   # Correctly halted (would have failed anyway)
    false_positives: int = 0  # Incorrectly halted (would have succeeded)
    true_negatives: int = 0   # Correctly not halted (succeeded)
    false_negatives: int = 0  # Incorrectly not halted (failed)
    avg_detection_latency_hours: float = 0.0

    @property
    def total(self) -> int:
        return self.true_positives + self.false_positives + self.true_negatives + self.false_negatives

    @property
    def fpr(self) -> float:
        """False Positive Rate: FP / (FP + TN)"""
        denom = self.false_positives + self.true_negatives
        return self.false_positives / denom if denom > 0 else 0.0

    @property
    def fnr(self) -> float:
        """False Negative Rate: FN / (FN + TP)"""
        denom = self.false_negatives + self.true_positives
        return self.false_negatives / denom if denom > 0 else 0.0

    @property
    def precision(self) -> float:
        """Precision: TP / (TP + FP)"""
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        """Recall: TP / (TP + FN)"""
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def f1_score(self) -> float:
        """F1 Score: 2 * (precision * recall) / (precision + recall)"""
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    def expected_cost(self, c_fp: float = 1.0, c_fn: float = 10.0) -> float:
        """
        Expected cost given FP and FN costs.
        Default: FN is 10x more costly than FP (missing a failure is worse than unnecessary halt)
        """
        return c_fp * self.fpr + c_fn * self.fnr


class ThresholdSandbox:
    """
    Sandbox for testing experiment halt threshold configurations.

    Replays historical experiments with different thresholds to find
    optimal settings that minimize false positives while catching failures.
    """

    # Default parameter grid for threshold sweep
    ERROR_RATE_THRESHOLDS = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0]
    MIN_EXECUTIONS_OPTIONS = [5, 10, 15, 20, 30, 50]
    MIN_AGE_OPTIONS = [10, 20, 30, 45, 60]  # minutes

    def __init__(self, days_back: int = 90):
        """
        Initialize sandbox with historical window.

        Args:
            days_back: How far back to look for historical experiments
        """
        self.days_back = days_back
        self.cutoff = timezone.now() - timedelta(days=days_back)

    def get_dataset_summary(self) -> Dict:
        """
        Get summary statistics of the experiment dataset.

        Returns:
            Dict with total counts, status distribution, halt reasons, etc.
        """
        from core.models_pilot_readiness import Experiment
        from core.models_unified_system import AgentExecution

        experiments = Experiment.objects.filter(created_at__gte=self.cutoff)

        # Status distribution
        by_status = dict(
            experiments.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        # Halt statistics
        halted = experiments.filter(is_halted=True)
        halted_count = halted.count()

        # Halt reasons
        halt_reasons = {}
        for exp in halted:
            reason = (exp.halt_reason or 'Unknown')[:50]
            halt_reasons[reason] = halt_reasons.get(reason, 0) + 1

        # Execution linkage
        total_execs = AgentExecution.objects.filter(created_at__gte=self.cutoff).count()
        linked_execs = AgentExecution.objects.filter(
            created_at__gte=self.cutoff,
            experiment__isnull=False
        ).count()

        return {
            'time_window_days': self.days_back,
            'total_experiments': experiments.count(),
            'status_distribution': by_status,
            'halted_count': halted_count,
            'halt_rate': halted_count / experiments.count() if experiments.count() > 0 else 0,
            'top_halt_reasons': dict(sorted(halt_reasons.items(), key=lambda x: -x[1])[:10]),
            'total_executions': total_execs,
            'linked_executions': linked_execs,
            'execution_link_rate': linked_execs / total_execs if total_execs > 0 else 0,
        }

    def classify_experiment_outcome(self, experiment) -> str:
        """
        Classify an experiment's true outcome (independent of whether it was halted).

        Returns:
            'success': Experiment would have succeeded
            'failure': Experiment would have failed regardless of halt
            'unknown': Cannot determine
        """
        # If experiment completed successfully without halt, it's a success
        if experiment.status == 'success' and not experiment.is_halted:
            return 'success'

        # If experiment failed without being halted, it's a true failure
        if experiment.status == 'failure' and not experiment.is_halted:
            return 'failure'

        # If halted, we need to infer what would have happened
        if experiment.is_halted:
            # Check halt reason - if it was due to error rate, check if there were real issues
            if experiment.halt_reason and 'Error rate' in experiment.halt_reason:
                # Extract the actual error rate from the reason
                try:
                    # Format: "Error rate X% exceeded threshold Y%"
                    parts = experiment.halt_reason.split('%')
                    actual_rate = float(parts[0].split()[-1])

                    # If error rate was 100%, something was seriously wrong
                    if actual_rate >= 90:
                        return 'failure'

                    # If error rate was moderate, it might have recovered
                    if actual_rate < 50:
                        return 'unknown'  # Could have gone either way

                    return 'failure'
                except (ValueError, IndexError):
                    pass

            # For other halt reasons, classify based on final status
            if experiment.status == 'failure':
                return 'failure'
            elif experiment.status == 'success':
                return 'success'  # Recovered after halt

        # Partial or inconclusive
        if experiment.status == 'partial':
            return 'unknown'
        if experiment.status == 'inconclusive':
            return 'unknown'

        return 'unknown'

    def simulate_halt_decision(
        self,
        experiment,
        config: ThresholdConfig
    ) -> Tuple[bool, Optional[str]]:
        """
        Simulate whether an experiment would be halted with given thresholds.

        This is a simplified simulation based on the experiment's recorded data.
        In a full implementation, this would replay the actual metric stream.

        Args:
            experiment: Experiment to simulate
            config: Threshold configuration to test

        Returns:
            Tuple of (would_halt: bool, reason: str or None)
        """
        # Get the conditions that were in place
        conditions = experiment.halt_conditions or {}

        # Check if the experiment was halted and why
        if not experiment.is_halted:
            # Wasn't halted - check if it SHOULD have been with new thresholds
            # We don't have the metric history, so we can only use the final status
            if experiment.status == 'failure':
                # Failed but wasn't halted - this would be a false negative
                return False, None
            return False, None

        # Experiment was halted - check if it would STILL be halted with new thresholds
        if experiment.halt_reason and 'Error rate' in experiment.halt_reason:
            try:
                parts = experiment.halt_reason.split('%')
                actual_rate = float(parts[0].split()[-1])

                # Would new threshold have halted?
                if actual_rate > config.error_rate_max:
                    return True, f"Error rate {actual_rate}% > {config.error_rate_max}%"
                else:
                    return False, None  # New threshold is more lenient
            except (ValueError, IndexError):
                pass

        # For non-error-rate halts, assume same behavior
        return experiment.is_halted, experiment.halt_reason

    def evaluate_threshold_config(self, config: ThresholdConfig) -> CalibrationResult:
        """
        Evaluate a single threshold configuration against historical data.

        Args:
            config: Threshold configuration to test

        Returns:
            CalibrationResult with FPR/FNR metrics
        """
        from core.models_pilot_readiness import Experiment

        experiments = Experiment.objects.filter(created_at__gte=self.cutoff)
        result = CalibrationResult(config=config)

        detection_latencies = []

        for experiment in experiments:
            true_outcome = self.classify_experiment_outcome(experiment)
            would_halt, reason = self.simulate_halt_decision(experiment, config)

            if true_outcome == 'unknown':
                continue  # Skip experiments we can't classify

            # Classify the prediction
            if would_halt and true_outcome == 'failure':
                result.true_positives += 1
                # Calculate detection latency
                if experiment.halted_at and experiment.created_at:
                    latency = (experiment.halted_at - experiment.created_at).total_seconds() / 3600
                    detection_latencies.append(latency)
            elif would_halt and true_outcome == 'success':
                result.false_positives += 1
            elif not would_halt and true_outcome == 'success':
                result.true_negatives += 1
            elif not would_halt and true_outcome == 'failure':
                result.false_negatives += 1

        if detection_latencies:
            result.avg_detection_latency_hours = sum(detection_latencies) / len(detection_latencies)

        return result

    def run_threshold_sweep(
        self,
        error_rate_thresholds: List[float] = None,
        min_executions_options: List[int] = None,
        verbose: bool = False
    ) -> List[CalibrationResult]:
        """
        Run a sweep of threshold configurations and evaluate each.

        Args:
            error_rate_thresholds: List of error rate thresholds to test
            min_executions_options: List of min execution counts to test
            verbose: Whether to log progress

        Returns:
            List of CalibrationResult objects
        """
        error_rates = error_rate_thresholds or self.ERROR_RATE_THRESHOLDS
        min_execs = min_executions_options or [20]  # Keep min_executions fixed for now

        results = []
        total = len(error_rates) * len(min_execs)

        for i, error_rate in enumerate(error_rates):
            for min_exec in min_execs:
                config = ThresholdConfig(
                    error_rate_max=error_rate,
                    min_executions=min_exec
                )

                result = self.evaluate_threshold_config(config)
                results.append(result)

                if verbose:
                    logger.info(
                        f"[{i+1}/{total}] error_rate={error_rate}%, min_exec={min_exec}: "
                        f"FPR={result.fpr:.2%}, FNR={result.fnr:.2%}, F1={result.f1_score:.3f}"
                    )

        return results

    def find_optimal_threshold(
        self,
        results: List[CalibrationResult],
        c_fp: float = 1.0,
        c_fn: float = 10.0,
        max_fpr: float = 0.05,
        max_fnr: float = 0.10
    ) -> Optional[CalibrationResult]:
        """
        Find the optimal threshold configuration based on cost weighting.

        Args:
            results: List of CalibrationResult from threshold sweep
            c_fp: Cost of false positive (unnecessary halt)
            c_fn: Cost of false negative (missed failure)
            max_fpr: Maximum acceptable FPR
            max_fnr: Maximum acceptable FNR

        Returns:
            Best CalibrationResult or None if no config meets constraints
        """
        # Filter to configs that meet constraints
        valid = [r for r in results if r.fpr <= max_fpr and r.fnr <= max_fnr]

        if not valid:
            # Relax constraints and find best overall
            valid = results

        # Find minimum expected cost
        best = min(valid, key=lambda r: r.expected_cost(c_fp, c_fn))
        return best

    def run_calibration(
        self,
        c_fp: float = 1.0,
        c_fn: float = 10.0,
        verbose: bool = True
    ) -> Dict:
        """
        Run full calibration analysis and return recommendations.

        Args:
            c_fp: Cost of false positive (default 1.0)
            c_fn: Cost of false negative (default 10.0, failures are 10x more costly)
            verbose: Whether to log progress

        Returns:
            Dict with dataset summary, all results, and recommendations
        """
        logger.info("[ThresholdSandbox] Starting calibration analysis...")

        # Get dataset summary
        summary = self.get_dataset_summary()
        logger.info(
            f"[ThresholdSandbox] Dataset: {summary['total_experiments']} experiments, "
            f"{summary['halted_count']} halted ({summary['halt_rate']:.1%})"
        )

        # Run threshold sweep
        results = self.run_threshold_sweep(verbose=verbose)

        # Find optimal configurations
        conservative = self.find_optimal_threshold(results, c_fp=1, c_fn=20, max_fpr=0.01, max_fnr=0.10)
        balanced = self.find_optimal_threshold(results, c_fp=1, c_fn=10, max_fpr=0.05, max_fnr=0.10)
        permissive = self.find_optimal_threshold(results, c_fp=1, c_fn=5, max_fpr=0.10, max_fnr=0.15)

        # Build recommendations
        recommendations = {
            'conservative': {
                'description': 'Minimizes missed failures, accepts more unnecessary halts',
                'config': conservative.config.__dict__ if conservative else None,
                'fpr': conservative.fpr if conservative else None,
                'fnr': conservative.fnr if conservative else None,
                'f1': conservative.f1_score if conservative else None,
            },
            'balanced': {
                'description': 'Balances FPR/FNR with 10:1 cost ratio',
                'config': balanced.config.__dict__ if balanced else None,
                'fpr': balanced.fpr if balanced else None,
                'fnr': balanced.fnr if balanced else None,
                'f1': balanced.f1_score if balanced else None,
            },
            'permissive': {
                'description': 'Minimizes unnecessary halts, accepts more missed failures',
                'config': permissive.config.__dict__ if permissive else None,
                'fpr': permissive.fpr if permissive else None,
                'fnr': permissive.fnr if permissive else None,
                'f1': permissive.f1_score if permissive else None,
            },
        }

        # Current config for comparison
        current_config = ThresholdConfig(error_rate_max=35.0, min_executions=20, min_age_minutes=30)
        current_result = self.evaluate_threshold_config(current_config)

        return {
            'dataset_summary': summary,
            'all_results': [
                {
                    'error_rate_max': r.config.error_rate_max,
                    'min_executions': r.config.min_executions,
                    'tp': r.true_positives,
                    'fp': r.false_positives,
                    'tn': r.true_negatives,
                    'fn': r.false_negatives,
                    'fpr': r.fpr,
                    'fnr': r.fnr,
                    'precision': r.precision,
                    'recall': r.recall,
                    'f1': r.f1_score,
                    'expected_cost': r.expected_cost(c_fp, c_fn),
                }
                for r in results
            ],
            'current_config': {
                'config': current_config.__dict__,
                'fpr': current_result.fpr,
                'fnr': current_result.fnr,
                'f1': current_result.f1_score,
            },
            'recommendations': recommendations,
            'analysis_metadata': {
                'days_analyzed': self.days_back,
                'cost_fp': c_fp,
                'cost_fn': c_fn,
                'timestamp': timezone.now().isoformat(),
            }
        }


def run_threshold_calibration(days_back: int = 90, verbose: bool = True) -> Dict:
    """
    Convenience function to run threshold calibration.

    Args:
        days_back: How many days of historical data to analyze
        verbose: Whether to log progress

    Returns:
        Calibration report dict
    """
    sandbox = ThresholdSandbox(days_back=days_back)
    return sandbox.run_calibration(verbose=verbose)
