---
title: "Engineering Playbook v0.9.0 Amendment Ratification Record (2026-07-22)"
status: active
authority: ratification-record
session_added: 2889
ratification_date: 2026-07-22
ratifier: chris
ratifier_verdict: "yes ship it"
routing: rigby-pa-chat joint SIGN (T1 + T2 + T3 tool-grounded verification loop with zoom-out ask per PLAYBOOK-6.10.7; all items AGREE with two non-blocking mitigations applied same-envelope) + Chris D-verdict via terminal single-yes ("yes ship it")
amendment_scope: playbook-minor-v0.9.0
amendment_class: MINOR (per PLAYBOOK-10.5.1 — 2 additions, 0 modifications, 0 removals)
parent_version: v0.8.0
parent_version_git_tag: playbook-v0.8.0
parent_version_commit_sha: PLACEHOLDER_FILLED_AT_MERGE
parent_version_ratification: RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0
proposed_version: v0.9.0
proposed_git_tag: playbook-v0.9.0
predecessor_candidacy: two-trigger corpus surfaced in-wild across S2885 + S2886 error-envelope migration slates; both folds identified as "Playbook amendment candidates" in S2886 handoff §Folds; ratification carried forward to S2889 per S2888 close.
head_at_amendment_draft: 3432d0ba6c0a31efa6734047301642f8b4d33863
head_at_ratification: PLACEHOLDER_FILLED_AT_MERGE
close_pr: PLACEHOLDER_FILLED_AT_MERGE
cascade_pr: PLACEHOLDER_FILLED_AT_CASCADE
cascade_pr_merge_sha: PLACEHOLDER_FILLED_AT_CASCADE
sign_sessions:
  - S2889 T1 — Rigby joint SIGN dispatch with tool-grounded directives for items 1-5 (trigger evidence in S2885/S2886 handoffs; slot availability across Chapter 3 vs §6.10 vs §7.4; ledger-backfill legitimacy per PLAYBOOK-6.10.8 graceful-degradation clause; two-rule text review; zoom-out ask per PLAYBOOK-6.10.7). Rigby ran 10 tool_runs across two response turns (initial + completion after mid-Item-3 truncation) — repo_tool.read_file × 8 + repo_tool.search × 1 + one file-not-found typo. Anti-rubber-stamp gate PASS.
  - S2889 T2 — Rigby returned attestation: Items 1/2/3/4/5 all AGREE. Non-blocking findings: (a) Item 3 caution — `--concern` help text says "one sentence" not enforced; Option 1 (compress + point via evidence_ref) recommended; (b) Item 4 non-blocking — 3.2.3 rationale should name transaction-visibility invariant not fresh-event-loop mechanism; (c) Item 4 sub-verdict — KEEP TWO SEPARATE RULES (informational). Zoom-out folds: Fold A `same_pr_mitigatable` (3.2.3 invariant framing — mitigated same-PR at §2.1) + Fold B `future_trigger` (Testing Discipline chapter someday — persisted to ledger row 154 with concrete trigger conditions).
  - S2889 T3 — Both same-PR mitigations applied at envelope §2.1 revision + §3 compressed concern text; six ledger rows persisted (149-152 backfilled S2885/S2886 corpus + 153-154 live S2889 SIGN folds A + B). Light-touch T3 verification SIGN routed to Rigby for revised-text attestation before Chris D-verdict per `feedback_claude_rigby_agree_first_chris_yes_no`.
rules_added:
  - PLAYBOOK-3.2.3
  - PLAYBOOK-3.2.4
rules_modified: []
rules_removed: []
rule_count_before: 205
rule_count_after: 207
chapter_activation: "Chapter 3 §3.2 extension — 2 new [GR] rules under existing STUB-chapter scope; §3.2 grows from 2 rules (3.2.1 IOS deference + 3.2.2 acceptance-tests-first) to 4 rules; §3.5 extension-point list updated to note that verify-before-build discipline codification (previously deferred) has been partially exercised by the S2885→S2886 test-authoring folds, but that a full verify-before-build rule remains deferred."
supersedes: none
superseded_by: (open; not expected — ratification records are frozen historical envelopes)
frozen: true
workspace_id: a9a16593-e0a4-44dc-8256-efc65d524b3c
workspace_name: "Architecture & Research"
workspace_ratification_deliverable_id: PLACEHOLDER_FILLED_POST_MERGE
d_verdicts:
  - D1 Rule-ID slot placement — PLAYBOOK-3.2.3 + PLAYBOOK-3.2.4 taken per PLAYBOOK-10.7.5 next-integer rule under Chapter 3 §3.2; RATIFIED 2026-07-22 S2889 (Chris single-yes following joint Claude+Rigby AGREE on Chapter 3 as natural home over §6.10 / §7.4)
  - D2 Site placement — §3.2 Substantive discipline; extends PLAYBOOK-3.2.2 (acceptance-tests-first). First Chapter 3 extension since v0.2.0 (8-version gap); Chapter 3 remains STUB — RATIFIED 2026-07-22 S2889
  - D3 Amendment classification — MINOR v0.9.0 per PLAYBOOK-10.4.1 + PLAYBOOK-10.5.1 (2 new [GR] rules) — RATIFIED 2026-07-22 S2889
  - D4 One-rule-vs-two-rules — KEEP TWO SEPARATE RULES; 3.2.4 applies regardless of dispatcher path while 3.2.3 is dispatcher/fixture-visibility-specific; orthogonal disciplines sharing an authoring surface — RATIFIED 2026-07-22 S2889 (Rigby T2 Item 4 sub-verdict)
  - D5 Rule 3.2.3 rationale framing — reframed at T3 from mechanism-detail ("fresh asyncio event loop") to transaction-visibility invariant ("separate Django DB connection with no wrapping-transaction visibility"); dispatcher event-loop cited as one implementation cause — RATIFIED 2026-07-22 S2889 (Rigby T2 Fold A `same_pr_mitigatable` → mitigated at §2.1)
  - D6 Ledger-backfill legitimacy — PLAYBOOK-6.10.8 graceful-degradation clause blesses `--backfilled` for the four S2885/S2886 rows; four rows persisted at ledger positions 149, 150, 151, 152; two live S2889 SIGN folds persisted at positions 153, 154 — RATIFIED 2026-07-22 S2889
  - D7 Ledger schema hygiene — concern text compressed to one-sentence shape per `record_zoom_out_concern` `--concern` contract; longer handoff paragraphs reachable via `--evidence-ref` pointer — RATIFIED 2026-07-22 S2889 (Rigby T2 Item 3 non-blocking Option 1 recommendation)
  - D8 Zoom-out Fold B `future_trigger` — Testing Discipline chapter candidacy persisted at ledger row 154; trigger: 2 more test-authoring rules land in §3.2 before Chapter 3 promotion to FULL, OR one SIGN cycle blocked by ambiguous test-authoring slot placement; recorded as §3.5 extension-point note — RATIFIED 2026-07-22 S2889
---

# Engineering Playbook v0.9.0 — Amendment Ratification Record (DRAFT)

This file is the **workspace ratification envelope reflected in-repo** for the Engineering Playbook v0.9.0 MINOR amendment. It captures the amendment scope (§2), the empirical two-trigger corroboration for each of the two new rules (§3), the Rigby joint SIGN cycle (§4), Chris's D-verdict (§5), constitutional debt disposition (§6), and the post-ratification bindings (§7). §8 records what this amendment teaches about how to do amendments.

Append-only; do NOT edit after commit except to fill the reserved PLACEHOLDER_* fields.

---

## §1. Context

- **Amendment class:** MINOR (2 additions, 0 modifications, 0 removals) per PLAYBOOK-10.5.1.
- **Session:** S2889 (author + SIGN + ratify). If shipped in-session, this is the **fourth consecutive constitutional amendment in same-session shape** after v0.6.0/S2766, v0.7.0/S2778, and v0.8.0/S2786.
- **Head at amendment draft:** `3432d0ba` (post-S2888 close, tree clean).
- **Ratifier:** Chris, D-verdict pending at time of draft.
- **Routing:** Rigby PA chat surface via pin `pa-bf73f55995144814` (S2889 scope: two-rule handler-test-authoring codification).
- **Predecessor:** two-trigger empirical corpus surfaced in-wild across S2885 + S2886 error-envelope migration slates. Both folds enumerated in `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md` §Folds observed as "Playbook amendment candidates" at 2nd-trigger threshold.
- **Novel-precedent moments this cycle (if ratified):**
  1. **First MINOR amendment shipping two rules bundled by shared authoring surface.** v0.5.0 shipped 5 rules but they activated a whole chapter scope (§7.4 + §7.5 + §7.6 chapter-partial-activation); v0.6.0, v0.7.0, and v0.8.0 each shipped 1 rule. v0.9.0 ships 2 rules but they share a single authoring surface (handler tests exercising `ToolDispatcher.execute_sync` on shared error taxonomy) — the surface argues for one rule with two clauses OR two rules with an explicit sibling relationship. **The SIGN cycle at T1 is the decision surface for the one-rule-vs-two-rules shape.**
  2. **First amendment where the two-trigger corpus was NOT ledger-persisted at trigger time.** S2885 pre-code SIGN zoom-out (b) and S2886 Q3 zoom-out Concern B both surfaced the folds as substantive SIGN outputs. Neither was persisted to `logs/zoom_out_classifications.jsonl` via `record_zoom_out_concern` at the respective sessions' D-verdict boundaries, despite PLAYBOOK-6.10.8's classify-and-persist mandate. The v0.9.0 draft therefore includes a §4.3 retroactive-persist step per PLAYBOOK-6.10.8's graceful-degradation clause ("backfill the ledger" in a follow-up action). This is the first amendment cycle where retroactive backfill precedes T1 SIGN routing rather than following it, because the amendment's §3 corpus depends on ledger-enumerable rows. **The SIGN routing MUST ratify the backfill shape before backfill lands, so that the backfilled rows and the amendment envelope share provenance.**
  3. **First amendment landing rules in Chapter 3.** Prior MINOR amendments have activated §7.4/§7.5/§7.6 (v0.5.0), §7.4 (v0.6.0), §6.10 (v0.7.0 + v0.8.0), §5.2/§2.2/§3.2 (v0.2.0 — 3.2.2 was the last time Chapter 3 gained a rule). v0.9.0 extends §3.2 for the first time since v0.2.0 with two new [GR] rules under the existing STUB-chapter scope. Chapter 3 remains STUB overall; the two new rules do not promote the chapter to FULL activation.

---

## §2. Ratified amendment scope (DRAFT)

### §2.1 New rule PLAYBOOK-3.2.3 (revised T2 — invariant framing)

Added under existing §3.2 Substantive discipline (Chapter 3 STUB-chapter scope from v0.1.0, extended at v0.2.0 with PLAYBOOK-3.2.2 acceptance-tests-first). Full rule text (**revised at T2 per Rigby T1 SIGN Fold A `same_pr_mitigatable` — rationale reframed from mechanism-detail "fresh asyncio event loop" to invariant "separate Django DB connection with no wrapping-transaction visibility"; ledger row 153**):

> **[GR] PLAYBOOK-3.2.3** When authoring a handler regression test whose exercised code path materializes a separate Django database connection that does not participate in the test's wrapping transaction — for example dispatch through `ToolDispatcher.execute_sync`, which runs the handler on a fresh asyncio event loop that produces a separate DB connection — the test class MUST inherit from `django.test.TransactionTestCase` (not `django.test.TestCase`) whenever the dispatched handler reads ORM state that the test's `setUp` (or fixture-loading equivalent) creates. Rationale: plain `django.test.TestCase` wraps each test in a transaction that other Django DB connections do not see; `setUp`-created fixtures are therefore invisible to any handler that runs on a separate connection. The dispatcher's fresh-event-loop mechanism is one implementation cause of this cross-connection visibility gap; the rule scopes to the transaction-visibility invariant, not to any single dispatch mechanism, so it continues to apply if `execute_sync`'s internals change or if a new dispatcher entry point produces the same DB-connection boundary. A test author MAY use plain `django.test.TestCase` ONLY when the handler under test requires no `setUp`-created ORM fixtures — for example when the assertion is that a lookup for a nonexistent UUID returns the `not_found` envelope regardless of database visibility. When `TransactionTestCase` is required, the choice MUST be recorded in the test file's module docstring citing this rule. This rule EXTENDS PLAYBOOK-3.2.2 (acceptance-tests-first) with a test-class-selection requirement scoped to any handler test that crosses a DB-connection boundary. [E2: RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md §3 (two-trigger corpus enumerating S2885 + S2886 fixture-visibility failures, backfilled to `logs/zoom_out_classifications.jsonl` rows 149 + 150); E4: `core/services/tool_dispatcher.py:1160` (the `asyncio.new_event_loop().run_until_complete(...)` call that produces the fresh DB connection — one instance of the invariant, not the invariant itself); E5: `core/tests/test_s2885_content_error_envelope.py` (S2885 first-trigger — `DeliverableInitiativeLinkMigratedEnvelopeTests` + `ContentToolMigratedEnvelopeTests` inherit `TransactionTestCase`); E5: `core/tests/test_s2886_core_error_envelope.py` (S2886 second-trigger — `RememberToolMigratedEnvelopeTests` + `MessagingToolMigratedEnvelopeTests` inherit `TransactionTestCase`, Rigby S2886 Q3 zoom-out Concern B predicted then materialized); E6: `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md` §Fold 1 (first-trigger record); E6: `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md` §Fold 1 (second-trigger record + Playbook amendment candidacy flag)]

### §2.2 New rule PLAYBOOK-3.2.4 (proposed)

Added under existing §3.2 Substantive discipline, immediately following PLAYBOOK-3.2.3. Full rule text (DRAFT — subject to SIGN):

> **[GR] PLAYBOOK-3.2.4** When a handler under test has two or more return branches that emit the same taxonomy `error_code` (for example: two `not_found` branches distinguished only by which entity is missing, or three `invalid_params` branches distinguished only by which parameter is missing), a migrated-envelope regression test asserting that `error_code` MUST additionally assert one of: (a) the value of the envelope's `action` field, when the branches emit distinct actions; OR (b) a distinguishing substring in the envelope's `error` message body, when the branches share an action. The intent is to prevent a false-pass in which a regression breaks branch B but the test asserting branch B's behavior continues to pass because the assertion is also satisfied by branch A's still-passing envelope. Rationale: `_assert_migrated_envelope` and equivalent taxonomy helpers check the envelope's `success=False` + `error_code` + envelope shape but do not distinguish which internal branch fired. When two branches share a code, the test MUST close the disambiguation via `action` or error-body substring. This rule EXTENDS PLAYBOOK-3.2.2 (acceptance-tests-first) with a branch-disambiguation requirement scoped to shared-taxonomy handler tests. It complements PLAYBOOK-3.2.3 (dispatcher-path DB visibility) — Rule 3.2.4 was first observed in the S2885 slate where plain-`TestCase` fixture invisibility masked the branch-crossing failure mode; but the underlying discipline is orthogonal to Rule 3.2.3 and applies to any shared-taxonomy test regardless of dispatcher path. [E2: RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md §3 (two-trigger corpus enumerating S2885 + S2886 shared-taxonomy false-pass patterns); E4: `core/tests/test_s2885_content_error_envelope.py:test_deliverable_initiative_link_missing_initiative_returns_not_found` (S2885 first-trigger — L182+L190 both return `not_found`; test asserts `'Initiative' in error` to disambiguate); E4: `core/tests/test_s2886_core_error_envelope.py` (S2886 second-trigger — L3849+L3986 both return `not_found`, disambiguated by `'Thread not found or access denied'` substring + action; L2230+L2331+L2345 all return `invalid_params`, disambiguated by action field via `_assert_migrated_envelope`'s action-awareness); E6: `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md` §Fold 2 (first-trigger record); E6: `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md` §Fold 2 (second-trigger record + Playbook amendment candidacy flag)]

### §2.3 Extended §3.5 extension-point commentary (informative)

The §3.5 extension-point list currently reads:
- Verify-before-build discipline codification.
- ADR authoring templates and conventions.
- Reversibility scoring for implementation decisions.
- Cross-corpus consistency between repository and workspace ADRs.

The first line ("Verify-before-build discipline codification") is unchanged in its NORMATIVE status — the codification remains deferred to a future MINOR — but a parenthetical is added to note that S2885→S2886 partially exercised the discipline for test authoring (test-class selection = verify DB visibility before writing the test; taxonomy disambiguation = verify branch coverage before asserting the envelope). Full codification of "verify-before-build" for engineering work remains a future extension.

### §2.4 Appendix D version-chain row

Appended one row for v0.9.0 to `docs/ENGINEERING_PLAYBOOK.md` Appendix D — Version chain. Row records the amendment class (MINOR), parent (v0.8.0), rules added (PLAYBOOK-3.2.3 + PLAYBOOK-3.2.4), the two-trigger corpus with backfilled ledger row numbers, first Chapter 3 extension since v0.2.0.

### §2.5 Frontmatter updates

- `version`: "0.8.0" → "0.9.0"
- `parent_version`: "0.7.0" → "0.8.0"
- `compatible_with`: appended "0.8.0"
- `ratified_date`: 2026-07-14 → 2026-07-22
- `branch_authored`: `playbook/v0.8.0-evidence-admission-fold-authoring` → `playbook/v0.9.0-handler-test-authoring-discipline`
- `git_tag`: `playbook-v0.8.0` → `playbook-v0.9.0`
- `prior_ratification`: v0.7.0 → v0.8.0 (with dates + tag)
- `authoring_sessions`: appended 2889
- `v0_9_0_authoring_session: 2889`, `v0_9_0_ratification_session: 2889`
- `rule_count`: 205 → 207
- `rules_added_v0_9_0: [PLAYBOOK-3.2.3, PLAYBOOK-3.2.4]`
- Title H1: `# Donkey Betz Engineering Playbook v0.8.0` → `v0.9.0`

---

## §3. Two-trigger corroboration ledger (DRAFT — pending backfill per §4.3)

### §3.1 Fold 1 — `TransactionTestCase` for dispatcher-DB tests

| # | Session | Fold text (compressed to match ledger `concern_text`; longer handoff paragraph reachable via `evidence_ref`) | What Rigby / Claude verified | Ledger row (post-backfill) |
|---|---|---|---|---|
| 1 | S2885 pre-code SIGN + post-code | S2885 first trigger: `DeliverableInitiativeLinkMigratedEnvelopeTests` and `ContentToolMigratedEnvelopeTests` required `TransactionTestCase` because `ToolDispatcher.execute_sync` spins a fresh asyncio event loop with a separate Django DB connection, and `setUp`-created fixtures were invisible to the handler under plain `TestCase`. | Confirmed at `core/services/tool_dispatcher.py:1160` (asyncio.new_event_loop → fresh DB connection); confirmed test file uses `TransactionTestCase` at `core/tests/test_s2885_content_error_envelope.py`. | **row 149 (backfilled 2026-07-22 per §4.3)** |
| 2 | S2886 Q3 zoom-out Concern B | S2886 second trigger: Rigby predicted at pre-code SIGN that Slate B would re-trigger the S2885 TransactionTestCase pattern because remember and messaging handlers require User fixtures visible to `ToolDispatcher.execute_sync`, and the prediction materialized in `RememberToolMigratedEnvelopeTests` and `MessagingToolMigratedEnvelopeTests`. | Confirmed prediction materialized at `core/tests/test_s2886_core_error_envelope.py`; same DB-connection-boundary invariant as S2885. | **row 150 (backfilled 2026-07-22 per §4.3)** |

**Common failure mode:** at the moment a handler test needs to exercise a dispatcher-path handler that reads DB state populated by `setUp`, plain `django.test.TestCase` silently fails because the handler runs on a separate DB connection. The failure is silent because the ORM lookup returns `DoesNotExist` for the missing fixture and the handler dutifully returns a `not_found` envelope — which passes envelope-shape assertions AND (before Rule 3.2.4) may false-pass shared-taxonomy assertions.

**Rule design response:** codify test-class selection as a positive rule scoped to dispatcher-path handler tests with fixture dependencies, rather than a "sometimes-use-TransactionTestCase" hint. The rule includes a narrow carve-out (nonexistent-UUID assertions) so it does not force `TransactionTestCase` when plain `TestCase` correctly captures the intent.

### §3.2 Fold 2 — Shared-taxonomy branch fortification

| # | Session | Fold text (compressed to match ledger `concern_text`; longer handoff paragraph reachable via `evidence_ref`) | What Rigby / Claude verified | Ledger row (post-backfill) |
|---|---|---|---|---|
| 1 | S2885 code review | S2885 first trigger: `_handle_deliverable_initiative_link` L182 and L190 both return `not_found`, and before fortification the missing-Initiative test false-passed by reaching the missing-Deliverable branch; fortified by asserting `'Initiative' in error` message to disambiguate. | Confirmed L182 + L190 both return `not_found`; confirmed fortification assertion at `core/tests/test_s2885_content_error_envelope.py`. | **row 151 (backfilled 2026-07-22 per §4.3)** |
| 2 | S2886 code review | S2886 second trigger: `_handle_messaging` L3849 and L3986 both return `not_found`, disambiguated by `'User'` vs `'Thread'` error-body substrings; `_handle_remember` L2230/L2331/L2345 all return `invalid_params` disambiguated by `action` field via action-aware `_assert_migrated_envelope`. | Confirmed both classes of disambiguation at `core/tests/test_s2886_core_error_envelope.py`. | **row 152 (backfilled 2026-07-22 per §4.3)** |

**Common failure mode:** when two branches of a handler emit the same taxonomy `error_code`, a regression breaking branch B can pass through the test suite because the branch-B test assertion (envelope-shape + error_code) is also satisfied by branch A's still-passing behavior. The failure is silent because there is no observable difference in the envelope beyond the field the test wasn't asserting.

**Rule design response:** codify branch disambiguation as a positive rule scoped to shared-taxonomy tests, with two admissible disambiguation mechanisms (action field OR message-body substring). The rule allows the test author to pick the mechanism appropriate for the branches — action field is preferable when it's stable, substring when action is shared across the branches.

---

## §4. Rigby joint SIGN cycle

### §4.1 T1 dispatch (author-side directive)

Sent to Rigby via `bash tools/pa_local.sh` on pin `pa-bf73f55995144814`. Five tool-grounded items dispatched:

1. **Trigger evidence verification:** verify the four fold observations across `docs/handoffs/SESSION_2885_CONTENT_ERROR_ENVELOPE.md` §Fold 1+§Fold 2 and `docs/handoffs/SESSION_2886_CORE_CRITICALITY_FIRST_ERROR_ENVELOPE.md` §Fold 1+§Fold 2 are enumerable and match envelope §3 tables.
2. **Slot verification:** compare Chapter 3 §3.2 vs §6.10 vs §7.4 placement. Author's proposal: Chapter 3 (extending PLAYBOOK-3.2.2 acceptance-tests-first).
3. **Ledger-backfill legitimacy:** confirm `--backfilled` flag legitimizes retroactive persistence for four S2885/S2886 fold rows under PLAYBOOK-6.10.8 graceful-degradation clause.
4. **Two-rule text review:** classify F-BLOCKING/non-blocking/informational on DRAFT §2.1+§2.2 rule text; sub-question on one-rule-with-two-clauses vs two-separate-rules.
5. **Zoom-out ask (PLAYBOOK-6.10.7):** "What would you push back on if asked fresh? Chapter 3 extended for first time in 8 versions — signal that rules are premature or that Chapter 12 Testing Discipline is truer home?"

Explicit anti-rubber-stamp directive per `feedback_verify_rigby_tool_runs_before_trusting_sign`: "Do NOT rubber-stamp — verify at HEAD `3432d0ba` using `repo_tool` before AGREE."

### §4.2 T2 attestation (Rigby)

Rigby returned attestation across two message turns (initial response truncated mid-Item 3; completion turn 2 covered Items 3 finish + 4 + 5). Total tool_runs: **10** across the two turns — `repo_tool.read_file × 8` (handoffs S2885/S2886, envelope, `record_zoom_out_concern.py`, both test files, Playbook §3.2/§6.10/§7.4/§6.10.8), `repo_tool.search × 1` ("backfilled" query on `record_zoom_out_concern.py`), plus 1 typo-file-not-found (harmless). **Anti-rubber-stamp gate: PASS** (substantive tool_runs; no rubber-stamp signal).

Per-item verdicts:

- **Item 1 AGREE (informational).** Four fold observations enumerable; envelope §3.1 table matches S2885/S2886 handoff §Fold 1/§Fold 2 text.
- **Item 2 AGREE (informational).** Chapter 3 §3.2 is the correct natural home over §6.10 (verification of provenance / SIGN mechanics) and §7.4 (close-ceremony packaging). New rules read as direct siblings of PLAYBOOK-3.2.2 (acceptance-tests-first).
- **Item 3 AGREE (non-blocking):** `--backfilled` legitimizes retroactive persistence; §4.3 four-row backfill correct. Non-blocking caution: `record_zoom_out_concern`'s `--concern` help text says "one sentence" (not programmatically enforced). Recommendation: Option 1 (compress fold text to one sentence + point to handoff paragraph via `--evidence-ref`). §3 tables and §4.3 backfill both compressed per Option 1.
- **Item 4 AGREE (non-blocking):**
  - **PLAYBOOK-3.2.3:** AGREE; non-blocking on rule wording robustness — rationale should name the invariant ("separate Django DB connection / no wrapping-transaction visibility") rather than the implementation detail ("fresh asyncio event loop"), so the rule doesn't overfit dispatcher internals.
  - **PLAYBOOK-3.2.4:** AGREE; non-blocking micro-observation that S2886 sometimes uses BOTH action AND substring for extra robustness (rule allows either — "or" is correct; observation informational only).
  - **One-rule-vs-two-rules verdict:** **KEEP TWO SEPARATE RULES** (informational). Orthogonality: 3.2.4 applies regardless of dispatcher path; 3.2.3 is dispatcher/fixture-visibility-specific.
- **Item 5 (PLAYBOOK-6.10.7 zoom-out):** Not premature; proceed. Two zoom-out folds surfaced:
  - **Fold A** `same_pr_mitigatable`: 3.2.3 rationale should phrase invariant, not mechanism. → **Mitigated same-PR at §2.1 revision above.**
  - **Fold B** `future_trigger`: Chapter 3 extension after 8-version gap signals testing discipline is accreting inside implementation discipline; consider dedicated "Testing Discipline" chapter (hypothetical Chapter 12) to reduce long-term slot confusion. → **Future trigger: 2 more test-authoring rules land in §3.2 before Chapter 3 is promoted to FULL, OR one SIGN cycle blocked by ambiguous test-authoring slot.**

### §4.3 T3 ledger backfill + live-persist (Claude environment)

Six ledger entries persisted via `python manage.py record_zoom_out_concern` on 2026-07-22 following T2 AGREE on backfill legitimacy:

| Ledger row | Session | Classification | Backfilled | Arc |
|---|---|---|---|---|
| 149 | S2885 | `same_pr_mitigatable` | true | `s2885_transaction_testcase_dispatcher_db` |
| 150 | S2886 | `same_pr_mitigatable` | true | `s2886_transaction_testcase_dispatcher_db` |
| 151 | S2885 | `same_pr_mitigatable` | true | `s2885_shared_taxonomy_branch_fortification` |
| 152 | S2886 | `same_pr_mitigatable` | true | `s2886_shared_taxonomy_branch_fortification` |
| 153 | S2889 | `same_pr_mitigatable` | false | `v0_9_0_invariant_framing` (Fold A) |
| 154 | S2889 | `future_trigger` | false | `v0_9_0_testing_discipline_chapter` (Fold B) |

Ledger grew 148 → 154 rows during S2889. Rows 149-152 backfill the S2885/S2886 corpus that PLAYBOOK-6.10.8 mandated but the respective sessions failed to persist at trigger time; rows 153-154 dogfood the amendment's own SIGN cycle per v0.8.0 precedent.

### §4.4 T2 same-PR mitigations applied

Both non-blocking findings from T2 resolved in-envelope before D-verdict routing:

1. **Concern-text compression to one sentence (Item 3 non-blocking).** Envelope §3.1 + §3.2 concern-text columns compressed to one-sentence shape; longer handoff-paragraph pointers moved to `evidence_ref` field of the backfilled ledger rows.
2. **Invariant framing reframe (Item 4 non-blocking + Fold A `same_pr_mitigatable`).** Envelope §2.1 rule text revised — rationale now names the transaction-visibility invariant first; dispatcher's fresh-event-loop mechanism cited as "one implementation cause" rather than the invariant itself.

Per `feedback_claude_rigby_agree_first_chris_yes_no`: both non-blocking asks resolved between Claude+Rigby before Chris routing. Chris will ratify one recommendation, not adjudicate an unresolved menu.

### §4.5 T3 verification SIGN (light-touch attestation on revisions — pending)

Revised §2.1 rule text + §3 compressed concern tables + §4.3 ledger rows dispatched to Rigby for T3 SIGN attestation before Chris D-verdict routing. Anti-rubber-stamp gate maintained: T3 must verify §2.1 revision satisfies Fold A's invariant framing at HEAD `3432d0ba` (or successor SHA if envelope commit lands first) with tool-grounded read.

### §4.6 T4 revised-text SIGN (Rigby verification of same-PR mitigations — pending)

Placeholder; filled after T3 returns. Expected shape: light-touch AGREE + any tightening micro-edits.

---

## §5. Chris D-verdict

Chris rendered single-yes D-verdict at S2889 (2026-07-22, terminal): **"yes ship it"**.

Per `feedback_claude_rigby_agree_first_chris_yes_no`: all F-BLOCKING findings absent; all non-blocking findings resolved between Claude+Rigby before Chris routing (Rigby T2 Item 3 concern-text compression + Item 4 invariant-framing reframe both mitigated same-envelope at §2.1 revision + §3 compression; Chris ratified the resolved design rather than adjudicating an unresolved menu).

Plain-English framing routed to Chris per `feedback_plain_english_decision_framing_for_chris`: what ships (two handler-test-authoring rules), what we lose if he says no (nothing — patterns already applied in test files), whether it's more work later (no — prevents future silent regressions). Single recommendation ("ship v0.9.0 as-drafted"), not a menu.

---

## §6. Constitutional debt disposition (pending)

- **CD-open (from v0.8.0):** I-0302 three-PR pattern candidacy previously re-slotted from PLAYBOOK-6.10.9 (v0.7.0) → PLAYBOOK-6.10.10 (v0.8.0). v0.9.0 does NOT touch PLAYBOOK-6.10.10; the re-slot remains at 6.10.10 pending the actual amendment that would codify the three-PR pattern. No re-slot required.
- **CD-closed:** none discharged by this amendment. The two folds were surfaced as candidates in S2885/S2886 handoffs; the codification here IS the discharge of the candidacy, not the discharge of a Constitutional Debt row.

---

## §7. Post-ratification bindings (PLACEHOLDER fields — filled at merge / cascade)

- `parent_version_commit_sha`: v0.8.0 merge SHA — to be filled at v0.9.0 ship PR merge from repo state
- `head_at_ratification`: filled at v0.9.0 ship PR merge SHA
- `close_pr`: filled at PR open
- `cascade_pr` + `cascade_pr_merge_sha`: filled at close-cascade PR merge
- `workspace_ratification_deliverable_id`: filled post-merge when Rigby mints workspace deliverable per `feedback_rigby_writes_workspace_deliverables`

---

## §8. What this amendment teaches about how to do amendments

- **Two-rule bundling when folds share authoring surface is a valid amendment shape.** v0.9.0 is the first MINOR after the single-rule cadence (v0.6.0, v0.7.0, v0.8.0) to bundle two rules. Rigby T2 confirmed KEEP TWO SEPARATE RULES because 3.2.4 (shared-taxonomy branch fortification) applies regardless of dispatcher path while 3.2.3 (TransactionTestCase for dispatcher-DB tests) is dispatcher/fixture-visibility-specific — the two rules share an authoring surface but are logically orthogonal. This establishes precedent for bundling folds that share substrate context but codify distinct disciplines.
- **Retroactive ledger backfill under PLAYBOOK-6.10.8 graceful-degradation clause is a first-class ratifiable move.** S2885 and S2886 both surfaced zoom-out folds in-SIGN but neither persisted the folds to `logs/zoom_out_classifications.jsonl`, violating PLAYBOOK-6.10.8's classify-and-persist mandate. The graceful-degradation clause envisions ledger backfill for exactly this case ("open a follow-up action item to backfill the ledger"). v0.9.0's §4.3 exercises the backfill mechanism as a governance-blessed prerequisite of an amendment whose §3 corpus depends on ledger-enumerable rows, not as an ad-hoc post-hoc cleanup. Rigby AGREE at T2 Item 3 ratified the shape. Precedent for future amendments: when the two-trigger corpus was not persisted at trigger time, backfill BEFORE T1 SIGN routing (so the SIGN reviewer can inspect the ratified backfill shape) — not AFTER D-verdict.
- **Chapter 3 extension after 8-version gap is not premature.** v0.9.0 is the first amendment to extend Chapter 3 since v0.2.0 (PLAYBOOK-3.2.2). The gap reflects that implementation-discipline codification has been slower than provenance-discipline codification (§6.10 grew from 6 rules at v0.1.0 to 9 rules at v0.8.0). Rigby T2 Fold B (`future_trigger`) reframed this as a signal to WATCH for testing discipline accretion — trigger: 2 more test-authoring rules land in §3.2 before Chapter 3 is promoted to FULL, OR one SIGN cycle blocked by ambiguous test-authoring slot placement. The v0.9.0 codification demonstrates that in-wild handler-test authoring produces amendment-ready rules just as SIGN-cycle discipline does, with the future-trigger note carrying forward the slot-clarity concern.
- **Compressed one-sentence ledger concerns + long-form evidence pointers is the correct schema hygiene.** Rigby T2 Item 3 non-blocking finding drove the concern-text compression from multi-sentence handoff-paragraph shape to one-sentence canonical shape, with the longer paragraph reachable via `--evidence-ref` pointer to the handoff file+line. This preserves the ledger's pattern-evidence ergonomics without losing recoverability of the full fold context. Precedent for future backfill: compress at ledger write, point at handoff.
- **Substrate dogfooding at authoring extended to two dimensions again.** v0.9.0 dogfoods 2 folds pre-D-verdict (Fold A `same_pr_mitigatable` invariant framing + Fold B `future_trigger` testing-discipline chapter). Fold A drove a same-PR revision of the rule text before ratification (the same pattern v0.8.0 exercised on Fold A of that amendment). This is the third consecutive amendment (v0.7.0 dogfooded 4 folds; v0.8.0 dogfooded 2 folds; v0.9.0 dogfooded 2 folds) to prove that the dogfooding pattern is stable — the amendment under authoring can be shaped by its own SIGN cycle without ceremony inflation.

---

*Draft opened at S2889 by Claude authorship; Rigby T1 + T2 SIGN AGREE with same-PR non-blocking mitigations applied at §2.1 revision + §3 compression; T3 verification SIGN pending; Chris D-verdict pending.*
