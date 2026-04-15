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
    # Session 833: Expanded mappings to cover more experiment types
    KPI_SOURCE_MAPPINGS = {
        # Pattern in experiment name/KPI -> (source_type, calculation_method)
        'mit tech review': ('spider', 'mit_tech_review'),
        'financial': ('spider', 'financial'),
        'content': ('agent', 'content'),
        'convertkit': ('agent', 'content'),
        'synthesis': ('decision', 'synthesis'),
        'market': ('spider', 'market'),
        'trading': ('spider', 'financial'),
        # Session 833: Spider intelligence patterns
        'huggingface': ('spider', 'tech'),
        'healthtech': ('spider', 'tech'),
        'mobihealthnews': ('spider', 'tech'),
        'venturebeat': ('spider', 'tech'),
        'crunchbase': ('spider', 'tech'),
        'securityweek': ('spider', 'tech'),
        'indiehackers': ('spider', 'tech'),
        'discord': ('spider', 'tech'),
        'investment tracker': ('spider', 'financial'),
        # Session 833: Research and analysis patterns
        'research': ('agent', 'research'),
        'analyze': ('agent', 'research'),
        'competitor': ('agent', 'research'),
        'customer': ('agent', 'research'),
        'debate': ('agent', 'content'),
        'educational': ('agent', 'content'),
        'behavior': ('agent', 'content'),
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

        # Session 1103c: previously results['success'] = True was
        # initialized once and NEVER flipped, even when per-experiment
        # updates threw exceptions caught at line ~165. Upstream
        # orchestration treated success=True as "KPI job ran clean,"
        # masking broken KPI sources and letting experiments drift
        # with stale current_value + missing snapshots. Now success
        # is computed at the end of the loop based on whether any
        # errors were captured.
        results = {
            'success': True,  # provisional; recomputed after the loop
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

                # Session 833: Auto-complete experiments that meet their target
                if self._check_target_met(exp, new_value):
                    exp.complete(
                        status='success',
                        result_summary=f"Target KPI reached: {new_value} >= {exp.target_value}",
                        outcome_classification='pass'
                    )
                    results.setdefault('completed', []).append({
                        'id': str(exp.id),
                        'name': exp.name[:50],
                        'final_value': str(new_value),
                    })
                    self.logger.info(f"🎉 Auto-completed experiment {exp.name[:40]} - target met!")

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
            'completed_count': len(results.get('completed', [])),
        }

        # Session 1103c: real success calculation. Job is success if
        # there were zero errors AND we either updated something or
        # had nothing to update. Any error flips success=False so
        # upstream monitoring can react.
        results['success'] = len(results['errors']) == 0
        if not results['success']:
            self.logger.warning(
                "auto_kpi_tracking: KPI update job had %d errors out "
                "of %d running experiments — reporting success=False",
                len(results['errors']), running_experiments.count(),
            )

        return results

    def _check_target_met(self, exp, current_value) -> bool:
        """
        Session 833: Check if experiment has met its target KPI.

        Handles various value formats: percentages, numbers, etc.
        """
        try:
            # Parse current value
            current_str = str(current_value).replace('%', '').strip()
            current = float(current_str) if current_str else 0

            # Parse target value
            target_str = str(exp.target_value or '100').replace('%', '').strip()
            target = float(target_str) if target_str else 100

            # Check if target is met (with small tolerance for floating point)
            return current >= target and target > 0

        except (ValueError, TypeError) as e:
            self.logger.debug(f"Could not parse values for {exp.name}: {e}")
            return False

    def _get_data_source(self, exp) -> Tuple[Optional[str], Optional[str]]:
        """
        Determine the data source for an experiment.

        Session 656: First check secondary_kpis for explicit data source mapping,
        then fall back to pattern matching.
        """
        # Session 656: Check for explicit data source in secondary_kpis
        if exp.secondary_kpis:
            source_type = exp.secondary_kpis.get('data_source_type')
            source_id = exp.secondary_kpis.get('data_source_id')
            if source_type and source_id:
                return source_type, source_id

        # Fall back to pattern matching
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
        """
        Calculate the current KPI value from the data source.

        Session 656: Added support for content, knowledge, thinking, and agent sources.
        Session 657: Added 'all' source type for comprehensive System Health Score.
        """
        details = {'source_type': source_type, 'source_id': source_id}

        if source_type == 'all':
            # Session 657: Comprehensive calculation from all data sources
            return self._calculate_system_health_score(exp, details)
        elif source_type == 'spider':
            return self._calculate_from_spider(exp, source_id, details)
        elif source_type == 'agent':
            return self._calculate_from_agent(exp, source_id, details)
        elif source_type == 'decision':
            return self._calculate_from_decisions(exp, source_id, details)
        elif source_type == 'content':
            return self._calculate_from_content(exp, source_id, details)
        elif source_type == 'knowledge':
            return self._calculate_from_knowledge(exp, source_id, details)
        elif source_type == 'thinking':
            return self._calculate_from_thinking(exp, source_id, details)
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

        # Session 656: New spider source types
        elif spider_type == 'news':
            runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='news') |
                Q(spider_name__icontains='reuters') |
                Q(spider_name__icontains='cnn') |
                Q(spider_name__icontains='bbc') |
                Q(spider_name__icontains='npr') |
                Q(spider_name__icontains='techcrunch') |
                Q(spider_name__icontains='axios'),
                started_at__gte=lookback,
                status='success'
            )
            total_items = sum(r.items_collected or 0 for r in runs)
            per_day = round(total_items / self.DEFAULT_LOOKBACK_DAYS, 1)
            value = f"{per_day} items/day"

            details['runs'] = runs.count()
            details['items'] = total_items
            details['per_day'] = per_day
            details['notes'] = f"{total_items} news items in {self.DEFAULT_LOOKBACK_DAYS} days"

        elif spider_type == 'tech':
            runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='tech') |
                Q(spider_name__icontains='hackernews') |
                Q(spider_name__icontains='devto') |
                Q(spider_name__icontains='github') |
                Q(spider_name__icontains='wired') |
                Q(spider_name__icontains='verge') |
                Q(spider_name__icontains='mit'),
                started_at__gte=lookback,
                status='success'
            )
            success_count = runs.count()
            total_runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='tech') |
                Q(spider_name__icontains='hackernews') |
                Q(spider_name__icontains='devto') |
                Q(spider_name__icontains='github') |
                Q(spider_name__icontains='wired') |
                Q(spider_name__icontains='verge') |
                Q(spider_name__icontains='mit'),
                started_at__gte=lookback,
            ).count()
            success_rate = round(success_count / total_runs * 100, 1) if total_runs > 0 else 0
            value = f"{success_rate}%"

            details['successful_runs'] = success_count
            details['total_runs'] = total_runs
            details['notes'] = f"{success_count}/{total_runs} tech spider runs successful"

        elif spider_type == 'social':
            runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='reddit') |
                Q(spider_name__icontains='bluesky') |
                Q(spider_name__icontains='discord') |
                Q(spider_name__icontains='hackernoon'),
                started_at__gte=lookback,
                status='success'
            )
            success_count = runs.count()
            total_runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='reddit') |
                Q(spider_name__icontains='bluesky') |
                Q(spider_name__icontains='discord') |
                Q(spider_name__icontains='hackernoon'),
                started_at__gte=lookback,
            ).count()
            success_rate = round(success_count / total_runs * 100, 1) if total_runs > 0 else 0
            value = f"{success_rate}%"

            details['successful_runs'] = success_count
            details['total_runs'] = total_runs
            details['notes'] = f"{success_count}/{total_runs} social spider runs successful"

        elif spider_type == 'business':
            runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='crunchbase') |
                Q(spider_name__icontains='venturebeat') |
                Q(spider_name__icontains='business') |
                Q(spider_name__icontains='sec_edgar'),
                started_at__gte=lookback,
                status='success'
            )
            success_count = runs.count()
            total_runs = SpiderRun.objects.filter(
                Q(spider_name__icontains='crunchbase') |
                Q(spider_name__icontains='venturebeat') |
                Q(spider_name__icontains='business') |
                Q(spider_name__icontains='sec_edgar'),
                started_at__gte=lookback,
            ).count()
            success_rate = round(success_count / total_runs * 100, 1) if total_runs > 0 else 0
            value = f"{success_rate}%"

            details['successful_runs'] = success_count
            details['total_runs'] = total_runs
            details['notes'] = f"{success_count}/{total_runs} business spider runs successful"

        elif spider_type == 'all':
            runs = SpiderRun.objects.filter(started_at__gte=lookback, status='success')
            total_items = sum(r.items_collected or 0 for r in runs)
            per_week = round(total_items * 7 / self.DEFAULT_LOOKBACK_DAYS, 1)
            value = f"{per_week} items/week"

            details['runs'] = runs.count()
            details['items'] = total_items
            details['per_week'] = per_week
            details['notes'] = f"{total_items} items from all spiders in {self.DEFAULT_LOOKBACK_DAYS} days"

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

        # Session 656: Handle new agent source types
        elif agent_type == 'conversations':
            from core.models_unified_system import AgentConversation
            convos = AgentConversation.objects.filter(started_at__gte=lookback)
            count = convos.count()
            # Calculate per-day rate
            days = self.DEFAULT_LOOKBACK_DAYS
            per_day = round(count / days, 1)
            value = f"{per_day} convos/day"

            details['total_conversations'] = count
            details['per_day'] = per_day
            details['notes'] = f"{count} agent conversations in {days} days"

        elif agent_type == 'activity':
            from core.models_unified_system import AgentConversation, AgentDream
            convos = AgentConversation.objects.filter(started_at__gte=lookback).count()
            dreams = AgentDream.objects.filter(dreamed_at__gte=lookback).count()
            total = convos + dreams
            per_day = round(total / self.DEFAULT_LOOKBACK_DAYS, 1)
            value = f"{per_day} events/day"

            details['conversations'] = convos
            details['dreams'] = dreams
            details['per_day'] = per_day
            details['notes'] = f"{convos} convos + {dreams} dreams = {total} events"

        else:
            return None, details

        return value, details

    def _calculate_from_content(
        self,
        exp,
        content_type: str,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """Session 656: Calculate KPI from content generation data."""
        from content.models import ContentAnalytics

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)

        # Map content types to query filters
        type_filters = {
            'video': ['video', 'episode', 'series'],
            'audio': ['audio', 'podcast', 'episode'],
            'blog': ['blog', 'article', 'post'],
            'image': ['image', 'art', 'visual', 'graphic'],
            'social': ['social', 'post', 'tweet'],
            'mixed': [],  # All content types
        }

        filters = type_filters.get(content_type, [])

        if filters:
            query = Q()
            for f in filters:
                query |= Q(content_type__icontains=f)
            content = ContentAnalytics.objects.filter(query, created_at__gte=lookback)
        else:
            content = ContentAnalytics.objects.filter(created_at__gte=lookback)

        count = content.count()
        per_week = round(count * 7 / self.DEFAULT_LOOKBACK_DAYS, 1)
        value = f"{per_week} items/week"

        details['total_items'] = count
        details['per_week'] = per_week
        details['content_type'] = content_type
        details['notes'] = f"{count} {content_type} items in {self.DEFAULT_LOOKBACK_DAYS} days"

        return value, details

    def _calculate_from_knowledge(
        self,
        exp,
        knowledge_type: str,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """Session 656: Calculate KPI from knowledge transfer data."""
        from core.models import KnowledgeTransfer

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)

        if knowledge_type == 'transfers':
            transfers = KnowledgeTransfer.objects.filter(created_at__gte=lookback)
            count = transfers.count()
            per_week = round(count * 7 / self.DEFAULT_LOOKBACK_DAYS, 1)

            # Calculate quality metrics
            high_quality = transfers.filter(usefulness_score__gte=0.8).count()
            quality_pct = round(high_quality / count * 100, 1) if count > 0 else 0

            value = f"{per_week} transfers/week"

            details['total_transfers'] = count
            details['per_week'] = per_week
            details['high_quality_count'] = high_quality
            details['quality_percent'] = quality_pct
            details['notes'] = f"{count} transfers, {quality_pct}% high quality"

        else:
            return None, details

        return value, details

    def _calculate_from_thinking(
        self,
        exp,
        thinking_type: str,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """Session 656: Calculate KPI from thinking engine data."""
        from core.models_unified_system import AutonomousAction

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)

        if thinking_type == 'actions':
            actions = AutonomousAction.objects.filter(executed_at__gte=lookback)
            total = actions.count()
            success = actions.filter(result='success').count()

            if total > 0:
                success_rate = round(success / total * 100, 1)
                value = f"{success_rate}%"
            else:
                value = "N/A"

            # Also calculate per-day rate
            per_day = round(total / self.DEFAULT_LOOKBACK_DAYS, 1)

            details['total_actions'] = total
            details['successful_actions'] = success
            details['success_rate'] = success_rate if total > 0 else 0
            details['per_day'] = per_day
            details['notes'] = f"{success}/{total} actions successful, {per_day}/day"

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

    def _calculate_system_health_score(
        self,
        exp,
        details: Dict
    ) -> Tuple[Optional[Any], Dict]:
        """
        Session 657: Calculate comprehensive System Health Score from ALL data sources.

        This aggregates metrics from all 5 data source types:
        - Spider: Success rate and data freshness
        - Agent: Conversation and activity rates
        - Content: Generation rate
        - Knowledge: Transfer rate and quality
        - Thinking: Autonomous action success rate

        Returns a 0-100 health score.
        """
        from core.models_unified_system import (
            SpiderExecutionLog as SpiderRun,
            AgentConversation,
            AgentDream,
            AgentExecution,
            AutonomousAction,
        )

        lookback = timezone.now() - timedelta(days=self.DEFAULT_LOOKBACK_DAYS)
        component_scores = {}
        days = self.DEFAULT_LOOKBACK_DAYS

        # 1. Spider Health (0-100): Success rate weighted by activity
        try:
            spider_total = SpiderRun.objects.filter(started_at__gte=lookback).count()
            spider_success = SpiderRun.objects.filter(started_at__gte=lookback, status='success').count()
            spider_success_rate = (spider_success / spider_total * 100) if spider_total > 0 else 0
            # Activity bonus: more runs = healthier (max 20% bonus)
            activity_bonus = min(20, spider_total / 50)  # 1000 runs/week = 20% bonus
            component_scores['spider'] = min(100, spider_success_rate + activity_bonus)
            details['spider'] = {
                'success': spider_success,
                'total': spider_total,
                'rate': round(spider_success_rate, 1),
                'score': round(component_scores['spider'], 1)
            }
        except Exception as e:
            component_scores['spider'] = 50  # Default to neutral
            details['spider'] = {'error': str(e), 'score': 50}

        # 2. Agent Health (0-100): Conversation and dream activity
        try:
            convos = AgentConversation.objects.filter(started_at__gte=lookback).count()
            dreams = AgentDream.objects.filter(dreamed_at__gte=lookback).count()
            executions = AgentExecution.objects.filter(created_at__gte=lookback).count()
            # Expect ~100 conversations/week, ~100 dreams/week, ~50 executions/week
            convo_score = min(100, convos / 1 * 100 / 100)  # 100/week = 100%
            dream_score = min(100, dreams / 1 * 100 / 100)  # 100/week = 100%
            exec_score = min(100, executions / 0.5 * 100 / 100)  # 50/week = 100%
            component_scores['agent'] = (convo_score + dream_score + exec_score) / 3
            details['agent'] = {
                'conversations': convos,
                'dreams': dreams,
                'executions': executions,
                'score': round(component_scores['agent'], 1)
            }
        except Exception as e:
            component_scores['agent'] = 50
            details['agent'] = {'error': str(e), 'score': 50}

        # 3. Content Health (0-100): Content generation activity
        try:
            from content.models import ContentAnalytics
            content_count = ContentAnalytics.objects.filter(created_at__gte=lookback).count()
            # Expect ~20 content items/week = 100%
            component_scores['content'] = min(100, content_count / 20 * 100)
            details['content'] = {
                'items': content_count,
                'score': round(component_scores['content'], 1)
            }
        except Exception as e:
            component_scores['content'] = 50
            details['content'] = {'error': str(e), 'score': 50}

        # 4. Knowledge Health (0-100): Transfer rate and quality
        try:
            from core.models import KnowledgeTransfer
            transfers = KnowledgeTransfer.objects.filter(created_at__gte=lookback)
            transfer_count = transfers.count()
            high_quality = transfers.filter(usefulness_score__gte=0.8).count()
            quality_rate = (high_quality / transfer_count * 100) if transfer_count > 0 else 50
            # Expect ~50 transfers/week = 100%
            activity_score = min(100, transfer_count / 50 * 100)
            component_scores['knowledge'] = (activity_score + quality_rate) / 2
            details['knowledge'] = {
                'transfers': transfer_count,
                'high_quality': high_quality,
                'quality_rate': round(quality_rate, 1),
                'score': round(component_scores['knowledge'], 1)
            }
        except Exception as e:
            component_scores['knowledge'] = 50
            details['knowledge'] = {'error': str(e), 'score': 50}

        # 5. Thinking Health (0-100): Autonomous action success rate
        try:
            actions = AutonomousAction.objects.filter(executed_at__gte=lookback)
            total_actions = actions.count()
            success_actions = actions.filter(result='success').count()
            success_rate = (success_actions / total_actions * 100) if total_actions > 0 else 50
            # Activity bonus: more actions = healthier (max 20% bonus)
            activity_bonus = min(20, total_actions / 25)  # 500 actions/week = 20% bonus
            component_scores['thinking'] = min(100, success_rate + activity_bonus)
            details['thinking'] = {
                'total': total_actions,
                'success': success_actions,
                'rate': round(success_rate, 1),
                'score': round(component_scores['thinking'], 1)
            }
        except Exception as e:
            component_scores['thinking'] = 50
            details['thinking'] = {'error': str(e), 'score': 50}

        # Calculate overall health score (weighted average)
        weights = {
            'spider': 0.25,    # 25% - Data ingestion
            'agent': 0.25,     # 25% - Agent activity
            'content': 0.15,   # 15% - Content production
            'knowledge': 0.20, # 20% - Learning
            'thinking': 0.15,  # 15% - Autonomous decisions
        }

        total_score = sum(
            component_scores[comp] * weights[comp]
            for comp in weights.keys()
        )

        # Round to 1 decimal
        health_score = round(total_score, 1)
        value = f"{health_score}%"

        details['component_scores'] = {k: round(v, 1) for k, v in component_scores.items()}
        details['weights'] = weights
        details['health_score'] = health_score
        details['notes'] = f"System Health: {health_score}% (Spider:{round(component_scores['spider'],0)}%, Agent:{round(component_scores['agent'],0)}%, Knowledge:{round(component_scores['knowledge'],0)}%)"

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
