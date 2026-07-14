---
title: "Engineering Playbook v0.8.0 Amendment Ratification Record (2026-07-14)"
status: active
authority: ratification-record
session_added: 2786
ratification_date: 2026-07-14
ratifier: chris
ratifier_verdict: "yes ship it"
routing: rigby-pa-chat joint SIGN (2-turn tool-grounded verification loop with T2 F-BLOCKING DISAGREE on "at HEAD" underspecification driving a T4 revision cycle; final AGREE) + Chris D-verdict via terminal single yes
amendment_scope: playbook-minor-v0.8.0
amendment_class: MINOR (per PLAYBOOK-10.5.1 — 1 addition, 0 modifications, 0 removals)
parent_version: v0.7.0
parent_version_git_tag: playbook-v0.7.0
parent_version_commit_sha: PLACEHOLDER_FILLED_AT_MERGE
parent_version_ratification: RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0
proposed_version: v0.8.0
proposed_git_tag: playbook-v0.8.0
predecessor_candidacy: two-trigger corpus in `logs/zoom_out_classifications.jsonl` row 31 (S2784 T2 SIGN Fold 4, 2026-07-14T18:06:59Z) + row 32 (S2785 T1 SIGN Fold 1, 2026-07-14T20:55:21Z); flagged as Playbook amendment candidate at `docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md` §2 + §5
head_at_amendment_draft: 0b11bc07d075
head_at_ratification: PLACEHOLDER_FILLED_AT_MERGE
close_pr: PLACEHOLDER_FILLED_AT_MERGE
cascade_pr: PLACEHOLDER_FILLED_AT_CASCADE
cascade_pr_merge_sha: PLACEHOLDER_FILLED_AT_CASCADE
sign_sessions:
  - S2786 T1 — Rigby joint SIGN dispatch with tool-grounded directives for items 1-4 (ledger evidence, slot verification, version-history precedent, rule text review) + PLAYBOOK-6.10.7 zoom-out ask. Rigby ran 5 tool_runs (repo_tool.read_file × 2, repo_tool.search × 2, zoom_out_tool.list) — anti-rubber-stamp gate PASS
  - S2786 T2 — Rigby SIGN attestation: Items 1/2/3 AGREE, Item 4 DISAGREE (F-BLOCKING on "at HEAD" underspecification — HEAD moves after attestation, not replayable); zoom-out folds A (`same_pr_mitigatable` — hygiene→evidence-admission reframe) + B (`future_trigger` — helper-tooling extension point); persist blocked by tooling (read-only zoom_out_tool surface), handoff persist to Claude
  - S2786 T3 — Rigby classify + persist request handoff (both folds A + B recorded via `record_zoom_out_concern` from Claude environment; ledger 34 → 36 rows before D-verdict per PLAYBOOK-6.10.8)
  - S2786 T4 — Rigby verified revised rule text: Item 4 AGREE (F-BLOCKING resolved by evidence-admission reframe + stable-state-pointer requirement); Fold A AGREE (framing landed); Fold B AGREE (§6.12 note matches v0.4.1 informative-only precedent); DISAGREE on any new F-blockers (one non-blocking caution re: over-trigger scope, tightened via "materially change classification/action path" predicate); 1 tool_run (repo_tool.read_file for v0.4.1 §6.12 precedent) — anti-rubber-stamp gate PASS
rules_added:
  - PLAYBOOK-6.10.9
rules_modified: []
rules_removed: []
rule_count_before: 204
rule_count_after: 205
chapter_activation: "Chapter 6 §6.10 extension — 1 new [GR] rule under existing FULL-chapter scope; §6.10 commentary block extended to note proportionality for §6.10.9; §6.12 extension points augmented with 1 new candidate-future item (fold-authoring evidence-admission helper — Fold B forward-carry)"
supersedes: none
superseded_by: (open; not expected — ratification records are frozen historical envelopes)
frozen: true
workspace_id: a9a16593-e0a4-44dc-8256-efc65d524b3c
workspace_name: "Architecture & Research"
workspace_ratification_deliverable_id: PLACEHOLDER_FILLED_POST_MERGE
d_verdicts:
  - D1 Rule-ID slot — PLAYBOOK-6.10.9 taken per PLAYBOOK-10.7.5 next-integer rule; I-0302 three-PR pattern candidacy re-slotted forward to PLAYBOOK-6.10.10 (v0.7.0 provenance had already noted the same re-slot for 6.10.9; this amendment repeats the pattern for 6.10.10) — RATIFIED 2026-07-14 S2786
  - D2 Site placement — §6.10 (extends §6.10.8 for fold-authoring-turn scope), not a new section; matches v0.7.0 precedent of extending §6.10 rather than creating a new section for closely-related discipline — RATIFIED 2026-07-14 S2786
  - D3 Amendment classification — MINOR v0.8.0 per PLAYBOOK-10.4.1 (PATCH cannot introduce rules) + PLAYBOOK-10.5.1 (new [GR] rules are MINOR minimum). Initial CLAUDE-authored label "v0.7.1 PATCH" in `00-START-NEXT-SESSION.md` corrected to v0.8.0 MINOR at S2786 T1 SIGN routing before dispatch — RATIFIED 2026-07-14 S2786
  - D4 Rule-text framing — "evidence admission" (not "fold-authoring hygiene") per Rigby T2 Fold A (`same_pr_mitigatable`); rule text and §6.12 note both use evidence-admission vocabulary — RATIFIED 2026-07-14 S2786
  - D5 Stable-state-pointer definition — "commit SHA from `git rev-parse HEAD`; if PR or branch reference used, MUST include the commit SHA under review" per Rigby T4 non-blocking micro-edit — RATIFIED 2026-07-14 S2786
  - D6 Scope-predicate tightening — "code-state fact that, if wrong, would materially change the fold's classification or action path" per Rigby T4 non-blocking caution against over-trigger risk — RATIFIED 2026-07-14 S2786
  - D7 Zoom-out folds incorporated pre-D-verdict — 2 folds (Fold A `same_pr_mitigatable` + Fold B `future_trigger`) persisted to `logs/zoom_out_classifications.jsonl` before Chris routing per PLAYBOOK-6.10.8 and `feedback_claude_rigby_agree_first_chris_yes_no` — RATIFIED 2026-07-14 S2786
---

# Engineering Playbook v0.8.0 — Amendment Ratification Record

This file is the **workspace ratification envelope reflected in-repo** for the Engineering Playbook v0.8.0 MINOR amendment. It captures the amendment scope, the empirical two-trigger corroboration (§4), the Rigby joint SIGN 2-turn (with T4 revision) cycle (§5), Chris's D-verdict (§6), and the post-ratification bindings (§7). Append-only; do NOT edit after commit except to fill the reserved PLACEHOLDER_* fields.

---

## §1. Context

- **Amendment class:** MINOR (1 addition, 0 modifications, 0 removals) per PLAYBOOK-10.5.1.
- **Session:** S2786 (single-session author + SIGN + ratify + ship; third consecutive constitutional amendment in same-session shape after v0.6.0/S2766 and v0.7.0/S2778 precedent).
- **Head at amendment draft:** `0b11bc07d075` (post-S2785 cascade PR #3184).
- **Ratifier:** Chris ("yes ship it" at S2786, single-yes following joint Claude+Rigby agreement on corrected design).
- **Routing:** Rigby PA chat surface via pin `pa-d065f1dfadac4cd4` (S2786 scope: fold-authoring evidence-admission codification).
- **Predecessor:** two-trigger empirical corpus — ledger row 31 (S2784 T2 SIGN Fold 4) + row 32 (S2785 T1 SIGN Fold 1); flagged as Playbook amendment candidate at `docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md` §2 + §5.
- **Novel-precedent moments this cycle:**
  1. **First MINOR amendment shipped as direct closure of a two-trigger corpus enumerated in the ledger substrate itself.** The zoom-out ledger (`logs/zoom_out_classifications.jsonl`, ratified S2777) was designed as longitudinal signal, not automatic escalation trigger. S2786 is the first amendment where the empirical corpus that motivates the rule is enumerable directly from the ledger by row number (31 + 32), rather than reconstructed from handoff prose. **The substrate is being used to justify amendments to the substrate's own governing discipline.**
  2. **T2 F-BLOCKING DISAGREE on "at HEAD" underspecification demonstrated the T4 revision cycle's value.** Rigby's tool-grounded T2 caught a real reproducibility gap that would have shipped as-is under a rubber-stamp SIGN. Third F-BLOCKING DISAGREE of the S2771-rule streak (V1 slot collision at S2778 T1; V3 canonical home at S2780 T1; D4 "at HEAD" at S2786 T2). All three F-BLOCKING catches happened on tool-grounded SIGN turns; none happened on text-only SIGN turns.
  3. **Substrate dogfooding at authoring extended.** v0.7.0 dogfooded 4 folds pre-D-verdict; v0.8.0 dogfooded 2 folds pre-D-verdict AND the amendment's own rule text was the subject of the F-BLOCKING catch that drove reframing. The rule's discipline was applied to the rule's own drafting cycle before the rule was even ratified — the ledger record for Fold A (`same_pr_mitigatable`) drove the "evidence admission" reframe that appears in the ratified rule text.

---

## §2. Ratified amendment scope

### §2.1 New rule PLAYBOOK-6.10.9

Added under existing §6.10 Verification of provenance (Chapter 6 FULL-chapter scope from v0.1.0). Full rule text:

> **[GR] PLAYBOOK-6.10.9** When authoring a zoom-out fold whose concern text asserts a specific code-state fact that, if wrong, would materially change the fold's classification or action path — for example naming an authZ gap, an error-handling gap, an endpoint's gating state, a substrate location, or the presence/absence of a specific block of code — the fold-authoring turn MUST admit evidence for that assertion before classifying and persisting the fold. Evidence admission MUST cite (a) a stable state pointer (a commit SHA from `git rev-parse HEAD`; if a PR or branch reference is used, it MUST include the commit SHA under review) AND (b) file-and-line evidence resolving to exactly one of: (i) the assertion is accurate as authored — proceed to classify + persist the fold as written; (ii) the assertion is narrower or wider than the actual code state (e.g., decorator present but staff gate absent, or inline authN present but authZ absent) — rewrite the concern text to match the verified state before classify + persist; (iii) the assertion no longer holds because the underlying code has changed — the fold is void; do not persist. The evidence admission (stable state pointer + file+line citations + the (i)/(ii)/(iii) outcome) MUST be captured inline in the SIGN attestation immediately above the fold's classify + persist call. This rule EXTENDS PLAYBOOK-6.10.8 for the fold-authoring-turn scope; it does NOT waive the classification or persistence contract, and it complements PLAYBOOK-6.10.6 (which requires verify-before-implement for Cat A candidates) by requiring verify-before-persist for zoom-out folds.

### §2.2 Extended §6.10 commentary (informative)

Extends the closing sentence of the §6.10 commentary block to explain §6.10.9's proportionality: folds asserting no concrete code-state fact require no evidence admission; folds asserting a specific gap whose classification hinges on the assertion being accurate MUST admit evidence.

### §2.3 New §6.12 extension-point note (informative — Fold B forward-carry)

Added to §6.12 Extension points:

> - Fold-authoring evidence-admission helper — a pattern-matching helper that prefills stable-state-pointer + file+line prompts when a zoom-out fold's concern text includes gap-asserting phrases (e.g., "ungated", "no auth", "no error handling", "endpoint X is unprotected"). MAY be codified in a future MINOR amendment; trigger: 3+ SIGN cycles delayed >5min by manual verification of a §6.10.9 evidence admission, OR one SIGN blocked by absence of the helper. Corresponds to S2786 zoom-out Fold B (`future_trigger`), persisted in `logs/zoom_out_classifications.jsonl` at 2026-07-14T21:31Z under arc `n25_fold_authoring_hygiene_amendment`.

### §2.4 Appendix D version-chain row

Appended one row for v0.8.0 to `docs/ENGINEERING_PLAYBOOK.md` Appendix D — Version chain. Row records the amendment class (MINOR), parent (v0.7.0), rules added (PLAYBOOK-6.10.9), the two-trigger corpus with ledger row numbers, the T2/T4 dogfooding cycle, and the I-0302 candidacy re-slot forward to PLAYBOOK-6.10.10.

### §2.5 Frontmatter updates

- `version`: "0.7.0" → "0.8.0"
- `parent_version`: "0.6.0" → "0.7.0"
- `compatible_with`: appended "0.7.0"
- `ratified_date`: 2026-07-13 → 2026-07-14
- `branch_authored`: `playbook/v0.7.0-zoom-out-sign-discipline` → `playbook/v0.8.0-evidence-admission-fold-authoring`
- `git_tag`: `playbook-v0.7.0` → `playbook-v0.8.0`
- `prior_ratification`: v0.6.0 → v0.7.0 (with dates + tag)
- `authoring_sessions`: appended 2786
- `v0_8_0_authoring_session: 2786`, `v0_8_0_ratification_session: 2786`
- `rule_count`: 204 → 205
- `rules_added_v0_8_0: [PLAYBOOK-6.10.9]`
- Title H1: `# Donkey Betz Engineering Playbook v0.7.0` → `v0.8.0`

---

## §3. Two-trigger corroboration ledger

| # | Session | Fold text (as originally recorded) | What Rigby's tool_read revealed | Ledger classification | Ledger row |
|---|---|---|---|---|---|
| 1 | S2784 T2 SIGN Fold 4 (2026-07-14T18:06:59Z) | "Fold-authoring discipline drift — Fold 4 was recorded as 'no auth gating' when actual finding was 'no staff-only gating' (authN present, authZ absent)" | Original characterization overstated the gap; actual state was authN-present, authZ-absent. Fold text amended in-flight. | `same_pr_mitigatable` | row 31 |
| 2 | S2785 T1 SIGN Fold 1 (2026-07-14T20:55:21Z) | "Fold-authoring discipline drift RECURRED (2nd trigger). Initial audit said boardroom promote_decision was 'completely ungated' — Rigby tool_read revealed inline authN check with Token auth fallback at lines 2117-2135" | Original claim would have justified wrong-scoped mitigation (decorator gating that would break S887 Token codepath); actual state required inline helper extraction (C-lite design). Same phenomenon as trigger 1 at a different site. | `same_pr_mitigatable` | row 32 |

**Common failure mode:** at the moment of fold authoring (during SIGN attestation, before classify + persist), the concern text overstated the actual code state. In both triggers, the overstatement would have driven wrong-scoped mitigation work if it hadn't been caught by tool_read in the same or following SIGN turn.

**Rule design response:** rather than adding a "fold-authoring hygiene" checklist (which invites drift into optional style), the rule requires evidence admission — a stable-state-pointer + file+line citations + verified-state outcome captured inline before classify + persist. This treats fold persistence as a governance write that must be justified with evidence, not just a data-entry action.

---

## §4. Rigby joint SIGN cycle

### §4.1 T1 dispatch (author-side directive)

Sent to Rigby via `bash tools/pa_local.sh` with pin `pa-d065f1dfadac4cd4`. Directive included:
- Proposed rule text (T1 draft: "fold-authoring hygiene" framing, "at HEAD" verification)
- Slot proposal (6.10.9 per PLAYBOOK-10.7.5)
- Version proposal (v0.8.0 MINOR, correcting the CLAUDE-authored "v0.7.1 PATCH" label from `00-START-NEXT-SESSION.md`)
- Four explicit tool-grounded verification asks (ledger evidence, slot, version-history precedent, rule text review)
- Explicit PLAYBOOK-6.10.7 zoom-out ask ("what am I not seeing?")
- Explicit anti-rubber-stamp directive ("do NOT rubber-stamp; use tool_runs")

### §4.2 T2 attestation (Rigby)

- Items 1, 2, 3: AGREE with tool-grounded evidence (5 tool_runs total across T1: `repo_tool.read_file × 2`, `repo_tool.search × 2`, `zoom_out_tool.list × 1`)
- Item 4: **DISAGREE (F-BLOCKING).** "At HEAD" underspecified — HEAD can move after attestation; verification must be replayable. Required fix: replace with "at the repository state under review (current PR/branch state)" + require commit SHA + require cited lines. Non-blocking tighten-ups: (a) require attestation to include (i)/(ii)/(iii) + cited lines, (b) broaden examples beyond auth to avoid accidental narrowing.
- Zoom-out folds:
  - **Fold A** (`same_pr_mitigatable`): "Frame drift risk: amendment scoped as 'fold-authoring hygiene' when underlying defect is evidence-admission — durable fold ledger artifacts are persisted asserting substrate facts without a minimum evidence threshold. Hygiene framing invites drift into 'optional style' vs governance constraint." Mitigation: reframe rule text to require evidence admission (file+line + stable state pointer).
  - **Fold B** (`future_trigger`): "Burden/slowness risk without tooling nudge: rule may disproportionately slow close-cycle SIGNs by requiring manual repo inspection each time a fold claims a code gap. Trigger: 3+ SIGN cycles delayed >5min by manual verify OR one SIGN blocked by lack of helper."
- Persist blocked by tooling: Rigby's PA tool surface has read-only `zoom_out_tool.list`; no write action for `record_zoom_out_concern`. Handoff to Claude environment for persistence.

### §4.3 T3 persist (Claude environment)

Both folds persisted via `python manage.py record_zoom_out_concern` before D-verdict per PLAYBOOK-6.10.8:
- Fold A → row 35 (`same_pr_mitigatable`, entered_by `claude`, evidence_ref "S2786 T2 SIGN Fold A (Rigby)")
- Fold B → row 36 (`future_trigger`, entered_by `claude`, evidence_ref "S2786 T2 SIGN Fold B (Rigby)")

Ledger grew 34 → 36 rows during S2786. Counts by classification at S2786 close: 15 `same_pr_actionable` / 14 `same_pr_mitigatable` / 7 `future_trigger`.

### §4.4 T4 revised-text SIGN (author-side revision + Rigby verification)

Revised rule text addressed:
1. F-BLOCKING (Item 4): reframed as "evidence admission"; "at HEAD" replaced with "stable state pointer (commit SHA from `git rev-parse HEAD`; if PR/branch reference used, MUST include SHA under review)"; explicit requirement that stable-state-pointer + file+line + (i)/(ii)/(iii) outcome be captured inline in SIGN attestation.
2. Fold A same-PR mitigation: rule text and title switched from "hygiene" vocabulary to "evidence admission" throughout.
3. Fold B future_trigger: added §6.12 extension-point note referencing the pattern-matching helper as a future MINOR amendment candidate.
4. Broadened examples beyond auth: added "error-handling gap", "substrate location", "presence/absence of a specific block of code".
5. Complementarity with 6.10.6: explicit interaction note added.

Rigby T4 verdict:
- Item 4 (F-BLOCKING revisited): **AGREE** — evidence-admission framing + stable-state-pointer requirement resolves underspecification. One non-blocking micro-edit accepted: "PR/branch references MUST include the commit SHA under review" (incorporated as D5).
- Fold A landed: **AGREE** — reads as evidence admission, not hygiene.
- Fold B forward-carry: **AGREE** — §6.12 note matches v0.4.1 PATCH informative-only precedent (tool_read of Appendix D v0.4.1 row).
- New zoom-out: **DISAGREE (no new F-blockers).** One non-blocking caution: "any concrete claim about file contents" could over-trigger for trivial-but-time-expensive assertions. Tightened via "materially change classification/action path" predicate (incorporated as D6).

Anti-rubber-stamp gate: T1 = 5 tool_runs, T4 = 1 tool_run (v0.4.1 §6.12 precedent read). Both PASS.

---

## §5. Chris D-verdict

Chris ratified the revised rule text at S2786 with "yes ship it" (single-yes, following the joint Claude+Rigby agreement on corrected design). Per `feedback_claude_rigby_agree_first_chris_yes_no`, Claude and Rigby reached agreement on the F-BLOCKING resolution + both non-blocking refinements before Chris routing; Chris ratified rather than adjudicating.

---

## §6. Constitutional debt disposition

- **CD-open (from v0.7.0):** I-0302 three-PR pattern candidacy re-slotted forward to PLAYBOOK-6.10.10 (previously re-slotted to 6.10.9 by v0.7.0 provenance; the re-slot recurs because 6.10.9 was taken by this amendment per PLAYBOOK-10.7.5). No other CDs opened by this amendment.
- **CD-closed:** none discharged by this amendment (the two-trigger corpus was not previously a CD, but rather a Playbook amendment candidate surfaced at S2785 close).

---

## §7. Post-ratification bindings (PLACEHOLDER fields — filled at merge / cascade)

- `parent_version_commit_sha`: v0.7.0 merge SHA — to be filled at v0.8.0 ship PR merge from repo state
- `head_at_ratification`: filled at v0.8.0 ship PR merge SHA
- `close_pr`: filled at PR open
- `cascade_pr` + `cascade_pr_merge_sha`: filled at close-cascade PR merge
- `workspace_ratification_deliverable_id`: filled post-merge when workspace deliverable is minted

---

## §8. What this amendment teaches about how to do amendments

- **Two-trigger threshold with ledger-enumerable corpus is now demonstrated to work end-to-end.** The zoom-out ledger substrate (ratified S2777 as N22) was designed as longitudinal signal; S2786 is the first amendment where the corpus is enumerable directly by row number. This is the shape future §6.10.x amendments should take when the empirical basis is a ledger-recorded pattern.
- **T4 revision cycle after T2 F-BLOCKING is now a first-class move, not exception handling.** v0.7.0 had a 3-turn SIGN cycle (T1 tool-grounded, T2 zoom-out folds surfaced, T3 lock-in AGREE); v0.8.0 has a T1/T2/T3/T4 shape where T3 is Claude-side persistence + rule-text revision and T4 is Rigby verification of the revision. The two-and-a-half-turn cycle is what allows F-BLOCKING catches to drive substantive re-framing (hygiene → evidence admission) rather than surface tweaks.
- **Dogfooding at authoring extended to two dimensions.** v0.7.0 dogfooded 4 pre-D-verdict folds; v0.8.0 dogfooded 2 folds AND the amendment's own rule text was reshaped by the F-BLOCKING catch. When the rule under authoring can be applied to its own drafting cycle before ratification, that is the strongest possible corroboration signal.
- **Micro-edits from SIGN reviewer should be incorporated inline rather than routed to a second SIGN turn.** Rigby's T4 non-blocking micro-edits (stable-state-pointer tightener + over-trigger predicate) were incorporated directly into the D-verdict text without a T5 verification turn. Routing micro-edits back to SIGN would have added a ceremony round with no substantive review value.
