---
title: "Session 1130 — Move 3 Round 2: SSE replay + monotonic seq + FleetEvent TTL"
date: 2026-05-22
status: active
session: 1130
previous_handoff: SESSION_1129_FLEET_BRAIN_AUTH_ARTIFACTS_EVENTS.md
---

# Session 1130 — Reconnect-resilience for the fleet event stream

> **Read this if** you want to know why FleetEvent rows now carry a
> monotonic `seq`, how the canonical replay endpoint
> (`GET /api/fleet/events/?since=…`) is supposed to be used, what
> drove the brain_events.py rewrite across all 7 fleet repos, or
> what Move 3 still has left to do.

## TL;DR

Session 1130 closed Rigby's top-ranked carryover from 1129 — **Move 3
Round 2** — and shipped the FleetEvent retention quick win alongside.
The fleet event stream is now reconnect-resilient: tab-switch, mobile
sleep, transient network loss, none of them silently drop events any
more. The contract used to be "live while connected, gap on
reconnect"; it's now "live + canonical replay drains the gap on every
reconnect."

| Move | What shipped | PRs |
|---|---|---|
| **3 R2 — monotonic seq + replay endpoint** | `core_fleetevent_seq` Postgres sequence, `seq` column backfilled across the 12 existing rows, replay endpoint with exclusive cursor + `next_since` + `has_more`, SSE `id:` now carries `seq` not UUID, `Last-Event-ID` accepted best-effort | u-d-b [#2135](https://github.com/clwest/donkey-betz-platform/pull/2135) |
| **3 R2 — brain_events.py replay-before-subscribe** | Canonical recovery: drain GET `?since=last_seq` until exhausted, then attach `/stream`. Tracks `last_seq` across the subscriber's lifetime. Bounded at 50 pages (~5000 events) per reconnect | contract-concierge [#16](https://github.com/clwest/contract-concierge/pull/16) (canonical) + 6 byte-identical back-props |
| **Option C — FleetEvent TTL** | `FLEET_EVENT_RETENTION_DAYS` (default 30), hard-delete (events are pure log, not work-product like artifacts), scheduled 2:25 AM MST to stagger off artifact cleanup at 2:10 | rolled into u-d-b [#2135](https://github.com/clwest/donkey-betz-platform/pull/2135) |

**8 PRs open, all carry the same `feature/fleet-events-move3-r2`
branch name across repos** for easy ref. Smoke confirmed end-to-end
by Chris on http://localhost:5175 — Test 1 (live event preserved)
and Test 2 (tab-switch-then-resume replays missed events) both pass.

## Rigby's four locks (conversation pa-d19c1674b936)

These are the design decisions she rejected/accepted before any code
landed. They show up in commit messages + comments throughout the PRs
so future drift is easy to detect.

1. **Ordering tiebreak.** Monotonic `BIGINT` Postgres sequence, **not**
   timestamp + uuid. `ORDER BY seq ASC`, no secondary sort needed.
   Cursor semantics: `since=<last_seq>` means *strictly greater than*.
   Why: timestamp + uuid is not deterministic under concurrency and
   makes replay edge cases painful.
2. **Gap detection on reconnect.** Strict replay of all events with
   `seq > last_seen_seq`, paged by `limit`. Client loops
   `GET /api/fleet/events/?since=…&limit=100` until fewer than
   `limit` returned, then attaches stream. Why: "fuzzy last N" is a
   band-aid that breaks under bursty traffic.
3. **Replay path.** Explicit `GET /api/fleet/events/?since=…` first,
   *then* subscribe to `/stream`. `Last-Event-ID` accepted as a
   best-effort convenience for the rare case of micro-disconnects.
   Why: it's simpler to reason about, works even if the stream server
   can't efficiently backfill, and avoids "silent partial replay"
   bugs. Avoids buffering huge backlogs inside the SSE handler.
4. **TTL.** 30 days default via `FLEET_EVENT_RETENTION_DAYS`. Separate
   cleanup job from artifacts (events ≠ artifacts). Hard-delete, not
   soft-delete (events have no FK protection and no retention-aware
   visibility rules).
5. **Freebie:** `since` is **exclusive**. Response includes
   `next_since` (last seq in this page) so the client doesn't have to
   re-parse the `events[]` array to advance the cursor.

## What landed where

### u-d-b ([#2135](https://github.com/clwest/donkey-betz-platform/pull/2135))

- `core/migrations/0346_fleetevent_seq.py` — creates `core_fleetevent_seq`
  sequence, adds `seq BIGINT` column, backfills the 12 existing rows
  in `created_at` order, attaches the sequence as DEFAULT + NOT NULL,
  flips `Meta.ordering` to `["seq"]`. Backfill uses `ROW_NUMBER() OVER
  (ORDER BY created_at, id)` so the assignment is deterministic.
- `core/models/fleet.py` — `FleetEvent.seq` field with
  `db_default=models.expressions.RawSQL("nextval('core_fleetevent_seq')")`.
  Django 5's `db_default` is what makes INSERTs omit the column so
  Postgres' DEFAULT actually fires. (Naïve `null=True` field passes
  NULL explicitly and trips the NOT NULL constraint — verified by
  initial IntegrityError before the field was updated.)
- `core/services/fleet_events.py` — Redis envelope now carries `seq`.
- `core/views_fleet_events.py`:
    - SSE `id:` field is `str(seq)` when present (UUID falls back for
      `stream.opened` and other sentinel envelopes where `seq` is None).
    - `_parse_last_event_id_seq` parses the `Last-Event-ID` header into
      an int seq cursor; negative/non-int rejected.
    - `_replay_since` (capped at `SSE_REPLAY_CAP=200`) emits missed
      events at the top of a new SSE stream when `Last-Event-ID`
      was sent. Truncation surfaces a `stream.replay_truncated`
      sentinel envelope so the client knows to fall back to
      explicit GET replay.
    - `fleet_events_replay` view — `GET /api/fleet/events/?since=<seq>
      &limit=<n>`. Signed-only (same `verify_signed_request` posture
      as the stream). Default limit 100, max 500. Response:
      `{events: [...], next_since, has_more, app_slug}`.
- `core/services/fleet_event_cleanup.py` — pure function modeled on
  `fleet_artifact_cleanup` but hard-deletes by seq order. Returns
  `CleanupStats(deleted, capped, duration_ms, retention_days)`.
- `core/tasks.py` — `cleanup_expired_fleet_events` Celery task wrapper
  on the `broadcast` queue.
- `core/celery.py` — beat schedule entry at `crontab(hour=2, minute=25)`
  to stagger off the 2:10 artifact cleanup.
- `tests/services/test_fleet_events_move3_r2.py` — 18 pure-function
  tests for query parsing + SSE formatting. DB-dependent paths
  (replay ordering, TTL deletion) validated by live smoke against
  the running stack — pgvector still missing from the test DB
  creation path on this machine.

### contract-concierge ([#16](https://github.com/clwest/contract-concierge/pull/16))

- `backend/app/brain_events.py` is the **canonical Move 3 R2 copy**
  for the 7 fleet repos.
    - New `_replay_since` async generator drains the u-d-b replay
      endpoint until exhausted, yielding envelopes in the same
      SSE-shaped dict as live events.
    - `subscribe_fleet_events` loop: drain replay → attach SSE →
      track `last_seq` from each event's `data.seq`. On reconnect,
      drain replay again from the updated cursor. `Last-Event-ID`
      sent on the SSE GET as a best-effort fallback.
    - Bounded: `MAX_REPLAY_PAGES=50` so a long outage doesn't block
      live indefinitely; the SSE side surfaces
      `stream.replay_truncated` if the cap is hit.

### 6 byte-identical back-props

| Repo | PR |
|---|---|
| mentorforge | [#18](https://github.com/clwest/mentorforge/pull/18) |
| pitchdeckforge | [#17](https://github.com/clwest/pitchdeckforge/pull/17) |
| sellerpilot | [#11](https://github.com/clwest/sellerpilot/pull/11) |
| dealflowtracker | [#15](https://github.com/clwest/dealflowtracker/pull/15) |
| compliancesentinel | [#11](https://github.com/clwest/compliancesentinel/pull/11) |
| signal-studio | [#11](https://github.com/clwest/signal-studio/pull/11) |

Only `DEFAULT_APP_SLUG` differs. The `DO NOT EDIT EXCEPT THESE
CONSTANTS` rule is intact for Phase 2C extraction.

## Gotchas hit and saved

- **Django 5 `db_default` is mandatory** for DB-managed defaults on
  non-PK columns. `null=True` alone is not enough — Django will
  explicitly pass NULL in the INSERT statement, overriding the
  Postgres `DEFAULT nextval(...)` and tripping NOT NULL. Saved to
  feedback memory.
- **Docker container had a baked-in copy of brain_events.py**.
  Volume mounts were defined in `docker-compose.dev.yml` but the
  running stack uses `docker-compose.yml` (no mounts). Verified via
  `docker inspect <container> --format '{{...config_files}}'`.
  Solution: `docker compose up -d --build --force-recreate <svc>`.
  This matches Chris's existing feedback memory on
  `--force-recreate`.
- **Test DB lacks pgvector** on this machine, so the canonical
  approach for fleet-event work is unit tests for pure functions +
  live smoke against the running stack. Pattern is consistent with
  the Move 1 / Move 2 R1+R2 tests in `tests/services/test_fleet_auth.py`.

## What Session 1130 did NOT do (carryover for 1131)

Rigby's remaining priority order from her 1130 brief:

- **Option B — Service-token auth for `app_slug`.** Now ranks first
  for 1131 per her standing rule "auth-gate before UI for security-
  boundary features." The signed fleet → u-d-b path is auth'd; the
  PA-token brain-bridge path still trusts whatever `app_slug` the
  caller claims. Add `allowed_app_slugs` to the PA token model + a
  back-fill migration (probably `["*"]` for legacy tokens with a
  warning logged on use).
- **Option D — Wire SSE into mentorforge.** lesson generation has the
  same "long-running thing you want to watch live" shape as draft
  generation. Mostly reuse: u-d-b emits `lesson.created` /
  `lesson.published`, mentorforge backend mirrors CC's per-user
  endpoint, frontend gets an activity strip. ~½ session.
- **Option E — FC-path hint bias (Phase 2D).** Inject a system
  message biasing the LLM toward the hinted agent's tool when
  `PA_USE_FUNCTION_CALLING=True`. Independent of B + D.
- **Option F — fleet_health → signal-studio spider feed.** Still
  deferred from Session 1126.

## Pending cleanup

- **6 sibling fleet repos** are running R1 brain_events.py code — only
  contract-concierge was rebuilt this session. After the 6 PRs merge,
  `cd ~/development/infra && make up` will rebuild them. The R1
  subscriber is forward-compatible (it ignores the new `seq` field in
  envelopes) so nothing breaks while they're stale.
- **Per-user filter on u-d-b.** Optional `?user_id=…` query param on
  the replay endpoint to push filtering server-side. Not implemented
  — current fan-out + filter in each consumer is cheaper than another
  index for traffic this small. Add when traffic justifies it.
- **DB-dependent tests** for replay ordering + TTL deletion. Requires
  test DB with pgvector. Could potentially add a sqlite-bypass for
  these specific tests if it's worth the complexity.

## Source-of-truth touchpoints

- `core/migrations/0346_fleetevent_seq.py` — schema lock for `seq`.
- `core/services/fleet_events.py:emit_event` — envelope shape lock.
- `core/views_fleet_events.py:fleet_events_replay` — endpoint lock.
- `core/views_fleet_events.py:_format_sse_event` — `id:` field lock.
- `core/services/fleet_event_cleanup.py:run_cleanup` — TTL lock.
- `backend/app/brain_events.py` in **contract-concierge** — canonical
  R2 subscriber. Edit here first, back-prop to the other 6.

## Smoke recipe (for future sessions)

When you suspect the replay path has drifted:

1. `cd ~/development/infra && make up` to ensure all 7 fleet apps are
   running latest images.
2. `make all` from infra (or `make start && make celery` from u-d-b)
   to bring u-d-b up natively.
3. Visit `localhost:5175`, log in (chris@donkeybetz.com account), open the Drafts tab.
4. **Test 1**: New draft → event appears in activity strip within
   10–30s. Confirms live path.
5. **Test 2**: Tab-switch for ~30s, fire another draft (separate
   window / API call), tab back. Missed event should appear after
   reconnect. Confirms replay path.

If Test 2 fails, check `docker logs contract_concierge_api | grep
brain-events` for the upstream subscriber's view. The first thing to
look for is whether `_replay_since` even fires — if not, the seq
tracking probably regressed.

---

*Last edit: Session 1130 close, 2026-05-22.*
