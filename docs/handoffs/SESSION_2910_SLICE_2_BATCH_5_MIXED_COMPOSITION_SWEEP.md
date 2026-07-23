# Session 2910 — Slice 2 Batch 5 (Mixed-Composition Sweep)

**Status:** PR [#3446](https://github.com/clwest/donkey-betz-platform/pull/3446) merged at `e84d69343`. Post-merge live-dispatch verified via Rigby per PLAYBOOK-7.4.4.
**Date:** 2026-07-23
**Active conversation:** `pa-d17b6dea0eb84424` (S2910 pin — retired at close).
**Prior session:** [`SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`](./SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md).
**Next session entry point:** S2911 — see `00-START-NEXT-SESSION.md`.

## TL;DR

Fourth accelerated PA-tools sweep batch in Slice 2 after S2909 substrate cleanup arc closed the harness classifier + bridge preflight gaps. **First mixed-composition batch:** one 7-action mixed READ_ONLY+MUTATION tool (`brainstorm_tool` via per-action records) alongside three actionless tools (`web_fetch_tool` READ_ONLY, `schedule_followup` WRITE_GATED, `legal_doc_drafter_agent` MUTATION) via `TOOL_DEFAULTS`.

Batch composition + shape ratified by Rigby T0 SIGN AGREE-with-edits. Q4 zoom-out flagged heterogeneous risk surfaces bundled into one batch + `schedule_followup` PA-context coupling; this ship honored the ask with a targeted PA-context invariant regression test.

**One PR shipped ([#3446](https://github.com/clwest/donkey-betz-platform/pull/3446)) at `e84d69343`.** Merge → recycle-all → live-dispatch verified 4/4 tools. Rigby T1 SIGN caught real doc-pointer drift (schedule_followup doc pointed at a nonexistent test file path); fixed pre-commit.

## Tools swept

| Tool | Actions | Shape | Notes |
|---|---|---|---|
| `brainstorm_tool` | 6 R covered + 1 M excluded | Per-action (Pattern C — session_tool / revenue_tracker_tool / bpaas_tool precedent) | 3 R success (`list` / `recent` / `stats`) + 3 R `error_captured` on required-arg misses (`search` / `details` / `by_category`) + 1 skipped_mutation (`create`) |
| `web_fetch_tool` | actionless | `TOOL_DEFAULTS` READ_ONLY | Rigby Tool Gap Ledger #15 (S2865); httpx GET/POST bounded (scheme allowlist + method allowlist + timeout+max_bytes caps) |
| `schedule_followup` | actionless | `TOOL_DEFAULTS` WRITE_GATED conditional | PA-context invariant load-bearing; new regression test class added this ship |
| `legal_doc_drafter_agent` | actionless | `TOOL_DEFAULTS` MUTATION conditional | Disclaimer gate at `dispatch_legal_draft` (S2803 Phase 3.0 shared helper) |

## Shape decisions

- **Metadata seed:** MIXED patterns coexist correctly in this batch. `brainstorm_tool` uses per-action `TOOL_ACTION_METADATA` (Pattern C) because the `create` action's MUTATION class deviates from the 6 READ_ONLY siblings. The 3 actionless tools use `TOOL_DEFAULTS` (Pattern A) — no schema `action` enum to override, so safety class is doc-primary + drives gap-map/audit surfaces. Same precedent as `web_search` (S2906 batch 2).
- **Validation-doc `## Covered actions` heading:** for `brainstorm_tool`, list only the 6 READ_ONLY actions (in scope this ship). `create` goes in `§5a Mutation containment` per S2908 precedent — this is what drives the classifier to `validated_partial` correctly. Initially I inline-mentioned `` `create` `` in the `## Covered actions` intro paragraph, which the classifier picked up via the backtick-ident regex; had to strip the backtick reference from that section to get `validated_partial` classification. Documented as a subtle-doc-shape rule for future authors.
- **Sweep shape:** Slice 2 batch 5 is the second mixed-composition batch (after S2908 batch 4). S2907 close Fold A committed to breaking the uniform-only pattern; S2908 broke it once (mixed-tool-scoped-to-READ_ONLY-subset); S2910 breaks it again with a different shape (mixed-tool-composition-across-batch: one multi-action + three actionless). No new pattern-selection lint counter increment — both patterns are used correctly for the tools they apply to.

## Ship shape

- **Docs:** `docs/research/tools/validation/{brainstorm_tool,web_fetch_tool,schedule_followup,legal_doc_drafter_agent}_validation.md` (T1b template variant=sweep, version=v1).
- **Metadata seed:** `core/services/tool_action_metadata.py` — 3 new `TOOL_DEFAULTS` + 7 new `brainstorm_tool` per-action records. Header comment blocks document the mixed-shape decision.
- **Regression test:** `core/tests/test_schedule_followup_response_shape.py` — new `ScheduleFollowupPAContextInvariantTests` class (3 tests) alongside existing 8-test class:
  - `test_missing_context_pins_pa_context_error_marker` — pins `'requires a PA conversation context'` substring.
  - `test_nested_context_conversation_id_is_promoted` — verifies `payload['context']['conversation_id']` promotion path works.
  - `test_root_and_nested_forms_are_equivalent` — idempotency cross-check (both forms resolve to the same subscription row via unique constraint).
  - All 11 tests in file pass.
- **Auto-gen refresh:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` regenerated (117 tool schemas · 160 handlers · 116 wired both sides).
- **Gap map delta:** `td_handlers_agents` untested 10 → 6 (-4). Corpus-wide: untested 79 → 75 (-4); `validated_partial` 7 → 8 (+1 brainstorm_tool); `validated_full` 27 → 26 (net -1 because brainstorm went partial not full).

## Rigby joint SIGN cycles (2 substantive rounds, zero rubber-stamp)

### T0 SIGN — batch composition + shape (before code)

- **Q1 batch composition:** Rigby proposed 4 tools (brainstorm_tool + web_fetch_tool + schedule_followup + legal_doc_drafter_agent) after in-file verification of handler locations (used `repo_tool.read` at multiple ranges + `_handle_` prefix grep). Rejected the other 6 remaining Slice 2 tools without in-file grounding.
- **Q2 shape recommendation:** Mixed-safety scoped-to-READ_ONLY-subset (S2908 pattern) — READ_ONLY subset ships enabled, write-ish actions (brainstorm.create dispatch + schedule_followup subscribe + legal_doc_drafter dispatch) ship as explicit opt-in.
- **Q3 bridge dependencies:** None — no `external_bridge` metadata needed. web_fetch is HTTP (not bridge); brainstorm.create is Celery; schedule_followup is DB+PA context.
- **Q4 zoom-out AGREE-with-edits:** Flagged 3 concerns — (a) heterogeneous risk surfaces bundled in one batch (raw HTTP + DB subscription + Celery dispatch + agent registry), (b) `schedule_followup` context coupling requires PA context promotion invariant, (c) no red flags on pace itself IF batches stay coherent by side-effect class + explicit gating.
- **Chris D-verdict:** Approved 4-tool proposal as-is, with the ask to honor Rigby's Q4 concern by adding a targeted context-invariant test for `schedule_followup`.

### T1 SIGN — post-implementation (substantive verification)

- **Q1 metadata seed shape:** PASS. All classifications match handler behavior. Note: `create` correctly MUTATION not IRREVERSIBLE (reversible Celery dispatch, not destructive). Nit: metadata note for `create` wording tightened to "requires: topic OR query (non-empty)" per Rigby's suggestion.
- **Q2 validation doc spot-check (schedule_followup):** MOSTLY PASS but caught real drift — my doc `§Related` cited a test file at `core/tests/test_schedule_followup_pa_context.py` that doesn't exist; actual location is the new class in `core/tests/test_schedule_followup_response_shape.py`. Fixed pre-commit. Handler cross-check clean on all line-referenced claims (6425-6428 OR-fallback; 6430-6433 fail-loud string; 6448-6472 execution resolution; 6474-6503 non-PA + cross-conversation rejections; 6357-6387 11-key contract).
- **Q3 PA-context invariant test coverage:** PASS at handler-side but flagged a coverage limit — a refactor of the entrypoint-side injection at `unified_pa_entrypoint.py:2262-2264` (`arguments.setdefault('conversation_id', self.conversation_id)`) would NOT be caught by these handler-only tests. Documented in the validation doc as a follow-up candidate.
- **Q4 zoom-out AGREE:** No new generalized concerns beyond T0 SIGN Q4. One concrete data point: doc-pointer drift caught in-batch this session is itself evidence of pace-masking-2nd-order-issues pattern. Not a new arc trigger yet; watch for 2nd instance.

## Post-merge live-dispatch verification (per PLAYBOOK-7.4.4)

`make celery-recycle` at `e84d69343` → `bash tools/pa_local.sh` for 4 verifications:

- `brainstorm_tool  action=stats` → `{action: 'stats', period_days: 30, total_brainstorming: 0, total_discussions: 0, total_panels: 0, daily_breakdown: [], top_keywords: []}` — matches doc §6.1 shape exactly ✓
- `web_fetch_tool  url=https://httpbin.org/status/200  method=GET  timeout_seconds=10` → `{ok: true, status_code: 200, final_url, content_type: 'text/html; charset=utf-8', body_bytes: 0, truncated: false, body_text: '', json: null, response_headers, latency_ms: 254}` — matches doc §4/§5 golden path ✓
- `schedule_followup  execution_id=<fake-uuid>` → stable 11-key contract + `success: false, error: 'No AgentExecution found with execution_id=...'` — fail-loud verified ✓
- `legal_doc_drafter_agent` → registered in `platform_awareness_tool.tool_registry` listing ✓ (not dispatched — MUTATION-class end-to-end path not exercised at doc-only sweep per §5a)

## Zoom-out folds (per PLAYBOOK-6.10.7)

- **Fold Q4 (T1):** Rigby Q3 fold — PA-context invariant test coverage is handler-side-only. Entrypoint-side injection at `unified_pa_entrypoint.py:2262-2264` can silently regress without breaking these tests. Follow-up candidate ledger row, not this ship's scope.
- **Fold Q5 (T1):** Rigby T1 Q4 fold — doc/test pointer drift caught in-batch (schedule_followup doc → nonexistent test file path). Pace-masking-2nd-order-issues 1 instance; watch for 2nd trigger before proposing a doc-pointer-verification lint.

## Substrate findings (§Related deferrals — NOT new arc scope)

- **Ledger row candidate #33:** entrypoint-side context-injection test coverage gap. `unified_pa_entrypoint.py:2262-2264` `arguments.setdefault('conversation_id', self.conversation_id)` is not asserted anywhere. If a future refactor removes that line without updating callers, PA callers silently break. Substrate-arc scope; deferred.
- **Ledger row candidate #34:** doc-pointer-verification lint candidate. This ship's T1 SIGN caught `schedule_followup_validation.md` pointing to nonexistent `core/tests/test_schedule_followup_pa_context.py` before merge. One instance; if recurs, propose a lint that grep-verifies test file paths cited in validation docs exist.

## Ledger candidates (Rigby Tool Gap Ledger)

- **#33 (this session):** PA-context injection at `unified_pa_entrypoint.py:2262-2264` is not asserted anywhere. Handler-side is covered; entrypoint-side coverage gap.
- **#34 (this session):** Doc-pointer-verification lint candidate. Cite-a-test-that-exists in validation docs; 1 instance so far.

## PR shipped

- u-d-b PR [#3446](https://github.com/clwest/donkey-betz-platform/pull/3446) — S2910 Slice 2 batch 5 mixed-composition sweep, merged at `e84d69343`.
- u-d-b PR `<TBD>` — S2910 close cascade (this handoff + 00-START refresh + wrapper pin bump).

## Session close ceremony

- [x] All 4 batch-5 validation docs authored + T1b template v1 frontmatter compliant.
- [x] Metadata seed added (3 TOOL_DEFAULTS + 7 per-action brainstorm_tool records).
- [x] Regression test class added (3 tests) + 11 tests pass.
- [x] Rigby T0 + T1 SIGN cycles substantive (11 tool_runs across both rounds).
- [x] Full corpus harness re-run + gap map + audit regenerated.
- [x] PR #3446 opened, merged, live-dispatch verified.
- [x] `make celery-recycle` post-merge.
- [ ] Session handoff + 00-START refresh + wrapper pin bump → this PR.

## Next-session priorities

See `00-START-NEXT-SESSION.md`. Slice 2 batch 6 opens the sweep — 6 tools remaining in `td_handlers_agents`.
