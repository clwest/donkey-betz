# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1700 IN-PROGRESS; S1703 CAT C CLOSED; NEXT = S1704 CAT D

The local wrapper at `tools/pa_local.sh:128` points at Group 1700 arc pin. **Active arc pin state after S1703 close:**

- **Active Group 1700 arc pin: `pa-e7fbacc996b34b44`** (Rigby `session_tool.create_fresh` at S1700 open — title "Session 1700 — Observability research group (kickoff)"). Continues in service across Group 1700 arc (S1701 CLOSED + S1702 CLOSED + S1703 CLOSED + S1704-S1706 children pending + S1799 xx99 canonical summary). SIGN routing at S1703 landed on arc pin per S1600/S1700/S1701/S1702 parent-scoping precedent (arc pin doubles as SIGN pin; fresh SIGN pin `pa-f1a30b7ed5bb4042` minted per playbook §15 but routed-around by wrapper hard-code at L128).
- **Retire owed at next-session open (S1703 close):** Fresh SIGN isolation pin `pa-f1a30b7ed5bb4042` (was unused because wrapper hard-code routed SIGN to arc pin; retire per playbook §16 discipline).
- **Retired at S1702 close:** Fresh SIGN isolation pin `pa-c3927ab78c52479a`.
- **Retired at S1701 close:** Fresh SIGN isolation pin `pa-3147aef9db4945ac`.
- **Retired at S1700 open:** Group 1600 arc pin `pa-f52acf3f8d394faa`.
- **Retired earlier at S1699 close:** SIGN isolation pin `pa-846b6c4a532947c3`.
- **Retired earlier at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83`.
- **Retired earlier at S1605-S1601 closes:** SIGN isolation pins `pa-b1b26f4f35474df8` + `pa-4ce64003711de4f1` + `pa-8af9063864bf4a7f` + `pa-1c5298d807d7a1d2` + `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

**No wrapper rotation owed at next-session open** — arc pin in service through Group 1700 close at S1799.

## READ THIS THIRD — S1703 CAT C AGENT EXECUTION AUDIT LANDED; NEXT = S1704 CAT D TOOLCALLRECORD

Session 1703 shipped the **Group 1700 Cat C AgentExecution child audit** at `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md` (`status: active`, `category: child_audit`, `session: 1703`, `child_slot: P3`, `domain_slug: observability`, `research_group: 1700`, `head_commit: 9612ea95`, `authority: child-audit`; ~1090 lines post-fold; playbook §11.2 20-section child audit template THIRD application under Group 1700; playbook §13 6-parallel-Explore sweep + §14 verifier-loop applied pre-Explore + post-Explore; Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence — F1-F4 folds landed pre-commit). **15-consecutive-fully-clean-arms sub-pattern CONFIRMED via D48 20th arm** on arc pin `pa-e7fbacc996b34b44` (single-batch 4-question pattern per S1701/S1702 precedent).

**9 load-bearing findings locked in S1703 audit §1 Executive Summary:**

- **F1 (CRITICAL, §17)** — 3-class landmine resolves as 1-alive + 2-dead at HEAD via Django app registry check (`apps.get_app_config('intelligence').get_models()` shows only `core.AgentExecution` registered; both intelligence-side class bodies are unreachable dead code — `intelligence/models.py:587` package-shadowed by `intelligence/models/` directory + `intelligence/models/agent_execution.py:11` not re-exported from `__init__.py`); intelligence-side canonical is `intelligence.ActionPlanExecution` (S1243 migration `0003_session_1243_rename_agentexecution_to_actionplanexecution.py` RenameModel; 0 rows at rename time; data-safe).
- **F2 (CRITICAL, §14)** — S287 deprecation notice at `core/models_unified_system.py:882-887` is STALE and REVERSED — points at renamed `agents.AgentTaskExecution` per S1244 PR #2685 (commit `2d65b44f`); S1084 audit block at lines 993-1014 (commit `0d0afd1d`) is canonical override.
- **F3 (MEDIUM, §14)** — Parent §3.C mislocates write path — BaseAgent has no `route()` method; delegates via `self.agent_router.route()` at `base_agent.py:948`; canonical write path is `AgentRouter._create_execution_record()` at `agent_router.py:2787-2960` with lazy import at :2814 + `AgentExecution.objects.create` at :2921.
- **F4 (CRITICAL, §14)** — PA path zero AgentExecution coverage (`unified_pa_entrypoint.py` writes 0 rows; 1 comment-only reference at :6050; analog to S1702 Cat B F2).
- **F5 (MEDIUM, §15)** — No date-based retention. `cleanup_stale_agent_executions` at `tasks_agents.py:1554-1654` is stuck-heartbeat watchdog (30-min beat cadence, 60-min threshold), not analog to Cat A `CELERY_TASK_EVENT_RETENTION_DAYS` or Cat B sibling `cleanup_llm_call_logs`.
- **F6 (HIGH, §17)** — Cat D correlation gap. `ToolCallRecord` at `core/models_tool_calls.py:19-131` has `trace_id` + `conversation_id` + `agent_name` but NO `execution_id` field (verifier-loop grep 0 hits). Cross-cat correlation Cat D ↔ Cat C is trace_id semantic match only.
- **F7 (MEDIUM, §9)** — `input_data['celery_task_id']` JSON-path unindexed at HEAD. Writers at `tasks_agents.py:2274, 2280`. S1701 §9 U4 candidate confirmed.
- **F8 (MEDIUM, §10)** — 4 post_save receivers on `core.AgentExecution` (`rigby_delegation_signals:131` + `agent_execution_bridge:317` + `experiment_linker:256` + `human_attention_bridge:578`); watchdog + cancel paths use `.update()` bypassing signals — partial silence.
- **F9 (D74 axis contribution, §9)** — Cat C owns TWO cross-model spine primitives: `execution_id` (AgentExecution.id; 6 downstream carriers) + `trace_id` (S843 orchestration UUID; router-path-only writer via `TraceAttachmentService` per Rigby SIGN F1 fold — Celery-wrapper path does NOT thread; PA path writes nothing). Choice-point for xx99 among 4 posture options A/B/C/D. Cat A `task_id` is a THIRD spine candidate on the Cat A side.

**§9 Correlation-primitive posture (D74 axis evidence contribution):** Cat C owns TWO cross-model spine primitives. Router path writes trace_id via `TraceAttachmentService.resolve_trace_id(context)` at `agent_router.py:2850-2851, :2910`; Celery-wrapper writer path (`_impl_execute_agent_task` in `core/tasks_agents.py:2114+`) does NOT thread trace_id (verifier-loop grep 0 create-site hits); PA path writes nothing (F4). Option A (execution_id canonical) requires 2 gap-closures (PA path + ToolCallRecord.execution_id addition); Option B (trace_id canonical) requires 3 gap-closures (Celery-wrapper writer + PA path + LLMCallEvent.trace_id addition). Option A is smaller schema-level lift; Option B is closer to S843 orchestration semantics.

**§16 Boundary violation matrix: 6 candidates all LEGITIMATE.** Primary writer at `agent_router._create_execution_record`; companion writer at `tasks_agents._impl_execute_agent_task` per S1084 audit; heartbeat + cancel + timeout writers all Cat C-internal; ONE legitimate cross-cat exception `on_agent_task_failure_bridge` (Cat A→Cat C, S1701 F4 fire-alarm circuit-breaker inherited); 4 documented signal handlers write Cat C→Cat E + Learning + Experiment + Human-Attention side effects; ONE dead-code writer file (`core/agent_execution_wrapper.py` 97 lines; zero production callers verified per feedback_verify_before_deleting_dead_code memory rule).

**Maturity STABLE for router-covered surface + PARTIAL overall + Risk HIGH.**

**Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence** on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-f1a30b7ed5bb4042` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code — S1600/S1700/S1701/S1702 precedent applies). **F1-F4 folds landed pre-commit:**

- **F1 (Medium)** — trace_id writer-of-record + propagation expectations added to §9 D74 axis contribution paragraph (router path writes trace_id; Celery-wrapper does NOT; PA path writes nothing; Option A vs Option B posture-lift analysis added).
- **F2 (Low)** — D4 drift severity escalated MEDIUM → HIGH ("dead-code misclassification risks wrong remediation, not just documentation confusion").
- **F3 (Low)** — §9 spine-candidate wording clarified — replaced ambiguous "Cat C does NOT own a Cat A-style task_id-analog cross-model spine" with "Cat C's spine candidates are execution_id + trace_id; Cat A's spine is task_id".
- **F4 (optional Low)** — §19 R2 boundary guard added ("No deprecation ADR authored in Cat C; xx99 owns consolidation direction. R2 remains posture decision + evidence-plan needed and does NOT authorize model deletion or migration merge at S1703 close").

**Rigby CONFIRM verdicts (no folds required beyond F1-F4):** Q1 coverage-completeness Medium-High + Q2 drift-severity Medium (only D4 escalation needed) + Q3 D74 axis correctness High + Q4 R1-R10 ranking + xx99 scope discipline Medium-High.

**Session close artifacts committed at S1703 close:**

```
docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md  [new; ~1090 lines post-fold; Cat C child audit; F1-F4 folds landed pre-commit; THIRD child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                    [modified — v45 → v46 with §1.49 S1703 registration + §8 timeline S1703 row + line-6 v46 preamble]
docs/research/OPEN_ARCS.md                                                             [modified — Group 1700 In-progress row current-child updated S1702 → S1703; line-6 preamble bumped]
docs/handoffs/SESSION_1703_OBSERVABILITY_CAT_C_AGENT_EXECUTION_AUDIT.md                 [new — S1703 handoff]
00-START-NEXT-SESSION.md                                                                [modified — this file; S1703 Cat C CLOSED; next-session priority = S1704 Cat D ToolCallRecord]
```

Handoff: `docs/handoffs/SESSION_1703_OBSERVABILITY_CAT_C_AGENT_EXECUTION_AUDIT.md`.

### NEXT-SESSION MISSION — S1704 CAT D TOOLCALLRECORD CHILD AUDIT (D72 P4 slot)

Per D72 P4 slot + parent §5 sequence: **S1704 Cat D audit** — ToolCallRecord.

Cat D canonical questions the child audit gathers evidence for:

- Do all 74 enabled AGENT_MAP agents actually write ToolCallRecord on all tool calls at HEAD? Does the managed-agent path write? The orchestration-agent path? The PA-dispatch path (PA tools invoked via `unified_pa_entrypoint`)?
- Are there wrapped-tool call sites (delegation between agents) that skip the wrapper?
- Does the S970 `__init_subclass__()` auto-wrap actually cover all subclasses at runtime?
- Does the S1115 all-return-path fix survive at HEAD (regression check)?
- **Inherits from S1703 F6:** Should ToolCallRecord get an `execution_id` UUIDField (nullable non-FK per LLMCallEvent posture)? Or is trace_id semantic join the canonical contract? Xx99 R3 posture question.
- **Inherits from S1702 F9 + parent §3.D F3 accounting rule:** LLM calls made from inside tools remain Cat B, but how does the dedup contract work at schema level? ToolCallRecord has NO `tool_call_id` column even though parent §3.D cites it as dedup key.
- **Inherits from S1701 F5:** Does agent_name backfill / dimension apply here (matching S1169 pattern)?
- **Inherits from S1703 F8 partial-signal-silence pattern:** Are ToolCallRecord writers observably-idempotent, or do they exhibit similar `.update()` bypass gaps?

Per parent §3.D boundary discipline: **P4 catalogs tool-call telemetry writer coverage + names cross-cat correlation contract vs Cat C + evaluates S970 wrapper survival at HEAD; ADR to add `execution_id` FK OR formalize `trace_id` semantic join is post-arc T-slot per §6.3 parked candidate.** Do NOT attempt to design the correlation schema change in S1704.

**S1704 audit shape:**

- Playbook §11.2 20-section child audit template (child_slot: P4; domain_slug: observability; research_group: 1700).
- 6-parallel-Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims (pre-Explore + post-Explore).
- **Required full Rigby SIGN cycle 1** per playbook §15 stage-table child row (not optional light SIGN — child audit is research finding).
- Fresh SIGN isolation pin per playbook §15 promoted rule (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN routing will land on arc pin per S1700/S1701/S1702/S1703 wrapper hard-code precedent unless wrapper enhancement lands).
- Applies parent D69-D74 + Cat A S1701 §9 axis evidence + Cat B S1702 F9 axis contribution + Cat C S1703 F9 axis contribution.

Session flow at next-session open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1703 artifact set merged to `main` between sessions.
3. If not yet merged: Chris merge + PR merge.
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 21st arm start).
6. **Retire fresh SIGN isolation pin `pa-f1a30b7ed5bb4042`** from S1703 via Rigby `session_tool.retire` per playbook §16 discipline.
7. Mint fresh SIGN isolation pin for S1704 via Rigby `session_tool.create_fresh` (title: "Session 1704 — Group 1700 Cat D ToolCallRecord audit — SIGN isolation").
8. Dispatch 6-parallel Explore sweep on Cat D surface (ToolCallRecord model + S970 `__init_subclass__` auto-wrap + tool_dispatcher registry + PA path coverage + S1115 all-return-path fix regression + trace_id-vs-execution_id correlation contract).
9. Parent-Claude verifier-loop on any pre-Explore binary claims.
10. Draft S1704 audit per playbook §11.2 20-section template.
11. Rigby SIGN cycle 1 (single-batch 4-question pattern per S1701/S1702/S1703 precedent).
12. Land Rigby folds pre-commit.
13. Retire SIGN isolation pin at S1704 close per playbook §16.
14. Update ARCHITECTURE_INDEX v46 → v47 with §1.50 S1704 registration + §8 timeline row + line-6 preamble.
15. Update OPEN_ARCS Group 1700 In-progress row with S1704 child close note.
16. Write S1704 handoff + overwrite this `00-START-NEXT-SESSION.md`.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. ToolCallRecord.execution_id addition + S970 wrapper coverage remediation are post-arc T-slot per parent §3.D boundary discipline + §6.3 parked candidate.

### Post-arc queued items (Chris-gated, inherited from prior arcs + additions from S1703)

- **From S1703 §19:** R1 (HIGH) F4 PA path AgentExecution coverage + R2 (HIGH) F1 + F2 landmine + docstring cleanup ADR (xx99 evidence-plan framing only per Rigby SIGN F4 boundary guard — Cat C does NOT author ADR) + R3 (HIGH) F6 ToolCallRecord ↔ AgentExecution correlation posture + R4 (MEDIUM) dedicated PA `execution_history_tool` + admin registration + `.update()` signal instrumentation + R5 (MEDIUM) 3-hop correlation chain implementation + R6 (MEDIUM) retention policy + R7 (LOW) CASCADE vs SET_NULL on Agent + User FKs + R8 (LOW) tokens_used + cost denorm reconciliation with Cat B + R9 (LOW) dead-code sweep for `core/agent_execution_wrapper.py` + R10 (LOW) `AgentTaskExecution` (0 rows since S1244) posture cross-arc handoff.
- **From S1703 §14:** D1 CRITICAL (S287 stale docstring) + D2 MEDIUM (parent §3.C BaseAgent.route() wording) + D3 MEDIUM (parent §3.C references non-existent `core/services/execution_tracker.py`) + D4 HIGH (parent §3.C 3-class landmine misclassifies dead code — escalated per Rigby SIGN F2 fold) + D5 MEDIUM (Employee OS `evidence_for_mission` omits AgentExecution) + D6 LOW (PLATFORM_INVENTORY no per-class row count) — all owed to xx99 anchor-update PR.
- **From S1702 §19:** R1 (HIGH) F2 PA path adoption + R2 (HIGH) F1 multi-model dedup posture (LLMCallEvent + LLMCallLog + CostTracking triangulation; xx99 scope) + R3 (HIGH) F4 retention posture. R4-R10 additional including R4 (MEDIUM) F3 provider-shape completeness for `_extract_usage` + R6 (MEDIUM) Cat B/Cat D correlation gap.
- **From S1702 §14:** D1 (MEDIUM) parent scoping §3.B field-list drift + D6 (MEDIUM) parent scoping §3.B model line-range drift owed to xx99 anchor-update PR.
- **From S1701 §19:** R1 (HIGH) task_id ↔ execution_id spine posture is xx99 (S1799) scope. R2 (HIGH) monitor-task probe-decomposition root fix — separate follow-on ops/infra initiative. R3-R5 MEDIUM Cat A follow-ons. R6-R8 LOW.
- **From S1701 §14:** D1 (MEDIUM) signal-handler line-range drift + D2 (MEDIUM) field-set drift owed to xx99 anchor-update PR.
- **From S1701 §20.5:** `tools/pa_local.sh` wrapper enhancement to support per-child SIGN pin routing (nice-to-have; not blocking).
- **From Group 1600 (S1699):** T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E; T1 (20 items); T3 CROSS-DOMAIN-EMPLOYEE-ANALOG; cross-arc: Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery.
- **From Group 1500 (S1599):** T1 R.SPORTS.POSTURE + R.DBAO.CODENAME Chris-gated ADRs; T1 CRITICAL remediation sequences.
- **From Group 1400 (S1499):** T1-T10 unified follow-on queue tier structure (still pending).
- **From Group 1300 (S1399):** 21 follow-on items (still pending).
- **§8 timeline table drift** — missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600); owed to follow-up docs PR.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1703 artifact set is on `main` — if yes, next session branches off `main`
3. If not yet merged: Chris merge + PR merge
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin
6. **Retire fresh SIGN isolation pin `pa-f1a30b7ed5bb4042` from S1703** via Rigby `session_tool.retire`
7. Mint fresh SIGN isolation pin for S1704
8. Execute S1704 Cat D ToolCallRecord child audit per D72 P4 slot

---

## PA / Rigby context

- **Arc pin at session start:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; in service through Group 1700 close at S1799). `tools/pa_local.sh:128` points at active arc pin — no rotation needed.
- **S1703 SIGN routing:** SIGN-with-edits cycle 1 at Medium-High confidence (single-batch 4-question) on arc pin `pa-e7fbacc996b34b44` (S1600/S1700/S1701/S1702 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN pin `pa-f1a30b7ed5bb4042` minted per playbook §15 but routed-around by wrapper hard-code — retire owed at S1703 close). F1-F4 folds landed pre-commit; single-batch 4-question pattern held clean per D48 20th arm.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128 currently pointing at Group 1700 active arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 20-arc CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER at S1703 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703 20-arc pattern confirmed. **FIFTEEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703 CONFIRMED at S1703 close per single-batch-4-question criterion.** D48 preemptive stability-probe gate 21st arm anticipated at next-session S1704 child audit open. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1703 close, before merge):** `docs/session-1703-observability-cat-c-agent-execution-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1703 handoff at `docs/handoffs/SESSION_1703_OBSERVABILITY_CAT_C_AGENT_EXECUTION_AUDIT.md`. Prior handoffs: SESSION_1702 (Observability Cat B LLMCallEvent); SESSION_1701 (Observability Cat A CeleryTaskEvent); SESSION_1700 (Observability arc-open parent scoping); SESSION_1699 (Content Group 1600 xx99 canonical summary); SESSION_1606 (Content Cat F LAST child); SESSION_1605-1601 (Content Cat E/A/B/D/C children); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Memory Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v46 (bumped this session with §1.49 S1703 registration + §8 timeline S1703 row + line-6 v46 preamble). Next bump at S1704 child audit close (v46 → v47 with §1.50 S1704 registration).
- **OPEN_ARCS state:** Group 1700 row remains In-progress; current-child updated S1702 → S1703. Group 1600 remains Closed; Group 1500 remains Closed; Group 1400 remains Closed; Group 1300 remains Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1703 artifact set is on `main` — if yes, next session branches off `main`
- [ ] If not yet merged: Chris merge + PR merge
- [ ] **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
- [ ] Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 21st arm start)
- [ ] **Retire fresh SIGN isolation pin `pa-f1a30b7ed5bb4042` from S1703** via Rigby `session_tool.retire`
- [ ] Mint fresh SIGN isolation pin for S1704 via Rigby `session_tool.create_fresh`
- [ ] Execute S1704 Cat D ToolCallRecord child audit per playbook §11.2 20-section template

## Reference — where to look

- **S1703 Cat C audit doc:** `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md` — playbook §11.2 20-section template THIRD application under Group 1700; §17 F1 3-class landmine resolves as 1-alive + 2-dead via Django app registry check; §14 F2 CRITICAL S287 stale docstring; §14 F4 CRITICAL PA path zero coverage; §9 F9 Cat C owns TWO cross-model spine primitives (execution_id + trace_id) as D74 axis contribution with 4-option Chinese menu for xx99; §17 F6 HIGH ToolCallRecord no execution_id field; §19 R1-R10 follow-on queue; §20.6 Rigby SIGN cycle 1 F1-F4 fold notes.
- **S1702 Cat B audit doc:** `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md`.
- **S1701 Cat A audit doc:** `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md`.
- **S1700 parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md`.
- **S1699 canonical summary doc (fourth §11.3 §10 application):** `docs/research/domains/content/1699_content_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent template + §11.2 child template + §11.3 canonical summary template + §11.3 §10 meta-methodology template + §22 default queue lean).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (§8.1 RESEARCH contract + §12.3 "Start Group NNNN" target).
- **ARCHITECTURE_INDEX v46:** `docs/research/ARCHITECTURE_INDEX.md` — S1703 §1.49 + line-6 v46 preamble + §8 timeline S1703 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1700 In-progress row current-child S1703.
- **Cat D (ToolCallRecord) entry points for S1704:** `core/models_tool_calls.py:19-131` (ToolCallRecord model; NO execution_id field) + `core/agents/base_agent.py:__init_subclass__` (S970 auto-wrap) + `core/services/tool_dispatcher.py` (registry + dispatch) + `core/services/pa_tool_schemas.py` (113 tool schemas per PLATFORM_INVENTORY) + `core/services/td_handlers_*.py` (156 registered handlers).
- **Topic docs:** `docs/topics/agent-system.md` (ToolCallRecord operator playbook at :107-113) + `docs/topics/personal-assistant.md` (PA tool surface).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1703 = THIRD child under Group 1700; S1704-S1706 children + S1799 xx99 anticipated.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 xx99 anchor-update will surface narrative-anchor gap).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1703 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged.
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 + Group 1600 T1 CRITICAL remediation queues still pending (inherited); Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E blocks 20 T1 items.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); owed to follow-up docs PR.
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (not addressed this session per scope discipline).
- **D48 preemptive stability-probe gate 20th-arm CONFIRMED CLEAN at S1703 close** — 15-consecutive-fully-clean-arms sub-pattern CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** CONFIRMED-STRENGTHENED via fourth-application (S1700).
- **Playbook v3 §11.2 template promotion:** THIRD application under Group 1700 (S1703) CONFIRMED — methodology durable across new arc.
- **Arc pin `pa-e7fbacc996b34b44` in service** through Group 1700 close; wrapper rotation NOT owed at next-session open.
- **`tools/pa_local.sh:128` wrapper enhancement** — hard-codes arc pin with no runtime `--conversation` override. Fresh SIGN pins minted for child audits get routed to arc pin (S1600/S1700/S1701/S1702/S1703 precedent applies: arc pin doubles as SIGN pin). Nice-to-have follow-up.
