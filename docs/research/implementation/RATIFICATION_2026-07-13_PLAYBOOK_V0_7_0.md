---
title: "Engineering Playbook v0.7.0 Amendment Ratification Record (2026-07-13)"
status: active
authority: ratification-record
session_added: 2778
ratification_date: 2026-07-13
ratifier: chris
ratifier_verdict: "yes ship it"
routing: rigby-pa-chat joint SIGN (3-turn loop: V1..V6 tool-grounded verifications with V1 F-BLOCKING DISAGREE on rule-ID collision + 4 same_pr_actionable folds from V6 zoom-out ask; turn 3 lock-in AGREE on corrected design) + Chris D-verdict via terminal single yes
amendment_scope: playbook-minor-v0.7.0
amendment_class: MINOR (per PLAYBOOK-10.5.1 — 2 additions, 0 modifications, 0 removals)
parent_version: v0.6.0
parent_version_git_tag: playbook-v0.6.0
parent_version_commit_sha: PLACEHOLDER_FILLED_AT_MERGE
parent_version_ratification: RATIFICATION_2026-07-11_PLAYBOOK_V0_6_0
proposed_version: v0.7.0
proposed_git_tag: playbook-v0.7.0
predecessor_candidacy: MEMORY.md `feedback_zoom_out_ask_per_rigby_sign.md` (S2771 close) + RATIFICATION_2026-07-13_zoom_out_classifications_helper.md (S2777 N22 substrate ship with 13-row seed ledger)
head_at_amendment_draft: 59db8626324d
head_at_ratification: PLACEHOLDER_FILLED_AT_MERGE
close_pr: PLACEHOLDER_FILLED_AT_MERGE
sign_sessions:
  - S2778 turn 1 — Rigby V1..V6 tool-grounded verification (6+ real search_docs invocations; anti-rubber-stamp gate PASS); V1 F-BLOCKING DISAGREE on rule-ID collision (I-0302 candidate pre-allocated 6.10.7); V2/V3/V4 PASS on site scope and classification
  - S2778 turn 2 — Rigby V5 PASS (no existing rule mandates persistence) + V6 zoom-out ask produced 4 same_pr_actionable folds (V6a sequencing, V6b graceful-degradation, V6c definition inlining, V6d no-folds carve-out); overall verdict truncated by token cap
  - S2778 turn 3 — Rigby AGREE on corrected design with all 4 V6 folds incorporated (site §6.10 PATH A; IDs 6.10.7/6.10.8; MINOR v0.7.0; I-0302 re-slotted to 6.10.9)
rules_added:
  - PLAYBOOK-6.10.7
  - PLAYBOOK-6.10.8
rules_modified: []
rules_removed: []
rule_count_before: 202
rule_count_after: 204
chapter_activation: "Chapter 6 §6.10 extension — 2 new [GR] rules added under existing FULL-chapter scope; §6.10 preamble extended to note zoom-out + classification discipline; §6.12 extension points augmented with 2 new candidate-future items"
supersedes: none
superseded_by: (open; not expected — ratification records are frozen historical envelopes)
frozen: true
workspace_id: a9a16593-e0a4-44dc-8256-efc65d524b3c
workspace_name: "Architecture & Research"
workspace_ratification_deliverable_id: PLACEHOLDER_FILLED_POST_MERGE
d_verdicts:
  - V1 Rule-ID collision — I-0302 three-PR candidate re-slotted to PLAYBOOK-6.10.9 per PLAYBOOK-10.7.5 next-integer rule (pre-allocation ≠ ratified reservation) — RATIFIED 2026-07-13 S2778
  - V2 Site placement — §6.10 (not §7.6 close-cycle) because S2771 rule scope is all joint SIGN routings — RATIFIED 2026-07-13 S2778
  - V3 Rule-scope grounding — "joint SIGN routing" definition inlined in PLAYBOOK-6.10.7 text — RATIFIED 2026-07-13 S2778
  - V4 Amendment classification — MINOR v0.7.0 per PLAYBOOK-10.4.1 (PATCH cannot introduce rules) + PLAYBOOK-10.5.1 (new [GR] rules are MINOR minimum) — RATIFIED 2026-07-13 S2778
  - V5 No redundancy — no existing rule mandates zoom-out fold persistence; §6.10.1/6.10.2 provenance-recording is a different artifact/scope — RATIFIED 2026-07-13 S2778
  - V6 Zoom-out folds incorporated pre-D-verdict — 4 same_pr_actionable folds (a/b/c/d) all incorporated into rule text before Chris routing per `feedback_claude_rigby_agree_first_chris_yes_no` — RATIFIED 2026-07-13 S2778
---

# Engineering Playbook v0.7.0 — Amendment Ratification Record

This file is the **workspace ratification envelope reflected in-repo** for the Engineering Playbook v0.7.0 MINOR amendment. It captures the amendment scope, the empirical corroboration ladder (§4), the Rigby joint SIGN 3-turn cycle (§5), Chris's D-verdict (§6), and the post-ratification bindings (§7). Append-only; do NOT edit after commit except to fill the reserved TBD fields (`head_at_ratification`, `close_pr`, `workspace_ratification_deliverable_id`, `parent_version_commit_sha`).

---

## §1. Context

- **Amendment class:** MINOR (2 additions, 0 modifications, 0 removals) per PLAYBOOK-10.5.1.
- **Session:** S2778 (single-session author + SIGN + ratify + ship; second consecutive constitutional amendment in same-session shape after v0.6.0/S2766 precedent).
- **Head at amendment draft:** `59db8626324d` (post-S2777 merge PR #3166).
- **Ratifier:** Chris ("yes ship it" at S2778, single-yes following joint Claude+Rigby agreement on corrected design).
- **Routing:** Rigby PA chat surface via pin `pa-ced04dddd39346a9` (S2778 scope: zoom-out SIGN discipline codification).
- **Predecessor:** memory rule `feedback_zoom_out_ask_per_rigby_sign.md` (authored S2771 close 2026-07-12) + N22 substrate `RATIFICATION_2026-07-13_zoom_out_classifications_helper.md` (S2777 N22 ship with 13-row seed ledger).
- **Novel-precedent moments this cycle:**
  1. First mid-arc rubber-stamp catch survived and codified — S2777 turn 1 AGREE x4 with 0 tool_runs prompted Chris pressure test; anti-rubber-stamp gate now applied explicitly at S2778 SIGN dispatch (V1..V6 tool-grounded directives), producing 6+ real `search_docs` invocations in turn 1.
  2. Second F-BLOCKING DISAGREE of the S2771-rule streak (V1: rule-ID collision) surfaced only because tool-grounded verification was mandated — a text-only SIGN would have taken 6.10.7 without checking the I-0302 candidacy pre-allocation.
  3. Substrate dogfooding at authoring — 4 V6 folds from this amendment's own SIGN classified + persisted to `logs/zoom_out_classifications.jsonl` before D-verdict (ledger grew 13 → 17 rows), demonstrating PLAYBOOK-6.10.8 discipline in-wild before it was even ratified.

---

## §2. Ratified amendment scope

### §2.1 New rule PLAYBOOK-6.10.7

Added under existing §6.10 Verification of provenance (Chapter 6 FULL-chapter scope from v0.1.0). Full rule text:

> **[GR] PLAYBOOK-6.10.7** Every joint SIGN routing MUST include at least one open-ended zoom-out ask that steps back from the immediate change to surface framing risk, coupling accretion, or dropped-context signals. A *joint SIGN routing* is any SIGN dispatch in which the reviewer is asked both (a) to verify a design-lean or claim on its own terms AND (b) to render an independent zoom-out ("what would you push back on if I asked fresh?" / "what risk / coupling is this accreting?" / "what am I not seeing?"), whether the joint shape is invoked by explicit operator routing text or by session-open convention. The zoom-out ask MUST be phrased so it can produce a substantive fold; a rhetorical or leading formulation that permits only assent does NOT satisfy this rule.

### §2.2 New rule PLAYBOOK-6.10.8

Added under existing §6.10 immediately after 6.10.7. Full rule text:

> **[GR] PLAYBOOK-6.10.8** If a joint SIGN routing produces one or more folds or concerns from the zoom-out ask required by PLAYBOOK-6.10.7, each fold MUST be classified into exactly one of the enumerated categories {`same_pr_actionable`, `same_pr_mitigatable`, `future_trigger`} AND persisted to `logs/zoom_out_classifications.jsonl` via the `record_zoom_out_concern` management command before the ratifier's D-verdict is requested. The three categories are: `same_pr_actionable` — the fold identifies a change that MUST be incorporated into the same PR before ship; `same_pr_mitigatable` — the fold identifies a risk that CAN be mitigated in the same PR (via rule-text refinement, added carve-out, or scope narrowing) without expanding scope; `future_trigger` — the fold identifies a concern whose amendment is deferred to a named trigger condition. If a zoom-out ask produces zero folds, no ledger write is required. If the `record_zoom_out_concern` command fails due to tooling or runtime error, the reviewer MAY proceed to D-verdict ONLY after (i) pasting the classified fold verbatim inline in the SIGN attestation, (ii) tagging the entry `ledger-write deferred`, AND (iii) opening a follow-up action item in the close doc or handoff to backfill the ledger. The graceful-degradation clause does NOT waive classification; it defers only the persistence write.

### §2.3 Body doc updates

- Frontmatter version bump `0.6.0` → `0.7.0`; `parent_version` `0.5.0` → `0.6.0`; `compatible_with` appends `"0.6.0"`; `rule_count` 202 → 204; new `rules_added_v0_7_0: [PLAYBOOK-6.10.7, PLAYBOOK-6.10.8]` field; new `v0_7_0_authoring_session` + `v0_7_0_ratification_session` fields (both S2778); `prior_ratification` block updated with v0.6.0 metadata; `authoring_sessions` list appends 2778; `branch_authored` updated to `playbook/v0.7.0-zoom-out-sign-discipline`.
- Body title `v0.6.0` → `v0.7.0`.
- Chapter 6 frontmatter — `Last substantive change` updated `v0.1.0` → `v0.7.0`; `Rule ID range` extended `PLAYBOOK-6.1.1 through PLAYBOOK-6.10.4` → `PLAYBOOK-6.1.1 through PLAYBOOK-6.10.8`.
- §6.10 preamble extended with a third sentence noting the v0.7.0 zoom-out + fold-classification discipline extension with S2771–S2777 empirical anchor.
- §6.10 body — new rules PLAYBOOK-6.10.7 + PLAYBOOK-6.10.8 inserted after PLAYBOOK-6.10.6 and before the closing Commentary block. Commentary block extended with proportionality note applying §6.10.6 principle to §6.10.7/§6.10.8.
- §6.12 Extension points — 2 new bullets added (ledger evolution + anti-rubber-stamp SIGN discipline).
- Appendix D — new v0.7.0 row appended with authoring notes including I-0302 6.10.9 re-slot.

---

## §3. What was NOT changed

- No existing rule modified. PLAYBOOK-6.10.1 through 6.10.6 text unchanged; §7.x and §10.x untouched; Chapters 0–5 and 8–9 untouched.
- No evidence class or statement class added. No manifest additions (rules cite existing evidence corpus + new S2778 envelope + S2777 N22 envelope + memory rule).
- No canonical authority reclassification.
- No frontmatter `compatible_with` removal — v0.6.0 appended, prior entries preserved.
- No supersession or retirement.

---

## §4. Corroboration ladder (empirical basis for MINOR ratification)

The rule was surfaced by a memory-recorded operator observation at S2771 close (`feedback_zoom_out_ask_per_rigby_sign.md`) after Chris observed SIGN drift to 3 consecutive all-PASSes on ops-console iterations. Between S2772 and S2777, seven sessions accumulated in-wild application data:

### §4.1 Empirical streak (S2771–S2777)

| Session | Arc | Application signal | F-BLOCKING? | Handoff evidence |
|---|---|---|---|---|
| S2772 | ops_auth_regression_smoke_suite | 7 substantive folds from zoom-out ask (2 shipped same-PR / 4 forward-carry / 1 escalated) — first application after codification | no | `docs/handoffs/SESSION_2772_OPS_AUTH_REGRESSION_SMOKE_SUITE_RATIFIED.md` |
| S2773 | ops_query_param_allowlist | zoom-out produced 5 folds, all classified same-PR-actionable or forward-carry | no | `docs/handoffs/SESSION_2773_OPS_QUERY_PARAM_ALLOWLIST_RATIFIED.md` |
| S2774 | ops_urlconf_lambda_cleanup | zoom-out surfaced the PR-churn + capstone-verification concern that forced the same-PR capstone shape | no | `docs/handoffs/SESSION_2774_OPS_URLCONF_LAMBDA_CLEANUP_RATIFIED.md` |
| S2775 | session_freshness_verdicts | zoom-out identified JSONL rotation + PA-tool-read as future-trigger; ops-surface pause codified | no | `docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_RATIFIED.md` |
| S2776 | pa_wrapper_ownership_check | **first F-BLOCKING DISAGREE of streak** — Rigby refuted Q1 design lean; forced sharp 5-point `/api/pa/*` test codification | YES (Q1) | `docs/handoffs/SESSION_2776_PA_WRAPPER_OWNERSHIP_CHECK_RATIFIED.md` |
| S2777 | zoom_out_classifications_helper | **second F-BLOCKING DISAGREE of streak** — Rigby refuted Claude's PLAYBOOK-6.10 two-triggers claim; framing corrected pre-ship | YES (§6.10) | `docs/handoffs/SESSION_2777_ZOOM_OUT_CLASSIFICATIONS_HELPER_RATIFIED.md` |
| S2778 | this amendment | 4 same_pr_actionable folds from V6 zoom-out incorporated pre-D-verdict; substrate dogfooded at authoring | no | this envelope |

### §4.2 Ledger substrate (empirical basis for §6.10.8 persistence mandate)

- S2777 N22 shipped `logs/zoom_out_classifications.jsonl` with 13 seed rows (12 backfilled from S2774+S2775+S2776 envelope §4 SIGN Summary + envelope frontmatter + 1 live S2777).
- S2778 amendment authoring itself added 4 rows (V6a/V6b/V6c/V6d folds), demonstrating the discipline in-wild before ratification.
- Ledger at v0.7.0 ratification: 17 rows (5 same_pr_actionable / 7 same_pr_mitigatable / 1 future_trigger from S2774–S2777 + 4 same_pr_actionable from S2778).
- N22 substrate: 147-line JSONL writer + 128-line CLI reader + 10-test suite, 10/10 PASS at 0.008s at S2777 close.

### §4.3 Aggregate

- 7 sessions of in-wild application (S2771 codification + 6 sessions of exercise).
- 2 F-BLOCKING DISAGREEs prevented ship-time incorrect artifacts — the corroboration signal is exceptionally strong for a MINOR amendment.
- Same operator (Chris), same machine, same repo — single-operator context native to Donkey Betz per `project_single_user_pre_prod_operating_context`.
- PLAYBOOK §14.2 default two-trigger threshold satisfied at S2772 (first application after codification); triple-plus confirmed across S2773/S2774/S2775/S2776/S2777.
- Ledger substrate (§4.2) provides mechanical enforcement path — the rule is not merely aspirational; the discipline has a shipped implementation.

---

## §5. Rigby joint SIGN cycle

### §5.1 Turn 1 — V1..V6 tool-grounded verifications

Dispatched via wrapper pin `pa-ced04dddd39346a9` at S2778 P0 with explicit anti-rubber-stamp directives per S2777 lesson ("verify tool_runs non-empty when SIGN expects substantive verification of prior claims").

**Anti-rubber-stamp gate outcome:** PASS. Rigby executed 6+ real `search_docs` invocations with returned chunks + 1 `repo_tool` file read. Tool runs are visible in the tool-verbose output block; the SIGN was NOT text-only.

**V1 — §6.10 rule ID collision check.** F-BLOCKING DISAGREE.
- Claude proposed: PLAYBOOK-6.10.7 + 6.10.8 for the new rules; 6.10.7 is next-unused per PLAYBOOK-10.7.5.
- Rigby found: `RATIFICATION_2026-07-10_i0302_arc_close.md` §11 explicitly proposes PLAYBOOK-6.10.7 for the "three-PR substrate pattern" candidate; `SESSION_2751_I0302_ARC_CLOSED.md` §4 echoes the same slot.
- Resolution: pre-allocation in a candidate document does not constitute ratified reservation per PLAYBOOK-10.7.5 (gap-fill forbidden; next-integer assigned to first-authored). N23 takes 6.10.7 + 6.10.8; I-0302 re-slots to 6.10.9. Explicit sequencing note added to Appendix D + this envelope §2.

**V2 — §7.6 close-cycle vs §6.10 all-SIGN scope.** PASS.
- Rigby confirmed §7.6 is "close-cycle only" (verbatim quote from body); S2771 rule scope is all joint SIGN routings per ratification-record language across S2772–S2777. §6.10 correct home.

**V3 — S2771 memory rule scope grounding.** PASS.
- Rigby cited multiple ratification records using "joint SIGN routing" phrase; scope is general, not close-cycle. Definition inlined in PLAYBOOK-6.10.7 to prevent later scope drift.

**V4 — Amendment classification (PATCH vs MINOR).** PASS.
- Rigby cited PLAYBOOK-10.4.1 (PATCH forbids new rules) + PLAYBOOK-10.5.1 (MINOR MAY introduce new rules) + precedent from `SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md` and `SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md`. New [GR] rules mandate MINOR minimum. v0.7.0 constitutionally correct.

### §5.2 Turn 2 — V5 + V6 (truncated by token cap)

**V5 — No-redundancy check on existing persistence rules.** PASS.
- Rigby verified §6.10.1/6.10.2 mandate provenance-recording but different artifact/scope; no existing rule mandates zoom-out fold persistence. New rule not redundant.

**V6 — Zoom-out ask on the amendment itself.** 4 same_pr_actionable folds produced:
- **V6(a) sequencing risk** — I-0302 pre-allocation creates precedent risk. Mitigation: explicit sequencing note in envelope + Appendix D (mitigation applied).
- **V6(b) single-point-of-failure** — persistence-before-D-verdict without degradation clause would block all future SIGNs on tooling failure. Mitigation: graceful-degradation clause added to PLAYBOOK-6.10.8 (inline paste + `ledger-write deferred` tag + follow-up action) (mitigation applied).
- **V6(c) definition drift** — "joint SIGN routing" not Playbook-defined; reviewers will argue scope. Mitigation: definition inlined in PLAYBOOK-6.10.7 as parenthetical clause (mitigation applied).
- **V6(d) tiny-SIGN ceremony** — unconditional persistence would create overhead on trivial edits. Mitigation: no-folds carve-out added to PLAYBOOK-6.10.8 ("If a zoom-out ask produces zero folds, no ledger write is required.") (mitigation applied).

Overall verdict output truncated by GPT-5.2 token cap; substantive analysis complete.

### §5.3 Turn 3 — Verdict lock-in

Dispatched with compact re-formulation of corrected design (all 4 V6 folds incorporated). Rigby returned: **AGREE** on corrected design. Route to Chris for D-verdict. Tool runs non-empty (1 targeted verification of PLAYBOOK-10.7.5 language). Anti-rubber-stamp gate PASS.

### §5.4 SIGN verdict

**All 6 verifications resolved. Joint Claude+Rigby agreement reached before Chris routing per `feedback_claude_rigby_agree_first_chris_yes_no`. 4 V6 folds classified + persisted to ledger (dogfood).**

---

## §6. Chris D-verdict

Sequence:

1. **Session-open candidate selection (S2778):** Chris selected N23 from the S2778 candidate menu (Playbook amendment codifying zoom-out SIGN discipline) after Claude presented net-new engineering candidates per `feedback_engineering_bias_over_audit`.
2. **Joint recommendation card:** After turn 3 SIGN lock-in, Claude presented corrected design table with all 4 V6 folds incorporated pre-ratifier-routing.
3. **D-verdict:** "yes ship it."

**Effect:** Rule count 202 → 204. §6.10 grows from six rules to eight. Second consecutive MINOR amendment shipped in single-session shape (v0.6.0 precedent at S2766). First amendment with **substrate dogfooded at authoring** (4 folds classified + persisted before ratification). First MINOR amendment where an in-flight rule prevented a **second** ship-time incorrect artifact via the very discipline it codifies (V1 rule-ID collision caught by tool-grounded SIGN, the same discipline being ratified).

---

## §7. Provenance chain

- **Predecessor sessions:**
  - S2771 close (2026-07-12) — memory rule `feedback_zoom_out_ask_per_rigby_sign.md` authored.
  - S2772 → S2777 — in-wild application streak; 2 F-BLOCKING DISAGREEs at S2776 Q1 + S2777 §6.10 claim.
  - S2777 (2026-07-13) — N22 ratified: 275-line command surface + 13-row JSONL seed ledger; 10-test suite 10/10 PASS.
  - **S2778 (2026-07-13) — codification into Playbook as PLAYBOOK-6.10.7 + 6.10.8.**
- **Reference implementations:**
  - `core/management/commands/record_zoom_out_concern.py` (147-line JSONL writer, S2777 N22 ship).
  - `core/management/commands/zoom_out_streak_report.py` (128-line CLI reader with `--as-json`).
  - `logs/zoom_out_classifications.jsonl` (17 rows at v0.7.0 ratification).
  - `core/tests/test_zoom_out_classifications_2777.py` (10-test suite; both write-path + read-path).
- **Memory rules applied:**
  - `feedback_zoom_out_ask_per_rigby_sign.md` (originating rule — status shifts to constitutional at v0.7.0)
  - `feedback_verify_rigby_tool_runs_before_trusting_sign.md` (anti-rubber-stamp discipline applied at V1..V6 dispatch)
  - `feedback_claude_rigby_agree_first_chris_yes_no.md` (SIGN agreement reached before Chris routing)
  - `feedback_engineering_bias_over_audit.md` (N23 was a net-new engineering candidate selected over audit alternatives)
  - `feedback_gh_pr_merge_admin_until_billing_fixed.md` (`--admin` flag will be used on merge)
  - `feedback_local_truth_no_production.md` (post-merge dogfood recycle as the "shipped" gate)
- **Playbook rules exercised in the ship:**
  - PLAYBOOK-6.10.7 (dogfooded — this SIGN itself included the zoom-out ask at V6)
  - PLAYBOOK-6.10.8 (dogfooded — 4 V6 folds classified + persisted before D-verdict)
  - PLAYBOOK-7.4.1 (this PR is itself a single-PR close bundle — amendment doc + ratification envelope + handoff + cascade)
  - PLAYBOOK-7.4.2 (no substrate PRs interleaved on the Playbook doc)
  - PLAYBOOK-7.4.3 (cascade output COMBINED with close-doc PR)
  - PLAYBOOK-7.4.4 (post-merge `make recycle-all` invoked after HEAD advances)
  - PLAYBOOK-7.6.1 (SIGN structured as V1..V6 verification points per close-cycle watchpoint discipline — though this amendment is a research-methodology cycle rather than a close-cycle, the watchpoint shape was adopted)
  - PLAYBOOK-10.5.3 (MINOR amendment full SIGN cycle discharged across 3 turns)
  - PLAYBOOK-10.7.5 (next-integer rule invoked to resolve V1 collision; I-0302 candidate re-slotted 6.10.7 → 6.10.9)
- **Forward-carry:**
  - I-0302 three-PR pattern amendment (whenever it lands) targets PLAYBOOK-6.10.9.
  - Anti-rubber-stamp SIGN codification — second trigger observed at S2778 V1 (would have shipped 6.10.7 collision without tool-grounded verification); memory rule `feedback_verify_rigby_tool_runs_before_trusting_sign.md` now has 2 triggers. Candidate for future MINOR amendment extending §6.10.7 or §6.10.8 with explicit tool-runs assertion.
  - Ledger evolution candidates (Django model, PA-tool read handler, JSONL rotation) — deferred pending trigger per §6.12 new extension point.

---

## §8. Post-ratification bindings

- **Docs cascade** — 4-step (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed`) plus `build_docs_provenance`. Runs at close per PLAYBOOK-7.4.3 COMBINED cadence.
- **Workspace mirror** — this envelope mirrored to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research) as `deliverable_type='ratification_record'`, `category='governance'` per twin-canonical-representation rule.
- **Content mirror** — the Playbook body doc itself (as of v0.7.0) mirrored as content deliverable in the same workspace.
- **Handoff** — `docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`.
- **CLAUDE.md** — L3 anchor refreshed to reference v0.7.0 as latest ratified version with v0.6.0 preserved in ancestry chain.
- **Recycle dogfood** — `make recycle-all` invoked after PR merge (satisfies PLAYBOOK-7.4.4).
- **Memory** — MEMORY.md entry for `feedback_zoom_out_ask_per_rigby_sign.md` updated to reference this ratification (rule now constitutional, not just operator memory).
- **Ledger dogfood** — 4 V6 folds classified + persisted before D-verdict, satisfying PLAYBOOK-6.10.8 before the rule was even ratified.

---

## §9. Limitations

- **Local pass = shipped** per `feedback_local_truth_no_production`. No production observation window. Dogfood via `make recycle-all` at close = the deploy step.
- **Ledger corruption resilience is manual** — the graceful-degradation clause requires operator to paste fold inline + tag `ledger-write deferred` + open follow-up. Not machine-enforced. Automation candidate for a future PATCH sidecar or a future MINOR extension.
- **"Joint SIGN routing" definition is inline** — the parenthetical definition in PLAYBOOK-6.10.7 covers the common case (explicit operator routing + zoom-out) but does not enumerate every SIGN shape. If a future arc surfaces a SIGN shape not obviously covered (e.g., autonomous SIGN in an agent-loop context), the definition MAY need a MINOR-scope extension.
- **Anti-rubber-stamp rule not yet codified** — the discipline that produced the substantive V1..V6 tool-grounded SIGN at S2778 turn 1 is memory-rule-only (`feedback_verify_rigby_tool_runs_before_trusting_sign.md`). Second trigger observed at S2778 V1; ready for MINOR amendment when a third independent trigger surfaces OR when Chris authorizes early codification.

---

*Frozen at S2778 ratification. Do not edit except to fill reserved PLACEHOLDER fields.*
