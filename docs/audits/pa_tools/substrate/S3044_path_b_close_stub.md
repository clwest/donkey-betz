# Path B Systematic Sweep — CLOSE Artifact (STUB)

**Status:** STUB — pre-authored at S3044 Batch 1 per Rigby Q5 zoom-out suggestion. Finalized at S3046 Batch 3 close.
**Arc:** Path B PA tools systematic sweep (opened S2892, ratified S2900 substrate arc, resumed S3044).
**Close scope:** All 18 non-agent_via_run_agent gap-map entries flipped to `validated_full`. 45 `agent_via_run_agent` tools remain out-of-scope per S2900 Fold Q1.

---

## Acceptance criteria (finalize checklist at Batch 3 close)

- [x] **Batch 1 shipped (S3044):** 8 tools flipped → `validated_full` (`agent_capability_drift_tool`, `agent_job_status`, `bpaas_tool`, `brainstorm_tool`, `davinci_tool`, `media_tool`, `obs_tool`, `workspace_tool`).
- [ ] **Batch 2 shipped (S3045):** 5 tools flipped → `validated_full` (`agent_introspection_tool`, `autopilot_tool`, `kb_tool`, `ops_tool`, `search_docs`).
- [ ] **Batch 3 shipped (S3046):** 5 tools flipped → `validated_full` (`intelligence_tool`, `session_tool`, `work_tool`, `claude_code_tool`, `repo_tool`).
- [ ] **Post-Batch-3 gap map verified:** `validated_full=118`, `untested=0`, `validated_doc_exists_unknown=0`, `validated_partial=0`, `agent_via_run_agent=45`, `meta_no_handler=1`.
- [ ] **Ledger review:** Rigby Tool Gap Ledger reviewed for any new-since-S3040 entries requiring flip.
- [ ] **This artifact finalized:** stub content replaced with retrospective (what was found, what shipped, what deferred, what's next).

## Post-close forward-carry (candidates — verify at Batch 3 finalize)

- **Mutation coverage batches (Slice 2 write):** the 5 batch-1 partial docs + workspace_tool defer their mutation actions to a future write-shaped batch. Requires paired lifecycle scaffolding + dry_run affordance work (currently `unsafe_no_dry_run` for workspace_tool; unknown for others).
- **Bridge-live batches:** davinci/obs/media bridge-dependent mutations require a bridge-reachable environment to promote from `skipped_bridge_unreachable` → `validated_full` per-action.
- **`agent_via_run_agent` bucket (45 tools):** deferred at S2900 T1c Fold Q1. Requires separate arc scoping — the class shape (agent-dispatch via `_handle_agent_tool` with per-agent-class resolution) is fundamentally different from action-multiplexed tools.
- **Stem-matching heuristic false-positive prevention:** S3044 discovered `workspace_tool` falsely-classified as `validated_partial` via loose containment match to a workspace-family doc. If a 2nd false-positive surfaces in another workstream, promote to a substrate row with a lint proposal.
- **Handler-file coupling documentation:** `td_handlers_agents.py` hosts 30+ tools. Consider a shared-module cross-reference index for operators editing the file.

## Retrospective (fill at Batch 3 finalize)

Fill each section with concrete evidence + counts at Batch 3 close. Below are placeholder headings.

### What the sweep found
_(numbers + patterns discovered across S2892 → S3046)_

### What shipped
_(per-batch PR/commit list + tool counts)_

### What was deferred
_(mutation-shaped work, bridge-live work, agent_via_run_agent bucket)_

### What surprised us
_(sweep-pace vs estimates, tool-shape variance, drift discoveries)_

### What we'd do differently
_(retro on Row 161 substrate arc + T1a/T1b/T1c ordering + shape-break batches)_

## Related

- **Arc scoping:** `S2900_substrate_arc_scoping.md`.
- **Substrate cleanup arc:** `S2909_substrate_cleanup_arc_scoping.md`.
- **Prior slice CLOSE:** `slice_5_close_artifact.md` (S2928).
- **S3044 batch plan:** `S3044_path_b_finish_plan.md`.
- **Chris D-verdict on Option B:** "Ship it" — 2026-07-30 S3044.
