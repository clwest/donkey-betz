"""
PlatformContextService — real, queryable, evidence-backed platform context.

Session 1089: Phase 1 of "Agent Data Grounding: Facts Not Fiction" initiative.
Initiative ID: 111b5af1-ea3d-4b6f-92b3-5f59c0591c67

Any agent that produces factual claims about the platform MUST call this
service and include evidence IDs in its output. This replaces hardcoded
tool stubs that returned the same static data regardless of input.

Design principles:
- Evidence-first: every method returns evidence[] with source pointers
- Time-windowed: callers specify hours_back (default 24)
- Composable: call individual methods or snapshot() for a full brief
- Fail-safe: each method catches its own exceptions and returns partial data
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.utils import timezone

logger = logging.getLogger(__name__)


def _evidence(source_system: str, source_tool: str, summary: str,
              data: Any = None, record_ids: Optional[List[str]] = None) -> Dict:
    """Build a standard evidence block."""
    now = timezone.now()
    return {
        'evidence_id': f'ev_{uuid.uuid4().hex[:12]}',
        'type': 'db_query',
        'source': {
            'system': source_system,
            'tool': source_tool,
            'record_ids': record_ids or [],
        },
        'captured_at_utc': now.isoformat(),
        'summary': summary,
        'data': data,
    }


def _envelope(facts: Dict, evidence: List[Dict], hours_back: int = 24,
              warnings: Optional[List[str]] = None) -> Dict:
    """Build a standard response envelope."""
    now = timezone.now()
    return {
        'request_id': f'pcx_{uuid.uuid4().hex[:12]}',
        'as_of_utc': now.isoformat(),
        'time_window': {'hours_back': hours_back},
        'facts': facts,
        'evidence': evidence,
        'warnings': warnings or [],
    }


class PlatformContextService:
    """
    Single source of truth for platform state. Agents call this instead
    of returning hardcoded analysis.
    """

    def snapshot(self, hours_back: int = 24, modules: Optional[List[str]] = None) -> Dict:
        """
        One-call CTO-style brief. Aggregates all modules into a single envelope.
        """
        available_modules = {
            'agent_exec': self.agent_execution_stats,
            'slo': self.slo_status,
            'governor': self.governor_status,
            'work': self.work_progress,
            'cost': self.cost_metrics,
            'spiders': self.spider_health,
            'content': self.content_pipeline_state,
            'failures': self.failure_signatures,
        }

        if modules is None:
            modules = list(available_modules.keys())

        all_facts = {}
        all_evidence = []
        warnings = []

        for mod in modules:
            if mod not in available_modules:
                warnings.append(f'Unknown module: {mod}')
                continue
            try:
                result = available_modules[mod](hours_back=hours_back)
                all_facts[mod] = result.get('facts', {})
                all_evidence.extend(result.get('evidence', []))
                warnings.extend(result.get('warnings', []))
            except Exception as e:
                logger.warning(f"[PlatformContext] Module {mod} failed: {e}")
                all_facts[mod] = {'error': str(e)}
                warnings.append(f'{mod}: {e}')

        return _envelope(all_facts, all_evidence, hours_back, warnings)

    def agent_execution_stats(self, hours_back: int = 24,
                               agent_names: Optional[List[str]] = None,
                               limit: int = 15) -> Dict:
        """Real agent execution stats from AgentExecution table."""
        try:
            from core.models_unified_system import AgentExecution
            from django.db.models import Count, Q

            cutoff = timezone.now() - timedelta(hours=hours_back)
            qs = AgentExecution.objects.filter(created_at__gte=cutoff)
            if agent_names:
                qs = qs.filter(agent__name__in=agent_names)

            total = qs.count()
            by_status = dict(
                qs.values_list('status')
                .annotate(c=Count('id'))
                .values_list('status', 'c')
            )
            completed = by_status.get('completed', 0)
            failed = by_status.get('failed', 0)
            success_rate = round(completed / total * 100, 1) if total > 0 else 0

            # Top agents by execution count
            top_agents = list(
                qs.values('agent__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:limit]
            )

            # Top failing agents
            top_failures = list(
                qs.filter(status='failed')
                .values('agent__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )

            facts = {
                'total_executions': total,
                'by_status': by_status,
                'success_rate_pct': success_rate,
                'top_agents': top_agents,
                'top_failures': top_failures,
            }

            evidence = [_evidence(
                'postgres', 'AgentExecution',
                f'{total} executions in {hours_back}h, {success_rate}% success rate',
                data={'total': total, 'success_rate': success_rate},
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] agent_execution_stats failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])

    def slo_status(self, hours_back: int = 24) -> Dict:
        """Real SLO status from the ops monitoring system."""
        try:
            from core.services.td_handlers_ops import OpsHandlersMixin

            class _Ops(OpsHandlersMixin):
                pass

            ops = _Ops()
            result = ops._handle_ops('ops_tool', {'action': 'slo_status'}, None, 'platform_context')

            slos = result.get('slos', [])
            breaches = [s for s in slos if s.get('breach')]

            facts = {
                'total_slos': len(slos),
                'breaches': len(breaches),
                'all_clear': len(breaches) == 0,
                'slos': slos,
                'breach_details': breaches,
            }

            evidence = [_evidence(
                'postgres', 'ops_tool.slo_status',
                f'{len(slos)} SLOs checked, {len(breaches)} breaches',
                data={'breach_keys': [b.get('key') for b in breaches]},
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] slo_status failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])

    def governor_status(self, **kwargs) -> Dict:
        """Real governor status — missions, budgets, circuit breakers."""
        try:
            from core.services.priority.governor import (
                get_governor_status, get_mission_telemetry, _governor_enabled
            )

            status = get_governor_status()
            telemetry = get_mission_telemetry()

            facts = {
                'governor_enabled': status.get('governor_enabled', False),
                'active_priorities': status.get('active_priorities', 0),
                'priority_names': status.get('priority_names', []),
                'disabled_missions': status.get('disabled_missions', []),
                'circuit_breakers_tripped': status.get('circuit_breakers_tripped', []),
                'telemetry': telemetry,
            }

            evidence = [_evidence(
                'redis', 'governor_tool.status',
                f'Governor {"enabled" if facts["governor_enabled"] else "disabled"}, '
                f'{facts["active_priorities"]} missions, '
                f'{len(facts["circuit_breakers_tripped"])} CBs tripped',
            )]

            return _envelope(facts, evidence)

        except Exception as e:
            logger.error(f"[PlatformContext] governor_status failed: {e}")
            return _envelope({'error': str(e)}, [], 0, [str(e)])

    def work_progress(self, hours_back: int = 24, limit: int = 20) -> Dict:
        """Real initiative and action item progress."""
        try:
            from core.models import Initiative, InitiativeActionItem
            from django.db.models import Count

            init_counts = dict(
                Initiative.objects.values_list('status')
                .annotate(c=Count('id'))
                .values_list('status', 'c')
            )
            total_initiatives = sum(init_counts.values())

            item_counts = dict(
                InitiativeActionItem.objects.values_list('status')
                .annotate(c=Count('id'))
                .values_list('status', 'c')
            )

            # Recently completed initiatives
            cutoff = timezone.now() - timedelta(hours=hours_back)
            recent_completed = list(
                Initiative.objects.filter(
                    status='COMPLETED',
                    updated_at__gte=cutoff
                ).values_list('name', flat=True)[:limit]
            )

            facts = {
                'initiatives': {
                    'total': total_initiatives,
                    'by_status': init_counts,
                },
                'action_items': {
                    'total': sum(item_counts.values()),
                    'by_status': item_counts,
                },
                'recently_completed': recent_completed,
            }

            evidence = [_evidence(
                'postgres', 'Initiative + InitiativeActionItem',
                f'{total_initiatives} initiatives, {sum(item_counts.values())} action items',
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] work_progress failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])

    def cost_metrics(self, hours_back: int = 24, limit: int = 15) -> Dict:
        """Real LLM cost data from LLMCallLog."""
        try:
            from core.models_llm_routing import LLMCallLog
            from django.db.models import Sum, Count

            cutoff = timezone.now() - timedelta(hours=hours_back)
            qs = LLMCallLog.objects.filter(created_at__gte=cutoff)

            totals = qs.aggregate(
                total_cost=Sum('cost'),
                total_calls=Count('id'),
                total_tokens=Sum('total_tokens'),
            )

            by_agent = list(
                qs.values('agent_name')
                .annotate(cost=Sum('cost'), calls=Count('id'), tokens=Sum('total_tokens'))
                .order_by('-cost')[:limit]
            )
            # Convert Decimal to float for JSON serialization
            for row in by_agent:
                row['cost'] = float(row['cost'] or 0)

            by_provider = list(
                qs.values('provider')
                .annotate(cost=Sum('cost'), calls=Count('id'))
                .order_by('-cost')
            )
            for row in by_provider:
                row['cost'] = float(row['cost'] or 0)

            facts = {
                'total_cost_usd': float(totals['total_cost'] or 0),
                'total_calls': totals['total_calls'],
                'total_tokens': totals['total_tokens'] or 0,
                'by_agent': by_agent,
                'by_provider': by_provider,
            }

            evidence = [_evidence(
                'postgres', 'LLMCallLog',
                f'${facts["total_cost_usd"]:.2f} across {facts["total_calls"]} calls in {hours_back}h',
                data={'total_cost': facts['total_cost_usd'], 'total_calls': facts['total_calls']},
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] cost_metrics failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])

    def spider_health(self, hours_back: int = 24, limit: int = 50) -> Dict:
        """Real spider network health from SpiderData."""
        try:
            from core.models_unified_system import SpiderData
            from django.db.models import Count, Max

            cutoff = timezone.now() - timedelta(hours=hours_back)

            # Spider activity
            spider_stats = list(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('spider_name')
                .annotate(
                    items=Count('id'),
                    last_run=Max('created_at'),
                )
                .order_by('-items')[:limit]
            )

            active = [s for s in spider_stats if s['items'] > 0]

            # Total spiders ever seen
            all_spiders = SpiderData.objects.values('spider_name').distinct().count()
            stale = all_spiders - len(active)

            facts = {
                'total_spiders_known': all_spiders,
                'active_in_window': len(active),
                'stale': stale,
                'top_active': spider_stats[:15],
            }

            evidence = [_evidence(
                'postgres', 'SpiderData',
                f'{len(active)} active spiders in {hours_back}h, {stale} stale',
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] spider_health failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])

    def content_pipeline_state(self, hours_back: int = 24) -> Dict:
        """Real content pipeline stats."""
        try:
            from core.models_deliverables import Deliverable
            from core.models_unified_system import SelfBlog
            from django.db.models import Count

            # Deliverables
            deliv_count = Deliverable.objects.count()
            recent_delivs = Deliverable.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=hours_back)
            ).count()

            # Blog stats
            blog_counts = dict(
                SelfBlog.objects.values_list('status')
                .annotate(c=Count('id'))
                .values_list('status', 'c')
            )
            total_blogs = sum(blog_counts.values())

            facts = {
                'deliverables_total': deliv_count,
                'deliverables_recent': recent_delivs,
                'blogs': {
                    'total': total_blogs,
                    'by_status': blog_counts,
                },
            }

            evidence = [_evidence(
                'postgres', 'Deliverable + SelfBlog',
                f'{deliv_count} deliverables, {total_blogs} blogs ({recent_delivs} new in {hours_back}h)',
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] content_pipeline_state failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])

    def failure_signatures(self, hours_back: int = 24, limit: int = 20) -> Dict:
        """Real failure patterns from agent executions and LLM calls."""
        try:
            from core.models_unified_system import AgentExecution
            from core.models_llm_routing import LLMCallLog
            from django.db.models import Count

            cutoff = timezone.now() - timedelta(hours=hours_back)

            # Agent failure patterns
            agent_fails = list(
                AgentExecution.objects.filter(
                    created_at__gte=cutoff, status='failed'
                ).values('agent__name', 'error_message')
                .annotate(count=Count('id'))
                .order_by('-count')[:limit]
            )

            # LLM failure patterns
            llm_fails = list(
                LLMCallLog.objects.filter(
                    created_at__gte=cutoff, success=False
                ).values('error_message', 'agent_name')
                .annotate(count=Count('id'))
                .order_by('-count')[:limit]
            )

            total_agent_fails = sum(f['count'] for f in agent_fails)
            total_llm_fails = sum(f['count'] for f in llm_fails)

            facts = {
                'agent_failures': {
                    'total': total_agent_fails,
                    'signatures': agent_fails,
                },
                'llm_failures': {
                    'total': total_llm_fails,
                    'signatures': llm_fails,
                },
            }

            evidence = [_evidence(
                'postgres', 'AgentExecution + LLMCallLog',
                f'{total_agent_fails} agent failures, {total_llm_fails} LLM failures in {hours_back}h',
            )]

            return _envelope(facts, evidence, hours_back)

        except Exception as e:
            logger.error(f"[PlatformContext] failure_signatures failed: {e}")
            return _envelope({'error': str(e)}, [], hours_back, [str(e)])
