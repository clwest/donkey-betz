"""
Public-read intelligence endpoint for marketing surfaces (247globalai.com).

Exposes a curated, anonymized slice of SignalCluster. Token-gated via a
shared secret (env: PUBLIC_INTEL_TOKEN) so it can be rotated without a
code change. NEVER exposes spider_data_ids, raw URLs, or sample_signals
— those can contain scraped excerpts and PII.

See docs/247_LIVE_INTELLIGENCE_PANEL_SKETCH.md for the architecture story.
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status, throttling
from rest_framework.authentication import BaseAuthentication, exceptions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models_signal_intelligence import SignalCluster


# Whitelist of pattern types safe to surface publicly. `knowledge_gap` etc.
# are intentionally excluded — they read as weakness signals to a stranger.
PUBLIC_PATTERN_TYPE_WHITELIST = (
    'demand_spike',
    'trend_emergence',
    'opportunity_window',
    'competitive_signal',
    'market_movement',
    'skill_demand',
    'sentiment_shift',
)


class PublicIntelTokenAuth(BaseAuthentication):
    """Header `X-Intel-Token` matched against settings.PUBLIC_INTEL_TOKEN.

    Defaults to off — if the env var is unset, every request is rejected.
    """

    def authenticate(self, request):
        expected = getattr(settings, 'PUBLIC_INTEL_TOKEN', '')
        if not expected:
            raise exceptions.AuthenticationFailed(
                'Endpoint disabled (no PUBLIC_INTEL_TOKEN configured)'
            )
        token = request.META.get('HTTP_X_INTEL_TOKEN', '')
        if token != expected:
            raise exceptions.AuthenticationFailed('Invalid intel token')
        # Token authorizes the route, not a user — return (None, None).
        return (None, None)


class PublicIntelThrottle(throttling.SimpleRateThrottle):
    """30 reqs/min per source IP. Generous because Next.js ISR collapses traffic."""

    scope = 'public_intel'
    rate = '30/min'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


PATTERN_LABEL_MAP = dict(SignalCluster.PATTERN_TYPE_CHOICES)


def _public_cluster_dict(cluster: SignalCluster) -> dict:
    """Hand-shape the JSON. Never serialize internal IDs or raw signal text."""
    return {
        'id': str(cluster.id),
        'name': cluster.name,
        'pattern_type': cluster.pattern_type,
        'pattern_label': PATTERN_LABEL_MAP.get(cluster.pattern_type, cluster.pattern_type),
        'strength': round(cluster.strength or 0.0, 2),
        'novelty': round(cluster.novelty or 0.0, 2),
        'confidence': round(cluster.confidence or 0.0, 2),
        'urgency': round(cluster.urgency or 0.0, 2),
        'detected_at': cluster.detected_at.isoformat() if cluster.detected_at else None,
        # source_breakdown is a count-only dict ({'reddit': 6, 'bluesky': 12}) —
        # safe to surface; no URLs/excerpts in there.
        'source_breakdown': cluster.source_breakdown or {},
        # Keywords: cap to 6, truncate to 40 chars each — defense in depth.
        'keywords': [k[:40] for k in (cluster.keywords or [])[:6]],
    }


class PublicIntelligenceNowView(APIView):
    """
    GET /api/public/intelligence/now/

    Returns up to 20 recent active SignalClusters from the last 24h plus
    aggregate counters. Token-gated via `X-Intel-Token` header. Cache
    lifetime is upstream — Next.js ISR enforces ~5 min between origin
    fetches regardless of visitor count.
    """

    permission_classes = [AllowAny]
    authentication_classes = [PublicIntelTokenAuth]
    throttle_classes = [PublicIntelThrottle]

    def get(self, request):
        window_start = timezone.now() - timedelta(hours=24)

        qs = (
            SignalCluster.objects
            .filter(
                status='active',
                detected_at__gte=window_start,
                pattern_type__in=PUBLIC_PATTERN_TYPE_WHITELIST,
            )
            .order_by('-strength', '-detected_at')
        )
        top = list(qs[:20])

        total_24h = qs.count()
        type_counts: dict[str, int] = {}
        for cluster in qs:
            type_counts[cluster.pattern_type] = type_counts.get(cluster.pattern_type, 0) + 1
        top_patterns = sorted(type_counts.items(), key=lambda kv: -kv[1])[:3]

        # Sources watched = total spider count. Lazy import keeps the
        # registry off the request hot path if it ever grows expensive.
        from ai_core.spiders.spider_registry import get_spider_registry
        sources_watched = len(get_spider_registry().list_spiders())

        payload = {
            'as_of': timezone.now().isoformat(),
            'window_hours': 24,
            'stats': {
                'total_signals_24h': total_24h,
                'top_patterns': [
                    {
                        'type': pattern_type,
                        'label': PATTERN_LABEL_MAP.get(pattern_type, pattern_type),
                        'count': count,
                    }
                    for pattern_type, count in top_patterns
                ],
                'sources_watched': sources_watched,
            },
            'clusters': [_public_cluster_dict(c) for c in top],
        }
        return Response(payload, status=status.HTTP_200_OK)
