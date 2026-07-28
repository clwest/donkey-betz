# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3022 CLOSED. **U5b backfill shipped as data migration 0404.** Pre-U5 stranded Initiatives (parent_topic string but NULL FK) now normalized. Audit surfaced tiny scope: N=3 all-clean, all-resolvable. Rigby endorsed data-migration shape over management-command ceremony after seeing numbers. Post-migration: 4/4 rows linked, 0 NULL. 60/60 S3013-S3021 tests still pass. 8-session zero-hallucination Rigby SIGN streak. **U5 arc (U5 + U5b) fully closed in 2 sessions.**

**1 feature PR shipped this session.**

**PR #3729 (`1ff5475c4`) — `feat(s3022): U5b — backfill Initiative.signal_cluster FK from parent_topic (data migration 0404)`.**

- **NEW** `core/migrations/0404_s3022_backfill_initiative_signal_cluster_fk.py` — data migration, `apps.get_model` + idempotent + skip-on-missing + `RunPython.noop` reverse.
- **Migration output:** `linked=3 skipped_malformed=0 skipped_missing_cluster=0`.
- **Post-migration ORM verify:** 4/4 rows linked, 0 NULL.
- **Test result:** S3013-S3021 subset: 60/60 pass in 8.828s.
- **Deferred (per Rigby):** management command not shipping until 2nd batch of stranded rows appears (evidence of drift from alternate writer path).

**HEAD at close:** docs cascade → `1ff5475c4` (PR #3729).

Full context:
- `docs/handoffs/SESSION_3022_U5B_INITIATIVE_SIGNAL_CLUSTER_FK_BACKFILL.md` — full session close.

---

## S3023 primary directive candidates

**No in-flight arc.** Chris directive-required. **U5 auto-link arc fully closed** (U5 writer + U5b backfill, 2 sessions). Fresh engineering queue is next.

### Option A — Continue fresh engineering (bias-engineering rule)

- **U4:** AgentDecisionSummary bulk-decide (referenced in S3014 handoff, carried through S3015-S3022). ~1 session.
- **U6:** per-row name editing in bulk cluster confirm modal. Currently bulk always uses defaults. ~1 session.
- **Progress bar for bulk create** (SSE or optimistic UI): from S3015 forward-carry.

### Option B — Continue audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.
- **Audit script multiline regex extension** — catch `.filter(...)\n.get(...)` split across lines.
- **Extend predicate universe** as new predicates land.

### Option C — S3018 Fold extensions

- **Fold B (S3018 REVISE-2):** test-time advisory telemetry for decorator-chain-break. ~1 session.
- **Method-decorator detection extension:** catch `@method_decorator(superuser_required)` on CBV methods. ~1 session.

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option E — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry.
- 9th test coupling from S3013 non-blocking carry.

### Option F — Chris's own priority (supersedes A-E)

**Joint recommendation at close:** **Option A U4 (AgentDecisionSummary bulk-decide)** — natural next in the user-facing bulk-actions arc (S3013 U1 → S3014 U2 → S3015 U3 → S3021 U5 → S3022 U5b → S3023 U4). Ships another user-visible capability.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3022 handoff (`docs/handoffs/SESSION_3022_U5B_INITIATIVE_SIGNAL_CLUSTER_FK_BACKFILL.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `1ff5475c4` (PR #3729) → `3e80f6ce3` (S3021 close cascade).
   - `python manage.py showmigrations core | tail -5` — 0404 should show `[X]`.
   - `python manage.py test core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters --keepdb` — 22/22 OK.

---

## S3023 carry-forward seeds

### New from S3022

- **Management command for FK backfill** — NOT shipped this session per Rigby. Ship only if second batch of stranded rows appears. Non-action carry (conscious defer).
- **Fold A `informational`** — audit-first-then-shape-decide for backfill scope (codification candidate).
- **Fold B `informational`** — `RunPython.noop` reverse for deterministic-linkage backfills (codification candidate — migration template comment?).

### Carried from S3021 (STATUS UPDATED)

- **S3021 U5b backfill** — **CLOSED by S3022 PR #3729**.
- **S3021 Fold A (backfill-as-separate-PR)** — still `1st trigger` on codification path.
- **S3021 Fold B (hivemind direct-set-then-fallback pattern)** — still `informational`.
- **S3021 Fold C (Rigby T1 REVISE catches something)** — 5-session streak ended at S3021; not extended at S3022 (design was clean; audit numbers matched expectation; migration shape converged on first pass). Recorded as observation only.

### Carried from S3020 (STATUS PRESERVED)

- **S3020 Fold A** — audit script per-hit / per-function suppression refactor.
- **S3020 Fold B** — `scope_queryset_memory_cluster` predicate candidate.
- **Audit multiline chained `.filter(...).get(...)` regex extension.**
- **Predicate universe expansion.**

### Carried from S3019 (STATUS PRESERVED)

- **S3019 Fold B (predicate-shape-table)** — still open.

### Carried from S3018 (STATUS PRESERVED)

- **S3018 Fold B (test-time advisory for decorator-chain-break)** — still open, future arc.
- **S3018 Fold D (Rigby response truncation)** — still at 1st trigger.
- **Method-decorator detection extension** — still open.

### Carried from S3017 / older — all preserved from S3021 close 00-START (see S3021 + S3022 handoffs).

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (audit → shape-recalibrate → implement → verify → ship → recycle-all).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 14 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive ("begin U5b backfill") + merge decision via Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3729 merge.
- **Fold classification (PLAYBOOK-6.10.8):** 2× `informational` (audit-first-then-shape, RunPython.noop reverse for deterministic-linkage backfills).

---

## Wrapper pin note

The active PA conversation pin at S3022 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3022 shipped 1-PR U5b backfill via data migration after audit surfaced tiny scope (N=3 all-clean). Rigby recalibrated the shape after seeing numbers. The U5 arc (U5 + U5b) is fully closed in 2 sessions. S3023 opens with U4 (AgentDecisionSummary bulk-decide) as joint recommendation — natural next in the user-facing bulk-actions series.**
