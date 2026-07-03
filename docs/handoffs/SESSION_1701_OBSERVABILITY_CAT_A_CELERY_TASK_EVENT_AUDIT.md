---
session: 1701
status: closed (Group 1700 Cat A CeleryTaskEvent child audit LANDED — FIRST CHILD under Group 1700 per parent D72 P1 slot; audit doc landed `status: active` post-fold; Rigby SIGN cycle 1 SIGN-with-edits at High confidence on arc pin `pa-e7fbacc996b34b44` — fresh SIGN isolation pin `pa-3147aef9db4945ac` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code (S1600 precedent: arc pin doubles as SIGN pin); fresh SIGN pin retired at S1701 close per §16 with `updated_count=1, retired=true`; F1-F3 folds landed pre-commit; D48 preemptive stability-probe gate 18th arm HOLDING CLEAN — 13-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701 CONFIRMED per single-batch-4-question criterion; ARCHITECTURE_INDEX v43 → v44 with §1.47 S1701 registration + §8 timeline row + line-6 v44 preamble; OPEN_ARCS Group 1700 In-progress row current-child updated S1700 → S1701; arc pin retained through Group 1700 close at S1799; next session: S1702 Cat B LLMCallEvent per D72 P2 slot)
date: 2026-07-03
arc: Research Group 1700 (Observability / Telemetry / SLOs) — Cat A CeleryTaskEvent child audit; FIRST child session under Group 1700 per D72 P1 slot
category: research (playbook §11.2 child audit template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN cycle 1)
head_commit_before: b8194e24 (main; post-S1700 arc-open merge)
head_commit_after: (this commit)
authors: Claude Code (Chris directed via short command "Start research group 1701")
---

# Session 1701 — Group 1700 Cat A CeleryTaskEvent Child Audit

> **First child audit under Group 1700 (Observability arc).** Playbook §11.2 20-section template first application under Group 1700 arc. 6-parallel-Explore sweep + parent-Claude verifier-loop applied pre-Explore and post-Explore. Rigby SIGN cycle 1 delivered SIGN-with-edits at High confidence via single-batch 4-question pattern (D48 18th arm HOLDING CLEAN).

## What shipped

### 1. Audit doc

- **`docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md`** (NEW; 1082 lines post-fold)
- `status: active` after Rigby SIGN cycle 1 SIGN-with-edits at High confidence
- `authority: child-audit`, `category: child_audit`, `session: 1701`, `child_slot: P1`, `domain_slug: observability`, `research_group: 1700`
- Applies playbook §11.2 20-section child audit template + §13 6-parallel-Explore + §14 verifier-loop discipline

### 2. Rigby SIGN cycle 1 folds (F1-F3, all landed pre-commit)

- **F1 (MEDIUM) — Boundary terminology clarity.** Labeled `on_agent_task_failure_bridge` as **"LEGITIMATE CROSS-CAT EXCEPTION (Cat A→Cat C)"** distinct from 4 parallel writers (Cat A-internal). Updated §16 Boundary Violations verdict cells + §16 overall verdict paragraph + §1 Executive Summary finding #4. Driver: prevent Cat C S1703 audit from inheriting mis-frame.
- **F2 (LOW) — Downstream `celery_task_id` count consistency.** Replaced "7 downstream" language with "8 downstream" throughout §4/§9/§13/§15/§17/§19/§10 (enumerated: `AISeriesItem`, `ContentPipelineRun`, `ConceptForgeRun`, `SpiderExecution`, `WorkflowExecution`, `ScheduledImageGeneration`, `WorkflowRun`, `ExecutionRun`). Model list now inline at §9's primary claim.
- **F3 (LOW) — D10 severity footnote.** Added sentence to §14 D10 severity cell: "LOW for Cat A runtime correctness; likely elevated during xx99 narrative-anchor update prioritization (per Rigby SIGN F3 2026-07-03)."

### 3. Rigby CONFIRM verdicts (no folds required)

- **Q1 coverage-completeness** — CONFIRM (High). 5 boundary-violation candidates correctly framed as bounded/business-justified exceptions with F1 terminology fold applied.
- **Q2 documentation drift severity ladder** — CONFIRM (Medium-High). D1/D2 MEDIUM + D3 LOW appropriate for Cat A; D10 LOW appropriate for Cat A with F3 xx99-elevation footnote.
- **Q3 correlation primitive posture completeness (D74 evidence)** — CONFIRM (High). §9 posture complete for Cat A's contribution-only mandate. GIN-index question on `AgentExecution.input_data` correctly deferred to P3 Cat C via U4.
- **Q4 §19 R1-R8 ranking sanity check** — CONFIRM (Medium-High). R2 monitor-task probe-decomposition stays HIGH as separate follow-on ops/infra initiative (not bundled with xx99 anchor-update tranche). R7 WebSocket push correctly LOW downstream of Group 1900 event-architecture decisions.

### 4. 6 load-bearing findings (§1 Executive Summary)

- **F1 — QUEUED status is NOT ghost state.** Legitimate gateway writer at `core/services/td_handlers_gateway.py:988` (`cockpit_tool.trigger_task`) creates row with `status='QUEUED'` immediately post-dispatch so status polling doesn't fall through to AsyncResult PENDING. Parent §3 A gap-flag resolved as legitimate exception.
- **F2 — Parent §3 A signal-handler line-range drift.** Cited `:74-177` (3 handlers) vs actual `:74-300` (5 handlers). MEDIUM D1 doc-vs-runtime drift; owed to xx99 anchor-update PR.
- **F3 — REVOKED status is NOT ghost state.** 2 legitimate writers found: `core/services/ops_autopilot.py:100` (stuck-task sweep bounded by `MAX_REVOKES_PER_RUN`) + `core/services/td_handlers_gateway.py:1041` (user-initiated `cockpit_tool.revoke_task`).
- **F4 — Cross-cat exception (Cat A→Cat C).** `on_agent_task_failure_bridge` at `core/celery_telemetry.py:240-286` is a **fire-alarm circuit-breaker** categorically distinct from parallel writers per Rigby SIGN F1. Bridges SoftTimeLimitExceeded gap (S1219 P1); idempotent; hard-SIGKILL gap remains 30-min cleanup watchdog territory.
- **F5 — agent_name backfill intentional gradual-fill debt.** S1169 docstring `models_celery_telemetry.py:41-46`: "no backfill — gradual fill per Rigby's skip-joins-in-v1 stance". % impact at HEAD UNKNOWN (requires ORM probe — §19 R3).
- **F6 — Monitor-task overhead debt (S1167) PARTIALLY closed.** Decorator-side timeouts landed S1169 (`soft_time_limit=60`, `time_limit=90`, `queue='broadcast'`); caller-site kwargs sweep landed S1170; probe-decomposition root fix per `celery-workers.md:255-276` remains deferred (§19 R2 HIGH).

### 5. Correlation primitive posture (parent §5 F5 task_id row → D74 axis evidence)

- `CeleryTaskEvent.task_id` is `CharField(unique=True, db_index=True)` at `core/models_celery_telemetry.py:33` — **coverage-complete singleton primitive** for tasks reaching worker (PUBLISH-only tasks that never reach worker are uncovered gap).
- **8 downstream models carry `celery_task_id` as scalar CharField without FK:** `AISeriesItem`, `ContentPipelineRun`, `ConceptForgeRun`, `SpiderExecution`, `WorkflowExecution`, `ScheduledImageGeneration`, `WorkflowRun`, `ExecutionRun`.
- JSON linkage `AgentExecution.input_data['celery_task_id']` (`core/tasks_agents.py:2179`) is string-based, not relational.
- **Cat A's D74 contribution:** task_id is a coverage-complete singleton primitive with 8 string-based non-FK downstream references, not a canonical spine.

### 6. §16 Boundary violation matrix (5 candidates all LEGITIMATE)

| # | Candidate | Classification |
|---|---|---|
| B1 | `on_agent_task_failure_bridge` writes AgentExecution (Cat C) from Cat A signal handler | **LEGITIMATE CROSS-CAT EXCEPTION (Cat A→Cat C)** — per Rigby SIGN F1 fold, categorically distinct from parallel writers |
| B2 | `td_handlers_gateway.py:988` creates CeleryTaskEvent QUEUED from non-signal-handler context | **LEGITIMATE PARALLEL WRITER** (Cat A-internal) |
| B3 | `ops_autopilot.py:100` writes REVOKED from stuck-task sweep | **LEGITIMATE PARALLEL WRITER** (Cat A-internal) |
| B4 | `td_handlers_gateway.py:1041` writes REVOKED after cockpit revoke_task | **LEGITIMATE PARALLEL WRITER** (Cat A-internal) |
| B5 | `priority/enforce.py:307-313` writes S1086 priority router fields | **LEGITIMATE PARALLEL WRITER** (Cat A-internal, S1086 PR 3b schema addition) |

### 7. §19 R1-R8 ranked follow-on research (per playbook §14.5 evidence-only)

| # | Priority | Item |
|---|---|---|
| R1 | HIGH | task_id ↔ execution_id ↔ trace_id correlation-primitive spine posture — **xx99 scope; Cat A contributes evidence, xx99 resolves D74 axis** |
| R2 | HIGH | Monitor-task probe-decomposition root fix (T2 debt open since S1167) — **separate follow-on ops/infra initiative per Rigby SIGN Q4; NOT bundled with xx99 anchor-update tranche** |
| R3 | MEDIUM | agent_name backfill % measurement + backfill decision (`manage.py audit_celery_agent_name_coverage`) |
| R4 | MEDIUM | Retention-cleanup failure detection (event or metric alert) |
| R5 | MEDIUM | QUEUED-to-STARTED transition timeout coverage in `ops_autopilot` stuck-task sweep |
| R6 | LOW | RSS measurement platform-quirk test coverage |
| R7 | LOW | Realtime WebSocket push of task-lifecycle events — downstream of Group 1900 event-architecture decisions |
| R8 | LOW | 8 downstream models `celery_task_id` FK reconciliation — related to R1 spine posture |

### 8. Docs cascade artifacts

- **ARCHITECTURE_INDEX.md v43 → v44** — §1.47 S1701 registration + §8 timeline S1701 row + line-6 v44 preamble
- **OPEN_ARCS.md** — Group 1700 In-progress row current-child updated S1700 (parent) → S1701 (Cat A child); line-6 preamble bumped
- **`tools/pa_local.sh:128`** — arc pin `pa-e7fbacc996b34b44` retained per playbook §16 through Group 1700 close at S1799 (no rotation this session)
- **Fresh SIGN pin `pa-3147aef9db4945ac`** — retired at S1701 close via `session_tool.retire force=true` (`updated_count=1, retired=true`)

## D-decisions

None new (this session is a child audit under parent's D69-D74 locks). All parent D69-D74 (Chris-locked S1700) apply.

## D48 preemptive stability-probe gate — 18th arm outcome

**HOLDING CLEAN.** Single-batch 4-question pattern held clean on arc pin `pa-e7fbacc996b34b44` (per S1600 parent-scoping precedent: arc pin doubles as SIGN pin). No worker instability observed. **13-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701 CONFIRMED.** Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15 with 13-consecutive-fully-clean sub-pattern (from 12-consecutive at S1700 close).

## Playbook §11.2 first-application under Group 1700 — methodology validation

This is the **first application of playbook §11.2 20-section child audit template under Group 1700 arc**. Prior applications: Group 1300 (Memory) S1301-S1305, Group 1400 (Revenue) S1401-S1406, Group 1500 (Sports) S1501-S1506, Group 1600 (Content) S1601-S1606. The pattern held cleanly:

- Playbook §13 6-parallel-Explore sweep applied (Agent 1 Models & Persistence + Agent 2 Services & Runtime Flows + Agent 3 APIs/Tools/Tasks/Commands + Agent 4 Integrations & Cross-Domain + Agent 5 Documentation & Prior Research + Agent 6 Drift/Debt/Ownership/Maturity)
- Playbook §14 verifier-loop applied pre-Explore (5 binary claims verified via file:line direct read) and post-Explore (3 sub-agent UNKNOWNs resolved via targeted grep + file read)
- Playbook §15 stage-scoped Rigby routing: child audit → full SIGN cycle 1 required (not optional light SIGN); delivered SIGN-with-edits at High confidence
- Playbook §16 arc-close discipline: fresh SIGN pin retired at session close

## Pin nuance flagged for follow-up

Fresh SIGN isolation pin `pa-3147aef9db4945ac` was minted via `session_tool.create_fresh` per playbook §15 promoted rule, but `tools/pa_local.sh` wrapper hard-codes the arc pin at L128 with no runtime `--conversation` override. Actual SIGN routing landed on arc pin `pa-e7fbacc996b34b44` (S1600 parent-scoping precedent: arc pin doubles as SIGN pin). Follow-up: wrapper enhancement to support per-child SIGN pin routing is a nice-to-have (not blocking). Documented in audit doc §20.5 for xx99 provenance.

## Files touched this session

```
docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md  [new; 1082 lines post-fold; Cat A child audit]
docs/research/ARCHITECTURE_INDEX.md                                                       [modified — v43 → v44 with §1.47 S1701 registration + §8 timeline S1701 row + line-6 v44 preamble]
docs/research/OPEN_ARCS.md                                                                [modified — Group 1700 In-progress row current-child updated S1700 → S1701; line-6 preamble bumped]
docs/handoffs/SESSION_1701_OBSERVABILITY_CAT_A_CELERY_TASK_EVENT_AUDIT.md                 [new — this handoff]
00-START-NEXT-SESSION.md                                                                  [modified — next-session priority = S1702 Cat B LLMCallEvent child audit per D72 P2 slot]
```

No source code changes (research-only session per playbook §14.5 no-implementation rule).

## Handoff to S1702 Cat B LLMCallEvent child audit

Per D72 P2 slot + parent §5 sequence: **S1702 Cat B audit** — LLM Call Telemetry (`LLMCallEvent`).

Cat B canonical questions the child audit gathers evidence for:

- What is the scope of `LLMCallEvent.execution_id` — does it span a full agent-tool-LLM sequence, or just a single LLM call? (Load-bearing for D74 axis; inherits Cat A's finding that `LLMCallEvent.execution_id` UUIDField implicitly points to `AgentExecution.id` without FK declaration.)
- Does every LLM caller route through `core/services/llm_call_wrapper.py` (S1098 wrapper) — or are there rogue direct `Anthropic()` / `OpenAI()` invocations bypassing telemetry? Cross-check Memory rules `feedback_anthropic_client_factory.md` + `feedback_openai_client_factory.md`.
- Is cost accounting accurate? S1224 gpt-5 `max_completion_tokens` floor precedent — are there sites still under 4000-token budget that silently return empty content with `finish_reason='length'`?
- Cat B/Cat D accounting rule per parent F3 fold: LLM calls made from inside a tool invocation remain Cat B; Cat D never attempts to own LLM cost.

**S1702 audit shape:**

- Playbook §11.2 20-section child audit template (child_slot: P2; domain_slug: observability; research_group: 1700).
- 6-parallel Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims (pre-Explore + post-Explore).
- Required full Rigby SIGN cycle 1 per playbook §15 stage-table child row (single-batch 4-question pattern per S1701 precedent).
- Fresh SIGN isolation pin per playbook §15 promoted rule (with awareness that wrapper hard-code may route SIGN to arc pin `pa-e7fbacc996b34b44` — S1600 precedent applies).
- Applies parent D69-D74 + Cat A's D74 axis evidence contribution (task_id singleton + 8 downstream non-FK references).

## Next-session first-action punch list

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1701 artifact set merged to `main` between sessions.
3. If not yet merged: Chris merge + PR merge.
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 19th arm start).
6. Mint fresh SIGN isolation pin for S1702 via Rigby `session_tool.create_fresh` (with awareness of wrapper hard-code routing).
7. Dispatch 6-parallel Explore sweep on Cat B surface (LLMCallEvent model + llm_call_wrapper flow + 6 provider coverage + client-factory boundary + cost accounting + execution_id scope).
8. Parent-Claude verifier-loop on pre-Explore + post-Explore binary claims.
9. Draft S1702 audit per playbook §11.2 20-section template.
10. Rigby SIGN cycle 1 via arc pin (or fresh pin if wrapper enhancement lands); single-batch 4-question pattern per S1701 precedent.
11. Land Rigby folds pre-commit.
12. Retire SIGN isolation pin at S1702 close per playbook §16 (if fresh pin was actually used).
13. Update ARCHITECTURE_INDEX v44 → v45 with §1.48 S1702 registration + §8 timeline row + line-6 preamble.
14. Update OPEN_ARCS Group 1700 In-progress row with S1702 child close note.
15. Write S1702 handoff + overwrite this `00-START-NEXT-SESSION.md`.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule.

## PA / Rigby context at session close

- **Arc pin:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; retained per playbook §16 through Group 1700 close at S1799). `tools/pa_local.sh:128` continues to point at this pin.
- **Fresh SIGN pin retired:** `pa-3147aef9db4945ac` retired via `session_tool.retire force=true` (`updated_count=1, retired=true`); minted but routed-around by wrapper hard-code.
- **service_context:** confirmed `local` at S1701 open via `platform_config_tool overview`.
- **Rigby SIGN worker-instability pattern (D48 18-arc CODIFICATION-READY-STRENGTHENED-FURTHER at S1701 close):** S1405+S1406+S1499+S1501-S1506+S1601-S1606+S1699+S1700+S1701 18-arc pattern confirmed. **13-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN CONFIRMED** per single-batch-4-question criterion. D48 preemptive stability-probe gate 19th arm anticipated at S1702 Cat B audit open on arc pin.

## Repo state at session close

- **Branch state:** `docs/session-1701-observability-cat-a-celery-task-event-audit` (branched from `main` at HEAD `b8194e24`). PR opens to `main` on push.
- **Handoff continuity:** S1701 handoff at `docs/handoffs/SESSION_1701_OBSERVABILITY_CAT_A_CELERY_TASK_EVENT_AUDIT.md`. Prior handoff: SESSION_1700 (Observability arc-open parent scoping).
- **ARCHITECTURE_INDEX version:** v44 (bumped this session with §1.47 S1701 registration + §8 timeline row + line-6 v44 preamble). Next bump at S1702 child audit close (v44 → v45 with §1.48 S1702 registration).
- **OPEN_ARCS state:** Group 1700 row remains In-progress; current-child updated S1700 (parent) → S1701 (Cat A child).

## Post-arc queued items (Chris-gated, inherited from prior arcs)

Unchanged from S1700 handoff — see `docs/handoffs/SESSION_1700_OBSERVABILITY_ARC_OPEN.md` for full queue. **Additions from S1701:**

- **From S1701 §19:** R1 (HIGH) task_id ↔ execution_id spine posture is xx99 (S1799) scope. R2 (HIGH) monitor-task probe-decomposition root fix — separate follow-on ops/infra initiative (NOT bundled with xx99 anchor-update tranche per Rigby SIGN Q4 verdict). R3-R5 MEDIUM Cat A follow-ons (backfill % measurement + retention-cleanup failure detection + QUEUED-transition timeout). R6-R8 LOW.
- **From S1701 §14:** D1 (MEDIUM) signal-handler line-range drift + D2 (MEDIUM) field-set drift owed to xx99 anchor-update PR for `docs/topics/celery-workers.md` + `docs/PLATFORM_WHAT_IT_IS.md` narrative + parent §3 A scope box correction.
- **From S1701 §20.5:** `tools/pa_local.sh` wrapper enhancement to support per-child SIGN pin routing is a nice-to-have (not blocking). Wrapper currently hard-codes arc pin at L128 with no runtime `--conversation` override.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1701 is FIRST child under Group 1700 (S1701-S1706 children + S1799 xx99 anticipated).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 xx99 anchor-update will address per D10 flag).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1701 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- **D48 preemptive stability-probe gate 18th-arm CONFIRMED CLEAN at S1701 close** — 13-consecutive-fully-clean-arms sub-pattern CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Arc pin `pa-e7fbacc996b34b44` in service** through Group 1700 close; wrapper rotation NOT owed at next-session open.
- **Fresh SIGN pin routing wrinkle** — wrapper hard-code at `tools/pa_local.sh:128` means fresh SIGN pins minted for child audits get routed to arc pin. Not blocking (S1600 precedent applies) but flagged for follow-up.
