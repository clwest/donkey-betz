"""
Session 702: LUNGS Service - Resource and Capacity Management

LUNGS = Limits, Usage, Notifications, Governance, Spending

The LUNGS manage the system's "breathing" - tracking token/cost consumption
against budgets and alerting when thresholds are crossed.

Human Body Metaphor:
- breathe() = Full respiratory check
- oxygen_level = Remaining budget %
- can_breathe() = Budget check before LLM call
- record_breath() = Log consumption after LLM call
- hyperventilation = Over budget alert

Usage:
    from core.services.lungs import get_lungs_monitor

    lungs = get_lungs_monitor()

    # Run full breathing check
    status = lungs.breathe()
    print(f"Oxygen: {status['oxygen_level']:.1f}%")

    # Check if we can make an LLM call
    allowed, reason = lungs.can_breathe(provider='openai', agent='ResearchAgent')
    if not allowed:
        print(f"Cannot breathe: {reason}")

    # Record consumption after a call
    lungs.record_breath(provider='openai', agent='ResearchAgent', tokens=1500, cost=0.0225)
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Tuple

from django.db.models import Sum, Count
from django.utils import timezone

logger = logging.getLogger(__name__)

# Singleton instance
_lungs_instance: Optional['LungsCapacityService'] = None


def get_lungs_monitor() -> 'LungsCapacityService':
    """Get the singleton LungsCapacityService instance."""
    global _lungs_instance
    if _lungs_instance is None:
        _lungs_instance = LungsCapacityService()
    return _lungs_instance


class LungsCapacityService:
    """
    Resource and capacity management - the breathing of the AI body.

    Monitors token/cost consumption against budgets, calculates forecasts,
    and sends alerts when thresholds are crossed.
    """

    def __init__(self):
        """Initialize the LUNGS service."""
        self._initialized = False

    def breathe(self) -> dict:
        """
        Run full breathing check - aggregate consumption and update statuses.

        This is the main respiratory function, similar to HEART's pulse().
        """
        import time
        start_time = time.time()

        from core.models_lungs import Budget, BreathCycle, RespiratoryStatus

        results = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'normal',
            'oxygen_level': 100.0,
            'respiratory_rate': 0.0,
            'breathing_metrics': {
                'system': {},
                'providers': {},
                'agents': {},
            },
            'budgets_checked': 0,
            'alerts': [],
            'can_breathe': True,
        }

        # Get all active budgets
        active_budgets = Budget.objects.filter(is_active=True)
        total_oxygen = 0.0
        budget_count = 0

        for budget in active_budgets:
            try:
                # Get or create current breath cycle
                cycle = self.get_current_cycle(budget)

                # Aggregate usage from LLMCallLog
                usage = self._aggregate_usage_for_cycle(cycle)

                # Update cycle with aggregated data
                cycle.tokens_used = usage.get('total_tokens') or 0
                cycle.cost_incurred = Decimal(str(usage.get('total_cost') or 0))
                cycle.call_count = usage.get('call_count') or 0
                cycle.update_remaining()

                # Calculate forecast
                self._calculate_forecast(cycle)

                # Check alerts
                alerts = self._check_and_alert(cycle)
                results['alerts'].extend(alerts)

                cycle.save()

                # Update respiratory status cache
                self._update_respiratory_status(budget, cycle)

                # Track metrics
                oxygen = cycle.get_oxygen_level()
                total_oxygen += oxygen
                budget_count += 1

                # Add to results based on scope
                scope_key = budget.get_scope_key()
                metric = {
                    'name': budget.name,
                    'oxygen_level': oxygen,
                    'status': self._get_status_from_oxygen(oxygen),
                    'tokens_used': cycle.tokens_used,
                    'cost_incurred': float(cycle.cost_incurred),
                    'call_count': cycle.call_count,
                    'utilization_percent': cycle.utilization_percent,
                    'limit': float(budget.cost_limit) if budget.cost_limit else budget.token_limit,
                    'remaining': float(cycle.cost_remaining) if cycle.cost_remaining else cycle.tokens_remaining,
                    'projected_end': float(cycle.projected_end_usage) if cycle.projected_end_usage else None,
                    'on_pace_to_exceed': cycle.on_pace_to_exceed,
                }

                if budget.scope == 'system':
                    results['breathing_metrics']['system'] = metric
                elif budget.scope == 'provider':
                    results['breathing_metrics']['providers'][budget.scope_identifier] = metric
                elif budget.scope == 'agent':
                    results['breathing_metrics']['agents'][budget.scope_identifier] = metric

            except Exception as e:
                logger.exception(f"Error checking budget {budget.name}: {e}")
                results['alerts'].append({
                    'type': 'error',
                    'budget': budget.name,
                    'message': str(e),
                })

        # Calculate overall metrics
        results['budgets_checked'] = budget_count
        if budget_count > 0:
            results['oxygen_level'] = total_oxygen / budget_count
            results['overall_status'] = self._get_status_from_oxygen(results['oxygen_level'])

        # Calculate respiratory rate (calls per minute over last 15 min)
        results['respiratory_rate'] = self._calculate_respiratory_rate()

        # Check if we can breathe overall
        results['can_breathe'] = results['oxygen_level'] > 0

        # Calculate check duration
        results['check_duration_ms'] = int((time.time() - start_time) * 1000)

        return results

    def check_oxygen_level(self, scope: str = 'system', identifier: str = None) -> float:
        """
        Get remaining budget percentage for a specific scope.

        Args:
            scope: 'system', 'provider', or 'agent'
            identifier: Provider or agent name (required for non-system scope)

        Returns:
            Oxygen level 0-100 (100 = full budget, 0 = exhausted)
        """
        from core.models_lungs import RespiratoryStatus

        component = scope if not identifier else f"{scope}:{identifier}"

        try:
            status = RespiratoryStatus.objects.get(component=component)
            return status.oxygen_level
        except RespiratoryStatus.DoesNotExist:
            return 100.0  # No budget configured = unlimited

    def can_breathe(
        self,
        provider: str = None,
        agent: str = None,
        estimated_tokens: int = 0
    ) -> Tuple[bool, str]:
        """
        Check if an LLM call is allowed within budget.

        This should be called BEFORE making an LLM call.

        Args:
            provider: LLM provider name
            agent: Agent name
            estimated_tokens: Estimated tokens for the call

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        from core.models_lungs import Budget, RespiratoryStatus

        # Check system-wide budget first
        try:
            system_status = RespiratoryStatus.objects.get(component='system')
            if system_status.oxygen_level <= 0:
                # Check if hard limit is enforced
                system_budget = Budget.objects.filter(
                    scope='system',
                    period='daily',
                    is_active=True,
                    enforce_hard_limit=True
                ).first()
                if system_budget:
                    return False, "System daily budget exhausted"
        except RespiratoryStatus.DoesNotExist:
            pass

        # Check provider budget
        if provider:
            try:
                provider_status = RespiratoryStatus.objects.get(component=f'provider:{provider}')
                if provider_status.oxygen_level <= 0:
                    provider_budget = Budget.objects.filter(
                        scope='provider',
                        scope_identifier=provider,
                        is_active=True,
                        enforce_hard_limit=True
                    ).first()
                    if provider_budget:
                        return False, f"Provider {provider} daily budget exhausted"
            except RespiratoryStatus.DoesNotExist:
                pass

        # Check agent budget
        if agent:
            try:
                agent_status = RespiratoryStatus.objects.get(component=f'agent:{agent}')
                if agent_status.oxygen_level <= 0:
                    agent_budget = Budget.objects.filter(
                        scope='agent',
                        scope_identifier=agent,
                        is_active=True,
                        enforce_hard_limit=True
                    ).first()
                    if agent_budget:
                        return False, f"Agent {agent} daily budget exhausted"
            except RespiratoryStatus.DoesNotExist:
                pass

        return True, "OK"

    def record_breath(
        self,
        provider: str,
        agent: str,
        tokens: int,
        cost: float
    ):
        """
        Record token consumption after an LLM call.

        This should be called AFTER making an LLM call.

        Args:
            provider: LLM provider name
            agent: Agent name
            tokens: Tokens consumed
            cost: Cost in USD
        """
        from core.models_lungs import RespiratoryStatus

        # Update system status
        try:
            system_status = RespiratoryStatus.get_or_create_status('system', 'System Overall')
            system_status.mark_breath(tokens, cost)
            system_status.save()
        except Exception as e:
            logger.warning(f"Failed to update system respiratory status: {e}")

        # Update provider status
        if provider:
            try:
                provider_status = RespiratoryStatus.get_or_create_status(
                    f'provider:{provider}',
                    provider.replace('_', ' ').title()
                )
                provider_status.mark_breath(tokens, cost)
                provider_status.save()
            except Exception as e:
                logger.warning(f"Failed to update provider respiratory status: {e}")

        # Update agent status
        if agent:
            try:
                agent_status = RespiratoryStatus.get_or_create_status(
                    f'agent:{agent}',
                    agent.replace('Agent', ' Agent')
                )
                agent_status.mark_breath(tokens, cost)
                agent_status.save()
            except Exception as e:
                logger.warning(f"Failed to update agent respiratory status: {e}")

    def get_budget(self, scope: str, identifier: str = None) -> Optional['Budget']:
        """Get a specific budget configuration."""
        from core.models_lungs import Budget

        filters = {'scope': scope, 'is_active': True}
        if identifier:
            filters['scope_identifier'] = identifier

        return Budget.objects.filter(**filters).first()

    def get_current_cycle(self, budget: 'Budget') -> 'BreathCycle':
        """
        Get or create the current breath cycle for a budget.

        Creates a new cycle if one doesn't exist for the current period.
        """
        from core.models_lungs import BreathCycle

        now = timezone.now()

        # Calculate period boundaries
        if budget.period == 'daily':
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif budget.period == 'weekly':
            # Start of current week (Monday)
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_start -= timedelta(days=period_start.weekday())
            period_end = period_start + timedelta(weeks=1)
        elif budget.period == 'monthly':
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # First day of next month
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
        else:
            # Default to daily
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)

        # Get or create the cycle
        cycle, created = BreathCycle.objects.get_or_create(
            budget=budget,
            period_start=period_start,
            defaults={
                'period_end': period_end,
            }
        )

        if created:
            logger.info(f"Created new breath cycle for {budget.name}: {period_start}")

        return cycle

    def forecast_end_of_period(self, budget: 'Budget') -> dict:
        """
        Project end-of-period usage based on current velocity.

        Returns forecast details including projected cost and whether
        we're on pace to exceed the budget.
        """
        cycle = self.get_current_cycle(budget)

        now = timezone.now()
        period_elapsed = (now - cycle.period_start).total_seconds()
        period_total = (cycle.period_end - cycle.period_start).total_seconds()

        if period_elapsed <= 0 or period_total <= 0:
            return {
                'projected_cost': 0,
                'projected_tokens': 0,
                'on_pace_to_exceed': False,
                'confidence': 0,
            }

        # Calculate velocity (per second)
        cost_velocity = float(cycle.cost_incurred) / period_elapsed
        token_velocity = cycle.tokens_used / period_elapsed

        # Project to end of period
        remaining_seconds = period_total - period_elapsed
        projected_additional_cost = cost_velocity * remaining_seconds
        projected_additional_tokens = int(token_velocity * remaining_seconds)

        projected_total_cost = float(cycle.cost_incurred) + projected_additional_cost
        projected_total_tokens = cycle.tokens_used + projected_additional_tokens

        # Check if on pace to exceed
        on_pace = False
        if budget.cost_limit:
            on_pace = projected_total_cost > float(budget.cost_limit)
        elif budget.token_limit:
            on_pace = projected_total_tokens > budget.token_limit

        # Calculate confidence based on how much of the period has elapsed
        confidence = min(period_elapsed / period_total, 1.0)

        return {
            'projected_cost': projected_total_cost,
            'projected_tokens': projected_total_tokens,
            'on_pace_to_exceed': on_pace,
            'confidence': confidence,
            'period_elapsed_percent': (period_elapsed / period_total) * 100,
        }

    def get_spending_velocity(self, hours: int = 24) -> dict:
        """
        Calculate current spending rate over recent period.

        Args:
            hours: Hours to look back

        Returns:
            Dict with cost_per_hour, tokens_per_hour, calls_per_hour
        """
        from core.models_llm_routing import LLMCallLog

        since = timezone.now() - timedelta(hours=hours)

        stats = LLMCallLog.objects.filter(created_at__gte=since).aggregate(
            total_cost=Sum('cost'),
            total_tokens=Sum('total_tokens'),
            call_count=Count('id')
        )

        total_cost = float(stats['total_cost'] or 0)
        total_tokens = stats['total_tokens'] or 0
        call_count = stats['call_count'] or 0

        return {
            'cost_per_hour': total_cost / hours if hours > 0 else 0,
            'tokens_per_hour': total_tokens / hours if hours > 0 else 0,
            'calls_per_hour': call_count / hours if hours > 0 else 0,
            'hours_analyzed': hours,
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'total_calls': call_count,
        }

    def get_respiratory_status(self) -> dict:
        """Get all respiratory statuses (cached)."""
        from core.models_lungs import RespiratoryStatus
        return RespiratoryStatus.get_all_vitals()

    def get_vitals(self) -> dict:
        """
        Get current breathing vitals for dashboard.

        Returns a simplified view of respiratory status.
        """
        from core.models_lungs import RespiratoryStatus

        vitals = {
            'timestamp': timezone.now().isoformat(),
            'system_oxygen': 100.0,
            'system_status': 'normal',
            'providers': {},
            'total_cost_today': 0.0,
            'total_calls_today': 0,
        }

        for status in RespiratoryStatus.objects.all():
            if status.component == 'system':
                vitals['system_oxygen'] = status.oxygen_level
                vitals['system_status'] = status.status
                vitals['total_cost_today'] = float(status.cost_today)
                vitals['total_calls_today'] = status.calls_today
            elif status.component.startswith('provider:'):
                provider_name = status.component.split(':')[1]
                vitals['providers'][provider_name] = {
                    'oxygen_level': status.oxygen_level,
                    'status': status.status,
                    'cost_today': float(status.cost_today),
                    'calls_today': status.calls_today,
                }

        # Session 712: Add overall_status for body_vitals compatibility
        vitals['overall_status'] = vitals['system_status']
        vitals['oxygen_level'] = vitals['system_oxygen']

        return vitals

    def is_breathing(self) -> bool:
        """Quick check - are we within system budget?"""
        return self.check_oxygen_level('system') > 0

    def get_history(self, hours: int = 24, limit: int = 100) -> list:
        """Get breath cycle history."""
        from core.models_lungs import BreathCycle

        since = timezone.now() - timedelta(hours=hours)
        cycles = BreathCycle.objects.filter(
            recorded_at__gte=since
        ).select_related('budget').order_by('-recorded_at')[:limit]

        return [
            {
                'budget_name': cycle.budget.name,
                'scope': cycle.budget.get_scope_key(),
                'period_start': cycle.period_start.isoformat(),
                'period_end': cycle.period_end.isoformat(),
                'tokens_used': cycle.tokens_used,
                'cost_incurred': float(cycle.cost_incurred),
                'call_count': cycle.call_count,
                'utilization_percent': cycle.utilization_percent,
                'oxygen_level': cycle.get_oxygen_level(),
                'warning_sent': cycle.warning_sent,
                'critical_sent': cycle.critical_sent,
                'recorded_at': cycle.recorded_at.isoformat(),
            }
            for cycle in cycles
        ]

    # Private helper methods

    def _aggregate_usage_for_cycle(self, cycle: 'BreathCycle') -> dict:
        """Aggregate usage from LLMCallLog for a breath cycle."""
        from core.models_llm_routing import LLMCallLog

        filters = {
            'created_at__gte': cycle.period_start,
            'created_at__lt': cycle.period_end,
        }

        # Add scope filter
        if cycle.budget.scope == 'provider':
            filters['provider'] = cycle.budget.scope_identifier
        elif cycle.budget.scope == 'agent':
            filters['agent_name'] = cycle.budget.scope_identifier

        try:
            stats = LLMCallLog.objects.filter(**filters).aggregate(
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('cost'),
                call_count=Count('id')
            )
            return stats
        except Exception as e:
            logger.warning(f"Failed to aggregate LLM usage: {e}")
            return {'total_tokens': 0, 'total_cost': 0, 'call_count': 0}

    def _calculate_forecast(self, cycle: 'BreathCycle'):
        """Calculate forecast for a breath cycle."""
        forecast = self.forecast_end_of_period(cycle.budget)
        cycle.projected_end_usage = Decimal(str(forecast['projected_cost']))
        cycle.on_pace_to_exceed = forecast['on_pace_to_exceed']

    def _check_and_alert(self, cycle: 'BreathCycle') -> list:
        """Check thresholds and send alerts if needed."""
        alerts = []

        # Check warning threshold
        if cycle.is_warning() and not cycle.warning_sent:
            alert = self._send_warning_alert(cycle)
            if alert:
                alerts.append(alert)
                cycle.warning_sent = True

        # Check critical threshold
        if cycle.is_critical() and not cycle.critical_sent:
            alert = self._send_critical_alert(cycle)
            if alert:
                alerts.append(alert)
                cycle.critical_sent = True

        return alerts

    def _send_warning_alert(self, cycle: 'BreathCycle') -> dict:
        """Send warning alert to Discord."""
        alert = {
            'type': 'warning',
            'budget': cycle.budget.name,
            'utilization': cycle.utilization_percent,
            'message': f"Budget {cycle.budget.name} at {cycle.utilization_percent:.1f}% utilization"
        }

        try:
            from core.services.discord_notifications import DiscordNotificationService
            service = DiscordNotificationService()
            service.send_system_status(
                f"LUNGS Warning: {cycle.budget.name} at {cycle.utilization_percent:.1f}%",
                color=0xFFA500  # Orange
            )
        except Exception as e:
            logger.warning(f"Failed to send Discord warning alert: {e}")

        return alert

    def _send_critical_alert(self, cycle: 'BreathCycle') -> dict:
        """Send critical alert to Discord."""
        alert = {
            'type': 'critical',
            'budget': cycle.budget.name,
            'utilization': cycle.utilization_percent,
            'message': f"CRITICAL: Budget {cycle.budget.name} at {cycle.utilization_percent:.1f}%!"
        }

        try:
            from core.services.discord_notifications import DiscordNotificationService
            service = DiscordNotificationService()
            service.send_system_status(
                f"LUNGS CRITICAL: {cycle.budget.name} at {cycle.utilization_percent:.1f}%! "
                f"Cost: ${float(cycle.cost_incurred):.2f}",
                color=0xFF0000  # Red
            )
        except Exception as e:
            logger.warning(f"Failed to send Discord critical alert: {e}")

        return alert

    def _update_respiratory_status(self, budget: 'Budget', cycle: 'BreathCycle'):
        """Update the respiratory status cache for a budget."""
        from core.models_lungs import RespiratoryStatus

        component = budget.get_scope_key()
        display_name = budget.name.replace(' Daily Budget', '').replace(' Monthly Budget', '')

        status = RespiratoryStatus.get_or_create_status(component, display_name)
        status.oxygen_level = cycle.get_oxygen_level()
        status.update_status_from_oxygen()
        status.tokens_used_today = cycle.tokens_used
        status.cost_today = cycle.cost_incurred
        status.calls_today = cycle.call_count

        if budget.cost_limit:
            status.daily_cost_limit = budget.cost_limit
        if budget.token_limit:
            status.daily_token_limit = budget.token_limit

        status.save()

    def _calculate_respiratory_rate(self) -> float:
        """Calculate calls per minute over the last 15 minutes."""
        from core.models_llm_routing import LLMCallLog

        since = timezone.now() - timedelta(minutes=15)

        try:
            count = LLMCallLog.objects.filter(created_at__gte=since).count()
            return count / 15.0  # Calls per minute
        except Exception as _e:
            logger.warning(
                "lungs._calculate_respiratory_rate: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0.0

    def _get_status_from_oxygen(self, oxygen_level: float) -> str:
        """Convert oxygen level to status string."""
        if oxygen_level >= 80:
            return 'normal'
        elif oxygen_level >= 50:
            return 'elevated'
        elif oxygen_level >= 20:
            return 'hyperventilating'
        else:
            return 'holding'
