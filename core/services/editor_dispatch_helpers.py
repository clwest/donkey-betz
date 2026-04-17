"""Editor dispatch helpers — Session 1092 / Session 1093.

Shared caller-side fallback for EditorAgent dispatches. EditorAgent's job
is to EDIT existing content; it correctly fails when callers don't pass
`content` or `blog_id` in context. The fix lives at the dispatch layer:
when an LLM-generated next_step asks Editor to "synthesize the briefs"
without attaching them, gather the relevant workspace deliverables here
and inject them into context before the agent ever sees the call.

Used by:
- ``ToolDispatcher._handle_agent_tool`` (PA tool dispatch path,
  Session 1090 — kept that copy as a thin wrapper for back-compat).
- ``ConversationActionDispatcher._dispatch_to_agent`` (next_step
  dispatch path, Session 1092 — was missing this fallback and produced
  9 "No content provided" failures in a 24h CTOAgent platform audit).

Session 1093 (canary v8 finding): the v1 gather merged 6 most-recent
deliverables into one chimera blob. EditorAgent correctly failed loud
("Draft is a pasted bundle"). v2 returns a structured `sources` list with
relevance-scored selection (1 primary by default, max 3 additional) and
keeps `content` set to the primary source only as a transitional
fallback. See conversation pa-3966231ba0d140e7 for the spec.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)

# Agents whose output is "source material" — we prefer these over
# operational/diagnostic outputs when picking primary source for an editor.
SOURCE_AGENT_NAMES = {
    'ResearchAgent',
    'CompetitorAnalysisAgent',
    'OpportunityScoringAgent',
    'TrendAnalysisAgent',
    'MarketIntelligenceAgent',
    'MarketIntelligenceCoordinator',
    'ContentStrategyAgent',
    'ContentWriterAgent',
    'StockAnalystAgent',
    'BrandStrategyAgent',
}


def _extract_keywords(task_text: str) -> List[str]:
    """Extract candidate match tokens from the task text. Used to score
    whether a deliverable's title is "on-topic" for the requested task.
    Strips common stopwords + instruction-meta words.
    """
    if not task_text:
        return []
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'of', 'for', 'in', 'on',
        'at', 'to', 'with', 'into', 'as', 'is', 'are', 'was', 'were',
        'edit', 'tighten', 'rewrite', 'review', 'analyze', 'analyse',
        'summarize', 'summarise', 'create', 'produce', 'write', 'draft',
        'memo', 'brief', 'document', 'preserve', 'identify', 'into',
        'this', 'that', 'these', 'those', 'be', 'will', 'would', 'should',
        'must', 'may', 'can', 'could', 'their', 'there', 'they', 'them',
        'top', 'two', 'three', 'four', 'five', 'six', 'word', 'words',
        'publish', 'ready', 'clearer', 'structure', 'action', 'items',
        'citations', 'blockers',
    }
    tokens = re.findall(r'\b[a-z][a-z0-9_-]{2,}\b', task_text.lower())
    keywords = []
    for t in tokens:
        if t in STOPWORDS or t.isdigit():
            continue
        if len(t) < 3:
            continue
        if t not in keywords:
            keywords.append(t)
    return keywords[:15]  # cap to avoid quadratic title scoring


def _score_deliverable(d, task_keywords: List[str], now) -> tuple:
    """Return (score, reason) for a deliverable candidate.

    Components:
        recency:    100 (within 60 min) | 50 (24h) | 10 (older)
        tag/topic:  +50 if any task keyword appears in title (case-insensitive)
        source:     +30 if agent_name is in SOURCE_AGENT_NAMES
        canary:     +25 if "canary" appears in title (debug bonus — keeps
                    canary tests deterministic when other deliverables exist)
    """
    age_min = max(0, (now - d.created_at).total_seconds() / 60.0) if d.created_at else 1e9
    if age_min <= 60:
        recency = 100
        recency_label = '<60min'
    elif age_min <= 60 * 24:
        recency = 50
        recency_label = '<24h'
    else:
        recency = 10
        recency_label = '>24h'

    title_lower = (d.title or '').lower()
    matched = [k for k in task_keywords if k in title_lower]
    tag_bonus = 50 if matched else 0

    source_bonus = 30 if d.agent_name in SOURCE_AGENT_NAMES else 0

    canary_bonus = 25 if 'canary' in title_lower else 0

    score = recency + tag_bonus + source_bonus + canary_bonus
    parts = [recency_label]
    if matched:
        parts.append(f'kw={",".join(matched[:3])}')
    if source_bonus:
        parts.append(f'src={d.agent_name}')
    if canary_bonus:
        parts.append('canary')
    return score, '+'.join(parts)


def gather_workspace_content_for_editor(
    workspace_id: Optional[str],
    task_text: str,
    *,
    max_sources: int = 4,
    section_char_cap: int = 6000,
    recency_minutes: int = 60,
    additional_score_threshold: int = 100,
) -> Optional[Dict[str, Any]]:
    """Gather relevance-scored workspace deliverables for an editor agent.

    Selection strategy (Session 1093 v2):
        1. Filter to workspace, exclude EditorAgent's own prior outputs
           and ContentWriter blog posts (avoid feedback loops).
        2. Restrict to deliverables created within `recency_minutes`
           (default 60 min) — older items are noise for "edit my recent
           work" requests.
        3. Score each by recency + task-keyword/title overlap +
           source-agent preference + canary bonus.
        4. Always include a primary source (top scorer).
        5. Include additional sources only if they score >=
           `additional_score_threshold`. Cap total at `max_sources`.

    Returns:
        Structured dict with both v2 keys and v1 transitional keys:
        {
            # v2 (preferred — agents that handle multi-source)
            'sources': [{id, title, agent_name, created_at, score,
                         score_reason, excerpt, content}],
            'primary_source': {...},            # alias for sources[0]
            'gather_explanation': str,           # one-line "why these"
            'task_hint': str | None,             # only set when len(sources) > 1

            # v1 transitional (back-compat for callers that read .content
            # or .sections directly — these now hold PRIMARY ONLY, not the
            # chimera. Per Session 1093 canary v8 finding.)
            'content': str,                      # primary source content
            'title': str,                        # primary source title
            'intro': str,
            'sections': [{heading, content}],    # primary only
            'conclusion': '',
        }
        Or None if no usable deliverables.
    """
    try:
        from core.models_deliverables import Deliverable
        from core.models_skin_layer import ProjectWorkspace
        from django.utils import timezone
        from datetime import timedelta

        target_ws = workspace_id

        # Prefer the single active non-system workspace when caller's
        # workspace points at System Autonomous (which is empty by design).
        try:
            active_ws = (
                ProjectWorkspace.objects
                .filter(is_active=True)
                .exclude(name__icontains='autonomous')
                .exclude(name__icontains='system')
                .first()
            )
            if active_ws:
                candidate = str(active_ws.id)
                if candidate != workspace_id:
                    logger.info(
                        "[editor-gather] Preferring active workspace %s (%s) over %s",
                        active_ws.name, candidate, workspace_id,
                    )
                target_ws = candidate
        except Exception:
            pass

        if not target_ws:
            return None

        now = timezone.now()
        recency_cutoff = now - timedelta(minutes=recency_minutes)

        # Filter + recency window. We also fetch a small wider pool
        # (<= 24h) so logging can explain "we considered X, picked Y".
        qs = (
            Deliverable.objects
            .filter(workspace_id=target_ws)
            .exclude(title__startswith='EditorAgent:')
            .exclude(title__startswith='blog_post:')
            .exclude(deliverable_type='blog_post')
            .order_by('-created_at')
        )
        recent_pool = list(qs.filter(created_at__gte=recency_cutoff)[:20])
        if not recent_pool:
            # Fallback: take the single newest deliverable even if outside
            # the recency window. Better than failing the dispatch entirely.
            fallback = qs.first()
            if not fallback or not (fallback.content or '').strip():
                return None
            recent_pool = [fallback]

        keywords = _extract_keywords(task_text)
        scored = []
        for d in recent_pool:
            body = (d.content or '').strip()
            if not body:
                continue
            score, reason = _score_deliverable(d, keywords, now)
            scored.append((score, reason, d))
        if not scored:
            return None

        scored.sort(key=lambda t: t[0], reverse=True)

        # Primary always = top scorer. Additionals only if they clear the
        # threshold (so we don't pull in unrelated noise).
        chosen = [scored[0]]
        for s in scored[1:]:
            if len(chosen) >= max_sources:
                break
            if s[0] >= additional_score_threshold:
                chosen.append(s)

        sources = []
        for score, reason, d in chosen:
            body = d.content or ''
            sources.append({
                'id': str(d.id),
                'title': d.title or 'Untitled',
                'agent_name': d.agent_name or 'Unknown',
                'created_at': d.created_at.isoformat() if d.created_at else None,
                'score': score,
                'score_reason': reason,
                'excerpt': body[:500],
                'content': body[:section_char_cap],
            })

        primary = sources[0]

        # Build the legacy v1 sections/content from primary only so
        # back-compat callers stop seeing the chimera.
        v1_sections = [{
            'heading': primary['title'],
            'content': primary['content'],
        }]

        gather_explanation = (
            f"Selected {len(sources)} of {len(scored)} candidates from "
            f"workspace {target_ws} (recency window {recency_minutes}min). "
            f"Primary: {primary['title'][:60]} (score {primary['score']}, "
            f"{primary['score_reason']})"
        )

        task_hint = None
        if len(sources) > 1:
            task_hint = (
                "You are receiving multiple independent source documents. "
                "Treat each as a discrete input — do NOT assume they are "
                "one synthesized brief. Use Source #1 as the primary "
                "input unless the task explicitly asks you to compare or "
                "synthesize across them."
            )

        logger.info(
            "[editor-gather] %s for task '%s'. Sources: %s",
            gather_explanation, (task_text or '')[:60],
            ', '.join(
                f"{s['title'][:40]} (s={s['score']}, {s['score_reason']})"
                for s in sources
            ),
        )

        return {
            # v2 structured shape
            'sources': sources,
            'primary_source': primary,
            'gather_explanation': gather_explanation,
            'task_hint': task_hint,
            # v1 transitional — primary only (NOT the chimera)
            'title': primary['title'],
            'intro': f"Primary source: {primary['title']}",
            'sections': v1_sections,
            'conclusion': '',
            'content': primary['content'],
        }
    except Exception as e:
        logger.warning("[editor-gather] Failed: %s", e, exc_info=True)
        return None
