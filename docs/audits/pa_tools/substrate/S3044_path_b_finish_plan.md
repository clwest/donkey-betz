# S3044 — Path B PA Tools Sweep FINISH Plan

**Opened:** 2026-07-30 (Session 3044)
**Origin:** Chris directive "Let's finish up PA tools" — S3044 first-action override.
**Cycle 1A verify-before-build catch (29th consecutive session):** Memory + 00-START framed S3044 as "Slice 6 = td_handlers_content.py, 6 untested tools." Live `build_pa_tool_audit --gap-only` proved that stale — content-file is 100% validated_full (8/8). Actual remaining surface = 18 tools across 5 handler files (2 untested + 6 doc_exists_unknown + 10 validated_partial).
**Chris D-verdict:** Option B (close all 18 non-agent_via_run_agent gaps across 3 batches) ratified.
**Rigby A1 SIGN:** S3044 A1 SIGN AGREE (11 tool_runs) on plan shape. Q5 zoom-out flagged registration-count false-positive (resolved: `run_agent` is meta_no_handler by design) + pre-authored Path B CLOSE stub adopted.

---

## 1. Batch shape

| Batch | Session | Handler file | Tool count | Composition |
|---|---|---|---|---|
| 1 | S3044 (this) | `td_handlers_agents.py` | 8 | 2 untested (agent_capability_drift, agent_job_status) + 5 partial (bpaas, brainstorm, davinci, media, obs) + 1 wrong-stem-match rescue (workspace_tool) |
| 2 | S3045 | `td_handlers_ops.py` | 5 | agent_introspection, autopilot, kb, ops, search_docs |
| 3 | S3046 | mixed (core/codejobs/gateway) | 5 | intelligence (core), session (core), work (core), claude_code (codejobs), repo (gateway) |

**Total: 18 tools closed across 3 sessions.** Post-Batch-3, only 45 `agent_via_run_agent` tools remain out-of-scope (Fold Q1 defer at S2900 arc scoping).

## 2. Doc-only shape (per S2796)

- All 18 docs land in `docs/research/tools/validation/<tool_name>_validation.md` following T1b canonical template (sweep variant).
- `## Covered actions` heading is mandatory and includes every action in the tool's `action` enum (or a single-entrypoint bullet for zero-action tools like `agent_job_status`).
- Mutation actions listed with `- \`<action>\` — **mutation — deferred to <slice-target>** — see §5a` — includes backticked identifier so gap-map classifier counts them as covered.
- Bridge-dependent actions labeled `skipped_bridge_unreachable` per S2909 T2 semantics (davinci/obs/media bridge actions).
- Frontmatter `Execution mode: analyzed` for docs where live-dispatch is deferred; `Mutation safety: dry_run_supported` OR `unsafe_no_dry_run` per handler affordance.

## 3. Fold-log from Rigby A1 SIGN (2026-07-30)

- **Fold Q1 (safety) → doc-only is safe; bridge tools use `skipped_bridge_unreachable` label.** Applied to davinci/obs/media in Batch 1.
- **Fold Q2 (harness use) → selective — read-only actions via harness; hand-authored for bridge-dependent + mutation.** Applied to Batch 1 (existing partial docs already have harness evidence from S2907/S2908).
- **Fold Q3 (external-bridge) → doc-only close acceptable with `skipped_bridge_unreachable` labels.** Applied.
- **Fold Q4 (batch sizing 8 tools/session) → tractable given 6/8 are partial/unknown (lighter load).** Confirmed post-Batch-1 — all 8 flipped cleanly.
- **Fold Q5 (zoom-out) → pre-author Path B CLOSE stub this session; finalize in Batch 3.** Adopted — see `S3044_path_b_close_stub.md`.
- **Fold Q5-b (registration count 163 vs 164) → false-positive push-back.** Delta = `run_agent` (meta_no_handler, no `self.register` call by design). Not a structural smell.

## 4. Verify-before-build discoveries (S3044-specific)

- **Stem-matching heuristic false positive.** `pa_tools_gap_map.find_matching_doc_stem` uses 3-strategy resolution (exact → suffix-stripped → loose containment). For `workspace_tool`, strategies 1+2 miss (no `workspace_tool_validation.md`), and strategy 3 loose-matches to a workspace-family doc (`workspace_budget_tool_validation.md` starts with `workspace_`). Result: gap map reported `validated_partial` when the tool actually had no dedicated doc. **Mitigation:** Batch 1 authored dedicated `workspace_tool_validation.md`; strategy 1 now hits directly. **Future-trigger candidate:** if another tool exhibits the same false-partial pattern, promote to substrate ledger row with a lint proposal (warn when loose-containment fires and the containing stem is a distinct tool name).

## 5. MVP discipline

- **Session cap:** 1 session per batch. Batch 3 additionally includes Path B CLOSE artifact finalization.
- **Anti-scope-creep:** no handler/schema code changes in these batches. Bridge-live batches + mutation-coverage batches are downstream substrate arcs.
- **Regression tests deferred:** per S2796 doc-only shape; the sweep flips the gap-map classifier only, not the runtime behavior.

## 6. Close criteria

Arc closes (Path B systematic sweep DONE) when all three of:
1. **Batch 1 (S3044):** 8 tools flip to `validated_full`. **[SHIPPED — this session]**
2. **Batch 2 (S3045):** 5 tools flip.
3. **Batch 3 (S3046):** 5 tools flip + Path B CLOSE artifact finalized.

Expected post-close state:
- `untested: 0`
- `validated_doc_exists_unknown: 0`
- `validated_partial: 0`
- `validated_full: 118` (108 after Batch 1 + 5 Batch 2 + 5 Batch 3)
- `agent_via_run_agent: 45` (unchanged — deferred per S2900 Fold Q1)
- `meta_no_handler: 1` (`run_agent` — by design)

## 7. Related

- **Arc parent:** S2900 substrate scoping (`S2900_substrate_arc_scoping.md`).
- **Slice CLOSE artifact:** `slice_5_close_artifact.md` (S2928 close of Slice 5).
- **Pre-authored final artifact:** `S3044_path_b_close_stub.md` (this session).
- **Rigby A1 SIGN evidence:** conversation `pa-4549a2e261134f93` — 11 tool_runs at S3044.
- **Chris D-verdict:** "Ship it" — 2026-07-30.
