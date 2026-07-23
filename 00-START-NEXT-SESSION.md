# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2916 CLOSE → S2916 shipped **Slice 3 batch 6** (network trio, 3 tools) + introduced §5b **Appendix N (Network-Preflight)** + brought sweep to 20/22 core surface. **S2917 OPENS WITH BATCH 7 = ASYNC DUO (`studio_tool` + `workflow_run_tool`) applying §5b + introducing Appendix N sibling for async fan-out (`Async-Fanout appendix`)** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2916 close).** First batch to introduce the §5b **Appendix N (Network-Preflight)** shape per Rigby T0 SIGN Q2 verdict — 5 standardized fields (endpoint derivation / auth posture / timeout envelope / SSRF allowlist / redirect + non-2xx handling) for tools whose first-hop is the network. Third actionless-MUTATION `TOOL_DEFAULTS` entry (`http_smoke_test` after S2910 `legal_doc_drafter_agent` + S2915 `research_and_create_tool`) — triggers the S2915 forward-carry "actionless side-effecting chain" pattern-naming evaluation at next Slice close. Rigby post-merge live verify clean — zero critical flags.

**PRs shipped this session:**
- u-d-b PR [#3462](https://github.com/clwest/donkey-betz-platform/pull/3462) — Slice 3 batch 6 (network trio + §5b Appendix N), merged at `a56accd86`.
- u-d-b PR `<TBD>` — S2916 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Tools shipped (3):**
- Batch 6: `fleet_health` (READ_ONLY, actionless), `signal_studio_judge_stats` (READ_ONLY, actionless), `http_smoke_test` (MUTATION, actionless — third actionless-MUTATION `TOOL_DEFAULTS` entry).

**Rigby joint SIGN (2-turn cycle, zero rubber-stamp):**
- Batch 6 T0 SIGN turn 1: 8 tool-grounded probes (all `repo_tool` file reads including grep for `HMAC`); 2 factual catches (fleet_health has no HMAC signing; http_smoke_test writes OpsRun + OpsRunEvent rows on every dispatch).
- Batch 6 T0 SIGN turn 2: Appendix N template drafted (5 fields, copy/pasteable) + pushback on §5c naming (kept as discipline rule inside §5b, not new section).
- Batch 6 post-merge live verify: 2 live READ_ONLY dispatches clean (14ms + 14ms latency), 1 code-verified BLOCKED check on http_smoke_test via `tool_action_metadata.py:450` read. Zero critical flags.

**Sweep progress (post-S2916):**
- Slice 3 (`td_handlers_core`): **20/22 shipped; 2 remaining.** Async duo (batch 7): `studio_tool` + `workflow_run_tool`. Slice 3 CLOSE at 20/22 or 22/22 depending on batch 7 shape.
- Total corpus untested: 52 → **49** (batch 6 flipped 3 untested → 2 full + 1 partial).
- Gap map: **43 full + 11 partial + 49 untested** (validation-doc counts).
- Session cumulative pace: 3 tools / 1 batch / 1 session (with in-depth 2-turn SIGN + post-merge live verify).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3462 recycled clean at `sha=a56accd865cc`: 5 fresh workers, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`.

---

## S2917 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Batch 7 = async duo T0 SIGN routing

**No blocking Chris D-verdict.** Batch 6 established the Appendix N shape for network tools. Batch 7 applies §5b + **introduces Appendix A (Async-Fanout)** as the sibling appendix for tools that fan out via Celery `apply_async` into agents/spiders/LLMs — closing the S2916 Q4 Fold candidate's 2nd adoption trigger (Rigby-Tool-Gap Ledger row #38).

**S2917 T0 SIGN questions to route to Rigby:**

- **Q1 async duo composition:** Ship both async tools together (`studio_tool` + `workflow_run_tool`)? Both are declared async fan-out via Celery `apply_async` per handler-read. `studio_tool` orchestrates Signal Studio operations (registered tool ID from `td_handlers_core.py`); `workflow_run_tool` is the general workflow dispatcher including `source_pack_comparison` (referenced from `competitor_comparison_tool` at S2915). Alternative: split into 2 sessions if either handler's callee list is too large to enumerate in one batch.

- **Q2 §5b Appendix A (Async-Fanout) template:** Draft the async-fanout appendix template with fields analogous to Appendix N's 5 fields — proposed: (A1) dispatch target types (agent task / workflow run / spider job / etc.), (A2) queue name(s) + priority, (A3) idempotency key or task_id envelope shape, (A4) side-effect boundary declaration (LLM calls / DB writes / network fetches that may fire in the fanned-out work), (A5) revisit-trigger discipline for opaque callees. Alternative: fewer/different fields per handler-body needs.

- **Q3 §5c opaque callee revisit trigger discipline:** Batch 6 introduced §5c as a discipline rule INSIDE §5b (per Rigby T0 SIGN turn-2 pushback). Batch 7 will test this at scale — async fan-out callees are inherently opaque at the handler layer (Celery tasks live in `core/tasks.py`; agent handlers live in `AGENT_MAP`). Should the §5c rule stay embedded in §5b, or does async-duo's opaque density warrant promoting §5c to a first-class subsection? Or does Appendix A itself carry the revisit-trigger declaration in field A5?

- **Q4 zoom-out ask (required per feedback_zoom_out_ask_per_rigby_sign):** After batch 7, Slice 3 closes at 20/22 or 22/22 depending on whether batch 7 covers both tools. What sweep-shape or substrate signals should we watch for as Slice 3 transitions to Slice 4 (`td_handlers_gateway` — 17 tools)? What are we accreting from Slice 3 (5 batches, ~1900 lines of validation docs, 10 TOOL_DEFAULTS entries + 25+ per-action records) that risks becoming unreviewable? Any Fold candidate ready for promotion at Slice 3 CLOSE (row #38 standardized-appendices, actionless-side-effecting-chain 3rd instance, IRREVERSIBLE dry_run flag 2/3, cascade-audit companion doc 1/2)?

### Alternative Step 1 candidates (unchanged from prior sessions)

- **Slice 4 open:** pivot to `td_handlers_gateway` (17 tools) and leave 2 as backlog. Not recommended — batch 7 closes Slice 3 cleanly.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2917 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without 2nd confirmed instance.**
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** 5 instances observed at Slice 3 CLOSE; framing (a) recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** S2913 batch 2 `conversation_tool.search` (LLM) + S2914 batch 4 `intelligence_tool.search` (network) = 2 instances. 3rd would trigger Fold candidate evaluation.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** S2915 `competitor_comparison_tool.delete` = 1st instance.
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** S2908 `media_tool.delete` + S2915 `competitor_comparison_tool.delete` = 2 instances. 3rd would trigger evaluation.
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** S2914 + S2915 = 2 instances of `###`-subsection breaking parity extraction; batch 6 workaround = keep `###` subsections only under §5b/Appendix N (AFTER `## Covered actions`).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** S2916 `http_smoke_test` OpsRunTracker = 1st instance.
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** S2916 signal_studio_judge_stats = 1st instance. Likely harness-side normalization — audit deferred.
- **No "grep-before-claim" Fold promotion without 2nd instance.** S2916 fleet_health HMAC-claim without grep = 1st instance.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2916 sustained decoupled pace (batch 6 was 3 tools + verify cycle).
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 6 used TOOL_DEFAULTS for all 3 (all actionless). Zero shadowing; no lint counter increment.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — corroborated at S2915 (`competitor_comparison_tool.delete`). 2/3 instances toward Fold candidate evaluation.
- **S2909 FT-1 through FT-5** — unchanged; FT-5 (`minimal_safe_args_v2`) still tracked as candidate arc.
- **S2910 FT-1 (Ledger #33)** — unchanged.
- **S2910 FT-2 (Ledger #34)** — unchanged.
- **S2911 Ledger #35** — unchanged.
- **S2911 Ledger #36 — Candidate Fold Trigger #1 (schema-drift-fix)** — unchanged.
- **S2911 Ledger #37 — HIDDEN MUTATION planner-safety pattern** — unchanged.
- **S2912 §5a mitigation note — `dry_run` add-flag pattern for actionless mutation-class dispatchers** — unchanged.
- **S2913 batch 2 Ledger candidate — envelope drift on `active_repo_tool.set/clear` + `conversation_tool.get`** — unchanged.
- **S2913 batch 3 Ledger candidates** — unchanged.
- **S2914 batch 4 Ledger candidate — metadata-classification descriptive vs runtime-gate distinction** — unchanged; no recurrence in batch 6 (validation docs correctly framed classification as audit metadata).
- **S2914 batch 4 Ledger candidate — "hidden network/LLM in read-shaped gateway" pattern reaches 2nd instance** — unchanged; not corroborated at batch 6. Watch batch 7 (async duo — highest risk for hidden cost via Celery fan-out).
- **S2914 batch 4 Ledger candidate — intelligence_tool 10 delegate/composite documented-not-verified** — unchanged.
- **S2915 batch 5 Ledger candidate — second actionless-MUTATION `TOOL_DEFAULTS` entry.** **CORROBORATED at S2916** (`http_smoke_test` = 3rd instance). **3rd instance triggers "actionless side-effecting chain" pattern-naming evaluation** at next Slice close.
- **S2915 batch 5 Ledger candidate — opaque callee trust-downgrade pattern.** Batch 6 recorded 0 new opaques — all first-hop callees enumerated with firm evidence. Discipline held. Watch batch 7 async fan-out for opaque density.
- **S2915 batch 5 Ledger candidate — model-file cascade audit gap.** Unchanged (1st instance from `competitor_comparison_tool.delete`).
- **S2915 batch 5 Ledger candidate — `NEXT_HEADING_RE` breaks parity on `###` subsections.** Not corroborated at batch 6. Batch 6 workaround = keep `###` only under §5b/Appendix N (AFTER Covered actions). Parser fix deferred; 3rd instance triggers evaluation.
- **S2915 batch 5 Ledger candidate — second IRREVERSIBLE action.** Unchanged (2/3 instances).
- **NEW S2916 batch 6 Ledger candidate — Rigby Tool Gap Ledger row #38: standardized appendices (Network-Preflight + Async-Fanout).** Classification: future-trigger. 1st adoption this batch (Network-Preflight); 2nd adoption at batch 7 (Async-Fanout) promotes to Fold-candidate evaluation at Slice 3 CLOSE.
- **NEW S2916 batch 6 Ledger candidate — Third actionless-MUTATION `TOOL_DEFAULTS` entry.** 3rd instance triggers "actionless side-effecting chain" pattern-naming evaluation at Slice 3 CLOSE.
- **NEW S2916 batch 6 Ledger candidate — Observability-tracker as unconditional MUTATION vector.** 1st instance (`OpsRunTracker`). Watch for 2nd during batch 7 or Slice 4-5.
- **NEW S2916 batch 6 Ledger candidate — Post-merge undocumented envelope field.** `signal_studio_judge_stats` returned `error_code: 'legacy_error'` in failure envelope; not documented. Likely harness-side normalization. 1st instance.
- **NEW S2916 batch 6 Ledger candidate — Cross-file architecture claim without grep verification.** My initial `fleet_health` framing claimed "HMAC signing path via mgmt command"; Rigby's grep for HMAC returned zero matches. 1st instance in sweep.
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

**Slice 3 — `td_handlers_core` (22 tools):** **20/22 shipped after S2916.** Slice CLOSE pending batch 7 (async duo).
- **S2913 batch 1: 4 tools ✓** (paid_interest_status, platform_awareness_tool, persona_tool, platform_config_tool).
- **S2913 batch 2: 4 tools ✓** (active_repo_tool, db_health_tool, conversation_tool, remember_tool).
- **S2913 batch 3: 4 tools ✓** (messaging_tool, learning_tool, dream_tool, governance_tool).
- **S2914 batch 4: 2 tools ✓** (work_tool, intelligence_tool). Explicit allowlist + transitive exclusions shape.
- **S2915 batch 5: 3 tools ✓** (task_breakdown_tool, research_and_create_tool, competitor_comparison_tool). Row-create trio + §5b first-hop dependency proof shape.
- **S2916 batch 6: 3 tools ✓** (fleet_health, signal_studio_judge_stats, http_smoke_test). Network trio + §5b Appendix N (Network-Preflight).
- **Remaining: 2 tools untested.** Async duo (batch 7): `studio_tool` + `workflow_run_tool`.

**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~49. Post-S2916 pace: 3 tools this session with in-depth SIGN + post-merge verify cycle. If S2917 ships async duo, sweep is at 22/22 = Slice 3 CLOSED.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2916 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2916: zero A4 spend — pure sweep-batch engineering (1 batch).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2916)

See:
- **S2916 handoff (current):** `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`
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
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2916 per-tool validation docs (this session's 3):** at `docs/research/tools/validation/`
  - `fleet_health_validation.md`, `signal_studio_judge_stats_validation.md`, `http_smoke_test_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 63 non-substrate post-S2916)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
