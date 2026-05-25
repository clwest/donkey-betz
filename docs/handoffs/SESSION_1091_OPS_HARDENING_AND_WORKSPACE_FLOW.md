---
originating_session: 1091
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1091 — Ops Hardening + Workspace/Deliverable Flow

**Date:** April 16, 2026
**Previous handoff:** [`SESSION_1090_DEMO_READINESS.md`](SESSION_1090_DEMO_READINESS.md)
**Status:** All 7 PRs merged to main, post-merge soak GREEN locally. Railway auto-deploy in flight. Session 1090's two SLO breaches closed at the source.

---

## What this session accomplished

Two work streams ran back-to-back, both initiated by Rigby's ops telemetry findings.

### Stream 1 — SLO breach remediation (PRs #1963, #1964)

Two SLOs were breaching at session start:
- `agent_timeout_rate`: 1.95% vs target ≤0.2%
- `pa_tool_success_rate`: 99.89% vs target ≥99.9%

Root causes turned out to be unrelated.

### Stream 2 — Workspace/Deliverable flow verification (PRs #1965 → #1969)

Started as "let's verify the workspace assignment pipeline doesn't orphan deliverables", became a 5-PR sprint covering observability, data correctness, UI surfacing, cross-channel field naming consistency, and per-workspace stats.

---

## All 7 PRs in chronological order

| PR | Title | Why it landed |
|----|-------|---------------|
| **#1963** | `fix(agents): enforce router wall-clock + harden heartbeat` | Direct `AgentRouter.route()` callers (artifact_execution, test harnesses, orchestrator fallback paths) had no wall-clock timeout — only the Celery wrapper enforced one. Hung executions sat until the 60-min cleanup watchdog reaped them, accounting for the `TIMEOUT_WATCHDOG_CLEANUP_*` signatures Rigby flagged. Also hardened `_router_heartbeat_loop` to survive 3 consecutive DB errors instead of dying on first (was killing heartbeat thread mid-execution → flatline → 60-min reap). New shared module `core/services/agent_timeouts.py` so tasks_agents and agent_router share one source of truth. |
| **#1964** | `fix(fullstack-agent): bump build_feature timeout to 600s, switch to gpt-5.2` | All 6 PA-tool failures in the prior 24h were identical: `APITimeoutError: Request timed out` at ~271s (just under the 300s read ceiling). Six autonomous "build me an entire production app" prompts dispatched in 3.5 hours by FullStackDeveloperAgent. Raised read timeout to 600s and migrated model to gpt-5.2 (platform default). |
| **#1965** | `fix(deliverables): close orphan paths + surface workspace_id in PA tool` | Three smoking guns: (1) `deliverable_tool.list` omitted workspace_id entirely → no PA-tool orphan auditing; (2) `clone_deliverable` always created orphans (didn't pass workspace FK); (3) Factory silently created orphans when no eligible workspace existed. Fix: added `workspace_id`/`workspace__name`/`is_orphan` + `orphans=true` filter to PA tool list; clone now inherits workspace + initiative; factory routes fallbacks to a per-user "Unassigned" sentinel bucket auto-created on first use. **Orphan rate now zero by construction.** |
| **#1966** | `fix(pa-schema): expose deliverable_tool orphans filter + hash params` | The new `orphans` param shipped in #1965 wasn't advertised in the PA tool schema sent to GPT-5.2, so the model never generated calls with that argument. Also: `_compute_schema_version()` only hashed tool names, so adding parameters didn't bump the version → the live-reload mechanism never fired. Now hash includes parameter shape too — any schema change auto-reloads. |
| **#1967** | `feat(ui): surface workspace assignment + Unassigned bucket in deliverables UI` | UI didn't render the new schema fields. Added: workspace badge per Deliverables card (red if orphan, amber if Unassigned, blue otherwise); Unassigned bucket sorted to top of WorkspaceSelectorModal with amber styling + "Triage" badge + clarifying subtitle. REST serializer also extended with `workspace_id`/`workspace_name`/`is_orphan` (the React side reads REST, not the PA tool). |
| **#1968** | `fix(pa-tool): alias workspace__name → workspace_name in deliverable list` | API surface inconsistency: PA tool returned `workspace__name` (Django ORM `.values()` artifact, double underscore), REST returned `workspace_name` (single underscore, dict-style). Both worked in their own consumers; cross-channel debugging would confuse anyone. One-line alias in `_sanitize_deliverable` so both keys ship together. Backwards compatible. |
| **#1969** | `feat(deliverables): per-workspace stats breakdown + orphan/unassigned counts` | Final P1 from Rigby's UX-gap triage. Adds `by_workspace` + `orphan_count` + `unassigned_count` to both REST stats and PA tool stats. New "Workspace Breakdown" card in DeliverablesTab below the existing 4-stat grid. Treats `orphan_count` (workspace_id IS NULL) and `unassigned_count` (lives in sentinel bucket) as DISTINCT — they're different failure modes. |

---

## Local-only fix (no PR — recorded rationale per "no fake on prod" policy)

**Autopilot DB drift:** Migration 0282 had an errant `DeleteModel('AutopilotAction')`. Migration 0284's idempotent `CREATE TABLE` RunPython was marked applied in `django_migrations` but the physical table never landed (likely a SAVEPOINT-wrapped CREATE got swallowed in a prior run). Un-faked migrations 0284→0291 forward via `migrate core 0283 --fake` then `migrate core`; tables that already existed (0288, 0290) were re-faked since their physical state matched the model. Table now exists with all 14 columns. `autopilot_tool.dry_run_report` works again.

**Discovery:** While un-faking, found 41 unapplied migrations on local from 0292 onward (`outreach_draft`, `close_pack`, `engagement_event`, `meeting`, `kill_switch`, `code_runner`, `vip_invite`, `llmcalllog_trace_id`, etc. through 0331). Per Rigby's recommendation, **left alone** — Chris's preference is test-on-Railway, and prod parity should be verified before normalizing local. Logged as a follow-up.

---

## What changed for future sessions

### New shared modules and patterns

- **`core/services/agent_timeouts.py`** — single source of truth for per-agent wall-clock timeouts. Both `core/tasks_agents.py` and `core/agent_router.py` now import `get_agent_timeout(agent_name)` from here. Add per-agent overrides here, not in either consumer.
- **Unassigned sentinel workspace** — `core/services/deliverable_factory._get_or_create_unassigned_workspace_id(user)` lazily creates a per-user `ProjectWorkspace` named `"Unassigned"` with `allow_autonomous_writes=True`. Anything created without an explicit workspace lands here instead of becoming an orphan.
- **`router_wall_clock` timeout signature** — new failure-signature class. Replaces `TIMEOUT_WATCHDOG_CLEANUP_*` for any direct `router.route()` caller that exceeds its per-agent ceiling. Watchdog cleanup signatures should now only fire on legitimate carryover from pre-merge runs (pre-restart). If a `TIMEOUT_WATCHDOG_CLEANUP_*` signature appears on a fresh execution, that means a dispatch path is bypassing both the Celery wrapper AND the router — investigate.
- **Schema-version hash includes parameters** — adding/changing a parameter on a PA tool now correctly bumps `SCHEMA_VERSION` and triggers `_get_live_tool_schemas` to reload without process restart.

### Process learnings worth remembering

- **PA tool changes need both Daphne AND celery restart.** Any edit to `core/services/td_handlers_*.py`, `core/services/tool_dispatcher.py`, or `core/services/pa_tool_schemas.py` requires `make stop && make start` AND `make celery-stop && make celery`. The celery-pa worker holds the dispatcher class in memory separately from Daphne.
- **REST-only changes need Daphne restart only.** No celery cycle required.
- **Frontend changes for the Daphne-served UI** at `localhost:8000` need `cd frontend && npm run build` THEN `make stop && make start`. Daphne caches `index.html` at startup. Vite dev server at `localhost:3000` would HMR live, but Chris uses Daphne.
- **Field name conventions across PA-tool vs REST surfaces:** Django ORM `.values('foo__bar')` produces double-underscore dict keys. REST serializers built by hand use single-underscore. When exposing the same field across both surfaces, alias inside `_sanitize_*` helpers so both keys ship together.
- **Orphan vs Unassigned are DIFFERENT counts.** Orphan = `workspace_id IS NULL` (regression alarm — should always be 0 post-#1965). Unassigned = lives in the sentinel triage bucket (informational volume, expected to be >0). Don't conflate them in stats output.

---

## Deliverables saved this session (Donkey Betz workspace)

| Title | ID | Purpose |
|-------|----|---------| 
| Rigby: Session 1091 Follow-ups | `ac87f650-3a8b-4cba-8201-fb0486d82e7a` | Six grooming-ready follow-up tickets with sequencing recommendation |
| Rigby: Deploy Broadcast: Session 1091 Ops Hardening | `b71f14a4-9c2a-4cd9-a754-649bdc4e9b00` | Cutoff timestamp + treat-pre-cutoff-as-historical guidance for cached agent contexts |
| Rigby: SOP v1: Executability Verification Checklist | `a4b00a82-00d3-4e8c-9fc2-ff9754fb8b53` | 5-test pass/fail checklist for deliverable workspace flow, run pre/post deploy |
| Rigby: UI Visibility Audit: Deliverables vs Workspace | `0f018ec8-55ec-4908-a486-ef888b0186f9` | Findings + fixes doc, closed with full Sprint A → A.5 → B → post-merge soak verification stamp |

---

## Open follow-ups for Session 1092+

From the Session 1091 Follow-ups deliverable (`ac87f650`):

1. **Verify Railway/prod migration parity** — local has 41 unapplied migrations (0292+ through 0331). Confirm prod is current via `db_health_tool.migrations` against Railway.
2. **Adopt "no fake on prod" migration policy** — document in `CLAUDE.md` or new `docs/topics/migration_policy.md`. Local fakes require recorded rationale; prod fakes require explicit approval.
3. **Audit LLM client construction for explicit request timeouts** — fail fast at the socket layer instead of waiting for the wall-clock kill.
4. **Decompose `build_feature` into per-component subtasks** — one prompt → entire production app will keep brushing whatever ceiling we set. Schema → API → frontend → integration as separate bounded calls. ~1 day of work.
5. **Governor budget gate for FullStackDeveloperAgent** — block "6 monster build_feature calls in 3.5 hours" patterns even when each call succeeds.
6. **`tool_calls_tool.list_failures` PA tool** — direct PA-tool access to `ToolCallRecord` so failure triage doesn't need Django shell round-trips.

Plus from session conversation:

7. **Run the SOP v1 checklist against Railway prod** — once auto-deploy settles, repeat the 5-call smoke battery against production URLs to confirm parity. The `orphans=true` filter and `workspace_orphans` should both register on prod after the schema-version hash auto-reload.
8. **Investigate why ResearchAgent volume is amplifying dependency instability** (carried from Session 1090).

---

## Known carryforward concerns (not new this session)

- **CodeGeneratorAgent** still blocked (1051.6h) on "No codebase access in Railway sandbox." Either add TTL or unblock — Rigby's autopilot dry-run keeps surfacing it.
- **QROI: $45.53 spend / 0 outcomes (24h).** PersonalAssistant is the dominant cost ($45.47). Most of this is autonomous work that didn't tie back to a measurable user-facing outcome. Either improve outcome attribution or trim autonomous spend.
- **3 missing API keys** (DeepSeek, Replicate, TheOdds) — known.
- **content.0046 migration unapplied** — known (this is among the 41).

---

## Service state at end of session

- **Daphne** running on `localhost:8000`, serving `index-BGHgntWk.js` (build sha `a9063296` from #1967, manifest auto-updated by postbuild script)
- **Celery:** default + pa + long-running + broadcast workers + beat scheduler — all up
- **Redis:** running daemonized
- **Health endpoint:** `{"ok": true}`
- **Branch:** `main`, up-to-date with `origin/main`
- **Working tree:** clean except for build artifacts in `frontend/dist/` (will be committed in the wrap PR), pre-existing untracked dirs (`backend/`, `sports/arbitrage/`, `sports/odds/`, `norman-handyman-mvp/`), and a stale `.pyc` (ignorable)
