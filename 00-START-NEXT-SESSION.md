# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3031 CLOSED. **S3026 → S3031 canonical-promotion drift + idempotency arc FULLY CLOSED (broadcast + mutation + historical heal + race elimination).** PR #3751 (`d7bb28b4f`) made `AgentDecisionSummary.promote_to_canonical` return `bool` (True if this call did the transition, False if row was already canonical) and wrapped `emit_canonical_promotion_broadcast` in `if did_promote:` at all 6 caller sites. Duplicate-broadcast race across 6 promotion paths now closed. 3 new tests + full regression **77/77 pass in 7.166s**. **17-session zero-hallucination Rigby SIGN streak. 16th consecutive Cycle 1A verify-before-build session.**

**2 feature PRs shipped this terminal session (S3030 + S3031, both ratified by Chris):**

- **PR #3749 (`e7fc79282`) — `feat(s3030): backfill_canonical_drift command`.** Heals `AgentDecisionSummary.filter(status='canonical', is_canonical=False)` drift rows created by 5 years of `.update(status='canonical')` bypassing model save. Dry-run default; `--apply` to heal; `--limit N` batching; promoted_at ← pre-heal updated_at proxy; marker `backfill-s3030-tasks-ops-drift`; no broadcast (rows too old). 5 new tests. Rigby explicitly deferred this from PR #3747; S3030 closes it.
- **PR #3751 (`d7bb28b4f`) — `feat(s3031): did_promote idempotency`.** Model method returns bool + early-exits if already canonical + `save(update_fields=[...])` containment. All 6 caller sites (`ai_decision_promoter`, `decision_promotion_rules`, `td_handlers_agents`, `tasks_ops`, `views_agent_learning` single + bulk) gate broadcast on return value. 3 new tests including end-to-end AI-service spy proving 2 calls = 1 broadcast.

**Arc close:** S3026 → S3031 canonical-promotion arc now fully closed across all 4 axes:
- Broadcast side (S3026 → S3028): all 6 paths emit `canonical_decision_promoted`.
- Mutation side (S3029): all 6 paths delegate to `promote_to_canonical()` model method.
- Historical drift (S3030): backfill command heals existing broken rows.
- Race elimination (S3031): duplicate-broadcast race closed via `did_promote` gating.

**HEAD at close:** docs cascade → `d7bb28b4f` (PR #3751).

Full context:
- `docs/handoffs/SESSION_3031_DID_PROMOTE_IDEMPOTENCY.md` — current session close.
- `docs/handoffs/SESSION_3030_BACKFILL_CANONICAL_DRIFT.md` — earlier this terminal session.

---

## S3032 primary directive candidates

**No in-flight arc.** S3026 → S3031 canonical-promotion arc FULLY closed. Two operator carries open (not sessions of code):
- Run `python manage.py backfill_canonical_drift --apply` against Railway prod (S3030 carry).
- Consider re-visiting Fold C 3rd-cycle codification (A2 zoom-out sweep pattern) — 3 cycles of evidence now (1 discovery + 2 clean sweeps). Could codify with "clean-sweep-confirms-closure" framing.

### Option A — Continue engineering (bias-engineering rule)

- **Extend broadcast pattern to `bulk_reject_decisions`:** add `canonical_decision_rejected` broadcast for symmetry. ~1 session.
- **S3024 Fold A backend-source default preview API:** removes frontend/backend default-formatter shadowing. Watch-for-2nd-trigger. ~1 session.
- **S3025 Fold C codification (BulkPromoteModal reducer extraction):** ~30-45 min.
- **Rigby Tool Gap Ledger substrate slate (S3030 Fold D):** add `AgentDecisionSummary` (and adjacent frequently-inspected S30XX models) to `orm_inspect_tool` allowlist. Enables Rigby to run ORM probes for future SIGN cycles without falling back to Django shell. ~30 min.
- **Fold C 3rd-cycle codification:** promote the "A2 zoom-out sweep for drift/hardening class" pattern into a Playbook rule. 3 cycles of evidence (S3029 discovery + S3030 + S3031 clean sweeps). ~30 min substrate + spec cycle.

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

**Joint recommendation at close:** either **`bulk_reject_decisions` symmetry** (~1 session, natural next adjacent play — extends broadcast pattern to the deprecation side of the promotion lifecycle) OR **Fold C 3rd-cycle codification** (~30 min, matures the A2-sweep pattern into a repeatable Playbook rule now that it's proven over 3 cycles). Both are small clean leans; either closes a still-open pattern-evidence loop.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3031 handoff (`docs/handoffs/SESSION_3031_DID_PROMOTE_IDEMPOTENCY.md`).
4. Optional state probes:
   - `git log --oneline -8` — should show docs cascade → `d7bb28b4f` (PR #3751).
   - Full regression bundle (12 files): 77/77 OK.

---

## S3032 carry-forward seeds

### New from S3031

- **Fold A `2nd trigger`** — boolean-return semantics discipline. Watch for 2nd `did_X`-style bool-return method on a similar mutation-with-side-effect shape to codify. `did_promote` mitigates via naming discipline, but the broader contract ("callers must treat False as idempotent no-op success, not error") is worth formalizing.
- **Fold C `3rd cycle, no discovery`** — A2 zoom-out sweep applied cleanly again in S3031. Codification pressure elevated but not automatic.

### Carried from S3030 (STATUS UPDATED)

- **S3030 Fold A `informational` (Rigby ORM allowlist gap)** — carried unchanged as S3031 Fold D. Ledger candidate for future substrate slate.
- **S3030 Fold B `informational` (spy fragility)** — carried unchanged as S3031 Fold B.
- **S3030 Fold C `2nd cycle`** — advanced to `3rd cycle, no-discovery` as S3031 Fold C.
- **S3030 Fold D `informational` (dup-broadcast race)** — **RESOLVED** by S3031 PR #3751.
- **S3030 prod deploy carry** — still open: run `backfill_canonical_drift --apply` against Railway prod.

### Carried from S3029 → S3026 (STATUS PRESERVED)

- **S3028 Fold A** — FULLY RESOLVED at S3029.
- **S3029 PR #3747 deferred item** — RESOLVED by S3030 PR #3749.
- **S3029 Fold A → S3030 Fold B → S3031 Fold B** — spy fragility (carried).
- **S3029 Fold B → S3030 Fold D** — RESOLVED by S3031 PR #3751.
- **S3029 Fold C → S3030 Fold C → S3031 Fold C** — 3rd cycle no-discovery.
- **S3026 Fold A `1st trigger`** — S3030 + S3031 A2 sweeps = additional supporting evidence. Codification pressure stays at 1st trigger.
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

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3030 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (PR #3751 planned end-to-end from S3030 forward-carry recommendation).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles this session (5× across S3030 + S3031 terminal). Zero rubber-stamp. 23 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris directive at S3030 close: "If you have the context can you knock out the did_promote in this terminal session?" — ratified the small clean lean.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3751, clean at `sha=d7bb28b4f91f`.
- **Fold classification (PLAYBOOK-6.10.8):** 4 folds. A 2nd trigger. B/D informational carried. C 3rd cycle no-discovery.
- **Verify-before-build (Cycle 1A):** **16th consecutive session** — read method + 6 caller sites + grep for missing callers + grep for adjacent silent writes before spec.

---

## Wrapper pin note

The active PA conversation pin at S3031 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3030 + S3031 shipped in the same terminal session (Chris ratified continuation). S3030 healed 5 years of historical drift; S3031 closed the last known race in the canonical-promotion arc via did_promote gating. The S3026 → S3031 arc is now FULLY CLOSED across all 4 axes (broadcast + mutation + historical heal + race elimination). S3032 opens with either `bulk_reject_decisions` symmetry (~1 session, adjacent extension) or Fold C 3rd-cycle codification (~30 min, matures a proven-over-3-cycles workflow pattern) as recommendations; Chris's own priority supersedes.**
