---
title: "Session 1128 — Fleet brain bridge sends routing (Phase 2B back-prop, 7 PRs)"
date: 2026-05-22
status: active
session: 1128
previous_handoff: SESSION_1127_FLEET_ROUTING_PHASE_2A.md
---

# Session 1128 — Phase 2B: fleet apps now send routing

> **Read this if** you want to know which apps can now request a specific
> u-d-b agent (and which ones are still inert), what the wire shape looks
> like at the `/api/brain/ask` boundary, why one `brain_client.py` file is
> intentionally copy-pasted across 7 repos, or what Phase 2C still needs.

## TL;DR

Seven PRs. Phase 2A (u-d-b PR #2127) made routing *actionable*; Phase
2B makes the fleet apps actually *send* routing blocks. Without 2B,
2A's dispatch path stayed inert.

| Repo | PR | Notes |
|---|---|---|
| contract-concierge | [#10](https://github.com/clwest/contract-concierge/pull/10) | Reference implementation. `force_allowed=true` so this app can actually test end-to-end force dispatch. |
| mentorforge | [#13](https://github.com/clwest/mentorforge/pull/13) | Verbatim back-prop. |
| pitchdeckforge | [#12](https://github.com/clwest/pitchdeckforge/pull/12) | Verbatim back-prop. |
| sellerpilot | [#6](https://github.com/clwest/sellerpilot/pull/6) | Verbatim back-prop. |
| dealflowtracker | [#10](https://github.com/clwest/dealflowtracker/pull/10) | Verbatim back-prop. |
| compliancesentinel | [#6](https://github.com/clwest/compliancesentinel/pull/6) | Verbatim back-prop. Default agent is `null` (no SecurityAgent in AGENT_MAP); routing falls through to normal PA. |
| signal-studio | [#6](https://github.com/clwest/signal-studio/pull/6) | Verbatim back-prop, no-auth shape. `force_allowed=true`. |

Co-designed with Rigby in conversation `pa-d19c1674b936` (Session 1127
→ 1128). Three of her Session 1128 adjustments shaped the wire shape;
see "Wire shape" below.

## Wire shape — what /api/brain/ask now sends

Outbound payload from any fleet app to u-d-b `/api/pa/chat/`:

```json
{
  "message": "draft an NDA",
  "source": "mentorforge",
  "platform": "brain-bridge",
  "context": {
    "source": "mentorforge",
    "platform": "brain-bridge",
    "workspace": "contract-concierge",
    "user_id": "...",
    "app_slug": "contract-concierge",
    "request_id": "<uuid4 hex>"
  },
  "routing": {
    "requested_by": "fleet_app",
    "mode": "force",
    "agent": "legal_doc_drafter_agent"
  }
}
```

Three Rigby-driven contract decisions worth flagging:

1. **`app_slug` lives in `context`, not as a top-level field.** The
   u-d-b view already passes `context` through verbatim; this avoids
   schema-reject risk from any stricter serializer landing later.
   The Phase 2A view code still accepts a top-level `app_slug` for
   back-compat with Phase 1 callers, but new callers should use the
   canonical location.
2. **No silent hint-mode default.** Routing block is only sent when
   the caller explicitly passes mode/agent/role. A bare
   `/api/brain/ask` POST behaves exactly like it did before 2B.
3. **`request_id` auto-propagation.** Every call generates a `uuid4()`
   in `context.request_id` if the caller didn't pass one. Joins
   fleet-app logs to u-d-b logs without a manual trace_id hand-off.

Returned response now surfaces u-d-b's `routing` block:

```json
{
  "ok": true,
  "answer": "...",
  "trace_id": "trace-abc",
  "routing": {
    "app_slug": "contract-concierge",
    "resolved_agent": "legal_doc_drafter_agent",
    "routed_to": "LegalDocDrafterAgent",
    "phase2_dispatched": true,
    "allowlist_hit": true,
    "force_permitted": true,
    "was_overridden": false
  }
}
```

`routing.phase2_dispatched` is the headline signal: when `true`, u-d-b
bypassed its intent detector entirely and went straight to the
requested agent.

## Why `brain_client.py` is intentionally copy-pasted

Per Rigby's Session 1127 signoff: "ship per-app updates first, keep
the code identical and minimal so it's easy to converge later."
Across the 7 repos, the file differs in exactly two places:

- the docstring's first line (cosmetic — repo name)
- `DEFAULT_APP_SLUG` constant

A "DO NOT EDIT EXCEPT THESE CONSTANTS" header sits at the top of every
copy so the next round (Phase 2C — extract into a shared package)
doesn't have to diff away accidental per-repo drift.

If you find yourself wanting to fix something in `brain_client.py`,
**fix it in contract-concierge first, then back-prop with the helper
script saved at `/tmp/propagate_brain_client.py` (or recreate it).**

## Invariant test per app (Rigby's required test)

Every repo now ships `backend/tests/test_brain_routing_forwarding.py`
with 3 cases:

- No routing fields → no `routing` block on outbound payload, but
  `context.app_slug` + `context.request_id` always present.
- `mode=force` + `agent` → routing block forwarded; response
  `routing.phase2_dispatched` surfaced back through `/api/brain/ask`.
- `mode=hint` + `role` only → routing block forwarded with role, no
  agent (covers the role-only path).

Tests mock `app.brain_client._http_request` so they never touch the
network; they also pre-set `BRAIN_TOKEN` and `DATABASE_URL` envvars
before importing the app so the SQLAlchemy engine doesn't crash at
import time. 21 tests pass across the 7 repos (3 × 7).

## End-to-end smoke (deferred — needs all 7 merged)

The natural integration test runs once all 7 PRs are merged:

1. Bring up the fleet: `cd ~/development/infra && make up`
2. Hit any app's `/api/brain/ask` with an explicit force route:
   ```bash
   curl -X POST http://localhost:8003/api/brain/ask \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "draft a 1-page NDA",
       "mode": "force",
       "agent": "legal_doc_drafter_agent"
     }'
   ```
3. Expect response: `routing.phase2_dispatched: true` and
   `routing.routed_to: "LegalDocDrafterAgent"`.

contract-concierge and signal-studio are the two with
`force_allowed=true`; either is a valid e2e target.

## What did NOT land (deferred)

### Frontend role-select dropdown (Phase 2B.2)

Each repo's Brain page currently has only a freeform message input.
Adding a role-select dropdown (e.g. "PA chooses" / "Legal drafter
(force)" / "Trend analyst (hint)") is the natural next UI step. Out
of scope for 2B to keep the PR focused on the wire contract.

### FC-path hint bias

u-d-b's `_run_agentic_loop` (the GPT-5.2 function-calling path) doesn't
yet read `_routing_hint` from context. Only the keyword routing path
applies hints. When `PA_USE_FUNCTION_CALLING=True` (the default in
prod), hints are observable in the routing decision dict but have no
effect on routing. Deferred to Phase 2D.

### `SecurityAgent` for compliancesentinel

`compliancesentinel`'s default agent is still `null` (no SecurityAgent
class). Force-dispatch from compliancesentinel is impossible until
either (a) a real `SecurityAgent` lands in u-d-b's AGENT_MAP, or
(b) the default + allowlist get remapped to an existing concrete
agent (likely `MemoryIsolationAgent` or `ContentAuditAgent`).
Rigby's call.

### Service-token verification for `app_slug` (Phase 2C-ish)

Any caller with a valid PA token can still claim any `app_slug`.
Mitigated by u-d-b's allowlist + force_allowed gates; hard
verification waits for a separate hardening PR.

## Carryovers (open / parked)

- **u-d-b PR #2127** — Phase 2A; needs merge so the dispatch contract
  is on `main`. 2B PRs depend on the response shape it ships.
- **ai-content-studio#2** — Docker foundation PR. Per Chris: back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).

## Operational notes

- **`brain_client.py` is byte-identical across 6 of 7 repos.** Only
  `DEFAULT_APP_SLUG` and the docstring's first line legitimately
  differ. Any other drift is a bug — diff against contract-concierge
  to find it.
- **Test files require BRAIN_TOKEN + DATABASE_URL env hints.** The
  test sets `os.environ.setdefault(...)` for both before importing
  the app. If you write a new test, follow the same pattern or the
  SQLAlchemy engine will fail at import time.
- **The `requested_by: "fleet_app"` field in `routing`** is forward-
  compatible metadata for Phase 2C service-token verification.
  u-d-b's resolver currently ignores it; that's intentional.
