# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1700 IN-PROGRESS; S1702 CAT B CLOSED; NEXT = S1703 CAT C

The local wrapper at `tools/pa_local.sh:128` points at Group 1700 arc pin. **Active arc pin state after S1702 close:**

- **Active Group 1700 arc pin: `pa-e7fbacc996b34b44`** (Rigby `session_tool.create_fresh` at S1700 open — title "Session 1700 — Observability research group (kickoff)"). Continues in service across Group 1700 arc (S1701 CLOSED + S1702 CLOSED + S1703-S1706 children pending + S1799 xx99 canonical summary). SIGN routing at S1702 landed on arc pin per S1600/S1700/S1701 parent-scoping precedent (arc pin doubles as SIGN pin; fresh SIGN pin `pa-c3927ab78c52479a` minted per playbook §15 but routed-around by wrapper hard-code at L128).
- **Retired at S1702 close:** Fresh SIGN isolation pin `pa-c3927ab78c52479a` (was unused because wrapper hard-code routed SIGN to arc pin; retired per playbook §16 discipline with `updated_count=1, retired=true`).
- **Retired at S1701 close:** Fresh SIGN isolation pin `pa-3147aef9db4945ac`.
- **Retired at S1700 open:** Group 1600 arc pin `pa-f52acf3f8d394faa`.
- **Retired earlier at S1699 close:** SIGN isolation pin `pa-846b6c4a532947c3`.
- **Retired earlier at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83`.
- **Retired earlier at S1605-S1601 closes:** SIGN isolation pins `pa-b1b26f4f35474df8` + `pa-4ce64003711de4f1` + `pa-8af9063864bf4a7f` + `pa-1c5298d807d7a1d2` + `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

**No wrapper rotation owed at next-session open** — arc pin in service through Group 1700 close at S1799.

## READ THIS THIRD — S1702 CAT B LLM CALL EVENT AUDIT LANDED; NEXT = S1703 CAT C AGENTEXECUTION

Session 1702 shipped the **Group 1700 Cat B LLMCallEvent child audit** at `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md` (`status: active`, `category: child_audit`, `session: 1702`, `child_slot: P2`, `domain_slug: observability`, `research_group: 1700`, `head_commit: 2bb196e8`, `authority: child-audit`; ~1090 lines post-fold; playbook §11.2 20-section child audit template SECOND application under Group 1700; playbook §13 6-parallel-Explore sweep + §14 verifier-loop applied pre-Explore + post-Explore; Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence — F1-F3 folds landed pre-commit). **14-consecutive-fully-clean-arms sub-pattern CONFIRMED via D48 19th arm** on arc pin `pa-e7fbacc996b34b44` (single-batch 4-question pattern per S1701 precedent).

**9 load-bearing findings locked in S1702 audit §1 Executive Summary:**

- **F1 (CRITICAL, §17)** — Multi-model LLM telemetry duplication. `LLMCallEvent` (S1098, `core/models_llm_telemetry.py:30-115`, 16 fields, NO `cost`/`total_tokens`/`latency_ms`) coexists at HEAD with `LLMCallLog` (S697, `core/models_llm_routing.py:297-362`, HAS `cost` line 335 + `total_tokens` line 331 + `latency_ms` line 332) AND a **third store `CostTracking` at `core/models_unified_system.py:6665`** (surfaced by Rigby SIGN cycle 1 F1 fold via `repo_tool.search`).
- **F2 (CRITICAL, §14)** — PA agentic loop uncovered. `core/services/unified_pa_entrypoint.py` + `core/llm_enforcer.py` both import zero wrapper symbols (verified grep). PA GPT-5.2 function-calling loop generates 1-20 LLM calls per user message and writes zero LLMCallEvent rows.
- **F3 (MEDIUM, latent, §14)** — `_extract_usage` provider-shape gap for Gemini `prompt_token_count`/`candidates_token_count` (`llm_provider_registry.py:847-848`) + Ollama `prompt_eval_count`/`eval_count` (`:969-970`). LATENT because all 23 production wrapper call sites use OpenAI/Anthropic (or OpenAI-compatible DeepSeek/Together).
- **F4 (HIGH, §15)** — No date-based retention for LLMCallEvent. Only 10-min stuck-STARTED watchdog (`_impl_cleanup_stale_llm_calls` at `tasks_agents.py:1659`, S1221 P2 Tier 2). LLMCallLog has 30-day retention analog; Cat B has none.
- **F5 (MODERATE, §13)** — Wrapper adoption 23 production sites across 8 files: content_writer_agent (3) + code_review_agent (5) + devops_agent (5) + tasks_initiatives (5) + market_intelligence_agent (2) + campaign_orchestrator (1) + thinking_agent (1 async) + curated_action_card_generator (1). BaseAgent + agent_router import only `LLMCallCancelled` exception.
- **F6 (MEDIUM, §14)** — Parent scoping §3.B field list drift; root cause is F1 (parent's field list matches LLMCallLog schema, mislabeled as LLMCallEvent).
- **F7 (MEDIUM, §15)** — PR #3 cancel PARTIAL. Provider adapters do not yet abort in-flight sockets per wrapper docstring `:18-21`.
- **F8 (LOW, §15)** — PR #4 nested dispatch budget NOT SHIPPED.
- **F9 (D74 axis contribution, §9)** — `call_id` is Cat B's LLM-call-level singleton primitive (0 downstream models carry `llm_call_id`; not a cross-model spine); `execution_id` is Cat C-owned spine primitive tagged onto Cat B rows (nullable by design, non-FK'd per docstring `:56-60` "so telemetry survives AgentExecution row deletion"). **Cat B does NOT own a cross-model spine analog to Cat A's task_id.** Cross-cat correlation to Cat A goes via 3-hop chain.

**§9 Correlation-primitive posture (D74 axis evidence contribution):** `LLMCallEvent.call_id` is UUIDField(primary_key=True, default=uuid.uuid4, editable=False) — singleton at LLM-call level, no downstream references. `LLMCallEvent.execution_id` is UUIDField(nullable, indexed, NOT FK) — Cat C-owned spine primitive tagged onto Cat B rows; correlation is untyped (3 AgentExecution classes exist per parent §3.C landmine). If xx99 decides task_id → execution_id needs canonical spine, work chain per F9 is: (a) F1 dedup + (b) F2 PA coverage + (c) F3 provider-shape completeness + (d) F4 retention + (e) option set — NOT NULL + FK (breaks survival-of-deletion rationale) OR shared correlation-view / join contract.

**§16 Boundary violation matrix: 6 candidates all LEGITIMATE.** No cross-cat writes from wrapper, no direct `LLMCallEvent.objects.create` outside wrapper, no cross-cat reads inside wrapper; cancel_registry is clean support-service dependency. No Cat B analog to S1219 P1 cross-cat exception.

**Maturity STABLE for covered surface + PARTIAL overall + Risk MEDIUM-HIGH.**

**Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence** on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-c3927ab78c52479a` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code — S1600/S1700/S1701 precedent applies). **F1-F3 folds landed pre-commit:**

- **F1 (LOW)** — CostTracking added to §17 as third LLM-cost store (Rigby `repo_tool.search` surfaced `core/models_unified_system.py:6665` during Q1 coverage-completeness verification).
- **F2 (MEDIUM)** — §9 D74 axis contribution reframed "upgrade execution_id to NOT NULL + FK" from mandatory step into option set (either NOT NULL + FK OR shared correlation-view / join contract — NOT-NULL+FK conflicts with survival-of-deletion rationale).
- **F3 (LOW)** — Verification that R6 Cat B/Cat D correlation gap was already present in §19; no additional fold needed.

**Rigby CONFIRM verdicts (no folds required beyond F1-F3):** Q1 coverage-completeness Medium-High + Q2 drift-severity High + Q3 D74 axis correctness Medium-High + Q4 R1-R10 ranking + xx99 scope discipline Medium-High.

**Session close artifacts committed at S1702 close:**

```
docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md   [new; ~1090 lines post-fold; Cat B child audit; F1-F3 folds landed pre-commit; SECOND child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                    [modified — v44 → v45 with §1.48 S1702 registration + §8 timeline S1702 row + line-6 v45 preamble]
docs/research/OPEN_ARCS.md                                                             [modified — Group 1700 In-progress row current-child updated S1701 → S1702; line-6 preamble bumped]
docs/handoffs/SESSION_1702_OBSERVABILITY_CAT_B_LLM_CALL_EVENT_AUDIT.md                  [new — S1702 handoff]
00-START-NEXT-SESSION.md                                                                [modified — this file; S1702 Cat B CLOSED; next-session priority = S1703 Cat C AgentExecution]
```

Handoff: `docs/handoffs/SESSION_1702_OBSERVABILITY_CAT_B_LLM_CALL_EVENT_AUDIT.md`.

### NEXT-SESSION MISSION — S1703 CAT C AGENTEXECUTION CHILD AUDIT (D72 P3 slot)

Per D72 P3 slot + parent §5 sequence: **S1703 Cat C audit** — AgentExecution (with 3-class landmine).

Cat C canonical questions the child audit gathers evidence for:

- Which of the 3 `AgentExecution` classes is the actual canonical audit trail at HEAD? Parent §3.C landmine: `intelligence/models/agent_execution.py:11` (ActionPlan-scoped canonical per S1273 §3.25) + `intelligence/models.py:587` (duplicate class body; likely legacy re-export OR true duplicate) + `core/models_unified_system.py:882` (DEPRECATED per S287 docstring pointing at `agents.models` which is now a compatibility shim per S391 — **deprecation notice stale/wrong at HEAD**).
- Which class does BaseAgent's `route()` wrapper actually write to at HEAD? What is the correlation between the 3 classes (FK / trace_id / none)?
- Is the S287 deprecation stale (all callers migrated), a live orphan, or masking a migration incomplete?
- Is the S843 trace_id field usable as the canonical arc-wide correlation spine?
- **Inherits from Cat B S1702 F9 + §20.4 UNK-1:** which AgentExecution class does `LLMCallEvent.execution_id` correlate to? BaseAgent primary path status UNKNOWN — grep at S1702 close showed only `LLMCallCancelled` import at `base_agent.py:4723`, not span usage.
- **Inherits from Cat A S1701 §9:** does `AgentExecution.input_data['celery_task_id']` have a GIN index? (Parent §9 U4 candidate; JSON-path unindexed by default per S1701.)
- **Cat B/Cat D dedup contract:** does `AgentExecution.llm_call_count` match LLMCallEvent count per agent per execution?

Per parent §3.C boundary discipline: **P3 catalogs 3 classes + names canonical + defines correlation contract; deprecation ADR is post-arc T-slot per §6.3 parked candidate.** Do NOT attempt to design deprecation in S1703.

**S1703 audit shape:**

- Playbook §11.2 20-section child audit template (child_slot: P3; domain_slug: observability; research_group: 1700).
- 6-parallel-Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims (pre-Explore + post-Explore).
- **Required full Rigby SIGN cycle 1** per playbook §15 stage-table child row (not optional light SIGN — child audit is research finding).
- Fresh SIGN isolation pin per playbook §15 promoted rule (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN routing will land on arc pin per S1700/S1701/S1702 wrapper hard-code precedent unless wrapper enhancement lands).
- Applies parent D69-D74 + Cat A S1701 §9 axis evidence + Cat B S1702 F9 axis contribution.

Session flow at next-session open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1702 artifact set merged to `main` between sessions.
3. If not yet merged: Chris merge + PR merge.
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 20th arm start).
6. Mint fresh SIGN isolation pin for S1703 via Rigby `session_tool.create_fresh` (title: "Session 1703 — Group 1700 Cat C AgentExecution audit — SIGN isolation").
7. Dispatch 6-parallel Explore sweep on Cat C surface (3-class AgentExecution model catalog + BaseAgent route() wrapper write path + agent_name backfill dimension + trace_id S843 posture + input_data JSON structure + tool_call_count/llm_call_count denormalization if any).
8. Parent-Claude verifier-loop on any pre-Explore binary claims.
9. Draft S1703 audit per playbook §11.2 20-section template.
10. Rigby SIGN cycle 1 (single-batch 4-question pattern per S1701/S1702 precedent).
11. Land Rigby folds pre-commit.
12. Retire SIGN isolation pin at S1703 close per playbook §16.
13. Update ARCHITECTURE_INDEX v45 → v46 with §1.49 S1703 registration + §8 timeline row + line-6 preamble.
14. Update OPEN_ARCS Group 1700 In-progress row with S1703 child close note.
15. Write S1703 handoff + overwrite this `00-START-NEXT-SESSION.md`.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. AgentExecution 3-class deprecation ADR is post-arc T-slot per parent §3.C boundary discipline + §6.3 parked candidate.

### Post-arc queued items (Chris-gated, inherited from prior arcs + additions from S1702)

- **From S1702 §19:** R1 (HIGH) F2 PA path adoption + R2 (HIGH) F1 multi-model dedup posture (LLMCallEvent + LLMCallLog + CostTracking triangulation; xx99 scope) + R3 (HIGH) F4 retention posture. R4-R10 additional including R4 (MEDIUM) F3 provider-shape completeness for `_extract_usage` + R6 (MEDIUM) Cat B/Cat D correlation gap.
- **From S1702 §14:** D1 (MEDIUM) parent scoping §3.B field-list drift + D6 (MEDIUM) parent scoping §3.B model line-range drift owed to xx99 anchor-update PR.
- **From S1702 §20.4:** UNK-1 BaseAgent primary LLM call path wrapper adoption status; UNK-2 `enforce_real_ai` LLMCallLog vs LLMCallEvent write behavior; UNK-3 `employees/status.py` + `signals/rigby_delegation_signals.py` LLMCallEvent read intent; UNK-4 LLMCallEvent execution_id null-rate at HEAD; UNK-5 per-provider wrapper adoption skew; UNK-6 `_extract_usage` provider-shape test coverage.
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
2. Check if S1702 artifact set is on `main` — if yes, next session branches off `main`
3. If not yet merged: Chris merge + PR merge
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin
6. Mint fresh SIGN isolation pin for S1703
7. Execute S1703 Cat C AgentExecution child audit per D72 P3 slot

---

## PA / Rigby context

- **Arc pin at session start:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; in service through Group 1700 close at S1799). `tools/pa_local.sh:128` points at active arc pin — no rotation needed.
- **S1702 SIGN routing:** SIGN-with-edits cycle 1 at Medium-High confidence (single-batch 4-question) on arc pin `pa-e7fbacc996b34b44` (S1600/S1700/S1701 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN pin `pa-c3927ab78c52479a` minted per playbook §15 but routed-around by wrapper hard-code — retired at S1702 close). F1-F3 folds landed pre-commit; single-batch 4-question pattern held clean per D48 19th arm.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128 currently pointing at Group 1700 active arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 19-arc CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER at S1702 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702 19-arc pattern confirmed. **FOURTEEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702 CONFIRMED at S1702 close per single-batch-4-question criterion.** D48 preemptive stability-probe gate 20th arm anticipated at next-session S1703 child audit open. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1702 close, before merge):** `docs/session-1702-observability-cat-b-llm-call-event-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1702 handoff at `docs/handoffs/SESSION_1702_OBSERVABILITY_CAT_B_LLM_CALL_EVENT_AUDIT.md`. Prior handoffs: SESSION_1701 (Observability Cat A CeleryTaskEvent); SESSION_1700 (Observability arc-open parent scoping); SESSION_1699 (Content Group 1600 xx99 canonical summary); SESSION_1606 (Content Cat F LAST child); SESSION_1605-1601 (Content Cat E/A/B/D/C children); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Memory Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v45 (bumped this session with §1.48 S1702 registration + §8 timeline S1702 row + line-6 v45 preamble). Next bump at S1703 child audit close (v45 → v46 with §1.49 S1703 registration).
- **OPEN_ARCS state:** Group 1700 row remains In-progress; current-child updated S1701 → S1702. Group 1600 remains Closed; Group 1500 remains Closed; Group 1400 remains Closed; Group 1300 remains Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1702 artifact set is on `main` — if yes, next session branches off `main`
- [ ] If not yet merged: Chris merge + PR merge
- [ ] **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
- [ ] Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 20th arm start)
- [ ] Mint fresh SIGN isolation pin for S1703 via Rigby `session_tool.create_fresh`
- [ ] Execute S1703 Cat C AgentExecution child audit per playbook §11.2 20-section template

## Reference — where to look

- **S1702 Cat B audit doc:** `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md` — playbook §11.2 20-section template SECOND application under Group 1700; §17 F1 multi-model duplication (LLMCallEvent + LLMCallLog + CostTracking); §14 F2 PA agentic loop CRITICAL uncovered; §9 correlation-primitive posture (`call_id` singleton at Cat B + `execution_id` borrowed Cat C spine primitive) as D74 axis evidence contribution; §19 R1-R10 follow-on queue; §20.5 Rigby SIGN cycle 1 F1-F3 fold notes.
- **S1701 Cat A audit doc:** `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md`.
- **S1700 parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md`.
- **S1699 canonical summary doc (fourth §11.3 §10 application):** `docs/research/domains/content/1699_content_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent template + §11.2 child template + §11.3 canonical summary template + §11.3 §10 meta-methodology template + §22 default queue lean).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (§8.1 RESEARCH contract + §12.3 "Start Group NNNN" target).
- **ARCHITECTURE_INDEX v45:** `docs/research/ARCHITECTURE_INDEX.md` — S1702 §1.48 + line-6 v45 preamble + §8 timeline S1702 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1700 In-progress row current-child S1702.
- **Cat C (AgentExecution) entry points for S1703:** `intelligence/models/agent_execution.py:11` (ActionPlan-scoped canonical) + `intelligence/models.py:587` (duplicate class body) + `core/models_unified_system.py:882` (DEPRECATED per stale S287 docstring) + `core/agent_execution_wrapper.py` + `core/services/execution_tracker.py` + BaseAgent `route()` wrapper.
- **Topic docs:** `docs/topics/agent-system.md` (Cat C operator playbook + AgentExecution wrapper + ToolCallRecord) + `docs/topics/employee-os.md` (AgentExecution join with LLMCallEvent + ToolCallRecord for evidence).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1702 = SECOND child under Group 1700; S1703-S1706 children + S1799 xx99 anticipated.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 xx99 anchor-update will surface narrative-anchor gap).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1702 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged.
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 + Group 1600 T1 CRITICAL remediation queues still pending (inherited); Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E blocks 20 T1 items.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); owed to follow-up docs PR.
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (not addressed this session per scope discipline).
- **D48 preemptive stability-probe gate 19th-arm CONFIRMED CLEAN at S1702 close** — 14-consecutive-fully-clean-arms sub-pattern CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** CONFIRMED-STRENGTHENED via fourth-application (S1700).
- **Playbook v3 §11.2 template promotion:** SECOND application under Group 1700 (S1702) CONFIRMED — methodology durable across new arc.
- **Arc pin `pa-e7fbacc996b34b44` in service** through Group 1700 close; wrapper rotation NOT owed at next-session open.
- **`tools/pa_local.sh:128` wrapper enhancement** — hard-codes arc pin with no runtime `--conversation` override. Fresh SIGN pins minted for child audits get routed to arc pin (S1600/S1700/S1701/S1702 precedent applies: arc pin doubles as SIGN pin). Nice-to-have follow-up.
