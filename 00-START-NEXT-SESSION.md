# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2926 CLOSE → SLICE 5 ADVANCED to 8/14. **S2927 CONTINUES SLICE 5 batch 3.** D6 MORATORIUM STILL IN FORCE.

**Refreshed 2026-07-23 (S2926 close).** Batch 2 quartet shipped + heartbeat wrong-model fix shipped as sibling PR. Rigby SIGN cycle turn 1 → turn 2 arc surfaced two structural discoveries: **(1) CompetitorAnalysisAgent content-shape FAIL** on `"test dispatch"` inputs (agent runs to `status='completed'` but returns generic "concept too vague" note with no competitor list + no SWOT) — filed as workspace-deliverable engineering item `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5` per Chris D-verdict; NOT this-session scope; **(2) workflow_orchestration_agent tool_name maps to WorkflowAgent** at `td_handlers_agents.py:127` even though a `WorkflowOrchestrationAgent` class exists at `core/agents/workflow_orchestration_agent.py:105+` with 16+ built-in workflow templates (10 files reference the class including `workflow_builder.py:378` which actively consumes it). Deferred to batch 3 investigation.

**PRs shipped this session:**
- u-d-b PR [#3484](https://github.com/clwest/donkey-betz-platform/pull/3484) — AgentTaskExecution heartbeat wrong-model fix, merged at `cea3f9215`. Bug latent since Session 1100; first observed instance was S2925 CustomerResearchAgent execution.
- u-d-b PR [#3485](https://github.com/clwest/donkey-betz-platform/pull/3485) — Slice 5 batch 2 quartet (validated_full), merged at `12ca8848c`.
- u-d-b PR `<TBD>` — S2926 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped this session (4 — Slice 5 batch 2 quartet; Slice 5 advances to 8/14):**
- `create_brand_video` → WorkflowAgent (register at `tool_dispatcher.py:455`; mapping row `td_handlers_agents.py:127`). **WorkflowAgent-family completion-verify representative.**
- `video_editing_agent` → VideoEditingAgent (register at `:315`; mapping `:90`). Receipt-verify only.
- `three_d_generation_agent` → ThreeDAgent (register at `:318`; mapping `:93`). Receipt-verify only.
- `character_training_agent` → CharacterTrainingAgent (register at `:319`; mapping `:94`). **Media-family completion-verify representative** — test-dispatch scoped to `create_character` (setup only), NOT `submit_training` (billable Replicate FLUX LoRA compute).

All 4 dispatch through shared handler `_handle_agent_tool` at `tool_dispatcher.py:1196` (same as batch 1). Async receipt shape: `{task_id, mode: 'async', agent, auto_followup, follow_up_will_fire, message}`. Queue: `long_running`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3485 recycled clean at `sha=12ca8848c10e`: 5 fresh workers + beat, zero surviving old PIDs.
- Rigby dispatch **4/4 receipt PASS** (task_ids `39d44f0a`/`cf108119`/`5661edd7`/`e7a1fcaf`).
- Completion-verify outcome: see S2926 handoff §"Completion-verify outcome" (background ORM poll ran through session close).

**§5a end-to-end classification (batch 2):** All 4 classified `external`. `create_brand_video` **amplified** by WorkflowAgent recursive fanout (2nd corroborating instance — still gated per S2925 forbidden entry until 3rd). `character_training_agent` adds **out-of-band Replicate training** as a distinct downstream axis (billable, persists beyond parent AgentExecution). All media agents add **media provider egress** (ffmpeg/Cloudinary/Replicate) as a distinct downstream axis vs the LLM-only egress in batch 1.

**Sibling engineering-backlog item filed (NOT shipped as code this session):**
- CompetitorAnalysisAgent content-shape FAIL — deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Category `agent_quality`, deliverable_type `engineering_backlog`, status `ready` (Rigby noted `deliverable_tool` doesn't accept `status='open'`; open-backlog semantics via tags). Evidence: batch 1 CompetitorAnalysisAgent execution `759198d5-259c-4cc5-966a-f167d4102125`.

**Sweep progress (post-S2926, gap-map regen at close):**
- **Slice 1 (`td_handlers_ops`):** unchanged.
- **Slice 2 (`td_handlers_agents`):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`):** CLOSED at S2924 (17/17).
- **Slice 5 (`tool_dispatcher`, 14 tools):** **OPEN at 8/14 post-S2926.** 6 remaining.
- Total corpus untested: **22** post-batch-2 (from 26 pre-S2926).
- Gap map: **77 full · 10 partial · 7 unknown · 22 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 2 substantive PRs + close cascade in 1 session — matches recent pace.

Full session context: `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`.

---

## S2927 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 5 batch 3 composition SIGN cycle

Batch 2 completed the "sample every agent-family present in Slice 5" pattern (Business Research at batch 1 + Media Creation & Editing + WorkflowAgent at batch 2). Batch 3 should:
- (a) Cover `workflow_orchestration_agent` with the **mapping-vs-class-file asymmetry investigation** as a first-order §6 discovery — decides whether the tool_name→WorkflowAgent mapping is intentional or a stale-mapping bug to fix
- (b) Cover 2–3 tools from the content-strategy tier (`content_strategy_agent` / `content_writer_agent` / `marketing_strategy_agent` / `strategic_review`) — new agent-family class
- (c) Optionally: cover `image_editing_agent` (last remaining media-family tool)

**Q1 (batch 3 composition):** propose a 3-4 tool quartet mixing (a) + (b), optionally including (c). Rationale for including workflow_orchestration_agent: it's the last WorkflowAgent-family tool in Slice 5 + surfacing the mapping asymmetry converts a discovery into either a documented decision or a fix.

**Q2 (workflow_orchestration_agent asymmetry investigation):**
Before authoring the validation doc, decide: is `td_handlers_agents.py:127` mapping `'workflow_orchestration_agent'` → `'WorkflowAgent'` (a) intentional (WorkflowAgent is a superset that handles both orchestration + custom workflows), (b) legacy carry-over (WorkflowOrchestrationAgent was newer + the mapping wasn't updated), or (c) a bug (should map to `'WorkflowOrchestrationAgent'`)? Check `agent_router` for whether both agents have registered handlers; check `AGENT_MAP` for whether both are enabled. If (c), a mapping fix PR should precede the validation doc.

**Q3 (recursive fanout coverage — 3rd instance trigger):**
If `workflow_orchestration_agent` DOES route to WorkflowAgent (i.e., asymmetry stays), its completion-verify would provide the 3rd instance of recursive fanout topology proof — unlocking Fold promotion per S2925 forbidden entry. If it routes to `WorkflowOrchestrationAgent` after a fix, that's a different agent's fanout shape (16+ workflow templates) — potentially new evidence class.

**Q4 (deferred item pickup — pick 0 or 1):**
- (a) CompetitorAnalysisAgent content-FAIL remediation (deliverable `5703a6c8-...`) — targeted engineering slate; ~1-2 sessions
- (b) Ledger #34 broader stale-model sweep (UserSkill + 5 other service imports) — multi-hour engineering
- (c) AgentTaskExecution `error_traceback` / `started_at` / `completed_at` pre-existing pyright drift (lines 114/766/888/1209/1235 in `tasks_agents.py` — same class as PR #3484's fix but different attributes) — worth folding into a small dev-env drift PR alongside batch 3

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Recursive fanout topology proof is now at 2/3 corroborating instances (S2925 create_project_from_research + S2926 create_brand_video). If S2927 batch 3 hits the 3rd, do we have the right Fold promotion shape drafted? Preview it during batch 3 SIGN to avoid a scramble at instance-3-plus-1.
- Content-shape FAIL (CompetitorAnalysisAgent) is 1st instance. If batch 3 completion-verify surfaces a similar false-PASS in another agent (content-strategy tier is next; those are also structured-output agents), promote the diagnostic pattern to Fold.
- workflow_orchestration_agent mapping asymmetry — if the resolution is "fix the mapping" that changes the tool_dispatcher's registration → touches `_tool_to_agent_name` cardinality. Worth checking whether OTHER tools have similar tool_name-vs-class-name asymmetries via grep before shipping the fix.

### Alternative Step 1 candidates

- **workflow_orchestration_agent mapping fix ONLY** — standalone PR (~30-60 min) if the S2927 open SIGN cycle concludes the asymmetry is a bug not a wrapper strategy. Batch 3 authoring proceeds after.
- **CompetitorAnalysisAgent content-FAIL remediation** — targeted engineering slate; deliverable `5703a6c8-...`.
- **Ledger #34 broader stale-model sweep** — multi-hour engineering.
- **Bundled dev-env drift slate** — group Ledger #33/#34 legacy + AgentTaskExecution pre-existing pyright drift + S2919 narrative drift into one PR.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note. Unchanged.

### What's forbidden at S2927 (D6 MORATORIUM still in force)

All S2925 forbidden entries carry forward (see S2925 handoff §Forbidden entries). New S2926 forbidden entries below.

**S2926 new forbidden entries (all 1st-instance — require corroborating trigger before promotion):**

- **No "wrong-model reference to sister model in same registry" Fold promotion without 2nd instance.** 1st (PR #3484 `AgentTaskExecution` vs `AgentExecution` heartbeat write). Same class of bug is visible in the pyright pre-existing warnings at `tasks_agents.py:114/766/888/1209/1235` (`error_traceback`/`started_at`/`completed_at`) — but those are attribute-access issues on adjacent methods, not the same heartbeat write pattern. Watch for a second HEARTBEAT-shaped instance before promoting.
- **No "content-shape FAIL surfaces only under completion-verify, not receipt-verify" Fold promotion without 2nd instance.** 1st (CompetitorAnalysisAgent, S2926 Q2 discovery). Watch for a second agent that runs cleanly to `status='completed'` but returns AgentResult failing an expected content schema. Codify the diagnostic pattern (add a content-shape check helper?) after 2nd instance.
- **No "third-tier identifier surface in AgentResult (external-provider id beyond AgentExecution + celery_task_id)" Fold promotion without 2nd instance.** 1st (character_training_agent Replicate prediction id documented). Requires 2nd instance for promotion.
- **No "media provider egress as distinct §5a downstream axis" Fold promotion without 2nd instance.** 1st (batch 2 media agents' Cloudinary/ffmpeg/Replicate egress documented). Requires 2nd instance for promotion.
- **No "semantic-alias contract for shared-agent tool_names" Fold promotion without corroboration.** 1st exercise (`create_brand_video` vs `create_project_from_research` in the same WorkflowAgent). Documented as an authoring convention in `create_brand_video_validation.md` §Related; requires 2nd instance for pattern promotion.

**S2925 forbidden entries (carried forward — full list in S2925 handoff):** D6 STRATEGIC DISCOVERY MORATORIUM; no R1a-shaped proposals; no v2 → v3 harness schema bump without substrate-arc-scoped SIGN; no new gate/lint proposals; no agent-substrate validation arc; no `minimal_safe_args_v2` arc without explicit Chris directive; no entrypoint-side context-injection substrate arc; no schema-drift-fix Fold promotion; no `dry_run` infrastructure arc; no Concern C schema↔doc drift substrate arc; no `post_save signal cascade` substrate arc; no harness-level soft_error accounting substrate arc; no "metadata-classification-as-runtime-gate" substrate arc; no "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd instance (2/3); no "cascade audit companion doc" pattern promotion without 2nd instance (1/2); no "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance (2/3); no `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance (2 instances); no "observability-tracker as MUTATION vector" Fold promotion without 2nd instance (1st); no "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc (**22 instances corroborated post-S2926 — the 22nd is `orm_inspect_tool` allowlist rejection during Rigby's Q2 verify; still post-D6 gated**); no "grep-before-claim" Fold promotion (1st); no "dispatcher re-entry" Fold promotion (1st); no "handler-forwarded param not in schema" Fold promotion (1st); no "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion (1st); no "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive (3/3 TRIGGERED; still Chris-gated); no "multi-tenant leak on detail/results action" Fold promotion; no "template-preservation swap" Fold promotion without explicit Chris directive (CODIFIED S2921); no "mixed user-scoping within single response" Fold promotion without 2nd instance (1st); no "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance (2/3); no "limit does not gate nested lists" Fold promotion without 2nd instance (1st); no "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance (1st); no "envelope-representation asymmetry" Fold promotion without 2nd instance (1st); no "00-START span-math source-of-truth regen" Fold promotion (CODIFIED S2921 as permanent close-ceremony step; validated 6 consecutive sessions S2921-S2926 inclusive); no "signal wiring exists but gate exempts tool's mutation shape → external not cascading" Fold promotion without 2nd instance (1st cockpit); no "verify-protocol authoring SIGN checkpoint" Fold promotion without 2nd instance (1st cockpit; addressed via #3478 at S2924); no "single-row FAILURE probe as latent-cascade test" Fold promotion (CODIFIED S2923; shipped as #3478 at S2924); no "user-scoping gap on notification-inbox mutations" Fold promotion without 2nd instance (1st proactive); no "dismiss observable-idempotency divergence from mark_read" Fold promotion without 2nd instance (1st); no "handler accepts bulk form but schema surfaces only single form" Fold promotion without 2nd instance (1st profile update_preferences); no "READ action name with side effect of new-row creation" Fold promotion without 2nd instance (1st profile preferences implicit get_or_create); no "error field embedded in success-shape envelope" Fold promotion without 2nd instance (1st profile preferences/update_preferences/desk_preferences); no "silent whitelist filtering without per-item feedback" Fold promotion without 2nd instance (1st profile update_preferences); no "migration-history-marks-applied-but-table-deleted-downstream" Fold promotion without 2nd instance (1st Ledger #33); no "stale-model reference across N services" substrate arc without explicit Chris directive (1st Ledger #34); no "wrapper-pre-processing changes end-to-end §5a tier" Fold promotion without 2nd instance (1st S2925 Slice 5 batch 1; **codified as authoring guidance in-doc — S2926 batch 2 uses the same authoring guidance across all 4 new docs, corroborating usage but not adding a new instance**); no "recursive fanout dispatch topology proof" Fold promotion without 2nd instance → **2nd corroborating instance surfaced this session (create_brand_video); still gated until 3rd**; no "sub-agent AgentExecution not auto-enumerated in job_status" UX-gap Fold promotion without recurrence (1st; documented in create_brand_video doc as continued authoring detail); no "cancel-not-recursive across WorkflowAgent tree" Fold promotion without recurrence (1st; documented in create_brand_video doc as continued authoring detail); no "many-to-one tool→agent mapping" Fold promotion without recurrence (1st).

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
- **S2909-S2925 Ledger candidates** — unchanged.
- **NEW S2926 Ledger candidates:**
  - **WorkflowOrchestrationAgent mapping-vs-class-file asymmetry** — surfaced during batch 2 SIGN; documented in `create_brand_video_validation.md` §Related; investigation queued for S2927 batch 3.
  - **Content-shape FAIL diagnostic pattern (CompetitorAnalysisAgent)** — 1st instance; deliverable `5703a6c8-...` in Donkey Betz workspace; requires 2nd instance for Fold promotion of the diagnostic pattern.
  - **`deliverable_tool.create` doesn't accept `status='open'`** — Rigby self-flagged; minor tool-surface gap; not appended to Rigby Tool Gap Ledger this session (Rigby's discretion).
  - **`orm_inspect_tool` allowlist gap for `AgentExecution`** — recurrence of existing Ledger #31 (MEDIUM); worked around via `execution_history_tool`.
  - **AgentTaskExecution pre-existing pyright drift** — `error_traceback` (:114, :766) + `started_at` (:888) + `completed_at` (:1209, :1235) attribute-access mismatches. Same class as PR #3484's fix but different attributes. Candidate for bundled dev-env drift slate.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #33 (LOW)** — CLOSED via PR #3481 (from S2925).
- **S2925 Ledger #34 (LOW)** — broader stale-model latent bug; multi-hour cleanup deferred; may become substrate work.
- **S2925 Ledger candidate — AgentTaskExecution `last_heartbeat_at`** — **CLOSED via PR #3484 (S2926).** Bug was wrong-model reference (`AgentTaskExecution` vs `AgentExecution`), not missing field.
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

**Slice 5 — `tool_dispatcher` (14 tools):** **OPEN at 8/14 post-S2926.** 6 remaining. Batch 2 quartet: create_brand_video + video_editing_agent + three_d_generation_agent + character_training_agent. Remaining Slice 5 tools: content_strategy_agent, content_writer_agent, marketing_strategy_agent, strategic_review, image_editing_agent, workflow_orchestration_agent.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). **S2921 §5a 4-tier taxonomy amendment** shipped as doc-only sweep substrate. **S2923 latent-cascade authoring convention** shipped as doc-level rationale-writing pattern. **S2924 Slice 4 §5a tier distribution artifact** shipped as slice-close reference. **S2925 Slice 5 batch 1 end-to-end §5a classification pattern** shipped as authoring guidance in-doc (deferred to template amendment on 2nd-instance trigger — S2926 batch 2 uses the same guidance, corroborating usage but not adding a new instance-class). **S2926 delivered no new substrate arcs** — pure sweep-batch engineering + 1 latent-bug fix.

**Total remaining tools to close:** ~22. Post-S2926 pace: 2 substantive PRs + close cascade in single session. Slice 5 continues at S2927 batch 3.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2926 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2926: zero A4 spend — pure sweep-batch engineering (heartbeat fix + Slice 5 batch 2 quartet + close cascade).** A1 shipping spend was 3 PRs.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2926)

See:
- **S2926 handoff (current):** `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`
- **S2925 handoff:** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **S2924 handoff:** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **S2923 handoff:** `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`
- **S2922 handoff:** `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- **S2921 handoff:** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- **S2920 handoff:** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier blast-radius taxonomy amended S2921; Slice 5 end-to-end classification guidance in-doc post-S2925 + corroborated across S2926 batch 2)
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 94 non-substrate post-S2926)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no appends this session).
- **CompetitorAnalysisAgent content-FAIL engineering item (S2926):** `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`.

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
