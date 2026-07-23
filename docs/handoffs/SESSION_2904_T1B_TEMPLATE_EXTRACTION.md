# Session 2904 Handoff — T1b Family-Doc Template + Ratchet Lint (Row 161 Substrate Arc CLOSE)

**Date:** 2026-07-22
**Session pin:** `pa-3844c4126d624cf6` (retired at close)
**Branch:** `main`
**HEAD at open:** `d24176fd5` (S2903 close cascade)
**HEAD at close:** `101c25aad` (S2904 T1b) + `<pending>` (S2904 close cascade)
**PRs shipped:** #3433 (T1b), `<TBD>` (close cascade)

---

## What shipped

**PR #3433 — S2904 T1b family-doc template + ratchet-and-warn lint (Row 161 substrate arc close).**

Third and final thread of the Row 161 PA Tools Sweep substrate arc. Ships:

1. `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` — canonical template file with **sweep** (default) + **protocol** variant skeletons. Header comment explains ratchet-and-warn opt-in semantics (`Template version: v1` activates mandatory-section + required-frontmatter check).
2. `core/services/pa_tools_gap_map.py` extensions:
   - `index_validation_docs` skips `_`-prefixed files (Rigby SIGN D-1 blocking mitigation — the template file itself must not be treated as a validation doc).
   - `COVERED_ACTIONS_HEADING_RE` loosened from `r'^#+\s+covered\s+actions\b'` to `r'^#+\s+(?:\d+\s*[\.\)\-–—:]?\s*)?covered\s+actions\b'` (Rigby SIGN D-2 blocking mitigation — prevents locking incidental regex behavior into policy). Accepts `## Covered actions` (bare, recommended) + `## 2. Covered actions` / `## 2) Covered actions` / `## 2 — Covered actions` (numbered variants). Still rejects `## Actions covered` (word-order false-positive).
   - New `evaluate_template_compliance()` returns `pass|warn|fail` with alias-tolerant frontmatter check (accepts `Main handler` / `Session validated` / `Report status` / `Rigby cross-check` for protocol-variant equivalents).
   - `build_gap_map` enriches each row with `template_compliance` + `template_missing`; summary carries `per_template_compliance` counter.
   - `render_gap_map_markdown` adds `Template` column between Category and Lint, plus a `## Template compliance (T1b)` summary section.
3. `core/tests/test_pa_tools_gap_map_2795.py` — 15 new tests across 4 T1b classes covering regex accept/reject, verdicts across all doc states, `_TEMPLATE_` exclusion, legacy-still-warns end-to-end. 39/39 pass.
4. `docs/audits/PA_TOOLS_GAP_MAP.md` regenerated — all 161 rows show `warn` (advisory legacy); zero `fail`. Lint gate is live for the next sweep-session doc-author to opt into via `Template version: v1`.

**Merge:** `101c25aad` at 2026-07-23T03:51:55Z via `gh pr merge --admin --squash --delete-branch`. Post-merge `make recycle-all` executed at same SHA per PLAYBOOK-7.4.4.

## Rigby SIGN T1 (S2904) — tool-grounded, no rubber-stamp

Routed 2026-07-22 via `bash tools/pa_local.sh` on pin `pa-3844c4126d624cf6` with mandatory zoom-out ask (§8 of ship-shape doc, ZO-Q1 through ZO-Q6). Rigby returned SIGN with 10 tool_runs verifying:

- Ship-shape doc + parent frames read at HEAD
- `pa_tools_gap_map.py:96` regex source + line number confirmed at HEAD
- Validation-dir tree enumerated (32 total `*_validation.md`)
- `## Covered actions` heading count verified via search (14 sweep-shape docs)
- Sample frontmatter shapes cross-checked (autopilot + agent_control sweep-shape + session_tool protocol-shape)

**Verdicts:**
- **SIGN A** (§2 template shape): AGREE-with-edits — corpus counts corrected + "shared frontmatter" reframed as v1 target.
- **SIGN B** (§2.4 new frontmatter fields): AGREE-with-edits — exact accepted values defined + presence-not-exact for legacy protocol docs.
- **SIGN C** (§3 ratchet-and-warn semantics): AGREE-with-edits — added row for invalid `Template version:` value → fail.
- **SIGN D** (§4 lint implementation): REVISE (blocking, 2 concerns):
  - **D-1 (blocking):** `_TEMPLATE_per_tool_validation.md` would be indexed as a real validation doc without an explicit `_`-prefix filter in `index_validation_docs`. Same-PR mitigated.
  - **D-2 (blocking):** template ship-shape rested on "bare heading only" language, locking an incidental regex limitation into policy. Same-PR mitigated by loosening the regex to accept optional numbering + updating template language.
- **SIGN E** (§5 ship shape): AGREE-with-edits — test coverage requirements folded (both variants pass + false-positive rejection + numbered form accepted).
- **SIGN F** (§6 non-goals): AGREE-with-edits — added 2 explicit non-goals (no protocol-frontmatter normalization + no `Template version` backfill).

**Also caught real error in §1 corpus count** (Rigby DISAGREE): my initial 22 per-tool + 17 sweep-shape claim was wrong; ground truth via direct enumeration = 19 per-tool `*_tool_validation.md` (14 sweep + 5 protocol). I over-counted by including 3 per-tool-adjacent docs (`agent_introspection_run_agent`, `kb_ingest`, `workspace_retrieval`) that don't follow the `*_tool_validation.md` naming. Same-PR corrected before merge.

**Rigby zoom-out folds (per PLAYBOOK-6.10.7):**

Nine substantive zoom-out concerns raised (ZO-Q1 through ZO-Q9). Same-PR vs forward-carry classification:

- **Same-PR:** Q1 (§1 evidence correction), Q3 (regex loosening), Q6 (both-variants-pass tests), Q9 (presence-not-exact frontmatter enforcement).
- **Forward-carry to Rigby Tool Gap Ledger:**
  - **ZO-Q2** (warn-noise escalation ladder): after 5+ sweep sessions where `template_compliance` warn count is NOT monotonically decreasing, escalate — any TOUCHED legacy doc must add `Template version: v1` in same PR.
  - **ZO-Q7** (automated corpus-counter helper): future §1 corpus-survey sections should source counts from a tiny script/mgmt command, not eyeballed grep.
  - **ZO-Q8** (structured-parse migration): if a third template variant or lint scope expansion happens, migrate `pa_tools_gap_map.py` from regex to markdown AST.

## Rigby-side artifacts (twin workspace mirror + ledger)

Written by Rigby via PA tool surface per `feedback_rigby_writes_workspace_deliverables`. Verified via `orm_inspect_tool` cross-check in the same tool_runs block:

- **Content mirror:** `adf67e67-76ab-4df0-8ebc-71f43a11fe8b` — `initiative_phase_doc` / `engineering` / title "S2904 T1b — Family-doc template + ratchet lint (Row 161 substrate arc CLOSE)"
- **Ratification envelope:** `dace0795-6518-4a53-8313-ae42a7f0ab51` — `ratification_record` / `governance` / title "RATIFICATION_20260722_S2904_T1B_ARC_CLOSE"
- **Rigby Tool Gap Ledger update:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — appended 1428 chars with the 3 ZO-Q2/Q7/Q8 forward-carry rows

All three writes landed in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`.

## Arc-close impact

**Row 161 substrate arc CLOSED.** 4 sessions total (T1c ✓ S2901 → T1a Phase 1 ✓ S2902 → T1a Phase 2 ✓ S2903 → T1b ✓ S2904) vs the ~4-5 initial estimate. Substrate now in place:

- **T1a auto-harness** (`pa_tool_validate_harness` management command) — enumerates a tool's schema `action` enum, dispatches READ_ONLY actions in-process, captures response + latency + tool_runs shape, emits structured JSON artifact. Currently dispatches 39 actions live; ready to pre-populate validation-doc stubs.
- **T1b template + ratchet lint** — canonical template + `evaluate_template_compliance` returning pass/warn/fail. Opt-in via `Template version: v1`.
- **T1c triage decisions** — 3-bucket assignment (defer / promote / close-with-note) + Action Metadata Map location decision landed at S2901.

**Expected sweep pace acceleration:** ~50 sessions → ~10-15 sessions for the remaining ~76 tools. First accelerated batch is S2905's validation opportunity.

## Zoom-out fold-log for this session

Two folds captured per PLAYBOOK-6.10.7 + persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8:

1. **Regex-as-policy footgun** (Rigby SIGN D-2) → `same_pr_mitigated`. My initial ship-shape entrenched the current bare-heading regex by requiring "bare" — Rigby correctly reframed as "template extraction should not codify an incidental regex limitation as policy." Loosened regex + `## Actions covered` false-positive regression test both shipped same-PR.
2. **§1 corpus-count drift** (Rigby SIGN A DISAGREE) → `future_trigger` ZO-Q7 (automated corpus counter). My initial count was 22→17 sweep; ground truth is 19→14 sweep. Whole SIGN discussion of "why two variants" was resting on drifted numbers. Same-PR corrected + logged as forward-carry to prevent recurrence at scale.

## Session close bookkeeping

- [x] PR #3433 merged at `101c25aad`
- [x] `make recycle-all` executed post-merge (PLAYBOOK-7.4.4)
- [x] Rigby twin workspace mirror written (content `adf67e67-…` + envelope `dace0795-…`)
- [x] Rigby Tool Gap Ledger updated (ZO-Q2 + ZO-Q7 + ZO-Q8 rows appended)
- [x] `00-START-NEXT-SESSION.md` refreshed (arc CLOSED; S2905 open sequence = Slice 2 first batch recommended)
- [x] This handoff doc written
- [ ] `session_lifecycle close` — mints S2905 pin + rewrites wrapper
- [ ] Commit wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`

## For S2905

Recommended first action: Slice 2 batch 1 (`td_handlers_agents`, 4-5 tools) using the new T1b template opt-in. First accelerated sweep batch validates the ~10-15-session multiplier claim.

Alternatives: Phase 0 heading fixes (doc-only PR clearing 8 parity mismatches) OR Slice 1.5b autopilot mutations (staged enforcement per pre-commit note in 00-START).
