"""
Relevant Knowledge Service — CDR-002 Gap 3 (P3, Option 1)
=========================================================

Shared retrieval surface for "relevant knowledge for a task" used by
BOTH ``BaseAgent`` (agent-side, per-execution) and
``UnifiedPAEntrypoint._build_context`` (PA-side, per-turn). Closes the
PA/BaseAgent asymmetry named as Gap 3 in CDR-002 §7 by extracting the
body of ``BaseAgent._get_relevant_knowledge_for_task`` (Session 400)
into a service both surfaces consume.

Retrieval sequence (unchanged from S400 semantics, three phases):

1. **Spider semantic search** (Session 452 re-enabled with
   pre-generated embeddings) — top-3 results via
   ``spider_semantic_search.semantic_search_with_db_embeddings``.
2. **AgentKnowledgeSource keyword match** — DB keyword-in-title/summary
   filter, ordered by ``-confidence_score, -freshness_score,
   -last_updated_at``. Fills remaining budget after phase 1.
3. **SharedKnowledge** (Session 1085) — cross-agent shared knowledge
   with ``effectiveness_score >= 0.5``, keyword match. Fills remaining
   budget after phase 2. Increments ``applied_count`` on rows consumed.

Return shape (stable across callers) — ``List[Dict[str, Any]]``:

    [
        {
            'source_agent': str,        # producer identity
            'title': str,               # capped at 60 chars
            'summary': str,              # capped at 200-300 chars
            'knowledge_type': str,       # 'spider_data' | knowledge_type field
            'confidence': float,         # 0.0-1.0
            'spider_sources': List[str], # producer spider IDs
        },
        ...
    ]

Discipline notes:

- Narrow-except allowlist matches the S1234 D17-D21 discipline
  (``DatabaseError``, ``ConnectionError``, ``OSError``) — env errors
  log-and-skip; logic errors propagate fail-loud. This is a
  P3-scoped tightening of the BaseAgent original which used broad
  ``except Exception``.
- Sync method — callers must wrap with ``asyncio.to_thread`` when
  invoked from async code (PA turn does this at ``_build_context``).
- Read-only — the only DB write is ``SharedKnowledge.applied_count``
  bump on consumed rows, per S1085 telemetry contract.

Governance:

- CDR-002 §7 Gap 3 authoritative scope. Chris ratified P3 + Option 1
  on 2026-07-09.
- Acceptance test AT-11 at ``test_pa_knowledge_retrieval_capability.py``.
- Reference: BaseAgent hook was at ``core/agents/base_agent.py:1435``
  (delegates here after P3).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)

# Narrow-except allowlist — same shape as S1234 D17-D21 and the
# CDR-002 P2 `_CONTEXT_INJECTION_ENV_ERRORS` module allowlist.
_KNOWLEDGE_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)


def get_relevant_knowledge_for_task(task: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve relevant knowledge for a task/message.

    Shared substrate for BaseAgent + UnifiedPAEntrypoint. See module
    docstring for full contract.

    Args:
        task: The task or PA-turn message text.
        limit: Maximum knowledge items to return across all three
            phases combined. Default 5.

    Returns:
        List of knowledge dicts (see module docstring for shape).
        Empty list if no matches or all phases fail with env errors.
        Logic errors (AttributeError, TypeError, KeyError) propagate.
    """
    results: List[Dict[str, Any]] = []

    # Phase 1 — Spider semantic search (Session 452 re-enabled).
    try:
        from core.services.spider_semantic_search import get_spider_semantic_search
        search = get_spider_semantic_search()
        semantic_results = search.semantic_search_with_db_embeddings(task, limit=3)

        for sr in semantic_results:
            results.append({
                'source_agent': 'SpiderNetwork',
                'title': (sr.title or 'Spider Intelligence')[:60],
                'summary': (sr.description or '')[:200],
                'knowledge_type': 'spider_data',
                'confidence': sr.similarity,
                'spider_sources': [sr.source] if sr.source else [],
            })
    except _KNOWLEDGE_ENV_ERRORS as e:
        logger.debug(f"[relevant_knowledge] Phase 1 spider semantic env error ({type(e).__name__}): {e}")
    except ImportError as e:
        # Spider semantic module may be optionally absent in some deployments.
        logger.debug(f"[relevant_knowledge] Phase 1 spider semantic unavailable: {e}")

    # CDR-002 §19 P3.1 (Rigby SIGN O6): empty-keyword guard. If no
    # length-4+ keywords could be extracted from the task, Phase 2 and
    # Phase 3 fall back to unbounded "top rows by score" — global
    # AgentKnowledgeSource + SharedKnowledge sweeps that aren't
    # semantically related to the task. In addition, the S1085
    # applied_count bump would silently inflate on generic tasks. Skip
    # both phases when no keywords are available so `relevant` actually
    # means relevant.
    task_lower = task.lower()
    task_keywords = [w for w in task_lower.split() if len(w) > 3]

    # Phase 2 — AgentKnowledgeSource keyword match.
    if task_keywords:
        try:
            from core.models_unified_system import AgentKnowledgeSource
            from django.db.models import Q

            keywords = task_keywords[:5]
            keyword_q = Q()
            for kw in keywords:
                keyword_q |= Q(title__icontains=kw)
                keyword_q |= Q(summary__icontains=kw)
            query = Q(is_active=True) & keyword_q

            remaining = limit - len(results)
            if remaining > 0:
                knowledge_items = AgentKnowledgeSource.objects.filter(query).order_by(
                    '-confidence_score',
                    '-freshness_score',
                    '-last_updated_at',
                )[:remaining]
                for ks in knowledge_items:
                    results.append({
                        'source_agent': ks.agent.name if ks.agent else 'Unknown',
                        'title': (ks.title or '')[:60],
                        'summary': (ks.summary or '')[:300],
                        'knowledge_type': ks.knowledge_type,
                        'confidence': ks.confidence_score,
                        'spider_sources': ks.source_spider_names or [],
                    })
        except _KNOWLEDGE_ENV_ERRORS as e:
            logger.warning(f"[relevant_knowledge] Phase 2 AgentKnowledgeSource env error ({type(e).__name__}): {e}")

    # Phase 3 — SharedKnowledge (S1085) with applied_count increment.
    # Same empty-keyword guard as Phase 2: no keywords → no bump, no
    # generic sweep. Prevents applied_count inflation on generic tasks.
    if task_keywords:
        try:
            from core.models_unified_system import SharedKnowledge
            from django.db.models import F, Q

            remaining = limit - len(results)
            if remaining > 0:
                sk_keywords = task_keywords[:3]
                kw_q = Q()
                for kw in sk_keywords:
                    kw_q |= Q(title__icontains=kw) | Q(description__icontains=kw)
                sk_query = SharedKnowledge.objects.filter(
                    effectiveness_score__gte=0.5,
                ).filter(kw_q)

                for sk in sk_query.order_by('-effectiveness_score')[:remaining]:
                    results.append({
                        'source_agent': sk.source_agent,
                        'title': (sk.title or '')[:60],
                        'summary': (sk.description or '')[:300],
                        'knowledge_type': sk.knowledge_type,
                        'confidence': sk.effectiveness_score,
                        'spider_sources': [],
                    })
                    # S1085 telemetry contract — bump applied_count on consumed rows.
                    # Only fires when the row actually matched a task keyword.
                    SharedKnowledge.objects.filter(id=sk.id).update(
                        applied_count=F('applied_count') + 1,
                    )
        except _KNOWLEDGE_ENV_ERRORS as e:
            logger.debug(f"[relevant_knowledge] Phase 3 SharedKnowledge env error ({type(e).__name__}): {e}")

    if results:
        logger.debug(f"[relevant_knowledge] Found {len(results)} items for task (limit={limit})")

    return results[:limit]
