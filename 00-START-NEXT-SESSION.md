# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2925 CLOSE → SLICE 5 OPENED at 4/14. **S2926 CONTINUES SLICE 5 batch 2.** D6 MORATORIUM STILL IN FORCE.

**Refreshed 2026-07-23 (S2925 close).** First Slice 5 batch shipped — 4 tools per Chris D-verdict "ship it" on Claude+Rigby joint recommendation. Ledger #33 was reframed mid-session from "15-min migration replay" to code fix (migration 0229 explicitly DeleteModel'd core_userskill in Feb 2026; stale-model bug affects 6 services — profile_tool remediated, broader sweep filed as Ledger #34 by Rigby). Rigby T0 SIGN grounded in 10 `repo_tool` receipts; zero rubber-stamp — Q2 corrected Claude's initial "pure pass-through wrapper" framing (surfaced that `_handle_agent_tool` mutates inputs, reroutes Editor→ContentWriter, gathers workspace deliverables).

**PRs shipped this session:**
- u-d-b PR [#3481](https://github.com/clwest/donkey-betz-platform/pull/3481) — Ledger #33 profile_tool stale-model fix (Option C), merged at `c70ff84fe`.
- u-d-b PR [#3482](https://github.com/clwest/donkey-betz-platform/pull/3482) — Slice 5 batch 1 quartet (validated_full), merged at `17897125a`.
- u-d-b PR `<TBD>` — S2925 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped this session (4 — Slice 5 batch 1 quartet; Slice 5 opens at 4/14):**
- `brand_strategy_agent` → BrandStrategyAgent. Register at `tool_dispatcher.py:331`. Mapping row `td_handlers_agents.py:112`.
- `competitor_analysis_agent` → CompetitorAnalysisAgent. Register at `tool_dispatcher.py:328`. Mapping row `:110`.
- `customer_research_agent` → CustomerResearchAgent. Register at `tool_dispatcher.py:329`. Mapping row `:111`.
- `create_project_from_research` → WorkflowAgent. Register at `tool_dispatcher.py:457`. Mapping row `:127`.

All 4 dispatch through shared handler `_handle_agent_tool` at `tool_dispatcher.py:1196`. Async receipt shape: `{task_id, mode: 'async', agent, auto_followup, follow_up_will_fire, message}`. Queue: `long_running`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3482 recycled clean at `sha=17897125a`: 5 fresh workers + beat, zero surviving old PIDs.
- Rigby dispatch **4/4 receipt PASS** + **3/4 end-to-end completion PASS** (ORM verified via `AgentExecution.objects.filter(celery_task_id=...)`):
  - BrandStrategyAgent: `completed` (bonus — planned as receipt-only)
  - CompetitorAnalysisAgent: `completed` + 1 subsequent `in_progress` (delegated by WorkflowAgent per its `delegate_to_agent` capability)
  - CustomerResearchAgent: `completed`, 3937 tokens, $0.0085 — planned business-family representative
  - WorkflowAgent: `in_progress` at session close — 3-min LLM timeout + sub-agent fanout ongoing; recursive fanout topology validated (second CompetitorAnalysisAgent execution row observed)
- One pre-existing drift observed: `AgentTaskExecution has no field named 'last_heartbeat_at'` heartbeat write fails silently — NOT batch 1 regression; deferred.

**§5a taxonomy shift for Slice 5 (Rigby Q2 verdict, codified in-tree):** classification target is **end-to-end** (wrapper pre-processing + mapped agent behavior), NOT wrapper-only. All 4 batch 1 tools classified `external` end-to-end. `create_project_from_research` amplified due to WorkflowAgent recursive fanout. Codified as authoring guidance in the 4 validation docs; promotion to §5a template amendment deferred to 2nd-instance trigger.

**Batch 1 opens Slice 5 shape rhythm:**
- **5/17 previously** Slice 4 mutation-bearing (12 pure READ) — Slice 4 was per-file multi-action shape
- **Slice 5 all 14 tools:** single shared handler, agent-forwarding, async-receipt — a fundamentally different substrate shape

**Sweep progress (post-S2925, gap-map regen at close):**
- **Slice 1 (`td_handlers_ops`):** unchanged.
- **Slice 2 (`td_handlers_agents`):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`):** CLOSED at S2924 (17/17).
- **Slice 5 (`tool_dispatcher`, 14 tools):** **OPEN at 4/14 post-S2925.** 10 remaining.
- Total corpus untested: **26** post-batch-1 (from 30 pre-S2925).
- Gap map: **73 full · 10 partial · 7 unknown · 26 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 2 substantive PRs + close cascade in 1 session — matches recent pace.

Full session context: `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`.

---

## S2926 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 5 batch 2 composition SIGN cycle

Batch 1 opened Slice 5 rhythm. Batch 2 should:
- (a) Close the batch 1 deferrals: end-to-end completion-verify for `brand_strategy_agent` + `competitor_analysis_agent` (both `completed` in ORM by session close — but batch 2 SIGN should confirm final AgentResult content shape)
- (b) Cover second WorkflowAgent-family tool: `create_brand_video` OR `workflow_orchestration_agent` (both → WorkflowAgent per `_tool_to_agent_name`; one covers the shared logic + specific tool-name entry semantics)
- (c) Cover a NEW agent-family class: media-generation (`image_editing_agent` / `three_d_generation_agent` / `video_editing_agent` — Media Creation & Editing section of the mapping) OR content-strategy tier (`content_strategy_agent` / `content_writer_agent` / `marketing_strategy_agent` / `strategic_review`)

**Q1 (batch 2 composition):** propose a 3-4 tool quartet mixing (b) + (c) — one WorkflowAgent-family entry point + 2-3 tools from a new agent-family class. Rationale for family diversity: batch 2 should complete the "sample every agent-family present in Slice 5" pattern before batch 3.

**Q2 (batch 1 completion-verify carry-forward):** verify `brand_strategy_agent` + `competitor_analysis_agent` AgentResult content matches expected agent output shape (positioning + audience alignment for brand; competitor list + SWOT for competitor). One-off SIGN turn, then move to batch 2 authoring.

**Q3 (recursive fanout coverage):** for the 2 remaining WorkflowAgent-mapped Slice 5 tools (`create_brand_video` + `workflow_orchestration_agent`), does one of them offer meaningful additional evidence beyond what `create_project_from_research` already proved? If yes, cover in batch 2. If no, defer to a later batch.

**Q4 (pre-existing drift piggyback — AgentTaskExecution `last_heartbeat_at`):** small drift (~15 min); worth folding into batch 2 open as a standalone PR (like S2924 #3478 pattern + S2925 #3481 pattern) OR defer to a bundled dev-env drift slate?

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Slice 5 batch 1 delivered 3/4 completion-verifies vs planned 2 — is the completion-verify budget too conservative for future batches?
- Legacy-error envelope at 21 corroborated instances (unchanged S2925 — no new instances surfaced by batch 1 receipt-verify dispatches). Still post-D6 gated.
- Ledger #33 reframe (migration-history-marks-applied-but-table-deleted) — is there a diagnostic pattern worth codifying that would catch this class of latent bug earlier next time? (1st instance; requires 2nd instance for promotion.)

### Alternative Step 1 candidates

- **Ledger #34 broader stale-model sweep** — remove UserSkill / SkillDemonstration / AgentFeedback / GoalProgress / ProfileCompletionPrompt imports from 5 remaining services + delete model classes from `core/models_user_learning.py`. Multi-hour engineering slate.
- **AgentTaskExecution `last_heartbeat_at` migration** — ~15 min drift fix per Q4 above.
- **Rigby Tool Gap Ledger #31 orm_inspect_tool allowlist expansion** — unchanged; MEDIUM; ~1-2 hours.
- **Bundled dev-env drift slate** — group Ledger #33/#34 legacy + AgentTaskExecution `last_heartbeat_at` + S2919 narrative drift; single-session engineering slate.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note. Unchanged.

### What's forbidden at S2926 (D6 MORATORIUM still in force)

All S2924 forbidden entries carry forward (see S2924 handoff §Forbidden entries). New S2925 forbidden entries below.

**S2925 new forbidden entries (all 1st-instance — require corroborating trigger before promotion):**

- **No "migration-history-marks-applied-but-table-deleted-downstream" Fold promotion without 2nd instance.** 1st (Ledger #33 reframe). Diagnostic pattern: migration X creates table T; migration Y `DeleteModel`'s T; both marked [X] applied; code still references T. Requires code-side inspection to distinguish from dev-env drift.
- **No "stale-model reference across N services" substrate arc without explicit Chris directive.** 1st (Ledger #34 — UserSkill/etc. + 6 service imports). Multi-hour cleanup deferred.
- **No "wrapper-pre-processing changes end-to-end §5a tier" Fold promotion without 2nd instance.** 1st (Slice 5 batch 1). Codified as authoring guidance in the 4 batch 1 validation docs.
- **No "recursive fanout dispatch topology proof" Fold promotion without 2nd instance.** 1st (create_project_from_research WorkflowAgent). Codified as authoring detail.
- **No "sub-agent AgentExecution not auto-enumerated in job_status" UX-gap Fold promotion without recurrence.** 1st. Documented as authoring detail + Rigby Tool Gap Ledger candidate if recurrence.
- **No "cancel-not-recursive across WorkflowAgent tree" Fold promotion without recurrence.** 1st. Documented as authoring detail.
- **No "many-to-one tool→agent mapping" Fold promotion without recurrence.** 1st (create_project_from_research + create_brand_video + workflow_orchestration_agent all → WorkflowAgent). Documented as authoring detail.

**S2924 forbidden entries (carried forward — full list in S2924 handoff):** D6 STRATEGIC DISCOVERY MORATORIUM; no R1a-shaped proposals; no v2 → v3 harness schema bump without substrate-arc-scoped SIGN; no new gate/lint proposals; no agent-substrate validation arc; no `minimal_safe_args_v2` arc without explicit Chris directive; no entrypoint-side context-injection substrate arc; no schema-drift-fix Fold promotion; no `dry_run` infrastructure arc; no Concern C schema↔doc drift substrate arc; no `post_save signal cascade` substrate arc; no harness-level soft_error accounting substrate arc; no "metadata-classification-as-runtime-gate" substrate arc; no "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd instance (2/3); no "cascade audit companion doc" pattern promotion without 2nd instance (1/2); no "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance (2/3); no `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance (2 instances); no "observability-tracker as MUTATION vector" Fold promotion without 2nd instance (1st); no "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc (**21 instances corroborated; unchanged at S2925 close — no new instances surfaced by batch 1 receipt-verify**); no "grep-before-claim" Fold promotion (1st); no "dispatcher re-entry" Fold promotion (1st — batch 1 provides adjacent evidence for CompetitorAnalysisAgent/CustomerResearchAgent web_search dispatcher re-entry, but not a Fold promotion trigger); no "handler-forwarded param not in schema" Fold promotion (1st); no "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion (1st); no "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive (3/3 TRIGGERED; still Chris-gated); no "multi-tenant leak on detail/results action" Fold promotion; no "template-preservation swap" Fold promotion without explicit Chris directive (CODIFIED S2921); no "mixed user-scoping within single response" Fold promotion without 2nd instance (1st); no "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance (2/3); no "limit does not gate nested lists" Fold promotion without 2nd instance (1st); no "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance (1st); no "envelope-representation asymmetry" Fold promotion without 2nd instance (1st); no "00-START span-math source-of-truth regen" Fold promotion (CODIFIED S2921 as permanent close-ceremony step; validated 5 consecutive sessions S2921-S2925 inclusive); no "signal wiring exists but gate exempts tool's mutation shape → external not cascading" Fold promotion without 2nd instance (1st cockpit); no "verify-protocol authoring SIGN checkpoint" Fold promotion without 2nd instance (1st cockpit; addressed via #3478 at S2924); no "single-row FAILURE probe as latent-cascade test" Fold promotion (CODIFIED S2923; shipped as #3478 at S2924); no "user-scoping gap on notification-inbox mutations" Fold promotion without 2nd instance (1st proactive); no "dismiss observable-idempotency divergence from mark_read" Fold promotion without 2nd instance (1st); no "handler accepts bulk form but schema surfaces only single form" Fold promotion without 2nd instance (1st profile update_preferences); no "READ action name with side effect of new-row creation" Fold promotion without 2nd instance (1st profile preferences implicit get_or_create); no "error field embedded in success-shape envelope" Fold promotion without 2nd instance (1st profile preferences/update_preferences/desk_preferences); no "silent whitelist filtering without per-item feedback" Fold promotion without 2nd instance (1st profile update_preferences).

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
- **S2909-S2924 Ledger candidates** — unchanged.
- **NEW S2925 batch 1 Ledger candidates:**
  - **First Slice 5 §5a end-to-end classification exercise** — 4 batch 1 tools classified end-to-end; documented as authoring guidance in each validation doc.
  - **First WorkflowAgent-family recursive fanout topology proof** — create_project_from_research provides the anchor; documented in `create_project_from_research_validation.md` §5b Appendix A A4.
  - **Ledger #34 (LOW) — broader stale-model latent bug (UserSkill + 5 other service imports)** — added by Rigby via `deliverable_tool.append`.
  - **Post-close pin management working via session_lifecycle close** — S2926 fresh pin `pa-7e17133240eb4c44` minted atomically, wrapper rewritten. No stale-worker issues expected at S2926 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #33 (LOW)** — CLOSED via PR #3481 code fix (Option C); tool restored to live-verify. Broader latent bug per Ledger #34.
- **NEW S2925 Ledger #34 (LOW)** — broader stale-model latent bug; multi-hour cleanup deferred; may become substrate work.
- **NEW S2925 Ledger candidate — AgentTaskExecution missing `last_heartbeat_at` field** — heartbeat write fails silently for CustomerResearchAgent execution `b7681140-...` observed at S2925 batch 1 verify. Pre-existing drift (not batch 1 regression). ~15 min migration fix. Group with S2919 narrative + Ledger #33/#34 as bundled dev-env drift slate candidate.
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

**Slice 5 — `tool_dispatcher` (14 tools):** **OPEN at 4/14 post-S2925.** 10 remaining. Batch 1 quartet: brand_strategy_agent + competitor_analysis_agent + customer_research_agent + create_project_from_research. Remaining Slice 5 tools: content_strategy_agent, content_writer_agent, create_brand_video, character_training_agent, image_editing_agent, marketing_strategy_agent, strategic_review, three_d_generation_agent, video_editing_agent, workflow_orchestration_agent.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). **S2921 §5a 4-tier taxonomy amendment** shipped as doc-only sweep substrate. **S2923 latent-cascade authoring convention** shipped as doc-level rationale-writing pattern. **S2924 Slice 4 §5a tier distribution artifact** shipped as slice-close reference. **S2925 Slice 5 batch 1 end-to-end §5a classification pattern** shipped as authoring guidance in-doc (deferred to template amendment on 2nd-instance trigger).

**Total remaining tools to close:** ~24. Post-S2925 pace: 2 substantive PRs + close cascade in single session. Slice 5 continues at S2926 batch 2.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2925 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2925: zero A4 spend — pure sweep-batch engineering (Ledger #33 code fix + Slice 5 batch 1 quartet + close cascade).** A1 shipping spend was 3 PRs.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2925)

See:
- **S2925 handoff (current):** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **S2924 handoff:** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **S2923 handoff:** `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`
- **S2922 handoff:** `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- **S2921 handoff:** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- **S2920 handoff:** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a 4-tier blast-radius taxonomy amended S2921; Slice 5 end-to-end classification guidance in-doc post-S2925)
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 90 non-substrate post-S2925)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #34 added this session by Rigby via deliverable_tool.append).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
