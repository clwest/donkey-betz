# S2900 — PA Tools Sweep Substrate Arc (Scoping)

**Opened:** 2026-07-22 (Session 2900)
**Origin:** Ledger Row 161 (`sweep-arc pace sustainability substrate arc`) — mitigation of the "at current sweep pace (~4 tools/session), ~50 sessions remain to close the ~76 untested tools across Slices 1.5b + 2 + 3 + 4 + 5" concern.
**Chris D-verdict:** Ratified Option A at S2900 open (2026-07-22) after the "Row 161 mandatory decision point" gate carried forward from S2899 close. Options A/B/C presented plainly per `feedback_plain_english_decision_framing_for_chris`; A selected.
**Claude+Rigby SIGN:** T1 SIGN routed 2026-07-22 with mandatory zoom-out ask (`feedback_zoom_out_ask_per_rigby_sign`). Rigby REVISE on SIGN A (filing location) + SIGN D (template posture); AGREE-with-tweak on SIGN B (thread order); AGREE on SIGN C. Five substantive zoom-out concerns folded into shape below.
**Shape ratification:** Chris "Ship it!" 2026-07-22 on the Claude+Rigby-agreed shape.

---

## 1. What this arc IS

An engineering substrate arc that builds sweep-pace-multiplier tooling for the PA Tools Sweep (Path B, ratified S2892). Three parallel threads:

- **[T1a — Auto-harness build](T1a_auto_harness.md).** A Django management command (`pa_tool_validate_harness`) that enumerates a tool's schema `action` enum, dispatches read-only actions in-process (not HTTP), captures response + latency + tool_runs shape, and emits a structured JSON artifact that both (i) feeds the gap-map lint pipeline and (ii) scaffolds validation-doc stubs.
- **[T1b — Family-doc template extraction](T1b_family_doc_templates.md).** Canonicalize the per-tool validation-doc section structure. Ratchet-and-warn posture: mandatory sections enforced on new/edited docs, advisory-warn for legacy docs until touched.
- **[T1c — Low-signal tool audit](T1c_low_signal_audit.md).** Fast batch-triage of the ~14 doc-unknown/partial/doc-only tools + explicit decision on whether the 44 "agent-via-run_agent" tools fold into the sweep at all. Also decides where per-action safety+applicability metadata lives (Rigby zoom-out fold Q2/Q4).

## 2. What this arc is NOT

- **NOT a general PA-tool refactor arc.** Handler consolidation, schema simplification, error-envelope unification — all out of scope. Substrate here means sweep-pace tooling, not tool-code changes.
- **NOT a Testing Discipline chapter ratification** (Playbook Ch 8 stub). Substrate tooling MAY inform a future Playbook amendment, but this arc ships tooling first; codification later if patterns hold.
- **NOT a smoke-test framework replacement.** Existing `http_smoke_test` + ops-proof-bundle pattern stays authoritative for HTTP-surface + auth + end-to-end concerns. Auto-harness output schema is designed to be superset-compatible with those, not replace them (per Rigby zoom-out fold Q3).
- **NOT a bulk migration of legacy per-tool docs.** T1b ratchet posture explicitly avoids the churn cost of retrofitting 22 existing docs.

## 3. Thread sequencing (per Rigby SIGN B tweak)

**T1c FIRST (~1 session, may be a fast pass within a session).** Rationale: T1c decides which tools are even in-class for the harness. The 44 agent-via-run_agent tools may fold out entirely, cutting T1a's surface area before T1a is built. Also carves out external-service-dependent tools (Railway/OBS/DaVinci) whose "action" enum values are effectively not-runnable-in-local-harness.

**T1a SECOND (≤2 sessions — scaffold + harden).** Locked at MVP discipline (see §5). Auto-harness ships with per-action safety classifier + Action Metadata Map + minimal output-schema contract.

**T1b LAST (1–2 sessions).** Template extraction happens after T1a output schema is stable — otherwise template design rigidifies before we know what auto-generated sections look like.

## 4. Fold-log from Rigby SIGN T1 zoom-out (2026-07-22)

Five substantive concerns from Rigby's zoom-out; all folded into thread shape:

- **Fold Q1 (safety semantics) → T1a design constraint.** Harness must classify actions as `READ_ONLY` / `WRITE_GATED` / `SIDE_EFFECT` and only auto-execute `READ_ONLY` by default. For `WRITE_GATED` / `SIDE_EFFECT`, harness validates schema/permission edges without executing writes ("expects 400/403 + shape"). See T1a §3.
- **Fold Q2 (action-enum ≠ testability) → T1c decision point.** Some enum values need external deps or specific env. T1c decides where per-action `applicability` metadata (env_required / deps_required / auth_required / mutation) lives — doc frontmatter vs. code registry. See T1c §4.
- **Fold Q3 (fragmentation risk) → T1a output-schema contract.** Harness artifact shape is a stable minimal contract: `tool_name`, `action`, `input_profile`, `expected_outcome`, `status_code`, `latency_ms`, `response_shape_keys`, `notes`. Explicitly superset-compatible with `http_smoke_test` replay. See T1a §5.
- **Fold Q4 (4th thread → micro-thread instead) → T1a scope inclusion.** Action Metadata Map (per-tool/per-action safety + applicability registry, in code adjacent to dispatcher) folds INSIDE T1a as a scoped micro-thread — NOT split out as a fourth arc thread. Rigby's judgment call, adopted.
- **Fold Q5 (session-estimate blowup) → arc governance constraint.** T1a MVP discipline is hard: scaffold + harden ≤2 sessions total. If T1a grows to full HTTP + auth + async followups + pagination + golden-files, payoff is lost. See §5.

## 5. MVP discipline (arc-level governance)

- **T1a session cap:** 2 sessions maximum before T1a is considered "shipped" (may be doc-only ship per S2796). Additional harness features become downstream substrate rows, not T1a scope expansion.
- **Anti-scope-creep:** if a "obviously useful" feature would add 3rd session to T1a, it gets deferred to a follow-on substrate row (added to Rigby Tool Gap Ledger with `future_trigger` tag).
- **Output-schema stability:** once T1a v1 output schema ships, changes require substrate-arc-scoped SIGN (not slipped in during a T1b or per-tool sweep session).
- **T1b anti-churn:** legacy docs are NOT bulk-updated. Ratchet fires only on new-doc-authoring OR when a tool's covered-actions set changes.

## 6. Close criteria for this arc

Arc closes when all three of:
1. **T1c** produces a triage table (defer/promote/close-with-note bucket assignment for the ~14 doc-unknown/partial/doc-only tools + the 44 agent-via-run_agent set) AND the Action Metadata Map location decision is recorded.
2. **T1a** ships `pa_tool_validate_harness` management command with per-action safety classifier + stable output schema + Action Metadata Map wired in.
3. **T1b** ships the canonical template file + the gap-map lint extension enforcing ratchet-and-warn posture.

Total session estimate: **~4–5 sessions** for the substrate arc itself (T1c 1s + T1a 2s + T1b 1–2s). Expected downstream sweep-pace acceleration: **~50 sessions → ~10–15 sessions** for remaining ~76 tools.

## 7. Session count sanity-check (per Rigby Fold Q5)

The 10–15-session close estimate for the remaining sweep holds only if:
- T1c cleanly carves out the run_agent-family + external-service tools from harness surface.
- T1a stays MVP; does not evolve into a full end-to-end integration suite.
- The savings come from **reducing human dispatch + manual note-taking**, not from building exhaustive integration coverage.

If any of these three constraints slips during arc execution, the arc reopens for scope re-negotiation with Chris + Rigby before continuing.

## 8. What this arc explicitly does NOT block

- The engineering-ship pattern (S2896–S2899) is NOT frozen. Chris may still greenlight an engineering ship in any session where a ledger-row mitigation fits; substrate-arc sessions and engineering-ship sessions can interleave.
- The D6 strategic-discovery moratorium remains in force independently.
- Slice 1.5b (autopilot_tool mutations) is deferred but not blocked — may open once T1a's WRITE_GATED classification is stable.

## 9. Downstream pointers

- Row 161 status update: 00-START-NEXT-SESSION.md must reflect "OPENED at S2900 as substrate arc" on next handoff.
- Rigby Tool Gap Ledger (workspace `b4503364-2573-4401-9e28-61a739e0ce50`, deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`): downstream substrate rows accumulate here per Rigby's ledger.
- OPEN_ARCS.md: register this arc under whichever manifest slot Chris + Rigby designate at S2901 open (deferred to avoid churn during scoping session).
- Workspace mirror (Rigby writes, per `feedback_rigby_writes_workspace_deliverables`): content mirror of this scoping doc + ratification envelope in Donkey Betz workspace at arc-open close.
