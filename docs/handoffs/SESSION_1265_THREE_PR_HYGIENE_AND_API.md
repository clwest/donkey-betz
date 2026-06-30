---
session: 1265
status: closed
date: 2026-06-30
arc: Three-PR session — (1) stale-worker guard for process_core_spider_data, (2) mechanical drift hygiene (orphan CELERY_TASK_ROUTES + CLAUDE.md autoblock + verifier baselines), (3) read-only Employee/Mission HTTP API (5 endpoints, IsAdminUser-gated). Architecture review at open → option (i) build-on-strength + Rigby's caveat → 3 PRs shipped clean in one session.
prs_merged: [2758, 2759, 2760]
prs_open: []
companions:
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
deliverables: []
---

# Session 1265 — Stale-Worker Guard, P2+P3 Hygiene, Employee/Mission HTTP API

## TL;DR

Three small, scoped PRs shipped end-to-end in one session, all
admin-merged after Rigby SIGN. Total surface: 9 files +910 / -17,
54 new tests added, 0 regressions. No MissionRunner / JobContract /
Employee OS / employee_tool behavior changed.

| PR | Type | Scope | Merge SHA |
|---|---|---|---|
| [#2758](https://github.com/clwest/donkey-betz-platform/pull/2758) | fix | Defensive guard at `_impl_process_core_spider_data` entry — preflight-check model's `db_table` exists; on miss log `[STALE_WORKER_MODEL_TABLE_MISSING]` + return diagnostic dict | `8f94f66b` |
| [#2759](https://github.com/clwest/donkey-betz-platform/pull/2759) | chore | Mechanical drift hygiene — delete orphan `'content.*'` route + refresh CLAUDE.md/AGENTS.md autoblocks + bump 2 verifier baselines | `0eb5a671` |
| [#2760](https://github.com/clwest/donkey-betz-platform/pull/2760) | feat | Read-only Employee/Mission HTTP API — 5 GET endpoints, IsAdminUser-gated, thin wrappers around existing helpers | `3740bac0` |

## Architecture review at session open

Independent verification surfaced two findings the priority menu didn't:
1. **PR #2756 emitted ZERO `authority_contract_observed` events** since
   merge (~30 min earlier). Workers' `.pid` files dated 11:16, predating
   the 11:42 merge — classic `sys.modules` cache scenario (start-here
   §READ-THIS-FOURTH case 2). Code correct on disk; runtime hadn't
   loaded it.
2. **`core.tasks.process_core_spider_data` had 50 historical FAILURE
   rows** from `ProgrammingError: relation "core_spiderdata" does not
   exist`, last failure 2026-06-27 23:15, then 3 days clean. Same root
   cause: workers held the pre-S1243 `core.SpiderData → LegacySpiderData`
   rename in `sys.modules`.

Both closed by Step A (`make celery` restart). Then Rigby SIGNed a
defensive guard PR as the actual "S1265 first PR" — converts the recur
class into an actionable ops signal without re-introducing the
flapping.

## What shipped — PR #2758 (admin-merged 2026-06-30, merge SHA `8f94f66b`)

**Files:**

| File | Net | Purpose |
|---|---|---|
| `core/tasks_spiders.py` | +51 / 0 | Preflight `db_table` introspection guard at function entry; diagnostic dict return on miss; subprocess `_git_sha()` only on failure branch |
| `core/tests/test_process_core_spider_data_stale_worker_guard_s1265.py` | +106 / 0 (NEW) | 2 tests: missing-table soft-fail + present-table happy-path |

**Behavior contract:**

When `LegacySpiderData._meta.db_table` is missing from the introspected
DB schema:

- Log `[STALE_WORKER_MODEL_TABLE_MISSING] model=... db_table=... worker_git_sha=...`
- Return `{processed: 0, ..., skipped: True, reason: 'stale_worker_model_table_missing', expected_table: <name>, worker_git_sha: <sha>}`
- Do NOT raise `ProgrammingError`

When `connection.introspection.table_names()` itself fails:

- Log `[STALE_WORKER_GUARD_SKIPPED]` warning, fall through to original
  query (treat introspection error as transient; canonical failure
  via the original query is the next signal)

**Rigby SIGN decisions:**

- Soft-fail with diagnostic dict, NOT raise — prevents FAILURE flap
  storm vs SLO baseline
- Introspection-error fallthrough (warn + continue) — better than
  false-negative skip on transient infra
- Scoped only to `_impl_process_core_spider_data` — the 6 other
  `LegacySpiderData` call sites in the same file are non-periodic
  and fail loud already
- `worker_git_sha` forensic enrichment via subprocess (only on
  failure branch — zero cost on the every-2-min happy path)

## What shipped — PR #2759 (admin-merged 2026-06-30, merge SHA `0eb5a671`)

**Files (4 files, +17 / -13):**

| File | Net | Purpose |
|---|---|---|
| `core/settings.py` | +4 / -1 | Delete orphan `'content.*'` wildcard route from `CELERY_TASK_ROUTES`. Was leftover from S1246 `cc9ab2c1` which deleted `content/tasks.py` (3 tasks) and the explicit `content.tasks.poll_pending_trainings` route but missed the wildcard. Content QUEUE itself preserved by 7 explicit per-task routes. |
| `CLAUDE.md` | +5 / -5 | Autoblock refresh via `refresh_doc_inventory_blocks`: Services 355→362 files, Celery Tasks 412→414, Beat Schedule 90→91 enabled, PA Tools 109→113 schemas / 152→156 handlers, Database Models 584→585, agent taxonomy `74 enabled / 8 rerouted / 1 blocked` → `74 / 9 / 0` (CodeGeneratorAgent reclassified blocked → rerouted between S1115 and now) |
| `docs/AGENTS.md` | +2 / -2 | 2 autoblock entries refreshed (pure runtime-derived counts) |
| `core/services/doc_claim_verification.py` | +6 / -5 | Verifier baseline refresh: `agent_taxonomy_reconciliation` expected `74/8/1 → 74/9/0`; `services_file_count_103` expected `351 → 362`; session comments refreshed |

**NOT touched (preserved as historical snapshot):**

- `docs/SERVICES.md` header text `"112 *Service classes across 351 files"` — explicitly self-labeled
  "Historical snapshot — do not cite as current"
- Broader Rigby drift-hygiene PR (9 `autopilot_tool drift_scan`
  warnings) — deferred as latent contract drift requiring design
  judgment

**Verification post-merge:**

- `test_every_route_pattern_matches_a_registered_task`: PASS (was FAIL)
- `verify_doc_claims --only-drift`: clean (both previously-drifting
  claims now `✓ ok`)
- `refresh_doc_inventory_blocks --check`: 0 WOULD UPDATE

## What shipped — PR #2760 (admin-merged 2026-06-30, merge SHA `3740bac0`)

**Files (3 files, +736 / 0):**

| File | Net | Purpose |
|---|---|---|
| `core/views_employee_api.py` | +250 / 0 (NEW) | 5 DRF function views with `@api_view(['GET'])` + `@permission_classes([IsAdminUser])` — thin wrappers around `list_employees`, `get_employee`, `list_jobs_with_keys`, `derive_status`, `evidence_for_mission`, `_dataclass_to_jsonable`, `_parse_window` |
| `core/urls.py` | +31 / 0 | 5 path() entries under `/api/employees/` and `/api/missions/` with `<uuid:mission_id>` typing |
| `core/tests/test_employee_mission_http_api_s1265.py` | +455 / 0 (NEW) | 18 tests across 7 classes |

**Endpoints:**

| Method + Path | Wraps | Notes |
|---|---|---|
| `GET /api/employees/` | `list_employees()` + `_dataclass_to_jsonable` | Returns `{ok, count, employees:[…]}` |
| `GET /api/employees/<handle>/` | `get_employee` + `list_jobs_with_keys` | Envelope mirrors `employee_tool action=describe` verbatim |
| `GET /api/employees/<handle>/jobs/<job_key>/status/?window=7d` | `derive_status` | window default '7d', valid '7d'\|'30d'\|'90d'; `?mission_id=…` forwards as `mission_id_hint` |
| `GET /api/missions/<mission_id>/` | OpsRun model | Exposes 8 contract fields always present (locked by `_MISSION_DETAIL_FIELDS` constant + contract test) |
| `GET /api/missions/<mission_id>/evidence/?verbose=true` | `evidence_for_mission` | `verbose=false` (default) returns `error_tail_preview` + `has_full_error_tail`; `verbose=true` returns full `error_tail`; `mission_not_found` soft-error → HTTP 404 |

**Rigby SIGN decisions:**

- D1 — Response shapes mirror `employee_tool` verbatim
- D2 — DRF function views (right weight for non-model dataclasses)
- D3 — `IsAdminUser` (flipped from Claude's IsAuthenticated). Verified
  `chris.is_staff=True` + `is_superuser=True` before locking
- D4 — Imported `_dataclass_to_jsonable` + `_parse_window` directly
  from `td_handlers_employee.py` (module-private but stable shared
  serializer surface)
- D5 — `/api/employees/` + `/api/missions/` roots, no `/v1` prefix
- SIGN-with-edits: parity test refactored to compare against public
  helpers (`get_employee` + `list_jobs_with_keys` + `_dataclass_to_jsonable`)
  rather than reaching into `ToolDispatcher._handle_employee_tool` —
  removes brittle coupling to dispatcher internals

**Mission detail 8-field contract** (locked by `MissionDetailEndpointTest.test_returns_8_contract_fields`):
id, status, run_kind, triggered_by, started_at, finished_at, mission_id, summary

**Test coverage:**

- `EmployeeApiAuthGateTest` (3) — D3 contract: anon blocked / non-staff blocked / staff passes
- `EmployeeListEndpointTest` (1) — happy path
- `EmployeeDetailEndpointTest` (3) — happy path + unknown handle 404 +
  shape parity via public-helper reconstruction
- `EmployeeJobStatusEndpointTest` (5) — default 7d / explicit 30d /
  invalid window 400 / unknown employee 404 / unknown job 404
- `MissionDetailEndpointTest` (3) — 8-field presence contract +
  `finished_at` null preservation for running missions + unknown 404
- `MissionEvidenceEndpointTest` (3) — verbose=false vs verbose=true
  contract + unknown 404

## Post-merge verification (all 3 PRs)

### Live HTTP probe via Django Client + chris.force_login

| Check | Result |
|---|---|
| Staff (chris) → all 5 endpoints | ✓ 5/5 returned 200 |
| Non-staff (verify_regular_s1265) → `/api/employees/` | ✓ 403 (D3 gate enforced) |
| `/api/employees/` content | ✓ count=3, handles=`['chief_of_staff', 'platform_auditor', 'rigby']` |
| `/api/missions/<id>/` 8-field contract | ✓ all 8 fields present in response |
| `/api/missions/<id>/evidence/?verbose=false` | ✓ preview=True, flag=True, full=False |
| `/api/missions/<id>/evidence/?verbose=true` | ✓ preview=False, full=True |
| `git diff 8f94f66b..3740bac0 -- core/employees/ core/services/td_handlers_employee.py` | ✓ EMPTY — zero changes to Employee OS source files |
| `employee_tool action=describe` still routes correctly | ✓ `ok=True, action=describe, employee.handle=rigby, job_count=1` |
| Recent task SUCCESS/FAILURE (10 min) | ✓ 24 SUCCESS / 0 FAILURE |

### Two apparent failures that are expected behavior

| Symptom | Explanation |
|---|---|
| `authority_contract_observed` event count stayed at 1 after a fresh `platform_auditor_run.delay()` | `platform_auditor_run` is **daily-idempotent** per its docstring (`already_ran=True` on re-dispatch within same calendar day). Today's mission already ran at 17:06 via S1265 Step A. Not a regression. |
| HTTP `derive_status` output vs `employee_tool action=status` output failed deep-equal | `derive_status` embeds wall-clock `as_of` / `window_start` / `window_end` fields that change between calls. The PR's contract test uses **describe** (timestamp-free) and passes correctly. Status equivalence holds modulo timestamps — by design. |

## What's preserved unchanged

- **MissionRunner public API** + all hooks + lifecycle event sequence
- **JobContract dataclass** — zero new fields
- **Employee OS primitives** (RIGBY, PLATFORM_AUDITOR, CHIEF_OF_STAFF,
  DOCUMENTATION_MANAGER, PLATFORM_AUDIT_JOB, MORNING_BRIEF_JOB)
- **`employee_tool` / `mission_verdict` tool behavior** — zero diff
  in `core/services/td_handlers_employee.py`
- **`derive_status` / `evidence_for_mission` internals** — zero diff
  in `core/employees/status.py`
- **OpsRun / OpsRunEvent models** — schema unchanged
- **MissionRunner code** — zero diff in
  `core/employees/mission_runner.py`
- **CELERY_TASK_ROUTES** content queue + 7 explicit per-task routes
  (only the dead wildcard removed)
- **docs/SERVICES.md** header text — explicit historical snapshot

## Memory observations worth keeping

- **`sys.modules` cache + model rename = silent SQL flap.** When a
  rename ships and workers haven't restarted, their cached model class
  generates SQL against the dropped table. ProgrammingError every fire,
  no telemetry beyond CeleryTaskEvent. The S1265 guard converts this
  into a single greppable ERROR per fire with worker_git_sha attached.
- **Daily-idempotency on Celery tasks looks like "regression" until you
  read the docstring.** `platform_auditor_run` was added in S1257 with
  the `already_ran=True` short-circuit so beat fires don't re-run the
  same daily audit. Post-merge verification should account for this.
- **`derive_status` is intentionally non-idempotent (timestamp-embedded).**
  Any future contract test that compares its output across two calls
  will fail. Use `describe` for the deterministic parity surface.
- **Verifier baseline refresh is the intended workflow.** When
  taxonomy reclassifies or file counts grow, the verifier fires drift
  → hygiene PR bumps the baseline + adds session note → drift clears.
  Working as designed (S1115 → S1222 → S1265 baseline progression).
- **The architecture-review pattern at session open paid off again.**
  S1265 opened with a P0-P7 menu; independent verification surfaced
  two findings the menu didn't (PR #2756 silent + dead-table flap).
  Both closed by the same `make celery` restart. The actual S1265
  first PR came from Rigby's caveat #2 on that discovery, not from
  the original menu.

## Three S1265 PRs scope summary

| PR | Files | LOC | Tests | Time-to-merge |
|---|---|---|---|---|
| #2758 stale-worker guard | 2 | +157 / 0 | 2 new | ~45 min |
| #2759 P2+P3 hygiene | 4 | +17 / -13 | 0 new (existing test now passes) | ~30 min |
| #2760 Employee/Mission HTTP API | 3 | +736 / 0 | 18 new | ~90 min |
| **Total** | **9** | **+910 / -13** | **20 new + 1 unblocked** | **~3 hours** |

## S1266 priorities

### FIRST THING Session 1266

Decide between two next-priority candidates before starting either:

#### Candidate A — Employee #4 discovery

S1264 close noted Employee #4 is **architecturally ready**:
- MissionRunner contract stable (S1259-1264)
- Per-employee boilerplate eliminated (S1261)
- Receipts pipeline + Agent row hygiene clean (S1262-1263)
- Warn-mode inherited automatically via `job_contract=...` factory
  kwarg (S1264)
- Estimated cost: 1,990-2,790 LOC, 9-14 hours

**Open question:** which employee? The choice frames the entire
arc:

- **Code Reviewer** — high-leverage for PR quality but overlaps with
  Claude Code's review surface
- **Frontend Auditor** — would catch UI rot, but UI changes are rare
- **Bug Triage Specialist** — fits Employee OS pattern; pairs with
  Platform Auditor's outputs
- **Doc Search Agent** — moves search_docs functionality into a
  daily routine
- Other — Chris's call

#### Candidate B — Rigby's broader drift-hygiene PR

9 `autopilot_tool drift_scan` warnings deferred from S1265 P3 as
"latent contract drift requiring design judgment":

- 2 action-enum coverage mismatches: `db_health_tool` (7 actions in
  schema but not in handler) + `mission_verdict` (3 actions in schema
  but not in handler) — would surface as "Unknown action" GPT errors
  if exercised
- 7 agent_registry orphans: DB Agent rows not in AGENT_MAP (Rigby,
  claude-code, PersonalAssistant, System, ValidationCheckAgent, rigby,
  3DGenerationAgent) — some legitimate (persona agents), some
  potentially stale

**Design judgment required:**

- For each action-enum mismatch: add the missing handler branches OR
  trim the schema entries (which is right depends on whether the
  actions are reachable via PA flow)
- For each agent_registry orphan: confirm whether the DB row is a
  legitimate persona (System, claude-code, Rigby, rigby) vs a stale
  reference

Estimated cost: 100-200 LOC + ~10 schema/handler decisions.

### Recommendation (per session-close directive)

**Do not start either until fresh session orientation.** Both
candidates would benefit from a clean conversation thread + reading
the current state of `td_handlers_employee.py` / `td_handlers_ops.py`
(for B) or surveying which employee role has the highest expected
weekly utilization (for A).

### Pre-existing S1264 carryover

#### Priority 0 — Pre-existing SLO breaches (unchanged)

`ops_tool action=overview window=30d` still reports:
- `agent_timeout_rate` 0.024284 vs target 0.002 (12× over — 28
  timeouts / 1153 agent calls / 30d)
- `celery_task_success_rate` 0.998825 vs target 0.999 (marginal —
  53 failures / 45,104 tasks / 30d)

**Note:** S1265 analysis showed 150 of the 241 30d agent failures
(62%) are sports-spider source drought (SportsOddsAnalyst +
ArbitrageDetector with "Odds API returned no data"), not agent
defects. Real "agent-internal" failures over 30d are ~63 = ~2/day.
The agent_timeout_rate breach is genuine but bounded.

#### Priority 5 — Future S1263 hygiene follow-up

Shrink `_CLAUDE_CODE_AGENT_NAMES = ('claude-code', 'ClaudeCode')` →
`('claude-code',)` in `claude_code_engineer.py:63` after 1+ week of
clean operation. ~3-line PR.

#### Priority 6 — Future S1264 follow-up — Authority enforce-mode arc

Switching WARN → ENFORCE requires (documented in S1264 handoff):
1. Symbol mapping exists (steps declare `action_classes_invoked`
   OR tool registry maps tool names to action_class)
2. ≥14 days clean warn-mode telemetry on N≥4 employees
3. False-positive rate ≤5% over ≥30 days
4. Per-employee `trust_ratio` ≥0.75 maintained
5. Manual operator review on ≥3 employees confirms contract-vs-reality

None blocking — separate arc when prerequisites met.

#### Priority 7 — Carryover backlog (S1264 list, unchanged)

| Item | Source | Severity |
|---|---|---|
| `_persist_to_summary` 2/3 dup consolidation | S1261 deferred | low |
| `_resolve_chris_user` generalization in morning_brief | S1261 deferred | low |
| `sync_celery_beat` orphan-handler revert trap (code fix) | S1258 mitigated via migration 0373 | medium |
| PA tool surface gaps — no `celery_inspect_tool`, `evidence_for_mission` default-to-latest | S1258 verification | low |
| `RIGBY.primary_chat_id` contract constant still stale | S1252 carryover | low — cosmetic |
| `Deliverable.create` defaults-to-completed upstream fix | S1252 carryover | low |

## Session metadata

- **Window:** 2026-06-30, ~3 hour active session
- **Rigby conversation:** `pa-3a226cd451494350` (created at S1265 open
  via `session_tool.create_fresh`; prior conv `pa-85960cfecf5e42d5`
  rotated at score 35/strongly_recommend_fresh after 38 turns / 19k
  tokens / 7 topics across S1258-1264 arc)
- **Verifier-loop pattern:** every PR routed to Rigby for SIGN
  (discovery + pre-PR + sometimes pre-merge). Caught at least 2
  design issues that would have shipped wrong otherwise (PR #2760
  ToolDispatcher coupling refactored to public-helper reconstruction;
  D3 auth gate flipped from IsAuthenticated to IsAdminUser).
- **Token budget:** modest. No SLO regressions, no test failures
  introduced.
