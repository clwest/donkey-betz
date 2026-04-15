"""
Session 721: BRAIN SYSTEM - Cognitive Processing & Reasoning Service

The BRAIN is the cognitive layer of the AI body - monitoring how the AI
thinks, reasons, and processes information through LLM calls.

Human Body Metaphor:
- Neurons = Individual LLM API calls
- Synapses = Agent-to-agent communication
- Thoughts = Reasoning chains / completions
- Memory Recall = RAG queries, embedding lookups
- Focus = Active conversation count
- Fatigue = High latency, error rates
- Brain Fog = Model timeouts, degraded responses
- Cognitive Load = Concurrent thinking tasks

Key Metrics:
- LLM calls (success rate, latency, tokens)
- Active conversations
- Agent thinking/executions
- RAG query performance
- Model routing decisions
"""

import logging
import time
from datetime import timedelta
from typing import Dict, List, Optional, Any

from django.db.models import Count, Sum, Avg, F, Q, DecimalField, FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Singleton instance
_brain_instance: Optional['BrainService'] = None


def get_brain_service() -> 'BrainService':
    """Get the singleton BrainService instance."""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = BrainService()
    return _brain_instance


class BrainService:
    """
    BRAIN SYSTEM - Cognitive processing and reasoning monitoring.

    Monitors:
    - LLM API calls (latency, success rate, tokens)
    - PA conversations (active, turns, success)
    - Agent thinking/executions
    - RAG/embedding queries
    - Model routing decisions
    """

    # Status thresholds (based on cognitive score)
    FOCUSED_THRESHOLD = 80.0      # Excellent cognitive function
    THINKING_THRESHOLD = 60.0     # Active, slightly elevated
    OVERLOADED_THRESHOLD = 40.0   # High load
    FOGGY_THRESHOLD = 20.0        # Degraded performance

    # Cache keys and TTLs
    CACHE_KEY_STATUS = 'brain:status'
    CACHE_KEY_VITALS = 'brain:vitals'
    CACHE_TTL = 60  # 1 minute cache

    def __init__(self):
        """Initialize the Brain Service."""
        self._last_check = None
        self._last_pulse_id = None

    def think(self, force: bool = False) -> Dict[str, Any]:
        """
        Run full brain check - monitor all cognitive processing.

        Args:
            force: If True, bypass cache and run fresh check

        Returns:
            Dict with brain status and metrics
        """
        start_time = time.time()

        # Check cache unless forced
        if not force:
            cached = cache.get(self.CACHE_KEY_STATUS)
            if cached:
                return cached

        try:
            # Get time window
            now = timezone.now()
            window_24h = now - timedelta(hours=24)
            window_1h = now - timedelta(hours=1)

            # Collect metrics from various sources
            llm_metrics = self._collect_llm_metrics(window_24h)
            conversation_metrics = self._collect_conversation_metrics(window_24h)
            agent_metrics = self._collect_agent_metrics(window_24h)
            rag_metrics = self._collect_rag_metrics(window_24h)
            routing_metrics = self._collect_routing_metrics(window_24h)

            # Calculate cognitive score
            cognitive_score = self._calculate_cognitive_score(
                llm_metrics, conversation_metrics, agent_metrics
            )

            # Determine status
            overall_status = self._determine_status(
                cognitive_score, llm_metrics, agent_metrics
            )

            # Detect issues
            issues = self._detect_issues(
                llm_metrics, conversation_metrics, agent_metrics
            )

            # Calculate throughput
            check_duration_ms = int((time.time() - start_time) * 1000)

            # Build result
            result = {
                'timestamp': now.isoformat(),
                'overall_status': overall_status,
                'cognitive_score': cognitive_score,
                'is_thinking': overall_status not in ['resting', 'offline'],
                'check_duration_ms': check_duration_ms,

                # LLM metrics
                'llm': llm_metrics,

                # Conversation metrics
                'conversations': conversation_metrics,

                # Agent metrics
                'agents': agent_metrics,

                # RAG metrics
                'rag': rag_metrics,

                # Routing metrics
                'routing': routing_metrics,

                # Provider breakdown
                'providers': llm_metrics.get('by_provider', {}),
                'models': llm_metrics.get('by_model', {}),

                # Issues
                'cognitive_issues': issues,

                # Integration status
                'integrations': {
                    'heart': self._check_heart_integration(),
                    'lungs': self._check_lungs_integration(),
                },
            }

            # Save pulse record
            self._save_pulse(result)

            # Cache result
            cache.set(self.CACHE_KEY_STATUS, result, self.CACHE_TTL)
            self._last_check = now

            return result

        except Exception as e:
            logger.error(f"Brain check failed: {e}", exc_info=True)
            return {
                'timestamp': timezone.now().isoformat(),
                'overall_status': 'offline',
                'cognitive_score': 0,
                'is_thinking': False,
                'error': str(e),
            }

    def is_thinking(self) -> bool:
        """Quick check - is the brain actively processing?"""
        try:
            vitals = self.get_vitals()
            return vitals.get('is_thinking', False)
        except Exception as _e:
            logger.warning(
                "brain.is_thinking: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def get_vitals(self) -> Dict[str, Any]:
        """Get current brain vitals (cached)."""
        cached = cache.get(self.CACHE_KEY_VITALS)
        if cached:
            return cached

        # Run fresh check
        result = self.think(force=False)

        vitals = {
            'status': result.get('overall_status', 'unknown'),
            'cognitive_score': result.get('cognitive_score', 0),
            'is_thinking': result.get('is_thinking', False),
            'llm_calls_24h': result.get('llm', {}).get('calls_24h', 0),
            'llm_success_rate': result.get('llm', {}).get('success_rate', 100),
            'active_conversations': result.get('conversations', {}).get('active', 0),
            'agent_executions_24h': result.get('agents', {}).get('executions_24h', 0),
            'tokens_24h': result.get('llm', {}).get('tokens_total_24h', 0),
            'timestamp': result.get('timestamp'),
        }

        cache.set(self.CACHE_KEY_VITALS, vitals, self.CACHE_TTL)
        return vitals

    def get_history(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get brain pulse history (returns empty if table doesn't exist)."""
        try:
            from core.models_brain import BrainPulse
            from django.db.utils import ProgrammingError, OperationalError

            since = timezone.now() - timedelta(hours=hours)
            pulses = BrainPulse.objects.filter(
                recorded_at__gte=since
            ).order_by('-recorded_at')[:limit]

            return [
                {
                    'id': str(p.id),
                    'timestamp': p.recorded_at.isoformat(),
                    'status': p.overall_status,
                    'cognitive_score': p.cognitive_score,
                    'is_thinking': p.is_thinking,
                    'llm_calls_24h': p.llm_calls_24h,
                    'llm_success_rate': p.llm_success_rate,
                    'tokens_total_24h': p.tokens_total_24h,
                    'active_conversations': p.active_conversations,
                    'emoji': p.get_status_emoji(),
                }
                for p in pulses
            ]
        except (ProgrammingError, OperationalError):
            # Table doesn't exist - return empty history
            return []
        except Exception as e:
            # Also catch by error message for psycopg2 exceptions
            error_str = str(e).lower()
            if 'does not exist' in error_str or 'relation' in error_str:
                return []
            logger.error(f"Failed to get brain history: {e}")
            return []

    def _collect_llm_metrics(self, since: timezone.datetime) -> Dict[str, Any]:
        """Collect LLM call metrics."""
        try:
            from core.models_llm_routing import LLMCallLog

            # Get all calls in window
            calls = LLMCallLog.objects.filter(created_at__gte=since)

            # Aggregate metrics
            total_calls = calls.count()
            successful_calls = calls.filter(success=True).count()
            failed_calls = total_calls - successful_calls

            # Token and latency aggregates
            aggregates = calls.aggregate(
                total_tokens=Coalesce(Sum('total_tokens'), 0),
                prompt_tokens=Coalesce(Sum('prompt_tokens'), 0),
                completion_tokens=Coalesce(Sum('completion_tokens'), 0),
                avg_latency=Coalesce(Avg('latency_ms'), 0.0, output_field=FloatField()),
                total_cost=Coalesce(Sum('cost'), 0, output_field=DecimalField()),
            )

            # By provider
            by_provider = {}
            provider_stats = calls.values('provider').annotate(
                count=Count('id'),
                successes=Count('id', filter=Q(success=True)),
                tokens=Coalesce(Sum('total_tokens'), 0),
                avg_latency=Coalesce(Avg('latency_ms'), 0.0),
            )
            for ps in provider_stats:
                by_provider[ps['provider']] = {
                    'calls': ps['count'],
                    'success_rate': (ps['successes'] / ps['count'] * 100) if ps['count'] > 0 else 100,
                    'tokens': ps['tokens'],
                    'avg_latency_ms': round(ps['avg_latency'], 2),
                }

            # By model
            by_model = {}
            model_stats = calls.values('model_id').annotate(
                count=Count('id'),
                successes=Count('id', filter=Q(success=True)),
                tokens=Coalesce(Sum('total_tokens'), 0),
                avg_latency=Coalesce(Avg('latency_ms'), 0.0),
            )
            for ms in model_stats:
                by_model[ms['model_id']] = {
                    'calls': ms['count'],
                    'success_rate': (ms['successes'] / ms['count'] * 100) if ms['count'] > 0 else 100,
                    'tokens': ms['tokens'],
                    'avg_latency_ms': round(ms['avg_latency'], 2),
                }

            # Timeout count (latency > 30s)
            timeouts = calls.filter(latency_ms__gt=30000).count()

            # Fallback count
            fallbacks = calls.filter(was_fallback=True).count()

            return {
                'calls_24h': total_calls,
                'successful_24h': successful_calls,
                'failed_24h': failed_calls,
                'success_rate': (successful_calls / total_calls * 100) if total_calls > 0 else 100,
                'tokens_total_24h': aggregates['total_tokens'],
                'tokens_input_24h': aggregates['prompt_tokens'],
                'tokens_output_24h': aggregates['completion_tokens'],
                'avg_latency_ms': round(aggregates['avg_latency'], 2),
                'total_cost_24h': float(aggregates['total_cost']),
                'timeouts_24h': timeouts,
                'fallbacks_24h': fallbacks,
                'by_provider': by_provider,
                'by_model': by_model,
            }

        except Exception as e:
            logger.error(f"Failed to collect LLM metrics: {e}")
            return {
                'calls_24h': 0,
                'success_rate': 100,
                'tokens_total_24h': 0,
                'avg_latency_ms': 0,
                'by_provider': {},
                'by_model': {},
            }

    def _collect_conversation_metrics(self, since: timezone.datetime) -> Dict[str, Any]:
        """Collect PA conversation metrics."""
        try:
            from core.models_unified_system import ConversationMessage

            # Recent conversations (approximated by messages)
            recent_messages = ConversationMessage.objects.filter(
                created_at__gte=since
            )

            total_messages = recent_messages.count()

            # Get distinct conversations
            distinct_convos = recent_messages.values('conversation_id').distinct().count()

            # Active conversations (messages in last hour)
            one_hour_ago = timezone.now() - timedelta(hours=1)
            active_convos = ConversationMessage.objects.filter(
                created_at__gte=one_hour_ago
            ).values('conversation_id').distinct().count()

            # Average turns per conversation
            avg_turns = total_messages / distinct_convos if distinct_convos > 0 else 0

            return {
                'active': active_convos,
                'total_24h': distinct_convos,
                'messages_24h': total_messages,
                'avg_turns': round(avg_turns, 1),
                'success_rate': 100.0,  # Assume success unless we track failures
            }

        except Exception as e:
            logger.error(f"Failed to collect conversation metrics: {e}")
            return {
                'active': 0,
                'total_24h': 0,
                'messages_24h': 0,
                'avg_turns': 0,
                'success_rate': 100,
            }

    def _collect_agent_metrics(self, since: timezone.datetime) -> Dict[str, Any]:
        """Collect agent execution metrics."""
        try:
            from core.models_unified_system import AgentExecution

            # Get executions in window
            executions = AgentExecution.objects.filter(created_at__gte=since)

            total = executions.count()
            completed = executions.filter(status='completed').count()
            failed = executions.filter(status='failed').count()
            running = executions.filter(status='running').count()

            # Aggregates
            aggregates = executions.aggregate(
                total_tokens=Coalesce(Sum('tokens_used'), 0),
                avg_time=Coalesce(Avg('execution_time_ms'), 0.0),
            )

            # Tool calls (from metadata if tracked)
            tool_calls = 0
            tool_successes = 0
            # This would need a separate tracking mechanism

            return {
                'executions_24h': total,
                'completed_24h': completed,
                'failed_24h': failed,
                'running': running,
                'success_rate': (completed / total * 100) if total > 0 else 100,
                'tokens_used_24h': aggregates['total_tokens'],
                'avg_execution_time_ms': round(aggregates['avg_time'], 2),
                'tool_calls_24h': tool_calls,
                'tool_success_rate': 100.0,
            }

        except Exception as e:
            logger.error(f"Failed to collect agent metrics: {e}")
            return {
                'executions_24h': 0,
                'completed_24h': 0,
                'failed_24h': 0,
                'running': 0,
                'success_rate': 100,
            }

    def _collect_rag_metrics(self, since: timezone.datetime) -> Dict[str, Any]:
        """Collect RAG/embedding query metrics."""
        # This would need a RAG query log model to track properly
        # For now, return placeholder metrics
        return {
            'queries_24h': 0,
            'avg_latency_ms': 0,
            'hit_rate': 0,
            'embedding_lookups_24h': 0,
        }

    def _collect_routing_metrics(self, since: timezone.datetime) -> Dict[str, Any]:
        """Collect model routing decision metrics."""
        try:
            from core.models_llm_routing import LLMCallLog

            calls = LLMCallLog.objects.filter(created_at__gte=since)
            total = calls.count()
            fallbacks = calls.filter(was_fallback=True).count()
            auto_selected = calls.filter(was_auto_selected=True).count()

            return {
                'decisions_24h': total,
                'fallback_count_24h': fallbacks,
                'fallback_rate': (fallbacks / total * 100) if total > 0 else 0,
                'auto_selected_24h': auto_selected,
                'primary_model_rate': 100 - ((fallbacks / total * 100) if total > 0 else 0),
            }

        except Exception as e:
            logger.error(f"Failed to collect routing metrics: {e}")
            return {
                'decisions_24h': 0,
                'fallback_count_24h': 0,
                'fallback_rate': 0,
            }

    def _calculate_cognitive_score(
        self,
        llm_metrics: Dict,
        conversation_metrics: Dict,
        agent_metrics: Dict
    ) -> float:
        """Calculate overall cognitive score (0-100)."""
        score = 100.0

        # LLM success rate impact (40% weight)
        llm_success = llm_metrics.get('success_rate', 100)
        if llm_success < 90:
            score -= (90 - llm_success) * 0.8  # -0.8 per % below 90

        # Latency impact (20% weight)
        avg_latency = llm_metrics.get('avg_latency_ms', 0)
        if avg_latency > 5000:  # Over 5 seconds
            latency_penalty = min((avg_latency - 5000) / 1000, 20)
            score -= latency_penalty

        # Agent success rate impact (20% weight)
        agent_success = agent_metrics.get('success_rate', 100)
        if agent_success < 90:
            score -= (90 - agent_success) * 0.4

        # Timeout/error impact (20% weight)
        timeouts = llm_metrics.get('timeouts_24h', 0)
        if timeouts > 0:
            score -= min(timeouts * 2, 20)  # -2 per timeout, max -20

        return max(0, min(100, score))

    def _determine_status(
        self,
        score: float,
        llm_metrics: Dict,
        agent_metrics: Dict
    ) -> str:
        """Determine brain status based on score and metrics."""
        # Check for offline (no activity)
        if llm_metrics.get('calls_24h', 0) == 0 and agent_metrics.get('executions_24h', 0) == 0:
            return 'resting'

        # Check for active thinking
        if agent_metrics.get('running', 0) > 0:
            if score >= self.THINKING_THRESHOLD:
                return 'thinking'

        # Score-based status
        if score >= self.FOCUSED_THRESHOLD:
            return 'focused'
        elif score >= self.THINKING_THRESHOLD:
            return 'thinking'
        elif score >= self.OVERLOADED_THRESHOLD:
            return 'overloaded'
        elif score >= self.FOGGY_THRESHOLD:
            return 'foggy'
        else:
            return 'offline'

    def _detect_issues(
        self,
        llm_metrics: Dict,
        conversation_metrics: Dict,
        agent_metrics: Dict
    ) -> List[Dict]:
        """Detect cognitive issues/problems."""
        issues = []

        # High error rate
        llm_success = llm_metrics.get('success_rate', 100)
        if llm_success < 95:
            issues.append({
                'type': 'high_error_rate',
                'severity': 'warning' if llm_success >= 80 else 'critical',
                'message': f"LLM success rate at {llm_success:.1f}%",
                'metric': llm_success,
            })

        # High latency
        avg_latency = llm_metrics.get('avg_latency_ms', 0)
        if avg_latency > 10000:
            issues.append({
                'type': 'high_latency',
                'severity': 'warning' if avg_latency < 20000 else 'critical',
                'message': f"Average response time {avg_latency/1000:.1f}s",
                'metric': avg_latency,
            })

        # Many timeouts
        timeouts = llm_metrics.get('timeouts_24h', 0)
        if timeouts > 5:
            issues.append({
                'type': 'frequent_timeouts',
                'severity': 'warning' if timeouts < 20 else 'critical',
                'message': f"{timeouts} timeouts in 24h",
                'metric': timeouts,
            })

        # High fallback rate
        fallbacks = llm_metrics.get('fallbacks_24h', 0)
        calls = llm_metrics.get('calls_24h', 1)
        fallback_rate = (fallbacks / calls * 100) if calls > 0 else 0
        if fallback_rate > 10:
            issues.append({
                'type': 'high_fallback_rate',
                'severity': 'warning',
                'message': f"{fallback_rate:.1f}% of calls using fallback models",
                'metric': fallback_rate,
            })

        # Agent failures
        agent_success = agent_metrics.get('success_rate', 100)
        if agent_success < 90:
            issues.append({
                'type': 'agent_failures',
                'severity': 'warning' if agent_success >= 70 else 'critical',
                'message': f"Agent success rate at {agent_success:.1f}%",
                'metric': agent_success,
            })

        return issues

    def _check_heart_integration(self) -> str:
        """Check integration with HEART system."""
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            return 'connected' if heart.is_alive() else 'degraded'
        except Exception:
            return 'disconnected'

    def _check_lungs_integration(self) -> str:
        """Check integration with LUNGS system."""
        try:
            from core.services.lungs import get_lungs_service
            lungs = get_lungs_service()
            return 'connected' if lungs.is_breathing() else 'degraded'
        except Exception:
            return 'disconnected'

    def _save_pulse(self, result: Dict) -> None:
        """Save brain pulse record to database (optional - fails silently if table missing)."""
        try:
            from core.models_brain import BrainPulse
            from django.db.utils import ProgrammingError, OperationalError

            pulse = BrainPulse.objects.create(
                overall_status=result.get('overall_status', 'unknown'),
                cognitive_score=result.get('cognitive_score', 0),
                is_thinking=result.get('is_thinking', False),

                # LLM metrics
                llm_calls_24h=result.get('llm', {}).get('calls_24h', 0),
                llm_success_rate=result.get('llm', {}).get('success_rate', 100),
                llm_avg_latency_ms=result.get('llm', {}).get('avg_latency_ms', 0),
                llm_errors_24h=result.get('llm', {}).get('failed_24h', 0),
                llm_timeouts_24h=result.get('llm', {}).get('timeouts_24h', 0),

                # Token metrics
                tokens_input_24h=result.get('llm', {}).get('tokens_input_24h', 0),
                tokens_output_24h=result.get('llm', {}).get('tokens_output_24h', 0),
                tokens_total_24h=result.get('llm', {}).get('tokens_total_24h', 0),

                # Conversation metrics
                active_conversations=result.get('conversations', {}).get('active', 0),
                conversations_24h=result.get('conversations', {}).get('total_24h', 0),
                avg_conversation_turns=result.get('conversations', {}).get('avg_turns', 0),

                # Agent metrics
                agent_thoughts_24h=result.get('agents', {}).get('executions_24h', 0),

                # Routing metrics
                routing_decisions_24h=result.get('routing', {}).get('decisions_24h', 0),
                fallback_count_24h=result.get('routing', {}).get('fallback_count_24h', 0),

                # Provider breakdown
                provider_stats=result.get('providers', {}),
                model_stats=result.get('models', {}),

                # Issues
                cognitive_issues=result.get('cognitive_issues', []),

                # Integration
                heart_connected=result.get('integrations', {}).get('heart') == 'connected',
                lungs_connected=result.get('integrations', {}).get('lungs') == 'connected',

                # Check metadata
                check_duration_ms=result.get('check_duration_ms', 0),
            )

            self._last_pulse_id = pulse.id

        except (ProgrammingError, OperationalError) as e:
            # Table doesn't exist - this is expected if migrations haven't run
            # Log once at debug level to avoid log spam
            if not getattr(self, '_pulse_table_warning_logged', False):
                logger.debug(f"BrainPulse table not available (skipping pulse save): {e}")
                self._pulse_table_warning_logged = True
        except Exception as e:
            # Also catch by error message for psycopg2 exceptions
            error_str = str(e).lower()
            if 'does not exist' in error_str or 'relation' in error_str:
                if not getattr(self, '_pulse_table_warning_logged', False):
                    logger.debug(f"BrainPulse table not available (skipping pulse save): {e}")
                    self._pulse_table_warning_logged = True
            else:
                logger.error(f"Failed to save brain pulse: {e}")
