# Session 2795 — PA tools validation-coverage gap map

**Date:** 2026-07-15
**Session:** S2795
**Branch/PR:** `s2795-pa-tools-gap-map` → **PR #3203** (merged as `5ec09d625`)
**Predecessor:** [SESSION_2794_TENANT_BOUNDARY_HEALTH.md](SESSION_2794_TENANT_BOUNDARY_HEALTH.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** thirty-fifth post-PLAYBOOK-7.4.4 (sha=`5ec09d625e85`)

---

## §1 — Ship summary

Engineering-first session #9 in row. Not on the original S2795 candidate menu — surfaced by Chris mid-session: "Rigby has noted a few times that she doesn't have certain tools to call from the chat UI. I know at one point we had started you and Rigby testing/verifying all the tools she has and things like curl/HTTP tools she might need but I don't know if we ever actually finished it."

Investigated: the S2728→S2732 tool validation campaign shipped **57 defect patches, 270 regression tests, 4 shared primitives across 18 tools in 4 batches over 5 sessions**. But 18 of the platform's 114 schemas / 157 handlers / 113 pairs was only ~7% per-tool coverage. Ship: a right-sized "gap map" that surfaces the shopping list without pre-committing to another 5-session sweep. Chris D-verdict: "Yes".

Rigby's tool-grounded read (4 `repo_tool` search + read calls) surfaced substantial existing substrate: `build_pa_tool_audit` command + `docs/PA_TOOL_AUDIT.md` (84KB, stale from 2026-05-12) + `test_pa_tool_schema_drift.py` CI guard. Rigby SIGN-with-edits **upgraded ship shape from B (new command) to (c) extend `build_pa_tool_audit` behind optional flags** — preserves BC on the established artifact, delivers gap-map behind opt-in flags.

**Files changed (6):**

| File | Change | Purpose |
|------|--------|---------|
| `core/services/pa_tools_gap_map.py` | new (431 lines) | Pure-logic module: SUBSTRATE_DOC_STEMS + index_validation_docs + find_matching_doc_stem + classify_tool + lint_schema + build_triage_slices + build_gap_map + render_gap_map_markdown |
| `core/management/commands/build_pa_tool_audit.py` | +150 | Adds 4 optional flags: `--include-validation-xref`, `--emit-gap-json`, `--gap-only`, `--output PATH`. Default invocation unchanged (BC contract test locks the 5-column overview table stays 5-column) |
| `core/tests/test_pa_tools_gap_map_2795.py` | new (23 tests × 6 classes) | Locks 14 contracts: index-doc parsing, category classification, schema-quality lint, triage-slice grouping, command flag behavior |
| `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` | new | First emit of the gap map (fresh at close). 158 tool names, 105 untested, 8 doc_exists_unknown, 44 agent_via_run_agent, 1 meta |
| `docs/PA_TOOL_AUDIT.md` | regen | 2 months stale (101/166 → correct 114/157/113); refreshed at ship time |
| `tools/pa_local.sh` | +1 / -1 | Fresh pin (`pa-dd870b3158784a9d`) |

**Full 17-suite regression:** 318 tests OK (295 prior + 23 new, 4.1s).

**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **64 rows** (26 `same_pr_actionable` / 22 `same_pr_mitigatable` / 16 `future_trigger`). Rows 60/61/62/63/64 are S2795's own SIGN folds.

---

## §2 — Novel-precedent moments

**First mid-session Chris pivot to a candidate not on the S2795 open menu.** The S2795 candidate menu I wrote at S2794 close listed 10+ engineering candidates + "Something entirely new". Chris did NOT pick from that menu. Instead: "Before we move on I have a question that's not on the current map…". Ship happened outside the pre-planned S2795 open scope. Signal: candidate menus are useful priors, not gates.

**First tool-grounded discovery of pre-existing substrate that reshaped ship scope BEFORE code was written.** Rigby's read surfaced `build_pa_tool_audit` (existing) + `PA_TOOL_AUDIT.md` (existing) + `test_pa_tool_schema_drift.py` (existing CI guard). Without her read, I might have built a parallel `build_pa_tools_gap_map` command that duplicated 60% of the introspection logic. Direct payoff of `feedback_cycle_1a_verify_before_build`.

**First BC-preserving extension of a DOC-AUTOGEN artifact.** `docs/PA_TOOL_AUDIT.md` is DOC-AUTOGEN'd; downstream readers may consume its shape. Ship contract-tests locked: default `build_pa_tool_audit` invocation still emits the 5-column overview table (not 7-column). Additive columns only surface behind `--include-validation-xref`. Standalone gap map only surfaces behind `--gap-only`.

**First rendered "triage slices" section as an explicit anti-burn-down device.** F3 mitigation — the gap map artifact leads with "NOT a burn-down queue; triage slices below are decision aids, not commitments. Chris picks what to validate." Then emits 3-5 slices ranked by handler file with `est_sessions` calculated at 4/session pace (matching S2728→S2732 empirical cadence). The framing IS the mitigation.

**Continued Rigby SIGN response non-truncation.** S2790→S2795 all clean = sample size **6** post-Row 44 tightened-prompt pattern. Trend claim now strongly holds.

---

## §3 — T1 SIGN cycle detail

**Pin:** `pa-dd870b3158784a9d` (label `s2795-pa-tool-gap-map`), minted at S2795 T1 open via `session_lifecycle open`. Retired at close, force=true, twenty-sixth consecutive.

**Dispatch 1 — joint scoping (tool-grounded per `feedback_verify_rigby_tool_runs_before_trusting_sign`):**
Presented 4 candidates (A extend build_pa_tool_audit / B new build_pa_tools_gap_map / C fold into existing but BC-preserve) with my A lean + zoom-out ask + 5 verification claims for tool-grounded check.

**Response:** `tool_runs` = 6+ `repo_tool` search/read calls verifying `PA_TOOL_SCHEMAS` structure, `test_pa_tool_schema_drift.py` existing CI guard, `_tool_handlers` registry, `tool_dispatcher.py:560-680` register calls, `docs/research/tools/validation/` 18 files tree, and — most importantly — the existing `build_pa_tool_audit` command Rigby found unprompted. Not empty. Not rubber-stamp.

**Rigby verdict:** SIGN-with-edits upgrading recommendation from (A/B) to **(c) fold gap map into build_pa_tool_audit + preserve BC on defaults**. Reasoning: (a) blunt extend risks churn to downstream readers; (b) reading MD as input is stale + parse-fragile; (c) sources of truth (schemas + dispatcher) drive both default output and gap map from one entrypoint.

**5 folds classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8/9:**

| # | Ledger row | Class | Fold title | Disposition |
|---|-----------|-------|-----------|-------------|
| F1 | 60 | `same_pr_actionable` | Doc-exists ≠ validated surface — need `_full` / `_partial` / `_doc_exists_unknown` distinction via "Covered actions" heading parse | ✅ Adopted — 3-state categorization |
| F2 | 61 | `same_pr_mitigatable` | "validated_cross_cutting" too generous — substrate docs don't validate per-tool invariants | ✅ Adopted — renamed to `covered_substrate_only` (though currently unused as a category since honest signal is "untested" when no per-tool doc exists) |
| F3 | 62 | `same_pr_actionable` | Shopping-list coupling risk — big untested list creates burn-down pressure | ✅ Adopted — 3-5 triage slices grouped by handler file with "NOT a burn-down queue" framing + est_sessions |
| F4 | 63 | `future_trigger` | Complaints should be telemetry-backed (ToolCallRecord + error signatures), not memory-based | ⏸ Deferred (no complaints column this PR); trigger: tool_call_error_rate query surface exists |
| F5 | 64 | `same_pr_mitigatable` | Semantic drift worth flagging — schema quality lint | ✅ Adopted — 5 lint tags (missing/short desc, no props, no required, actions not mentioned) |

**Dispatch 2 — Chris D-verdict:** "Yes" — SHIP option (c) with all 4 mitigations inline.

**Dispatch 3 — post-merge dogfood:** Rigby invoked `repo_tool` to search for `GAP_MAP` in the codebase, then searched `gap` under `docs/audits/`, confirming `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` appears in the results. `tool_runs` non-empty. Local ORM verification also confirmed:
- 158 tool names / 105 untested / 44 agent_via_run_agent / 8 doc_exists_unknown / 1 meta_no_handler
- 23 tools flagged actions_not_mentioned_in_description; 14 no_required; 1 no_properties
- Top triage slices: td_handlers_agents (23) + td_handlers_core (22) — both ~6 sessions at 4/session

---

## §4 — Constitutional posture

- **Playbook v0.8.0 (205 rules)** — unchanged
- **PLAYBOOK-6.10.7** zoom-out ask: ✅ 1 explicit ask; drove all 5 folds
- **PLAYBOOK-6.10.8** fold classify+persist BEFORE D-verdict: ✅ rows 60/61/62/63/64 persisted before Chris "Yes"
- **PLAYBOOK-6.10.9** evidence admission: ✅ stable-state pointer `a2b3e484b` + file+line evidence for schema/handler/validation-doc claims + verified outcome inline (Rigby corrected my initial 114/157 vs stale-doc 101/166 via `build_pa_tool_audit --check` re-run)
- **PLAYBOOK-7.4.4** recycle-after-merge: ✅ `make recycle-all` completed post-merge (thirty-fifth cycle, sha=`5ec09d625e85`)
- **`feedback_engineering_bias_over_audit`**: ✅ net-new engineering candidate (engineering-first session #9 in row)
- **`feedback_cycle_1a_verify_before_build`**: ✅ pre-existing substrate found + ship reshaped to extend rather than duplicate
- **`feedback_verify_rigby_tool_runs_before_trusting_sign`**: ✅ 6+ tool_runs verified before trusting SIGN
- **`feedback_claude_rigby_agree_first_chris_yes_no`**: ✅ joint recommendation before Chris D-verdict
- **`feedback_zoom_out_ask_per_rigby_sign`**: ✅ 1 zoom-out ask; drove 5 folds

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2795 artifacts:**

- **Ship logic:** `core/services/pa_tools_gap_map.py` (431 lines, no Django imports at module scope)
- **Ship command:** `python manage.py build_pa_tool_audit --gap-only --output <path>` (or `--include-validation-xref` for the extended default audit)
- **Ship artifact:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`
- **Ship refresh:** `docs/PA_TOOL_AUDIT.md` (2 months stale — regenerated at close)
- **Ship tests:** `core/tests/test_pa_tools_gap_map_2795.py` (23 tests, 6 classes, 14 contracts locked)
- **Handoff:** `docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md` (this file)
- **PR:** [#3203](https://github.com/clwest/donkey-betz-platform/pull/3203) merged as `5ec09d625`
- **Predecessors:** S2733 (tool validation campaign retrospective), S2732 (campaign close), S2794 (tenant boundary health)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No Workspace tab this ship** — deliberately CLI + markdown-only per S2795 T1 explicit non-scope
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **64 rows** (26/22/16)
  - `logs/recycle_events.jsonl` — +1 event (post-#3203, sha=`5ec09d625e85`)
  - `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` — freshly written

---

## §6 — Open items / follow-ups

- **F4 (telemetry-backed complaints) future_trigger** — fires when a `tool_call_error_rate` query surface exists (ToolCallRecord model already exists). Would enable a "recently-failing tools" column in the gap map that's grounded in data, not memory.
- **The 8 existing per-tool validation docs need "Covered actions" checklists** — currently all 8 land in `validated_doc_exists_unknown`. If we add explicit action checklists, the gap map upgrades them to `validated_full` (or `_partial` for tools that grew actions after the doc was written).
- **Triage slices ready for Chris to pick** — top 5 in the artifact today (td_handlers_agents 23 · td_handlers_core 22 · td_handlers_content 12 · td_handlers_gateway 11 · td_handlers_ops 8). Each ~2-6 sessions at 4/session pace.
- **Schema quality lints as pre-shopping-list** — 23 tools with actions_not_mentioned_in_description are the cheapest fixes (edit schema description text). Advisory column suggests those. 1 tool with no_properties is the closest to broken.
- **First autonomous Rigby invocation of `build_pa_tool_audit`** — S2795 dogfood was prompted. First unprompted invocation is next trigger.
- **First trigger for factoring gap-map service out** — currently `core/services/pa_tools_gap_map.py`. If a second consumer needs it (e.g., a Workspace tab surfaces the gap map, or a Slack alerter), factor-out abstraction test fires.
- **Model drift arc** — 38+ auto-migrations queued (unchanged this session; no model changes).
- **`SESSION_819_SYSTEM_AUDIT_*` cleanup** — 17 untracked files from webhook cron (grew from 15 during S2795).
- **Encoding-future-triggers-as-tests pattern — third instance still standing** (S2791/S2792/S2793). S2795 F4 was future_trigger but not encoded-as-test (deferred with no locked contract); pattern streak neither extends nor breaks.

---

## §7 — Repo state at close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `5ec09d625` (S2795 ship #3203) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Substrate: gap-map surface built. Direct RUR-C1 parent-close blocker unchanged (I-0303 still not opened). |
| Session pin | `pa-dd870b3158784a9d` (retired at S2795 close, force=true, twenty-sixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-dd870b3158784a9d` (retired; forces fresh mint at S2796 open) |
| Live infra state | S2755→S2794 substrate + S2795 PA tools gap map |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2795 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3203, sha=`5ec09d625e85`) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **64 rows** (26/22/16) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — regenerated at close (158/114/157/113) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` — first emit (105 untested / 8 doc_exists_unknown / 44 agents / 1 meta) |
