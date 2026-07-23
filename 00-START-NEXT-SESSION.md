# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2905 CLOSE → First accelerated sweep batch ✓ shipped. Substrate multiplier validated. S2906 opens with Slice 2 batch 2 (4-5 more read-only tools from `td_handlers_agents.py`) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2905 close).** First accelerated PA-tools sweep batch after the Row 161 substrate arc close (T1c/T1a/T1b all shipped S2901-S2904). PR [#3435](https://github.com/clwest/donkey-betz-platform/pull/3435) merged at `7d763b504`. Four tools validated end-to-end via the T1a auto-harness + T1b template v1 opt-in: `gates_tool`, `pilots_tool`, `cost_telemetry_tool`, `revenue_tracker_tool` (12 actions total; 3 uniform-safety via TOOL_DEFAULTS + 1 mixed-safety via per-action TOOL_ACTION_METADATA).

**Substrate multiplier validated (per S2904 §Ledger row 161 mitigation claim):**
- Zero manual dispatch — T1a auto-harness pre-populated response shapes for all 12 actions
- First 4 `pass` verdicts appear in the gap map (0 → 4)
- `validated_full: 12 → 16 (+4)`, `untested: 94 → 90 (-4)`, `template_compliance pass: 0 → 4 (+4)`
- Rigby joint SIGN: 6 verification tool_runs, AGREE on A/B/C/D, AGREE-with-edits on zoom-out ask (folded same-PR)
- Both metadata patterns exercised in first accelerated batch — proves the code path for uniform + mixed tools

**Rigby joint SIGN (S2905):** T1 SIGN routed with 6 tool_runs. AGREE on all 4 verification sections A/B/C/D. AGREE-with-edits on zoom-out ask — pattern-selection rule folded into `core/services/tool_action_metadata.py` header comment before merge (rule + coexistence risk + escalation-to-lint trigger stated inline). Zero rubber-stamp SIGN.

**PRs shipped this session:**
- u-d-b PR [#3435](https://github.com/clwest/donkey-betz-platform/pull/3435) — S2905 Slice 2 batch 1, merged at `7d763b504`
- u-d-b PR `<TBD>` — S2905 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- Fold — mixed-pattern first-batch coupling risk caught by Rigby SIGN zoom-out → `same_pr_mitigated`. Choosing 3 TOOL_DEFAULTS tools + 1 per-action tool as the FIRST accelerated batch was intentional but validates two things at once (substrate multiplier + metadata-pattern comparison). Same-PR mitigation shipped: pattern-selection rule + coexistence risk statement now in code header adjacent to the map. Escalation trigger: if ≥3 sweep sessions mix patterns without rule-based justification, promote to a lint (flag per-action records shadowing tool-defaults with same safety class).

Full session context: `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`.

---

## S2906 open sequence

### Step 1 (RECOMMENDED FIRST ACTION) — Slice 2 batch 2 (`td_handlers_agents`, 4-5 more read-only tools)

**S2906 recommended open: Slice 2 batch 2.** With S2905 proving the accelerated pace, the next batch should push toward the 8-10 tools/session target and exercise the actionless-tool shape (tools whose schema has no `action` enum — the T1a harness produces zero-row artifacts for these, so §Covered actions authoring depends on handler-trace evidence).

**Concrete work:**
- Pick 4-5 read-only tools from remaining 21 in `td_handlers_agents.py` per `PA_TOOLS_GAP_MAP.md` triage slice.
- Good actionless candidates: `get_body_vitals`, `check_resource_budget`, `get_system_alerts`, `web_search` (all have no `action` enum → single dispatch surface).
- Larger candidate for stretch: `orm_inspect_tool` (10+ actions, more author time; would test template shape at scale).
- Author validation docs using T1b canonical template with `Template variant: sweep` + `Template version: v1`.
- Add TOOL_DEFAULTS entries for each new tool (or per-action if mixed-safety surfaces).
- Regenerate `PA_TOOLS_GAP_MAP.md`; expect pass verdicts to climb 4 → 8+ post-batch.

**Session cap:** target 1 session for batch of 5-6 (accelerated pace). S2905 shipped 4 in a single session — S2906 can push higher now that both metadata patterns are proven and the harness output shape is stable.

### Alternative Step 1 candidates

- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears all remaining parity mismatches (agent_introspection_tool, autopilot_tool, deliverable_tool, kb_tool, ops_tool, repo_tool, session_tool, workspace_tool). Still valid if Chris wants clean parity gate before more sweep sessions.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per the pre-commit note (§ below, unchanged).

**Recommend Slice 2 batch 2** — sustains sweep momentum; Phase 0 heading fixes + Slice 1.5b can bundle into subsequent S2907+ sessions.

### What's forbidden at S2906 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- No v1 → v2 harness schema bump without substrate-arc-scoped SIGN. FT-2 (`soft_error` outcome) would need this; do NOT act on it without the SIGN cycle.
- No v1 → v2 template variant bump without substrate-arc-scoped SIGN. If a third template variant is proposed at any point, that's ZO-Q8's trigger — evaluate structured-parse migration, not just add another variant.
- No agent-substrate validation arc (peer to PA tools sweep). Requires explicit Chris directive.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — Chris pivoted to the sweep at S2892. If character-os side pings, stand by per pre-S2892 protocol.
- **Testing Discipline chapter candidacy** — ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — ledger row 159. Unchanged.
- **2-tier evidence template promotion** — ledger row 160. Triggers after 1-2 more large-surface sweeps adopt cleanly.
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close. First accelerated batch shipped S2905 (PR #3435) — 4 tools with 12 actions in a single session, first 4 `pass` verdicts, both metadata patterns exercised.**
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
- **Harness timestamp churn** — S2903 fold, `future_trigger`. Trigger to act: harness becomes CI-invoked OR a PR needs to isolate content-change signal.
- **T1a FT-1 defaulted-tool action-set change lint** — S2903 substrate-arc-scope. Trigger: pre-commit or CI shape becomes concrete.
- **T1a FT-2 harness `soft_error` outcome value** — S2903 substrate-arc-scope. Trigger: v1 → v2 schema bump signed off.
- **T1b ZO-Q2 warn-noise escalation ladder** — S2904 substrate-arc-scope. Trigger: 5+ sweep sessions where `template_compliance` warn count is NOT monotonically decreasing → any TOUCHED legacy doc must upgrade to `Template version: v1` in same PR. Do NOT escalate untouched legacy.
- **T1b ZO-Q7 automated corpus-counter helper** — S2904 substrate-arc-scope. Trigger: any §1 corpus-survey section claiming numeric distribution over `docs/research/tools/validation/` — write a tiny helper (script or mgmt command) that prints (i) total *_tool_validation.md count / (ii) sweep-vs-protocol split by Template variant / (iii) missing-frontmatter counts / (iv) top-N offenders. Then require future §1 surveys to source from output.
- **T1b ZO-Q8 structured-parse migration** — S2904 substrate-arc-scope. Trigger: third template variant proposed OR lint scope expands beyond 2 heading hooks. Migrate `pa_tools_gap_map.py` from regex parsing to frontmatter parser + markdown AST.
- **NEW — S2905 metadata-pattern-selection lint** — substrate-arc-scope. Trigger: ≥3 sweep sessions mix TOOL_DEFAULTS + per-action `TOOL_ACTION_METADATA` without stated rule-based justification. Promote inline rule (currently comment in `core/services/tool_action_metadata.py`) to a lint that flags per-action records shadowing tool-defaults with the same safety class (redundant override).
- **NEW — S2905 Ledger candidate: `pilots_tool` undeclared `action=running`** — handler branch exists but schema enum omits it. Deferred; operator impact today zero (schema validation blocks reach). Remediation: drop handler branch OR extend schema enum.
- **NEW — S2905 Ledger candidate: `cost_telemetry_tool` silent `limit` cap at 50** — cross-tool consistency gap; same class as F-RT-2/F-RT-5. Deferred (batch-close observation).
- **NEW — S2905 Ledger candidate: `revenue_tracker_tool` `status='confirmed'` default drift** — handler default at line 1690 not in schema enum. Remediation: schema-conformant default OR extend enum. Deferred pending Rigby SIGN direction.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — deferred; trigger = operator/customer signals batched-lead triage ambiguity.
- **Applicability metadata pattern (entry #28)** — deferred; trigger = next integrity detector added.
- **Baseline lookback cap for HISTORICAL_BASELINE fields (entry #29)** — MITIGATED at PR #3423 (S2899). Substrate available; operator has not flipped default None yet.
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — deferred; trigger = embedding-pipeline lag becomes chronic (>3 sessions of persistent 100%-null embedding spikes).
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
- **S2900-S2904:** Row 161 substrate arc — CLOSED. T1c ✓ S2901 + T1a ✓ S2902-S2903 + T1b ✓ S2904.
- **Remainder:** Slice 1.5b (autopilot_tool mutations, ~1 session; staged enforcement per pre-commit note) + `ops_tool` sweep slot (promoted from partial at T1c) + Phase 0 heading fixes for 8 close_with_short_note tools.

**Slice 2 — `td_handlers_agents` (25 tools):**
- **S2905 batch 1: 4 tools ✓** (gates_tool, pilots_tool, cost_telemetry_tool, revenue_tracker_tool). First accelerated batch; substrate multiplier validated.
- **S2906+ batches 2-5:** 21 tools remaining. Target ~5-6 tools/batch at accelerated pace → ~4 more batches.

**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arc CLOSED (S2900-S2904):** T1c ✅ S2901 → T1a ✅ S2902+S2903 → T1b ✅ S2904. Total actual: **4 substrate sessions** vs ~4-5 initial estimate.

**Total remaining tools to close:** 72 (or ~100 counting partials + doc-unknowns). Post-substrate sweep pace observed: 4 tools in S2905 (batch 1). Extrapolated remaining ~14-18 sessions at accelerated pace.

---

## Autopilot Slice 1.5b pre-commit note

When `autopilot_tool` mutations are eventually swept (Slice 1.5b), the shape MUST be:

1. **Staged-enforcement session** — many mutations require paired lifecycle scaffolding: `experiment_create` + `_start` (paired), `outreach_generate` + `_approve` + `_reject` (needs synthetic draft rows or A4 throttle waiver), `close_pack_generate` + `_approve` (needs synthetic opportunity_id), `meeting_create` + `_brief` + `_recap` (creates real calendar substrate), `governance_kill_switch` + `_deactivate_switch` (paired), `release_freeze` + `_unfreeze` (paired), `run` (evaluates all policies against real state — may create real blocks/downgrades).
2. **Canary containment per-action:** some are inherently global (`run`, `governance_set_mode global`, `release_freeze`) — need paired revert protocol. Others operate on single rows — canary to synthetic test data.
3. **A4 warm-up hard-throttle** (S2846) governs outreach mutations — max 3-5 total intros even in the mutation session.
4. **`backfill_impacts` + `backfill_failure_reasons`** — data-substrate writes; need idempotency verification post-write.
5. **`security_containment_plan dry_run=false, confirm=true`** — S1228 PR-A gate; explicit both-flag dispatch required.

Do NOT try to sweep both categories in one session.

---

## Two-Claude concurrency safety envelope (still active from S2889)

Rulebook: `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`.

- Each terminal uses its own Rigby conversation pin — no state collision.
- Different repos, different branches — no git collision.
- **Watch:** character-os Docker postgres previously captured u-d-b's `:5433` via IPv6 wildcard (S2885). `USE_PGBOUNCER=0` still in force in both `.env` files. If character-os side runs `docker compose up`, verify port ownership before restarting u-d-b.
- Shared u-d-b PA endpoint (`http://localhost:8000`) — both Claudes may drive it; surface handles concurrent conversations.

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2905 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2905: zero A4 spend — pure sweep-batch execution.** A1 shipping spend was the S2905 batch 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2905)

See:
- **S2905 handoff (current):** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping (closed at S2904):** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + `T1a_auto_harness.md` + `T1b_family_doc_templates.md` + `T1c_low_signal_audit.md` + `T1b_ship_shape_s2904.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2905 per-tool validation docs (new this session):**
  - `docs/research/tools/validation/gates_tool_validation.md`
  - `docs/research/tools/validation/pilots_tool_validation.md`
  - `docs/research/tools/validation/cost_telemetry_tool_validation.md`
  - `docs/research/tools/validation/revenue_tracker_tool_validation.md`
- **S2899 handoff:** `docs/handoffs/SESSION_2899_EMBEDDING_BASELINE_LOOKBACK_CAP.md`
- **S2898 handoff:** `docs/handoffs/SESSION_2898_INTEGRITY_NULL_SPIKE_APPLICABILITY.md`
- **S2897 handoff:** `docs/handoffs/SESSION_2897_PROSPECTING_QUEUE_TITLE_FIX.md`
- **S2896 handoff:** `docs/handoffs/SESSION_2896_AUTOPILOT_HISTORY_WIPE_DIAGNOSTIC.md`
- **S2895 handoff:** `docs/handoffs/SESSION_2895_PA_TOOLS_SWEEP_SLICE_1_5A_AUTOPILOT_READ_ONLY.md`
- **S2894 handoff:** `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`
- **S2889 handoff:** `docs/handoffs/SESSION_2889_PLAYBOOK_V0_9_0_RATIFIED.md`
- **A4↔A1 ratification:** current `00-START-NEXT-SESSION.md` §A4 Constraints (this file, above)
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`
- **Pressure-test addendum:** `docs/research/platform/S2841_PRESSURE_TEST_ADDENDUM.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 26 non-substrate total)
- **S2905 workspace mirrors:** Rigby to author at S2906 open (both into Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) — content mirror + ratification envelope per `feedback_rigby_writes_workspace_deliverables`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace above).

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
