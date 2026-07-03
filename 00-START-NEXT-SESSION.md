# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1700 IN-PROGRESS; S1701 CAT A CLOSED; NEXT = S1702 CAT B

The local wrapper at `tools/pa_local.sh:128` points at Group 1700 arc pin. **Active arc pin state after S1701 close:**

- **Active Group 1700 arc pin: `pa-e7fbacc996b34b44`** (Rigby `session_tool.create_fresh` at S1700 open — title "Session 1700 — Observability research group (kickoff)"). Continues in service across Group 1700 arc (S1701 CLOSED + S1702-S1706 children pending + S1799 xx99 canonical summary). SIGN routing at S1701 landed on arc pin (fresh SIGN pin `pa-3147aef9db4945ac` minted but routed-around by wrapper hard-code — S1600 parent-scoping precedent: arc pin doubles as SIGN pin).
- **Retired at S1701 close:** Fresh SIGN isolation pin `pa-3147aef9db4945ac` (was unused because wrapper hard-code routed SIGN to arc pin; retired per playbook §16 discipline with `updated_count=1, retired=true`).
- **Retired at S1700 open:** Group 1600 arc pin `pa-f52acf3f8d394faa`.
- **Retired earlier at S1699 close:** SIGN isolation pin `pa-846b6c4a532947c3`.
- **Retired earlier at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83`.
- **Retired earlier at S1605-S1601 closes:** SIGN isolation pins `pa-b1b26f4f35474df8` + `pa-4ce64003711de4f1` + `pa-8af9063864bf4a7f` + `pa-1c5298d807d7a1d2` + `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

**No wrapper rotation owed at next-session open** — arc pin in service through Group 1700 close at S1799.

## READ THIS THIRD — S1701 CAT A CELERYTASKEVENT AUDIT LANDED; NEXT = S1702 CAT B LLMCallEvent

Session 1701 shipped the **Group 1700 Cat A CeleryTaskEvent child audit** at `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md` (`status: active`, `category: child_audit`, `session: 1701`, `child_slot: P1`, `domain_slug: observability`, `research_group: 1700`, `head_commit: b8194e24`, `authority: child-audit`; 1082 lines post-fold; playbook §11.2 20-section child audit template FIRST application under Group 1700; playbook §13 6-parallel-Explore sweep + §14 verifier-loop applied pre-Explore + post-Explore; Rigby SIGN cycle 1 SIGN-with-edits at High confidence — F1-F3 folds landed pre-commit). **13-consecutive-fully-clean-arms sub-pattern CONFIRMED via D48 18th arm** on arc pin `pa-e7fbacc996b34b44` (single-batch 4-question pattern per S1701 precedent).

**6 load-bearing findings locked in S1701 audit §1 Executive Summary:**

- **F1** — QUEUED status is NOT ghost state: legitimate gateway writer at `td_handlers_gateway.py:988` (`cockpit_tool.trigger_task`) fills pre-prerun polling gap so status polling doesn't fall through to AsyncResult PENDING.
- **F2** — Parent §3 A signal-handler line-range drift (`:74-177` claimed vs `:74-300` actual with 5 handlers, not 3). MEDIUM D1 doc-vs-runtime drift; owed to xx99 anchor-update PR.
- **F3** — REVOKED status is NOT ghost state: 2 legitimate writers found — `ops_autopilot.py:100` (stuck-task sweep) + `td_handlers_gateway.py:1041` (user-initiated `cockpit_tool.revoke_task`).
- **F4** — `on_agent_task_failure_bridge` at `core/celery_telemetry.py:240-286` is a legitimate S1219 P1 **cross-cat exception** (Cat A→Cat C fire-alarm circuit-breaker), categorically distinct from parallel writers per Rigby SIGN F1 terminology fold. Hard-SIGKILL gap remains 30-min cleanup watchdog territory.
- **F5** — agent_name backfill intentional gradual-fill debt (S1169 no-backfill stance).
- **F6** — Monitor-task overhead debt (S1167) PARTIALLY closed — decorator-side timeouts landed S1169; probe-decomposition root fix per `celery-workers.md:255-276` remains deferred (§19 R2 HIGH priority).

**§9 Correlation primitive posture (D74 axis evidence):** task_id is coverage-complete singleton primitive at `core/models_celery_telemetry.py:33`; **8 downstream models** (`AISeriesItem`, `ContentPipelineRun`, `ConceptForgeRun`, `SpiderExecution`, `WorkflowExecution`, `ScheduledImageGeneration`, `WorkflowRun`, `ExecutionRun`) carry `celery_task_id` as scalar CharField without FK. Cat A's D74 contribution: task_id is a singleton primitive with 8 string-based non-FK downstream references, NOT a canonical spine.

**§16 Boundary violation matrix: 5 candidates all LEGITIMATE** (1 cross-cat exception + 4 parallel writers). Recommendation for xx99: codify Cat A boundary rule with 4 sub-clauses + separate cross-cat exception sub-clause for B1.

**Maturity STABLE + Research Coverage MODERATE + Risk MEDIUM.**

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence** on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-3147aef9db4945ac` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code — S1600 parent-scoping precedent applies). **F1-F3 folds landed pre-commit:**

- **F1 (MEDIUM)** — Boundary terminology clarity: labeled `on_agent_task_failure_bridge` explicitly as "LEGITIMATE CROSS-CAT EXCEPTION (Cat A→Cat C)" distinct from 4 parallel writers.
- **F2 (LOW)** — Downstream `celery_task_id` count consistency (7→8 with 8 models enumerated inline).
- **F3 (LOW)** — D10 severity footnote (Cat A LOW + xx99 elevation flagged).

**Rigby CONFIRM verdicts (no folds required):** Q1 coverage-completeness High + Q2 drift severity Medium-High + Q3 correlation-primitive posture High (GIN-index question correctly deferred to P3 Cat C via U4) + Q4 R1-R8 ranking Medium-High (R2 monitor-task probe-decomposition stays HIGH as separate follow-on; R7 WebSocket push correctly LOW downstream of Group 1900).

**Session close artifacts committed at S1701 close:**

```
docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md   [new; 1082 lines post-fold; Cat A child audit; F1-F3 folds landed pre-commit; FIRST child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                        [modified — v43 → v44 with §1.47 S1701 registration + §8 timeline S1701 row + line-6 v44 preamble]
docs/research/OPEN_ARCS.md                                                                 [modified — Group 1700 In-progress row current-child updated S1700 → S1701; line-6 preamble bumped]
docs/handoffs/SESSION_1701_OBSERVABILITY_CAT_A_CELERY_TASK_EVENT_AUDIT.md                  [new — S1701 handoff]
00-START-NEXT-SESSION.md                                                                   [modified — this file; S1701 Cat A CLOSED; next-session priority = S1702 Cat B LLMCallEvent]
```

Handoff: `docs/handoffs/SESSION_1701_OBSERVABILITY_CAT_A_CELERY_TASK_EVENT_AUDIT.md`.

### NEXT-SESSION MISSION — S1702 CAT B LLMCallEvent CHILD AUDIT (D72 P2 slot)

Per D72 P2 slot + parent §5 sequence: **S1702 Cat B audit** — LLM Call Telemetry (`LLMCallEvent`).

Cat B canonical questions the child audit gathers evidence for:

- What is the scope of `LLMCallEvent.execution_id` — does it span a full agent-tool-LLM sequence, or just a single LLM call? **Inherits from Cat A S1701 §9:** `LLMCallEvent.execution_id` is a UUIDField implicitly pointing to `AgentExecution.id` without FK declaration. Does the execution_id inherit from CeleryTaskEvent.task_id, or is it disjoint?
- Does every LLM caller route through `core/services/llm_call_wrapper.py` (S1098 wrapper) — or are there rogue direct `Anthropic()` / `OpenAI()` invocations bypassing telemetry? Cross-check Memory rules `feedback_anthropic_client_factory.md` + `feedback_openai_client_factory.md`.
- Is cost accounting accurate? S1224 `gpt-5* max_completion_tokens` floor precedent — are there sites still under 4000-token budget that silently return empty content with `finish_reason='length'`?
- 6-provider coverage: OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini per `LLMProviderRegistry`. Which providers are wrapped, which bypass?
- Cat B/Cat D accounting rule per parent F3 fold: LLM calls made from inside a tool invocation remain **Cat B**; Cat D never attempts to own LLM cost.

Per F5 correlation-primitives box (`execution_id` primitive row): P2 verifies execution_id scope + inheritance-from-task_id + FK-declaration-status — feeds directly into xx99's D74 axis resolution.

**S1702 audit shape:**

- Playbook §11.2 20-section child audit template (child_slot: P2; domain_slug: observability; research_group: 1700).
- 6-parallel-Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims (pre-Explore + post-Explore).
- **Required full Rigby SIGN cycle 1** per playbook §15 stage-table child row (not optional light SIGN — child audit is research finding).
- Fresh SIGN isolation pin per playbook §15 promoted rule (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN routing will land on arc pin per S1700/S1701 wrapper hard-code precedent unless wrapper enhancement lands).
- Applies parent D69-D74 + Cat A S1701 D74 axis evidence contribution (task_id singleton + 8 downstream non-FK references).

Session flow at next-session open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1701 artifact set merged to `main` between sessions.
3. If not yet merged: Chris merge + PR merge.
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 19th arm start).
6. Mint fresh SIGN isolation pin for S1702 via Rigby `session_tool.create_fresh` (title: "Session 1702 — Group 1700 Cat B LLMCallEvent audit — SIGN isolation").
7. Dispatch 6-parallel Explore sweep on Cat B surface (LLMCallEvent model + llm_call_wrapper flow + 6 provider coverage + client-factory boundary + cost accounting + execution_id scope).
8. Parent-Claude verifier-loop on any pre-Explore binary claims.
9. Draft S1702 audit per playbook §11.2 20-section template.
10. Rigby SIGN cycle 1 (single-batch 4-question pattern per S1701 precedent).
11. Land Rigby folds pre-commit.
12. Retire SIGN isolation pin at S1702 close per playbook §16.
13. Update ARCHITECTURE_INDEX v44 → v45 with §1.48 S1702 registration + §8 timeline row + line-6 preamble.
14. Update OPEN_ARCS Group 1700 In-progress row with S1702 child close note.
15. Write S1702 handoff + overwrite this `00-START-NEXT-SESSION.md`.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. R2 monitor-task probe-decomposition root fix is a separate follow-on ops/infra initiative (per Rigby SIGN Q4 verdict; NOT bundled with xx99 anchor-update tranche).

### Post-arc queued items (Chris-gated, inherited from prior arcs + additions from S1701)

- **From S1701 §19:** R1 (HIGH) task_id ↔ execution_id spine posture is xx99 (S1799) scope. **R2 (HIGH) monitor-task probe-decomposition root fix — separate follow-on ops/infra initiative** (T2 debt open since S1167). R3-R5 MEDIUM Cat A follow-ons (agent_name backfill % measurement + retention-cleanup failure detection + QUEUED-transition timeout). R6-R8 LOW (RSS platform-quirk test coverage + realtime WebSocket push + 8-downstream FK reconciliation).
- **From S1701 §14:** D1 (MEDIUM) signal-handler line-range drift + D2 (MEDIUM) field-set drift owed to xx99 anchor-update PR for `docs/topics/celery-workers.md` + `docs/PLATFORM_WHAT_IT_IS.md` narrative + parent §3 A scope box correction.
- **From S1701 §20.5:** `tools/pa_local.sh` wrapper enhancement to support per-child SIGN pin routing is a nice-to-have (not blocking). Wrapper currently hard-codes arc pin at L128.
- **From Group 1600 (S1699):** T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E; T1 (20 items) including RAG-SCOPE + citation integrity + force-bypass; T3 CROSS-DOMAIN-EMPLOYEE-ANALOG; cross-arc: Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery.
- **From Group 1500 (S1599):** T1 R.SPORTS.POSTURE + R.DBAO.CODENAME Chris-gated ADRs; T1 CRITICAL remediation sequences.
- **From Group 1400 (S1499):** T1-T10 unified follow-on queue tier structure (still pending).
- **From Group 1300 (S1399):** 21 follow-on items (still pending).
- **§8 timeline table drift** — missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600); owed to follow-up docs PR.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1701 artifact set is on `main` — if yes, next session branches off `main`
3. If not yet merged: Chris merge + PR merge
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin
6. Mint fresh SIGN isolation pin for S1702
7. Execute S1702 Cat B LLMCallEvent child audit per D72 P2 slot

---

## PA / Rigby context

- **Arc pin at session start:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; in service through Group 1700 close at S1799). `tools/pa_local.sh:128` points at active arc pin — no rotation needed.
- **S1701 SIGN routing:** SIGN-with-edits cycle 1 at High confidence (single-batch 4-question) on arc pin `pa-e7fbacc996b34b44` (S1600 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN pin `pa-3147aef9db4945ac` minted per playbook §15 but routed-around by wrapper hard-code — retired at S1701 close). F1-F3 folds landed pre-commit; single-batch 4-question pattern held clean per D48 18th arm.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128 currently pointing at Group 1700 active arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 18-arc CODIFICATION-READY-STRENGTHENED-FURTHER at S1701 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701 18-arc pattern confirmed. **THIRTEEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701 CONFIRMED at S1701 close per single-batch-4-question criterion.** D48 preemptive stability-probe gate 19th arm anticipated at next-session S1702 child audit open. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1701 close, before merge):** `docs/session-1701-observability-cat-a-celery-task-event-audit` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1701 handoff at `docs/handoffs/SESSION_1701_OBSERVABILITY_CAT_A_CELERY_TASK_EVENT_AUDIT.md`. Prior handoffs: SESSION_1700 (Observability arc-open parent scoping); SESSION_1699 (Content Group 1600 xx99 canonical summary); SESSION_1606 (Content Cat F LAST child); SESSION_1605-1601 (Content Cat E/A/B/D/C children); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Memory Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v44 (bumped this session with §1.47 S1701 registration + §8 timeline S1701 row + line-6 v44 preamble). Next bump at S1702 child audit close (v44 → v45 with §1.48 S1702 registration).
- **OPEN_ARCS state:** Group 1700 row remains In-progress; current-child updated S1700 (parent) → S1701 (Cat A child). Group 1600 remains in Closed; Group 1500 remains in Closed; Group 1400 remains in Closed; Group 1300 remains in Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1701 artifact set is on `main` — if yes, next session branches off `main`
- [ ] If not yet merged: Chris merge + PR merge
- [ ] **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
- [ ] Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 19th arm start)
- [ ] Mint fresh SIGN isolation pin for S1702 via Rigby `session_tool.create_fresh`
- [ ] Execute S1702 Cat B LLMCallEvent child audit per playbook §11.2 20-section template

## Reference — where to look

- **S1701 Cat A audit doc:** `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md` — playbook §11.2 20-section template FIRST application under Group 1700; §16 Boundary violations matrix (5 candidates all legitimate — 1 cross-cat exception + 4 parallel writers); §9 correlation-primitive posture (task_id singleton + 8 downstream non-FK references) as D74 axis evidence; §19 R1-R8 follow-on queue; §20.5 Rigby SIGN cycle 1 fold notes.
- **S1700 parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md` — playbook §11.1 template FOURTH application; §3 six-category taxonomy A–F with F1-F3 folds; §4 PARENT-WITH-CHILDREN verdict; §5 P1→P7 sequence with F5 correlation primitives box; §7 21-item anti-scope with F6 three adds; §8 D69-D74 all Chris-locked.
- **S1699 canonical summary doc (fourth §11.3 §10 application):** `docs/research/domains/content/1699_content_canonical_summary.md`.
- **S1600 parent scoping doc (third §11.1 application):** `docs/research/domains/content/1600_content_domain_scoping.md`.
- **S1500 parent scoping doc (second §11.1 application):** `docs/research/domains/sports/1500_sports_domain_scoping.md`.
- **S1400 parent scoping doc (first §11.1 application):** `docs/research/domains/revenue/1400_revenue_domain_scoping.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent template + §11.2 child template + §11.3 canonical summary template + §11.3 §10 meta-methodology template + §22 default queue lean).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (§8.1 RESEARCH contract + §12.3 "Start Group NNNN" target).
- **ARCHITECTURE_INDEX v44:** `docs/research/ARCHITECTURE_INDEX.md` — S1701 §1.47 + line-6 v44 preamble + §8 timeline S1701 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1700 In-progress row current-child S1701.
- **Cat B (LLMCallEvent) entry points for S1702:** `core/models_llm_telemetry.py:30-100` (LLMCallEvent model) + `core/services/llm_call_wrapper.py` (S1098 wrapper) + Memory rules `feedback_anthropic_client_factory.md` + `feedback_openai_client_factory.md` + `feedback_gpt5_max_completion_tokens_floor.md` + `feedback_llm_autofills_boolean_params_with_false.md`.
- **Topic docs:** `docs/topics/celery-workers.md` (Cat A operator playbook) + `docs/topics/agent-system.md` (ToolCallRecord + AgentExecution wrapper).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1701 = FIRST child under Group 1700; S1702-S1706 children + S1799 xx99 anticipated.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 xx99 anchor-update will surface D10 narrative-anchor gap per Rigby SIGN F3).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1701 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 + Group 1600 T1 CRITICAL remediation queues still pending (inherited); Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E blocks 20 T1 items.
- **§8 timeline table drift** flagged in S1700 timeline row body: missing rows for S1605 + S1606 + S1699 (Group 1600); owed to follow-up docs PR.
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (not addressed this session per scope discipline).
- **D48 preemptive stability-probe gate 18th-arm CONFIRMED CLEAN at S1701 close** — 13-consecutive-fully-clean-arms sub-pattern CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** CONFIRMED-STRENGTHENED via fourth-application (S1700); formal codification is a separate follow-up per Chris ratification.
- **Playbook v3 §11.2 template promotion:** FIRST application under Group 1700 (S1701) CONFIRMED — same as prior 5 group arcs; methodology durable across new arc.
- **Arc pin `pa-e7fbacc996b34b44` in service** through Group 1700 close; wrapper rotation NOT owed at next-session open.
- **`tools/pa_local.sh:128` wrapper enhancement** — hard-codes arc pin with no runtime `--conversation` override. Fresh SIGN pins minted for child audits get routed to arc pin (S1600 precedent applies: arc pin doubles as SIGN pin). Nice-to-have follow-up per S1701 §20.5 pin nuance flag.
