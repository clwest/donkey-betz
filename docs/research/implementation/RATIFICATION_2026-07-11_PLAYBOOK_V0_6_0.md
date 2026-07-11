---
title: "Engineering Playbook v0.6.0 Amendment Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2766
ratification_date: 2026-07-11
ratifier: chris
ratifier_verdict: "yes ship it as MINOR v0.6.0"
routing: rigby-pa-chat SIGN (watchpoints W1..W5, batched 3+2 per gpt-5.2 multi-fold optimization) + Chris D-verdict via Claude directly (single yes/no after joint Claude+Rigby recommendation)
amendment_scope: playbook-minor-v0.6.0
amendment_class: MINOR (per PLAYBOOK-10.5.1 — 1 addition, 0 modifications, 0 removals)
parent_version: v0.5.0
parent_version_git_tag: playbook-v0.5.0
parent_version_commit_sha: f7e40ddb
parent_version_ratification: RATIFICATION_2026-07-11_PLAYBOOK_V0_5_0 (workspace deliverable 4c322f48-3d0b-4e32-8a30-15a08400f887 in workspace a9a16593-e0a4-44dc-8256-efc65d524b3c)
proposed_version: v0.6.0
proposed_git_tag: playbook-v0.6.0
predecessor_candidacy: MEMORY.md `feedback_recycle_after_merge.md` (S2761 close observation 2026-07-11) + RATIFICATION_2026-07-11_ops_tool_recent_recycles.md §4.1 (three-cycle corroboration table)
head_at_amendment_draft: f2cba2917
head_at_ratification: PLACEHOLDER_FILLED_AT_MERGE
close_pr: PLACEHOLDER_FILLED_AT_MERGE
sign_sessions:
  - S2766 turn 1 — Rigby watchpoint-attestation SIGN batch 1 (W1..W3): PASS/AGREE on all three (constitutional MINOR reclass, new PLAYBOOK-7.4.4 placement, behavior-neutral wording)
  - S2766 turn 2 — Rigby watchpoint-attestation SIGN batch 2 (W4..W5): PASS/AGREE on both (close-ceremony scope with mechanical exemption list, evidence sufficient for MINOR under §14.2 default two-triggers threshold)
rules_added:
  - PLAYBOOK-7.4.4
rules_modified: []
rules_removed: []
rule_count_before: 201
rule_count_after: 202
chapter_activation: "Chapter 7 §7.4 extension — PLAYBOOK-7.4.4 added under existing partial-activation scope; §7.3 deferral scope unchanged"
supersedes: none
superseded_by: (open; not expected — ratification records are frozen historical envelopes)
frozen: true
workspace_id: a9a16593-e0a4-44dc-8256-efc65d524b3c
workspace_name: "Architecture & Research"
workspace_ratification_deliverable_id: PLACEHOLDER_FILLED_POST_MERGE
d_verdicts:
  - W1 Constitutional classification — MINOR v0.6.0 (NOT PATCH v0.5.1 as Chris pre-labeled in 00-START-NEXT-SESSION.md) — RATIFIED 2026-07-11 S2766
  - W2 Rule placement — new PLAYBOOK-7.4.4 sibling under §7.4 (NOT amend PLAYBOOK-7.4.1) — RATIFIED 2026-07-11 S2766
  - W3 Command specificity — behavior-neutral wording ("processes match HEAD SHA"); cite `make recycle-all` in evidence chain — RATIFIED 2026-07-11 S2766
  - W4 Rule scope — close-ceremony PRs only, with mechanical exemption for docs/frontend-only merges — RATIFIED 2026-07-11 S2766
  - W5 Evidence sufficiency — corroboration ladder (4 negative + 3 positive signals over 8 sessions) sufficient for MINOR under §14.2 default two-triggers — RATIFIED 2026-07-11 S2766
---

# Engineering Playbook v0.6.0 — Amendment Ratification Record

This file is the **workspace ratification envelope reflected in-repo** for the Engineering Playbook v0.6.0 MINOR amendment. It captures the amendment scope, the empirical corroboration ladder (§4), the Rigby watchpoint-attestation SIGN cycle (§5), Chris's D-verdict (§6), and the post-ratification bindings (§7). Append-only; do NOT edit after commit except to fill the reserved TBD fields (`head_at_ratification`, `close_pr`, `workspace_ratification_deliverable_id`).

---

## §1. Context

- **Amendment class:** MINOR (1 addition, 0 modifications, 0 removals) per PLAYBOOK-10.5.1.
- **Session:** S2766 (single-session author + SIGN + ratify + ship; smallest amendment scope shipped to date).
- **Head at amendment draft:** `f2cba2917` (post-S2765 merge PR #3154).
- **Ratifier:** Chris ("yes ship it as MINOR v0.6.0" at S2766, following joint Claude+Rigby recommendation).
- **Routing:** Rigby PA chat surface via pin `pa-3811268cfce14a49` (S2766 scope: recycle-after-merge codification).
- **Predecessor:** memory rule `feedback_recycle_after_merge.md` (recorded S2761 close 2026-07-11) + operational corroboration across S2762→S2765 (`RATIFICATION_2026-07-11_ops_tool_recent_recycles.md` §4.1 three-cycle table).
- **Precedent broken:** START-NEXT-SESSION.md at S2766 open pre-labeled this amendment as "first PATCH amendment to v0.5.0 → v0.5.1." Constitutional review (§5.1 W1) determined a new [GR] rule cannot be a PATCH per PLAYBOOK-10.4.1. Amendment reclassified to MINOR v0.6.0 before draft.

---

## §2. Ratified amendment scope

### §2.1 New rule PLAYBOOK-7.4.4

Added under existing §7.4 Close-ceremony delivery discipline (Chapter 7 partial-activation scope introduced at v0.5.0). Full rule text:

> **[GR] PLAYBOOK-7.4.4** Every close-ceremony PR (phase close or arc close per PLAYBOOK-7.4.1) MUST include a post-merge step that recycles local worker processes so that they match HEAD SHA before the next session opens. The recycle step is invoked *after* the merge advances HEAD, not merely before pre-merge E2E verification. A close-ceremony PR MAY waive the post-merge recycle step ONLY when the merge diff touches none of: `*.py` files, `pyproject.toml` / `requirements*` / `Pipfile*`, `Dockerfile*` / `Procfile` / `railway.toml`, Django `settings.py` or `settings/`, `migrations/`, or Celery / worker configuration. The waiver, when taken, MUST be recorded in the close-doc SIGN log alongside the exemption reason.

### §2.2 Body doc updates

- Frontmatter version bump `0.5.0` → `0.6.0`; `parent_version` `0.4.1` → `0.5.0`; `compatible_with` appends `"0.5.0"`; `rule_count` 201 → 202; new `rules_added_v0_6_0: [PLAYBOOK-7.4.4]` field; new `v0_6_0_authoring_session` + `v0_6_0_ratification_session` fields (both S2766); `prior_ratification` block updated with v0.5.0 metadata.
- Body title `v0.5.0` → `v0.6.0`.
- Chapter 7 frontmatter — `Last substantive change` updated `v0.5.0` → `v0.6.0`; `Status` line extended to note v0.6.0 §7.4 extension.
- §7.4 preamble revised to say "codifies four rules" (was three) and to add the S2758–S2765 corroboration provenance sentence.
- Appendix D — new v0.6.0 row appended.

---

## §3. What was NOT changed

- No existing rule modified. PLAYBOOK-7.4.1 / 7.4.2 / 7.4.3 text unchanged; §7.5 and §7.6 untouched; Chapters 0–6 and 8–10 untouched.
- No evidence class or statement class added. No manifest additions (rule cites existing evidence corpus + new S2766 envelope + memory rule).
- No canonical authority reclassification.
- No frontmatter `compatible_with` removal.

---

## §4. Corroboration ladder (empirical basis for MINOR ratification)

The rule was surfaced by a memory-recorded operator observation at S2761 close (`feedback_recycle_after_merge.md`). Between S2758 and S2765, seven independent data points accumulated:

### §4.1 Negative signals (pre-convention — recycle before E2E only)

| Session | Signal | Handoff evidence |
|---|---|---|
| S2758 open | STALE_BOTH | `docs/handoffs/SESSION_2758_*.md` next-session-open diagnosis |
| S2759 open | STALE_BOTH | `docs/handoffs/SESSION_2759_*.md` next-session-open diagnosis |
| S2760 open | STALE_BOTH | `docs/handoffs/SESSION_2760_*.md` next-session-open diagnosis |
| S2761 open | STALE_BOTH | `docs/handoffs/SESSION_2761_*.md` next-session-open diagnosis (memory-rule authored at close) |

### §4.2 Positive signals (post-convention — recycle also AFTER merge)

| Session | Signal | Handoff evidence |
|---|---|---|
| S2763 open | FRESH · SHA-match | `docs/handoffs/SESSION_2763_*.md` next-session-open verdict |
| S2764 open | FRESH · SHA-match | `docs/handoffs/SESSION_2764_OPS_HEALTH_TILE_V2_SLO_RATIFIED.md` next-session-open verdict |
| S2765 open | FRESH · SHA-match | `docs/handoffs/SESSION_2765_OPS_TOOL_RECENT_RECYCLES_RATIFIED.md` next-session-open verdict |

### §4.3 Aggregate

- 7 empirical data points spanning 8 sessions (S2758–S2765) over 2 days.
- Same operator (Chris), same machine, same repo — narrow but deep; single-operator context matches all v0.4.x / v0.5.0 ratification history.
- PLAYBOOK §14.2 default two-trigger threshold satisfied at cycle 2 (S2764 open); triple-confirmed at cycle 3 (S2765 open).
- Cross-arc corroboration deferred (see §7 forward-carry) because single-operator single-machine context is native to Donkey Betz per `project_single_user_pre_prod_operating_context`.

---

## §5. Rigby SIGN cycle

### §5.1 Batch 1 — Watchpoints W1–W3

Dispatched via wrapper pin `pa-3811268cfce14a49` at S2766 P0.

**W1 — Constitutional classification (PATCH vs MINOR).**
- Claude lean: MINOR v0.6.0 (constitutional constraint per PLAYBOOK-10.4.1 forbids rule introduction as PATCH).
- Rigby: PASS/AGREE — "Codifying 'recycle-after-merge' is new normative requirement (new [GR] or a material change to an existing rule), so PATCH is constitutionally disallowed → MINOR v0.6.0."

**W2 — Rule placement (7.4.4 new vs 7.4.1 amend).**
- Claude lean: A (new PLAYBOOK-7.4.4 sibling under §7.4). Reasoning: §7.4.1 is scoped to PR-bundle shape; recycle is a post-merge operational step run outside the PR — worse semantic fit under B. Backward-compat precedent favors add-over-modify.
- Rigby: PASS/AGREE — "Operational post-merge hygiene is a different semantic category than 'what ships inside the PR,' so A (new 7.4.4) is cleaner, more discoverable, and aligns with the backward-compat 'prefer add over modify' precedent."

**W3 — Command specificity (explicit `make recycle-all` vs behavior-neutral).**
- Claude lean: B (behavior-neutral). Reasoning: Playbook is constitutional; renaming the Make target later shouldn't require another amendment.
- Rigby: PASS/AGREE — "Playbook should state the behavioral invariant (processes match HEAD SHA) and keep tool-specific commands in evidence/implementation notes to avoid churn on future renames."

### §5.2 Batch 2 — Watchpoints W4–W5

Dispatched immediately after batch 1 PASS.

**W4 — Rule scope / exemptions.**
- Claude lean: close-ceremony PRs only; waiver when neither Python code nor Django settings/migrations touched.
- Rigby: PASS/AGREE with refinement — extended exemption list to a mechanical file-path enumeration: no changes to `*.py`, `pyproject.toml`/`requirements*`, `Pipfile*`, `Dockerfile*`, `Procfile`, `railway.toml`/deploy config, Django `settings.py`/`settings/`, `migrations/`, or Celery/worker config. Rule text adopts Rigby's mechanical list verbatim.

**W5 — Evidence sufficiency for MINOR.**
- Claude lean: sufficient (7 data points > §14.2 two-triggers default; exceeds any prior v0.4.x/v0.5.0 rule's corroboration budget).
- Rigby: PASS/AGREE — "Sufficient for MINOR ratification under §14.2: you have a clear before/after intervention with 4 negatives → 3 positives in tight time, same environment, and it meets/exceeds the platform's historical corroboration bar for [GR] rules."

### §5.3 SIGN verdict

**All 5 watchpoints PASS/AGREE. Joint Claude+Rigby recommendation reached before Chris routing per `feedback_claude_rigby_agree_first_chris_yes_no`.**

---

## §6. Chris D-verdict

Sequence:

1. **Session-open candidate selection (S2766):** Chris selected N5 from the S2766 standing candidate menu (Playbook amendment for recycle-after-merge codification). Selection consistent with Claude's top lean (starred as ⭐ recommendation).
2. **Joint recommendation card:** Claude presented all 5 watchpoint decisions with joint Claude+Rigby PASS, including the flagged constitutional mismatch on W1 (Chris pre-labeled PATCH v0.5.1; joint recommendation is MINOR v0.6.0).
3. **D-verdict:** "yes ship it as MINOR v0.6.0."

**Effect:** Rule count 201 → 202. §7.4 grows from three rules to four. First MINOR amendment following v0.5.0. First amendment whose class was corrected (PATCH → MINOR) via SIGN cycle prior to draft. Sets the precedent for "constitutional constraint overrides operator pre-labeling" when the two conflict.

---

## §7. Provenance chain

- **Predecessor sessions:** S2758–S2761 (negative signals, memory rule authored S2761 close) → S2762–S2765 (positive signals, corroboration ladder complete S2765 close) → **S2766 (codification into Playbook)**.
- **Reference implementations:**
  - `Makefile:91-94` — `recycle-all` target (JSONL emitter added at S2765 for observability, not for compliance; `make recycle-all` invocation itself is what the new rule requires).
  - `logs/recycle_events.jsonl` — first-party operator-action timeline (S2765 substrate).
  - `core/services/td_handlers_ops.py::_ops_recent_recycles` — PA tool surface (S2765 substrate).
- **Memory rules applied:**
  - `feedback_recycle_after_merge.md` (originating rule)
  - `feedback_claude_rigby_agree_first_chris_yes_no` (workflow discipline for the D-verdict routing)
  - `feedback_gpt5_stalls_on_multifold_design_prompts` (SIGN batching 3+2 instead of 5-fold)
  - `feedback_local_truth_no_production` (post-merge dogfood recycle as the "shipped" gate)
- **Playbook rules exercised in the ship:**
  - PLAYBOOK-7.4.1 (this PR is itself a single-PR close bundle — amendment doc + ratification envelope + handoff + cascade)
  - PLAYBOOK-7.4.2 (no substrate PRs interleaved on the Playbook doc)
  - PLAYBOOK-7.4.3 (cascade output COMBINED with close-doc PR)
  - PLAYBOOK-7.4.4 (dogfooded at merge — `make recycle-all` runs after PR merge advances HEAD)
  - PLAYBOOK-7.6.1 (SIGN structured as W1..W5 watchpoint-attestation, per-watchpoint PASS/AGREE recorded above)
  - PLAYBOOK-10.5.3 (MINOR amendment full SIGN cycle discharged)
- **Forward-carry:** cross-arc corroboration (e.g., when the platform gains a second operator or a CI job that merges close-ceremony PRs autonomously) is a candidate for a future MINOR amendment to broaden PLAYBOOK-7.4.4 scope beyond `close-ceremony PRs`. Not urgent — the constitutional single-operator context is durable through the pre-prod window.

---

## §8. Post-ratification bindings

- **Docs cascade** — 4-step (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed`) plus `build_docs_provenance`. Runs at close per PLAYBOOK-7.4.3 COMBINED cadence.
- **Workspace mirror** — this envelope mirrored to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research) as `deliverable_type='ratification_record'`, `category='governance'` per twin-canonical-representation rule.
- **Content mirror** — the Playbook body doc itself (as of v0.6.0) mirrored as content deliverable in the same workspace.
- **Handoff** — `docs/handoffs/SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md`.
- **CLAUDE.md** — L7 anchor refreshed to reference v0.6.0 as latest ratified version with v0.5.0 preserved in ancestry chain.
- **Recycle dogfood** — `make recycle-all` invoked after PR merge (satisfies the very rule this envelope ratifies).
- **Memory** — MEMORY.md entry for `feedback_recycle_after_merge.md` updated to reference this ratification (rule now constitutional, not just operator memory).

---

## §9. Limitations

- **Local pass = shipped** per `feedback_local_truth_no_production`. No production observation window. Dogfood via `make recycle-all` at close = the deploy step.
- **Waiver enforcement is manual** — the exemption clause requires operator to log the waiver reason in the close-doc SIGN log; not machine-enforced. Automation candidate for a future PATCH sidecar (evidence sidecar-refresh — non-normative).
- **Handoff-file naming** — `SESSION_2758_*.md` through `SESSION_2761_*.md` and `SESSION_2763_*.md` slugs are cited generically because negative-signal handoffs pre-date the tile ratifications and don't share a common slug convention; the cited handoffs exist under their session-specific slugs in `docs/handoffs/`. Verifier should treat the citations as "the handoff whose header slug carries the session number" rather than exact filename matches.

---

*Frozen at S2766 ratification. Do not edit except to fill reserved PLACEHOLDER fields.*
