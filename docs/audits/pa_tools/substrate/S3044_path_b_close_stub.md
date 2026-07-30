# Path B Systematic Sweep — CLOSE Artifact

**Status:** CLOSED at S3044 Batch 3 (2026-07-30). Path B systematic sweep DONE.
**Arc:** Path B PA tools systematic sweep (opened S2892, ratified S2900 substrate arc, resumed + closed S3044).
**Close scope:** All 18 non-agent_via_run_agent gap-map entries flipped to `validated_full` across S3044 Batches 1-3. 45 `agent_via_run_agent` tools remain out-of-scope per S2900 Fold Q1 defer + 1 `meta_no_handler` (`run_agent`) by design.

---

## Acceptance criteria (all checkbox states final)

- [x] **Batch 1 shipped (S3044, PR #3788, commit `17dd03f56`):** 8 tools flipped → `validated_full` (`agent_capability_drift_tool`, `agent_job_status`, `bpaas_tool`, `brainstorm_tool`, `davinci_tool`, `media_tool`, `obs_tool`, `workspace_tool`). Wrong-stem-match rescue #1 (`workspace_tool`).
- [x] **Batch 2 shipped (S3044, PR #3789, commit `bcc4b0694`):** 5 tools flipped → `validated_full` (`agent_introspection_tool`, `autopilot_tool`, `kb_tool`, `ops_tool`, `search_docs`). Wrong-stem-match rescue #2 (`kb_tool`). Substrate ledger row appended (Rigby Tool Gap Ledger, +2347 chars).
- [x] **Batch 3 shipped (S3044, PR #_TBD, commit _TBD_):** 5 tools flipped → `validated_full` (`claude_code_tool`, `intelligence_tool`, `repo_tool`, `session_tool`, `work_tool`). Additional NEXT_HEADING_RE parser-cut discovery for intelligence + work docs (fixed by converting `###` subheadings to bold labels).
- [x] **Post-Batch-3 gap map verified:** `validated_full=118`, `untested=0`, `validated_doc_exists_unknown=0`, `validated_partial=0`, `agent_via_run_agent=45`, `meta_no_handler=1`. Total = 118+45+1 = 164 ✓
- [x] **Ledger review:** Rigby Tool Gap Ledger reviewed at Batch 2; wrong-stem-match row appended. No new ledger candidates from Batch 3.
- [x] **This artifact finalized:** stub content replaced with retrospective below.

## Cumulative gap map delta (Batches 1+2+3)

| Category | S3043 close | S3044 close | Delta |
|---|---|---|---|
| `validated_full` | 100 | **118** | **+18** |
| `validated_partial` | 10 | **0** | −10 |
| `validated_doc_exists_unknown` | 6 | **0** | −6 |
| `untested` | 2 | **0** | −2 |
| `agent_via_run_agent` | 45 | 45 | 0 (deferred) |
| `meta_no_handler` | 1 | 1 | 0 (by design) |
| **Total** | 164 | 164 | 0 |

## Retrospective — Path B Systematic Sweep (S2892 → S3044)

### What the sweep found

The sweep started at S2892 with ~100 untested + ~16 partial tools out of ~117 total (per opening deliverable). Over ~50 sessions (~S2892 → S3044), the pattern-recognition surfaced:

- **Handler-file-batched sweeps** were the productive shape (per S2900 substrate arc): sweep by handler file (Slice 1 = `td_handlers_ops.py`, Slice 2 = `td_handlers_agents.py`, etc.) rather than by tool family.
- **Doc-only ship shape (S2796)** held for 18/18 in this final push — the sweep never required code changes to flip categorization. Runtime handler behavior stayed untouched; only validation-doc coverage was authored/extended.
- **Two distinct wrong-stem-match false-positives** surfaced in S3044 (`workspace_tool`, `kb_tool`) — a stem-matcher heuristic issue in `pa_tools_gap_map.find_matching_doc_stem` strategy-3 loose containment. Now documented as a Rigby Tool Gap Ledger row with 3 mitigation options for future decision.
- **A parser-cut bug in `NEXT_HEADING_RE`** was discovered in Batch 3 — the classifier's section extraction terminates at the first `###` subheading, so docs organized with `### READ_ONLY` / `### MUTATION` subsections were undercounted. Fixed cleanly by converting subheadings to bold labels; no runtime change needed.
- **The 45 `agent_via_run_agent` bucket** stayed out-of-scope throughout, per S2900 T1c Fold Q1 defer. Class-shape is fundamentally different (agent dispatch via `_handle_agent_tool` with per-agent-class resolution) and needs a separate arc scoping.
- **PLAYBOOK-7.7.5 class-scoped A2 sweeps** were exercised twice in the final push (Batch 1 for coverage-closure shape, Batch 2 for wrong-stem-match class). Both cycles produced substantive tool_runs + zero rubber-stamp — the rule held.

### What shipped

- **3 PRs in S3044** — PR #3788 (Batch 1, 8 tools), PR #3789 (Batch 2, 5 tools), PR #_TBD (Batch 3, 5 tools + this CLOSE artifact).
- **18 tools flipped** to `validated_full` in one session (S3044).
- **2 wrong-stem-match rescues** shipped via dedicated exact-match validation docs.
- **1 Rigby Tool Gap Ledger row appended** (Batch 2 promotion) documenting the wrong-stem-match pattern.
- **1 parser-cut bug documented** (Batch 3 `###`-terminates-section discovery) — reused fix pattern across intelligence + work docs.

### What was deferred

- **`agent_via_run_agent` bucket (45 tools):** deferred at S2900 T1c Fold Q1. Requires separate arc scoping — the class shape (agent-dispatch via `_handle_agent_tool` with per-agent-class resolution) is fundamentally different from action-multiplexed tools.
- **Mutation coverage batches:** many partial docs deferred their mutation actions to a future Slice 2 write batch (e.g., autopilot has 23 mutations documented but explicitly out-of-scope; workspace_tool has 6 mutations deferred). Requires paired lifecycle scaffolding + `dry_run` affordance work.
- **Bridge-live batches:** davinci / obs / media bridge-dependent mutations require a bridge-reachable environment to promote from `skipped_bridge_unreachable` → `validated_full` per-action.
- **Stem-matcher fix (Option B lint or Option C refinement):** deferred to a future substrate row upgrade if a 3rd trigger surfaces. Currently mitigated by the dedicated-doc-per-tool convention (S3044 Batches 1+2 precedent).
- **`NEXT_HEADING_RE` parser refinement:** currently mitigated by the bold-labels convention. If future docs regress to `###` subheadings, fix at author time or upgrade the regex to accept `####`+ but not `###`+ (arbitrary depth cutoff).

### What surprised us

- **Sweep-pace acceleration was real.** S2900 substrate arc predicted ~10-15 sessions to close 76 remaining tools; S3044 discharged the final 18 in ONE session. The pace multiplier came from (a) doc-only shape stability, (b) T1b template maturity, (c) per-file batching, (d) auto-harness evidence being reusable across doc edits.
- **Stale opening frame.** S3044 opened with memory + 00-START framing "Slice 6 = td_handlers_content.py, 6 untested tools." Live gap map proved that stale — content-file was 100% validated_full. Verify-before-build (29th consecutive session) caught this before authoring the wrong slice.
- **Two consecutive stem-matcher false-positives.** Not one — TWO tools were misclassified via the same heuristic bug (`workspace_tool`, `kb_tool`). Both discovered mid-sweep; both mitigated same-batch; ledger row promoted at 2nd trigger per Rigby Q5 recommendation.
- **NEXT_HEADING_RE cut behavior surfaced only at Batch 3.** No prior sweep batch exercised docs with `###` subsections in `## Covered actions`. Intelligence + work docs used them and the classifier undercount was invisible until my Python diff-tool caught it.
- **All 3 batches completed in single session (S3044).** Chris's direction "let's finish PA tools" translated to a 3-batch sprint that took ~3-4 hours end-to-end — well within a single-session cadence.

### What we'd do differently

- **Regenerate the auto-classifier report at session-open**, not at session-close. S3044 opened against a stale memory framing that would have been caught immediately by re-running `build_pa_tool_audit --gap-only --check` first. Consider adding this to the session-open ritual for any tools-adjacent work.
- **Author docs with the classifier's parser shape in mind.** `NEXT_HEADING_RE` matches `#+` — using `###` subsections inside `## Covered actions` silently undercounts. Prefer bold labels for organizational structure within the section.
- **Route sweep dispatches through Rigby by default.** Batch 1 verifications were short-circuited by Claude via repo tool grep (for speed); Batch 2+3 partially routed through Rigby. Chris directive `feedback_loop_rigby_in_when_short_circuiting` (S3044) codifies this: Claude should send an FYI when short-circuiting Rigby-offered work. Applied post-hoc in Batch 1; applied natively in Batch 2+3.
- **Pre-authored CLOSE stubs.** Rigby's Q5 zoom-out at Batch 1 T0 SIGN suggested pre-authoring the Path B CLOSE artifact stub in Batch 1 rather than scrambling at Batch 3. Adopted, and it worked — this artifact was skeleton-first, filled last, minimal-scramble.

## Post-close forward-carry (open work + ledger candidates)

- **Mutation coverage batches (future).** ~50+ mutation actions across 6+ tools defer to future write-shaped batches with dry_run scaffolding. Not blocked; open when Chris wants mutation coverage.
- **Bridge-live batches (future).** davinci / obs / media bridge-dependent mutations. Not blocked; open when a bridge-reachable environment is stood up.
- **`agent_via_run_agent` bucket audit (future arc).** 45 tools — separate class shape, separate arc scoping needed.
- **Stem-matcher upgrade (advisory, warn-only lint = Option B).** In Rigby Tool Gap Ledger (`[S3044] PA tools gap-map find_matching_doc_stem strategy-3 loose-containment false-positive`). Open if 3rd trigger surfaces.
- **`NEXT_HEADING_RE` parser refinement (advisory).** Doc discipline (bold labels within Covered actions) is current mitigation. Regex upgrade optional.

## Related

- **Arc scoping:** `S2900_substrate_arc_scoping.md`.
- **Substrate cleanup arc:** `S2909_substrate_cleanup_arc_scoping.md`.
- **Prior slice CLOSE:** `slice_5_close_artifact.md` (S2928).
- **S3044 batch plan:** `S3044_path_b_finish_plan.md`.
- **Chris D-verdicts (S3044):** "Ship it" x3 (Batch 1 open, Batch 2 continuation, Batch 3 close-out) — 2026-07-30.
- **Rigby Tool Gap Ledger substrate row:** `[S3044] PA tools gap-map find_matching_doc_stem strategy-3 loose-containment false-positive` (workspace `b4503364-2573-4401-9e28-61a739e0ce50`, deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`).
- **Rigby SIGN cycles (S3044):** A1 (Batch 1 plan-shape) + T0×3 (Batch 1, Batch 2, Batch 3) — 4 substantive cycles, all AGREE, all tool_runs-grounded, zero rubber-stamp. PLAYBOOK-7.7.2 + PLAYBOOK-7.7.5 invariants held.
