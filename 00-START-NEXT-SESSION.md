# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3030 CLOSED. **S3026 → S3029 canonical-promotion drift arc FULLY CLOSED.** PR #3749 shipped `backfill_canonical_drift` management command healing 5 years of `AgentDecisionSummary` drift rows (status='canonical' + is_canonical=False from bulk `.update()` in the scheduled boardroom-auto-approve task, silent since ~S988). Dry-run default, `--apply` flag, `--limit N` for batching. Per-row atomic + try/except; `promoted_at` restored to pre-heal `updated_at` proxy (true time unrecoverable); marker `promoted_by='backfill-s3030-tasks-ops-drift'`; deliberately no broadcast (rows years old, belated events misleading). **16-session zero-hallucination Rigby SIGN streak. 15th consecutive Cycle 1A verify-before-build session.**

**1 feature PR shipped this session.**

**PR #3749 (`e7fc79282`) — `feat(s3030): backfill_canonical_drift command`.** Heals `AgentDecisionSummary.objects.filter(status='canonical', is_canonical=False)`. Rigby explicitly deferred this from PR #3747 at S3029 close. Rigby A2 zoom-out sweep this session confirmed ZERO other lingering silent sites in the same drift class (7 `repo_tool` searches: no other `.update(status='canonical')` in production, no `update(**{})` kwargs-shape hiding same bug, no adjacent 'published/is_published' models at risk, marker doesn't collide with existing AI-heuristic aggregate). 5 new tests + full regression bundle **74/74 pass in 7.547s**.

- **Test result:** New S3030 5/5 + full regression (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028 + S3029 [both] + S3030) **74/74 pass in 7.547s**. Baseline 69/69 at S3029 close; +5 new = 74.
- **Behavior change:** command available for prod. Local DB has 0 rows; Chris runs on Railway prod to heal accumulated drift. Downstream `is_canonical=True` consumers (policy_context, views_project_intelligence, views_agent_learning, project_intelligence_consumer, agent_intelligence_context, auto_kpi_tracking, pa_intelligence_enricher, experiment_suggestion) will see the healed rows after the prod run.

**HEAD at close:** docs cascade → `e7fc79282` (PR #3749).

Full context:
- `docs/handoffs/SESSION_3030_BACKFILL_CANONICAL_DRIFT.md` — full session close.

---

## S3031 primary directive candidates

**No in-flight arc.** S3026 → S3030 arc FULLY closed the entire canonical-promotion drift class:
- Broadcast side (S3026 → S3028): all 6 promotion paths emit `canonical_decision_promoted`.
- Mutation side (S3029): all 6 paths delegate to `promote_to_canonical()` model method.
- Historical drift (S3030): backfill command healing existing broken rows.

**Open carry that requires operator action, not new code:** run `python manage.py backfill_canonical_drift --apply` on Railway prod to heal accumulated drift. Not a session's worth of work; either Chris runs manually or fold into a routine prod-ops session.

### Option A — Continue engineering (bias-engineering rule)

- **S3029 Fold C 2nd cycle codification watch:** A2-zoom-out-sweep pattern applied cleanly in S3030 with zero discovery — this is a "pattern works even when it finds nothing" signal, not a 2nd-catch signal. Watch for a genuine 2nd discovery in the next few sessions to elevate codification pressure. Not urgent.
- **S3024 Fold A backend-source default preview API:** removes frontend/backend default-formatter shadowing. Watch-for-2nd-trigger. ~1 session.
- **Extend broadcast pattern to `bulk_reject_decisions`:** add `canonical_decision_rejected` broadcast for symmetry. ~1 session.
- **`did_promote` idempotency (S3029 Fold B → S3030 Fold D):** gate broadcast on state-transition to close the duplicate-broadcast race. ~30 min.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction):** ~30-45 min.
- **Rigby Tool Gap Ledger update (S3030 Fold A):** add `AgentDecisionSummary` (and adjacent frequently-inspected S30XX models) to `orm_inspect_tool` allowlist. Enables Rigby to run ORM probes for future SIGN cycles without Claude having to drop to Django shell. ~30 min substrate slate.

### Option B — Design-arc candidates (needs Chris ratification)

- **KnowledgeTransfer model realignment for canonical decision persistence** — Multi-session.
- **Governance unification (Rigby A1 zoom-out standing carry, S3023):** HAI vs ADS lifecycle families. Multi-session.

### Option C — Audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.
- **Audit script multiline regex extension.**

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option E — Chris's own priority (supersedes A-D)

**Joint recommendation at close:** **Option A — `did_promote` idempotency** (~30 min, closes S3030 Fold D + finally hardens the last known race condition in the canonical-promotion arc) OR **Rigby Tool Gap Ledger substrate slate** (~30 min, unblocks future SIGN cycles from Django-shell dependency). Either is a small clean lean. If wanting a fresh arc, the `bulk_reject_decisions` symmetry (~1 session) is the natural next canonical-promotion adjacent play.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3030 handoff (`docs/handoffs/SESSION_3030_BACKFILL_CANONICAL_DRIFT.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `e7fc79282` (PR #3749).
   - Full regression bundle (11 files): 74/74 OK.

---

## S3031 carry-forward seeds

### New from S3030

- **Fold A `informational` (NEW)** — Rigby ORM allowlist gap for `AgentDecisionSummary`. Ledger candidate for future substrate slate.
- **Fold B `informational` (carried from S3029 Fold A)** — spy `side_effect=lambda` signature fragility.
- **Fold C `2nd cycle, no discovery`** — A2 zoom-out sweep applied cleanly, zero residue. Different signal than S3029 discovery. Watch for genuine 2nd discovery.
- **Fold D `informational` (carried from S3029 Fold B)** — duplicate-broadcast race across 6 promotion paths.
- **Prod deploy carry** — run `backfill_canonical_drift --apply` on Railway prod. Not a session's worth of work; operator action.

### Carried from S3029 (STATUS UPDATED)

- **S3029 Fold A** — carried as S3030 Fold B (same content).
- **S3029 Fold B** — carried as S3030 Fold D (same content).
- **S3029 Fold C `1st trigger`** — advanced to `2nd cycle, no-discovery` as S3030 Fold C.
- **S3029 PR #3747 deferred item** — **RESOLVED** by S3030 PR #3749.

### Carried from S3026 → S3028 (STATUS PRESERVED)

- **S3028 Fold A** — FULLY RESOLVED at S3029.
- **S3026 Fold A `1st trigger`** — S3030 A2 sweep = supporting evidence (Rigby's tool-grounded `repo_tool` sweep). Codification pressure stays at 1st trigger.
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

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3029 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (PR #3749 planned end-to-end from S3029 forward-carry).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 22 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris session-open directive "Please begin Backfill migration..." ratified the direction; joint Claude+Rigby AGREE on shape; no mid-flight routing needed.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3749, clean at `sha=e7fc7928284e`.
- **Fold classification (PLAYBOOK-6.10.8):** 4 folds. A informational new. B/D informational carried. C 2nd cycle no-discovery.
- **Verify-before-build (Cycle 1A):** **15th consecutive session** — read model + method + template backfill commands + 12 downstream consumers before spec.

---

## Wrapper pin note

The active PA conversation pin at S3030 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3030 executed the S3029 deferred backfill cleanly, and Rigby's A2 zoom-out sweep confirmed ZERO other lingering silent sites in the drift class. All 6 canonical-promotion paths converged (broadcast + mutation + historical heal). The S3026 → S3030 arc is FULLY CLOSED. S3031 opens with a small clean lean (`did_promote` idempotency, ~30 min) or an adjacent extension (`bulk_reject_decisions` symmetry, ~1 session) as recommendation; Chris's own priority supersedes.**
