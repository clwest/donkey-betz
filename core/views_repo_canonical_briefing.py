"""
Canonical Briefing endpoints.

Endpoints:
- POST /api/repo/canonical-briefing/  — LLM briefing (cards + citations)
  for a canonical summary doc, scope-filtered to the arc folder by default.
  (S2985)
- POST /api/repo/canonical-briefing/send-to-rigby/  — creates a
  ``briefing_action_item`` Deliverable in the Donkey Betz workspace from
  one briefing bullet + its retrieved citations, so Claude can pick the
  work up next session via the workspace UI. (S2988)

Reuses the S2984 PR3 hardening pattern (DRF @api_view + IsAuthenticated +
Path.resolve() containment check against BASE_DIR) so 401/403 surface as
JSON, not the 302 HTML redirect that django-native @login_required emits.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes as drf_permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse

from core.services.canonical_briefing import (
    BriefingError,
    build_briefing,
)

# S2988: canonical Donkey Betz workspace UUID for briefing action items.
# Confirmed via `docs/research/implementation/RATIFICATION_2026-07-19_*.md`
# + `tests/test_smoke_dispatch.py:141`. If this ever moves, update here.
DONKEY_BETZ_WORKSPACE_ID = "b4503364-2573-4401-9e28-61a739e0ce50"
BRIEFING_ACTION_ITEM_TYPE = "briefing_action_item"
BRIEFING_ACTION_ITEM_CATEGORY = "research_followup"
BRIEFING_ACTION_ITEM_TITLE_MAX = 100

logger = logging.getLogger(__name__)


DOCS_PREFIX = "docs/"
DEFAULT_MAX_CHUNKS_PER_SECTION = 12
DEFAULT_MAX_BULLETS_PER_SECTION = 6
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


def _compose_action_item_body(
    anchor_path: str,
    section_key: str,
    section_title: str,
    bullet_text: str,
    citations: List[Dict[str, Any]],
) -> str:
    """Render a markdown body for the briefing_action_item Deliverable.

    Kept small and greppable — Chris reads these in the workspace UI and
    Claude picks them up next session via `deliverable_tool.list`.
    """
    lines: List[str] = [
        f"**Action** (from {section_title}): {bullet_text}",
        "",
        f"**Source canonical summary:** `{anchor_path}`",
        f"**Section:** `{section_key}` ({section_title})",
        "",
        "**Retrieved citations:**",
    ]
    if not citations:
        lines.append("- (none — bullet lacked citation coverage in the source briefing)")
    for c in citations:
        path = c.get("path") or "?"
        snippet = (c.get("snippet") or "").replace("\n", " ").strip()
        if len(snippet) > 200:
            snippet = snippet[:199] + "\u2026"
        lines.append(f"- `{path}` — {snippet}")
    return "\n".join(lines)


def _derive_title(bullet_text: str) -> str:
    """First N chars of the bullet, trimmed at a word boundary, prefix-tagged."""
    trimmed = (bullet_text or "").strip()
    if len(trimmed) > BRIEFING_ACTION_ITEM_TITLE_MAX:
        cut = trimmed[:BRIEFING_ACTION_ITEM_TITLE_MAX].rsplit(" ", 1)[0].rstrip(",.;:")
        trimmed = cut + "\u2026"
    return f"Briefing action: {trimmed}" if trimmed else "Briefing action: (empty)"


@api_view(["POST"])
@drf_permission_classes([IsAuthenticated])
def canonical_briefing_send_to_rigby_view(request):
    """POST /api/repo/canonical-briefing/send-to-rigby/

    Creates a ``briefing_action_item`` Deliverable in the Donkey Betz
    workspace from one briefing bullet + its retrieved citations. Uses the
    same ``deliverable_factory.create_deliverable`` path Rigby's
    ``deliverable_tool.create`` uses, so downstream (workspace UI,
    ``deliverable_tool.list``) sees an identically-shaped row.

    Request body::

        {
          "anchor_path": "docs/research/domains/pa/2699_pa_canonical_summary.md",
          "section_key": "next_actions",
          "section_title": "Next Actions",
          "bullet_text": "Open S2601 Cat A endpoint contract SoT design-prep as the first child workstream.",
          "citations": [
            {"document_id": "…", "chunk_id": "…", "path": "docs/…", "snippet": "…"},
            …
          ]
        }

    Response::

        {
          "deliverable_id": "<uuid>",
          "workspace_id": "b4503364-…",
          "title": "Briefing action: Open S2601 Cat A endpoint…",
          "deliverable_type": "briefing_action_item"
        }
    """
    try:
        body: Dict[str, Any] = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return DRFResponse({"error": "Invalid JSON body"}, status=400)

    anchor_path = str(body.get("anchor_path") or "").strip()
    anchor_path, err = _validate_docs_path(anchor_path, "anchor_path")
    if err is not None:
        return err
    assert anchor_path is not None

    bullet_text = str(body.get("bullet_text") or "").strip()
    if not bullet_text:
        return DRFResponse({"error": "Missing bullet_text"}, status=400)
    if len(bullet_text) > 2000:
        return DRFResponse({"error": "bullet_text exceeds 2000 chars"}, status=400)

    section_key = str(body.get("section_key") or "").strip() or "unknown"
    section_title = str(body.get("section_title") or "").strip() or section_key

    raw_citations = body.get("citations") or []
    if not isinstance(raw_citations, list):
        return DRFResponse({"error": "citations must be a list"}, status=400)
    citations: List[Dict[str, Any]] = [c for c in raw_citations if isinstance(c, dict)]

    title = _derive_title(bullet_text)
    content = _compose_action_item_body(
        anchor_path=anchor_path,
        section_key=section_key,
        section_title=section_title,
        bullet_text=bullet_text,
        citations=citations,
    )

    try:
        from core.services.deliverable_factory import (
            create_deliverable,
            DeliverableGatedError,
        )
        from core.models_skin_layer import ProjectWorkspace
    except ImportError:
        logger.exception("send_to_rigby: import failed")
        return DRFResponse({"error": "Deliverable subsystem unavailable"}, status=500)

    try:
        workspace = ProjectWorkspace.objects.get(id=DONKEY_BETZ_WORKSPACE_ID)
    except ProjectWorkspace.DoesNotExist:
        logger.error(
            "send_to_rigby: Donkey Betz workspace %s not found",
            DONKEY_BETZ_WORKSPACE_ID,
        )
        return DRFResponse(
            {"error": "Target workspace missing — contact operator"},
            status=500,
        )

    try:
        deliverable = create_deliverable(
            title=title,
            content=content,
            agent_name="canonical_briefing_send_to_rigby",
            category=BRIEFING_ACTION_ITEM_CATEGORY,
            deliverable_type=BRIEFING_ACTION_ITEM_TYPE,
            user=request.user if request.user.is_authenticated else None,
            workspace_id=str(workspace.id),
            workspace=workspace,
            tags=["briefing-action", "canonical-summary", section_key],
            content_format="markdown",
            metadata={
                "source": "canonical_briefing_send_to_rigby",
                "trigger_source": "pa_tool",  # bypass factory gate 3
                "anchor_path": anchor_path,
                "section_key": section_key,
                "section_title": section_title,
                "citation_count": len(citations),
            },
            preserve_title=True,
            raise_on_gated=True,
            status="ready",
        )
    except DeliverableGatedError as exc:
        logger.warning("send_to_rigby: gated (%s: %s)", exc.reason_code, exc.reason)
        return DRFResponse(
            {
                "error": "Deliverable was rejected by the quality gate",
                "reason_code": exc.reason_code,
                "reason": exc.reason,
            },
            status=422,
        )
    except Exception:  # noqa: BLE001 - JSON 500 not 302
        logger.exception(
            "send_to_rigby failed for anchor=%s section=%s",
            anchor_path,
            section_key,
        )
        return DRFResponse({"error": "Failed to create deliverable"}, status=500)

    if deliverable is None:
        return DRFResponse({"error": "Deliverable factory returned no row"}, status=500)

    return DRFResponse(
        {
            "deliverable_id": str(deliverable.id),
            "workspace_id": str(workspace.id),
            "title": deliverable.title,
            "deliverable_type": deliverable.deliverable_type,
        },
        status=201,
    )
