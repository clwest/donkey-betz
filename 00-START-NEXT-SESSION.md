# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2911 CLOSE → S2911 Slice 2 batch 6a shipped (4 tools; scoped-to-READ_ONLY subset) + reasoning_engine drift-fix (batch 6b pre-req). **S2912 OPENS WITH SLICE 2 CLOSE — batch 6b = universal_agent_tool alone (last Slice 2 tool)** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2911 close).** Fifth accelerated PA-tools sweep batch in Slice 2 + a substrate-arc-adjacent drift-fix. Batch 6a scoped-to-READ_ONLY-subset for 4 mixed-safety tools (`opportunity_manager_tool`, `task_manager_tool`, `pipeline_orchestrator_tool`, `video_history_tool`) via per-action `TOOL_ACTION_METADATA` seeds. Second PR closed 1st confirmed instance of schema↔handler drift class Rigby flagged at S2911 T0 zoom-out (reasoning_engine schema aligned to handler + latent handler bug fixed).

**PRs shipped this session:**
- u-d-b PR [#3448](https://github.com/clwest/donkey-betz-platform/pull/3448) — S2911 Slice 2 batch 6a scoped-to-R subset sweep, merged at `a35ebd5c5`.
- u-d-b PR [#3449](https://github.com/clwest/donkey-betz-platform/pull/3449) — S2911 reasoning_engine_tool drift-fix (pre-req for batch 6b), merged at `547fba978`.
- u-d-b PR `<TBD>` — S2911 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Batch 6a outcomes:**

- **`opportunity_manager_tool`** — 6 actions: 3R covered (list/stats success + get error_captured on missing opportunity_id), 2 MUTATION + 1 IRREVERSIBLE (`delete` cascade) skipped. HIDDEN mutation cascade-to-OpportunityTask documented.
- **`task_manager_tool`** — 6 actions: 2R covered, 3 MUTATION + 1 IRREVERSIBLE skipped. **HIDDEN MUTATION on `create`** when opportunity_id absent (implicit standalone Opportunity creation) — schema description now warns planner at dispatch time (Rigby Q4a same-PR mitigation).
- **`pipeline_orchestrator_tool`** — 1 action (status; Initiative aggregate reads); fully covered.
- **`video_history_tool`** — 7 actions: 5R covered (1 success + 4 error_captured on missing required args), 2 MUTATION (async Celery: transcribe + content_pack) skipped.

**Drift-fix outcomes (reasoning_engine_tool):**

- Schema align direction: schema→handler. Removed dead params (query, reasoning_type); added action enum (status|thoughts|trigger) matching handler branches.
- **LATENT HANDLER BUG caught + fixed in-scope**: `_handle_reasoning_engine` at line 5388 filtered `AgentExecution.objects.filter(agent_name='ThinkingAgent')` but there is no `agent_name` field. Fixed to `agent__name='ThinkingAgent'` (FK traversal). Also fixed `.values('success')` → `.values('status')`. Both bugs invisible pre-fix because callers passed `{query}` and fell into `status` default; never hit `thoughts` branch.
- Post-merge live-dispatch: `thoughts limit=3` returned 3 real completed ThinkingAgent executions with proper shape.

**Sweep progress (post-S2911):**
- Slice 2 (`td_handlers_agents`): 6 batches + drift-fix = **24/25 shipped**; 1 remaining (`universal_agent_tool`).
- Total corpus untested: 75 → 70 (-5). Gap map: 31 full + 8 partial + 70 untested.

**Rigby joint SIGN (3 substantive cycles this session, zero rubber-stamp):**
- Batch 6a T0 SIGN AGREE-with-edits — 4-tool composition + scoped-to-READ_ONLY subset shape ratified; Q4 zoom-out surfaced 4 concerns (reasoning_engine schema↔handler drift 1st confirmed instance, HIDDEN mutation on task_manager.create, opportunity_manager.delete CASCADE, coupling between ORM tools + dispatch tools).
- Batch 6a T1 SIGN AGREE-with-edits — 8+ handler/doc tool_runs cross-checks; Q3 additional catch on opportunity_manager.delete same-envelope-drift-class; Q4 same-PR mitigations applied (task_manager schema description warning) + separate PR for drift-fix ratified.
- Drift-fix T1 SIGN AGREE — 4 repo tool_runs; direction ratified via grep confirming `reasoning_type` has zero refs outside metadata; **Q2 formalized rule of thumb**: *"latent-bug fixes can stay in-scope when required to make the newly-aligned contract actually work, and you prove it with harness output in the PR description."* **Q3 Candidate Fold — Trigger #1**: *"when fixing schema drift, always exercise every action branch, not just the previously-callable ones."*

**Post-merge live-dispatch verified (per PLAYBOOK-7.4.4):**
- Batch 6a: 4/4 tools dispatched cleanly (envelope shapes match doc §6.1); real data snapshot 47 opportunities / 62 initiatives / 0 tasks / 0 videos.
- Drift-fix: reasoning_engine `thoughts limit=3` returned 3 real completed executions post-recycle.

Full session context: `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`.

---

## S2912 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Close Slice 2 with batch 6b

**No blocking Chris D-verdict.** S2911 shipped 2 PRs cleanly; drift-fix substrate is clean; harness trustworthy post-S2909 arc + S2911 latent-bug reveal.

**Slice 2 remaining: 1 tool** — `universal_agent_tool` (only tool left in `td_handlers_agents`).

**S2912 T0 SIGN questions to route to Rigby:**
- Batch 6b composition: universal_agent_tool alone (1-tool batch pattern precedent: S2908 media_tool single-tool ship?) or pull in a tool from another slice to make a coherent 2-3 tool batch?
- Shape recommendation: TOOL_DEFAULTS MUTATION conditional (actionless, LLM-cost surface) vs per-action metadata. `universal_agent_tool` at `td_handlers_agents.py:1771` — inspect handler for what side-effects on `context` param, what agents are auto-routable vs blocked.
- Bridge dependencies: agent dispatch has no external bridges but does invoke LLM (cost surface).
- Q4 zoom-out ask (per feedback_zoom_out_ask_per_rigby_sign) — required. Slice 2 closes at end of this session; what does closing Slice 2 unlock / where does the coupling with Slice 3 (`td_handlers_core`) start?

### Alternative Step 1 candidates (unchanged from S2911 open)

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2912 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.** v2 is frozen at S2909 close.
- No new gate/lint proposals (S2910 FT-3/FT-4 stay logged, not built).
- No agent-substrate validation arc (peer to PA tools sweep). Requires explicit Chris directive.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.** FT-5 is a tracked candidate; opens only via Chris ratify.
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.** S2910 Ledger #33 candidate is logged, not built.
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance.** S2911 Ledger #36 is Candidate Fold — Trigger #1 only; forward-carry per Rigby T1 SIGN Q3.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close.** S2905→S2911 sustained accelerated pace.
- **Response-level introspection field creep** — Ledger row 162 (S2896). Same-PR mitigated.
- **S2905 metadata-pattern-selection lint** — substrate-arc-scope. Batch 6a used uniform per-action Pattern C; no shadowing. Counter unchanged.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1 conflates OBS_DISABLED vs BRIDGE_UNREACHABLE error envelopes** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — confirmation-flow ADR candidate. Design-arc-scope; deferred.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc, opens only via explicit Chris directive.
- **S2910 FT-1 (Ledger #33) — Entrypoint-side context-injection test coverage gap** — unchanged.
- **S2910 FT-2 (Ledger #34) — Doc-pointer-verification lint candidate** — 1 instance S2910; no new instances S2911. Unchanged.
- **NEW S2911 Ledger #35 — Envelope-shape inconsistency on `opportunity_manager.delete` + `task_manager.delete` unknown-id paths** — both return inline `{success: False}` instead of raising. Same class as S2907 FT-5 candidate. Not urgent (both IRREVERSIBLE-skipped this ship); track for future MUTATION-coverage batch.
- **NEW S2911 Ledger #36 — Candidate Fold — Trigger #1**: "when fixing schema drift, always exercise every action branch, not just the previously-callable ones." Rigby T1 SIGN Q3 verdict: forward-carry, promote on 2nd independent instance.
- **NEW S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern**: `task_manager.create` implicit parent-Opportunity creation. Same-PR mitigated with schema description warning. Track for other tools with similar implicit-parent-row patterns.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — Unchanged.
- **Applicability metadata pattern (entry #28)** — Unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — Unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits (`requested_model_id`, `was_policy_reroute`) — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batches 1-4 (S2892-S2895): 9 tools ✓
- **S2896-S2899:** 4 engineering ships (Rows A/B/C/#29 mitigated).
- **S2900-S2904:** Row 161 substrate arc — CLOSED.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session) + `ops_tool` sweep slot (promoted from partial at T1c) + Phase 0 heading fixes for 8 close_with_short_note tools.

**Slice 2 — `td_handlers_agents` (25 tools):**
- **S2905 batch 1: 4 tools ✓** (gates_tool, pilots_tool, cost_telemetry_tool, revenue_tracker_tool). Mixed-pattern proof.
- **S2906 batch 2: 4 tools ✓** (get_body_vitals, check_resource_budget, get_system_alerts, web_search). Actionless-only proof.
- **S2907 batch 3: 3 tools ✓** (ml_analysis, voice_clone_tool, orm_inspect_tool). Small-actionful all-READ_ONLY proof.
- **S2908 batch 4: 4 tools ✓** (bpaas_tool, davinci_tool, obs_tool, media_tool). SHAPE-BREAK mixed-scoped-to-READ_ONLY-subset proof.
- **S2909:** substrate cleanup arc (T1+T2 shipped, arc closed). Zero sweep-batch contribution.
- **S2910 batch 5: 4 tools ✓** (brainstorm_tool, web_fetch_tool, schedule_followup, legal_doc_drafter_agent). Mixed-composition-across-batch proof.
- **S2911 batch 6a: 4 tools ✓** (opportunity_manager_tool, task_manager_tool, pipeline_orchestrator_tool, video_history_tool). Scoped-to-READ_ONLY-subset mixed-safety proof (all pure ORM, no bridges).
- **S2911 drift-fix ✓** (reasoning_engine_tool). Schema↔handler drift 1st confirmed instance CLOSED + latent handler bug fixed.
- **S2912+ batch 6b:** 1 tool remaining (`universal_agent_tool`). Slice 2 closes at end of S2912.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2 close.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~52. Post-substrate sweep pace at S2905-S2911 = 4/4/3/4/4/4 tools/batch + 1 drift-fix. Extrapolated remaining ~8-11 sessions at accelerated pace with trustworthy harness.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2911 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2911: zero A4 spend — pure sweep-batch + drift-fix engineering.** A1 shipping spend was batch 6a PR + drift-fix PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2911)

See:
- **S2911 handoff (current):** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2909 handoff:** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
- **S2909 arc scoping doc:** `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`
- **S2908 handoff:** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping (closed at S2904):** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + T1a/T1b/T1c child docs
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2911 per-tool validation docs (this session):** `opportunity_manager_tool_validation.md`, `task_manager_tool_validation.md`, `pipeline_orchestrator_tool_validation.md`, `video_history_tool_validation.md`, `reasoning_engine_tool_validation.md`
- **S2910 per-tool validation docs:** `brainstorm_tool_validation.md`, `web_fetch_tool_validation.md`, `schedule_followup_validation.md`, `legal_doc_drafter_agent_validation.md`
- **S2908 per-tool validation docs:** `bpaas_tool_validation.md`, `davinci_tool_validation.md`, `obs_tool_validation.md`, `media_tool_validation.md`
- **S2907 per-tool validation docs:** `ml_analysis_validation.md`, `voice_clone_tool_validation.md`, `orm_inspect_tool_validation.md`
- **S2906 per-tool validation docs:** `get_body_vitals_validation.md`, `check_resource_budget_validation.md`, `get_system_alerts_validation.md`, `web_search_validation.md`
- **S2905 per-tool validation docs:** `gates_tool_validation.md`, `pilots_tool_validation.md`, `cost_telemetry_tool_validation.md`, `revenue_tracker_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 42 non-substrate post-S2911)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entries #35 + #36 + #37 candidates surfaced this session; workspace mirror TBD via Rigby dispatch).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
