"""
Session 2978: Theme Signals v1 UI endpoint — Phase A.

Thin HTTP wrapper over `core.services.theme_signals_service.get_theme_signals`.
Matches the auth + shape conventions of `core/views/signals_ui.py`.

Endpoint (session-authenticated):
  GET /api/theme-signals/?tab={buildable|investable}&days=7&limit=20
                        [&min_confidence=0.6]

Spec deliverable: `63ec4d1d-9425-468b-815c-b4e571e3fe44`.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.services.theme_signals_service import get_theme_signals

logger = logging.getLogger(__name__)


def _parse_int(raw: Any, default: Optional[int] = None) -> Optional[int]:
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _parse_float(raw: Any, default: Optional[float] = None) -> Optional[float]:
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def theme_signals(request: Request) -> Response:
    """Return tab-scoped Theme Signals cards for the Workspace UI."""
    tab_raw = (request.query_params.get("tab") or "buildable").strip().lower()
    tab = "investable" if tab_raw == "investable" else "buildable"
    days = _parse_int(request.query_params.get("days"), 7) or 7
    limit = _parse_int(request.query_params.get("limit"), 20) or 20
    min_confidence = _parse_float(request.query_params.get("min_confidence"), None)

    payload = get_theme_signals(
        tab=tab,
        days=days,
        limit=limit,
        min_confidence=min_confidence,
    )
    return Response(payload)
