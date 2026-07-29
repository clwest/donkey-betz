# Session 3034 — Rejection broadcast symmetry + first PLAYBOOK-7.7.5 activation

**Date:** 2026-07-28 · **HEAD at close:** `723115151` (PR #3757 merged) + wrapper pin bump cascade

## What shipped

**PR #3757 (`723115151`) — `feat(s3034): rejection broadcast symmetry`.** Closes the deprecation-side gap of the S3026 → S3032 canonical-promotion arc. Promotion emits `canonical_decision_promoted` across 6 paths via a single-source-of-truth helper; rejection was silent across 4 paths. S3034 adds the parallel structure so both terminal lifecycle transitions emit lifecycle broadcasts through a single helper.

**This is the first real-world exercise of PLAYBOOK-7.7.5** (ratified at S3033 in Playbook v0.11.0 — the class-scoped mandatory A2 sweep rule for drift/hardening intents). Rigby T1 SIGN sweep discovered a 4th rejection production site (`update_gate_status` action='decline') that the initial Verified Premises + Artifact Map missed. **Rule earned its keep on first activation** — same near-miss shape as S3029's `tasks_ops` 4th-site catch on the promotion side.

### Artifact Map delivered

- **NEW** `AgentDecisionSummary.reject(rejected_by='human') -> bool` in `core/models_unified_system.py:18218` — mirrors `promote_to_canonical()`: early-exit if already rejected (returns False); `save(update_fields=['status', 'updated_at'])` containment. No new fields.
- **NEW** `emit_canonical_rejection_broadcast(decision, *, request_id=None) -> bool` in `core/services/canonical_decision_broadcast.py:100` — publishes `canonical_policy_rejected` envelope + `canonical_decision_rejected` payload to `agent_learning` Redis channel with keys identical to promotion (`schema_version:1`, `decision_id`, `topic`, `decision_type`, `summary`, `participants`, `agents_involved` S657 back-compat alias). Increments `canonical_decisions:rejected_total` counter. Best-effort, non-fatal.
- **REVISE 4 production paths** to call `did_reject = decision.reject(...)` then gate broadcast on `did_reject`:
  1. `core/views_agent_learning.py:reject_decision` (single view).
  2. `core/views_agent_learning.py:bulk_reject_decisions` (bulk view — converted `.update()` to per-row loop matching `bulk_promote_decisions` shape; adds `broadcasts_succeeded`/`broadcasts_failed` counters).
  3. `core/services/td_handlers_agents.py` PA tool `boardroom` action `reject_decision`.
  4. `core/views_agent_learning.py:update_gate_status` action='decline' (the **4th-site DISCOVERY** — Rigby T1 sweep Pushback #1 `same_pr_actionable`).

Docstring rewrite on `core/services/canonical_decision_broadcast.py:1-49` names the meta-invariant ("any production code path transitioning an AgentDecisionSummary to a terminal lifecycle state MUST emit the matching lifecycle broadcast via a helper defined here") and enumerates the 6 promotion callers + 4 rejection callers.

## Results

| Metric | Actual |
|---|---|
| PR #3757 diff | +454/-23 (5 files: 1 model + 1 broadcast helper + 1 PA handler + 1 view file + 1 new test) |
| S3034 test suite | **7/7 pass in 0.162s** |
| Canonical-lifecycle regression bundle (12 files) | **66/66 pass in 4.760s** (baseline 61/61 pre-S3034 across 11 files; +5 new = 66) |
| Post-merge `make recycle-all` | clean, `sha=72311515193f` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**19th consecutive session.** Verify pass at T1: read 3 rejection-path sites + broadcast helper module + `promote_to_canonical` reference method + grep for existing `def reject` collisions before dispatching Rigby T1 SIGN.

**The real Cycle 1A win here was Rigby's A2 (which was actually T1 in this arc):** her tool-grounded 4th-site sweep caught the gate-decline path that my initial 3-site enumeration missed. Same distinct signal as S3029 — verify-before-build is upfront author work; the PLAYBOOK-7.7.5 mandatory sweep catches adjacent silent bugs during SIGN.

## Rigby SIGN quality this session

**1 substantive T1 SIGN + 1 substantive A2 SIGN with full PLAYBOOK-7.7.5 sweep.** **20-session zero-hallucination Rigby SIGN streak** (S3010 → S3034).

### T1 SIGN summary

**5/5 dimensions AGREE, 1 F-BLOCKER (D2 shape signature)**:

- **D1 Scope-for-1-session — AGREE.** Ship `.reject()` model method in this arc; multiple mutation sites justify convergence.
- **D2 Shape-signature adequacy — DISAGREE.** Initial signature (`decision.status = 'rejected'`) missed relationship-deref writes. Mitigation: widened to include `gate.decision.status = 'rejected'` shape; added 4th site to Artifact Map. `same_pr_mitigatable`.
- **D3 Bulk endpoint semantics change — AGREE** with counter-reporting caution.
- **D4 Payload shape — AGREE** (mirror promotion).
- **D5 Naming `reject()` — AGREE** (rejection isn't limited to canonical).

Zoom-out folds persisted BEFORE Chris D-verdict (learning from S3033 §6 procedural note):
- Pushback #1 (4th-site coverage gap) — `same_pr_actionable`.
- Pushback #2 (KnowledgeTransfer coupling) — `future_trigger`.

### A2 SIGN summary — first PLAYBOOK-7.7.5 activation

Rigby ran the mandatory 4-dimension sweep with tool_runs inline per PLAYBOOK-7.7.2:

- **(i) Other production sites of same shape signature** — CLEAN (0 orphan writes). Verified via `repo_tool search "status\s*=\s*['\"]rejected['\"]"` + `repo_tool search "update\(.*status\s*=\s*['\"]rejected['\"]"` (0 matches — old `.update()` shape gone). All 4 confirmed sites route through `.reject()`.
- **(ii) Adjacent classes on same table/model** — AGREE bounded. Model has `superseded`, `experiment`, `review` status values but they're not currently declared terminal. `future_trigger` fold recorded — if a future arc redeclares any as terminal, a new broadcast helper + PLAYBOOK-7.7.5 sweep will be needed.
- **(iii) Downstream consumers** — CLEAN. Grep at HEAD verified no in-repo consumer subscribes to `agent_learning` + filters on `canonical_policy_created` envelope type. No consumer breaks. `future_trigger` fold recorded.
- **(iv) Tests locking in old behavior** — CLEAN. Read `test_s3023_bulk_agent_decision_mutation.py:125-184` verified all 6 BulkRejectDecisionsMutationTests assert only specific keys (`count`, `success`, 400 status) with no exact-dict-equality. Additive `broadcasts_*` fields don't break assertions. `same_pr_mitigatable` fold recorded (verified via targeted grep + test-run).

Initial A2 was partial (Rigby explicitly flagged (iii) + (iv) as unverified). Claude ran the missing sweeps + persisted findings to ledger + routed evidence back to Rigby, who then flipped the partial DISAGREE to full **AGREE** with tool_grounded evidence for both dimensions.

## Folds

### Same-PR resolved

- **T1 Pushback #1 `same_pr_actionable`** — 4th site added to Artifact Map + shape signature widened. RESOLVED.
- **A2 Pushback #2 `same_pr_mitigatable`** — bulk response additive fields verified test-safe. RESOLVED via evidence.

### Forward carries — `future_trigger`

- **T1 Pushback #2 (KnowledgeTransfer coupling risk)** — if the multi-session KnowledgeTransfer realignment arc opens and needs a different rejection payload shape, revisit `schema_version` bump + subscriber gating story.
- **A2 Pushback #1 (subscriber wire-contract fragility)** — no in-repo subscribers today; revisit if/when the first subscriber lands with strict envelope-type filtering.
- **A2 Dimension (ii) adjacent-axis (superseded/experiment)** — if a future arc redeclares any of AgentDecisionSummary's non-terminal statuses as terminal, run a new PLAYBOOK-7.7.5 sweep.

### Meta-fold — PLAYBOOK-7.7.5 first-activation observation

**The rule caught what it was designed to catch on the very first activation** — a 4th silent production site (`gate.decision.status = 'rejected'` via OneToOneField relationship-deref) that a narrower verify-before-build would have missed. This is a same-shape signal as S3029 (Fold C 1st-cycle DISCOVERY). If a 2nd similar in-wild PLAYBOOK-7.7.5 activation catches an adjacent site, that's corroborating evidence for the rule's value. Recorded as observational fold; watch for 2nd trigger.

## Forward carries

### Carried from S3033 (STATUS PRESERVED)

- **S3033 Fold B `procedural observation`** — ledger persistence timing. Fixed this session: all folds persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8. First trigger discharged; watch for 3rd occurrence to determine whether a sequencing sub-rule is warranted.

### Carried from S3032 (STATUS PRESERVED)

- **S3030 prod deploy carry** — still open: run `backfill_canonical_drift --apply` against Railway prod when convenient.
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion pattern. Unchanged this session.
- **S3031 Fold A `2nd trigger` (bool-return semantics)** — carried unchanged; `did_reject` this session is a 2nd instance of the `did_X` pattern (following `did_promote`), elevating this fold to potentially-3rd-trigger. Watch for a 3rd surface (e.g. `did_deprecate`) to codify.
- **S3031 Fold B `informational` (spy fragility)** — carried unchanged.

### Carried from S3029 → S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — evidence-driven investigation. S3034 A2 SIGN adds additional supporting evidence (6-tool_run sweep + shape-signature widening at T1).
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment (multi-session; standing carry).

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.11.0 (this session is first real-world PLAYBOOK-7.7.5 exercise). No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (S3034 planned end-to-end from S3033 open recommendation).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive T1 SIGN + 1× substantive A2 SIGN, both tool-grounded (T1: 8 `repo_tool` operations; A2: 8+ `repo_tool` operations across 4 dimensions).** Zero rubber-stamp. **20 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied at Phase 5 ("do we lose anything?" + "is it more work later?" + ≤1 decision).
- **Class-scoped A2 sweep (PLAYBOOK-7.7.5):** **FIRST REAL-WORLD ACTIVATION.** Rule performed as designed — sweep caught 4th-site coverage gap that verify-before-build alone would have missed.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` post-merge; `sha=72311515193f` recorded.
- **Fold classification (PLAYBOOK-6.10.8):** 5 folds this session (2 same_pr_actionable/mitigatable RESOLVED same-envelope + 3 future_trigger persisted). All persisted BEFORE Chris D-verdict.
- **Verify-before-build (Cycle 1A):** **19th consecutive session.**

## Wrapper pin note

Session-open pin was `pa-21c85ada63514ffb` (minted at S3033 close). Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.

## Two-session terminal note

S3033 (Playbook v0.11.0 amendment ratifying PLAYBOOK-7.7.5) + S3034 (first real-world PLAYBOOK-7.7.5 activation) shipped in the same terminal session per Chris directive at S3033 close ("start the bulk_reject_decisions arc"). Total shipped: 3 PRs across 2 sessions in one terminal (PR #3755 v0.11.0 amendment, PR #3756 v0.11.0 cascade, PR #3757 S3034 feature). This is the 4th single-terminal multi-session close in the S3026→S3034 arc series. Pattern: a governance amendment ratified in one session and immediately exercised in the next demonstrates that the rule is actionable, not aspirational — a form of dogfooding on the constitutional level.
