# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2927 CLOSE → SLICE 5 ADVANCED to 12/14. **S2928 OPENS SLICE 5 batch 4 (FINAL) — CLOSES SLICE 5 AT 14/14.** D6 MORATORIUM STILL IN FORCE.

**Refreshed 2026-07-23 (S2927 close).** Batch 3 quartet shipped + workflow_orchestration_agent mapping fix shipped as prerequisite sibling PR. Rigby SIGN cycle turn 1 → chris D-verdict "yes, ship PR-A first then batch 3" arc surfaced one confirmed latent bug and eliminated a discovery deferral from S2926. **Q2 verdict on the workflow_orchestration_agent mapping asymmetry: (c) BUG** — mapping at `td_handlers_agents.py:123` was routing to `WorkflowAgent` (delegate coordinator) instead of `WorkflowOrchestrationAgent` (template-based orchestrator with 16+ AVAILABLE_WORKFLOWS). Task receipts had been passing regardless of which class the tool_name resolved to; completion outputs were coming from the wrong class. PR #3487 shipped the one-line fix + 3-test regression suite + confirmed sweep across `_tool_to_agent_name` produced 0 additional bugs (3 other asymmetries — `security_agent`, `strategic_review`, `create_brand_video`/`create_project_from_research` — verified as intentional/legacy aliases via `WorkflowOrchestrationAgent.AVAILABLE_WORKFLOWS` cross-check + comment-embedded rationale). **PR #3487 mapping fix validated end-to-end at both envelope layer and ORM parent-execution layer during batch 3 live-dispatch.**

**PRs shipped this session:**
- u-d-b PR [#3487](https://github.com/clwest/donkey-betz-platform/pull/3487) — workflow_orchestration_agent mapping fix + regression suite, merged at `389c048b0`.
- u-d-b PR [#3488](https://github.com/clwest/donkey-betz-platform/pull/3488) — Slice 5 batch 3 quartet (validated_full), merged at `c06bf7e57`.
- u-d-b PR `<TBD>` — S2927 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped this session (4 — Slice 5 batch 3 quartet; Slice 5 advances to 12/14):**
- `workflow_orchestration_agent` → WorkflowOrchestrationAgent (register at `tool_dispatcher.py:455`; mapping row `td_handlers_agents.py:123` — **fixed this session in PR #3487**). **WorkflowOrchestrationAgent-family completion-verify representative.** Documents new-evidence-class fanout shape (template-driven, bounded via `AVAILABLE_WORKFLOWS`) — distinct from LLM-planner-driven unbounded fanout via WorkflowAgent (S2925/S2926, 2/3 instances of the existing Fold-candidate).
- `content_strategy_agent` → ContentStrategyAgent (register at `:331`; mapping `:113`). Receipt-verify only. BaseAgent subclass, strategy-only.
- `marketing_strategy_agent` → MarketingStrategyAgent (register at `:332`; mapping `:114`). Receipt-verify only. Inherits `BaseBusinessResearchAgent` (SAME base class as CompetitorAnalysisAgent — S2926 content-shape FAIL surface). Flagged as content-shape FAIL 2nd-instance candidate for future completion-verify. `create_deliverable_on_schedule = True`.
- `strategic_review` → ContentStrategyAgent (register at `:458`; mapping `:131` — legacy alias, Session 1068). Receipt-verify only. 2nd documented instance of multi-tool-single-class pattern.

All 4 dispatch through shared handler `_handle_agent_tool` at `tool_dispatcher.py:1196` (same as batches 1+2). Async receipt shape: `{task_id, mode: 'async', agent, auto_followup, follow_up_will_fire, message}`. Queue: `long_running`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3487 recycled clean at `sha=389c048b0a04`: 5 fresh workers + beat, zero surviving old PIDs.
- PR #3488 recycled clean at `sha=c06bf7e57f76`: 5 fresh workers + beat, zero surviving old PIDs.
- Rigby dispatch **4/4 receipt PASS** (task_ids `58d165dd` / `b2af49ff` / `d70e38de` / `dcb12206`).
- **PR #3487 fix VALIDATED end-to-end at 3 observation surfaces** — dispatch envelope + parent AgentExecution `owner_agent` field + completion `output_data.data.keys` shape (all show `WorkflowOrchestrationAgent`; template payload shape `['image_ids', 'project_created', 'step_results', 'summary', 'video_ids', 'workflow']` matches `workflow_orchestration_agent.py:313-320`).
- **`strategic_review` alias mismatch VALIDATED at runtime (post-close observation)** — SWOT prompt → content-strategy-shaped output (`"Generated 3 content recommendations"` message + identical `data.keys` to `content_strategy_agent`). Doc §5 warning graduated from theoretical to observed once.
- **All 4 completed by 05:39:08** (2 min–5.5 min latency window). See handoff §"Post-close completion observations" for full detail. **Content-shape FAIL Fold candidate stays at 1/2** — `marketing_strategy_agent` produced real structured Markdown target-audience content, not a 2nd false-PASS instance.
- **New feedback rule saved to Claude memory:** wait for in-flight agent completions before starting close cascade (see `feedback_wait_for_agent_completions_before_close_cascade.md`).

**§5a end-to-end classification (batch 3):** `workflow_orchestration_agent` = `external` amplified via template-driven bounded fanout (16+ AVAILABLE_WORKFLOWS templates); `content_strategy_agent` = `external` non-amplified; `marketing_strategy_agent` = `external` amplified via `BaseBusinessResearchAgent` spider + web_search integration + auto-Deliverable INSERT (post_save cascading); `strategic_review` = `external` non-amplified (identical to `content_strategy_agent` — same class).

**No engineering-backlog items filed this session** — pure sweep-batch engineering + 1 latent-bug fix.

**Sweep progress (post-S2927, gap-map regen at close):**
- **Slice 1 (`td_handlers_ops`):** unchanged.
- **Slice 2 (`td_handlers_agents`):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`):** CLOSED at S2924 (17/17).
- **Slice 5 (`tool_dispatcher`, 14 tools):** **OPEN at 12/14 post-S2927.** 2 remaining: `content_writer_agent`, `image_editing_agent`.
- Total corpus untested: **17** post-batch-3 (from 22 pre-S2927).
- Gap map: **81 full · 11 partial · 7 unknown · 17 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 2 substantive PRs + close cascade in 1 session — matches S2926 pace.

Full session context: `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md`.

---

## S2928 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 5 batch 4 (FINAL) composition SIGN cycle

Batch 4 CLOSES Slice 5 with the 2 remaining tools + optional carry-forward observations. Batch 4 should:
- (a) Cover `content_writer_agent` — completion-verify representative candidate (creates Deliverable rows per invocation; structured content output; content-shape FAIL 2nd-instance candidate class if the output schema is required)
- (b) Cover `image_editing_agent` — receipt-verify only (last remaining media-family tool)
- (c) Optionally include: bundled ORM enumeration of S2927 `workflow_orchestration_agent` completion-verify tree (parent AE `20ad3024-e9b8-4905-be0c-99e7e72f3819`) — completes the new-evidence-class template-driven fanout datapoint.
- (d) Optionally include: bundled completion-verify against `marketing_strategy_agent` — S2927 flagged as content-shape FAIL 2nd-instance highest-signal test candidate.

**Q1 (batch 4 composition):** propose a 2-tool pair with (a) + (b) + optional (c) + (d) as bundled follow-up dispatches.

**Q2 (content_writer_agent completion-verify representative decision):**
Should `content_writer_agent` be the batch 4 completion-verify representative? Rationale for YES: (1) it auto-creates Deliverable rows (`ContentWriterAgent` — content-strategy-tier peer of `marketing_strategy_agent`); (2) it's a structured-output agent — content-shape FAIL risk class; (3) it's the last content-strategy tool in the corpus — natural closer. Rationale for NO: (1) if S2928 also does bundled `marketing_strategy_agent` completion-verify (Q1d), that's already 2 completion-verifies — no need for a 3rd. Pick the one most likely to surface content-shape FAIL 2nd instance if forced to choose.

**Q3 (S2927 workflow_orchestration_agent completion tree — 3rd instance disposition):**
S2927's `workflow_orchestration_agent` completion was in-progress at session close. If S2928 batch 4 includes Q1c ORM enumeration and the tree shows template-driven bounded fanout (bounded step count = the template's declared steps; not the unbounded LLM-planner shape), that IS the 1st confirmed instance of a new-evidence-class fanout Fold candidate. Note: this is 1st of a NEW class — NOT a 3rd instance of the existing WorkflowAgent LLM-planner Fold candidate. Fold ladder for the existing candidate stays at 2/3.

**Q4 (Slice 5 CLOSE reflection — pattern promotion candidates):**
Slice 5 batches 1+2+3 shipped 12/14 tools with the shared `_handle_agent_tool` handler + shared `_tool_to_agent_name` mapping. Post-CLOSE, is there a Slice-scoped promotion candidate that summarizes the Slice 5 authoring pattern (all agent-forwarding, all async, all `long_running` queue, all wrap agent class, all Slice 5 doc header cadence)? This would be a Slice 5 CLOSE artifact analogous to S2924's Slice 4 §5a tier distribution artifact.

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Content-shape FAIL is 1st instance (S2926 CompetitorAnalysisAgent). If S2928 batch 4 completion-verify of `content_writer_agent` OR bundled follow-up completion-verify of `marketing_strategy_agent` surfaces a 2nd instance, promote the diagnostic pattern to Fold. Preview the fold shape sketch during T0 SIGN.
- Multi-tool-single-class pattern is 2nd instance (S2927 batch 3 — `content_strategy_agent` + `strategic_review`). If a future batch (post-Slice-5) surfaces a 3rd (e.g. `security_agent → MemoryIsolationAgent` if it validates in Slice 6+), promote as an authoring pattern.
- Slice 5 CLOSE structural retrospective: are there patterns across all 14 Slice 5 tools that should be codified BEFORE opening Slice 6+ sweep? (Handler consolidation? Schema-required-field regularization? Envelope-shape lint?)
- What am I not asking? What structural risk or coupling are we accreting into the sweep close by continuing the doc-only cadence for the final 2 tools?

### Alternative Step 1 candidates

- **CompetitorAnalysisAgent content-FAIL remediation** — targeted engineering slate; deliverable `5703a6c8-...`.
- **Ledger #34 broader stale-model sweep** — multi-hour engineering.
- **Bundled dev-env drift slate** — group Ledger #33/#34 legacy + AgentTaskExecution pre-existing pyright drift + S2919 narrative drift + S2927-observed td_handlers_agents.py pyright drift (10 diagnostics latent) into one PR.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note. Unchanged.

### What's forbidden at S2928 (D6 MORATORIUM still in force)

All S2925/S2926 forbidden entries carry forward (see S2926 handoff §Forbidden entries and S2926 00-START Forbidden section — comprehensive list from S2843 through S2926). **S2927 new forbidden entries below.**

**S2927 new forbidden entries (all 1st-instance — require corroborating trigger before promotion):**

- **No "template-driven bounded fanout via WorkflowOrchestrationAgent" Fold promotion without 2nd instance.** 1st (S2927 `workflow_orchestration_agent` completion-verify — pending ORM enumeration; new-evidence-class distinct from LLM-planner unbounded fanout via WorkflowAgent). Watch for 2nd template-driven fanout instance.
- **No "PR-A prerequisite → PR-B pattern-shape" Fold promotion without recurrence.** 1st (S2927 PR #3487 → PR #3488 sequencing where PR-A fixes a runtime mapping that PR-B's completion-verify signal depends on). Specific instance of the more general "grep-before-claim" pattern with additional axis of "prerequisite-fix-before-observation-signal". Watch for a 2nd instance where a sweep-batch's evidence would be invalidated without a prerequisite fix.
- **No "multi-tool-single-class asymmetry doc-authoring pattern" Fold promotion without 3rd instance.** 2nd this session (`content_strategy_agent` + `strategic_review` → same `ContentStrategyAgent`). 3rd instance = potential `security_agent → MemoryIsolationAgent` when that tool validates.

**S2926 forbidden entries (carried forward):** No "wrong-model reference to sister model in same registry" Fold promotion without 2nd instance; no "content-shape FAIL surfaces only under completion-verify" Fold promotion without 2nd instance; no "third-tier identifier surface in AgentResult" Fold promotion without 2nd instance; no "media provider egress as distinct §5a downstream axis" Fold promotion without 2nd instance; no "semantic-alias contract for shared-agent tool_names" Fold promotion without corroboration.

**S2925 + prior forbidden entries (carried forward):** D6 STRATEGIC DISCOVERY MORATORIUM; no R1a-shaped proposals; no v2 → v3 harness schema bump without substrate-arc-scoped SIGN; no new gate/lint proposals; no agent-substrate validation arc; no `minimal_safe_args_v2` arc without explicit Chris directive; no entrypoint-side context-injection substrate arc; no schema-drift-fix Fold promotion; no `dry_run` infrastructure arc; no Concern C schema↔doc drift substrate arc; no `post_save signal cascade` substrate arc; no harness-level soft_error accounting substrate arc; no "metadata-classification-as-runtime-gate" substrate arc; no "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd instance (2/3); no "cascade audit companion doc" pattern promotion without 2nd instance (1/2); no "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance (2/3); no `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance (2 instances); no "observability-tracker as MUTATION vector" Fold promotion without 2nd instance (1st); no "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc (22 instances corroborated post-S2926); no "grep-before-claim" Fold promotion (1st); no "dispatcher re-entry" Fold promotion (1st); no "handler-forwarded param not in schema" Fold promotion (1st); no "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion (1st); no "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive (3/3 TRIGGERED; still Chris-gated); no "multi-tenant leak on detail/results action" Fold promotion; no "template-preservation swap" Fold promotion without explicit Chris directive (CODIFIED S2921); no "mixed user-scoping within single response" Fold promotion without 2nd instance (1st); no "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance (2/3); no "limit does not gate nested lists" Fold promotion without 2nd instance (1st); no "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance (1st); no "envelope-representation asymmetry" Fold promotion without 2nd instance (1st); no "00-START span-math source-of-truth regen" Fold promotion (CODIFIED S2921 as permanent close-ceremony step; validated 7 consecutive sessions S2921-S2927 inclusive); no "signal wiring exists but gate exempts tool's mutation shape → external not cascading" Fold promotion without 2nd instance (1st cockpit); no "verify-protocol authoring SIGN checkpoint" Fold promotion without 2nd instance (1st cockpit; addressed via #3478 at S2924); no "single-row FAILURE probe as latent-cascade test" Fold promotion (CODIFIED S2923; shipped as #3478 at S2924); no "user-scoping gap on notification-inbox mutations" Fold promotion without 2nd instance (1st proactive); no "dismiss observable-idempotency divergence from mark_read" Fold promotion without 2nd instance (1st); no "handler accepts bulk form but schema surfaces only single form" Fold promotion without 2nd instance (1st profile update_preferences); no "READ action name with side effect of new-row creation" Fold promotion without 2nd instance (1st profile preferences implicit get_or_create); no "error field embedded in success-shape envelope" Fold promotion without 2nd instance (1st profile preferences/update_preferences/desk_preferences); no "silent whitelist filtering without per-item feedback" Fold promotion without 2nd instance (1st profile update_preferences); no "migration-history-marks-applied-but-table-deleted-downstream" Fold promotion without 2nd instance (1st Ledger #33); no "stale-model reference across N services" substrate arc without explicit Chris directive (1st Ledger #34); no "wrapper-pre-processing changes end-to-end §5a tier" Fold promotion without 2nd instance (1st S2925 Slice 5 batch 1; codified as authoring guidance in-doc — S2926/S2927 batches 2+3 corroborate usage across 8 additional docs but not adding a new instance-class); no "recursive fanout dispatch topology proof" Fold promotion without 2nd instance → 2nd instance surfaced at S2926 (`create_brand_video`); **still gated until 3rd — S2927 workflow_orchestration_agent completion-verify is NEW-EVIDENCE-CLASS (template-driven bounded), not a 3rd instance of the LLM-planner unbounded shape**; no "sub-agent AgentExecution not auto-enumerated in job_status" UX-gap Fold promotion without recurrence (1st; documented across S2926 + S2927 authoring); no "cancel-not-recursive across WorkflowAgent tree" Fold promotion without recurrence (1st; documented across S2926 + S2927 authoring — S2927 note extends to WorkflowOrchestrationAgent-family); no "many-to-one tool→agent mapping" Fold promotion without recurrence (1st; **S2927 documented 2nd instance for the strategic_review + content_strategy_agent alias; multi-tool-single-class Fold candidate at 2nd instance**).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. CLOSED at S2904.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — 2/3. Unchanged.
- **S2909-S2926 Ledger candidates** — unchanged.
- **NEW S2927 Ledger candidates:**
  - **workflow_orchestration_agent mapping bug** — CLOSED via PR #3487 (S2927).
  - **`_tool_to_agent_name` regression test coverage** — CLOSED via PR #3487 (S2927; 3-test suite in `core/tests/test_tool_to_agent_name_mapping.py`).
  - **td_handlers_agents.py pyright drift** (10 diagnostics latent across lines 165 return / 1295 user.username / 1875 list-callable / 1965 workspace_manager / 2109 / 2148 / 2152 / 2182 / 2186 / 2202) — surfaced during S2927 PR #3487 edit; all pre-existing; candidate for bundled dev-env drift slate alongside `tasks_agents.py` AgentTaskExecution pyright drift (S2926 Ledger).
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #33 (LOW)** — CLOSED via PR #3481 (from S2925).
- **S2925 Ledger #34 (LOW)** — broader stale-model latent bug; multi-hour cleanup deferred; may become substrate work.
- **S2925 Ledger candidate — AgentTaskExecution `last_heartbeat_at`** — CLOSED via PR #3484 (S2926).
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — `error_traceback` (:114, :766) + `started_at` (:888) + `completed_at` (:1209, :1235) attribute-access mismatches. Candidate for bundled dev-env drift slate.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** **CLOSED at S2912.**
**Slice 3 — `td_handlers_core` (22 tools):** **CLOSED at S2917 (22/22).**
**Slice 4 — `td_handlers_gateway` (17 tools):** **CLOSED at S2924 (17/17).**

**Slice 5 — `tool_dispatcher` (14 tools):** **OPEN at 12/14 post-S2927.** 2 remaining. Batch 3 quartet: workflow_orchestration_agent + content_strategy_agent + marketing_strategy_agent + strategic_review. Remaining Slice 5 tools: content_writer_agent, image_editing_agent.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). S2921 §5a 4-tier taxonomy amendment shipped as doc-only sweep substrate. S2923 latent-cascade authoring convention shipped as doc-level rationale-writing pattern. S2924 Slice 4 §5a tier distribution artifact shipped as slice-close reference. S2925 Slice 5 batch 1 end-to-end §5a classification pattern shipped as authoring guidance in-doc. **S2927 delivered no new substrate arcs** — pure sweep-batch engineering + 1 latent-bug fix + 1 regression test suite (`_tool_to_agent_name` map integrity — new coverage where 0 existed).

**Total remaining tools to close:** ~17. Post-S2927 pace: 2 substantive PRs + close cascade in single session. Slice 5 CLOSE candidate at S2928.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2927 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2927: zero A4 spend — pure sweep-batch engineering (mapping fix + Slice 5 batch 3 quartet + close cascade).** A1 shipping spend was 3 PRs.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2927)

See:
- **S2927 handoff (current):** `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md`
- **S2926 handoff:** `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`
- **S2925 handoff:** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **S2924 handoff:** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **S2923 handoff:** `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`
- **S2922 handoff:** `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- **S2921 handoff:** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- **S2920 handoff:** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier blast-radius taxonomy amended S2921; Slice 5 end-to-end classification guidance in-doc post-S2925 + corroborated across S2926 batch 2 + S2927 batch 3)
- **S2927 per-tool validation docs (batch 3):** `docs/research/tools/validation/{workflow_orchestration_agent,content_strategy_agent,marketing_strategy_agent,strategic_review}_validation.md`
- **S2927 regression test:** `core/tests/test_tool_to_agent_name_mapping.py` (3 tests — new coverage where 0 existed)
- **S2926 per-tool validation docs (batch 2):** `docs/research/tools/validation/{create_brand_video,video_editing_agent,three_d_generation_agent,character_training_agent}_validation.md`
- **S2925 per-tool validation docs (batch 1):** `docs/research/tools/validation/{brand_strategy_agent,competitor_analysis_agent,customer_research_agent,create_project_from_research}_validation.md`
- **S2924 per-tool validation docs (batch 7):** `docs/research/tools/validation/{proactive,profile}_tool_validation.md`
- **S2923 per-tool validation doc:** `docs/research/tools/validation/cockpit_tool_validation.md` (§6 step 8 threshold-aware reframing shipped at #3478)
- **S2922 per-tool validation docs (batch 5):** `docs/research/tools/validation/{podcast,vip_invite}_tool_validation.md`
- **S2921 per-tool validation doc:** `docs/research/tools/validation/self_awareness_tool_validation.md`
- **S2920 per-tool validation docs (batch 3):** `docs/research/tools/validation/{mobile,calendar,conceptforge}_tool_validation.md`
- **S2919 per-tool validation docs (batch 2):** `docs/research/tools/validation/{discord,distribution,ats,narrative}_tool_validation.md`
- **S2918 per-tool validation docs (batch 1):** `docs/research/tools/validation/{analytics,audit,campaign,experiment}_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 98 non-substrate post-S2927)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no appends this session).
- **CompetitorAnalysisAgent content-FAIL engineering item (S2926):** `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`.

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
