# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2917 CLOSE → S2917 shipped **Slice 3 batch 7** (async duo — `studio_tool` + `workflow_run_tool`) + introduced **§5b Appendix A (Async-Fanout)** + promoted 2 Fold candidates at Slice CLOSE. **SLICE 3 CLOSED 22/22.** **S2918 OPENS WITH SLICE 4 (`td_handlers_gateway` — 17 tools) — batch composition to be shaped by Rigby T0 SIGN at S2918 open** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2917 close).** Batch 7 introduces the §5b **Appendix A (Async-Fanout)** shape per Rigby T0 SIGN Q2 AGREE-with-edits + Chris ratification — 5 standardized fields (dispatch target types / queue+priority / task_id envelope + polling / downstream side-effect boundary / observability + cancel + revisit triggers) for tools whose first-hop is Celery `apply_async` fan-out. **Two Fold candidates promoted at Slice 3 CLOSE per Chris D2:** (1) row #38 standardized-appendices (2nd adoption via Appendix A); (2) opaque side-effecting chain via internal dispatch — Rigby Q4 broadening of the actionless pattern with concrete dispatcher-re-entry evidence at `tasks_content.py:4050-4057`. Rigby post-merge live verify clean — zero critical flags (studio_tool.list_jobs 25ms with 5 real media rows + workflow_run_tool.list 5ms empty envelope, both shape-match validation docs).

**PRs shipped this session:**
- u-d-b PR [#3464](https://github.com/clwest/donkey-betz-platform/pull/3464) — Slice 3 batch 7 (async duo + §5b Appendix A + 2 Fold promotions + Slice 3 CLOSE 22/22), merged at `68cf4f60a`.
- u-d-b PR `<TBD>` — S2917 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (2 — Slice 3 CLOSED at 22/22):**
- Batch 7: `studio_tool` (MIXED — 4 MUTATION async fan-out via `execute_agent_task`/`create_talking_video_task` to `long_running` queue + 2 READ_ONLY over CeleryTaskEvent/AsyncResult/`<Media>History`), `workflow_run_tool` (MIXED — 2 MUTATION `start`+`cancel` including `run_source_pack_workflow.apply_async` to `content` queue + `celery_app.control.revoke(terminate=True)` + 3 READ_ONLY over WorkflowRun). No new TOOL_DEFAULTS entries (MIXED composition — 11 per-action TOOL_ACTION_METADATA records instead).

**Rigby joint SIGN (2-turn cycle + 3rd for truncation workaround, zero rubber-stamp):**
- Batch 7 T0 SIGN turn 1: 10 `repo_tool` file reads + 2 searches (verified tool_runs) covering both handlers end-to-end + `execute_agent_task` + `run_source_pack_workflow` + `_impl_run_source_pack_workflow`. Q1 verdict AGREE ship-both (studio ~8 callees/237 lines; workflow_run ~4 callees/160 lines). Factual catch: my dispatch claimed studio has `:1202`/`:1241` actions — those belong to `_handle_persona`.
- Batch 7 T0 SIGN turn 2 (Q2 continuation, output-cap workaround): Appendix A drafted with 5 fields + edits (dual identifiers in A3; observability + cancel semantics in A5; task-wrapper subtype in A1; optional priority in A2). Verdict AGREE-WITH-EDITS.
- Batch 7 T0 SIGN turn 3 (Q3+Q4, output-cap workaround): Q3 pick (c) fold §5c into Appendix A A5. Q4 zoom-out: 2 Fold candidates READY at Slice 3 CLOSE (row #38 + opaque-side-effecting-chain broadened); 2 accretion risks (per-action sprawl + defaults drift); 2 sweep-shape signals for Slice 3→4 (callee-density beyond reviewability + dispatcher re-entry). Pushback on Q1 threshold: fan-out presence is itself an opacity flag regardless of callee count.
- Batch 7 post-merge live verify: 2 live READ_ONLY dispatches clean (studio 25ms, workflow_run 5ms). Zero critical flags. Envelope shapes match validation docs.

**Sweep progress (post-S2917):**
- **Slice 3 (`td_handlers_core`): CLOSED at 22/22.** All batches 1-7 shipped.
- Total corpus untested: 49 → **47** (batch 7 flipped 2 untested → full via auto-classifier).
- Gap map: **52 full · 10 partial · 7 unknown · 47 untested** (validation-doc counts post-regen).
- Session cumulative pace: 2 tools / 1 batch / 1 session (with in-depth 2-turn SIGN + Fold promotions + post-merge live verify).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3464 recycled clean at `sha=68cf4f60acc6`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs), zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`.

---

## S2918 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 opening batch T0 SIGN

**No blocking Chris D-verdict.** Slice 3 CLOSED at 22/22. Slice 4 (`td_handlers_gateway`) opens with 17 untested tools:

`analytics_tool` · `ats_tool` · `audit_tool` · `calendar_tool` · `campaign_tool` · `cockpit_tool` · `conceptforge_tool` · `discord_tool` · `distribution_tool` · `experiment_tool` · `mobile_tool` · `narrative_tool` · `podcast_tool` · `proactive_tool` · `profile_tool` · `self_awareness_tool` · `vip_invite_tool`

**S2918 T0 SIGN questions to route to Rigby:**

- **Q1 batch composition:** Pick 3-4 tools with similar first-hop characteristics for Slice 4 batch 1. Options: (a) gateway reads (analytics/audit/profile/self_awareness) — pure ORM aggregates, likely small; (b) gateway writes (campaign/experiment/distribution) — likely CRUD-heavy; (c) mixed pilot (1 read + 1 write + 1 async) to test whether Appendix A/N patterns hold across gateway. Recommend option (a) or (c); avoid (b) at open per Rigby S2914 batch-4 "mixed pilot better than all-write" precedent.
- **Q2 Appendix N/A applicability audit:** Do any Slice 4 tools appear to fit Appendix N (network-first-hop) or Appendix A (async-fanout)? Rigby probe: grep for `apply_async` + `httpx.get` + `urllib.request` across `td_handlers_gateway.py`. If ≥3 tools fit an appendix, keep the pattern; if ≤1 fits, the appendix pattern doesn't scale to gateway and needs re-evaluation.
- **Q3 first-batch shape:** Doc-only S2796 shape as default. Any candidate tool that appears MUTATION-heavy at first inspection triggers §5a deferral shape.
- **Q4 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign):** Slice 4 is 17 tools = 4-5 batches at current pace. What are we accreting from the Slice 3 close (22 tools shipped, ~5000 lines of validation docs across 7 batches, 2 Fold promotions) that we should carry forward or leave behind? Any pattern from Slice 3 that broke at scale + shouldn't be repeated at Slice 4? Any Fold candidate ready to promote at gateway-open (e.g. legacy-error envelope corroborated 4× — do we open a substrate arc?)?

### Alternative Step 1 candidates (unchanged)

- **Legacy-error envelope substrate arc** — S2916/S2917 corroborated 4-instance pattern; substrate arc opens the S2874 structured envelope migration for legacy tools. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2918 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance.**
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 instances (S2913 conversation_tool.search + S2914 intelligence_tool.search). Watch Slice 4 gateway tools closely.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915 competitor_comparison_tool.delete).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 media_tool.delete + S2915 competitor_comparison_tool.delete).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 6+7 workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916 http_smoke_test OpsRunTracker).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **4 instances corroborated post-S2917** (S2916 signal_studio_judge_stats + S2917 studio_tool.job_status + workflow_run_tool.status + workflow_run_tool.detail). Substrate arc candidate — post-D6 evaluation.
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st (S2916 fleet_health HMAC-claim).
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** **1st observed** (S2917 workflow_run_tool.start via `_impl_run_source_pack_workflow` → `tool_dispatcher._handle_competitor_comparison` at `tasks_content.py:4050-4057`). 2nd instance triggers evaluation — candidate name Appendix D.
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st (S2917 workflow_run_tool.start `focus_areas` at `td_handlers_core.py:3162`).
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st (S2917 studio single task_id vs workflow_run dual).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2917 sustained decoupled pace (batch 7 was 2 tools + 3-dispatch SIGN + live verify).
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 7 used TOOL_ACTION_METADATA per-action (MIXED tools). Batch 6 used TOOL_DEFAULTS. Batches 5/6/7 mixed patterns; not incrementing lint counter (per-action + defaults coexist as expected).
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — 2/3 (with S2915 competitor_comparison_tool.delete).
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc.
- **S2910 FT-1 (Ledger #33)** — unchanged.
- **S2910 FT-2 (Ledger #34)** — unchanged.
- **S2911 Ledger #35** — unchanged.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix)** — unchanged.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged.
- **S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — unchanged.
- **S2913 batch 2 Ledger candidate — envelope drift on `active_repo_tool.set/clear` + `conversation_tool.get`** — unchanged.
- **S2913 batch 3 Ledger candidates** — unchanged.
- **S2914 batch 4 Ledger candidate — metadata-classification descriptive vs runtime-gate distinction** — unchanged.
- **S2914 batch 4 Ledger candidate — "hidden network/LLM in read-shaped gateway" pattern reaches 2nd instance** — unchanged. Watch Slice 4 gateway sweep closely.
- **S2914 batch 4 Ledger candidate — intelligence_tool 10 delegate/composite documented-not-verified** — unchanged.
- **S2915 batch 5 Ledger candidate — second actionless-MUTATION `TOOL_DEFAULTS` entry.** **BROADENED at S2917** into "opaque side-effecting chain via internal dispatch" — Fold promoted at Slice 3 CLOSE per Chris D2.
- **S2915 batch 5 Ledger candidate — opaque callee trust-downgrade pattern.** Batch 7 recorded async fan-out as opaque with explicit Appendix A A4/A5 declarations. Discipline held.
- **S2915 batch 5 Ledger candidate — model-file cascade audit gap.** Unchanged (1/2).
- **S2915 batch 5 Ledger candidate — `NEXT_HEADING_RE` breaks parity on `###` subsections.** Batch 7 kept `###` only under §5b/Appendix A (AFTER Covered actions). Parser fix deferred; 3rd instance triggers evaluation.
- **S2915 batch 5 Ledger candidate — second IRREVERSIBLE action.** Unchanged (2/3 instances).
- **S2916 batch 6 Ledger candidate — Rigby Tool Gap Ledger row #38: standardized appendices.** **PROMOTED at Slice 3 CLOSE (S2917) per Chris D2.**
- **S2916 batch 6 Ledger candidate — Third actionless-MUTATION `TOOL_DEFAULTS` entry.** **PROMOTED at Slice 3 CLOSE (S2917) per Chris D2 as "opaque side-effecting chain via internal dispatch" Fold (Rigby Q4 broadening).**
- **S2916 batch 6 Ledger candidate — Observability-tracker as unconditional MUTATION vector.** 1/2 (`OpsRunTracker`). Watch Slice 4 gateway.
- **S2916 batch 6 Ledger candidate — Post-merge undocumented envelope field.** **CORROBORATED at S2917 — 4-instance pattern** (S2916 signal_studio_judge_stats + S2917 studio_tool.job_status + workflow_run_tool.status + workflow_run_tool.detail). Substrate arc candidate — post-D6 evaluation.
- **S2916 batch 6 Ledger candidate — Cross-file architecture claim without grep verification.** 1/2 (fleet_health HMAC-claim).
- **NEW S2917 batch 7 Ledger candidate — Contract asymmetry (single vs dual identifier in async envelopes).** 1st formal instance (studio task_id vs workflow_run run_id+task_id). Captured in Appendix A A3.
- **NEW S2917 batch 7 Ledger candidate — Undocumented handler-forwarded param.** 1st (workflow_run.start `focus_areas` at `td_handlers_core.py:3162`).
- **NEW S2917 batch 7 Ledger candidate — Dispatcher re-entry as async-fanout audit hotspot.** 1st observed (`_impl_run_source_pack_workflow` → `dispatcher._handle_competitor_comparison` at `tasks_content.py:4050-4057`). 2nd instance triggers promotion — candidate name Appendix D.
- **NEW S2917 batch 7 Ledger candidate — Auto-classifier upgrades MUTATION-deferred docs to `validated_full`.** 2nd corroboration (S2916 http_smoke_test + S2917 both batch-7 tools). Not a bug; handoff-note only.
- **NEW S2917 batch 7 Ledger candidate — Legacy-error envelope backfill 4-instance corroboration.** See above.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
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
- S2913 batches 1/2/3: 12 tools ✓
- S2914 batch 4: 2 tools ✓ (explicit allowlist + transitive exclusions shape)
- S2915 batch 5: 3 tools ✓ (row-create trio + §5b first-hop dependency proof shape)
- S2916 batch 6: 3 tools ✓ (network trio + §5b Appendix N Network-Preflight)
- **S2917 batch 7: 2 tools ✓ (async duo + §5b Appendix A Async-Fanout + 2 Fold promotions at Slice CLOSE)**

**Slice 4 — `td_handlers_gateway` (17 tools):** **NEXT** (S2918 open).
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~47. Post-S2917 pace: 2 tools this session with in-depth SIGN + Fold promotions + post-merge verify cycle. If Slice 4 sustains 3-tool/batch pace, Slice 4 CLOSE at ~6 sessions.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2917 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2917: zero A4 spend — pure sweep-batch engineering (1 batch + Slice CLOSE + 2 Fold promotions).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2917)

See:
- **S2917 handoff (current):** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **S2916 handoff:** `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`
- **S2915 handoff:** `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md`
- **S2914 handoff:** `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`
- **S2913 handoff:** `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`
- **S2912 handoff:** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **S2911 handoff:** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2909 handoff:** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
- **S2909 arc scoping doc:** `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`
- **S2908 handoff:** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (S2917: extended with Appendix N + Appendix A specs inside §5b)
- **S2917 per-tool validation docs (this session's 2):** at `docs/research/tools/validation/`
  - `studio_tool_validation.md`, `workflow_run_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 65 non-substrate post-S2917)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
