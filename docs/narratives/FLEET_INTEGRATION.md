---
title: "Fleet Integration — narrative (batch M)"
status: draft (batch M of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/multi-repo-management.md
  - docs/topics/fleet-doc-verifier-rollout.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to multi-repo-management topic doc + MEMORY.md fleet arc notes for Sessions 1117/1119/1125/1126/1129/1130/1131-1133)
provenance_note: u-d-b became the brain bridge for a fleet of laptop-local sibling apps (signal-studio, mentorforge, pitchdeckforge, contract-concierge, sellerpilot, dealflowtracker, compliancesentinel). This narrative covers what the fleet is, how it talks to u-d-b, and why HMAC + canonical env are the security primitives. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f). 7 fleet apps + u-d-b itself; fleet-net Docker network; ~50 lines of brain_client.py per app.
---

# Fleet Integration

> u-d-b became a service. Seven sibling FastAPI+React apps
> live in their own repos, run in Docker on shared
> `fleet-net`, and HMAC-sign every call back to u-d-b for
> PA chat + agent dispatch + corpus retrieval. This
> narrative covers what the fleet is, how it authenticates,
> and what footguns are documented in memory.

---

## 1. What this is

The fleet is seven laptop-local sibling apps that consume
u-d-b as a service. Each app:

- Has its own repo (separate from u-d-b).
- Is Dockerized as a FastAPI+React pair.
- Runs on the shared `fleet-net` Docker network.
- Has a ~50-line `brain_client.py` that wraps PA chat calls
  to u-d-b.
- HMAC-signs every PA call with canonical
  `FLEET_APP_SLUG / KEY_ID / SERVICE_SECRET` env vars.
- Owns its own domain UI but delegates AI work back to u-d-b.

The seven apps:
- **signal-studio** — signal intelligence vertical (signal
  clusters, judge stats, action cards)
- **mentorforge** — mentoring / coaching vertical
- **pitchdeckforge** — pitch deck generation
- **contract-concierge** — contract review / drafting
- **sellerpilot** — sales / CRM vertical
- **dealflowtracker** — deal flow tracking
- **compliancesentinel** — compliance + regulatory

Plus u-d-b itself as the brain. Eight processes total on
`fleet-net` (per memory `project_session_1125_docker_fleet_brain_bridge.md`).

This is the technical layer of the 24/7 Global AI strategy
(narrative N): u-d-b is the shared core; the fleet apps are
the vertical-specific front-ends.

The most operationally important fact is **the HMAC sign-key
footgun**: fleet apps must sign with
`sha256(raw_secret).hexdigest()`, not the raw secret.
`FleetServiceKey.secret_hash` stores the hex digest. Wrong
key → 401 `signature_mismatch`. This is in memory as
`feedback_fleet_hmac_sign_with_secret_hash.md` because it
was discovered the hard way.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **Fleet** | The collection of laptop-local sibling apps consuming u-d-b as a service. Seven currently: signal-studio, mentorforge, pitchdeckforge, contract-concierge, sellerpilot, dealflowtracker, compliancesentinel. |
| **`fleet-net`** | The Docker network all fleet containers join. Created by `~/development/infra/make up`. Containers communicate by service name within the network. |
| **`~/development/infra/`** | The private repo that orchestrates the fleet. `make up` brings up all 7 Docker apps; `make all` adds u-d-b natively (daphne + celery); `make status` reports what's running. |
| **`brain_client.py`** | The ~50-line client each fleet app ships. Wraps `POST /api/pa/chat/` to u-d-b. Handles auth, retries, timeout. Reference impl: `contract-concierge/backend/app/fleet_signer.py:141`. |
| **`FleetServiceKey`** | The u-d-b model row representing an authorized fleet app. Carries `app_slug`, `key_id`, `secret_hash` (hex digest of `sha256(raw_secret)`). |
| **HMAC sign-key footgun** | The sign key for HMAC verification is `sha256(raw_secret).hexdigest()`, **not** the raw secret. u-d-b stores the hex digest; signs with the same digest on the verify side. A fleet app signing with the raw secret will produce a wrong signature → 401 `signature_mismatch`. Memory: `feedback_fleet_hmac_sign_with_secret_hash.md`. |
| **Canonical fleet env vars** | `FLEET_APP_SLUG` (which app, e.g., `signal-studio`), `KEY_ID` (the FleetServiceKey row's key_id), `SERVICE_SECRET` (the raw secret — never sent over the wire; only used to compute the HMAC sign-key). All three required for every fleet app. |
| **PA-chat audit table** | u-d-b model. Every PA call records auth posture, fleet origin, validation result. Currently **warn-only mode** (per Sessions 1131-1133 arc). Reject-mode flip queued on ≥ 3 days clean telemetry. |
| **FleetEvent** | The fleet event-stream row (Session 1129 + 1130). Carries `seq` (BIGSERIAL monotonic, Session 1130), `created_at`, payload, app origin. Used for cross-app SSE event delivery. TTL: 30 days default (`FLEET_EVENT_RETENTION_DAYS`). Hard-delete at 2:25 AM daily. |
| **`GET /api/fleet/events/?since=<seq>&limit=<n>`** | The replay endpoint (Session 1130). Exclusive cursor; returns `next_since` + `has_more`. Used by reconnecting clients to replay missed events. |
| **`Last-Event-ID` SSE header** | The reconnect mechanism. Accepted best-effort with 200-event cap. If the cap is exceeded, `stream.replay_truncated` sentinel event is sent to tell the client to drain via `/api/fleet/events/?since=...`. |
| **Brain bridge endpoint** | The pattern each fleet app implements: a FastAPI route that takes a user message, calls `brain_client.py` to relay to u-d-b's PA, and returns the PA's response. Adds the fleet-specific context (workspace_id, app_slug, etc.). |
| **Fleet routing (Phase 1, Session 1126)** | `config/fleet_agent_routing.json` + `core/services/fleet_routing.py:resolve()`. PA chat accepts/emits `routing` block. Metadata-only in Phase 1 (Phase 2 wires `resolved_agent` into PA's deliberation router + 7 fleet brain_clients). |
| **fleet_health_rollup** | Mgmt command from Session 1126. Aggregates Docker container status + endpoint healthchecks across all fleet apps. Surfaced via PA tool `fleet_health`. |
| **Move 3 (the event-stream arc)** | Session 1129 = R1 (DB-first FleetEvent + Redis pub/sub + 2-hop SSE fan-out). Session 1130 = R2 (monotonic seq, replay with cursor, TTL, `Last-Event-ID` reconnect). Each piece is the next layer of "events survive disconnects." |
| **Signal-studio Step 3** | The first fleet app to exercise the full pipeline (signal pipeline + judge stats + action cards). Reference impl for the canonical fleet pattern. |
| **`FleetPaidInterest`** | F1 paid-interest demand-gate (Session 1138). Used to gate signal-studio access on the platform-side demand model. |
| **Reject-mode audit** | The future state of the PA-chat audit table. Currently warn-only (logs but doesn't block). Reject-mode would 401 any mis-signed fleet call. Queued for after ≥ 3 days clean telemetry. |
| **Per-repo backfill (Session 1131-1133)** | All 7 fleet repos updated in parallel to use canonical `FLEET_APP_SLUG / KEY_ID / SERVICE_SECRET` env. Six byte-identical changes; only `DEFAULT_APP_SLUG` differs per repo. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Session 1117 — local portfolio Rigby grounding (the vision)** | The framing of "Rigby is the brain bridge for a fleet of laptop-local apps." Established the pattern: each app has its own corpus + UI, but delegates AI work to u-d-b. Corpus + fleet-net + consult_engine bridge first pass shipped end-to-end. Was queued as the "headline project for the next session Chris flags" for months. | The platform's value isn't in one Django monorepo; it's in the AI brain that can be reused across vertical apps. Each fleet app is cheaper to build than rebuilding the brain inside it. The shared brain = u-d-b. | Vision documented; first proof case (corpus + bridge) shipped. The "fleet of repos consuming u-d-b" model crystallized. | **Active concept** — the entire fleet arc that follows is the operationalization of this vision. | Memory: `project_local_portfolio_rigby_grounding.md`; `docs/handoffs/SESSION_1117_LOCAL_PORTFOLIO_GROUNDING_BRIDGE.md` |
| **Session 1119 — Multi-repo v0 (character-os first proof)** | `ProjectWorkspace` model exists for any repo other than u-d-b itself. `config/external_repos/<repo_id>.json` defines a repo profile. 3 mgmt commands: `register_external_repo`, `refresh_repo_context`, `survey_external_repo`. Workspace category `repo_profile` / `repo_snapshot` / `repo_survey` for pinned deliverables. Character-os was the first proof case (NOT u-d-b — Character-os is separate). | The platform needed to manage multiple repos as projects. The existing `ProjectWorkspace` "SKIN layer" model already had `root_path`, `tech_stack`, `entry_points`, `protected_paths`, permissions — perfect fit. No new API endpoints; existing primitives. | Multi-repo v0 in production. Character-os onboarded. Pattern reusable. | **Active** — `register_external_repo` etc. are still the canonical onboarding path. | `docs/topics/multi-repo-management.md`; `docs/handoffs/SESSION_1119_MULTI_REPO_V0.md` |
| **Session 1125 — Docker fleet (the 7 apps)** | ~25 PRs across 9 repos. Dockerized 7 FastAPI+React fleet apps on shared `fleet-net`: mentorforge, pitchdeckforge, contract-concierge, sellerpilot, dealflowtracker, compliancesentinel, signal-studio. Brain bridge PoC in mentorforge#12, then back-prop to other 6: ~50 lines `brain_client.py` + 1 endpoint + 1 env block + frontend page per app. Defang sweep `POSTGRES_PASSWORD=<repo>` → `change-me-in-production` across all 6 (GitGuardian-clean). Signal-studio backend port 8080→8007 (collided with u-d-b frontend). u-d-b PGDATA env fix (#2121) — data was in `/var/lib/postgresql/data/pgdata` subdir, missing env caused crash-loop. End-to-end verified ~4.7–9 s round-trip per app. `infra/` made its own private repo with `make up` launcher. **Two Docker-Desktop gotchas:** multi-network containers break host-port forwarding; don't run parallel `docker compose build` — daemon hangs. | The 7 apps needed to be runnable locally without polluting u-d-b's monolith. Docker + fleet-net let each app keep its own backend / frontend / database while sharing the u-d-b brain. | 7 Dockerized fleet apps in production locally. Round-trip latency tractable. Pattern reusable for adding new fleet apps. | **Active** — fleet-net + the 7 apps are the current state. | Memory: `project_session_1125_docker_fleet_brain_bridge.md` |
| **Session 1126 — fleet runtime + health rollup + routing Phase 1** | Docker runtime metadata added to each fleet repo profile (web/api URLs, brain bridge endpoint, fleet-net hostnames, healthchecks). `fleet_health_rollup` mgmt command + `fleet_health` PA tool. Phase 1 of agent routing: `config/fleet_agent_routing.json` + `core/services/fleet_routing.py:resolve()`. PA chat accepts/emits `routing` block. METADATA pipeline only — Phase 2 plumbs `resolved_agent` into PA's deliberation router + 7 fleet brain_clients. | The fleet was running but u-d-b had no view of "which apps are healthy?" or "which agent should serve this app's request?" Phase 1 added observability (health rollup) and metadata for routing (no enforcement yet). | Fleet health visible via PA. Routing metadata flows through PA chat. Phase 2 wiring queued. | **Active Phase 1** — Phase 2 not yet shipped. | Memory: `project_session_1126_fleet_runtime_brain_plumbing.md` |
| **Session 1129 — fleet auth + artifacts + SSE event stream (Move 3 R1)** | (Move 1) HMAC-signed identity, 11 deny codes, Redis nonce replay protection, audit log. (Move 2 R1+R2) Push/pull/list artifacts with TTL retention. Contract Concierge AI Draft Library flagship demo end-to-end. (Move 3 R1) DB-first `FleetEvent` + Redis pub/sub + 2-hop SSE fan-out u-d-b → CC backend per-user filter → browser EventSource. 17+ PRs across u-d-b + 7 fleet repos. | The fleet needed auth (so u-d-b knows which app is calling and can refuse impostors), artifact exchange (so apps can send/receive files), and event streaming (so apps can react to u-d-b state changes in real time). Three concurrent shipments. | Full HMAC auth model in place. Artifacts work. SSE event-stream proof case shipped (Contract Concierge AI Draft Library). | **Active.** | Memory: `project_session_1129_fleet_auth_artifacts_events.md`; `docs/handoffs/SESSION_1129_*.md` |
| **Session 1130 — Move 3 R2 (replay + seq + TTL)** | Monotonic `seq` BIGSERIAL on `FleetEvent` (migration 0346 backfilled 12 rows in created_at order). `GET /api/fleet/events/?since=<seq>&limit=<n>` exclusive cursor + `next_since` + `has_more`. SSE `id:` field carries `seq` not UUID. `Last-Event-ID` accepted best-effort with 200-event cap + `stream.replay_truncated` sentinel. `FleetEvent` TTL (`FLEET_EVENT_RETENTION_DAYS` default 30, hard-delete, 2:25 AM). `brain_events.py` canonical rewrite in Character OS: drain-then-subscribe pattern with `last_seq` cursor across reconnects, MAX_REPLAY_PAGES=50 bound. 6 byte-identical back-props (only `DEFAULT_APP_SLUG` differs). 8 PRs (u-d-b#2135 + CC#16 + 6 sibling). | Move 3 R1 worked but tab-switch silently dropped events (no replay). R2 closed the reconnect-resilience gap with monotonic sequence + cursor-based replay + TTL hard-delete. | Events survive tab-switches. Reconnecting clients drain missed events without manual intervention. **New gotcha** captured: Django 5 `db_default` mandatory for DB-managed defaults (sequences, `nextval`, `gen_random_uuid()`); `null=True` alone trips NOT NULL. | **Active.** | Memory: `project_session_1130_fleet_events_move3_r2.md`; `feedback_db_default_for_db_managed_columns.md` |
| **Sessions 1131-1133 arc — signal-studio vertical slice + PA-chat audit + fleet HMAC back-prop** | 14 PRs merged in 3 sessions. signal-studio went from 5 hardcoded seeds to 131 real clusters + Top-10 daily curated set + live SSE refresh. **PA-chat audit table** in u-d-b records every call's auth posture (warn-only, no enforcement). **All 7 fleet repos** now HMAC-sign PA chat via canonical `FLEET_APP_SLUG / KEY_ID / SERVICE_SECRET` env. (Y) reject-mode flip queued for 1134 gated on ≥ 3 days clean audit telemetry post-merge. (A) action-card pre-gen queued as visible-feature alternative. | The fleet had HMAC infrastructure (Session 1129) but only some apps used it consistently. The 1131-1133 arc back-propagated the canonical auth pattern to all 7 fleet repos and introduced the audit table that lets u-d-b watch for misconfigured fleet calls without blocking. **The HMAC sign-key footgun** was captured to memory here (sha256(raw_secret).hexdigest, not raw secret). | All 7 fleet apps sign PA chat consistently. Audit table is warm in warn-mode. Reject-mode flip pending. | **Active warn-mode.** Reject-mode flip queued (not yet enabled). | Memory: `project_session_1131_1133_arc.md`; `feedback_fleet_hmac_sign_with_secret_hash.md` |
| **Session 1138 — F1 paid-interest demand-gate (signal-studio)** | `FleetPaidInterest` model + HMAC POST endpoint + `paid_interest_status` PA tool. Used to gate signal-studio access on platform-side demand model. Part of the broader Atlas Phase 1 work (cross-ref narrative N). | The 24/7 Global AI strategy (narrative N) requires demand-gated access for new verticals. F1 is the first paid-interest-gated feature; the pattern is reusable for SS / SP / CS Stripe wiring. | Demand-gate live. Pattern proven. | **Active.** | Memory entry on Session 1138 (referenced in `00-START-NEXT-SESSION.md` history) |

---

## 4. What came of it

### Wins

- **u-d-b is a service, not just a monolith.** Seven
  vertical apps consume it. Each app stays small;
  u-d-b's accumulated capability is amortized across
  all of them.
- **HMAC auth + audit catches misconfigured fleet
  calls.** Warn-mode means the audit logs without
  blocking — a misconfigured fleet app can still talk
  to u-d-b but its calls are flagged for review.
  Reject-mode flip queued.
- **Replay-resilient event stream.** Move 3 R2's
  monotonic seq + cursor-based replay + TTL means tab
  switches don't silently drop events.
- **Pattern reusable.** Adding an 8th fleet app would
  be `brain_client.py` + 1 endpoint + 1 env block + a
  FleetServiceKey row. ~1 day of work, not a re-
  architecture.
- **Docker network isolation.** Each fleet app's
  database / Redis / backend is per-container. Only
  the brain (u-d-b) is shared, via HMAC-authenticated
  calls.
- **Memory captures the footguns.** `feedback_fleet_hmac_sign_with_secret_hash.md`
  + `feedback_db_default_for_db_managed_columns.md`
  + Docker Desktop gotchas (multi-network host-port
  forwarding; parallel `docker compose build` hangs)
  are all in memory.
- **Fleet routing Phase 1 = metadata-first.** The
  pattern of "ship observability before action"
  (Session 1126) avoids the "we made A do B and broke
  C" failure mode.

### Tradeoffs

- **HMAC sign-key footgun is real.** Wrong key →
  401 with no helpful error message. Memory entry
  exists; new fleet integrators still hit it.
- **Reject-mode audit not yet active.** Warn-only is
  the current state. Misconfigured fleet apps can
  still talk to u-d-b.
- **Docker Desktop on macOS is fragile.** Two gotchas
  documented (multi-network host-port forwarding;
  parallel `docker compose build`). Not Linux problems;
  developer-laptop problems.
- **Fleet routing Phase 2 not yet shipped.** Routing
  metadata flows in PA chat (Phase 1) but isn't
  enforced — `resolved_agent` doesn't change the PA's
  actual deliberation router behavior.
- **One u-d-b = single point of failure.** All 7
  fleet apps go down if u-d-b goes down. No
  redundancy in the brain layer.
- **Round-trip latency ~5–10 s per fleet → u-d-b PA
  call.** Acceptable for chat workflows; not
  acceptable for real-time UI updates. SSE event
  stream is the mitigation for "tell me when state
  changes" but not for "tell me right now."
- **Fleet apps are laptop-local.** No production
  deployment of the fleet outside Chris's laptop yet.
  Production deployment would require fleet-net
  equivalent in a cloud environment.
- **Per-app secret rotation = manual.** No automated
  rotation of `SERVICE_SECRET` across the 7 apps.

### Follow-on systems enabled

- **PA (D)** — `governance_tool`, `intelligence_tool`,
  every fleet app calls through PA.
- **24/7 Global AI strategy (N)** — fleet integration
  is the technical layer beneath the brand / vertical /
  pricing strategy.
- **Spokesperson corpus + Character OS bridge (O)** —
  Character OS was the first proof case for multi-repo
  v0 (Session 1119); the canonical fleet pattern is
  the foundation.
- **Knowledge + RAG + Memory (H)** — `search_docs` +
  `kb_tool` are PA tools the fleet can consume.

---

## 5. Current state snapshot

> Source: `docs/topics/multi-repo-management.md`,
> MEMORY.md fleet arc notes, PLATFORM_INVENTORY 2026-05-25.

**Fleet apps (7).**
- **signal-studio** — signal intelligence vertical
- **mentorforge** — mentoring / coaching
- **pitchdeckforge** — pitch deck generation
- **contract-concierge** — contract review
- **sellerpilot** — sales / CRM
- **dealflowtracker** — deal flow
- **compliancesentinel** — compliance / regulatory

Plus u-d-b as the brain.

**Docker network.** `fleet-net`. Launcher:
`~/development/infra/make up` (brings up 7 apps);
`make all` (adds u-d-b natively); `make status`.

**Auth model.** HMAC. Sign-key =
`sha256(raw_secret).hexdigest()` — **not** raw secret.
Stored as `FleetServiceKey.secret_hash`. Required env:
`FLEET_APP_SLUG`, `KEY_ID`, `SERVICE_SECRET`. 11 deny
codes documented.

**PA-chat audit.** Warn-only mode. Every call records
auth posture + fleet origin + validation result.
Reject-mode flip queued (≥ 3 days clean telemetry).

**Event stream.**
- `FleetEvent` model with monotonic `seq` BIGSERIAL.
- `GET /api/fleet/events/?since=<seq>&limit=<n>` —
  exclusive cursor, `next_since`, `has_more`.
- SSE `id:` field carries `seq`.
- `Last-Event-ID` accepted best-effort with 200-event
  cap.
- `stream.replay_truncated` sentinel when cap exceeded.
- TTL: 30 days (`FLEET_EVENT_RETENTION_DAYS`).
  Hard-delete daily 2:25 AM.

**Brain bridge.** Each fleet app: ~50 lines
`brain_client.py` wrapping `POST /api/pa/chat/` to
u-d-b. Adds workspace_id + app_slug + tools context.

**Fleet routing.** Phase 1 (Session 1126). Metadata
flows in PA chat `routing` block. Phase 2
(`resolved_agent` enforcement) pending.

**`infra/` launcher repo.** `~/development/infra/`
(private). `make up`, `make all`, `make status`.

**Demand-gate.** `FleetPaidInterest` (Session 1138).
`paid_interest_status` PA tool.

**Where to look when something stops working.**
- 401 `signature_mismatch` from u-d-b → wrong sign
  key. Use `hashlib.sha256(raw_secret.encode()).hexdigest()`,
  not the raw secret. Memory:
  `feedback_fleet_hmac_sign_with_secret_hash.md`.
- Fleet app can't reach u-d-b on `fleet-net` → check
  `make status`; check Docker network has both
  containers attached.
- Tab-switch lost events → SSE replay should pick up
  via `Last-Event-ID`; if not, check
  `GET /api/fleet/events/?since=<last_seq>`. If `seq`
  is 0, the client cursor is stale — query Postgres
  directly for `MAX(seq)` to confirm events exist.
- New fleet repo not signing → check
  `FLEET_APP_SLUG / KEY_ID / SERVICE_SECRET` env
  populated; `FleetServiceKey` row exists in u-d-b
  with matching `key_id`; `secret_hash` matches
  `sha256(SERVICE_SECRET).hexdigest()`.
- `fleet_health` PA tool shows red → use
  `fleet_health_rollup` mgmt command for the detailed
  view; check Docker container status + healthcheck
  endpoint.
- Docker Desktop hang → don't run parallel `docker
  compose build`. Memory: documented in Session 1125
  notes.
- Host-port forwarding broken after `make up` → multi-
  network container issue on Docker Desktop. Memory:
  Session 1125 notes.

---

## 6. Open questions / unknown outcomes

- **Reject-mode flip timing.** *Known:* queued for
  ≥ 3 days clean telemetry. *Unknown:* current
  telemetry status. Was queued for Session 1134.
- **Fleet routing Phase 2.** *Known:* Phase 1
  metadata flows. *Unknown:* whether Phase 2
  (enforcement) has started or is scheduled.
- **Production deployment of the fleet.** *Known:*
  laptop-local only. *Unknown:* whether production
  deployment is on any roadmap; what the cloud
  equivalent of `fleet-net` would be.
- **Adding an 8th fleet app.** *Known:* pattern is
  established. *Unknown:* what app, if any, is
  queued next.
- **Cross-fleet event consumption.** *Known:* SSE
  fan-out works one-way (u-d-b → fleet app). *Unknown:*
  whether any pattern exists for app A to consume
  events from app B (probably no — would require
  routing through u-d-b first).
- **u-d-b downtime impact.** *Known:* single point of
  failure. *Unknown:* whether any fleet app has graceful
  degradation when u-d-b is unavailable, or whether all
  7 just stop working.
- **Per-app secret rotation.** *Known:* manual.
  *Unknown:* whether automated rotation is on any
  roadmap.
- **Round-trip latency reduction.** *Known:* ~5–10 s
  per call. *Inferred:* dominated by PA's Celery-async
  pipeline. *Unknown:* whether any latency reduction
  is feasible without changing the PA's architecture.
- **Audit table query surface.** *Known:* audit table
  is warm. *Unknown:* whether there's a PA tool or
  dashboard surface to query it — or whether `psql` is
  the only way to inspect.

---

## 7. Source index

### Primary doc sources

- `docs/topics/multi-repo-management.md` — Multi-repo
  v0 (Session 1119).
- `docs/topics/fleet-doc-verifier-rollout.md` —
  companion fleet-net work.
- `docs/topics/active-module-ownership-map.md` —
  per-app ownership.
- `docs/PLATFORM_INVENTORY.md` — model counts.
- `docs/narratives/PERSONAL_ASSISTANT.md` (D) —
  PA-chat audit + fleet HMAC + search_docs cross-refs.

### Named session handoffs cited above

- `docs/handoffs/SESSION_1117_LOCAL_PORTFOLIO_GROUNDING_BRIDGE.md`
  — vision + first proof case.
- `docs/handoffs/SESSION_1119_MULTI_REPO_V0.md` —
  multi-repo v0.
- Memory: `project_session_1125_docker_fleet_brain_bridge.md`
- Memory: `project_session_1126_fleet_runtime_brain_plumbing.md`
- Memory: `project_session_1129_fleet_auth_artifacts_events.md`
- Memory: `project_session_1130_fleet_events_move3_r2.md`
- Memory: `project_session_1131_1133_arc.md`
- MEMORY.md feedback entries:
  `feedback_fleet_hmac_sign_with_secret_hash.md`,
  `feedback_db_default_for_db_managed_columns.md`,
  `feedback_docker_force_recreate.md`.

### Code anchors

- `core/services/fleet_routing.py` — `resolve()`.
- `core/services/fleet_signer.py` (or similar) — HMAC
  signing.
- `core.models` — `FleetServiceKey`, `FleetEvent`,
  `FleetPaidInterest`.
- `core/management/commands/fleet_health_rollup.py` —
  health aggregation.
- `core/management/commands/register_external_repo.py` —
  multi-repo registration.
- `config/external_repos/*.json` — per-repo profiles.
- `config/fleet_agent_routing.json` — Phase 1 routing
  metadata.
- Reference fleet impl:
  `contract-concierge/backend/app/fleet_signer.py:141`.

### Verification commands

- `python manage.py generate_platform_inventory` —
  inventory.
- `python manage.py fleet_health_rollup` — fleet
  health.
- `python manage.py register_external_repo --repo
  <repo_id>` — onboard new app.
- PA tool: `fleet_health` — chat-time health check.
- PA tool: `paid_interest_status` — demand-gate
  status.
- `~/development/infra/make up && make status` —
  fleet up + status.
