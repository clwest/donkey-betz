# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3027 CLOSED. **S3023 Fold B (re-scoped) shipped.** `bulk_promote_decisions` now emits the S3026-shaped `canonical_policy_created` Redis broadcast per row, via a shared `_emit_canonical_promotion_broadcast` helper both single + bulk endpoints call. Byte-identical event shape between the two paths (regression-tested via deep-equal). 13-session zero-hallucination Rigby SIGN streak. **12th consecutive Cycle 1A verify-before-build session** — extracted the S3026 broadcast code into a helper + reused mock patterns from `test_s3026_promote_decision_fold_c.py`. Zero new folds.

**1 PR shipped this session.**

**PR #3741 (`35c3ed0e5`) — `feat(s3027): S3023 Fold B re-scope — bulk_promote_decisions emits canonical broadcast via shared helper`.**

- **New module-level helper** `_emit_canonical_promotion_broadcast(decision, *, request_id=None) -> bool` at `core/views_agent_learning.py`. Only place in the file that owns `schema_version`, dual-key `participants`+`agents_involved`, `rationale/stance` accessor cascade, and the Redis publish try/except. Best-effort, non-fatal.
- **Single endpoint** (`promote_decision`): inline broadcast block REPLACED with helper call. `HTTP_X_REQUEST_ID` piped through for trace correlation.
- **Bulk endpoint** (`bulk_promote_decisions`): helper called inside existing per-row loop; tracks `broadcasts_succeeded`/`broadcasts_failed`; response additive-only (`{success, count, broadcasts_succeeded, broadcasts_failed, message}` — no per-row results[] per Rigby A1 REVISE #2).
- **NEW** `core/tests/test_s3027_bulk_promote_broadcast_parity.py` (5 tests): per-row broadcast, failure isolation, shape-parity regression guard (single==bulk minus timestamp/decision_id/topic), additive contract, edge case.
- **Test result:** 5/5 pass in 0.504s. Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027): **58/58 pass in 6.867s**.
- **Behavior change:** Bulk-promoted decisions now fire the Redis broadcast that has been missing since S942 (~Session 942). Any subscriber to `agent_learning` channel starts receiving events for bulk-promoted rows.

**HEAD at close:** docs cascade → `35c3ed0e5` (PR #3741).

Full context:
- `docs/handoffs/SESSION_3027_FOLD_B_BULK_PROMOTE_BROADCAST_PARITY.md` — full session close.

---

## S3028 primary directive candidates

**No in-flight arc.** Chris directive-required. S3023 folds are now fully closed (Fold B RESOLVED S3027, Fold C RESOLVED S3026, Fold A still `informational`, Fold D still `1st trigger`). Backlog trending toward small-cleanup + design-arc candidates.

### Option A — Fresh engineering (bias-engineering rule)

- **S3024 Fold A backend-source default preview API:** add `GET /api/platform/signal-cluster/<uuid>/default-initiative-name/` (or bulk variant) so frontend stops shadowing the backend default formatter (`defaultNameFor()` mirrors backend logic). Watch-for-2nd-trigger candidate — the drift class is real and S3026/S3027 arc reinforces the general "avoid shadowed transport shapes" principle. ~1 session.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction):** Extract chunking + row-status transitions before U8+ lands more logic in the modal. ~30-45 min.
- **Extend broadcast pattern to bulk_reject_decisions:** the helper is now available; add a `canonical_decision_rejected` broadcast for the rejection path (currently silent). Adjacent Cycle 1A win — reuses S3027 helper pattern. ~1 session.
- **Extend broadcast pattern to `AI-AutoPromoter` (`core/tasks_misc.py:2802 _impl_ai_promote_decisions`):** the ai-promote Celery task also calls `promote_to_canonical` but doesn't emit the broadcast. Add a call to the S3027 helper. ~30 min.

### Option B — S3026 Fold A codification (2nd-trigger watch)

- **Fold evidence requirement:** "fold claim must be backed by minimal failing test or stacktrace pointing at true first-cause." S3027 clean-execution provided contrast evidence for well-authored forward-carries; codification pressure stays at 1st trigger. Watch for 2nd trigger in a session where an ill-described fold burns real work.

### Option C — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — S3026 removed the broken KT write; either add `DecisionPromotionLearningEvent` model or remap KT. Not urgent (5 years silent failure with no user impact). Multi-session.
- **Governance unification (Rigby A1 zoom-out standing carry, S3023):** HAI vs ADS lifecycle families. Multi-session.

### Option D — Continue audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.
- **Audit script multiline regex extension.**

### Option E — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option F — Chris's own priority (supersedes A-E)

**Joint recommendation at close:** **Option A — extend broadcast pattern to `AI-AutoPromoter` (`_impl_ai_promote_decisions`)**. Small (~30 min), reuses S3027 helper, closes the same silent-drift class for the Celery-driven promotion path that Fold C+B just closed for the human-driven paths. Alt: **Option A — bulk_reject_decisions broadcast** (~1 session, extends helper pattern further).

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3027 handoff (`docs/handoffs/SESSION_3027_FOLD_B_BULK_PROMOTE_BROADCAST_PARITY.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `35c3ed0e5` (PR #3741).
   - `python manage.py test core.tests.test_s3027_bulk_promote_broadcast_parity --keepdb` — 5/5 OK.
   - Full regression bundle (7 files): 58/58 OK.

---

## S3028 carry-forward seeds

### New from S3027

- **None.** Session shipped 1 PR cleanly; no new folds or non-MVP followups.
- **Substrate strengthened:** `_emit_canonical_promotion_broadcast` helper is now available for future decision-lifecycle broadcasts (rejection, deferral, AI-auto-promote, etc.).

### Carried from S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions should be backed by minimal failing test or stacktrace. S3027 clean-execution = counter-evidence; codification pressure stays at 1st trigger.
- **S3026 Fold B `informational`** — 2 spec-invalidations in one session; watch for 3rd trigger in next 5 sessions.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment for canonical decision persistence.

### Carried from S3025 (STATUS PRESERVED)

- **S3025 Fold A `informational`** — `chunks.indexOf(chunk)` inside loop.
- **S3025 Fold B `informational`** — cancelled rows revert to `pending` glyph.
- **S3025 Fold C `codification candidate`** — `BulkPromoteModal` complexity growth. Watch: next PR adding 4th responsibility triggers extraction.

### Carried from S3024 (STATUS PRESERVED)

- **Fold A `1st trigger`** — cross-tier default-formatting shadowing.
- **Fold B `informational`** — silent-fallback vs strict-validate asymmetry.

### Carried from S3023 (ALL FOLDS RESOLVED OR STANDING)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes. S3027 supports "well-authored forward-carries execute cleanly."
- **S3023 Fold B** — **RESOLVED** by S3027 PR #3741.
- **S3023 Fold C** — RESOLVED by S3026 PR #3738.
- **S3023 Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract.
- **Decision lifecycle parity (Rigby A1 zoom-out standing carry)** — HAI vs ADS lifecycle families still fragmented.

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3026 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (clean execution, zero abort-early invocations after 2 in S3026).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 19 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "start s3023 fold b" ratified S3027 primary — joint recommendation from S3026 close matched Chris directive exactly.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-merge (`sha=35c3ed0e5a33`).
- **Fold classification (PLAYBOOK-6.10.8):** 0 new folds. All Rigby A1 REVISE conditions applied same-PR.
- **Verify-before-build (Cycle 1A):** **12th consecutive session** — helper extraction reused S3026 code; tests reused S3026 mock pattern.

---

## Wrapper pin note

The active PA conversation pin at S3027 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3027 executed S3023 Fold B (re-scoped after S3026) cleanly in one PR: extracted the S3026 broadcast code into a shared helper, wired bulk endpoint to it, added drift-regression test. Fold B + Fold C both closed. S3028 opens with `_impl_ai_promote_decisions` broadcast extension as joint recommendation (~30 min small-slice reuse) or `bulk_reject_decisions` broadcast (~1 session, extends helper pattern) — both are Cycle 1A wins that reuse the S3027 helper.**
