"""
ToolDispatcher mixin for the ``rigby_shift_brief_tool`` PA tool (PR 12A).

Single action ``generate`` (default). Read-only. Returns the structured
shift-brief payload from :func:`core.services.rigby_shift_brief.build_shift_brief`.

No human notification surface. No agent dispatch. No state mutation. No
feature flag — this tool is always live.
"""
from __future__ import annotations

import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)


class RigbyShiftBriefMixin:
    """Mixin providing the ``rigby_shift_brief_tool`` handler."""

    def _handle_rigby_shift_brief(
        self,
        tool_name: str,
        payload: dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> dict[str, Any]:
        from core.services.rigby_shift_brief import build_shift_brief

        p = payload or {}
        action = p.get("action", "generate")

        if action != "generate":
            return {
                "ok": False,
                "tool": "rigby_shift_brief_tool",
                "error": (
                    f"Unknown action {action!r}. Supported: generate."
                ),
            }

        conversation_id = (
            p.get("conversation_id")
            or getattr(self, "_current_conversation_id", None)
        )
        window = p.get("window", "24h")

        result = build_shift_brief(
            user_id=user_id,
            conversation_id=conversation_id,
            window=window,
        )
        result["tool"] = "rigby_shift_brief_tool"
        result["action"] = action
        return result
