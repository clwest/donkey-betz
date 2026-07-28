# Session 3013 — U1 Governance Batch Triage (fresh engineering + bundled defect fix)

**Date:** 2026-07-28
**HEAD at close:** `ecfcf8d1a` (PR #3706 merged) + docs cascade PR (this file + 00-START refresh + INDEX regen + wrapper pin bump)
**Session shape:** Fresh engineering (Option A). Single-PR arc. Break from 5 consecutive envelope/substrate sessions (S3008 → S3012) per Chris bias-engineering rule.

---

## What shipped

### PR #3706 — `feat(s3013): U1 — Governance batch triage UI + BulkAttentionDecideView defect fix` (`ecfcf8d1a`)

**Two changes bundled per PLAYBOOK-6.10.8 `same_pr_mitigatable`.**

**Frontend enhancement (`frontend/src/pages/workspace/tabs/GovernanceTab.tsx` +250 lines, `frontend/src/lib/api.ts` +15 lines):**
- Batch selection: checkbox column on each Pending Decision card (with `stopPropagation` to preserve existing card-click → `DecisionDetailModal` behavior).
- Header controls: "Select all visible" / "Deselect all" + selection counter.
- Sticky action bar when ≥1 selected: `[Approve N]` `[Ignore N]` `[Reject N]` with per-action `Loader2` spinner (matches on `bulkDecideMutation.variables?.decision`).
- Filter chips: urgency (all/critical/high/medium/low) + item_type (all/decision/alert/opportunity). Filter state doesn't clear selection (selection tracked independently).
- Confirm dialog for Reject (terminal action) — Rigby A1 SIGN guardrail against fat-finger mass-reject; names "Human Attention Items" explicitly for semantic clarity.
- Sublabel "Actions apply to Human Attention Items" — Rigby zoom-out mitigation for semantic mismatch concern.
- Partial-failure handling in `onSuccess`: checks `response.data?.success === false` (error toast) + `count < requested` (info toast with skipped count).
- Reuses existing `FeedbackMessage` toast pattern (matches `runRemediationMutation` shape).

**Backend defect fix (`core/views_human_interface.py` +31 -14 lines):**

Rigby A2 SIGN STRENGTHEN caught two latent defects in `BulkAttentionDecideView` (Session 942) that S2785 auth-regression tests never exercised (they only covered blocking, not mutation path):

1. Wrote invalid status values: `'approved'` and `'rejected'` are NOT in `HumanAttentionItem.STATUS_CHOICES` (which allows only `pending`/`viewed`/`acted`/`deferred`/`ignored`/`expired`/`watching`/`verified`). Model contract violation.
2. Wrote to nonexistent field: `.update(handled_at=now)` — `handled_at` does not exist on `HumanAttentionItem` (canonical field is `decided_at`). Would raise `FieldError` on first authenticated invocation.

Fix: added `_BULK_DECISION_TO_MODEL` class-level mapping matching `record_decision()` canonical semantics:
- `'approved'` → `(decision='approve', status='acted')`
- `'rejected'` → `(decision='reject', status='acted')`
- `'ignored'` → `(decision='ignore', status='ignored')`

Applied via `queryset.update(status=model_status, decision=model_decision, decided_at=now)`. API contract preserved (still accepts past-tense enum from UI); only persistence changed.

**Test suite (`core/tests/test_s3013_bulk_attention_decide_mutation.py` +156 lines, 8 tests):**

Mutation-path coverage that S2785 didn't provide. 8/8 PASS in 1.4s.

1. `test_approved_maps_to_acted_status_and_approve_decision` — 3 items, POST bulk-decide, assert `status=STATUS_ACTED` + `decision=DECISION_APPROVE` + `decided_at` NOT NULL.
2. `test_rejected_maps_to_acted_status_and_reject_decision` — same shape for reject.
3. `test_ignored_maps_to_ignored_status_and_ignore_decision` — asserts `status=STATUS_IGNORED` + `decision=DECISION_IGNORE`.
4. `test_persisted_status_values_are_in_model_status_choices` — **direct regression assertion** that `status ∈ STATUS_CHOICES` (would have caught pre-fix bug).
5. `test_invalid_decision_returns_400` — imperative form ('approve') rejected.
6. `test_invalid_json_returns_400`.
7. `test_only_pending_items_mutated` — already-acted item not re-decided.
8. `test_cross_user_items_untouched` — user-scope preserved.

---

## Cycle 1A verify-before-build win

Original U1 spec assumed a new bulk endpoint would need to be built. **Rigby's tool_runs during discovery surfaced `BulkAttentionDecideView` already existed at Session 942** — the endpoint has a URL + tests + method decorator gates. Cut the PR scope roughly in half (from 2-file backend+frontend to frontend + defect-fix). Then during A2 SIGN, Rigby's tool-grounded read caught the latent status-enum defect in that same endpoint — turning "reuse existing thing" into "reuse + fix bug in the thing you reused" but within the same PR shape.

This is the pattern Chris's `feedback_cycle_1a_verify_before_build` rule targets. Two-turn savings this session: (1) skipped writing a redundant endpoint, (2) surfaced a latent 500 that would have shipped on first bulk-approve click.

---

## Rigby SIGN quality this session

**5 substantive SIGN cycles this session.** All tool-grounded. **Zero hallucination triggers** (matches S3010 + S3011 + S3012 pattern — **4 sessions continuous**).

Cycle summary:
1. **Session-open handshake** — 3 fresh engineering candidates surfaced (2 substrate + 1 user-facing correction after Claude flagged bias-engineering rule). Result: joint recommendation U1.
2. **Discovery** — Rigby repo_tool + kb_tool surfaced `GovernanceTab.tsx` exists, `BulkAttentionDecideView` exists, `_get_pending_decisions` shape.
3. **A1 SIGN** — APPROVE clean with 4 non-blocking guardrails (all adopted): confirm-Reject dialog, mutation-in-flight disable, partial-failure handling, semantic-clarity sublabel.
4. **A2 SIGN (first pass)** — STRENGTHEN caught bulk endpoint status-enum defect + nonexistent `handled_at` field. Prevented shipping a UI that would 500 on first click.
5. **A2 SIGN (re-verify after fix)** — APPROVE clean with optional 9th test suggestion (non-blocking, forward-carry).

---

## Folds (pattern evidence, not automatic escalation)

### Fold A `1st trigger` — Cycle 1A verify-before-build saved half a PR

Original discovery assumed `BulkAttentionDecideView` would need to be built. Rigby's search caught it exists. Turned "build new endpoint" into "reuse + fix latent bug in existing endpoint." Pattern: **when spec expects to build a new thing, spend one Rigby tool_run first to confirm nothing similar already exists.** Watch for 2nd trigger — likely already at 2nd (Chris's rule was ratified because it kept happening).

### Fold B `1st trigger` — S2785 auth-regression contract has a mutation-path blind spot

`test_decision_approve_auth_regression_2785.py` covers auth blocking for 19 endpoints (15 `/api/human/*` + 4 boardroom) but doesn't test the actual mutation path for any of them. `BulkAttentionDecideView` would 500 on first authenticated call because tests never exercised the write path. **Ledger candidate:** systematic mutation-path smoke-test sweep of the S2785 auth-inventoried endpoints. Watch for 2nd instance.

### Fold C `informational` — Rigby's web_fetch_tool auth context is unclear

Rigby's live probe of `/api/human/attention/{id}/` returned 404 because her `web_fetch_tool` likely goes through unauthenticated (or with a non-chris user). Made the A2 SIGN more painful than it needed to be — Rigby couldn't distinguish "endpoint broken" from "her tool can't reach it." **Ledger candidate:** clarify web_fetch_tool auth context OR add authenticated-as-chris probe capability. Rigby Tool Gap Ledger workspace deliverable (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`).

### Fold D `future_trigger` — Bulk endpoint still uses Family B envelope shape

`BulkAttentionDecideView` returns `{'success': True/False, 'error': '...'}` shape — the Family B pattern that T-ENVELOPE arcs retired everywhere else. Not migrated in this PR (out of scope; T-ENVELOPE arc closed at S3012). **Candidate for post-T-ENVELOPE cleanup arc** if a T-ENVELOPE-4 opens. Same applies to the 32 grandfathered sports odds sites.

### Fold E `informational` — Bulk endpoint decision-string enum is inconsistent with model enum

Bulk API accepts past-tense (`'approved'`/`'ignored'`/`'rejected'`) while model uses imperative (`'approve'`/`'reject'`/`'ignore'`). Fixed via mapping in this PR. Taxonomy could be unified in a future clean-up but not urgent — the two enums serve different purposes (API contract vs model DECISION_CHOICES).

---

## Forward carries

**New from S3013:**

- **Rigby non-blocking A2 suggestion:** 9th test asserting `governance_view.pending_decisions[].id` → `HumanAttentionItem.id` couples the two endpoints tightly. ~10-line addition. Would prevent silent drift if `_get_pending_decisions()` ever added a non-`HumanAttentionItem` source (e.g. `AgentDecisionSummary`).
- **Batch Defer capability:** UI has 3 actions (Approve/Ignore/Reject). Batch Defer would require a new bulk endpoint OR per-item iteration through `/api/human/attention/{id}/defer/`. Parking-lot.
- **Attention Items separate section:** discarded during discovery (pending_decisions ALREADY IS the HumanAttentionItem list — a second section would double-render). Revisit only if source union changes.
- **Fold A `1st trigger`** — verify-before-build saved half a PR (see above).
- **Fold B `1st trigger`** — S2785 auth-contract has mutation-path blind spot (see above).
- **Fold C `informational`** — Rigby web_fetch_tool auth context clarification (ledger candidate; see above).

**Carried from S3012 (STATUS PRESERVED):**

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT. ~11 handlers, ~600 lines. Needs Chris ratification.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py. ~1 session.
- **Fold A `1st trigger`** (S3012) — S3011 audit counted grep matches, not real callers. Watch for 2nd trigger.
- **Fold B `1st trigger`** (S3012) — Migration-script text-replacement without line-offset tracking. Ledger deliverable `505dbdc1-9184-478a-b186-1f9e3912807a`.
- **Fold C `informational`** (S3012) — `@superuser_required` decorator is a Family B → Family E migration candidate. Separate T-slot arc — possibly T-ENVELOPE-4.
- **Fold B `5th trigger imminent → assessed at S3013 open`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne request path). S3013 used `make recycle-all` (broader superset) — counts as event but doesn't necessarily satisfy Fold B's specific signal about which command to use. Assess again when next Daphne-only issue surfaces.

**Carried from S3011 and earlier — see `docs/handoffs/SESSION_3012_T_ENVELOPE_3_COMPLETE.md` for the full carry-forward list.**

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0007. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× clean Flow B spec→ship this session** (A1→implement→A2-STRENGTHEN→fix→re-A2→ship→recycle-all post-merge).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **5× substantive Rigby SIGN cycles.** Zero hallucination triggers. **4 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session was arc-kickoff-only (approved U1). All PR-level shape decisions handled Claude ↔ Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` used both pre-merge (for live smoke) and post-merge (constitutional).
- **Verify-before-build (Cycle 1A):** paid off big this session. See Fold A.
- **Fold classification (PLAYBOOK-6.10.8):** backend defect fix classified `same_pr_mitigatable` — bundled into same PR because active scope was increasing the bug's blast radius.

---

## Chris directive transcript

**T1 (session open):** Chris typed "Please orient yourself and begin with Rigby." Claude ran context-kit orient, absorbed 00-START/MEMORY/CLAUDE, ran `session_lifecycle close --allow-no-mirror` (mint new pin `pa-ea5458c5f0d44bee`), routed session-open handshake to Rigby.

**T2 (primary directive):** Rigby floated 3 candidates (all substrate); Claude corrected framing (per bias-engineering rule) + asked for 1-2 user-facing candidates. Rigby's joint recommendation: U1 (Workspace Governance/Inbox tab). Claude presented Chris plain-English framing (do we lose anything / more work later / recommendation).

**T3 (D-verdict):** Chris "approve U1." Claude proceeded to discovery + spec + build + close.

No further Chris routing needed — A1/A2/re-A2 all Claude↔Rigby.

---

## Wrapper pin

Active PA conversation pin at S3013 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the docs cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
