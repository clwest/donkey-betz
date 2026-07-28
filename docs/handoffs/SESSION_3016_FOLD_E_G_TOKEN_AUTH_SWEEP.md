# Session 3016 — Fold E + Fold G Token-auth sweep

**Date:** 2026-07-28
**HEAD at close:** `14b4a7ad4` (PR #3717 merged) + docs cascade PR
**Session shape:** Substrate hardening — closed the S3015 hotfix follow-up (both halves of Chris's directive) before the next user-facing arc. Rebalances after 3 consecutive user-facing sessions (S3013 U1 → S3014 U2 → S3015 U3).

---

## What shipped

### PR #3716 — `test(s3016): Fold E — Token-auth parity guards for user-facing endpoints` (`ad84a847b`)

**Helper (`core/tests/helpers/token_auth.py` + `__init__.py`):**
- `token_client_for(user, *, host='localhost:8000')` — idempotent DRF `Token.objects.get_or_create` + `Client(HTTP_HOST=host, HTTP_AUTHORIZATION=f'Token {token.key}')`. Mirrors what the React frontend sends after login.
- Docstring explains the S3015 hotfix scenario and why session-auth-only tests missed it.

**Test coverage adds (4 files, +6 net tests):**
- `core/tests/test_s3013_bulk_attention_decide_mutation.py::test_token_auth_reaches_bulk_decide_endpoint_parity` — asserts BulkAttentionDecideView reaches under Token-auth and cross-user scope holds (2 items → count=2, both STATUS_ACTED, DECISION_APPROVE).
- `core/tests/test_s3014_create_initiative_from_cluster.py::test_token_auth_reaches_single_cluster_endpoint_parity` — single cluster → initiative create under Token-auth. **REVISE 1 strengthened:** now asserts `initiative.target_workspace.user_id == self.user.id` (anon can't resolve user's workspace).
- `core/tests/test_s3015_bulk_create_initiatives_from_clusters.py::test_token_auth_reaches_bulk_endpoint_parity` — bulk cluster → initiative create under Token-auth, per-initiative workspace-owner assertion.
- **NEW** `core/tests/test_s3016_initiatives_list_auth_parity.py` — 3 tests locking the exact PR #3714 scenario:
  - `test_token_and_session_auth_return_identical_shape` — session vs Token count parity + first-page id parity.
  - `test_token_auth_alone_returns_owned_initiatives_not_empty` — direct S3015 scenario (Token-auth caller → count=3 for owned initiatives).
  - `test_anonymous_still_returns_empty_200` — locks OPTIONAL_AUTH_PATHS "safe to expose publicly" contract (anon → 200 + count=0).

**Test result:** 32/32 pass in 4.125s (was 28 pre-Fold E; +4 net + workspace-owner strengthening).

### PR #3717 — `docs(s3016): Fold G — PUBLIC_PATHS bare-prefix audit for silent-empty reads` (`14b4a7ad4`)

**Candidate generator (`scripts/audit_public_paths_scoped_reads_s3016.py`):**
- Walks `get_resolver().url_patterns × PUBLIC_PATHS`, greps view source for 5 canonical scope predicates from `core/security/object_authz.py`.
- Explicitly **not a classifier** — anon behavior (401/403 loud vs empty 200 silent) requires hand-review. REVISE 1 corrected the initial framing.

**Findings doc (`docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md`):**
- **F-1 (false positive)** — `/api/celery/breakdown/` (`TaskBreakdownView` at `core/views_celery_api.py:256`). `@method_decorator(superuser_required)` gate at line 264 makes anon 401 loudly, not empty 200.
- **F-2 (unscoped detail row + silent enrichment drop)** — `/api/memory-palace/memory/<uuid>/` (`get_memory_detail` at `core/views_memory_palace.py:98`). **Primary issue:** the memory detail row itself is unscoped and public — anon with a valid UUID fetches the row + triggers access_count auto-increment side effect. **Secondary issue:** optional `execution_data` enrichment silently returns None for anon. REVISE 3 reframed to lead with the unscoped-row issue.
- **Housekeeping:** `/api/celery/` appears twice in PUBLIC_PATHS (lines 148 and 225). Idempotent runtime, noisy audit. Dedupe follow-up candidate.

**Substantive conclusion:** the S3015 list-endpoint-empty class does **not** repeat elsewhere in the current PUBLIC_PATHS surface for the 5 tracked predicates. Fold E hotfix + parity tests are correctly scoped.

**Machine-readable output:** `docs/audits/public_paths_bare_prefix_audit_s3016.json`.

---

## SIGN provenance (6 cycles this session, all tool-grounded)

- **Fold E T0** — AGREE + REVISE 1 (shared helper + one parity assertion per contract, not blind 1:1 duplication) + REVISE 2 (narrow Fold G audit to queryset-scoped endpoints).
- **Fold E T1** — REVISE (strengthen S3014 + S3015 with `target_workspace.user_id` assertion; add optional anon-negative test).
- **Fold E T1 close-out** — AGREE.
- **Fold G T1** — REVISE 1 (script docstring over-claimed silent-empty fidelity) + REVISE 2 (doc Method needs candidate-generator framing) + REVISE 3 (F-2 primary issue is unscoped memory row, not enrichment drop; added third remediation shape = new `scope_queryset_agent_memory` predicate).
- **Fold G T1 close-out** — AGREE.

**Rigby SIGN quality: zero rubber-stamp signals (empty tool_runs).** Every AGREE/REVISE included repo_tool reads with file:line evidence. Matches S3010–S3015 pattern → **8 sessions continuous hallucination-free**.

---

## Folds

### Fold A `same_pr_actionable → resolved` — Weak parity assertions can pass under anon-fallthrough

**Trigger:** T1 SIGN caught that S3014/S3015 parity tests only asserted `owner_id` + name shape, which could theoretically pass under an anon-fallthrough regression. **Resolution:** added `initiative.target_workspace.user_id == self.user.id` (anon can't resolve user's first workspace) — assertion now fails hard on regression. Same-PR mitigation per PLAYBOOK-6.10.8.

### Fold B `same_pr_actionable → resolved` — Fold G script over-claimed detection fidelity

**Trigger:** T1 SIGN caught that the audit script docstring implied silent-empty classification when the grep is really just a candidate generator. **Resolution:** script docstring reframed to "Candidate generator only"; MD doc Method section added explicit "grep yields candidates; hand-review classifies" framing + step 6 (hand-review). Same-PR mitigation.

### Fold C `same_pr_actionable → resolved` — F-2 framing misled on primary vs secondary issue

**Trigger:** T1 SIGN caught that F-2 was framed as "partial degradation of execution_data" when the primary issue is that the memory detail row itself is unscoped and public. **Resolution:** doc reframed to lead with the unscoped-row leak; enrichment drop demoted to secondary; third remediation shape added (introduce `scope_queryset_agent_memory` predicate). Same-PR mitigation.

### Fold D `1st trigger` — Doc-only PR still runs `make recycle-all` per PLAYBOOK-7.4.4

**Trigger:** PR #3717 is doc + non-imported script only — nothing for Daphne or Celery to reload. Ran `make recycle-all` anyway for constitutional consistency (Chris ratified "proceed" without carving out an exception). **Watch for 2nd trigger** — if another doc-only close-ceremony hits, consider whether PLAYBOOK-7.4.4 needs an explicit "doc-only PR = recycle optional" clause or stays constitutional-uniform.

### Fold E `zoom-out from Rigby T0 SIGN` — Middleware ordering / DRF ViewSets / WebSocket auth / Bearer-vs-Token

**Zoom-out concerns Rigby raised at Fold E T0 SIGN, all deferred (not in scope this session):**
1. Middleware ordering drift — Django test-client-with-middleware path may not match Daphne/ASGI in prod under a stack reorder.
2. DRF `authentication_classes` on ViewSets may bypass `UnifiedTokenAuthenticationMiddleware` entirely; parity tests only cover endpoints they explicitly target.
3. WebSocket auth — Fold E is HTTP READ scope only; WS regressions not defended.
4. `Bearer <token>` header format — only `Token <key>` currently covered by the helper.

All 4 are forward carries in the S3017 seeds.

### Fold F `informational` — Classifier under-fits inline `.filter(user=…)` patterns

**Zoom-out from Fold G T1 SIGN.** The audit script only catches views that reference the 5 tracked predicate names in source. Views doing inline `.filter(user=request.user)` or `get_object_or_404(Model, user=request.user, …)` are invisible. Not expanding this session — if a future silent-empty regression surfaces on an unscoped predicate endpoint, expand the classifier per Fold G doc's forward-carry note.

---

## Forward carries (from this session)

### New from S3016

- **F-2 remediation** (unscoped `/api/memory-palace/memory/<uuid>/`). Chris ratifies shape:
  1. `@token_auth_required` gate (simplest, matches S2789 pattern).
  2. Introduce `scope_queryset_agent_memory` in `core/security/object_authz.py` + scope the lookup itself (strongest, requires design addition).
  3. Add `execution_data_available` payload flag (secondary only — does NOT fix the unscoped row leak).
- **Dupe `/api/celery/` PUBLIC_PATHS entry** (lines 148 + 225) — low-priority housekeeping PR.
- **Fold D `1st trigger`** — doc-only PR + `make recycle-all` policy. Watch for 2nd.
- **Fold E `1st trigger` (renamed from S3015)** — retired: Fold E was S3015's "browser-layer defects invisible to shell/SIGN" carry; this session's Fold E test coverage class addresses it, so the S3015 Fold E carry is now closed by S3016 PR #3716.
- **Fold F `1st trigger` (renamed from S3015)** — carry-forward retained: empty-state diagnostic tree not yet formalized. (This session narrowed one silent-degradation class but the tree is broader.)
- **Fold G `informational` (renamed from S3015)** — retired: this session's PR #3717 doc IS the S3015 Fold G audit. Closed.
- **Zoom-out carries (from Fold E T0):**
  - Middleware-ordering drift → design: middleware-order snapshot test candidate.
  - DRF ViewSet auth-class audit → 2nd-trigger watch (would need parallel Fold-G-shape audit for DRF stack).
  - WebSocket auth-parity coverage class — separate arc, likely S3018+.
  - `Bearer <token>` helper extension — low-risk, small (30-min) follow-up.
- **Fold F `informational`** — inline-scoping classifier expansion (only if triggered by a future incident).

### Carried from S3015 (STATUS UPDATED)

- **Fold E `1st trigger`** — **CLOSED by S3016 PR #3716** (Token-auth parity coverage class shipped).
- **Fold F `1st trigger`** — carry-forward retained; empty-state diagnostic tree still open.
- **Fold G `informational`** — **CLOSED by S3016 PR #3717** (PUBLIC_PATHS bare-prefix audit).
- **U4 candidate (AgentDecisionSummary bulk-decide)** — carry-forward.
- **U5 candidate (post-create auto-link via `initiative_signal_linker`)** — carry-forward.
- **U6 candidate (per-row name editing in bulk cluster confirm modal)** — carry-forward.
- **Fold A `1st trigger` (bulk-endpoint scope-limit-cap standard)** — carry-forward.
- **Fold B `informational`** — carry-forward (refactor-first for U-N when U-(N-1) shipped shared logic).
- **Fold C `informational`** — carry-forward (bulk-endpoint invariants).
- **Fold D `3rd trigger` (Cycle 1A verify-before-build)** — carry-forward.
- **UI candidate: progress bar during bulk create** — carry-forward.

### Carried from earlier sessions

See prior handoffs for the full carry-forward tail. Notable retentions:
- Sports odds leak drain arc (32 DRF Response `str(e)` sites in `views_odds_sports.py`).
- Task #7 (delete dead A/B testing handlers) + Task #8 (DRF-decorator refactor for 15 auth guards).
- Fold B `5th trigger imminent` (PLAYBOOK-7.4.5 amendment for `make restart` — all recent sessions used `make recycle-all`, so trigger imminent but not fired).

---

## Cross-cutting workflow references

- **Constitutional governance:** Playbook v0.10.0. No amendments this session.
- **Spec→ship contract (PLAYBOOK-7.7.1):** 2× Flow B spec→ship this session (Fold E + Fold G).
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** 6× substantive Rigby SIGN cycles, zero rubber-stamp signals, all tool-grounded. **8 sessions continuous.**
- **Chris-facing decision framing (PLAYBOOK-7.7.3):** Chris routing this session: "correcting: I anchored on 00-START menu instead of your close summary" (Fold E scope pivot) + 4× "proceed" ratifications + 1× "merge and recycle" directive.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` twice — post-Fold-E merge and post-Fold-G merge (constitutional consistency even on doc-only PR).
- **Fold classification (PLAYBOOK-6.10.8):** 3× `same_pr_actionable → resolved` (Folds A/B/C all mitigated in same PR). 1× new `1st trigger` (Fold D). 2× `informational` (Folds E/F zoom-out).
- **Verify-before-build (Cycle 1A):** implicit in Fold E — the token-auth helper was placed in `core/tests/helpers/` after checking no prior helper pattern existed.

---

## Wrapper pin note

The active PA conversation pin at S3016 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3016 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Session shape summary.** S3016 ran as substrate hardening after 3 consecutive user-facing sessions. Chris's directive was two-part (Fold E test coverage + Fold G audit); both halves shipped as separate PRs with tight Rigby SIGN discipline. Zero critical audit findings + 0 test failures + 0 hallucination triggers = clean close-out. S3017 opens with no in-flight arc; F-2 remediation, U4/U5/U6 continuation candidates, or Chris directive.
