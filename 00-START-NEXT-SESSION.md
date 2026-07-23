# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2904 CLOSE → Row 161 substrate arc CLOSED (T1c ✓ S2901 + T1a ✓ S2902-S2903 + T1b ✓ S2904). Sweep resumes at accelerated pace at S2905. S2905 opens with Phase 0 heading fixes (recommended) OR Slice 1.5b autopilot mutations OR Slice 2 `td_handlers_agents` (25-tool sweep, first accelerated batch) — **D6 MORATORIUM STILL IN FORCE**

**Refreshed 2026-07-22 (S2904 close).** T1b family-doc template + ratchet-and-warn lint shipped in a single session. PR #3433 merged at `101c25aad` — canonical template file at `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` with sweep (default) + protocol variant skeletons; `core/services/pa_tools_gap_map.py` extended with `_`-prefix filter (Rigby SIGN D-1) + loosened `COVERED_ACTIONS_HEADING_RE` regex accepting optional numbering (Rigby SIGN D-2, prevents regex-as-policy trap) + new `evaluate_template_compliance()` presence-not-exact function with alias-tolerant frontmatter; 15 new tests (39/39 pass) covering both variants + false-positive rejection + `_TEMPLATE_` exclusion + legacy-still-warns end-to-end. Regenerated `PA_TOOLS_GAP_MAP.md` — all 161 rows show `warn` (advisory legacy); zero `fail`. Lint gate live for next sweep session doc-author to opt into via `Template version: v1`. Rigby wrote twin workspace mirror (content mirror `adf67e67-76ab-4df0-8ebc-71f43a11fe8b` + ratification envelope `dace0795-6518-4a53-8313-ae42a7f0ab51`, both in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) + 3 forward-carry ledger rows (ZO-Q2/Q7/Q8).

**T1b live results:**
- 161 per-tool rows in the gap map now carry a `template_compliance` field: 161 `warn`, 0 `pass`, 0 `fail`
- `warn` is advisory (legacy without `Template version:` marker); does NOT block
- Loosened regex accepts: `## Covered actions` / `## 2. Covered actions` / `## 2) Covered actions` / `## 2 — Covered actions`. Rejects: `## Actions covered` (false positive).
- Presence-not-exact frontmatter — protocol docs may keep their variant-specific keys (`Main handler`, `Downstream service`, `Session validated`, `Reviewer`, etc.). Alias-tolerant.

**Rigby joint SIGN (S2904):** T1 SIGN routed with 10 tool_runs. AGREE-with-edits on A/B/C/E/F; REVISE (blocking) on D-1 (`_`-prefix filter) + D-2 (regex loosening). All same-PR mitigations folded into v2 ship-shape doc BEFORE merge. Also caught real §1 corpus-count error (my initial 22→17 sweep claim; correct 19 per-tool `*_tool_validation.md` = 14 sweep + 5 protocol). Zero rubber-stamp SIGN in this cycle.

**PRs shipped this session:**
- u-d-b PR [#3433](https://github.com/clwest/donkey-betz-platform/pull/3433) — S2904 T1b template + ratchet lint, merged at `101c25aad`
- u-d-b PR `<TBD>` — S2904 close cascade (handoff + 00-START refresh + wrapper pin bump)

**Ledger status:** **Row 161 CLOSED (mitigated 2026-07-22 S2904 arc close).** T1c ✓ S2901; T1a Phase 1 ✓ S2902; T1a Phase 2 ✓ S2903; T1b ✓ S2904. Row A `mitigated` (PR #3419 S2897). Row B `mitigated` (PR #3421 S2898). Row C `mitigated` (PR #3417 S2896). Row #29 `mitigated` (PR #3423 S2899). Deferred rows 27/28/30 unchanged. New forward-carry rows added: ZO-Q2 (warn-noise escalation ladder) + ZO-Q7 (automated corpus-counter helper) + ZO-Q8 (structured-parse migration trigger).

**Zoom-out folds captured (per PLAYBOOK-6.10.7):**
- Fold — regex-as-policy footgun caught by Rigby SIGN D-2 → `same_pr_mitigated`. Original `COVERED_ACTIONS_HEADING_RE` only matched bare `## Covered actions`; T1b's initial ship-shape entrenched this by requiring "bare" — Rigby correctly reframed as "template extraction should not codify an incidental regex limitation as policy." Loosened regex + `## Actions covered` false-positive test both same-PR.
- Fold — §1 corpus-count drift caught by Rigby tool-grounded verification → `future_trigger` ZO-Q7 (automated corpus counter). My initial count was 22→17 sweep; ground truth is 19→14 sweep. Rigby ran the grep herself instead of accepting my count; the whole SIGN cycle's discussion of "why two variants" was resting on drifted numbers. Same-PR corrected + logged as forward-carry to prevent recurrence.

Full session context: `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`.

---

## S2905 open sequence

### Step 1 (RECOMMENDED FIRST ACTION) — Slice 2 first batch (`td_handlers_agents` sweep, accelerated pace)

**S2905 recommended open: Slice 2 batch 1 (`td_handlers_agents`, 4-5 tools).** With Row 161 substrate arc closed, the T1a auto-harness + T1b template + gap-map lint are all live substrate. First accelerated sweep batch should use the new template opt-in (`Template version: v1`) so the ratchet-and-warn lint transitions from theoretical to observed.

**Concrete work:**
- Pick 4-5 read-only tools from `td_handlers_agents.py` per `PA_TOOLS_GAP_MAP.md` triage slice (25 untested there, largest slice).
- Author validation docs using the T1b canonical template (opt into `Template variant: sweep` + `Template version: v1`).
- Verify `pa_tool_validate_harness` output pre-populates §Covered actions + §4 Golden-path from the T1a metadata (opt into T1a substrate).
- Regenerate `PA_TOOLS_GAP_MAP.md`; expect first `pass` verdicts to appear.

**Session cap:** 1 session for batch of 4-5 (pre-substrate pace) → target 1 session for batch of 8-10 (post-substrate accelerated pace).

### Alternative Step 1 candidate — Phase 0 heading fixes

Still defensible if Chris judges parity gate should be clean before accelerated sweeps. The 8 close_with_short_note tools (agent_introspection_tool / autopilot_tool / deliverable_tool / kb_tool / ops_tool / repo_tool / search_docs / session_tool) all need `## Covered actions` heading additions to their validation docs. Doc-only PR; would clear all 8 parity mismatches. Note: T1b loosened the regex, so numbered `## 2. Covered actions` form is now also accepted for these fixes.

### Alternative Step 1 candidate — Slice 1.5b autopilot mutations

Now unblocked (T1a WRITE_GATED classifier stable). Single-tool batch (`autopilot_tool` mutations) with paired-lifecycle staged enforcement per the S2905 "Autopilot Slice 1.5b pre-commit note" (§ below, unchanged).

**Recommend Slice 2 first** — the substrate arc close signals sweep acceleration; the first accelerated batch validates the multiplier claim. Phase 0 heading fixes + Slice 1.5b can bundle into subsequent S2905+ sessions.

### What's forbidden at S2905 (D6 MORATORIUM still in force)

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
- **Sweep-arc pace sustainability substrate arc** — ledger row 161. **CLOSED (mitigated) 2026-07-22 S2904 arc close. All 3 threads shipped: T1c ✓ S2901 PR #3427 → T1a Phase 1 ✓ S2902 PR #3429 → T1a Phase 2 ✓ S2903 PR #3431 → T1b ✓ S2904 PR #3433. Total substrate-arc actual: ~4 sessions vs ~4-5 initial estimate. Expected sweep acceleration ~50 sessions → ~10-15 sessions for remaining ~76 tools — first accelerated batch is S2905's validation opportunity.**
- **Response-level introspection field creep** — ledger row 162 (S2896). Same-PR mitigated; watch for pattern in other tools' response contracts.
- **Harness timestamp churn** — S2903 fold, `future_trigger`. Trigger to act: harness becomes CI-invoked OR a PR needs to isolate content-change signal.
- **T1a FT-1 defaulted-tool action-set change lint** — S2903 substrate-arc-scope. Trigger: pre-commit or CI shape becomes concrete.
- **T1a FT-2 harness `soft_error` outcome value** — S2903 substrate-arc-scope. Trigger: v1 → v2 schema bump signed off.
- **NEW — T1b ZO-Q2 warn-noise escalation ladder** — S2904 substrate-arc-scope. Trigger: 5+ sweep sessions where `template_compliance` warn count is NOT monotonically decreasing → any TOUCHED legacy doc must upgrade to `Template version: v1` in same PR. Do NOT escalate untouched legacy.
- **NEW — T1b ZO-Q7 automated corpus-counter helper** — S2904 substrate-arc-scope. Trigger: any §1 corpus-survey section claiming numeric distribution over `docs/research/tools/validation/` — write a tiny helper (script or mgmt command) that prints (i) total *_tool_validation.md count / (ii) sweep-vs-protocol split by Template variant / (iii) missing-frontmatter counts / (iv) top-N offenders. Then require future §1 surveys to source from output.
- **NEW — T1b ZO-Q8 structured-parse migration** — S2904 substrate-arc-scope. Trigger: third template variant proposed OR lint scope expands beyond 2 heading hooks. Migrate `pa_tools_gap_map.py` from regex parsing to frontmatter parser + markdown AST.
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

**Slice 2 — `td_handlers_agents` (25 tools):** UNBLOCKED at S2905 open. Substrate ready — first batch validates the multiplier claim.
**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2 batch pattern.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arc CLOSED (S2900-S2904):** T1c ✅ S2901 → T1a ✅ S2902+S2903 → T1b ✅ S2904. Total actual: **4 substrate sessions** vs ~4-5 initial estimate.

**Total remaining tools to close:** 76 (or ~104 counting partials + doc-unknowns). Post-substrate sweep pace target: **~10-15 sessions**.

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

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2904 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2904: zero A4 spend — pure substrate arc thread 3/3 execution (T1b).** A1 shipping spend was the T1b PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2904)

See:
- **S2904 handoff (current):** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2900 substrate arc scoping (closed at S2904):** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md` (parent) + `T1a_auto_harness.md` + `T1b_family_doc_templates.md` + `T1c_low_signal_audit.md` + `T1b_ship_shape_s2904.md` (S2904 ship-shape)
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
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
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 22 non-substrate total)
- **T1b workspace mirrors (S2904 close):** content mirror `adf67e67-76ab-4df0-8ebc-71f43a11fe8b` + ratification envelope `dace0795-6518-4a53-8313-ae42a7f0ab51` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace above) — updated at S2904 close with 3 new forward-carry rows ZO-Q2/Q7/Q8.

For older session history (S1-S2847), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
