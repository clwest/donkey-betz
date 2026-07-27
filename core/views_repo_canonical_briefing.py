"""
Canonical Briefing endpoint — S2985.

Endpoint:
- POST /api/repo/canonical-briefing/  — LLM briefing (cards + citations)
  for a canonical summary doc, scope-filtered to the arc folder by default.

Reuses the S2984 PR3 hardening pattern (DRF @api_view + IsAuthenticated +
Path.resolve() containment check against BASE_DIR) so 401/403 surface as
JSON, not the 302 HTML redirect that django-native @login_required emits.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes as drf_permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse

from core.services.canonical_briefing import (
    BriefingError,
    build_briefing,
)

logger = logging.getLogger(__name__)


DOCS_PREFIX = "docs/"
DEFAULT_MAX_CHUNKS_PER_SECTION = 12
DEFAULT_MAX_BULLETS_PER_SECTION = 10
HARD_MAX_CHUNKS_PER_SECTION = 30
HARD_MAX_BULLETS_PER_SECTION = 25


def _validate_docs_path(raw: str, kind: str) -> tuple[str | None, DRFResponse | None]:
    """Return (normalized_path, None) on success or (None, error_response).

    kind is used in error messages (e.g. "anchor_path", "scope.root").
    """
    if not raw:
        return None, DRFResponse({"error": f"Missing {kind}"}, status=400)
    if raw != "docs" and not raw.startswith(DOCS_PREFIX):
        return None, DRFResponse(
            {"error": f"Invalid {kind} - must be within docs/ directory"},
            status=403,
        )
    if ".." in raw:
        return None, DRFResponse(
            {"error": f"Invalid {kind} - directory traversal not allowed"},
            status=403,
        )
    base = Path(settings.BASE_DIR).resolve()
    candidate = (base / raw).resolve() if (base / raw).exists() else base / raw
    try:
        candidate.relative_to(base)
    except ValueError:
        return None, DRFResponse(
            {"error": f"Invalid {kind} - resolves outside repository"},
            status=403,
        )
    return raw, None


@api_view(["POST"])
@drf_permission_classes([IsAuthenticated])
def canonical_briefing_view(request):
    """POST /api/repo/canonical-briefing/

    Request body::

        {
          "anchor_path": "docs/research/domains/<slug>/....md",
          "scope": {"root": "docs/research/domains/<slug>"},  # optional; defaults to dirname(anchor_path)
          "max_chunks_per_section": 12,
          "max_bullets_per_section": 10,
          "force_refresh": false,
          "model": "gpt-5-mini"
        }

    Response shape mirrors the spec (sections[].bullets[].citations[]),
    plus a `cache` block and `retrieval` counts for debugging.
    """
    try:
        body: Dict[str, Any] = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return DRFResponse({"error": "Invalid JSON body"}, status=400)

    anchor_path = str(body.get("anchor_path") or "").strip()
    anchor_path, err = _validate_docs_path(anchor_path, "anchor_path")
    if err is not None:
        return err
    assert anchor_path is not None  # for type-checker; err path already returned

    scope_block = body.get("scope") or {}
    scope_root_raw = str(scope_block.get("root") or "").strip()
    if not scope_root_raw:
        scope_root_raw = str(Path(anchor_path).parent).replace("\\", "/")
    scope_root, err = _validate_docs_path(scope_root_raw, "scope.root")
    if err is not None:
        return err
    assert scope_root is not None

    max_chunks = int(body.get("max_chunks_per_section") or DEFAULT_MAX_CHUNKS_PER_SECTION)
    max_bullets = int(body.get("max_bullets_per_section") or DEFAULT_MAX_BULLETS_PER_SECTION)
    if max_chunks < 1 or max_chunks > HARD_MAX_CHUNKS_PER_SECTION:
        return DRFResponse(
            {"error": f"max_chunks_per_section must be between 1 and {HARD_MAX_CHUNKS_PER_SECTION}"},
            status=400,
        )
    if max_bullets < 1 or max_bullets > HARD_MAX_BULLETS_PER_SECTION:
        return DRFResponse(
            {"error": f"max_bullets_per_section must be between 1 and {HARD_MAX_BULLETS_PER_SECTION}"},
            status=400,
        )

    force_refresh = bool(body.get("force_refresh") or False)
    model_override = body.get("model")

    try:
        payload = build_briefing(
            anchor_path=anchor_path,
            scope_root=scope_root,
            max_chunks_per_section=max_chunks,
            max_bullets_per_section=max_bullets,
            model=model_override,
            force_refresh=force_refresh,
        )
    except BriefingError as exc:
        return DRFResponse({"error": str(exc)}, status=404)
    except Exception:  # noqa: BLE001 - surface a JSON 500, not a 302
        logger.exception("canonical_briefing failed for %s", anchor_path)
        return DRFResponse({"error": "Briefing generation failed"}, status=500)

    return DRFResponse(payload)
