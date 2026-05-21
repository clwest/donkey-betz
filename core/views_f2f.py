"""F2F (Rigby Face-to-Face) voice session HTTP endpoints — Session 1118 F2F.2.

Three endpoints mirror the broker's surface and translate broker
exceptions into the HTTP shape Rigby locked in F2F.2 design:

* POST /api/pa/voice_session/           — create
* POST /api/pa/voice_session/<uuid>/speak/ — push text to avatar
* POST /api/pa/voice_session/<uuid>/end/  — explicit teardown

Error JSON body shape (consistent across cap + unavailability + provider):
    {
        "error_code": "F2F_CAP_EXCEEDED_DAILY",
        "message": "...",
        "cap_kind": "daily" | "monthly" | "session_spend" | "session_duration",
        "reset_at": "<ISO>",       # daily/monthly only
        "duration_seconds": <num>, # duration trips only
        "duration_limit_seconds": <int>,
        "cap_limit_cents": <int>,  # spend trips only
        "cap_used_cents": <int>,
        "provider_name": "heygen" | "mock",
        "mock_mode": <bool>
    }
"""
from __future__ import annotations

import logging
from typing import Any

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import core.services.f2f_broker as f2f_broker
from core.models_f2f import F2FSession
from core.services.realtime_avatar import F2FUnavailableError

logger = logging.getLogger(__name__)


# ---- Workspace resolution ---------------------------------------


def _resolve_workspace(request) -> tuple[Any | None, Response | None]:
    """Resolve the ``ProjectWorkspace`` for this request.

    The client must send ``workspace_id`` in the body. We verify the
    authenticated user owns or co-owns the workspace. Returns
    ``(workspace, None)`` on success or ``(None, error_response)``
    on any failure.
    """
    workspace_id = request.data.get("workspace_id")
    if not workspace_id:
        return None, Response(
            {
                "error_code": "F2F_WORKSPACE_REQUIRED",
                "message": "workspace_id is required.",
            },
            status=400,
        )

    from core.models_skin_layer import ProjectWorkspace

    workspace = (
        ProjectWorkspace.objects.filter(id=workspace_id, user=request.user)
        .first()
    )
    if workspace is None:
        return None, Response(
            {
                "error_code": "F2F_WORKSPACE_NOT_FOUND",
                "message": "Workspace not found or not owned by you.",
            },
            status=404,
        )
    return workspace, None


# ---- Error → HTTP mapping ---------------------------------------


def _cap_response(exc: f2f_broker.F2FCapExceededError, session: F2FSession | None) -> Response:
    """Map ``F2FCapExceededError`` → HTTP 402 / 429 with the locked
    JSON body shape."""
    if exc.cap_kind in ("daily", "monthly"):
        status_code = 402
        code = f"F2F_CAP_EXCEEDED_{exc.cap_kind.upper()}"
    else:  # session_spend, session_duration
        status_code = 429
        code = f"F2F_CAP_EXCEEDED_{exc.cap_kind.upper()}"

    body: dict[str, Any] = {
        "error_code": code,
        "message": str(exc),
        "cap_kind": exc.cap_kind,
    }
    if exc.reset_at is not None:
        body["reset_at"] = exc.reset_at
    if exc.duration_seconds is not None:
        body["duration_seconds"] = exc.duration_seconds
    if exc.duration_limit_seconds is not None:
        body["duration_limit_seconds"] = exc.duration_limit_seconds
    if exc.cap_limit_cents is not None:
        body["cap_limit_cents"] = exc.cap_limit_cents
    if exc.cap_used_cents is not None:
        body["cap_used_cents"] = exc.cap_used_cents
    if session is not None:
        body["provider_name"] = session.provider_name
        body["mock_mode"] = session.mock_mode

    return Response(body, status=status_code)


# ---- Views -------------------------------------------------------


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_voice_session(request):
    """Allocate a new F2F session for the caller's workspace.

    Body: ``{workspace_id, avatar_id?, voice_id?, metadata?}``
    Returns 201 with the SDK-safe payload the SPA hands to its
    avatar SDK to establish the WebRTC connection.
    """
    workspace, err = _resolve_workspace(request)
    if err is not None:
        return err

    avatar_id = request.data.get("avatar_id", "") or ""
    voice_id = request.data.get("voice_id", "") or ""
    metadata = request.data.get("metadata") or {}
    if not isinstance(metadata, dict):
        return Response(
            {
                "error_code": "F2F_BAD_METADATA",
                "message": "metadata must be a JSON object.",
            },
            status=400,
        )

    try:
        result = f2f_broker.create_session(
            workspace=workspace,
            user=request.user,
            avatar_id=avatar_id,
            voice_id=voice_id,
            metadata=metadata,
        )
    except F2FUnavailableError as exc:
        return Response(
            {
                "error_code": "F2F_PROVIDER_UNAVAILABLE",
                "message": str(exc),
            },
            status=503,
        )
    except f2f_broker.F2FCapExceededError as exc:
        return _cap_response(exc, session=None)
    except f2f_broker.F2FProviderInvocationError as exc:
        logger.exception("F2F create_session provider failure")
        return Response(
            {
                "error_code": "F2F_PROVIDER_ERROR",
                "message": str(exc),
            },
            status=502,
        )

    session = result.session
    return Response(
        {
            "session_id": str(session.id),
            "provider_name": session.provider_name,
            "provider_session_id": result.provider_session_id,
            "mock_mode": session.mock_mode,
            "avatar_id": session.avatar_id,
            "voice_id": session.voice_id,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "expires_at": result.expires_at,
            "sdk_payload": result.sdk_payload,
        },
        status=201,
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def speak_voice_session(request, session_id: str):
    """Push ``text`` to the avatar. Body: ``{text: str}``.

    Returns 200 with chars/cost on success; cap trips return 402/429,
    provider errors 502, session-terminal 410.
    """
    text = request.data.get("text")
    if not isinstance(text, str) or not text.strip():
        return Response(
            {
                "error_code": "F2F_TEXT_REQUIRED",
                "message": "text is required and must be a non-empty string.",
            },
            status=400,
        )

    session = get_object_or_404(F2FSession, id=session_id, user=request.user)

    try:
        result = f2f_broker.speak(session, text)
    except f2f_broker.F2FSessionNotActiveError as exc:
        return Response(
            {
                "error_code": "F2F_SESSION_NOT_ACTIVE",
                "message": str(exc),
                "status": session.status,
                "ended_reason": session.ended_reason,
            },
            status=410,
        )
    except f2f_broker.F2FCapExceededError as exc:
        return _cap_response(exc, session=session)
    except f2f_broker.F2FProviderInvocationError as exc:
        logger.exception("F2F speak provider failure")
        return Response(
            {
                "error_code": "F2F_PROVIDER_ERROR",
                "message": str(exc),
                "provider_name": session.provider_name,
                "mock_mode": session.mock_mode,
            },
            status=502,
        )

    return Response(
        {
            "session_id": str(session.id),
            "chars_sent": result.chars_sent,
            "cost_cents": result.cost_cents,
            "accepted": result.accepted,
            "deduped": result.deduped,
            "total_chars_spoken": session.total_chars_spoken,
            "total_cost_cents": session.total_cost_cents,
            "speak_call_count": session.speak_call_count,
            "status": session.status,
        },
        status=200,
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def end_voice_session(request, session_id: str):
    """Explicit teardown. Idempotent — terminal sessions return 200
    with the existing terminal state."""
    session = get_object_or_404(F2FSession, id=session_id, user=request.user)
    reason = request.data.get("reason", "") or ""

    f2f_broker.end_session(session, reason=reason)
    session.refresh_from_db()

    return Response(
        {
            "session_id": str(session.id),
            "status": session.status,
            "ended_reason": session.ended_reason,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "total_chars_spoken": session.total_chars_spoken,
            "total_cost_cents": session.total_cost_cents,
            "speak_call_count": session.speak_call_count,
            "duration_seconds": session.duration_seconds(),
        },
        status=200,
    )
