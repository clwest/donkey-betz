# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3028 CLOSED. **S3027 broadcast helper de-layered + 3 silent promotion paths wired.** Chris asked for ~30 min slice (extend helper to AI-AutoPromoter); Cycle 1A grep sweep discovered TWO deeper issues (reverse-layering + 3 silent sites not 1). Rigby A1 REVISE required Shape C (de-layer + wire all 3). Helper moved to new `core/services/canonical_decision_broadcast.py`; PA tool handler + AI-AutoPromoter service + Session 589 rules service all now emit the same event as the boardroom endpoints. Byte-identical shape across all 5 promotion paths (regression-tested). 14-session zero-hallucination Rigby SIGN streak. **13th consecutive Cycle 1A verify-before-build session.**

**2 PRs shipped this session.**

**PR #3743 (`4c9939484`) — `feat(s3028): de-layer S3027 broadcast helper + wire 3 silent promotion paths`.**

- NEW `core/services/canonical_decision_broadcast.py` (~90 lines) exports `emit_canonical_promotion_broadcast(decision, *, request_id=None) -> bool`. Renamed from S3027's `_emit_...` (dropped private prefix now that it's a public services API). Same event shape as S3027 (schema_version:1, dual-key participants/agents_involved, rationale/stance accessor cascade, best-effort Redis try/except).
- 3 silent paths wired: PA tool `_handle_boardroom` action `promote_decision`, `AIDecisionPromoterService.promote_decision`, `DecisionPromotionRules.promote_decision`. AI + rules moved broadcast OUTSIDE their `transaction.atomic()` block so Redis-down never rolls back mutation.
- View-layer call sites (single + bulk) updated to import from the new services module.
- NEW `core/tests/test_s3028_canonical_broadcast_service_paths.py` (6 tests, one focused emit + one failure-survival per new call site).

**PR #3744 (`28e3fc9fa`) — `fix(s3028): PR-3743 A2 REVISE — drop lingering _emit_canonical_promotion_broadcast reference from test docstring`.** Cosmetic follow-up per Rigby A2 REVISE: S3027 test file docstring still referenced the old private-prefixed function name. Updated + noted rename provenance.

- **Test result:** New S3028 suite 6/6 pass in 0.295s. S3026+S3027 (helper-move regression): 10/10 pass in 0.945s (pure relocation). Full regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028): **64/64 pass in 6.921s**.
- **Behavior change:** all 5 promotion paths now emit the `canonical_policy_created` event on the `agent_learning` Redis channel. Downstream subscribers start receiving events for PA-driven, AI-AutoPromoter-driven, and Session 589 rules-driven promotions for the first time.

**HEAD at close:** docs cascade → `28e3fc9fa` (PR #3744).

Full context:
- `docs/handoffs/SESSION_3028_HELPER_DELAYERED_ALL_5_PROMOTION_PATHS_BROADCAST.md` — full session close.

---

## S3029 primary directive candidates

**No in-flight arc.** Chris directive-required. All 5 canonical-promotion paths now broadcast; the S3026 → S3028 arc closed a 5-years-old silent-drift class across the whole promotion surface. Remaining backlog is small-cleanup + new-engineering territory.

### Option A — Fresh engineering (bias-engineering rule)

- **S3028 Fold A codification: converge mutation style across 3 services.** Refactor `AIDecisionPromoterService.promote_decision` + `DecisionPromotionRules.promote_decision` to call `decision.promote_to_canonical(promoted_by=...)` model method instead of duplicating field mutation inline. Preserves transaction semantics per service (AI wraps in atomic; rules doesn't). Small (~30 min). Closes the second drift class the S3026-S3028 arc surfaced.
- **S3024 Fold A backend-source default preview API:** add `GET /api/platform/signal-cluster/<uuid>/default-initiative-name/` so frontend stops shadowing the backend default formatter. Watch-for-2nd-trigger candidate. ~1 session.
- **Extend broadcast pattern to `bulk_reject_decisions`:** add `canonical_decision_rejected` broadcast for symmetry. ~1 session.
- **`did_promote` idempotency semantics (S3028 Fold B):** gate broadcast on state-transition (mutation returns True only when row moved from non-canonical → canonical). Prevents double-fire under race. ~30 min.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction):** Extract chunking + row-status transitions. ~30-45 min.

### Option B — S3026 Fold A codification (2nd-trigger watch)

- **Fold evidence requirement:** "fold claim must be backed by minimal failing test or stacktrace." S3027 + S3028 both clean-executed with well-authored forward-carries → additional counter-evidence. Codification pressure stays at 1st trigger.

### Option C — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — S3026 removed the broken KT write; either add `DecisionPromotionLearningEvent` model or remap KT. Not urgent (5 years silent failure, no user impact). Multi-session.
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

**Joint recommendation at close:** **Option A — S3028 Fold A mutation-style convergence** (~30 min small slice). It closes the last drift axis in the promotion surface (broadcast side is done; mutation side is the last inconsistency). Cycle 1A friendly — reuses the model method already used by 3 of 5 paths. Alt: **`did_promote` idempotency** (~30 min) to close the S3028 Fold B duplicate-broadcast risk before it becomes a real race.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3028 handoff (`docs/handoffs/SESSION_3028_HELPER_DELAYERED_ALL_5_PROMOTION_PATHS_BROADCAST.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `28e3fc9fa` (PR #3744).
   - `python manage.py test core.tests.test_s3028_canonical_broadcast_service_paths --keepdb` — 6/6 OK.
   - Full regression bundle (8 files): 64/64 OK.

---

## S3029 carry-forward seeds

### New from S3028

- **Fold A `1st trigger`** — mutation-style drift across 3 promotion services (2 duplicate inline, 1 wraps in atomic, 3 use the model method). Codification candidate: converge on model method.
- **Fold B `informational`** — duplicate-broadcast risk under theoretical concurrent-promotion race. Low today; hardenable via `did_promote` semantics.

### Carried from S3027 (STATUS PRESERVED)

- **No new folds** — S3027 session shipped cleanly.

### Carried from S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions should be backed by minimal failing test or stacktrace. S3027 + S3028 both clean-executed → additional counter-evidence.
- **S3026 Fold B `informational`** — 2 spec-invalidations in one session. S3028 didn't spec-invalidate but did scope-expand 2×; distinct signal. Watch signal for 3rd trigger stays open through S3031.
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

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3027 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** with A1 REVISE requiring scope expansion (Chris's ~30 min slice → 2× larger deliverable + 3 silent-site fixes). Delivered same-PR + follow-up PR for A2 REVISE.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 20 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "continue on with extending the S3027 helper" ratified S3028 primary. Scope expansion handled Claude+Rigby-side.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3743 merge (`sha=4c9939484b23`). PR #3744 was docstring-only.
- **Fold classification (PLAYBOOK-6.10.8):** 2 new folds. Fold A `1st trigger`, Fold B `informational`.
- **Verify-before-build (Cycle 1A):** **13th consecutive session** — Cycle 1A grep sweep discovered the 3-silent-sites reality before any code was written.

---

## Wrapper pin note

The active PA conversation pin at S3028 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3028 executed the last major broadcast-side wiring in the S3026 → S3028 arc: canonical-promotion event now fires on all 5 promotion paths (2 view + 3 service) with byte-identical shape. Chris's ~30 min slice became a 2×-larger PR because verify-before-build discovered scope was 3× wider than the directive named — Rigby A1 REVISE approved the expansion because half-fixing would recreate the drift the arc has been closing. S3029 opens with mutation-style convergence (S3028 Fold A) as joint recommendation (~30 min, closes the last drift axis in the promotion surface) or `did_promote` idempotency (~30 min, closes S3028 Fold B).**
