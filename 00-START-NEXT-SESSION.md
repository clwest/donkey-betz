# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3029 CLOSED. **S3028 Fold A mutation-style convergence shipped + 4th silent site discovered & fixed same-session.** PR #3746 converged AI-AutoPromoter + Rules services onto the `promote_to_canonical` model method. Rigby A2 zoom-out sweep discovered a 4th silent site in `core/tasks_ops.py` — a bulk `.update(status='canonical')` in the scheduled boardroom-auto-approve task that was leaving `is_canonical=False`, `promoted_at=NULL`, `promoted_by=NULL` on every auto-promoted row (data integrity breach + silent broadcast, silent since ~S988). PR #3747 fixed it same session with per-row model-method loop + broadcast. 15-session zero-hallucination Rigby SIGN streak. **14th consecutive Cycle 1A verify-before-build session.**

**2 feature PRs shipped this session.**

**PR #3746 (`2b72a973e`) — `feat(s3029): S3028 Fold A — mutation-style convergence`.** Both services now call `decision.promote_to_canonical(promoted_by=...)`. Per-service transaction semantics INTENTIONALLY preserved (AI wraps in atomic; Rules doesn't). 2 spy tests using `patch.object(..., autospec=True, side_effect=lambda self, promoted_by='human': original(...))` to preserve real bound-method behavior while asserting the model method was called.

**PR #3747 (`d0841a0f6`) — `fix(s3029): PR-3746 A2 sweep follow-up — tasks_ops.py 4th silent site + data integrity fix`.** Rigby A2 zoom-out sweep discovery. 4 duplicated `.update(status='canonical')` blocks in `_impl_auto_approve_boardroom_items` consolidated into per-row loop over `_AUTO_PROMOTE_TYPES = ['experiment', 'pipeline', 'research', 'guideline']`. Single atomic per type; broadcast outside atomic. 3 tests including all-4-fields check + Redis-down survival.

- **Test result:** New S3029 convergence 2/2 + new S3029 tasks_ops 3/3 pass. Full regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028 + S3029 [both]): **69/69 pass in 7.107s**.
- **Behavior change:** all 6 canonical-promotion paths (was 5; +1 discovered via sweep) now delegate to the model method + fire broadcasts. Downstream `is_canonical=True` queries finally see auto-promoted rows going forward.

**HEAD at close:** docs cascade → `d0841a0f6` (PR #3747).

Full context:
- `docs/handoffs/SESSION_3029_MUTATION_CONVERGENCE_AND_4TH_SITE_DISCOVERY.md` — full session close.

---

## S3030 primary directive candidates

**No in-flight arc.** S3026 → S3029 arc closed the entire canonical-promotion drift class across all 6 paths (broadcast side + mutation side). **One known data-integrity residue open:** existing rows with `status='canonical'` but `is_canonical=False` from 5 years of the S3029 PR #3747 bug. Rigby explicitly deferred backfill from PR #3747 to S3030.

### Option A — S3030 primary (joint recommendation): backfill existing drift rows

- **NEW management command `python manage.py backfill_canonical_drift`.** Audit + backfill for `AgentDecisionSummary.objects.filter(status='canonical', is_canonical=False)`. Suggested shape:
  - Dry-run mode default (report count + sample rows without writing).
  - `--apply` flag to actually backfill: sets `is_canonical=True`, `promoted_at=created_at` (best-guess since the actual promotion time is lost), `promoted_by='backfill-s3030-from-tasks-ops-drift'`.
  - Optional: also emit broadcast for backfilled rows (or explicitly document why NOT — these rows are years old; subscribers probably shouldn't receive belated events).
  - Regression test asserts drift rows are healed + counts match.
- **Cost:** ~1 session (~100 lines command + tests).

### Option B — Continue engineering (bias-engineering rule)

- **S3029 Fold C codification watch (2nd trigger):** if S3030 or S3031 A2 zoom-out sweep catches another adjacent silent bug, codify "A2 SIGN routinely includes a repo-wide sweep for the drift-class being fixed" as a workflow rule.
- **S3024 Fold A backend-source default preview API:** removes frontend/backend default-formatter shadowing. Watch-for-2nd-trigger. ~1 session.
- **Extend broadcast pattern to `bulk_reject_decisions`:** add `canonical_decision_rejected` broadcast for symmetry. ~1 session.
- **`did_promote` idempotency (S3029 Fold B, elevated from S3028 Fold B):** gate broadcast on state-transition. ~30 min.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction):** ~30-45 min.

### Option C — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — Multi-session.
- **Governance unification (Rigby A1 zoom-out standing carry, S3023):** HAI vs ADS lifecycle families. Multi-session.

### Option D — Audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.
- **Audit script multiline regex extension.**

### Option E — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option F — Chris's own priority (supersedes A-E)

**Joint recommendation at close:** **Option A — backfill existing drift rows.** It's the direct forward-carry from PR #3747 (Rigby explicitly deferred), it closes the last known residue of the S3026-S3029 arc, and it's genuinely useful (5 years of accumulated drift rows are currently invisible to `is_canonical=True` queries used across `policy_context.py`, `views_project_intelligence.py`, `views_agent_learning.py`, `project_intelligence_consumer.py`). Alt: **`did_promote` idempotency** (~30 min) to close Fold B if a smaller slice is wanted.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3029 handoff (`docs/handoffs/SESSION_3029_MUTATION_CONVERGENCE_AND_4TH_SITE_DISCOVERY.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `d0841a0f6` (PR #3747).
   - Full regression bundle (10 files): 69/69 OK.

---

## S3030 carry-forward seeds

### New from S3029

- **Fold A `informational`** — spy `side_effect=lambda` signature fragility (future required kwarg silently forwards wrong args). Codification candidate: swap for `*args, **kwargs` forwarder.
- **Fold B `informational`** (elevated from S3028 Fold B) — duplicate-broadcast race across 6 promotion paths. Harden via `did_promote` semantics.
- **Fold C `1st trigger`** — codify A2-zoom-out-sweep-for-drift-class pattern. Watch for 2nd trigger.
- **PR #3747 deferred item** — backfill migration/command for existing drift rows (S3030 primary candidate).

### Carried from S3028 (STATUS UPDATED)

- **S3028 Fold A** — **FULLY RESOLVED** across all 6 paths (was 5 known; +1 via S3029 A2 sweep).
- **S3028 Fold B** — folded into S3029 Fold B (same content).

### Carried from S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions backed by evidence. S3029 A2-zoom-out sweep = supporting evidence.
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 (STATUS PRESERVED)

- **S3025 Fold A `informational`** — `chunks.indexOf(chunk)` inside loop.
- **S3025 Fold B `informational`** — cancelled rows revert to `pending` glyph.
- **S3025 Fold C `codification candidate`** — `BulkPromoteModal` complexity growth.

### Carried from S3024 (STATUS PRESERVED)

- **Fold A `1st trigger`** — cross-tier default-formatting shadowing.
- **Fold B `informational`** — silent-fallback vs strict-validate asymmetry.

### Carried from S3023 (ALL FOLDS RESOLVED OR STANDING)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes.
- **S3023 Fold B** — RESOLVED S3027.
- **S3023 Fold C** — RESOLVED S3026.
- **S3023 Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract.
- **Decision lifecycle parity (Rigby A1 zoom-out standing carry)** — HAI vs ADS lifecycle families.

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3028 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× Flow B spec→ship** (PR #3746 planned; PR #3747 discovered via A2 zoom-out sweep + shipped same-session).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 21 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "Lets keep going please" continuing the S3026-S3029 arc.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` twice (once per PR).
- **Fold classification (PLAYBOOK-6.10.8):** 3 folds. Fold A + B `informational`, Fold C `1st trigger`.
- **Verify-before-build (Cycle 1A):** **14th consecutive session** — Rigby A2 zoom-out sweep caught adjacent silent bug.

---

## Wrapper pin note

The active PA conversation pin at S3029 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3029 executed the S3028 Fold A convergence cleanly, then Rigby's A2 zoom-out sweep discovered a 4th silent site (data-integrity breach in a scheduled Celery task) which shipped as PR #3747 same-session. All 6 canonical-promotion paths now converged on the model method + broadcast. S3030 opens with the backfill migration for existing drift rows as joint recommendation — Rigby explicitly deferred this from PR #3747, and it's the last known residue of the S3026-S3029 arc.**
