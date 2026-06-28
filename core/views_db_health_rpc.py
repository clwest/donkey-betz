"""Prod RPC endpoint for db_health_tool — Session 1249 P2(a).

Exposes a token-gated forwarder to the existing db_health_tool dispatcher so
local Rigby (and future cross-env callers) can query prod DB state without
shell access. Read-only — action allowlist is enforced; no write surface.

Server-side PR scope (this file). A follow-up PR will add the local
db_health_tool ``env='prod'`` selector that POSTs here.

See ``00-START-NEXT-SESSION.md`` § "Priority 2 — local↔prod parity leverage
menu (a)".
"""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Optional

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


ALLOWED_ACTIONS = frozenset({
    'overview',
    'migrations',
    'tables',
    'verify_table',
    'search_tables',
    'pgvector',
    'learning_stats',
})

_DISPATCHER = None  # cached ToolDispatcher instance


def _get_configured_token() -> Optional[str]:
    token = os.environ.get('PA_DB_HEALTH_RPC_TOKEN', '').strip()
    return token or None


def _extract_token(request: HttpRequest) -> Optional[str]:
    header = request.META.get('HTTP_AUTHORIZATION', '')
    if not header.lower().startswith('token '):
        return None
    return header.split(' ', 1)[1].strip() or None


def _get_dispatcher():
    global _DISPATCHER
    if _DISPATCHER is None:
        from core.services.tool_dispatcher import ToolDispatcher
        _DISPATCHER = ToolDispatcher()
    return _DISPATCHER


@csrf_exempt
@require_POST
def db_health_rpc(request: HttpRequest) -> JsonResponse:
    """Token-gated thin forwarder to db_health_tool actions.

    - 404 when ``PA_DB_HEALTH_RPC_TOKEN`` is unset (reduces endpoint discovery).
    - 401 when the ``Authorization: Token <hex>`` header is missing or wrong.
    - 400 when payload is malformed JSON or missing ``action``.
    - 403 when ``action`` is not in :data:`ALLOWED_ACTIONS`.
    - 200 with ``{ok, result, error, trace_id}`` on dispatch.
    """
    configured = _get_configured_token()
    if not configured:
        return JsonResponse({'error': 'not found'}, status=404)

    provided = _extract_token(request)
    if not provided or provided != configured:
        return JsonResponse({'error': 'unauthorized'}, status=401)

    try:
        payload: Any = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'malformed JSON payload'}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({'error': 'payload must be a JSON object'}, status=400)

    action = payload.get('action')
    if not action:
        return JsonResponse({'error': "payload missing 'action'"}, status=400)

    if action not in ALLOWED_ACTIONS:
        return JsonResponse(
            {'error': f"action '{action}' not in allowlist",
             'allowed_actions': sorted(ALLOWED_ACTIONS)},
            status=403,
        )

    trace_id = f"rpc-{uuid.uuid4().hex[:12]}"
    dispatcher = _get_dispatcher()
    try:
        result = dispatcher._handle_db_health(
            tool_name='db_health_tool',
            payload=payload,
            user_id=None,
            trace_id=trace_id,
        )
    except Exception as exc:
        return JsonResponse(
            {'ok': False, 'error': f'{type(exc).__name__}: {exc}', 'trace_id': trace_id},
            status=500,
        )

    return JsonResponse({
        'ok': True,
        'result': result,
        'error': None,
        'trace_id': trace_id,
    })
