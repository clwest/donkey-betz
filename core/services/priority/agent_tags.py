"""
Session 1086 PR 2: Hardcoded agent → tag overrides for priority matching.

Per Rigby's Q3 answer during the Session 1086 design review, this dict is
**code-reviewed, not DB-editable** for the MVP. The goal is to get real
usage signal before investing in governance UX for tag editing. Once the
tag taxonomy stabilizes and Rigby wants to edit these live, we can
migrate to an ``AgentTag`` model and a PA tool action.

## How matching uses this dict

``core.services.priority.priority_router.PriorityRouter._derive_agent_tags``
consumes this dict alongside two other tag sources:

1. The agent's own ``agent_name`` (always included, lowercased)
2. ``Agent.category`` from ``core.models_unified_system`` (if present)
3. **This dict** — used as the primary manual override layer

When an :class:`ActivePriority` row's ``tags`` list overlaps with the
derived tag set for a given agent, the router returns a MATCH decision
with ``matched_via='tags'``.

## How to add an entry

Keep the keys aligned to ``AGENT_MAP`` keys in ``core/agent_router.py``
(i.e. the real class names used at dispatch time, not display names).
Tag values should be short, lowercase, and stable — prefer domain
language over implementation details. Good tags are things like
``content``, ``ops``, ``video``, ``legal``. Avoid ``gpt5`` / ``langchain``
/ ``beta`` — those describe how the agent works, not what it's for.

## Current taxonomy (v1 — keep narrow, add when needed)

The tags below cluster agents into ~6 rough families so that a priority
tagged ``platform`` will pick up ops-focused agents, ``content`` will
pick up creative agents, etc. This is intentionally conservative —
we'd rather miss matches (fail-open) than create false positives.
"""

from typing import Dict, List

AGENT_TAG_OVERRIDES: Dict[str, List[str]] = {
    # ── Content / Creative family ───────────────────────────────────────
    "ContentWriterAgent": ["content", "writing", "creative"],
    "BlogAgent": ["content", "writing", "creative"],
    "ImageAgent": ["image", "creative", "content"],
    "VideoAgent": ["video", "creative", "content"],
    "AudioAgent": ["audio", "creative", "content"],
    "ResolveAgent": ["video", "editing", "creative"],
    "PodcastAgent": ["audio", "content", "creative"],
    "SocialMediaAgent": ["content", "distribution", "creative"],

    # ── Ops / Platform / Orchestration family ──────────────────────────
    "WorkflowOrchestrationAgent": ["ops", "orchestration", "platform"],
    "CodeGeneratorAgent": ["code", "platform", "engineering"],
    "SystemIntelligenceAgent": ["ops", "platform", "observability"],
    "DiagnosticAgent": ["ops", "platform", "observability"],
    "DeploymentAgent": ["ops", "platform", "deployment"],

    # ── Research / Analysis family ─────────────────────────────────────
    "CustomerResearchAgent": ["research", "analysis"],
    "CompetitorAnalysisAgent": ["research", "analysis", "strategy"],
    "MarketAnalystAgent": ["research", "analysis", "finance"],
    "WhaleWatcherAgent": ["research", "crypto", "finance"],

    # ── Strategy / Planning family ─────────────────────────────────────
    "BrandStrategyAgent": ["strategy", "content"],
    "ContentStrategyAgent": ["strategy", "content"],
    "MarketingStrategyAgent": ["strategy", "content", "growth"],
    "StrategicReviewAgent": ["strategy", "governance"],

    # ── Legal / Compliance family ──────────────────────────────────────
    "LegalDocDrafterAgent": ["legal", "writing", "compliance"],

    # ── Revenue / Income family ────────────────────────────────────────
    "AIIncomeBuilder": ["income", "revenue", "jobs"],
    "RealJobExecutor": ["income", "jobs"],
    "RealContentCreatorAgent": ["content", "income"],
}
