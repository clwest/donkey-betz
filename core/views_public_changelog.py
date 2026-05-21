"""
Public-read changelog endpoint for marketing surfaces (247globalai.com).

Surfaces recently-published Deliverables — the "what we shipped" view of
the Initiative pipeline. Companion to /api/public/intelligence/now/ — same
token, same caller, parallel architecture.

Strict filter contract (defense in depth):
- publish_intent IN {publish_candidate, publish_required} — never INTERNAL_ONLY
- status = 'published' — never draft / ready / archived
- created_at within last 30 days
- Hand-shaped JSON: no workspace_id, no initiative_id, no user_id, no full content
"""
from datetime import timedelta
from typing import Optional

from django.utils import timezone
from rest_framework import status, throttling
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models_deliverables import Deliverable, DeliverableType, PublishIntent
from core.views_public_intelligence import PublicIntelTokenAuth


# Reuse the same env-var token via the existing auth class. Define a
# separate throttle scope so changelog traffic doesn't share the intel
# rate limit (one wire being saturated shouldn't starve the other).
class PublicChangelogThrottle(throttling.SimpleRateThrottle):
    """30 reqs/min per source IP — same rate as intel, separate bucket."""
    scope = 'public_changelog'
    rate = '30/min'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


DELIVERABLE_TYPE_LABELS = dict(DeliverableType.choices)


def _content_excerpt(content: Optional[str], max_chars: int = 220) -> str:
    """Strip markdown noise and truncate to a one-line summary.

    Public-facing — we deliberately don't leak the full deliverable body.
    """
    if not content:
        return ""
    # Strip markdown headers, bullet glyphs, link wrappers, code fences.
    cleaned = content.strip()
    for prefix in ("# ", "## ", "### ", "#### ", "##### ", "- ", "* ", "> "):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    # Code fence opener: drop the first line if it's just ``` markup.
    if cleaned.startswith("```"):
        nl = cleaned.find("\n")
        if nl > -1:
            cleaned = cleaned[nl + 1:]
    # Collapse whitespace, take first ~max_chars.
    cleaned = " ".join(cleaned.split())
    if len(cleaned) <= max_chars:
        return cleaned
    # Truncate on word boundary
    truncated = cleaned[:max_chars].rsplit(" ", 1)[0]
    return truncated + "…"


def _public_deliverable_dict(deliv: Deliverable) -> dict:
    """Hand-shape the JSON. Never serialize workspace/initiative/user IDs.

    Intentionally drops: workspace, initiative, dream, user, source_operation,
    trace_id, parent_object_*, content_hash, slug, content_format, agent_task,
    raw content (only an excerpt makes the wire).
    """
    return {
        'id': str(deliv.id),
        'title': deliv.title,
        'deliverable_type': deliv.deliverable_type,
        'type_label': DELIVERABLE_TYPE_LABELS.get(
            deliv.deliverable_type, deliv.deliverable_type
        ),
        'category': deliv.category or "",
        # Tags: cap to 6, truncate to 40 chars each — defense in depth
        'tags': [t[:40] for t in (deliv.tags or [])[:6]],
        'excerpt': _content_excerpt(deliv.content),
        'published_at': deliv.updated_at.isoformat() if deliv.updated_at else None,
        'created_at': deliv.created_at.isoformat() if deliv.created_at else None,
    }


class PublicChangelogRecentView(APIView):
    """
    GET /api/public/changelog/recent/

    Returns up to 20 recently-published Deliverables from the last 30 days,
    filtered to publishable intents only. Token-gated via X-Intel-Token
    header (same token as /api/public/intelligence/now/).
    """

    permission_classes = [AllowAny]
    authentication_classes = [PublicIntelTokenAuth]
    throttle_classes = [PublicChangelogThrottle]

    def get(self, request):
        window_start = timezone.now() - timedelta(days=30)
        publishable = [
            PublishIntent.PUBLISH_CANDIDATE,
            PublishIntent.PUBLISH_REQUIRED,
        ]

        qs = (
            Deliverable.objects
            .filter(
                status='published',
                publish_intent__in=publishable,
                created_at__gte=window_start,
            )
            .order_by('-updated_at', '-created_at')
        )
        top = list(qs[:20])

        total_30d = qs.count()
        # Type counts for the editorial stats strip
        type_counts: dict[str, int] = {}
        for deliv in qs:
            type_counts[deliv.deliverable_type] = type_counts.get(deliv.deliverable_type, 0) + 1
        top_types = sorted(type_counts.items(), key=lambda kv: -kv[1])[:3]

        payload = {
            'as_of': timezone.now().isoformat(),
            'window_days': 30,
            'stats': {
                'total_published_30d': total_30d,
                'top_types': [
                    {
                        'type': type_key,
                        'label': DELIVERABLE_TYPE_LABELS.get(type_key, type_key),
                        'count': count,
                    }
                    for type_key, count in top_types
                ],
            },
            'deliverables': [_public_deliverable_dict(d) for d in top],
        }
        return Response(payload, status=status.HTTP_200_OK)
