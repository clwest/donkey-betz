"""Editor dispatch helpers — Session 1092.

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
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def gather_workspace_content_for_editor(
    workspace_id: Optional[str],
    task_text: str,
    *,
    max_sections: int = 6,
    section_char_cap: int = 3000,
) -> Optional[Dict[str, Any]]:
    """Gather recent deliverables from a workspace as content for EditorAgent.

    Returns a content dict shaped like a SelfBlog (title/intro/sections/
    conclusion), or None if no usable deliverables are present. Excludes
    EditorAgent's own prior output and ContentWriter blog posts to avoid
    feedback loops.

    Args:
        workspace_id: Caller-provided workspace UUID. Falls back to the
            single active non-system workspace if the caller's id points
            to System Autonomous (which is typically empty).
        task_text: The original task string, kept for log readability.
        max_sections: Cap on number of source deliverables included.
        section_char_cap: Cap on each section's body length to limit
            prompt bloat.
    """
    try:
        from core.models_deliverables import Deliverable
        from core.models_skin_layer import ProjectWorkspace

        target_ws = workspace_id

        # Prefer the single active non-system workspace when one exists —
        # callers (especially the PA entrypoint) sometimes inject the
        # System Autonomous workspace which is empty by design.
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

        deliverables = (
            Deliverable.objects
            .filter(workspace_id=target_ws)
            .exclude(title__startswith='EditorAgent:')
            .exclude(title__startswith='blog_post:')
            .exclude(deliverable_type='blog_post')
            .order_by('-created_at')[:max_sections]
        )

        sections = []
        titles = []
        for d in deliverables:
            body = d.content or ''
            if not body.strip():
                continue
            title = d.title or 'Untitled'
            titles.append(title)
            sections.append({
                'heading': title,
                'content': body[:section_char_cap],
            })

        if not sections:
            return None

        logger.info(
            "[editor-gather] Gathered %d deliverables from workspace %s for task '%s': %s",
            len(sections), target_ws, (task_text or '')[:60],
            ', '.join(t[:60] for t in titles),
        )
        return {
            'title': f"Executive Brief (synthesized from {len(sections)} sources)",
            'intro': f"This brief synthesizes {len(sections)} workspace deliverables.",
            'sections': sections,
            'conclusion': '',
        }
    except Exception as e:
        logger.warning("[editor-gather] Failed: %s", e)
        return None
