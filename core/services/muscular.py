"""
Session 707: MUSCULAR SYSTEM - Agent Work Execution Service

The MUSCULAR SYSTEM monitors agent work execution and performance,
tracking strength, fatigue, and strain across agent muscle groups.

Key Features:
- Agent execution tracking per muscle group
- Success rate and performance metrics
- Fatigue and strain detection
- Weak/overworked agent identification
- Integration with HEART and DIGESTIVE systems

Usage:
    from core.services.muscular import get_muscular_system

    muscular = get_muscular_system()

    # Run full muscular check
    result = muscular.flex()

    # Quick health check
    is_ok = muscular.is_strong()

    # Get cached vitals
    vitals = muscular.get_vitals()

    # Find weak muscles
    weak = muscular.detect_weak_muscles()
"""

import logging
import uuid
from datetime import timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from django.db import transaction
from django.db.models import Count, Sum, Avg, Q, F, Max, Min
from django.utils import timezone

logger = logging.getLogger(__name__)


# Singleton instance
_muscular_instance: Optional['MuscularSystemService'] = None


def get_muscular_system() -> 'MuscularSystemService':
    """Get the singleton MuscularSystemService instance."""
    global _muscular_instance
    if _muscular_instance is None:
        _muscular_instance = MuscularSystemService()
    return _muscular_instance


class MuscularSystemService:
    """
    Agent Work Execution Monitoring - the muscles of the AI body.

    Monitors agent execution performance, tracking strength, fatigue,
    and strain across muscle groups to ensure healthy agent operation.
    """

    # Health thresholds (based on strength score)
    STRONG_THRESHOLD = 80.0       # 80%+ = strong
    FIT_THRESHOLD = 60.0          # 60-80% = fit
    FATIGUED_THRESHOLD = 40.0     # 40-60% = fatigued
    STRAINED_THRESHOLD = 20.0     # 20-40% = strained
    # Below 20% = paralyzed

    # Cache duration
    CACHE_DURATION_SECONDS = 45

    # Status UUID for singleton record
    STATUS_UUID = uuid.UUID('00000000-0000-0000-0000-000000000007')

    def __init__(self):
        self._cached_pulse = None
        self._cache_time = None

    def flex(self, force: bool = False) -> dict:
        """
        Run full muscular check - the main health check method.

        Returns:
            dict: Comprehensive muscular status including:
                - overall_status: strong/fit/fatigued/strained/paralyzed
                - strength_score: 0-100%
                - per-group metrics
                - weak and overworked muscles
        """
        from core.models_muscular import MuscleGroup, MuscularPulse, MuscleStatus

        start_time = timezone.now()
        cutoff_24h = timezone.now() - timedelta(hours=24)

        # Get all active muscle groups
        groups = MuscleGroup.objects.filter(is_active=True)
        groups_checked = groups.count()

        # Track group statuses
        groups_strong = 0
        groups_fit = 0
        groups_fatigued = 0
        groups_strained = 0
        groups_paralyzed = 0

        # Per-group metrics
        group_metrics = {}
        all_weak_muscles = []
        all_overworked_muscles = []

        # Calculate overall execution stats
        execution_stats = self._get_execution_stats(cutoff_24h)

        # Check each muscle group
        for group in groups:
            group_result = self._check_muscle_group(group, cutoff_24h)
            group_metrics[group.category] = group_result

            # Track group status distribution
            status = group_result.get('status', 'fit')
            if status == 'strong':
                groups_strong += 1
            elif status == 'fit':
                groups_fit += 1
            elif status == 'fatigued':
                groups_fatigued += 1
            elif status == 'strained':
                groups_strained += 1
            else:
                groups_paralyzed += 1

            # Collect weak muscles
            all_weak_muscles.extend(group_result.get('weak_agents', []))
            all_overworked_muscles.extend(group_result.get('overworked_agents', []))

            # Update group status in DB
            self._update_group_status(group, group_result)

        # Calculate overall strength score (weighted by criticality)
        critical_scores = []
        non_critical_scores = []

        for group in groups:
            result = group_metrics.get(group.category, {})
            score = result.get('strength_score', 100)
            if group.is_critical:
                critical_scores.append(score)
            else:
                non_critical_scores.append(score)

        # Weight critical groups higher (70/30)
        if critical_scores:
            critical_avg = sum(critical_scores) / len(critical_scores)
        else:
            critical_avg = 100

        if non_critical_scores:
            non_critical_avg = sum(non_critical_scores) / len(non_critical_scores)
        else:
            non_critical_avg = 100

        if critical_scores and non_critical_scores:
            strength_score = (critical_avg * 0.7) + (non_critical_avg * 0.3)
        elif critical_scores:
            strength_score = critical_avg
        else:
            strength_score = non_critical_avg

        # Determine overall status
        overall_status = self._determine_status(strength_score)
        is_strong = overall_status in ('strong', 'fit')

        # Count agent stats
        total_agents = self._get_total_agent_count()
        active_agents = execution_stats.get('active_agents', 0)
        idle_agents = total_agents - active_agents if total_agents > active_agents else 0
        fatigued_agents = len([m for m in all_overworked_muscles])
        strained_agents = len(all_weak_muscles)

        # Check integrations
        heart_connected = self._check_heart_connection()
        digestive_connected = self._check_digestive_connection()

        end_time = timezone.now()
        check_duration_ms = (end_time - start_time).total_seconds() * 1000

        # Create pulse record
        pulse = MuscularPulse.objects.create(
            overall_status=overall_status,
            strength_score=strength_score,
            is_strong=is_strong,

            # Execution metrics
            total_executions_24h=execution_stats.get('total', 0),
            successful_executions_24h=execution_stats.get('successful', 0),
            failed_executions_24h=execution_stats.get('failed', 0),
            success_rate_24h=execution_stats.get('success_rate', 100.0),

            # Performance metrics
            avg_execution_time_ms=execution_stats.get('avg_time_ms', 0),
            min_execution_time_ms=execution_stats.get('min_time_ms', 0),
            max_execution_time_ms=execution_stats.get('max_time_ms', 0),
            total_tokens_used_24h=execution_stats.get('total_tokens', 0),
            total_cost_24h=Decimal(str(execution_stats.get('total_cost', 0))),

            # Load metrics
            total_agents=total_agents,
            active_agents=active_agents,
            idle_agents=idle_agents,
            fatigued_agents=fatigued_agents,
            strained_agents=strained_agents,

            # Group breakdown
            group_metrics=group_metrics,

            # Issues
            weak_muscles=all_weak_muscles[:20],  # Top 20
            overworked_muscles=all_overworked_muscles[:20],

            # Groups info
            groups_checked=groups_checked,
            groups_strong=groups_strong,
            groups_fit=groups_fit,
            groups_fatigued=groups_fatigued,
            groups_strained=groups_strained,
            groups_paralyzed=groups_paralyzed,

            # Integrations
            heart_connected=heart_connected,
            digestive_connected=digestive_connected,

            # Metadata
            check_duration_ms=int(check_duration_ms),
        )

        # Cache result
        self._cached_pulse = pulse
        self._cache_time = timezone.now()

        result = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': overall_status,
            'strength_score': round(strength_score, 1),
            'is_strong': is_strong,
            'check_duration_ms': round(check_duration_ms, 2),

            # Execution summary
            'execution_summary': {
                'total_24h': execution_stats.get('total', 0),
                'successful_24h': execution_stats.get('successful', 0),
                'failed_24h': execution_stats.get('failed', 0),
                'success_rate': round(execution_stats.get('success_rate', 100), 1),
                'avg_execution_time_ms': round(execution_stats.get('avg_time_ms', 0), 0),
                'total_tokens_24h': execution_stats.get('total_tokens', 0),
                'total_cost_24h': round(execution_stats.get('total_cost', 0), 4),
            },

            # Agent summary
            'agent_summary': {
                'total_agents': total_agents,
                'active_agents': active_agents,
                'idle_agents': idle_agents,
                'fatigued_agents': fatigued_agents,
                'strained_agents': strained_agents,
            },

            # Groups
            'groups': {
                cat: {
                    'status': data.get('status', 'fit'),
                    'strength_score': round(data.get('strength_score', 100), 1),
                    'executions_24h': data.get('executions', 0),
                    'success_rate': round(data.get('success_rate', 100), 1),
                }
                for cat, data in group_metrics.items()
            },

            # Groups summary
            'groups_summary': {
                'checked': groups_checked,
                'strong': groups_strong,
                'fit': groups_fit,
                'fatigued': groups_fatigued,
                'strained': groups_strained,
                'paralyzed': groups_paralyzed,
            },

            # Issues
            'weak_muscles': all_weak_muscles[:10],
            'overworked_muscles': all_overworked_muscles[:10],

            # Integrations
            'integrations': {
                'heart': heart_connected,
                'digestive': digestive_connected,
            },
        }

        logger.info(f"MUSCULAR check: {overall_status} ({strength_score:.1f}%) - "
                   f"Executions: {execution_stats.get('total', 0)}, "
                   f"Active: {active_agents}/{total_agents} agents")

        return result

    def is_strong(self) -> bool:
        """Quick check - are agents executing well?"""
        pulse = self._get_cached_pulse()
        return pulse.is_strong if pulse else True

    def get_vitals(self) -> dict:
        """Get current muscular vitals (cached)."""
        pulse = self._get_cached_pulse()
        if not pulse:
            try:
                return self.flex()
            except Exception as e:
                logger.warning(f"MUSCULAR full check failed, returning defaults: {e}")
                return {
                    'overall_status': 'unknown',
                    'strength_score': 50,
                    'is_strong': True,
                    'success_rate_24h': 0,
                    'total_executions_24h': 0,
                    'active_agents': 0,
                    'total_agents': 0,
                    'fatigued_agents': [],
                    'strained_agents': [],
                    'weak_muscles': [],
                    'overworked_muscles': [],
                    'error': str(e),
                }

        return {
            'timestamp': pulse.recorded_at.isoformat(),
            'overall_status': pulse.overall_status,
            'strength_score': pulse.strength_score,
            'is_strong': pulse.is_strong,
            'success_rate_24h': pulse.success_rate_24h,
            'total_executions_24h': pulse.total_executions_24h,
            'active_agents': pulse.active_agents,
            'total_agents': pulse.total_agents,
            'fatigued_agents': pulse.fatigued_agents,
            'strained_agents': pulse.strained_agents,
            'weak_muscles': pulse.weak_muscles[:5],
            'overworked_muscles': pulse.overworked_muscles[:5],
        }

    def get_status(self) -> dict:
        """Get current status for body coordinator integration."""
        return self.get_vitals()

    def get_history(self, hours: int = 24, limit: int = 100) -> List[dict]:
        """Get muscular pulse history."""
        from core.models_muscular import MuscularPulse

        cutoff = timezone.now() - timedelta(hours=hours)
        pulses = MuscularPulse.objects.filter(recorded_at__gte=cutoff)[:limit]

        return [
            {
                'id': str(p.id),
                'timestamp': p.recorded_at.isoformat(),
                'status': p.overall_status,
                'strength_score': p.strength_score,
                'is_strong': p.is_strong,
                'total_executions': p.total_executions_24h,
                'success_rate': p.success_rate_24h,
                'active_agents': p.active_agents,
                'check_duration_ms': p.check_duration_ms,
            }
            for p in pulses
        ]

    def check_muscle_group(self, group_name: str) -> dict:
        """Check specific muscle group health (public method)."""
        from core.models_muscular import MuscleGroup

        cutoff_24h = timezone.now() - timedelta(hours=24)

        try:
            group = MuscleGroup.objects.get(name=group_name)
        except MuscleGroup.DoesNotExist:
            return {'error': f'Muscle group {group_name} not found'}

        return self._check_muscle_group(group, cutoff_24h)

    def get_group_agents(self, group_name: str) -> List[dict]:
        """Get agents in a muscle group with their status."""
        from core.models_muscular import MuscleGroup
        from core.models_unified_system import Agent, AgentExecution

        cutoff_24h = timezone.now() - timedelta(hours=24)

        try:
            group = MuscleGroup.objects.get(name=group_name)
        except MuscleGroup.DoesNotExist:
            return []

        agents_data = []
        for agent_name in group.agent_names:
            try:
                agent = Agent.objects.get(name=agent_name)

                # Get 24h executions
                executions = AgentExecution.objects.filter(
                    agent=agent,
                    created_at__gte=cutoff_24h
                )
                total = executions.count()
                successful = executions.filter(status='completed').count()
                failed = executions.filter(status='failed').count()

                success_rate = (successful / total * 100) if total > 0 else 100.0

                # Calculate performance metrics
                stats = executions.aggregate(
                    avg_time=Avg('execution_time_ms'),
                    total_tokens=Sum('tokens_used'),
                    total_cost=Sum('cost')
                )

                agents_data.append({
                    'name': agent_name,
                    'executions_24h': total,
                    'successful_24h': successful,
                    'failed_24h': failed,
                    'success_rate': round(success_rate, 1),
                    'avg_execution_time_ms': round(stats['avg_time'] or 0, 0),
                    'tokens_used_24h': stats['total_tokens'] or 0,
                    'cost_24h': float(stats['total_cost'] or 0),
                })
            except Agent.DoesNotExist:
                agents_data.append({
                    'name': agent_name,
                    'status': 'not_found',
                })

        return agents_data

    def detect_weak_muscles(self) -> List[dict]:
        """Find agents with low success rates."""
        from core.models_unified_system import Agent, AgentExecution

        cutoff_24h = timezone.now() - timedelta(hours=24)
        weak_muscles = []

        # Get agents with executions in last 24h
        agents_with_activity = AgentExecution.objects.filter(
            created_at__gte=cutoff_24h
        ).values('agent__name').annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed'))
        ).filter(total__gte=5)  # At least 5 executions

        for agent_data in agents_with_activity:
            success_rate = (agent_data['successful'] / agent_data['total'] * 100) if agent_data['total'] > 0 else 100
            if success_rate < 80:  # Below 80% is weak
                weak_muscles.append({
                    'agent': agent_data['agent__name'],
                    'success_rate': round(success_rate, 1),
                    'executions_24h': agent_data['total'],
                    'failed_24h': agent_data['failed'],
                    'issue': f"Low success rate ({success_rate:.1f}%)",
                    'severity': 'critical' if success_rate < 50 else 'warning',
                })

        # Sort by success rate (worst first)
        return sorted(weak_muscles, key=lambda x: x['success_rate'])

    def detect_overworked_muscles(self) -> List[dict]:
        """Find agents with high execution counts."""
        from core.models_muscular import MuscleGroup
        from core.models_unified_system import AgentExecution

        cutoff_24h = timezone.now() - timedelta(hours=24)
        overworked_muscles = []

        # Get execution counts per agent
        agent_counts = AgentExecution.objects.filter(
            created_at__gte=cutoff_24h
        ).values('agent__name').annotate(
            count=Count('id'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost')
        ).order_by('-count')

        # Get max daily executions thresholds from groups
        thresholds = {}
        for group in MuscleGroup.objects.all():
            for agent_name in group.agent_names:
                thresholds[agent_name] = group.max_daily_executions

        for agent_data in agent_counts:
            agent_name = agent_data['agent__name']
            max_daily = thresholds.get(agent_name, 500)  # Default 500

            if agent_data['count'] > max_daily:
                overworked_muscles.append({
                    'agent': agent_name,
                    'executions_24h': agent_data['count'],
                    'max_daily': max_daily,
                    'tokens_used': agent_data['total_tokens'] or 0,
                    'cost': float(agent_data['total_cost'] or 0),
                    'issue': f"High execution count ({agent_data['count']} > {max_daily})",
                    'severity': 'warning' if agent_data['count'] < max_daily * 1.5 else 'critical',
                })

        return overworked_muscles

    def get_groups(self, category: str = None, active_only: bool = True) -> List[dict]:
        """Get monitored muscle groups."""
        from core.models_muscular import MuscleGroup

        queryset = MuscleGroup.objects.all()

        if active_only:
            queryset = queryset.filter(is_active=True)
        if category:
            queryset = queryset.filter(category=category)

        return [
            {
                'id': str(g.id),
                'name': g.name,
                'display_name': g.display_name,
                'category': g.category,
                'description': g.description,
                'agent_count': len(g.agent_names),
                'agents': g.agent_names,
                'is_critical': g.is_critical,
                'is_active': g.is_active,
                'target_success_rate': g.target_success_rate,
                'max_daily_executions': g.max_daily_executions,
            }
            for g in queryset
        ]

    def get_status_emoji(self) -> str:
        """Get emoji for current status."""
        pulse = self._get_cached_pulse()
        if not pulse:
            return '?'

        return {
            'strong': '💪',      # Flexed bicep - strong
            'fit': '🏃',         # Runner - fit
            'fatigued': '😓',    # Sweating - tired
            'strained': '🥵',    # Hot face - stressed
            'paralyzed': '🦽',   # Wheelchair - immobile
        }.get(pulse.overall_status, '?')

    # Private methods

    def _check_muscle_group(self, group, cutoff_24h) -> dict:
        """Check health of a specific muscle group."""
        from core.models_unified_system import Agent, AgentExecution

        # Get agents in this group
        agent_names = group.agent_names or []
        if not agent_names:
            return {
                'status': 'paralyzed',
                'strength_score': 0,
                'executions': 0,
                'success_rate': 0,
                'issue': 'No agents in group',
            }

        # Get executions for these agents
        executions = AgentExecution.objects.filter(
            agent__name__in=agent_names,
            created_at__gte=cutoff_24h
        )

        total = executions.count()
        successful = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()

        success_rate = (successful / total * 100) if total > 0 else 100.0

        # Get performance stats
        stats = executions.aggregate(
            avg_time=Avg('execution_time_ms'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost')
        )

        avg_time_ms = stats['avg_time'] or 0

        # Calculate fatigue (based on execution volume)
        fatigue_level = min(100, (total / group.max_daily_executions) * 100) if group.max_daily_executions > 0 else 0

        # Calculate strain (based on error rate)
        error_rate = (failed / total * 100) if total > 0 else 0
        strain_level = min(100, error_rate * 2)  # Double the error rate for strain

        # Calculate strength score
        # Base 100, deduct for errors and slow execution
        strength_score = 100.0

        # Deduct for low success rate
        if success_rate < group.target_success_rate:
            deduction = (group.target_success_rate - success_rate)
            strength_score -= deduction

        # Deduct for slow execution
        if avg_time_ms > group.max_avg_execution_time_ms:
            slowness = ((avg_time_ms / group.max_avg_execution_time_ms) - 1) * 20
            strength_score -= min(30, slowness)

        # Deduct for high fatigue
        if fatigue_level > group.max_fatigue_level:
            strength_score -= (fatigue_level - group.max_fatigue_level) * 0.5

        strength_score = max(0, min(100, strength_score))
        status = self._determine_status(strength_score)

        # Handle no activity
        if total == 0:
            status = 'paralyzed'
            strength_score = min(strength_score, 19)

        # Find weak and overworked agents in this group
        weak_agents = []
        overworked_agents = []

        per_agent_stats = executions.values('agent__name').annotate(
            count=Count('id'),
            successful=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed'))
        )

        for agent_stat in per_agent_stats:
            agent_success_rate = (agent_stat['successful'] / agent_stat['count'] * 100) if agent_stat['count'] > 0 else 100
            if agent_success_rate < 80 and agent_stat['count'] >= 5:
                weak_agents.append({
                    'agent': agent_stat['agent__name'],
                    'success_rate': round(agent_success_rate, 1),
                    'executions': agent_stat['count'],
                    'issue': f"Low success rate ({agent_success_rate:.1f}%)",
                })

            if agent_stat['count'] > group.max_daily_executions:
                overworked_agents.append({
                    'agent': agent_stat['agent__name'],
                    'executions': agent_stat['count'],
                    'max': group.max_daily_executions,
                    'issue': f"Overworked ({agent_stat['count']} > {group.max_daily_executions})",
                })

        # Count active agents
        active_agent_names = set(executions.values_list('agent__name', flat=True).distinct())
        active_count = len(active_agent_names)
        idle_count = len(agent_names) - active_count

        return {
            'status': status,
            'strength_score': strength_score,
            'executions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'avg_time_ms': avg_time_ms,
            'fatigue_level': fatigue_level,
            'strain_level': strain_level,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': float(stats['total_cost'] or 0),
            'total_agents': len(agent_names),
            'active_agents': active_count,
            'idle_agents': idle_count,
            'weak_agents': weak_agents,
            'overworked_agents': overworked_agents,
        }

    def _update_group_status(self, group, result: dict):
        """Update group status in database."""
        from core.models_muscular import MuscleStatus

        status_obj, created = MuscleStatus.objects.get_or_create(
            group=group,
            defaults={'status': 'fit', 'is_healthy': True}
        )

        status_obj.status = result.get('status', 'fit')
        status_obj.is_healthy = result.get('status') in ('strong', 'fit')
        status_obj.strength_score = result.get('strength_score', 100)
        status_obj.fatigue_level = result.get('fatigue_level', 0)
        status_obj.strain_level = result.get('strain_level', 0)
        status_obj.executions_24h = result.get('executions', 0)
        status_obj.successful_24h = result.get('successful', 0)
        status_obj.failed_24h = result.get('failed', 0)
        status_obj.success_rate_24h = result.get('success_rate', 100)
        status_obj.avg_execution_time_ms = result.get('avg_time_ms', 0)
        status_obj.tokens_used_24h = result.get('total_tokens', 0)
        status_obj.cost_24h = Decimal(str(result.get('total_cost', 0)))
        status_obj.total_agents = result.get('total_agents', 0)
        status_obj.active_agents = result.get('active_agents', 0)
        status_obj.idle_agents = result.get('idle_agents', 0)

        # Find top/worst performers
        weak = result.get('weak_agents', [])
        if weak:
            status_obj.worst_performer = weak[0].get('agent', '')

        status_obj.save()

    def _get_execution_stats(self, cutoff) -> dict:
        """Get overall execution statistics."""
        from core.models_unified_system import AgentExecution

        executions = AgentExecution.objects.filter(created_at__gte=cutoff)

        total = executions.count()
        successful = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()

        success_rate = (successful / total * 100) if total > 0 else 100.0

        stats = executions.aggregate(
            avg_time=Avg('execution_time_ms'),
            min_time=Min('execution_time_ms'),
            max_time=Max('execution_time_ms'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost')
        )

        # Count distinct active agents
        active_agents = executions.values('agent').distinct().count()

        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'avg_time_ms': stats['avg_time'] or 0,
            'min_time_ms': stats['min_time'] or 0,
            'max_time_ms': stats['max_time'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': float(stats['total_cost'] or 0),
            'active_agents': active_agents,
        }

    def _get_total_agent_count(self) -> int:
        """Get total agent count."""
        from core.models_unified_system import Agent
        return Agent.objects.filter(is_active=True).count()

    def _determine_status(self, score: float) -> str:
        """Determine status based on score."""
        if score >= self.STRONG_THRESHOLD:
            return 'strong'
        elif score >= self.FIT_THRESHOLD:
            return 'fit'
        elif score >= self.FATIGUED_THRESHOLD:
            return 'fatigued'
        elif score >= self.STRAINED_THRESHOLD:
            return 'strained'
        else:
            return 'paralyzed'

    def _get_cached_pulse(self) -> Optional['MuscularPulse']:
        """Get cached pulse or fetch most recent from DB."""
        from core.models_muscular import MuscularPulse

        if (self._cached_pulse and self._cache_time and
            (timezone.now() - self._cache_time).total_seconds() < self.CACHE_DURATION_SECONDS):
            return self._cached_pulse

        try:
            pulse = MuscularPulse.objects.order_by('-recorded_at').first()
            self._cached_pulse = pulse
            self._cache_time = timezone.now()
            return pulse
        except Exception as _e:
            logger.warning(
                "muscular._get_cached_pulse: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _check_heart_connection(self) -> bool:
        """Check if HEART service is accessible."""
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            return heart.is_alive()
        except Exception as _e:
            logger.warning(
                "muscular._check_heart_connection: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def _check_digestive_connection(self) -> bool:
        """Check if DIGESTIVE service is accessible."""
        try:
            from core.services.digestive import get_digestive_system
            digestive = get_digestive_system()
            return digestive.is_digesting()
        except Exception as _e:
            logger.warning(
                "muscular._check_digestive_connection: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False
