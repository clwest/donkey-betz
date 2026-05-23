---
title: "Session 1129 — Fleet brain: signed identity + artifact lifecycle + SSE event stream"
date: 2026-05-22
status: active
session: 1129
previous_handoff: SESSION_1128_FLEET_BRAIN_BRIDGE_ROUTING.md
---

# Session 1129 — Fleet brain becomes a real distributed system

> **Read this if** you want to know how fleet apps now sign every
> request, where artifacts live, how lifecycle events flow back to
> the browser via two SSE hops, why Contract Concierge has a working
> Drafts library now, or what Move 3 Round 2 still needs.

## TL;DR

Session 1129 took the fleet from "apps can claim any app_slug" to
**authenticated, observable, push-capable distributed system**:

| Move | What it gives | PRs |
|---|---|---|
| **Move 1** — Service identity + signed requests | HMAC-SHA256 X-Fleet-* headers replace bare PA-token trust. Replay protection via Redis nonce store. 11 deny codes. Audit log. | u-d-b [#2129](https://github.com/clwest/donkey-betz-platform/pull/2129), 6 fleet repo back-props |
| **Move 2 Round 1** — Artifact push/pull | Fleet apps can persist work-product to u-d-b + retrieve by id. Auto-scoped to caller's app_slug. | u-d-b [#2130](https://github.com/clwest/donkey-betz-platform/pull/2130), CC [#12](https://github.com/clwest/contract-concierge/pull/12), 6 fleet back-props |
| **Move 2 Round 2** — List endpoint + TTL retention | Listing with pagination/filters; expires_at + soft-delete + cleanup beat task. | u-d-b spec [#2131](https://github.com/clwest/donkey-betz-platform/pull/2131), impl [#2132](https://github.com/clwest/donkey-betz-platform/pull/2132), CC [#13](https://github.com/clwest/contract-concierge/pull/13), 6 fleet back-props |
| **Flagship demo** — Contract Concierge AI Draft Library | Real user flow: log in → form → Rigby force-routes to `legal_doc_drafter_agent` → draft persisted as fleet artifact → library + view. | CC [#14](https://github.com/clwest/contract-concierge/pull/14) |
| **Move 3 Round 1** — SSE event stream | u-d-b emits `FleetEvent` rows + Redis pub/sub. SSE endpoint streams to fleet apps. CC re-emits to browser with per-user filter. | u-d-b [#2133](https://github.com/clwest/donkey-betz-platform/pull/2133), CC [#15](https://github.com/clwest/contract-concierge/pull/15), 6 fleet back-props (subscriber-only) |

Co-designed with Rigby in conversation `pa-d19c1674b936`. All
implementable details drafted by Rigby before code; deltas reviewed
in-session. Specs consolidated into
[`docs/specs/FLEET_MOVE_1_AND_2_SPEC.md`](../specs/FLEET_MOVE_1_AND_2_SPEC.md)
and [`docs/specs/FLEET_MOVE_2_ROUND_2_SPEC.md`](../specs/FLEET_MOVE_2_ROUND_2_SPEC.md).

## Move 1 — what "fleet auth" actually means now

### The trust model before vs after

**Before 1129.** Every fleet → u-d-b call carried a PA token
(`Authorization: Bearer <token>`) and a self-declared
`context.app_slug`. Any caller with a valid token could claim to be
any app and trigger any allowed agent. The allowlist + `force_allowed`
flags in `config/fleet_agent_routing.json` were the only thing
preventing cross-app abuse — and they were enforced by trusting the
client.

**After 1129.** Every fleet → u-d-b call carries five signed
headers:

```
X-Fleet-App:        contract-concierge
X-Fleet-Key-Id:     fs_contractconcierge_k2
X-Fleet-Timestamp:  20260522T183847Z
X-Fleet-Nonce:      <uuid4 hex>
X-Fleet-Signature:  <base64 HMAC-SHA256>
```

Signature base (canonical, line-delimited):

```
METHOD\n
PATH\n           (query-canonicalized for GET/DELETE/HEAD)
app_slug\n
key_id\n
timestamp\n
nonce\n
sha256_hex(body)
```

HMAC key is `sha256(raw_secret)`. The server stores **only the hash**;
captured signatures can't be inverted to recover the secret.

### What u-d-b does on receive

`core/services/fleet_auth.verify_signed_request()` runs every check:

1. All five headers present?
2. Timestamp within ±90s of server clock?
3. Nonce not already used in last 600s? (Redis `SETNX` with TTL.)
4. `app_slug` resolves to an active `FleetServiceIdentity` row?
5. `key_id` belongs to that identity AND is `is_active=true`?
6. Recomputed HMAC matches?
7. `app_slug` in the route's `app_slug_allowlist` (if any)?
8. Identity has the required `capability` (if endpoint declares one)?

Each failure maps to one of 11 `DenyCode` values
(`MISSING_HEADERS`, `TIMESTAMP_DRIFT`, `NONCE_REPLAY`,
`SIGNATURE_MISMATCH`, etc) → consistent HTTP status code →
`FleetAuthAuditLog` row. The audit row is written **regardless of
outcome** (success or denial) so we can build the
`fleet_routing.force_dispatch.count` metric (Rigby's Move 1
observability hook) without a separate signal.

### DRF integration

Two authentication classes:

- **`FleetSignatureAuthentication`** — side-effect-only. Always
  returns `None` (DRF treats the request as unauthenticated by this
  class), but sets `request.fleet_identity` if signing passed. This
  lets a hybrid endpoint (e.g. PA chat) keep user-session auth as
  its primary mechanism while still seeing the fleet identity for
  routing decisions.
- **`FleetSignatureExclusiveAuthentication`** — fleet-only.
  Raises `AuthenticationFailed` with the right status code on any
  signing failure. Used for `/api/fleet/artifacts/` and
  `/api/fleet/events/stream`.

### Key management

`core/services/fleet_provisioning.py`:

- `provision_identity(app_slug, capabilities=...)` creates a fresh
  identity + initial key + returns the raw secret **exactly once**.
- `add_key_for_identity(...)` mints a second active key for
  dual-active rotation.
- `core/services/fleet_rotation.py` runs the four-state machine:
  `plan → activate → complete | abort`. Tests cover all transitions.

### Backwards compatibility

PA endpoints (`/api/pa/chat/`) accept BOTH signed and unsigned
requests during the transition. Unsigned ones fall back to PA-token
auth and the `routing` block claim is stripped server-side (logged
with `override_reason="untrusted_app_slug"`). This lets Phase 2B's
existing fleet apps keep working through the rollout window. Move 4
will close that gap.

### Migrations

- `0342_fleetidentity` — `FleetServiceIdentity`,
  `FleetServiceKey`, `FleetServiceRotation`, `FleetAuthAuditLog`.
- `0343_fleetartifact` (Move 2 R1).
- `0344_artifact_ttl_columns` (Move 2 R2).
- `0345_fleetevent` (Move 3 R1).

## Move 2 — artifact lifecycle

### The push/pull contract (Round 1)

```
POST /api/fleet/artifacts/             ← signed; create
GET  /api/fleet/artifacts/<artifact_id>/  ← signed; fetch own
```

Each `FleetArtifact` row stores:

- `id` (uuid4 PK)
- `artifact_type` (short tag, e.g. `"contract_draft"`)
- `payload` (JSONField — the actual artifact body)
- `sha256` (computed from canonical payload bytes)
- `size_bytes`
- `caller_metadata` (free-form, e.g. `{"title": ..., "doc_type": ...}`)
- `created_by_identity` (FK to `FleetServiceIdentity`)
- `created_at`, `expires_at`, `deleted_at`, `delete_reason`

**Auto-scoping invariant.** Cross-app fetches return 404 (existence
not leaked across app_slugs). Both push and pull derive the caller's
app_slug from the signature, never the request body.

### List + TTL (Round 2)

`GET /api/fleet/artifacts/` adds pagination, filtering, and TTL
awareness:

- Query params: `limit`, `offset`, `artifact_type`,
  `created_after`, `created_before`, `include_expired`,
  `include_deleted`. Server clamps `limit` to 100.
- Default behavior: only `expires_at IS NULL` OR `expires_at > now()`
  AND `deleted_at IS NULL` rows. The two `include_*` flags relax
  these for ops use.
- Response shape: `{count, limit, offset, next_offset, results}`.
  `results` is a summary projection (no payload bodies — pull-by-id
  is the way to get the full row).

### Retention beat task

`core/services/fleet_artifact_cleanup.run_cleanup()`:

- Selects `expires_at <= now AND deleted_at IS NULL`.
- Batches updates by 500 ids; caps per run at 5000.
- Sets `deleted_at = now`, `delete_reason = "expired"`.
- Idempotent: `deleted_at__isnull=True` filter eliminates already-
  deleted rows from re-selection.
- Emits one `artifact.expired` event per soft-deleted row (Move 3
  hook).
- Returns + logs `CleanupStats{scanned, soft_deleted, capped,
  duration_ms}`.

Scheduled via `cleanup_fleet_artifacts` Celery beat task. Ops also
have a `python manage.py cleanup_fleet_artifacts` command for
manual runs / tests.

### Client side (`brain_client.py`)

Three helpers added in the canonical contract-concierge copy and
back-propped to 6 repos:

- `push_artifact(payload, artifact_type, metadata=...)`
- `pull_artifact(artifact_id)`
- `list_artifacts(limit=..., offset=..., artifact_type=..., ...)`

Each returns `{ok: bool, ...} | {ok: False, error: str}`. Never
raises — view code stays clean.

## Flagship demo — Contract Concierge AI Draft Library

This was the user-visible payoff for Move 1 + Move 2 landing
together. PR clwest/contract-concierge#14.

### What the user sees

1. **Log in.** `chris@donkeybetz.com` exists in the local CC postgres
   (created mid-session for end-to-end testing). Demo user
   `demo@concierge.dev` also seeded.
2. **Open `/drafts`.** Tab in the global nav.
3. **Fill out the draft form.** Doc type (NDA / MSA / SOW / LOI),
   parties + roles, jurisdiction, term, optional special clauses.
4. **Click "Generate draft".** Backend:
   - Signs the request to u-d-b.
   - Force-routes to `legal_doc_drafter_agent` via the routing block.
   - Persists the generated draft as a fleet artifact
     (`artifact_type="contract_draft"`, metadata includes the form
     inputs + `generated_by_user_id`).
   - Returns the new artifact id + the draft text.
5. **Frontend opens the new draft.** Pulls by id (proves
   round-trip persistence — uses `/drafts/{id}` instead of the
   inline text from POST response).
6. **Library mode** lists past drafts (per-user, auto-paginated).

### Auto-scoping (two layers)

- **App-level.** u-d-b's signed artifact endpoints only return rows
  whose `created_by_identity.app_slug == "contract-concierge"`.
  Cross-app fetches return 404.
- **User-level.** CC's `/api/drafts/` filters the returned set by
  `metadata.generated_by_user_id == jwt.sub`. Different users in the
  same app can't see each other's drafts.

The user-level filter is "app-local user identity" for now — there's
no fleet-wide suite identity yet. That's a Move 4 question.

### Login fix

The fleet's draft pipeline only works for logged-in users
(it persists user_id in artifact metadata). I shipped a `chris@donkeybetz.com`
user mid-session, mounted forgot/reset password endpoints, and
verified the login flow end-to-end in the running Docker stack
(`contract_concierge_api` on `:8003`, `contract_concierge_web` on
`:5175`).

## Move 3 Round 1 — SSE event stream

### The pipeline

```
artifact gets pushed                    (POST /api/fleet/artifacts/)
        │
        ▼
emit_event("artifact.created", ...)     ↓
        │                                fleet_events.emit_event:
        │                                1. write FleetEvent row (DB commit)
        ▼                                2. publish to Redis fleet_events:<app_slug>
   FleetEvent row                       
        │
        │  (subscriber on the Redis channel)
        ▼
u-d-b SSE endpoint /api/fleet/events/stream
        │
        │  (signed upstream from fleet app)
        ▼
fleet app backend brain_events.subscribe_fleet_events()
        │
        │  (per-user filter on metadata.generated_by_user_id)
        ▼
fleet app endpoint /api/<thing>/events?token=<JWT>
        │
        │  (EventSource — token in query, JWT same secret as decode_token)
        ▼
browser: real-time UI updates
```

### Design decisions (locked with Rigby)

1. **DB-first emit.** `FleetEvent` row is written and committed
   BEFORE the Redis publish. Round 2+ can add a replay endpoint
   that walks DB rows; subscribers can't see an event that doesn't
   have a row.
2. **Redis is optional.** If Redis is down, the publish silently
   fails (best-effort, logged as warning). The DB row is the source
   of truth.
3. **App-slug granularity at u-d-b.** Per-app Redis channel
   (`fleet_events:<app_slug>`). Per-user filtering is the consuming
   app's job — this is the 2-hop fan-out pattern.
4. **`text/event-stream` on the u-d-b side bypasses DRF.**
   DRF's content negotiation rejects `text/event-stream` with a 406.
   The SSE view is a plain Django `@require_http_methods(["GET"])`
   with manual signature verification + manual audit row write.
   Same security posture as the DRF auth class — just no DRF in the
   path.
5. **Async generator + `redis.asyncio`.** Initial impl used a sync
   generator with blocking `pubsub.get_message(timeout=...)`. Under
   daphne this hung the whole event loop and made the server
   unresponsive after one disconnect. Switching to
   `redis.asyncio` + `async def event_generator` fixed it. The sync
   variant is kept for utilities/tests.
6. **Token-in-query for browser EventSource.** EventSource can't
   set custom headers. JWT goes as a query param, verified by the
   same `SECRET_KEY` + `ALGORITHM` as `decode_token`. Tokens are
   short-lived (24h), connections are same-origin.

### CC-side filter rules

`/api/drafts/events` re-emits only when ALL of these hold:

- Event type starts with `artifact.` (drops upstream `stream.opened`,
  `stream.error`, future infra envelopes).
- `payload.metadata.generated_by_user_id` exists.
- That value equals the JWT subject.

Events without owner metadata are dropped — server-side / operator-
triggered events stay server-side rather than leak across users.

### Smoke tests run during session

End-to-end through the running Docker stack:

```bash
TOKEN=$(docker exec contract_concierge_api python -c \
  "from app.auth import create_token; print(create_token('<user-id>', 'chris@donkeybetz.com'))")
(curl -sN --max-time 30 \
  "http://localhost:8003/api/drafts/events?token=$TOKEN" > /tmp/cc_sse_out.txt 2>&1) &

# 1) Same-user event → received
# 2) Different-user event → filtered out
# 3) No-owner event → filtered out
# 4) Upstream stream.opened → NOT re-forwarded (only our own user-scoped hello)
```

All four assertions held.

### Frontend integration

`DraftsPage` in `frontend/src/App.tsx`:

- EventSource subscription on mount (when `token` set).
- Live indicator: emerald dot when `onopen` / `stream.opened`
  fired, gray when `onerror`.
- 20-event activity strip with dedupe-by-event_id.
- Auto-refresh of library list on `artifact.created` so newly-
  generated drafts appear without manual reload.

## Back-prop discipline

`brain_events.py` is byte-identical across all 7 fleet repos except
`DEFAULT_APP_SLUG`. Same pattern as `brain_client.py` from Session
1128:

- Edit contract-concierge first.
- Run the propagation script:
  `python /tmp/propagate_brain_events.py` (recreate if cleared —
  see Operational notes below).
- 6 PRs across the other repos; bodies are template-copies.

The 6 back-prop PRs add the subscriber primitive but do **not** wire
it into a user-facing endpoint yet. Each repo can add its own
`/api/<thing>/events` endpoint (mirroring CC's `/api/drafts/events`)
in a follow-up PR once it has a real "live workspace" use case.

| Repo | Back-prop PR |
|---|---|
| mentorforge | [#17](https://github.com/clwest/mentorforge/pull/17) |
| pitchdeckforge | [#16](https://github.com/clwest/pitchdeckforge/pull/16) |
| sellerpilot | [#10](https://github.com/clwest/sellerpilot/pull/10) |
| dealflowtracker | [#14](https://github.com/clwest/dealflowtracker/pull/14) |
| compliancesentinel | [#10](https://github.com/clwest/compliancesentinel/pull/10) |
| signal-studio | [#10](https://github.com/clwest/signal-studio/pull/10) |

## What did NOT land (deferred)

### Move 3 Round 2 — replay + per-user filter at u-d-b

Right now u-d-b only publishes via Redis pub/sub; a subscriber that
disconnects misses everything that happened while it was away.
Round 2 adds:

- `GET /api/fleet/events/?since=<event_id>&limit=100` — pulls from
  `FleetEvent` rows for replay on reconnect.
- Optional `?user_id=...` query for u-d-b-side per-user filtering
  (cheaper than fan-out + filter in every consuming app).
- Reconnect-with-`Last-Event-ID` support on the SSE endpoint so
  the browser side can pick up where it left off.

Estimate: ~⅓ session. Brief Rigby on the replay query shape first;
she'll want to lock event_id ordering semantics (timestamp tiebreak,
gap-detection rules).

### FleetEvent retention

`FleetEvent` rows have no TTL today. They'll grow unbounded.
Mirror Move 2 R2's pattern: `expires_at` column + cleanup beat
task. Quick win — borrow the cleanup primitive.

### Service-token auth for `app_slug` (carryover from Session 1128 option A)

Still Rigby's #1 priority. Today, signed fleet requests prove
"someone with a valid key signed this", but PA-token requests on
the brain-bridge path can still claim any `app_slug`. The two are
parallel auth modes with different trust models; collapsing them
needs the routing block to be REJECTED when the PA token's
`fleet_identity` association doesn't match the claimed app_slug.

Touches: PA token model (add `allowed_app_slugs` field), the brain
bridge view (verify mapping), and the `routing.was_overridden`
path (new override reason `untrusted_app_slug`).

### Per-app SSE endpoints in the other 6 repos

mentorforge, pitchdeckforge, etc. have the subscriber primitive
but no user-facing endpoint. Each needs:

- A user-meaningful event vocabulary (mentorforge: `lesson.created`,
  `lesson.published`; pitchdeckforge: `slide.regenerated`, etc.)
- u-d-b to emit those events when its agents push the
  corresponding artifacts.
- The per-app `/api/<thing>/events` endpoint mirroring CC's flow.
- Frontend EventSource integration mirroring CC's DraftsPage.

This is straight reuse of patterns shipped — likely ½ session per
app or 1 session for two simultaneously.

### FC-path hint bias (Phase 2D, still open)

u-d-b's `_run_agentic_loop` ignores `_routing_hint`. Carryover from
Session 1128. Independent of Move 3.

## Operational notes

- **Back-prop helper scripts are in `/tmp/`** —
  `propagate_brain_client.py` and `propagate_brain_events.py`. They
  get cleared on reboot; recreate from the canonical source in
  contract-concierge if needed.
- **`/api/fleet/events/` is in `OPTIONAL_AUTH_PATHS`** in
  `core/auth_middleware.py`. Signed-but-tokenless is the canonical
  fleet auth shape; the SSE view does its own signature verification.
- **EventSource is browser-only.** The 2-hop pattern is: u-d-b
  emits → fleet backend subscribes (signed, server-to-server) →
  fleet backend re-emits to browser (user-session, token in query).
  Don't try to point a browser directly at u-d-b's SSE; auth model
  doesn't fit.
- **Test DB needs pgvector.** The rotation tests use it; the local
  Postgres container has it but a bare `createdb` doesn't. Most of
  Move 1 was validated via manual smoke against the running stack
  rather than the test DB (skipif markers on the rotation suite).
- **Two Docker rebuild gotchas observed.** (1) `docker compose up -d
  --build <service>` doesn't always re-create the container — use
  `--force-recreate` when you need the new code to actually run.
  (2) `docker exec <api> python -c "..."` will fail with
  `psycopg2.OperationalError` unless you read `DATABASE_URL` from
  the container's environment, not your shell's.
- **CC user-level filter is JWT-subject based.** No suite identity
  yet — Move 4 will introduce that. For now, mentorforge's users
  and CC's users are different tables; a user "the same person"
  in both apps has two different `sub` values.

## Carryovers (open / parked)

- **u-d-b `feat/fleet-events-move-3-round-1` (PR #2133)** — open.
- **CC `feat/drafts-live-events` (PR #15)** — open.
- **6 fleet-event back-prop PRs** — open, listed above.
- **Service-token auth for `app_slug`** (carryover from 1128 option A) — top of next-session queue.
- **ai-content-studio#2** — Docker foundation PR. Back burner.
- **24-7-ai-global** — Next.js, not yet Dockerized.
- **context-kit doctor floor:** `10 OK / 2 warnings` (both upstream).

## Session 1130 — Rigby-ordered recommendations

1. **Move 3 Round 2: replay + per-user filter at u-d-b.** The MLC
   shipped this session works while connected; reconnection
   currently drops events. Replay endpoint + `Last-Event-ID` would
   close the gap and unlock confident production use.
2. **Service-token auth for `app_slug`** (carryover). Routing
   control is a security boundary now, not a hint.
3. **FleetEvent retention.** Quick win — borrow Move 2 R2's pattern.
4. **Wire SSE into one other fleet app.** mentorforge is the
   natural pick (lesson generation has the same "long-running task
   you want to watch live" shape as draft generation).
5. **FC-path hint bias** (Phase 2D, carryover). Independent of the
   above; can land alongside.

Brief Rigby with the replay query shape before implementing
Move 3 R2; she'll want to lock event_id ordering semantics
(timestamp tiebreak, gap-detection rules) up front.
