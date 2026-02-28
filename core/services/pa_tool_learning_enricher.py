"""
PA Tool Learning Enricher
=========================

Enrichment service that injects approved PAToolInsight records into
the PA system prompt, so the PA learns from past tool-call patterns.

Registered in INTENT_ENRICHMENT_MAP under 'tool_learning' and also
appended directly to the function-calling system prompt.
"""

import logging

from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class PAToolLearningEnricher:
    """Injects approved tool insights into the PA prompt."""

    def enrich(self, context: dict) -> str:
        from core.models_tool_calls import PAToolInsight

        now = timezone.now()
        insights = (
            PAToolInsight.objects
            .filter(safety_class='approved')
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .exclude(insight_type='consistency_check')
            .order_by('-confidence', '-evidence_count')[:20]
        )

        if not insights:
            return ""

        sections: dict[str, list[str]] = {}
        for insight in insights:
            sections.setdefault(insight.tool_name, []).append(
                insight.prompt_snippet
            )

        lines = ["## Tool Usage Insights (learned from past interactions)"]
        for tool, snippets in sections.items():
            lines.append(f"\n### {tool}")
            for s in snippets:
                lines.append(f"- {s}")

        return "\n".join(lines)
