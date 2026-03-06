"""
Session 1077: Noise metrics for cockpit — measures North Star coverage
and conversation topic clustering.

Pure aggregation functions, no LLM calls. Designed for <200ms response.
"""

import logging
from collections import Counter
from datetime import timedelta
from typing import Any

from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── North Star classification ─────────────────────────────────────────────

# Agent names whose output is inherently on a North Star path
_REVENUE_AGENTS = frozenset({
    'OpportunityPipelineAgent', 'CustomerResearchAgent',
    'MarketingAgent', 'BusinessContentAgent',
    'ContentDistributionAgent',
})

_CONTENT_AGENTS = frozenset({
    'ContentWriterAgent', 'EditorAgent', 'SEOOptimizerAgent',
    'ContentStrategyAgent', 'BrandStrategyAgent',
    'NarrativeDriftCoordinator', 'PodcastAgent',
    'TechnicalDocumentAgent', 'CreativeDirectorAgent',
})

_SPORTS_AGENTS = frozenset({
    'GamePredictor', 'SportsOddsAnalyst', 'ArbitrageDetector',
    'SportsIntelligenceCoordinator',
})

# Next-action types that signal North Star paths
_REVENUE_ACTIONS = frozenset({
    'outreach_draft', 'close_pack', 'meeting_brief',
    'opportunity_update', 'lead_qualify',
})

_CONTENT_ACTIONS = frozenset({
    'review_deliverable', 'approve_content', 'preview_media',
})

# Task keywords for fallback classification
_REVENUE_KEYWORDS = frozenset({
    'outreach', 'revenue', 'lead', 'client', 'sales', 'pitch',
    'proposal', 'invoice', 'close',
})

_CONTENT_KEYWORDS = frozenset({
    'blog', 'publish', 'article', 'content', 'editorial',
    'podcast', 'deliverable', 'draft', 'write',
})

_SPORTS_KEYWORDS = frozenset({
    'prediction', 'odds', 'wager', 'bet', 'spread',
    'arbitrage', 'sports', 'game', 'pick',
})


def classify_north_star(agent_name: str, enrichment: dict, task: str) -> str:
    """Classify a run into a North Star path: revenue, content, sports, or none."""
    # 1) Agent-based classification (strongest signal)
    if agent_name in _REVENUE_AGENTS:
        return 'revenue'
    if agent_name in _CONTENT_AGENTS:
        return 'content'
    if agent_name in _SPORTS_AGENTS:
        return 'sports'

    # 2) Artifact-based classification
    artifacts = enrichment.get('artifacts', {})
    if artifacts.get('wagers'):
        return 'sports'
    if artifacts.get('blogs') or artifacts.get('deliverables'):
        return 'content'

    # 3) Next-action type
    next_action_type = enrichment.get('next_action', {}).get('type', '')
    if next_action_type in _REVENUE_ACTIONS:
        return 'revenue'
    if next_action_type in _CONTENT_ACTIONS:
        return 'content'

    # 4) Task keyword fallback
    task_lower = (task or '').lower()
    for kw in _REVENUE_KEYWORDS:
        if kw in task_lower:
            return 'revenue'
    for kw in _SPORTS_KEYWORDS:
        if kw in task_lower:
            return 'sports'
    for kw in _CONTENT_KEYWORDS:
        if kw in task_lower:
            return 'content'

    return 'none'


# ── Runs metrics ──────────────────────────────────────────────────────────

def compute_runs_metrics(hours: int = 24) -> dict:
    """Aggregate run metrics with North Star coverage.

    Returns dict matching the schema from Rigby's context packet.
    Designed for <200ms — uses DB aggregation where possible,
    enrichment only on the result set.
    """
    from core.models_unified_system import AgentExecution
    from core.services.run_enrichment import enrich_run

    cutoff = timezone.now() - timedelta(hours=hours)
    qs = AgentExecution.objects.filter(created_at__gte=cutoff).select_related('agent')

    total = qs.count()

    # By-agent counts (DB aggregation — fast)
    by_agent = list(
        qs.values('agent__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:20]
    )
    by_agent = [{'agent_name': r['agent__name'] or 'unknown', 'count': r['count']} for r in by_agent]

    # We need enrichment for trigger/importance/north_star — but we don't need
    # to enrich ALL runs. Sample up to 500 for distribution stats.
    sample_limit = min(total, 500)
    records = list(qs.order_by('-created_at')[:sample_limit])

    trigger_counts: Counter = Counter()
    importance_counts: Counter = Counter()
    next_action_counts: Counter = Counter()
    artifact_type_counts: Counter = Counter()
    north_star_counts: Counter = Counter()

    for rec in records:
        run_dict = {
            'id': str(rec.id),
            'agent_name': rec.agent.name if rec.agent_id else '',
            'task': (rec.task or '')[:200],
            'status': rec.status,
        }
        enrich_run(run_dict, full_record=rec)
        enrichment = run_dict.get('enrichment', {})

        trigger_counts[enrichment.get('trigger', {}).get('type', 'unknown')] += 1
        importance_counts[enrichment.get('importance', {}).get('level', 'routine')] += 1
        next_action_counts[enrichment.get('next_action', {}).get('type', 'no_action')] += 1

        # Artifact type counts
        for art_type, items in enrichment.get('artifacts', {}).items():
            if items:
                artifact_type_counts[art_type] += len(items)

        # North Star classification
        ns = classify_north_star(
            run_dict['agent_name'],
            enrichment,
            rec.task or '',
        )
        north_star_counts[ns] += 1

    # Scale percentages to full population if we sampled
    sampled = len(records)
    ns_result = {}
    for path in ('revenue', 'content', 'sports', 'none'):
        count = north_star_counts.get(path, 0)
        pct = round(count / sampled * 100, 1) if sampled else 0
        # Extrapolate count to full population
        scaled_count = round(count / sampled * total) if sampled else 0
        ns_result[path] = {'count': scaled_count, 'pct': pct}

    return {
        'window_hours': hours,
        'total_runs': total,
        'sampled': sampled,
        'by_agent': by_agent,
        'by_trigger_type': [{'trigger_type': k, 'count': v} for k, v in trigger_counts.most_common()],
        'by_importance_level': [{'level': k, 'count': v} for k, v in importance_counts.most_common()],
        'by_next_action_type': [{'type': k, 'count': v} for k, v in next_action_counts.most_common()],
        'by_artifact_type': [{'type': k, 'count': v} for k, v in artifact_type_counts.most_common()],
        'north_star_coverage': ns_result,
    }


# ── Conversation metrics ──────────────────────────────────────────────────

# Simple keyword buckets for topic clustering v1
_TOPIC_BUCKETS = [
    ('competitor comparison', ['competitor', 'compare', 'vs ', 'versus', 'alternative']),
    ('content strategy', ['content strategy', 'editorial', 'publishing cadence', 'content plan']),
    ('market analysis', ['market', 'industry', 'sector', 'valuation']),
    ('sports betting', ['betting', 'prediction', 'odds', 'wager', 'spread', 'sports']),
    ('revenue/growth', ['revenue', 'growth', 'monetize', 'income', 'sales', 'lead']),
    ('technical', ['code', 'deploy', 'infrastructure', 'api', 'database', 'bug']),
    ('brand/marketing', ['brand', 'marketing', 'social media', 'seo', 'campaign']),
    ('legal', ['legal', 'court', 'custody', 'parenting', 'motion']),
    ('blockchain/crypto', ['blockchain', 'crypto', 'defi', 'web3', 'nft']),
    ('stock/finance', ['stock', 'ticker', 'sec', 'earnings', 'dividend', 'portfolio']),
    ('system health', ['health', 'heartbeat', 'diagnostic', 'failure', 'error']),
    ('ideation', ['brainstorm', 'idea', 'dream', 'explore', 'imagine', 'what if']),
]


def _bucket_topic(topic: str) -> str:
    """Classify a conversation topic into a bucket via keyword match."""
    topic_lower = (topic or '').lower()
    for bucket_name, keywords in _TOPIC_BUCKETS:
        for kw in keywords:
            if kw in topic_lower:
                return bucket_name
    return 'other'


def compute_conversation_metrics(hours: int = 24) -> dict:
    """Aggregate conversation metrics with topic clustering and zombie detection."""
    from core.models_unified_system import AgentConversation

    cutoff = timezone.now() - timedelta(hours=hours)
    qs = AgentConversation.objects.filter(started_at__gte=cutoff)

    total = qs.count()

    # By-agent (initiator)
    by_agent_raw = list(
        qs.values('initiator__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:15]
    )
    by_agent = [{'agent_name': r['initiator__name'] or 'unknown', 'count': r['count']} for r in by_agent_raw]

    # Topic clustering
    topics = list(qs.values_list('topic', flat=True)[:500])
    topic_buckets: Counter = Counter()
    for t in topics:
        topic_buckets[_bucket_topic(t)] += 1
    top_topics = [{'topic': k, 'count': v} for k, v in topic_buckets.most_common(10)]

    # Zombie detection: conversations still 'active' with 0-1 messages
    # or no conclusion after >2 hours
    two_hours_ago = timezone.now() - timedelta(hours=2)
    zombie_qs = qs.filter(
        Q(status='active', message_count__lte=1) |
        Q(status='active', started_at__lt=two_hours_ago, conclusion='')
    )
    zombie_count = zombie_qs.count()

    # By conversation type
    by_type_raw = list(
        qs.values('conversation_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    by_type = [{'conversation_type': r['conversation_type'], 'count': r['count']} for r in by_type_raw]

    return {
        'window_hours': hours,
        'total_conversations': total,
        'by_agent': by_agent,
        'by_type': by_type,
        'top_topics': top_topics,
        'zombie_rate': {
            'zombies': zombie_count,
            'total': total,
            'pct': round(zombie_count / total * 100, 1) if total else 0,
        },
    }
