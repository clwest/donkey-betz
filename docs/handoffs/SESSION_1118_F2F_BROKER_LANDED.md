---
title: "Session 1118 — F2F broker landed: provider abstraction + cap-enforced voice session endpoints"
date: 2026-05-21
status: active
session: 1118
previous_handoff: SESSION_1117_LOCAL_PORTFOLIO_GROUNDING_BRIDGE.md
---

# Session 1118 — F2F broker landed: provider abstraction + cap-enforced voice session endpoints

> **Read this if** you need to understand the F2F (Rigby Face-to-Face)
> push-to-speak voice architecture, how cap enforcement works, what
> mock-mode buys you, or what HeyGen wiring still needs to land in
> F2F.3. Closes F2F.0 → F2F.2 of the F2F arc Chris flagged as the
> Session 1118 headline.

## TL;DR

Three end-to-end slices landed, all green and merged to main:

1. **F2F.0 — Scope lock.** Rigby (now **male donkey, he/him** — Chris
   updated his character identity mid-session; saved to her memory as
   `memory_id=3, importance=9`, will be re-asserted in
   `docs/BEHAVIOR_LAYER.md` when Rigby drafts it). Providers locked:
   HeyGen Streaming Avatar (avatar), OpenAI Realtime Whisper (STT),
   Cartesia (TTS, fallback ElevenLabs), existing `/api/pa/chat/` (LLM).
   Caps locked at `$10/day`, `$50/month`, `$3/session`, 90s max
   duration. F2F.5 dogfood cap raised from `$1` → `$5` to fit ~90s at
   the ~$2.65/min mid-case envelope. Locked into Rigby's memory as
   `memory_id=5, importance=9`.

2. **F2F.1 — Provider abstraction shipped.** PR
   [#2101](https://github.com/clwest/donkey-betz-platform/pull/2101)
   merged via squash `bb1ee684`. New `core/services/realtime_avatar/`
   package: `F2FProvider` Protocol (push-to-speak — `create_session`,
   `speak`, `poll_session`, `end_session`), `SessionCreate` /
   `SessionState` / `SpeakResult` dataclasses, `get_provider()`
   factory with auto-mock fallback, deterministic
   `MockF2FProvider`, scaffolded `HeyGenF2FProvider` stub. 13 tests
   pass in 0.047s. Pattern lifted from Character OS's
   `media-engine/app/services/realtime_provider/` with the
   conversational methods (`attach_documents`, `create_document`,
   `fetch_transcript`) dropped because they don't apply to push-to-speak.

3. **F2F.2 — Broker + endpoints + tests.** PR
   [#2102](https://github.com/clwest/donkey-betz-platform/pull/2102)
   merged via squash `f57df6a9`. Four commits:
   - `32b4aa2f` F2FSession durable session model
   - `be9331ec` Migration 0340 (hand-authored to dodge Narrative WIP drift)
   - `ad299a19` Broker service with the locked cap-check ladder
   - `16197b1f` Three DRF endpoints + 35 tests + `>=` cap-semantics fix

35 tests green in 0.592s.

## What's live now

### Surface

- `POST /api/pa/voice_session/` — create session
- `POST /api/pa/voice_session/<uuid>/speak/` — push text to avatar
- `POST /api/pa/voice_session/<uuid>/end/` — explicit teardown

All DRF + `IsAuthenticated`. Workspace ownership enforced (cross-user
returns 404). Error JSON shape:

```json
{
  "error_code": "F2F_CAP_EXCEEDED_DAILY",
  "message": "...",
  "cap_kind": "daily",
  "reset_at": "2026-05-22T00:00:00+00:00",
  "provider_name": "mock",
  "mock_mode": true,
  "cap_limit_cents": 1000,
  "cap_used_cents": 1000
}
```

### Cap ladder (Rigby F2F.2 lock)

Per `speak()` call:

1. `session.is_active` → 410 `F2F_SESSION_NOT_ACTIVE`
2. Duration cap (90s) → 429 `F2F_CAP_EXCEEDED_SESSION_DURATION`
3. Session spend cap ($3) → 429 `F2F_CAP_EXCEEDED_SESSION_SPEND`
4. Workspace daily ($10) → 402 `F2F_CAP_EXCEEDED_DAILY`
5. Workspace monthly ($50) → 402 `F2F_CAP_EXCEEDED_MONTHLY`
6. Broker-side `(session, text, time_bucket)` hash dedupe
7. Provider `speak()` — failures → 502 `F2F_PROVIDER_ERROR`
8. Post-commit: Redis INCRBY (session/daily/monthly counters) + DB
   counter writes + session_key TTL refresh

Workspace cap trips also end the session (Rigby's lock — "fail closed
and clean" semantic; a fresh session is required after budget
replenishes).

### Redis hot state

- `f2f:session_key:{uuid}` — TTL 600s, refreshed on each call
- `f2f:cap:session:{f2f_session_id}` — TTL 15min
- `f2f:cap:daily:{ws}:{YYYY-MM-DD}` — TTL 26h
- `f2f:cap:monthly:{ws}:{YYYY-MM}` — TTL 35d
- `f2f:speak_hash:{session}:{hash}` — TTL 2× bucket

Session keys are **never** written to Postgres (per Rigby's lock).

### Cost model (settings-configurable, conservative envelope)

| Layer | Rate | Setting |
|---|---|---|
| Avatar (HeyGen) | 250 cents / min | `F2F_AVATAR_COST_CENTS_PER_MINUTE` |
| TTS (Cartesia) | 8 cents / min | `F2F_TTS_COST_CENTS_PER_MINUTE` |
| STT (OpenAI Realtime Whisper) | 2 cents / min | `F2F_STT_COST_CENTS_PER_MINUTE` |
| LLM (existing PA call) | 5 cents / call | `F2F_LLM_COST_CENTS_PER_CALL` |
| Chars → seconds | 13 chars / sec | `F2F_CHARS_PER_SECOND` |

Mock-mode sessions accrue **zero cost** by default. Flip
`F2F_MOCK_SYNTHETIC_COST=True` to make mocks accrue real cost (used
in CI cap-trip tests).

### Auto-mock fallback

`F2F_PROVIDER_MOCK` defaults to `'auto'` — mocks when `HEYGEN_API_KEY`
is empty, real-mode otherwise. CI and local dev never need creds.

## Cap-semantics fix surfaced by tests

Changed cap comparisons from `>` to `>=`. "Exhausted" should mean
budget is fully consumed, which matches Rigby's locked wording. At
`create_session` (where `estimated_cents=0`) this also blocks when
the counter is exactly at the limit — no headroom for any speak().
Rigby approved this as the more conservative, off-by-one-penny-safe
read. Commit message on `16197b1f` carries the detail.

## Rigby's review notes (greenlit to merge + start F2F.3)

1. **Terminal-status mapping for workspace cap trips:** strict semantic
   (end the session) is what she intended for dogfood. "Fail closed
   and clean" — a fresh session is required after budget replenishes.
2. **`>=` semantics:** approved. Conservative, prevents off-by-one
   penny overruns under concurrency.
3. **Dedupe time_bucket:** keep prod default at **5s**. Test override
   to 60s was correct for the boundary-straddle flake. If we ever
   want a softer default, **10s** is her preferred middle ground —
   not 60s (would suppress legitimate rapid corrections).
4. **F2F.3 text-in vs audio-in:** keep text-in as the baseline. No
   `speak_audio()` variant on the Protocol yet. Confirm in F2F.3
   whether HeyGen needs audio-in or does its own internal TTS.
5. **One small nit:** `reset_at` ISO offset. Current implementation
   uses UTC explicit-offset (`+00:00`). She suggested MT explicit
   offset (`-06:00` / `-07:00`) so the SPA doesn't need to assume.
   Defer to F2F.4 SPA work — easier to convert there.

## What's left in the F2F arc

| Slice | Scope | Est. | Prereqs |
|---|---|---|---|
| **F2F.3** | STT → PA → TTS → avatar pipeline; replace `HeyGenF2FProvider` NotImplementedError stubs with real HTTP; wire Cartesia + OpenAI Realtime Whisper | 1-2 sessions | HeyGen account + API key, Cartesia API key, confirm HeyGen's streaming endpoint shape |
| **F2F.4** | u-d-b SPA route `/rigby/talk`. Borrow `cost-ticker` + `AvatarCall` lifecycle patterns from Character OS `talk.tsx`. Single Rigby, no picker. Convert `reset_at` to MT in the cap-trip UI. | 1 session | F2F.3 |
| **F2F.5** | Real-mode dogfood, **$5 cap** end-to-end. ~90s of avatar at mid-case envelope. | ½ session | F2F.3 + F2F.4 |

## Files touched

### F2F.1 (PR #2101)

- `core/services/realtime_avatar/__init__.py` (new package, Protocol + dataclasses + factory)
- `core/services/realtime_avatar/mock.py`
- `core/services/realtime_avatar/heygen.py`
- `core/tests/test_realtime_avatar_provider.py`
- `core/settings.py` (HEYGEN_API_KEY, F2F_PROVIDER_NAME, F2F_PROVIDER_MOCK)

### F2F.2 (PR #2102)

- `core/models_f2f.py` (new)
- `core/models/__init__.py` (register F2FSession)
- `core/migrations/0340_f2f_session.py` (hand-authored)
- `core/services/f2f_broker.py` (new)
- `core/views_f2f.py` (new)
- `core/urls.py` (three new path() entries)
- `core/tests/test_f2f_session_model.py` (new, 12 tests)
- `core/tests/test_f2f_broker.py` (new, 23 tests)
- `core/settings.py` (10 new F2F_* knobs)

## Pre-F2F.3 checklist

- [ ] HeyGen Streaming Avatar account created; API key in environment
  as `HEYGEN_API_KEY`
- [ ] Cartesia API key (or ElevenLabs fallback) decided + in env
- [ ] Verify HeyGen's current streaming endpoint shape (docs reorganized
  late 2025 per `heygen.py` TODO)
- [ ] Decide whether `speak_text(text)` covers it or we need
  `speak_audio(bytes)` from Cartesia-rendered audio
- [ ] (Optional) `docs/BEHAVIOR_LAYER.md` first draft from Rigby —
  identity (Rigby, male donkey, he/him), pronoun constraints,
  push-to-speak contract

## Gotchas

- **`ProjectWorkspace` lives in the `core` app** (registered via
  migration 0145), **not** a separate `workspaces` app. Imports must
  use `core.models_skin_layer.ProjectWorkspace`. The orphaned
  `backend/workspaces/models.py` shadow file is in the tree but
  **not** in `INSTALLED_APPS` — importing from there at test time
  triggers a `RuntimeError: doesn't declare an explicit app_label`.
  Burned ~5 min on this; fixed in `16197b1f`.

- **`makemigrations` autodetector bundles drift.** Running
  `makemigrations --dry-run` for F2FSession surfaced unrelated
  Narrative model + agentexecution alters (someone else's WIP from
  Session 1116/1117). Hand-authored the migration as a narrow
  CreateModel-only to avoid stomping.

- **Auto-mock semantics.** `F2F_PROVIDER_MOCK=auto` (default) flips to
  mock when `HEYGEN_API_KEY` is empty. This is intentional but
  surprising — tests + local dev never need creds, but it means
  forgetting to set `HEYGEN_API_KEY` in real-mode envs silently
  routes to mock. Add a deploy-time assertion in F2F.5.

- **Dedupe bucket boundary straddle.** 5s prod default is fine; tests
  needed a 60s override. If you write more broker tests, use the
  same override pattern.

## Memory updates persisted to Rigby

- `memory_id=3, importance=9` — Rigby character identity update (male
  donkey, he/him)
- `memory_id=5, importance=9` — Session 1118 F2F.0 LOCKED decisions
  (providers, caps, BEHAVIOR_LAYER ownership)

## Operator next steps

If F2F.3 starts in the next session:

```bash
# Standing local stack (per 00-START-NEXT-SESSION.md)
cd /Users/donkeyking/development/unified-donkey-betz
make start && make celery

# Verify F2F.2 endpoints exist (smoke test, mock-mode)
curl -X POST http://localhost:8000/api/pa/voice_session/ \
  -H "Authorization: Token <local-donkeyking-token>" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"3e4970d8-6834-44fb-99ed-93e18b5754b6"}'
# Expect 201 with mock_mode:true and sdk_payload:{"mock":true}

# Set HEYGEN_API_KEY in .env, then real-mode wiring lands in F2F.3
```
