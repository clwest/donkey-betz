# Session 2900 — Row 161 substrate arc opened (PA tools sweep-pace multiplier)

**Date:** 2026-07-22
**PR:** [#3425](https://github.com/clwest/donkey-betz-platform/pull/3425) merged into main at commit `45f544970`
**Ship shape:** Doc-only substrate-arc opening. Chris ratified Option A at S2900 open (Row 161 gate — carried from S2899 close as the mandatory first action). Ends the four-consecutive-engineering-ship streak (S2896–S2899) with an explicit substrate-arc commit.
**D6 moratorium status:** IN FORCE (no strategic discovery arcs opened this session).

## What shipped

**PR #3425 — S2900 substrate arc opening (`docs/audits/pa_tools/substrate/`).** Four new docs + one 00-START edit:

- **`S2900_substrate_arc_scoping.md`** — parent arc doc: origin (Row 161), IS/IS-NOT scope, thread sequencing, fold-log from Rigby T1 SIGN, MVP discipline governance, close criteria, session-count sanity check.
- **`T1a_auto_harness.md`** — Django management command `pa_tool_validate_harness` design; per-action safety classifier (READ_ONLY / WRITE_GATED / SIDE_EFFECT); Action Metadata Map micro-thread; stable output-schema contract (superset-compatible with `http_smoke_test` replay); anti-scope-creep watchlist.
- **`T1b_family_doc_templates.md`** — canonical per-tool validation-doc template; ratchet-and-warn posture (mandatory on new/edited docs, advisory-warn on legacy); gap-map lint extension.
- **`T1c_low_signal_audit.md`** — fast-pass triage of ~14 low-signal tools + 44 agent-via-run_agent tools; Action Metadata Map location decision (Rigby lean = in-code, adjacent to `ToolDispatcher`).
- **`00-START-NEXT-SESSION.md`** — Row 161 status flip from "MANDATORY decision point" to "OPENED at S2900 as substrate arc" with scoping pointer.

## Session shape (three-part plain-English)

1. **What was done.** Chris ratified Option A at S2900 turn 1 ("go with A") after Row 161 gate presented three options in plain English (do-we-lose-anything / more-work-later framing per `feedback_plain_english_decision_framing_for_chris`). Claude drafted arc shape and routed T1 SIGN to Rigby with mandatory zoom-out ask; Rigby returned tool-grounded (active_priority.list + search_docs + deliverable.list of engineering_backlog — non-empty tool_runs per `feedback_verify_rigby_tool_runs_before_trusting_sign`); five substantive zoom-out folds absorbed into shape before Chris "Ship it!" ratification. Four docs written + 00-START Row 161 flipped + PR merged at `45f544970` via `gh pr merge --admin` (billing still not fixed per `feedback_gh_pr_merge_admin_until_billing_fixed`). Rigby wrote twin workspace mirror (content mirror `cc7bd2c5-ef83-4c71-b2a3-76dee6f3ad97` + ratification envelope `3e9011cf-6780-4dbb-b413-6a96611d20f2`) per `feedback_rigby_writes_workspace_deliverables` + `feedback_twin_deliverable_at_every_ratification`; neither diagnostic-flagged.
2. **Why it matters.** Four consecutive engineering-first sessions (S2896–S2899) had made "one more engineering ship" the default at every session open. At the sweep's current pace (~4 tools/session), the ~76 remaining untested tools = ~50 sessions to close Slices 1.5b + 2 + 3 + 4 + 5. Row 161 was written into S2899 close specifically to force this explicit decision at S2900 open before the pattern silently became the strategy. Substrate arc's tooling — auto-harness (mechanical dispatch + response capture) + template extraction (uniform validation docs) + low-signal audit (out-of-class carving) — targets **~50 sessions → ~10–15 sessions**. Savings are from eliminating human dispatch + manual note-taking, NOT from building exhaustive integration coverage. If T1a scope creeps to full HTTP/auth/async/pagination/golden-files, payoff is lost.
3. **What's next.** S2901 opens with **T1c** as the first thread (fast pass, ~1 session): triage the ~14 low-signal tools + 44 agent-via-run_agent tools + decide Action Metadata Map location (in-code registry vs per-tool doc frontmatter — Rigby's lean = in-code). T1c's triage output feeds T1a scoping (informs harness surface area). T1a follows (≤2 sessions, MVP-strict). T1b last (1–2 sessions). Total substrate arc: ~4–5 sessions.

## Rigby SIGN cycle summary

**Pre-ship SIGN (arc-shape routing):** One turn, envelope-format, four SIGN sub-questions + mandatory zoom-out ask. tool_runs non-empty and substantive.

- **SIGN A — Arc filing location:** REVISE. Proposed `docs/research/tools/substrate/`; Rigby REVISE to `docs/audits/pa_tools/substrate/`. Reason: this is audit substrate (adjacent to gap-map + validation-doc corpus), NOT product-facing research. Adopted.
- **SIGN B — Thread order:** AGREE-with-tweak. Proposed T1a → T1b → T1c; Rigby REVISE to T1c first (fast pass) → T1a → T1b. Reason: T1c decides which tools are in-class for the harness; without that decision, T1a's surface area is unknown and MVP scope-creeps. Adopted.
- **SIGN C — Auto-harness coupling:** AGREE. Django management command `pa_tool_validate_harness`, in-process dispatch (not HTTP). Reason: avoids pytest runtime coupling + auth-boundary interaction complexity; harness stays isolated and deterministic.
- **SIGN D — Template rigidity:** REVISE. Proposed mandatory-block OR advisory; Rigby proposed ratchet-and-warn middle path. Reason: mandatory-block creates bulk-retrofit churn on 22 legacy docs; pure advisory lets drift continue. Ratchet-on-touch converges toward uniformity without a big-bang migration. Adopted.

**Zoom-out folds (all absorbed into shape pre-ship):**

- **Q1 — Harness safety semantics:** T1a must classify actions as READ_ONLY / WRITE_GATED / SIDE_EFFECT. Only READ_ONLY auto-executes. WRITE_GATED validates schema+auth edge without executing writes. Default classification is conservative (unclassified → WRITE_GATED).
- **Q2 — Action-enum ≠ testability:** Not every enum value is runnable in a local harness (external deps, staff auth, env constraints). Per-action `applicability` metadata needed (env_required / deps_required / auth_required / mutation). T1c decides where this lives; Rigby's lean = in-code registry adjacent to `ToolDispatcher`.
- **Q3 — Fragmentation risk:** Existing `http_smoke_test` + ops-proof-bundle pattern already exists. T1a output schema is superset-compatible with those (`tool_name`, `action`, `input_profile`, `expected_outcome`, `status_code`, `latency_ms`, `response_shape_keys`, `notes`) so harness output can feed smoke-test replay, not fragment it.
- **Q4 — 4th thread candidate (Action Metadata Map):** Higher-leverage than T1b if time-boxed. Folded INSIDE T1a as micro-thread (in code, not docs) rather than split into a fourth arc thread. Rigby's structural call — adopted.
- **Q5 — Session-estimate blowup risk:** 10–15-session close estimate holds only if T1a stays MVP (scaffold + harden ≤2 sessions). If T1a grows to full end-to-end integration suite, it eats 3–5 sessions and payoff is lost. Enforced as arc-level governance constraint (parent §5).

**Verification tool_runs (twin workspace mirror creates):** Rigby created both deliverables cleanly. Neither `diagnostic_flagged: false`. Content mirror content_length 8573 bytes (matches source `S2900_substrate_arc_scoping.md` at 8633 bytes minus frontmatter). Ratification envelope content_length 1876 bytes. Rigby honestly flagged `verification_gap`: `repo_tool.read_file` doesn't certify git commit SHA; content mirrored from current path, not the specific commit — equivalent here since doc is on main at `45f544970`.

## Zoom-out folds this session

None new. Rigby's five zoom-out concerns from the pre-ship SIGN were all mitigated inline in the arc-shape decisions. No new fold candidates added to the Rigby Tool Gap Ledger from this session.

## Files touched

- **Created:** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md`
- **Created:** `docs/audits/pa_tools/substrate/T1a_auto_harness.md`
- **Created:** `docs/audits/pa_tools/substrate/T1b_family_doc_templates.md`
- **Created:** `docs/audits/pa_tools/substrate/T1c_low_signal_audit.md`
- **Edited:** `00-START-NEXT-SESSION.md` (Row 161 status flip)

## Workspace mirror (Rigby-authored)

- **Content mirror:** deliverable `cc7bd2c5-ef83-4c71-b2a3-76dee6f3ad97` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`. Title: "S2900 substrate arc scoping — Row 161 mitigation (PA tools sweep-pace multiplier)". Category: `initiative_phase_doc`. deliverable_type: `document`.
- **Ratification envelope:** deliverable `3e9011cf-6780-4dbb-b413-6a96611d20f2` in Donkey Betz workspace. Title: "RATIFICATION 2026-07-22 S2900 substrate arc opening — Row 161 Option A". Category: `governance`. deliverable_type: `ratification_record`.

## Ledger status

- **Row 161** — flipped from `deferred` (MANDATORY decision point at S2900 open) to `OPENED` as substrate arc. Substrate now provides downstream ledger rows for T1a follow-on features that are deferred out of MVP scope (async waiting, pagination cursors, golden-files, etc.).
- All other deferred rows unchanged.

## What is NOT in this session

- No engineering ship. No code changes. No test additions. Substrate arc opening only.
- No OPEN_ARCS.md registration (deferred to S2901+ per parent §9 to avoid churn during scoping session).
- No T1c execution (that's S2901 turn 1).
- No T1a harness build (that's S2902–S2903).
- No T1b template extraction (that's S2903–S2904).

## Twin-pointer card (per `feedback_twin_pointer_docs_at_boundaries`)

- **Repo:** `docs/audits/pa_tools/substrate/` (4 docs) + `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md` (this handoff).
- **Workspace UI:** Donkey Betz workspace at `/workspaces/b4503364-2573-4401-9e28-61a739e0ce50`; content mirror `cc7bd2c5-ef83-4c71-b2a3-76dee6f3ad97`; ratification envelope `3e9011cf-6780-4dbb-b413-6a96611d20f2`.
