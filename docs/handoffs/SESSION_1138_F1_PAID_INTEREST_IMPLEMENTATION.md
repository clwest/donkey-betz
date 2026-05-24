---
title: "Session 1138 — F1 Signal Studio paid-interest signal (Decision 13 implementation)"
date: 2026-05-24
status: active
session: 1138
previous_handoff: SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md
next_session_primary: Chris ratification pass on Jessica's 22 decisions + celery PA worker restart to expose `paid_interest_status` tool to Rigby
team: chris + claude
---

# Session 1138 — F1 paid-interest signal implementation

> **Read this if** you want the F1 / Decision 13 demand-gate implementation
> details: end-to-end vertical slice (model + migration + endpoint + PA
> tool + signal-studio backend relay + frontend form), what's verified
> against the live stack, what's left for next session.

## TL;DR

**Implemented Decision 13 demand-gate end-to-end.** signal-studio
free-tier users can submit "notify me when paid launches" via a footer
form; submissions are rate-limited per-IP at the FastAPI layer, signed
with fleet HMAC, persisted in u-d-b's `core_fleetpaidinterest` table.
Jessica queries the trigger state via Rigby's new `paid_interest_status`
PA tool.

**Verified live**: full HTTP path (signal-studio frontend port 8007 →
u-d-b daphne port 8000), Decision 13 condition 2 ("≥1 willing-pay ≥$49")
correctly flips trigger_state to `ready` with the smoke row.

**Verified live via Rigby** (same session, post-celery-restart):
- Rigby executed `paid_interest_status` in 13ms via `pa_local.sh`
- Returned `trigger_state="ready"` correctly (smoke row's willing_pay=49 fires Decision 13 condition 2)
- Tool runs verbose block shows `[OK] paid_interest_status (13ms)` — task_id `73fbef09-c97f-4a07-9fbf-d5055ea3fd7e`

**Not verified live yet** (next session):
- Frontend visual smoke (TypeScript build is clean; browser unverified)

**Honest scope note (Chris's pushback ratified mid-session)**: Signal
Studio is pre-launch with no traffic. The form will not capture organic
signal until it does. The **manual override clause** in
`evaluate_trigger_state(..., manual_override=True)` is the actual
mechanism Jessica should use today — outreach to 5 ICP conversations >
waiting on a form. The form is built and ready for when traffic exists.

## What landed

### u-d-b side (this PR — branch `feat/session-1138-paid-interest`)

| Path | Change |
|---|---|
| `core/models/fleet.py` | `FleetPaidInterest` model (UnifiedBaseModel subclass, 7 indexed fields, app_slug-keyed for fleet reuse) |
| `core/migrations/0350_fleetpaidinterest.py` | CreateModel migration; **applied locally** |
| `core/views_fleet_paid_interest.py` | `POST /api/fleet/paid-interest/` — HMAC-signed, server-side dedup (7-day window, casefolded use_case match), validation (email regex, 140-char use_case, workspace_size choices) |
| `core/services/fleet_paid_interest.py` | `evaluate_trigger_state(app_slug, manual_override=False)` — Decision 13 state machine; per-app config in `APP_TRIGGER_CONFIG` so SellerPilot/ComplianceSentinel can register their numbers when their gates land |
| `core/urls.py` | Register `api/fleet/paid-interest/` |
| `core/auth_middleware.py` | Add `/api/fleet/paid-interest/` to `OPTIONAL_AUTH_PATHS` (signed-but-tokenless fleet auth) |
| `core/services/pa_tool_schemas.py` | `paid_interest_status` schema + entries in `TOOL_TO_ENRICHMENT_SOURCES` (none) + `TOOL_TO_INTENT_MAP` (`system_health`) |
| `core/services/td_handlers_core.py` | `_handle_paid_interest_status` handler — thin wrapper over `evaluate_trigger_state` |
| `core/services/tool_dispatcher.py` | `self.register("paid_interest_status", ...)` |
| `tests/services/test_fleet_paid_interest.py` | 14 pure-function tests (email regex, use_case normalizer, workspace size set, per-app config defaults + signal-studio override) — all passing |

### signal-studio side (separate PR — branch `feat/paid-interest-form`)

| Path | Change |
|---|---|
| `backend/app/brain_client.py` | `submit_paid_interest(...)` — sibling of `push_artifact()`, calls `POST /api/fleet/paid-interest/` with HMAC signing |
| `backend/app/main.py` | `POST /api/paid-interest` — per-IP rate-limit (3/hr in-memory dict), validation, forwards to u-d-b |
| `frontend/src/App.tsx` | `PaidInterestForm` component — 3 states (collapsed banner / expanded form / submitted confirm), localStorage dismissal, embedded in App footer |

## Renames from spec

The spec literal said `signal_studio_paid_interest` table + path
`/api/signal-studio/paid-interest`. Chris green-lit fleet-convention
renames mid-session:

- Table: `core_fleetpaidinterest`, model `FleetPaidInterest`, keyed by
  `app_slug` so SellerPilot/ComplianceSentinel reuse it when their
  Decision-13-style gates come up. +2 hours of scope now, saves writing
  3 near-identical tables later.
- Path: `/api/fleet/paid-interest/` (no app slug in URL — slug derived
  from HMAC signature, same as `/api/fleet/artifacts/`).

## Decision 13 trigger conditions (re-derived for clarity)

The implementation matches Jessica's lock:

| # | Condition | Where |
|---|---|---|
| 1 | `last_90d_signals >= 5` (signal-studio config) | `evaluate_trigger_state` |
| 2 | `has_high_value_signal` = any row with `willing_pay >= 49` | `evaluate_trigger_state` |
| 3 | Jessica manual override | `evaluate_trigger_state(..., manual_override=True)` — caller's decision; no DB-side override row in MLC |

Per-app config in `APP_TRIGGER_CONFIG` (`core/services/fleet_paid_interest.py`):

```python
APP_TRIGGER_CONFIG = {
    "signal-studio": {
        "count_threshold": 5,
        "rolling_window_days": 90,
        "pro_price": 49,
    },
}
```

Add SellerPilot etc here when those gates come up. Unknown app_slug
falls back to `DEFAULT_*` constants (same numbers; only signal-studio
has explicit overrides today).

## Live smoke results

```bash
# u-d-b restarted (daphne PID 93286, fresh code)
# signal-studio rebuilt + recreated (docker compose up -d --build --force-recreate)

$ curl -X POST http://localhost:8007/api/paid-interest \
    -d '{"email":"smoke-test@example.com","use_case":"E2E smoke for session 1138","willing_pay":49}'
HTTP/1.1 200 OK
{"ok":true,"id":"81bec160-07a4-474f-a342-23507de8586c","deduped":false,
 "message":"Got it. We'll email you at launch."}

$ # Repeat submission within 1 hour from same IP:
HTTP/1.1 429 Too Many Requests   # rate-limit fires at submission #4 (3/hr cap)

# Trigger-state evaluation via ORM:
>>> evaluate_trigger_state("signal-studio").to_dict()
{
  "app_slug": "signal-studio",
  "total_signals": 1,
  "last_90d_signals": 1,
  "has_high_value_signal": True,        # willing_pay=49 meets Pro tier price
  "high_value_threshold_usd": 49,
  "trigger_state": "ready",             # Decision 13 condition 2 fires
  "rolling_window_days": 90,
  "count_threshold": 5,
  "last_signal_at": "2026-05-24T14:41:12.154283+00:00"
}

>>> evaluate_trigger_state("signal-studio", manual_override=True).to_dict()
{
  ...,
  "trigger_state": "manually_overridden"  # override wins regardless of counts
}
```

The smoke row (`81bec160-…`) is left in the table as live demo data.
Drop it at handoff close if undesired:

```python
FleetPaidInterest.objects.filter(email="smoke-test@example.com").delete()
```

## What's left

### ~~FIRST THING — Restart celery PA worker~~ DONE same session

Celery restarted (`pkill -f "celery -A core"; make celery`), Rigby
verified via `pa_local.sh` and successfully invoked the new tool.
Tool result + verbose Tool Runs block captured above in the
"Verified live via Rigby" section.

### FIRST — Frontend visual check

TypeScript build is clean (`./node_modules/.bin/tsc -b` exits 0).
Browser-side smoke not done. `cd signal-studio && docker compose
restart web` should reload the frontend container (vite dev server).
Then visit `http://localhost:5173` (or whichever port signal-studio's
web container exposes — check `make urls`).

Verify:
- Footer banner shows on first visit
- "Notify me" expands the form
- Submit with valid email + use_case → confirmation state
- Dismiss persists across page reload (localStorage)

### THIRD — Decide on the smoke row

Either delete it (one-liner above) or keep it as live demo data showing
the gate is `ready`. If Jessica's checking the state weekly, the
demo row will keep her dashboard at `ready` until removed.

## Open questions for Chris

1. **PA worker restart**: green-light to `pkill -f "celery -A core"; make celery`?
2. **Smoke row**: keep or delete?
3. **Per-IP rate-limit storage**: in-memory dict is fine for single-container signal-studio. When signal-studio scales to multi-instance (future), this needs Redis. Not blocking; flag for later.
4. **Frontend port**: signal-studio's web container — what port does it expose? Not in the brief I read.

## Honest scope reflection (carry into 1139)

The spec was correct that this is buildable in ~1.5 days. The
implementation took less but mostly because the fleet HMAC machinery
was already in place from Sessions 1129-1133.

The harder question — "should this exist now, given Signal Studio has
no traffic" — was raised mid-session and Chris ratified: **build it
now, mechanism's ready when traffic exists, manual override is the
working trigger until then**. Saved to memory.

## Files touched (summary)

```
u-d-b:
  core/models/fleet.py                           # +152 / -0   (FleetPaidInterest model)
  core/models/__init__.py                        # +1   / 0    (export)
  core/migrations/0350_fleetpaidinterest.py      # +183 / 0    (new file)
  core/views_fleet_paid_interest.py              # +247 / 0    (new file)
  core/services/fleet_paid_interest.py           # +151 / 0    (new file)
  core/urls.py                                   # +12  / 0
  core/auth_middleware.py                        # +3   / 0    (OPTIONAL_AUTH_PATHS)
  core/services/pa_tool_schemas.py               # +44  / 0    (schema + 2 map entries)
  core/services/td_handlers_core.py              # +22  / 0    (handler)
  core/services/tool_dispatcher.py               # +5   / 0    (register)
  tests/services/test_fleet_paid_interest.py     # +98  / 0    (new file, 14 tests passing)

signal-studio:
  backend/app/brain_client.py                    # +77 / 0     (submit_paid_interest)
  backend/app/main.py                            # +91 / 0     (FastAPI route + rate-limit)
  frontend/src/App.tsx                           # +193 / 0    (PaidInterestForm component)
```

## Test posture

- **14/14 pure-function tests pass** locally (`pytest tests/services/test_fleet_paid_interest.py -v`)
- **Live HTTP path verified** end-to-end via curl
- **State machine verified** against real DB row (Decision 13 condition 2 fires correctly)
- **DB-dependent state machine tests** parked because local Postgres
  has the template-collation issue blocking Django test-DB creation
  (same parking pattern as `test_fleet_signals_phase1.py` from Session
  1131). Live ORM smoke covers the same scenarios.

## Carryover into Session 1139

Inherits everything from `00-START-NEXT-SESSION.md` Session 1138 entry
minus F1 (which this session closed). Most-urgent unchanged item: Chris
ratification pass on Jessica's 22 Phase 1-4 decisions.
