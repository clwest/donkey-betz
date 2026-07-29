# Session 3028 — S3027 helper de-layered + 3 silent promotion paths wired

**Date:** 2026-07-28 · **HEAD at close:** `28e3fc9fa` (PR #3744 merged) + docs cascade

## What shipped

**2 PRs merged this session.**

### PR #3743 (`4c9939484`) — `feat(s3028): de-layer S3027 broadcast helper + wire 3 silent promotion paths`

Chris directive at open was "extend the S3027 helper to `_impl_ai_promote_decisions`" (~30 min small slice). Cycle 1A verify-before-build discovered **two deeper issues**:

1. **Reverse-layering:** the S3027 helper lived in `core/views_agent_learning.py`. Services importing from a view module is layering backwards (views import services, not vice-versa). Wiring the helper into services would have baked that in.
2. **Three silent call sites, not one:**
   - `core/services/td_handlers_agents.py` PA tool `_handle_boardroom` action `promote_decision` (silent since S940)
   - `core/services/ai_decision_promoter.py` `AIDecisionPromoterService.promote_decision` (silent since S658)
   - `core/services/decision_promotion_rules.py` `DecisionPromotionRules.promote_decision` (silent since S589)

Fixing only the AI-AutoPromoter path Chris named would leave 2 silent paths + bake in the drift class the S3026 → S3027 arc has been fighting. Rigby A1 REVISE required Shape C: de-layer + wire all 3.

**Shape C implementation (all 4 Rigby A1 must-haves applied):**

1. **NEW `core/services/canonical_decision_broadcast.py`** (~90 lines). Exports `emit_canonical_promotion_broadcast(decision, *, request_id=None) -> bool`. Renamed from S3027's `_emit_...` — dropped private prefix now that it's a public services API. Same event shape as S3027 (schema_version:1, dual-key participants/agents_involved, rationale/stance accessor cascade, best-effort Redis try/except).
2. **All 3 silent paths wired.** Each new call site is a single helper call after successful promotion. `AIDecisionPromoterService` and `DecisionPromotionRules` moved the broadcast **outside** their `transaction.atomic()` (where present) so Redis-down never rolls back the field mutation.
3. **Behavioral contract identical.** Pure relocation; S3026 + S3027 tests pass unchanged.
4. **NEW `core/tests/test_s3028_canonical_broadcast_service_paths.py`** — 6 tests, one focused emit + one failure-survival test per new call site.

**View-layer callers updated** to import from the new services module (2 files: `promote_decision` single + `bulk_promote_decisions`).

### PR #3744 (`28e3fc9fa`) — `fix(s3028): PR-3743 A2 REVISE — drop lingering _emit_canonical_promotion_broadcast reference from test docstring`

Rigby A2 REVISE flagged one cosmetic item: the S3027 test file's module docstring still referenced the old private-prefixed function name. Updated docstring; noted rename provenance for future readers. Zero remaining refs to the old name in the codebase.

### Results

| Metric | Actual |
|---|---|
| PR #3743 diff | +341/-71, 6 files (1 new helper module, 1 new test file, 4 edited) |
| PR #3744 diff | +3/-1 (docstring only) |
| New S3028 suite | **6/6 pass in 0.295s** |
| S3026 + S3027 (helper move regression) | **10/10 pass in 0.945s** — pure relocation, tests unchanged |
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028) | **64/64 pass in 6.921s** |
| Post-merge `make recycle-all` | HEAD `4c9939484`, `sha=4c9939484b23` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**13th consecutive session** — Cycle 1A caught the scope expansion BEFORE any code was written. The 3-silent-sites discovery came from grepping every `promote_to_canonical` call site + every direct `is_canonical=True` mutation. Without that sweep, the session would have shipped Chris's ~30 min slice cleanly but left 2 known silent drift sites unfixed.

## Rigby SIGN quality this session

**3 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3027 pattern (**14 sessions continuous**).

Cycle summary:

1. **A1 SIGN — REVISE-approve-after Shape C** with 4 must-haves (all applied same-PR). Rigby explicitly rejected Shape A (partial fix would recreate drift) and Shape D (mutation-refactor is separate axis with different transaction semantics per service).
2. **A2 SIGN — REVISE.** Verified via `repo_tool`: helper exists + exported at correct path (PASS), all 3 services import from it (PASS), views_agent_learning no longer defines helper (PASS), but one lingering `_emit_...` reference in test docstring (FAIL). Fixed in PR #3744.
3. **A2 zoom-out folds** — 2 new observations documented as forward-carries (mutation-style drift + duplicate-broadcast risk).

## Folds (pattern evidence, not automatic escalation)

### Fold A `1st trigger` — Mutation-style drift across promotion services

Now that all 5 promotion paths are wired to the broadcast, the remaining drift is that:
- `promote_decision` single (view) + `bulk_promote_decisions` (view) + PA tool handler → all call `AgentDecisionSummary.promote_to_canonical(promoted_by=...)` model method.
- `AIDecisionPromoterService.promote_decision` → duplicates the field mutation inline, wrapped in `transaction.atomic()`.
- `DecisionPromotionRules.promote_decision` → duplicates the field mutation inline, NO transaction wrapper.

Three different mutation styles for the same conceptual operation. Functional equivalence held (all 3 flip `status='canonical'` + `is_canonical=True` + `promoted_at` + `promoted_by`), but the drift-risk pattern is exactly what S3026-S3028 has been closing for the broadcast side. Codification candidate: centralize on the model method. Different transaction semantics per service is the real complication — not a session-scale fix.

### Fold B `informational` — Duplicate-broadcast risk if two promotion paths race the same row

With all 5 paths broadcasting, a theoretical race exists: e.g., AI-AutoPromoter Celery task picks up row X → mutates fields + broadcasts, then a human hits Promote in the UI on the same row before their query saw the AI update. Second broadcast would fire for a row already canonical. Today's paths all gate on `is_canonical=False` at query time, so realistic risk is very low. Harden later via `did_promote` semantics (return early from mutation if row was already canonical, don't broadcast).

## Forward carries

### New from S3028

- **Fold A `1st trigger`** — mutation-style drift across 3 promotion services (2 duplicate the mutation inline, 1 wraps in atomic, 3 use the model method). Codification candidate: converge on model method.
- **Fold B `informational`** — duplicate-broadcast risk under theoretical concurrent-promotion race. Low today, hardenable via `did_promote` semantics.

### Carried from S3027 (STATUS PRESERVED)

- **None from S3027** — session shipped clean, no new folds.

### Carried from S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions should be backed by minimal failing test or stacktrace. S3028 clean-execution = additional counter-evidence. Codification pressure stays at 1st trigger.
- **S3026 Fold B `informational`** — 2 spec-invalidations in one session (S3026). S3028 didn't hit spec invalidation — Rigby's REVISE required a SCOPE expansion (2× larger than Chris named), not a premise invalidation. Watch signal for 3rd trigger stays open through S3031.
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

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** with A1 REVISE requiring scope expansion (Chris's ~30 min slice → 2× larger deliverable + 3 silent-site fixes). Delivered same-PR + follow-up PR for A2 REVISE.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 20 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "continue on with extending the S3027 helper" ratified S3028 primary. Scope expansion (3-silent-sites discovery) handled Claude+Rigby-side per `feedback_claude_rigby_agree_first_chris_yes_no`; Chris receives it in close summary.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3743 merge (`sha=4c9939484b23`). PR #3744 was docstring-only so didn't require re-recycle.
- **Fold classification (PLAYBOOK-6.10.8):** 2 new folds. Fold A `1st trigger`, Fold B `informational`. Rigby A1 REVISE conditions all applied same-PR; A2 REVISE resolved in follow-up PR #3744.
- **Verify-before-build (Cycle 1A):** **13th consecutive session** — 3-silent-sites discovery came from Cycle 1A grep sweep before any code was written.

## Wrapper pin note

Session-open pin was `pa-eaee6590fb9c43e1` (retired at S3027 close). Active during session: `pa-5879c8b150324a2f`. Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.
