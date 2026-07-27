"""
Repo Research Arcs API — Session 2984 / PR3 spec `be68f1d1-1c88-4d72-a908-e57f6ce310dc`.

Endpoint:
- GET /api/repo/research/arcs/  — auto-discovered research arcs from
  `docs/research/domains/` with status buckets + entrypoints per spec §3.

Cached in Django's default cache with a 30s TTL to soften the git-log fanout.
The cache key does not vary by user (arcs are repo-scoped, not per-user), so
concurrent requests share the same warmed payload.
"""

from __future__ import annotations

import logging
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.services.research_arcs_scanner import scan_research_arcs

logger = logging.getLogger(__name__)


RESEARCH_ARCS_ROOT = Path(settings.BASE_DIR) / "docs" / "research" / "domains"
CACHE_KEY = "repo:research:arcs:v1"
CACHE_TTL_SECONDS = 30


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def research_arcs(request):
    """
    Return auto-discovered research arcs (spec §3 Response JSON).

    Cached 30s. Failure returns a 200 with `arcs: []` + a logged warning so
    the Home tab renders empty rather than error.
    """
    payload = cache.get(CACHE_KEY)
    if payload is None:
        try:
            payload = scan_research_arcs(RESEARCH_ARCS_ROOT)
        except Exception:
            logger.warning("research_arcs scan failed", exc_info=True)
            return Response(
                {
                    "generated_at": None,
                    "root": str(RESEARCH_ARCS_ROOT),
                    "active_days": 14,
                    "stale_days": 60,
                    "arcs": [],
                    "error": "scan_failed",
                }
            )
        cache.set(CACHE_KEY, payload, CACHE_TTL_SECONDS)
    return Response(payload)
