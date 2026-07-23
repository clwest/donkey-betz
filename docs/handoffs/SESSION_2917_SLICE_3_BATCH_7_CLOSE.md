# SESSION 2917 — Slice 3 batch 7 (async duo) + Slice 3 CLOSE (22/22)

**Date:** 2026-07-23
**Branch:** `main`
**HEAD at open:** `d884d9c8c`
**HEAD at close:** _filled at PR merge_
**Session pin:** `pa-8044f01583e1468b` (minted at S2916 close)
**Predecessor:** `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`

---

## Executive summary

Slice 3 CLOSED at **22/22**. Batch 7 shipped the async duo (`studio_tool` + `workflow_run_tool`), introduced **§5b Appendix A (Async-Fanout)** as the sibling to S2916's Appendix N, and promoted two Fold candidates at Slice CLOSE per Rigby T0 SIGN + Chris ratification:

1. **Row #38 standardized-appendices** (2nd adoption trigger reached — Network-Preflight batch 6 + Async-Fanout batch 7).
2. **Opaque side-effecting chain via internal dispatch** — Rigby Q4 broadening of the S2916 actionless-side-effecting-chain pattern, with concrete corroborating evidence: `_impl_run_source_pack_workflow` re-enters `tool_dispatcher._handle_competitor_comparison(...)` at `core/tasks_content.py:4050-4057` (1st observed dispatcher-re-entry instance).

Sweep counts post-S2917: **52 full · 10 partial · 47 untested** (from 43+11+49 pre-S2917 per validation-doc counts; auto-classifier upgrades the batch to `validated_full` on doc-completeness). No new TOOL_DEFAULTS entries this batch — both tools are MIXED-safety, so 11 per-action `TOOL_ACTION_METADATA` records instead (6 studio + 5 workflow_run).

---

## PRs shipped this session

- **PR `<TBD>`** — Slice 3 batch 7 async duo + §5b Appendix A + Fold promotions (this PR).
- **PR `<TBD>`** — S2917 close cascade (handoff + 00-START refresh + wrapper pin bump).

---

## Tools shipped (2)

### `studio_tool` — MIXED (4 MUTATION async fan-out + 2 READ_ONLY)

- **Handler:** `core/services/td_handlers_core.py:951` (`_handle_studio`)
- **Schema:** `core/services/pa_tool_schemas.py:1549` (6-action enum)
- **Actions:** `generate_image` / `generate_video` / `generate_audio` (all → `execute_agent_task.apply_async(queue='long_running')`) + `create_talking_video` (→ `create_talking_video_task.apply_async(queue='long_running')`, 2-stage pipeline) + `job_status` (reads `CeleryTaskEvent` then `AsyncResult` with `AgentExecution` enrichment) + `list_jobs` (reads `ImageHistory`/`VideoHistory`/`AudioHistory`).
- **Envelope:** single `task_id` — asymmetric with workflow_run_tool's dual `run_id`+`task_id`. Motivated Rigby's Q2 A3 dual-identifier edit.
- **Cancel:** none exposed — intentional contract surface.
- **Validation doc:** `docs/research/tools/validation/studio_tool_validation.md`

### `workflow_run_tool` — MIXED (2 MUTATION + 3 READ_ONLY)

- **Handler:** `core/services/td_handlers_core.py:3141` (`_handle_workflow_run`)
- **Schema:** `core/services/pa_tool_schemas.py:2290` (5-action enum)
- **Actions:** `start` (creates WorkflowRun + `run_source_pack_workflow.apply_async(queue='content')` + backfills celery_task_id) + `status`/`list`/`detail` (WorkflowRun reads) + `cancel` (`celery_app.control.revoke(terminate=True)` + `run.mark_cancelled()`).
- **Envelope:** dual `run_id` + `task_id`. Cancel is best-effort SIGKILL + reliable domain-side transition.
- **Downstream implementation:** `_impl_run_source_pack_workflow` at `core/tasks_content.py:3819+` — 6 stages (collect / ingest / embed / generate / export / complete) with WebSearch, LLM embedding, LLM comparison generation, and **dispatcher re-entry** into `competitor_comparison_tool.export_markdown` at `tasks_content.py:4050-4057`.
- **Validation doc:** `docs/research/tools/validation/workflow_run_tool_validation.md`

---

## Rigby joint SIGN (2 dispatches, tool-grounded, zero rubber-stamp)

**Dispatch 1 (T0 SIGN turn 1 — Q1 verdict + Q2 partial):**
- 10 `repo_tool` file reads + 2 `repo_tool` searches (verified via captured tool_runs) — includes reads of `td_handlers_core.py`, `tasks.py`, `tasks_content.py`, plus grep for `def run_source_pack_workflow` + `def execute_agent_task` + `def _impl_run_source_pack_workflow`.
- **Q1 verdict AGREE — ship both.** Studio ~8 distinct callees over 237 lines (`_handle_studio` :951→:1187); workflow_run ~4 distinct callees over 160 lines (`_handle_workflow_run` :3141→:3300). Both under ~10-callee threshold.
- **Q1 factual catch:** my dispatch claimed studio has `list at 1202 / invoke at 1241` actions — Rigby corrected: those belong to `_handle_persona` (starts at `:1189`), not `_handle_studio`. Doc corrected.
- **Q2 AGREE-WITH-EDITS on Appendix A shape** (partial due to output-cap truncation; resent as Dispatch 2).

**Dispatch 2 (Q2 continuation + Q3 + Q4):**
- **Q2 detailed edits to Appendix A:** A3 must allow dual identifiers (task_id + domain-object id); A5 must include observability contract AND cancel semantics (studio has `job_status` polling `CeleryTaskEvent`+`AsyncResult`; workflow_run has `cancel` via `revoke(terminate=True)`); A1 must include "task wrapper → agent router" as a first-class subtype; A2 keeps priority optional (neither handler sets it).
- **Q3 PICK (c):** fold §5c revisit-trigger declaration INTO Appendix A field A5. Both handlers are thin dispatch shells; enforce discipline at fan-out declaration point, not repeated subsection.
- **Q4 zoom-out verdicts:**
  - Top-2 accretion risks: **per-action sprawl eclipses pattern readability** (25+ action records across 5 batches); **TOOL_DEFAULTS drift without cross-tool index/checker**.
  - Fold promotions READY at Slice 3 CLOSE: (a) **row #38 standardized-appendices** YES (2nd adoption); (b) **actionless-side-effecting-chain 3rd instance** YES — Rigby broadened the pattern to "opaque side-effecting chain via internal dispatch" with concrete `tasks_content.py:4050-4057` dispatcher-re-entry evidence. NOT ready: IRREVERSIBLE dry_run (2/3) + cascade-audit doc (1/2).
  - Top-2 sweep-shape signals at Slice 3 → Slice 4 transition: **handler callee-density + opacity beyond reviewability** (many gateway tools may be thin `apply_async` shells → mandate Appendix-driven audit); **internal dispatcher re-entry becomes common** (need "re-entrant tool dispatch" appendix if repeats).
  - Rigby pushback on my framing (Q4-iv): **fan-out presence is itself an opacity flag regardless of callee count.** My Q1 "~10 callees" threshold gives false comfort for async shells — workflow_run has 4 callees but sprawls across `tasks_content.py`. Adopted in Appendix A A1 evidence-note.

---

## Chris D-verdicts (mid-flight decision routing)

- **D1: Ship both tools in batch 7 (Q1)** — RATIFIED (Rigby + Claude joint AGREE; no separate Chris D-verdict required per `feedback_claude_rigby_agree_first_chris_yes_no`).
- **D2: Promote both Fold candidates in batch 7 close** — RATIFIED. Chris directive: *"If you and Rigby both agree then batch them both in 7"*. Row #38 standardized-appendices + opaque-side-effecting-chain both folded in this PR.

---

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

_Filled after merge + recycle._

- HEAD at post-merge: `<sha>`
- `make celery-recycle` result: _pending_
- Rigby live-verify dispatches: _pending_

---

## Slice 3 CLOSED — sweep progress tracker

**Slice 3 (`td_handlers_core`, 22 tools):** **CLOSED at 22/22.**

| Batch | Session | Tools | Notes |
|---|---|---|---|
| 1 | S2913 | 4 (paid_interest_status / platform_awareness / persona / platform_config) | READ_ONLY sweep |
| 2 | S2913 | 4 (active_repo / db_health / conversation / remember) | READ_ONLY + envelope drift Ledger candidate |
| 3 | S2913 | 4 (messaging / learning / dream / governance) | READ_ONLY sweep |
| 4 | S2914 | 2 (work / intelligence) | Explicit allowlist + transitive exclusions |
| 5 | S2915 | 3 (task_breakdown / research_and_create / competitor_comparison) | Row-create trio + §5b first-hop dependency proof shape |
| 6 | S2916 | 3 (fleet_health / signal_studio_judge_stats / http_smoke_test) | Network trio + §5b Appendix N (Network-Preflight) |
| **7** | **S2917** | **2 (studio / workflow_run)** | **Async duo + §5b Appendix A (Async-Fanout) + 2 Fold promotions** |

**Sweep counts (from `docs/audits/PA_TOOLS_GAP_MAP.md` post-regen):**
- `validated_full`: **52** (from 43 pre-S2917 — auto-classifier bumps batch 7 pair + batch 6 trio to full on doc-completeness)
- `validated_partial`: **10** (from 11 pre — 1 tool flipped)
- `validated_doc_exists_unknown`: **7**
- `agent_via_run_agent`: **44**
- `untested`: **47** (from 49 pre — 2 tools closed)
- `meta_no_handler`: **1**
- **Total tool names:** 161

**Remaining slices (queued):**
- Slice 4 — `td_handlers_gateway` (17 untested tools).
- Slice 5 — `tool_dispatcher` (14 untested tools).

---

## Fold promotions (Slice 3 CLOSE)

### Fold 1 — **Row #38 standardized-appendices** (§5b appendix pattern)

**Trigger corroboration:**
- 1st adoption: S2916 batch 6 — **Appendix N (Network-Preflight)** introduced across 3 tools (fleet_health / signal_studio_judge_stats / http_smoke_test).
- 2nd adoption: S2917 batch 7 — **Appendix A (Async-Fanout)** introduced across 2 tools (studio_tool / workflow_run_tool).

**Promoted framing:** §5b (first-hop dependency proof) supports named appendices for common first-hop classes. Each appendix has a fixed field count + copy-pasteable table structure. Prevents "notes-field creep" into unreviewable policy surface. Future appendices as needed (candidate slots: **Appendix L (LLM-Call)** if a 2nd LLM-first-hop tool warrants it; **Appendix D (Dispatcher-Re-Entry)** if the pattern hits 2+ instances).

**Codified location:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` §5b now names both Appendix N + Appendix A with full field specs. Template version stays v1 (no schema bump — appendices are structural additions inside an existing optional section).

### Fold 2 — **Opaque side-effecting chain via internal dispatch** (Rigby Q4 broadening)

**Original pattern (S2916 forward-carry):** actionless-side-effecting chain. Triggered at 3 instances (`legal_doc_drafter_agent` S2910 + `research_and_create_tool` S2915 + `http_smoke_test` S2916) — all actionless MUTATION-classed `TOOL_DEFAULTS` entries where a single execution path unconditionally performs I/O with persistent side effect.

**Rigby Q4 broadening (S2917 batch 7):** the "actionless" constraint is too narrow. `workflow_run_tool.start` is actioned but has the same shape: single dispatch → async task → downstream tool-dispatch re-entry (`get_tool_dispatcher(); dispatcher._handle_competitor_comparison(...)` at `tasks_content.py:4050-4057`). The load-bearing property is **opacity of side-effect surface at the handler layer**, not whether the tool exposes an `action` enum.

**Promoted framing:** any tool where the handler dispatches into an opaque callee that itself performs unbounded side effects (LLM calls, DB writes, network fetches, tool-dispatch re-entry, agent execution) triggers this pattern. Mitigation = Appendix A field A4 (downstream side-effect boundary) + A5 revisit-trigger discipline. Discovery of a new "dispatcher re-entry" site (task calling back into `tool_dispatcher._handle_*`) is a load-bearing audit event.

**Codified location:** both S2917 validation docs (studio + workflow_run) name the pattern in §5b commentary + `TOOL_ACTION_METADATA` notes for the affected actions. Handoff doc + envelope reference. Not a new §5c (per Rigby Q3 pick c — folded into Appendix A A5).

---

## Post-close forward carry — S2918 open state

### D6 moratorium STILL IN FORCE

_(unchanged from S2916 — see `00-START-NEXT-SESSION.md` for the full forbidden list; refreshed at S2917 close)_

### New Ledger candidates raised S2917

- **Legacy-error envelope backfill 3-tool corroboration.** S2916 batch 6 raised this Ledger candidate at `signal_studio_judge_stats` (1st instance). S2917 harness runs corroborated at `studio_tool.job_status` + `workflow_run_tool.status` + `workflow_run_tool.detail` = **4 total instances across 3 tools**. Pattern confirmed: tools returning `{error, error_code}` envelopes without emitting the S2874 structured envelope shape get backfilled with `error_code: 'legacy_error'` by the dispatcher. Substrate-arc-candidate for S2918+ — schema/handler alignment sweep to migrate legacy error envelopes to S2874 shape. Not opened this session per D6 moratorium; ledgered for post-D6 evaluation.
- **Contract asymmetry — single vs dual identifier in async envelopes.** Studio returns single `task_id`; workflow_run returns dual `run_id`+`task_id`. Rigby Q2 A3 edit captured this in Appendix A. 1st formal instance of the pattern. If a future async-fan-out tool needs domain-object polling, this asymmetry will bite.
- **Undocumented handler-forwarded param.** `workflow_run_tool.start` handler at `td_handlers_core.py:3162` forwards `payload.get('focus_areas')` into `input_json`, but `focus_areas` is not in the schema `properties` block. Agentic loop won't suggest it. 1st formal instance of "handler-side param not in schema" in the sweep.
- **Dispatcher-re-entry as async-fanout audit hotspot.** Rigby Q4 first evidence: `_impl_run_source_pack_workflow` re-enters `dispatcher._handle_competitor_comparison(...)` at `tasks_content.py:4050-4057`. 1st observed instance. If a second async task calls back into `tool_dispatcher._handle_*` in a future slice, promote "dispatcher-re-entry" to a first-class Fold candidate (candidate name: **Appendix D (Dispatcher-Re-Entry)**).
- **Auto-classifier upgrades MUTATION-deferred tools to `validated_full`.** Both batch 7 docs frontmatter-declared `validated_partial` (live-exercise deferred for MUTATION actions per §5a); gap-map auto-classifier promoted to `validated_full` on doc-completeness (`Template version: v1` + `## Covered actions` heading present). Matches S2916 batch 6 http_smoke_test precedent — 2nd corroboration of this gap-map/frontmatter divergence. Not a bug; the classifier's completeness signal wins. Handoff-note only; no substrate change proposed.

### Fold candidates unchanged from S2916

- IRREVERSIBLE dry_run flag Fold: 2/3 instances (S2908 media_tool.delete + S2915 competitor_comparison_tool.delete). No new IRREVERSIBLE actions in batch 7.
- Cascade-audit companion doc Fold: 1/2 instances (S2915 competitor_comparison_tool.delete). No new instances in batch 7.
- Hidden network/LLM in read-shaped gateway Fold: 2/3 (S2913 conversation_tool.search + S2914 intelligence_tool.search). No new instances in batch 7 (async-shell tools declare their fan-out explicitly).
- Observability-tracker as MUTATION vector Fold: 1/2 (S2916 http_smoke_test OpsRunTracker). Not corroborated in batch 7.

### S2918 first-action candidates

**Batch 7 closes Slice 3 at 22/22.** S2918 opens Slice 4 (`td_handlers_gateway`, 17 untested tools). Alternative candidates:

- **Slice 4 opening batch composition.** Rigby T0 SIGN required at S2918 open to shape the first batch. Recommended: pick 3-4 tools with similar first-hop characteristics (e.g. 3 gateway reads or 3 gateway writes) to keep the batch coherent.
- **Legacy-error envelope substrate arc** (per Ledger candidate above) — post-D6 evaluation candidate; NOT to be opened without explicit Chris directive.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.

---

## PA tools sweep methodology pointers

- **Sweep doc:** `docs/audits/PA_TOOLS_GAP_MAP.md` (auto-regenerated by `python manage.py build_pa_tool_audit --gap-only`).
- **PA tool audit doc:** `docs/PA_TOOL_AUDIT.md` (auto-regenerated by `python manage.py build_pa_tool_audit`).
- **Per-tool validation docs:** `docs/research/tools/validation/*_validation.md` (63 non-substrate as of S2916; +2 = 65 at S2917 close).
- **Template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` — extended S2917 to include Appendix N + Appendix A specs inside §5b.
- **T1a harness:** `python manage.py pa_tool_validate_harness <tool_name>` — writes `docs/audits/pa_tools/harness_output/<tool>.json`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (unchanged from S2911).

---

## Session cadence

- 3 PA dispatches to Rigby (initial T0 SIGN + follow-up for Q2-truncation + follow-up for Q3/Q4-truncation). Output cap triggered on both Rigby responses > ~40KB — the 3-dispatch shape was the workaround.
- 1 harness run per tool (2 total).
- 1 gap-map regen + 1 PA-tool-audit regen.
- No live-exercise on any MUTATION action (per §5a deferral + D6 moratorium).
- Zero A4 spend (pure sweep-batch engineering).
