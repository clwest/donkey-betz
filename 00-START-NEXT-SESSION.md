# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3021 CLOSED. **U5 auto-link shipped in 1 PR with in-PR test tightening fold.** Direct-set `Initiative.signal_cluster` FK at create time in the shared U2/U3 factory `_create_initiative_from_cluster_core` (1 line of prod code + 2 tests). Chose direct-set over `auto_link_initiative_signals()` (embedding search) because we know the source cluster deterministically — matches existing precedent at `hivemind_execution_pipeline.py:503+519`. Live smoke: cluster `2795af6c...` → POST 200 → initiative `ce474a55...` with `signal_cluster_id` matching request cluster ✅. 60/60 S3013-S3020 tests + 22/22 S3014+S3015 (with 2 new) still pass. **Rigby T1 catches 5 sessions in a row** (S3017-S3021).

**1 feature PR shipped this session.**

**PR #3727 (`68bc94510`) — `feat(s3021): U5 — direct-link Initiative.signal_cluster FK in cluster→initiative factory`.**

- **MODIFIED** `core/views_platform_command.py` — added `signal_cluster=cluster` kwarg to Initiative.objects.create() inside `_create_initiative_from_cluster_core`. 1 line of prod code.
- **MODIFIED** `core/tests/test_s3014_create_initiative_from_cluster.py` — new test `test_signal_cluster_fk_set_at_create_time`.
- **MODIFIED** `core/tests/test_s3015_bulk_create_initiatives_from_clusters.py` — new test `test_signal_cluster_fk_set_at_create_time_bulk` (with Rigby A2 fold: parent_topic + FK pair in same assertion block).
- **Test result:** S3014+S3015: 22/22 pass in 2.520s. S3013-S3020 subset: 60/60 pass in 8.502s.
- **Live smoke:** cluster → initiative create → ORM verify FK set + parent_topic preserved ✅.

**HEAD at close:** docs cascade → `68bc94510` (PR #3727).

Full context:
- `docs/handoffs/SESSION_3021_U5_AUTO_LINK_SIGNAL_CLUSTER_FK.md` — full session close.

---

## S3022 primary directive candidates

**No in-flight arc.** Chris directive-required. **1 fresh-engineering session shipped**, streak reset. Backfill for pre-U5 initiatives is the natural next engineering item; alternates are audit-track continuation.

### Option A — U5 backfill follow-up (natural continuation)

- **U5b:** backfill `Initiative.signal_cluster_id` from `parent_topic='signal_cluster:<uuid>'` where FK is NULL. Rigby-suggested shape: audit query first (count eligible + failure-parse tail), then batched management command with dry-run mode. ~30-60 min.

### Option B — More fresh engineering

- **U4:** AgentDecisionSummary bulk-decide. ~1 session.
- **U6:** per-row name editing in bulk cluster confirm modal. ~1 session.
- **Progress bar for bulk create** (SSE or optimistic UI): from S3015 forward-carry.

### Option C — Continue audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.
- **Audit script multiline regex extension** — catch `.filter(...)\n.get(...)` split across lines.
- **Extend predicate universe** as new predicates land.

### Option D — S3018 Fold extensions

- **Fold B (S3018 REVISE-2):** test-time advisory telemetry for decorator-chain-break. ~1 session.
- **Method-decorator detection extension:** catch `@method_decorator(superuser_required)` on CBV methods. ~1 session.

### Option E — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option F — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry.
- 9th test coupling from S3013 non-blocking carry.

### Option G — Chris's own priority (supersedes A-F)

**Joint recommendation at close:** **Option A (U5b — backfill)** for closing the U5 loop while the design context is fresh. If Chris wants to keep building forward, Option B U4 or U6 is next in the fresh-engineering queue.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3021 handoff (`docs/handoffs/SESSION_3021_U5_AUTO_LINK_SIGNAL_CLUSTER_FK.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `68bc94510` (PR #3727) → `e1358b3cb` (S3020 close cascade).
   - `python manage.py test core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters --keepdb` — 22/22 OK.
   - For U5b: `Initiative.objects.filter(parent_topic__startswith='signal_cluster:', signal_cluster__isnull=True).count()` — audit-first eligibility count.

---

## S3022 carry-forward seeds

### New from S3021

- **U5b backfill candidate** — pre-U5 initiatives created via U2/U3 have `signal_cluster_id=NULL` even though `parent_topic='signal_cluster:<uuid>'`. Rigby-suggested shape: audit → dry-run → batched writes.
- **Fold A `1st trigger`** — backfill-as-separate-PR for FK-population changes (codification candidate).
- **Fold B `informational`** — hivemind direct-set-then-fallback pattern as canonical cluster→initiative shape.
- **Fold C** — Rigby A2 tool-grounded test-tightening catch (5th consecutive REVISE-catches-something session; T1 REVISE pattern remains validated).

### Carried from S3020 (STATUS PRESERVED)

- **S3020 Fold A** — audit script per-hit / per-function suppression refactor.
- **S3020 Fold B** — `scope_queryset_memory_cluster` predicate candidate (watch for 2nd trigger).
- **Audit multiline chained `.filter(...).get(...)` regex extension.**
- **Predicate universe expansion** as new predicates land.

### Carried from S3019 (STATUS PRESERVED)

- **S3019 Fold B (predicate-shape-table)** — still open.

### Carried from S3018 (STATUS PRESERVED)

- **S3018 Fold B (test-time advisory for decorator-chain-break)** — still open, future arc.
- **S3018 Fold D (Rigby response truncation)** — still at 1st trigger.
- **Method-decorator detection extension** — still open.

### Carried from S3017 / older — all preserved from S3020 close 00-START (see S3020 + S3021 handoffs for full carry list).

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship + 1× in-PR REVISE fold (test tightening).**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles (design-fork + A2 with tool-grounded diff). Zero rubber-stamp. 13 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: initial directive at session-open (Option A U5 auto-link, plain-English) + single merge decision via Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3727 merge.
- **Fold classification (PLAYBOOK-6.10.8):** 1× `same_pr_actionable → resolved` (test tightening). 1× `future_arc → deferred` (backfill scope). 1× `informational` (hivemind pattern precedent).

---

## Wrapper pin note

The active PA conversation pin at S3021 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3021 shipped 1-PR fresh engineering (U5 direct-link) with in-PR Rigby A2 test-tightening fold. The 5-session memory-* auth arc closed at S3020; S3021 opens a natural follow-up (U5b backfill) OR continued fresh engineering (U4, U6). Rigby T1 REVISE-catches-something now at 5 sessions continuous.**
