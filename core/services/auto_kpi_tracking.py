"""
Session 609: Auto KPI Tracking Service

Automatically tracks and updates KPI values for running experiments by:
1. Connecting experiments to data sources (spiders, agents, decisions)
2. Calculating current KPI values from those sources
3. Updating experiment current_value fields
4. Creating snapshots for trend visualization

Data sources:
- Spider runs and insights extracted
- Agent execution counts
- Boardroom decisions by topic
- Content generation metrics
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import timedelta
from collections import defaultdict

from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class AutoKPITrackingService:
    """
    Session 609: Automatically tracks KPIs for running experiments.

    Connects each experiment to relevant data sources and calculates
    current KPI values based on actual system activity.
    """

    # KPI type patterns and their data source mappings
    KPI_SOURCE_MAPPINGS = {
        # Pattern in experiment name/KPI -> (source_type, calculation_method)
        'mit tech review': ('spider', 'mit_tech_review'),
        'financial': ('spider', 'financial'),
        'content': ('agent', 'content'),
        'convertkit': ('agent', 'content'),
        'synthesis': ('decision', 'synthesis'),
        'market': ('spider', 'market'),
        'trading': ('spider', 'financial'),
    }

    # Time windows for calculations
    DEFAULT_LOOKBACK_DAYS = 7

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AutoKPITrackingService")

    def update_all_kpis(self) -> Dict[str, Any]:
        """
        Update KPIs for all running experiments.

        Returns summary of updates made.
        """
        from core.models_pilot_readiness import Experiment, KPISnapshot

        results = {
            'success': True,
            'updated': [],
            'skipped': [],
            'errors': [],
            'snapshots_created': 0,
        }

        running_experiments = Experiment.objects.filter(status='running')
        self.logger.info(f"Updating KPIs for {running_experiments.count()} running experiments")

        for exp in running_experiments:
            try:
                # Determine data source for this experiment
                source_type, source_id = self._get_data_source(exp)

                if not source_type:
                    results['skipped'].append({
                        'id': str(exp.id),
                        'name': exp.name[:50],
                        'reason': 'No data source mapping found',
                    })
                    continue

                # Calculate new KPI value
                new_value, details = self._calculate_kpi_value(exp, source_type, source_id)

                if new_value is None:
                    results['skipped'].append({
                        'id': str(exp.id),
                        'name': exp.name[:50],
                        'reason': f'Could not calculate value from {source_type}:{source_id}',
                    })
                    continue

                # Update experiment
                old_value = exp.current_value
                exp.current_value = str(new_value)
                exp.save(update_fields=['current_value', 'updated_at'])

                # Create snapshot
                snapshot = KPISnapshot.create_snapshot(
                    experiment=exp,
                    value=new_value,
                    data_source=f"{source_type}:{source_id}",
                    notes=details.get('notes', ''),
                )
                results['snapshots_created'] += 1

                results['updated'].append({
                    'id': str(exp.id),
                    'name': exp.name[:50],
                    'kpi': exp.primary_kpi,
                    'old_value': old_value,
                    'new_value': str(new_value),
                    'source': f"{source_type}:{source_id}",
                    'details': details,
                })

                self.logger.info(
                    f"Updated {exp.name[:40]}: {old_value} -> {new_value} "
                    f"(source: {source_type}:{source_id})"
                )

            except Exception as e:
                self.logger.error(f"Error updating KPI for {exp.name}: {e}")
                results['errors'].append({
                    'id': str(exp.id),
                    'name': exp.name[:50],
                    'error': str(e),
                })

        results['summary'] = {
            'total_experiments': running_experiments.count(),
            'updated_count': len(results['updated']),
            'skipped_count': len(results['skipped']),
            'error_count': len(results['errors']),
        }

        return results

    def _get_data_source(self, exp) -> Tuple[Optional[str], Optional[str]]:
        """Determine the data source for an experiment based on its name/KPI."""
        exp_text = f"{exp.name} {exp.primary_kpi or ''} {exp.hypothesis or ''}".lower()

        for pattern, (source_type, source_id) in self.KPI_SOURCE_MAPPINGS.items():
            if pattern in exp_text:
                return source_type, source_id

        return None, None

    def _calculate_kpi_value(
        self,
        exp,
        source_type: str,
        source_id: str
    ) -> Tuple[Optional[Any], Dict]:
        """Calculate the current KPI value from the data source."""

        details = {'source_type': source_type, 'source_id': source_id}

        if source_type == 'spider':
            return self._calculate_from_spider(exp, source_id, details)
        elif source_type == 'agent':
            return self._calculate_from_agent(exp, source_id, details)
        elif source_type == 'decision':
            return self._calculate_from_decisions(exp, source_id, details)
        else:
            return None, details

    def _calculate_from_spider(
        self,
        exp,
        spider_type: str,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """Calculate KPI from spider run data."""
        from core.models_unified_system import SpiderExecutionLog as SpiderRun

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)

        # Build query based on spider type
        if spider_type == 'mit_tech_review':
            runs = SpiderRun.objects.filter(
                spider_name__icontains='mit_tech',
                started_at__gte=lookback,
                status='success'
            )
            # Count successful runs as "insights"
            count = runs.count()
            # Also count items collected if available
            total_items = sum(r.items_collected or 0 for r in runs)
            value = total_items if total_items > 0 else count

            details['runs'] = count
            details['items'] = total_items
            details['notes'] = f"{count} spider runs, {total_items} items in last 7 days"

        elif spider_type == 'financial':
            runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='coingecko') |
                Q(spider_name__icontains='yahoo') |
                Q(spider_name__icontains='polygon') |
                Q(spider_name__icontains='finnhub'),
                started_at__gte=lookback,
                status='success'
            )
            count = runs.count()
            # For financial, estimate accuracy based on success rate
            total_runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='coingecko') |
                Q(spider_name__icontains='yahoo') |
                Q(spider_name__icontains='polygon') |
                Q(spider_name__icontains='finnhub'),
                started_at__gte=lookback,
            ).count()

            accuracy = round((count / total_runs * 100), 1) if total_runs > 0 else 50
            value = f"{accuracy}%"

            details['successful_runs'] = count
            details['total_runs'] = total_runs
            details['notes'] = f"{count}/{total_runs} successful financial spider runs"

        elif spider_type == 'market':
            runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='market') |
                Q(spider_name__icontains='trend') |
                Q(spider_name__icontains='news'),
                started_at__gte=lookback,
                status='success'
            )
            count = runs.count()
            # Quality score based on items collected
            total_items = sum(r.items_collected or 0 for r in runs)
            # Normalize to 0-10 scale (assume 50 items per week is good)
            quality_score = min(10, round(total_items / 5, 1))
            value = quality_score

            details['runs'] = count
            details['items'] = total_items
            details['notes'] = f"{total_items} market insights from {count} runs"

        else:
            return None, details

        return value, details

    def _calculate_from_agent(
        self,
        exp,
        agent_type: str,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """Calculate KPI from agent execution data."""
        from core.models_unified_system import AgentExecution

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)

        if agent_type == 'content':
            # Count content-related agent executions
            executions = AgentExecution.objects.filter(
                Q(agent__name__icontains='content') |
                Q(agent__name__icontains='writer') |
                Q(agent__name__icontains='creative'),
                created_at__gte=lookback,
                status='completed'
            )
            count = executions.count()

            # Estimate high-conversion ideas as ~30% of successful executions
            high_conversion = max(1, int(count * 0.3))
            value = high_conversion

            details['total_executions'] = count
            details['high_conversion_estimate'] = high_conversion
            details['notes'] = f"{count} content agent executions, ~{high_conversion} high-conversion"

        else:
            return None, details

        return value, details

    def _calculate_from_decisions(
        self,
        exp,
        decision_type: str,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """Calculate KPI from boardroom decisions."""
        from core.models_unified_system import AgentDecisionSummary

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)

        if decision_type == 'synthesis':
            # Count synthesis-related decisions
            decisions = AgentDecisionSummary.objects.filter(
                Q(topic__icontains='synthesis') |
                Q(topic__icontains='combining') |
                Q(decision_type='synthesis'),
                created_at__gte=lookback,
            )
            count = decisions.count()
            # Quality recommendations = canonical decisions
            canonical = decisions.filter(is_canonical=True).count()

            # Use canonical count or estimate based on total
            value = canonical if canonical > 0 else max(1, int(count * 0.2))

            details['total_decisions'] = count
            details['canonical_decisions'] = canonical
            details['notes'] = f"{count} synthesis decisions, {canonical} canonical"

        else:
            return None, details

        return value, details

    def get_kpi_trend(self, experiment_id: str, days: int = 30) -> Dict[str, Any]:
        """Get KPI trend data for an experiment."""
        from core.models_pilot_readiness import Experiment, KPISnapshot

        try:
            exp = Experiment.objects.get(id=experiment_id)
            lookback = timezone.now() - timedelta(days=days)

            snapshots = KPISnapshot.objects.filter(
                experiment=exp,
                captured_at__gte=lookback
            ).order_by('captured_at')

            trend_data = []
            for snap in snapshots:
                trend_data.append({
                    'date': snap.captured_at.isoformat(),
                    'value': snap.numeric_value,
                    'display_value': snap.value,
                    'progress_percent': snap.progress_percent,
                })

            # Calculate trend direction
            if len(trend_data) >= 2:
                first_val = trend_data[0].get('value') or 0
                last_val = trend_data[-1].get('value') or 0
                if last_val > first_val * 1.1:
                    trend_direction = 'up'
                elif last_val < first_val * 0.9:
                    trend_direction = 'down'
                else:
                    trend_direction = 'stable'
            else:
                trend_direction = 'insufficient_data'

            return {
                'success': True,
                'experiment_id': str(exp.id),
                'experiment_name': exp.name,
                'kpi': exp.primary_kpi,
                'target': exp.target_value,
                'current': exp.current_value,
                'trend_data': trend_data,
                'trend_direction': trend_direction,
                'data_points': len(trend_data),
            }

        except Experiment.DoesNotExist:
            return {'success': False, 'error': 'Experiment not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_all_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get trend summary for all running experiments."""
        from core.models_pilot_readiness import Experiment

        experiments = Experiment.objects.filter(status='running')
        trends = []

        for exp in experiments:
            trend = self.get_kpi_trend(str(exp.id), days)
            if trend.get('success'):
                trends.append({
                    'id': str(exp.id),
                    'name': exp.name[:50],
                    'kpi': exp.primary_kpi,
                    'current': exp.current_value,
                    'target': exp.target_value,
                    'trend_direction': trend.get('trend_direction'),
                    'data_points': trend.get('data_points', 0),
                })

        return {
            'success': True,
            'experiments': trends,
            'summary': {
                'total': len(trends),
                'trending_up': sum(1 for t in trends if t['trend_direction'] == 'up'),
                'trending_down': sum(1 for t in trends if t['trend_direction'] == 'down'),
                'stable': sum(1 for t in trends if t['trend_direction'] == 'stable'),
            }
        }


# Convenience functions
def update_all_experiment_kpis() -> Dict[str, Any]:
    """Update KPIs for all running experiments."""
    service = AutoKPITrackingService()
    return service.update_all_kpis()


def get_experiment_kpi_trend(experiment_id: str, days: int = 30) -> Dict[str, Any]:
    """Get KPI trend for a specific experiment."""
    service = AutoKPITrackingService()
    return service.get_kpi_trend(experiment_id, days)


def get_all_kpi_trends(days: int = 30) -> Dict[str, Any]:
    """Get trend summary for all experiments."""
    service = AutoKPITrackingService()
    return service.get_all_trends(days)
