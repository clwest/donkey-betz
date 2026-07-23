# Session 2895 — PA Tools Sweep (Path B) Slice 1.5a: `autopilot_tool` read-only

**Date:** 2026-07-22
**PR:** [#3415](https://github.com/clwest/donkey-betz-platform/pull/3415) merged into main at commit `7891ee9c3`
**Ratchet:** `untested` 95 → 94 (-1); `validated_partial` 2 → 3 (+1: `autopilot_tool`); `validated_full` 12 → 12 (unchanged); `per_tool_docs` 21 → 22; `per_tool_docs_with_covered_actions` 13 → 14.
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred. Adopts new **2-tier evidence template** per Rigby S2895 T1 SIGN Q5 zoom-out — reference shape for future large-surface tool sweeps.
**D6 moratorium status:** IN FORCE (no strategic discovery arcs opened this session).

## What shipped

**PR #3415 — S2895 PA tools sweep Slice 1.5a: `autopilot_tool` read-only.** New `docs/research/tools/validation/autopilot_tool_validation.md` (399 lines / 47 KB) covering 76 read-only actions exercised live across 5 Rigby-executed batches (A–E). All ~29 mutation actions documented in §5a and explicitly deferred to Slice 1.5b (staged-enforcement session).

The tool has 99 enum actions total; this ship covered all read-only ones (`_report`, `_queue`, `_inbox`, `_scan`, `_forecast`, `_status`, `_health`, `_audit`, `_snapshot`, `_summary`, `_rates`, `_gaps`, `_plan`, plus `status`, `history`, `config`, `dry_run_report`, `drift_scan`, `latest_overrides_snapshot`, `security_containment_plan` at its `dry_run=true` default per S1228 PR-A gate).

## Rigby SIGN cycle summary

**T1 SIGN (4 tool_runs):** `governor_tool.status`, `search_docs`, `autopilot_tool.dry_run_report`, `autopilot_tool.history` with `include_evidence=true` + 6-path `selected_fields`. Verdicts:
- Ship-shape `validated_partial` + doc-only + 2-tier template plan: **AGREE**.
- Read-only catalog: **AGREE with 2 nits absorbed inline** (`config` = read-only as called; `security_containment_plan` = conditionally read-only, mutation variant deferred).
- Canary = Donkey Betz workspace: **AGREE** (reads safe fleet-wide + DBZ richest substrate for Ledger Row A discriminator).
- Ledger Row A discriminator plan: **AGREE with add + caution**.
- Q5 ZOOM-OUT: **DISAGREE with dumping everything inline; AGREE with exercising everything but compressing evidence aggressively.** Proposed 2-tier template (Tier 1 compact Evidence Ledger table + group-by-family narrative in main doc; Tier 2 raw JSON appendix for discriminators/bugs/sole-exemplars only). This became the reference template for the doc.

**T2 SIGN (5 tool_runs):** `search_docs`, `repo_tool.read_file` × 2 (Rigby actually read the shipped 399-line doc via her tool surface), `autopilot_tool.history` × 2 (live projection retest with 8-path then 4-path selections). Verdicts:
- §6.2 family narrative + §6.1 Evidence Ledger accuracy: **AGREE (no wrong rows spotted)**.
- Ledger Row A framing (bucket (e) as primary hypothesis): **DISAGREE — lean bucket (a) more strongly**. Rigby observed `result.reason: operator_cap_change_hysteresis` explicitly on the downgrade_set/cleared pairs, cleanly explaining the $3.07/$2.98 oscillations as normal hysteresis during operator cap changes, not enforcer-side PA-bypass. Applied inline before ship — §7.1 revised.
- §5 empty-state notes: **DISAGREE — one add.** Rigby observed at T2 that longer `selected_fields` lists (8 paths incl `result.enforcement_tier`) got silently echoed as `[]` while a 4-path retry echoed correctly. Concrete operator footgun; added to §3 and §5 and swapped in as Ledger row #3.
- Fold classification for 2-tier template (`same_pr_mitigatable`): **AGREE**.
- Q4 ZOOM-OUT (sustainability at current pace): **substantive** — proposed 3 methodology shifts (family-level substrate audits + auto-harness + tool-deletion audit); classified as **`future_trigger`** (row 161 in the ledger), decision queued to S2896 open.

## Rigby Tool Gap Ledger candidates surfaced (routed to deliverable `5c84e75a-…`)

1. **`prospecting_queue` empty titles.** All 6 leads returned by `autopilot_tool action=prospecting_queue` had empty `title` fields (financial-spider sources: sec_edgar, finnhub, polygon_finance, etherscan, yahoo_finance, financial). Score 45 flat. Blocks operator triage.
2. **`integrity_null_spike_scan` false-positive noise.** 96 critical spikes at `null_rate=1.0` for `processed_data` + `embedding_text` fields across ~20 spider families — likely "not-populated-by-design" fields being flagged. Needs applicability-rule or allowlist.
3. **`autopilot_tool.history selected_fields` silent longer-list wipe.** Rigby T2 live observation — 8-path list echoed as `[]`, 4-path retry worked. Wipe location upstream of handler's per-item silent-ignore.

**Deprioritized (per T2 correction):** DBZ enforcement bucket (e) probe — replaced by doc-clarity item (annotate `enforcement_report` output to include hysteresis-oscillation shape).

## Zoom-out folds persisted to `logs/zoom_out_classifications.jsonl`

- **Row 160 (`same_pr_mitigatable`) — 2-tier evidence template for large-surface tool sweeps.** Mitigation shipped in-doc. Promotion trigger: 1-2 more large-surface (>30 action) sweeps adopt cleanly → promote to first-class sweep-methodology section or Playbook §7 amendment.
- **Row 161 (`future_trigger`) — sweep-arc pace not sustainable at current shape.** Math: ~400-line docs × 76 remaining tools × ~1-2 tools per session = ~50 sessions of validation before Slice 5 closes. Rigby proposed 3 methodology shifts (family-level substrate audits + shared templates + auto-harness + tool-deletion audit). Classified as `future_trigger` because changes exceed any single-PR scope. Decision point at S2896 open OR after Slice 1 fully closes (~4-5 more sessions), whichever comes first.

## Substrate observations captured in the validation doc

- **Backlog governor L1 (Generation throttled) active since 2026-06-24** (~28 days). Trigger condition may no longer apply; watch.
- **`SystemIntelligenceAgent` 57% failure rate** (4/7 executions in 7d) — flagged CRITICAL by `value_usage_gaps`.
- **`knowledge_staleness_report`: intelligence + opportunity data types ~940h stale** (39 days). Paused upstream producer worth investigating.
- **`capacity_bottleneck`: process_pa_chat_task avg 48.15s** across 127 calls; `rigby_documentation_manager_daily` +726 MB memory delta per run.
- **`revenue_pipeline_report` vs `revenue_full_pipeline` scope mismatch** (definitional, not bug): pipeline_report scopes to contactable Opportunity rows; full_pipeline aggregates cross-substrate.
- **`growth_funnel engage_rate_pct` can exceed 100%** by design (events-per-candidate, not unique-engaged-rate).
- **`drift_scan` 10 warnings** — 2 schema/handler mismatches (`db_health_tool`, `mission_verdict`) + 8 agent-registry orphans (case-sensitivity `Rigby` vs `rigby` among them).

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):**
- Batch 1 (S2892): agent_control_tool, agent_memory_tool, heartbeat_history_tool, infra_health_tool ✓
- Batch 2 (S2893): governor_tool, ops_digest_tool, scheduled_tasks_tool, spider_status_tool ✓
- Batch 3 (S2894): workspace_budget_tool ✓ (single-tool batch)
- **Batch 4 = Slice 1.5a (S2895, this session): autopilot_tool read-only ✓** (single-tool batch, `validated_partial`)
- **Remainder:** `agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool` (doc/unknown/partial → full) + Slice 1.5b autopilot_tool mutations

**Estimated remaining after this session:** ~4-5 sessions to fully close Slice 1 (Slice 1.5b autopilot mutations + 4 doc/unknown/partial ops tools). Then Slice 2 opens (or the substrate-arc decision fires per Row 161).

## Files touched

- `docs/research/tools/validation/autopilot_tool_validation.md` — new (399 lines / 47 KB)
- `docs/audits/PA_TOOLS_GAP_MAP.md` — regenerated
- `logs/zoom_out_classifications.jsonl` — appended 2 rows (160, 161); now 161 total (local-only, gitignored)

## What's next — S2896 open sequence

Per Chris's engineering-bias-over-audit rule + Ledger Row A close + Row 161 zoom-out landing:

1. **FIRST DECISION POINT — Row 161 substrate-arc gate.** Before running another sweep batch, decide: (a) open a dedicated substrate arc (auto-harness build + family-doc template extraction + low-signal tool audit) BEFORE more sweeps, (b) push through 3-4 more current-shape batches to close Slice 1 then re-evaluate, (c) skip ahead to a Ledger-row-fix engineering session first. Rigby lean = (a); Chris ratifies.
2. **If continue sweeps:** Slice 1.5b (`autopilot_tool` mutations sweep — 29 actions, needs staged-enforcement session with paired lifecycle scaffolding for `experiment_create`+`_start`, `outreach_generate`+`_approve`, `close_pack_generate`+`_approve`, `meeting_create`+`_brief`+`_recap`, plus canary/revert for `governance_*`, `release_*`, `run`).
3. **If Ledger-row-fix engineering:** highest-priority ship candidates from S2895 Ledger — `autopilot_tool.history selected_fields` batch-wipe fix (small; concrete operator footgun) OR `prospecting_queue` empty-titles investigation.
4. **Deferred (D6 moratorium still in force):** No strategic discovery arcs. No R1a-shaped proposals. Docs restructuring arc, W2 #1/#2b/#2c, LLMCallLog field splits, bulk workspace_budget operations, C4/C5/C6 character-os follow-ons all remain queued.

## For fuller sweep context

See:
- **S2895 handoff (this doc)**
- **S2894 handoff:** `docs/handoffs/SESSION_2894_PA_TOOLS_SWEEP_SLICE_1_BATCH_3.md`
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated)
- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` (local-only; rows 160+161 appended this session)
- **A4 warm-up constraints:** current `00-START-NEXT-SESSION.md` §A4 (S2894 close text, still in force at S2895 close).
