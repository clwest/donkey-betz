---
title: "Session 1132 — Curated tab live refresh + PA-chat warn-only audit"
date: 2026-05-22
status: active
session: 1132
previous_handoff: SESSION_1131_PHASE_2_SIGNAL_CURATOR.md
---

# Session 1132 — Real-time polish + security visibility

> **Read this if** you want to know how the Curated tab learns about
> new curator runs without polling, why the original "FleetServiceToken
> bearer" design got dropped mid-session in favor of an audit layer
> over existing HMAC infra, or what the rollout queries look like
> before flipping PA-chat enforcement to reject mode.

## TL;DR

Session 1131 closed Phase 1 + Phase 2. Session 1132 shipped Rigby's
locked **C (primary)** and **B-scaffold (stretch)** — both delivered
end-to-end in one session.

| What | Where |
|---|---|
| **(C) Curated tab live refresh** | signal-studio PR [#14](https://github.com/clwest/signal-studio/pull/14) |
| **(B-scaffold) PA-chat warn-only audit** | u-d-b PR [#2142](https://github.com/clwest/donkey-betz-platform/pull/2142) |

End-to-end smoke: trigger `curate_and_emit()` on u-d-b while
`localhost:5173` shows the Curated tab. Within ~5s the "🟢 New
curated set — refresh" pill appears in the corner. Click it → the
list refetches with the new snapshot's top 10.

Separate end-to-end: every `/api/pa/chat/` call now writes a
`FleetPAChatAuditRow` recording the actual auth posture
(`fleet_signature` / `bearer_only` / `session_user` / etc.) plus
whether the body's `context.app_slug` matches the verified identity.
**No enforcement** — purely visibility before flipping the existing
Session 1129 Move 1 gate to reject mode.

## The (C) shape — Curated tab live refresh

### Architecture (2-hop fan-out, Phase 1 lock preserved)

```
u-d-b SignalCuratorAgent
  └─ emit_event(signal.curated_published) ──┐
                                            ↓ (HTTPS SSE via brain_events)
signal-studio backend
  └─ signal_ingest._apply_curated_snapshot
      └─ notify_curated_refreshed (in-memory broadcast)
                                            ↓
signal-studio backend
  └─ /api/signals/events (new SSE endpoint)
                                            ↓
browser EventSource
  └─ "🟢 New curated set — refresh" pill
```

### Why in-memory broadcast (not Redis pub/sub) inside signal-studio

signal-studio runs one uvicorn process per container. An
`asyncio.Queue` per subscriber is the simplest correct primitive
for single-process broadcast. If signal-studio ever scales to
multi-process / multi-container, swap `notify_curated_refreshed`
for a Redis publish + change each subscriber's queue to a Redis
subscribe iterator. The browser SSE contract stays identical;
only the broadcast plumbing changes.

### What ships in PR #14

- `backend/app/browser_events.py` (new): in-memory pub/sub
  primitive, `notify_curated_refreshed(snapshot_id, top_n)` sync
  helper, async `curated_event_stream()` generator with 15s
  keep-alive comments and per-subscriber queue cap of 32
- `backend/app/signal_ingest.py`: `_apply_curated_snapshot` calls
  `notify_curated_refreshed` after commit
- `backend/app/main.py`: `GET /api/signals/events` StreamingResponse
  with proxy-friendly headers (`Cache-Control: no-cache`,
  `X-Accel-Buffering: no`)
- `frontend/src/App.tsx`: EventSource lifecycle bound to the
  Curated tab being active; "🟢 New curated set — refresh" pill
  renders when `pendingSnapshotId !== curatedSnapshotId`

### End-to-end latency

~5s from `curate_and_emit()` call to browser EventSource receipt.
Hop chain: u-d-b shell → emit_event → Redis publish → daphne SSE
stream → signal-studio brain_events consumer → dispatch_envelope
→ _apply_curated_snapshot → notify_curated_refreshed → browser SSE
endpoint → browser.

Acceptable for daily curation. If real-time matters more later,
collapse the brain_events.py hop by having u-d-b's emit publish
directly to signal-studio's Redis channel.

## The (B-scaffold) pivot — saved off the table

### What got dropped

The original (B) plan called for a new bearer-token model
(`FleetServiceToken`), a mint command, and a parallel auth scheme
on top of the existing HMAC signing. Halfway through implementation,
tracing the call path revealed:

- `unified_pa_chat`'s `@authentication_classes` already includes
  `FleetSignatureAuthentication`
- The Session 1129 Move 1 gate at `views_personal_assistant.py:340-360`
  ALREADY strips routing claims when `fleet_identity` is None
- signal-studio's `brain_client.py:223` already passes
  `fleet_path="/api/pa/chat/"` to `_http_request`, which auto-signs
  when `FLEET_*` env vars are present
- The OTHER 6 fleet repos use byte-identical `brain_client` code;
  they just need `FLEET_*` env vars populated

So the actual gap collapses from "add a second auth scheme" to
"make fleet apps actually use the signing they already have."
Briefed Rigby; she locked the pivot. Result: ~70% less code,
no parallel auth precedence rules, and we use the infrastructure
she already approved in 1129.

### What ships in PR #2142

- **Migration 0349**: `FleetPAChatAuditRow` table with `auth_mode`
  enum (`fleet_signature` / `bearer_only` / `session_user` /
  `api_user_token` / `anonymous`), `has_fleet_identity` bool,
  `verified_app_slug`, `claimed_app_slug`, nullable `match`,
  request metadata. Composite indexes for the two rollout queries
  below
- `core/services/fleet_pa_chat_audit.py` (new): `write_pa_chat_audit()`
  helper. Reads the `Authorization` header DIRECTLY for `auth_mode`
  classification (Django's session middleware can create anonymous
  sessions that fool DRF's `successful_authenticator`-based check
  — discovered mid-implementation)
- `core/views_personal_assistant.py`: calls audit helper at top of
  `unified_pa_chat`, wrapped in try/except (audit can never block
  a chat)
- 22 new unit tests covering classifier edge cases + claim
  extraction + IP extraction

### Smoke verified (4 scenarios)

| Scenario | auth_mode | has_id | verified | claimed | match |
|---|---|---|---|---|---|
| `pa_local.sh` (Token bearer) | `bearer_only` | False | `''` | `''` | NULL |
| Bearer + body claim `contract-concierge` (impersonation attempt) | `bearer_only` | False | `''` | `'contract-concierge'` | NULL |
| signal-studio brain bridge (HMAC signed) | `fleet_signature` | True | `'signal-studio'` | `'signal-studio'` | True |

The middle row is the security signal — anyone holding the shared
`BRAIN_TOKEN` can currently claim any `app_slug` they want in the
request body. The audit table will quantify how often this happens
across normal traffic; once it shows clean (signed + matching)
telemetry for a few days, flipping the Session 1129 Move 1 gate to
reject mode becomes a small config change.

### Pre-flip-enforcement rollout queries

Drop these into a dashboard or run them ad-hoc:

```sql
-- "How many bearer-only PA chat calls in last 24h, by claimed app_slug?"
SELECT claimed_app_slug, COUNT(*)
FROM core_fleetpachatauditrow
WHERE auth_mode = 'bearer_only'
  AND claimed_app_slug != ''
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY claimed_app_slug;

-- "How many mismatches (claimed != verified) in last 24h?"
SELECT verified_app_slug, claimed_app_slug, COUNT(*)
FROM core_fleetpachatauditrow
WHERE match = FALSE
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY verified_app_slug, claimed_app_slug;
```

When both queries return 0 for a few days of normal traffic, reject
mode is safe to flip. The first query is the canonical "rollout
progress" measure — every fleet app that flips from bearer-only to
HMAC drops from the result set.

## Discoveries (not new memory rules — already captured)

### Django session middleware can satisfy SessionAuthentication

DRF's `successful_authenticator` showed `SessionAuthentication`
even for curl requests with `Authorization: Token ...` and no
cookies. Django's session middleware was creating an anonymous
session for the request, which then satisfied SessionAuthentication's
"successful" check. Fix: read the `Authorization` header directly
in the classifier rather than trusting `successful_authenticator`.

### `request.fleet_identity` is a dict, not an ORM object

`FleetSignatureAuthentication` (since Session 1129) stores
`request.fleet_identity` as a dict of (`app_slug`, `key_id`,
`service_identity_id`, `request_id`, `verified_at`), NOT a
`FleetServiceIdentity` ORM row. Initially used `getattr` which
returned empty string for the dict; switched to `.get("app_slug")`.
First commit had this bug; smoke caught it before merge.

Both of these are documented inline in `fleet_pa_chat_audit.py` so
the next reader won't trip the same wires.

## Open carryovers (deferred again)

### Reject-mode flip in `unified_pa_chat`

The whole point of the audit table is to gate this flip on real
data. Not in scope for any session that doesn't have ≥3 days of
clean audit telemetry first.

### FLEET_* env var back-prop to 5 fleet repos

`contract-concierge` (1129) and `signal-studio` (Phase 1) already
have `FLEET_KEY_ID` + `FLEET_SERVICE_SECRET` in their container
env. The remaining 5 (`mentorforge`, `pitchdeckforge`,
`sellerpilot`, `dealflowtracker`, `compliancesentinel`) need them
provisioned (via `python manage.py provision_fleet_identity
--app-slug <name>`) and added to each repo's `.env` +
`docker-compose.yml`. Mechanical follow-up; can be one
ops-rollup PR or 5 small PRs.

After the back-prop, the audit table will start showing
`auth_mode=fleet_signature` rows for those apps too. That's the
prerequisite signal for the reject-mode flip.

### (A) Action-card pre-gen for curated

Still deferred per Rigby's forward note from Phase 1 close. When
greenlit: pre-generate u-d-b-side, include the actions in the
`signal.curated_published` payload (or `CuratedSignalEntry` child
rows). signal-studio becomes a renderer, not an LLM executor.

### Lower-priority cleanup

- **Evidence URL field** — both phases ship `url=""`. Cleanest path:
  enrichment agent adds URLs to `sample_signals`.
- **Semantic category** — `pattern_type` doubling as category is
  the honest placeholder. Future enrichment agent can map clusters
  to real semantic categories.
- **`docs/SERVICES.md` drift** — header says 320 service files;
  reality after 1132 is 336 (added `browser_events.py` on signal-studio
  side and `fleet_pa_chat_audit.py` on u-d-b side, plus the two
  Phase 1 + Phase 2 services).

## Recommended Rigby coordination for next session

Three credible directions; brief her with Chris's appetite + which
audit data has accumulated:

### (X) FLEET_* env back-prop to 5 fleet repos
- ~1 session, mostly mechanical
- Unlocks the reject-mode flip prerequisite
- Five repos: mentorforge, pitchdeckforge, sellerpilot,
  dealflowtracker, compliancesentinel. Each gets
  `provision_fleet_identity --app-slug <name>` + env var update +
  recreate container
- Lowest-risk, highest-readiness-for-next-step path

### (A) Action-card pre-generation for curated
- ~1 session, real LLM cost (~10 calls/day per curator run)
- Visible UX win — Curated tab cards show instant action plans
- Rigby's preferred shape locked: u-d-b generates, payload-or-child
  rows, signal-studio renders

### (Y) Reject-mode flip in `unified_pa_chat`
- ONLY if (X) has been done AND audit table shows ≥3 days of
  clean (signed + matching) telemetry
- ~half a session of careful config + verification
- Lock from this session: the existing Move 1 gate is the
  enforcement point; flipping is just changing log-only to deny

My read: **(X) → (Y)** as a security-focused arc, **(A)** if Chris
wants a visible feature. The seven-PR stack still needs review +
merge regardless of which direction next session goes.

---

*Session 1132 closed 2026-05-22 evening.*
