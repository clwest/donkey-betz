"""Active-repo context loader for the PA system prompt.

Session 1119 v1 graduation — when `active_repo_tool` has cached a pointer
for the user, this loader assembles a compact context block (Repo
Profile metadata + latest Snapshot git state + open TRIAGE Initiatives)
and returns it as markdown so `_build_function_calling_system_prompt`
in `unified_pa_entrypoint.py` can inject it.

The block is intentionally narrow:
- Identifies the repo + root + branch
- Lists 2-3 hard constraints from the Repo Profile (machine-aware
  guardrails for Rigby's responses)
- Surfaces the top open TRIAGE initiatives, ranked by urgency × impact
- Tells Rigby where to read deeper detail (deliverable_tool with the
  right category filters) instead of stuffing full content in the
  prompt

No new models, no migrations, no new PA tools. Reads the existing
multi-repo state shipped in #2104 + #2107.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

ACTIVE_REPO_CACHE_KEY = "pa:active_repo:user:{user_id}"

REPO_PROFILE_CATEGORY = "repo_profile"
REPO_SNAPSHOT_CATEGORY = "repo_snapshot"
TRIAGE_STATUS = "TRIAGE"
MAX_CONSTRAINTS_INLINED = 3
MAX_INITIATIVES_INLINED = 7


def _fetch_active_repo_data(user_id):
    """Sync data fetch. Pushed to a thread when called from an async
    PA context (Django ORM rejects sync queries in async contexts)."""
    from django.core.cache import cache
    from core.models_skin_layer import ProjectWorkspace
    from core.models_deliverables import Deliverable
    from core.models_document_registry import Initiative

    pointer = cache.get(ACTIVE_REPO_CACHE_KEY.format(user_id=user_id))
    if not pointer:
        return None
    workspace_id = pointer.get("workspace_id")
    if not workspace_id:
        return None

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id)
    except ProjectWorkspace.DoesNotExist:
        cache.delete(ACTIVE_REPO_CACHE_KEY.format(user_id=user_id))
        return None

    profile = (
        Deliverable.objects.filter(
            workspace=workspace,
            category=REPO_PROFILE_CATEGORY,
            is_pinned=True,
        )
        .order_by("-created_at")
        .first()
    )
    snapshot = (
        Deliverable.objects.filter(
            workspace=workspace,
            category=REPO_SNAPSHOT_CATEGORY,
        )
        .order_by("-created_at")
        .first()
    )
    initiatives = list(
        Initiative.objects.filter(
            target_workspace=workspace,
            status=TRIAGE_STATUS,
        )
        .order_by("-urgency", "-impact_score")[:MAX_INITIATIVES_INLINED]
    )

    return {
        "workspace": {
            "id": str(workspace.id),
            "name": workspace.name,
            "root_path": workspace.root_path,
            "current_branch": workspace.current_branch,
        },
        "profile": {
            "id": str(profile.id) if profile else None,
            "metadata": dict(profile.metadata) if profile and isinstance(profile.metadata, dict) else {},
        } if profile else None,
        "snapshot": {
            "id": str(snapshot.id) if snapshot else None,
            "metadata": dict(snapshot.metadata) if snapshot and isinstance(snapshot.metadata, dict) else {},
        } if snapshot else None,
        "initiatives": [
            {
                "name": i.name,
                "urgency": i.urgency,
                "impact_score": i.impact_score,
            }
            for i in initiatives
        ],
    }


def load_active_repo_context_block(user_id) -> Optional[str]:
    """Return a markdown block describing the user's currently-active
    external repo, or `None` if no pointer is set.

    Always cheap (one Redis read + at most 4 indexed DB queries). Failures
    log at debug and return None so PA flow never breaks because of
    multi-repo state. Uses async_to_sync(sync_to_async(...)) so this can
    be called from sync code that's nested inside an async PA flow
    (Django's async-safety check rejects bare sync ORM in async contexts).
    """
    try:
        # Django's async-safety rejects sync ORM inside an async event
        # loop. asgiref's async_to_sync also chokes ("cannot use
        # AsyncToSync in the same thread as an async event loop"). The
        # robust escape hatch: punt the fetch to a fresh thread which
        # has no event loop attached.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_fetch_active_repo_data, user_id)
            data = future.result(timeout=5)
        if not data:
            return None

        workspace = data["workspace"]
        profile = data["profile"]
        snapshot = data["snapshot"]
        initiatives = data["initiatives"]

        ws_id = workspace["id"]
        lines: list[str] = [
            "ACTIVE REPO CONTEXT (set via active_repo_tool — Session 1119 multi-repo v0):",
            f"- Repo: **{workspace['name']}** (workspace_id={ws_id})",
            f"- Root: `{workspace['root_path']}`",
            f"- Branch: `{workspace.get('current_branch') or 'unknown'}`",
        ]

        if profile:
            meta = profile.get("metadata", {})
            lines.append(
                f"- Repo Profile deliverable: {profile['id']} "
                f"(last refresh: {meta.get('last_refresh_at') or 'never'})"
            )

            bridge = meta.get("bridge_relationship")
            if isinstance(bridge, dict) and bridge.get("reaches_engine"):
                lines.append(
                    f"- Engine bridge: reaches `{bridge.get('reaches_engine')}` "
                    f"via {bridge.get('via', 'HTTP')}"
                )

            fleet_role = meta.get("fleet_role")
            if isinstance(fleet_role, dict) and fleet_role.get("role"):
                pieces = [f"role={fleet_role['role']}"]
                if fleet_role.get("pillar"):
                    pieces.append(f"pillar={fleet_role['pillar']}")
                if fleet_role.get("status"):
                    pieces.append(f"status={fleet_role['status']}")
                lines.append(f"- Fleet role: {', '.join(pieces)}")

            constraints = meta.get("constraints_text") or []
            if isinstance(constraints, list) and constraints:
                lines.append("- Hard constraints (respect these):")
                for c in constraints[:MAX_CONSTRAINTS_INLINED]:
                    text = str(c)[:240]
                    lines.append(f"  - {text}")

        if snapshot:
            meta = snapshot.get("metadata", {})
            git = meta.get("git") or {}
            head = (git.get("head") or "?")[:12]
            dirty = git.get("dirty")
            lines.append(
                f"- Latest snapshot: {snapshot['id']} (refreshed {meta.get('refreshed_at')})"
            )
            lines.append(f"  HEAD=`{head}` dirty=`{dirty}`")

        if initiatives:
            lines.append(
                f"- Open TRIAGE initiatives ({len(initiatives)} — auto-extracted from surveys, awaiting your review):"
            )
            for i in initiatives:
                lines.append(
                    f"  - [u={i['urgency']:.2f} i={i['impact_score']:.2f}] {i['name']}"
                )

        lines.extend([
            "",
            "USE THIS CONTEXT:",
            "- Scope answers to this repo unless the user explicitly asks about u-d-b or another fleet member.",
            "- For full Repo Profile / Snapshot / Survey content, call `deliverable_tool` with "
            f"`workspace_id={ws_id}` and category in [repo_profile, repo_snapshot, repo_survey].",
            "- For the TRIAGE initiatives list, call `initiative_tool` (or query Initiative model directly) "
            f"with `target_workspace={ws_id}` and `status=TRIAGE`.",
            "- DO NOT modify files in this repo via Claude Code unless the user has explicitly scoped the request.",
            "- u-d-b (this engine) is NOT a fleet member — don't try to set it as active_repo.",
        ])

        return "\n".join(lines)

    except Exception as e:  # noqa: BLE001 — never break PA flow
        logger.debug("[PA] active_repo_context load failed: %s", e)
        return None
