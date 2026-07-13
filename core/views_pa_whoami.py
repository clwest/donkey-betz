"""S2776 N21 — PA wrapper ownership verification endpoint.

`GET /api/pa/whoami/` returns the authenticated user's identity. Called by
the `verify_pa_wrapper_ownership` management command from the
`tools/pa_local.sh` bash prelude to confirm that `PA_API_TOKEN` resolves to
the expected user before any dispatch happens. Catches the S2774
travel-recovery scenario (wrapper token → user that didn't exist on the
newly-active DB, blocked dispatch for ~30min before symptoms surfaced) in
seconds instead of the next log-tail deep-dive.

────────────────────────────────────────────────────────────────────────────
SHARP 5-POINT TEST for future `/api/pa/*` endpoints (Rigby S2776 zoom-out
mitigation to prevent `/api/pa/*` from becoming a second `/api/ops/*`
surface subject to the S2774 pause discipline):

    Every new `/api/pa/*` view MUST be:

      1. Read-only
      2. Deterministic
      3. No side effects
      4. Bounded output schema
      5. Directly needed for toolchain correctness

    If any proposed `/api/pa/*` endpoint fails one of the above, it does
    NOT get a routine `api/pa/*` slot — it must go through the stricter
    `/api/ops/*` surface-pause rubric per S2774 forward-carry.

`/api/pa/whoami/` is the canonical exemplar: read-only (GET, no writes),
deterministic (same input → same output for the session), no side effects
(does not touch any DB row, does not enqueue a task, does not log to
ops-visible surfaces), bounded output schema (three fields), and directly
needed for `pa_local.sh` toolchain correctness (S2774 recovery incident).
────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
@login_required
def pa_whoami(request):
    """Return the authenticated user's identity in a bounded 3-field payload."""
    # user.id is a UUID on this platform; str() keeps the wire format
    # stable across UUID/int PK conventions and avoids JsonResponse's
    # non-serializable UUID trap.
    return JsonResponse({
        'username': request.user.username,
        'user_id': str(request.user.id),
        'is_staff': bool(request.user.is_staff),
    })
