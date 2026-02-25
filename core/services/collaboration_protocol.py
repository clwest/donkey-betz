"""
Three-Way Collaboration Protocol — structured message helpers.

Enables Claude Code to post structured messages into PA conversations
so the User and PA both have durable context about what was done and why.

Usage (from Claude Code via Railway API):
    from core.services.collaboration_protocol import CollaborationMessage, post_to_conversation

    msg = CollaborationMessage.result(
        title="PR-14 merged successfully",
        body="Created content pipeline screen with 4 views.",
        metadata={"pr_number": 1470, "files_changed": 4},
    )
    post_to_conversation(conversation_id="mobile-pr14", message=msg, token="<token>")

Usage (internal — from Django code):
    from core.services.collaboration_protocol import post_structured_message

    post_structured_message(
        user=request.user,
        conversation_id="mobile-pr14",
        msg_type="RESULT",
        title="PR-14 merged",
        body="Details here.",
        source="claude-code",
    )
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ── Message types ─────────────────────────────────────────────────────────────

VALID_TYPES = frozenset({"PLAN", "STATUS", "RESULT", "DIFF", "ERROR", "QUESTION"})

VALID_SOURCES = frozenset({"web", "mobile", "discord", "api", "claude-code", "pa"})


# ── Structured message dataclass ──────────────────────────────────────────────

@dataclass
class CollaborationMessage:
    """A structured message following the collaboration protocol."""

    msg_type: str
    title: str
    body: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.msg_type not in VALID_TYPES:
            raise ValueError(f"Invalid message type: {self.msg_type}. Must be one of {VALID_TYPES}")

    def render(self) -> str:
        """Render to the wire format that PA can parse."""
        parts = [f"[{self.msg_type}] {self.title}"]
        if self.body:
            parts.append("")
            parts.append(self.body)
        if self.metadata:
            parts.append("")
            parts.append("--- metadata ---")
            for k, v in self.metadata.items():
                parts.append(f"{k}: {v}")
        return "\n".join(parts)

    # ── Convenience constructors ──────────────────────────────────────────

    @classmethod
    def plan(cls, title: str, body: str, **meta: Any) -> CollaborationMessage:
        return cls(msg_type="PLAN", title=title, body=body, metadata=meta)

    @classmethod
    def status(cls, title: str, body: str = "", **meta: Any) -> CollaborationMessage:
        return cls(msg_type="STATUS", title=title, body=body, metadata=meta)

    @classmethod
    def result(cls, title: str, body: str, **meta: Any) -> CollaborationMessage:
        return cls(msg_type="RESULT", title=title, body=body, metadata=meta)

    @classmethod
    def diff(cls, title: str, body: str, **meta: Any) -> CollaborationMessage:
        return cls(msg_type="DIFF", title=title, body=body, metadata=meta)

    @classmethod
    def error(cls, title: str, body: str, **meta: Any) -> CollaborationMessage:
        return cls(msg_type="ERROR", title=title, body=body, metadata=meta)

    @classmethod
    def question(cls, title: str, body: str, **meta: Any) -> CollaborationMessage:
        return cls(msg_type="QUESTION", title=title, body=body, metadata=meta)


# ── Parser ────────────────────────────────────────────────────────────────────

_TYPE_RE = re.compile(r"^\[(\w+)\]\s*(.+)$")
_META_RE = re.compile(r"^(\w[\w_]*)\s*:\s*(.+)$")


def parse_structured_message(text: str) -> CollaborationMessage | None:
    """Parse a rendered structured message back into a CollaborationMessage.

    Returns None if the text doesn't match the protocol format.
    """
    lines = text.strip().split("\n")
    if not lines:
        return None

    m = _TYPE_RE.match(lines[0])
    if not m:
        return None

    msg_type = m.group(1).upper()
    title = m.group(2).strip()

    if msg_type not in VALID_TYPES:
        return None

    body_lines: list[str] = []
    metadata: dict[str, Any] = {}
    in_metadata = False

    for line in lines[1:]:
        if line.strip() == "--- metadata ---":
            in_metadata = True
            continue
        if in_metadata:
            mm = _META_RE.match(line)
            if mm:
                key, val = mm.group(1), mm.group(2).strip()
                # Try to parse as int/float/bool
                if val.lower() in ("true", "false"):
                    metadata[key] = val.lower() == "true"
                else:
                    try:
                        metadata[key] = int(val)
                    except ValueError:
                        try:
                            metadata[key] = float(val)
                        except ValueError:
                            metadata[key] = val
        else:
            body_lines.append(line)

    # Strip leading/trailing blank lines from body
    body = "\n".join(body_lines).strip()

    return CollaborationMessage(msg_type=msg_type, title=title, body=body, metadata=metadata)


# ── Internal posting (Django server-side) ─────────────────────────────────────

def post_structured_message(
    user,
    conversation_id: str,
    msg_type: str,
    title: str,
    body: str = "",
    source: str = "claude-code",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Post a structured collaboration message into a PA conversation.

    This is the server-side helper — used when code running inside Django
    (e.g. a Celery task or management command) needs to post to a conversation.

    For external callers (Claude Code CLI), use the REST API directly:
        POST /api/pa/chat/
        {
            "message": rendered_message,
            "conversation_id": "...",
            "source": "claude-code"
        }
    """
    msg = CollaborationMessage(
        msg_type=msg_type,
        title=title,
        body=body,
        metadata=metadata or {},
    )
    rendered = msg.render()

    # Import here to avoid circular imports
    from core.models import ChatConversation

    record = ChatConversation.objects.create(
        user=user,
        conversation_id=conversation_id,
        user_message=rendered,
        assistant_response="",  # PA hasn't responded yet
        platform="api",
        metadata={
            "source": source,
            "structured_type": msg_type,
            "structured_metadata": metadata or {},
            "collaboration_protocol": "1.0",
        },
    )

    logger.info(
        "[CollabProtocol] Posted %s message to conversation %s (source=%s, pk=%s)",
        msg_type,
        conversation_id,
        source,
        record.pk,
    )

    return {
        "success": True,
        "message_id": str(record.pk),
        "conversation_id": conversation_id,
        "type": msg_type,
        "source": source,
    }


# ── External posting helper (for scripts/CLI) ────────────────────────────────

def post_to_conversation(
    conversation_id: str,
    message: CollaborationMessage,
    token: str,
    base_url: str = "https://donkey-betz-platform-production.up.railway.app",
    source: str = "claude-code",
) -> dict[str, Any]:
    """Post a structured message to a PA conversation via the REST API.

    Used by external tools (Claude Code CLI) that can't import Django models.
    """
    import urllib.request

    url = f"{base_url}/api/pa/chat/"
    payload = json.dumps({
        "message": message.render(),
        "conversation_id": conversation_id,
        "source": source,
    }).encode()

    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    })

    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode())
