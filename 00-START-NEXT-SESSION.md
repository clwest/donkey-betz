# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3024 CLOSED. **U6 (per-row name editing in bulk cluster confirm modal) shipped.** Users can now edit each initiative name inline before submitting the bulk create; previously the modal was read-only with defaults. Backend accepts an optional `names` sparse dict keyed by cluster_id (Rigby A1 REVISE: full dict on submit, never diff-only — avoids default-drift coupling). 10-session zero-hallucination Rigby SIGN streak. **9th consecutive Cycle 1A verify-before-build session** (backend was 90% parameterized already; MVP reduced to ~18 backend + ~45 frontend lines).

**1 feature PR shipped this session.**

**PR #3733 (`6166d7cb3`) — `feat(s3024): U6 — per-row name editing in bulk cluster confirm modal`.**

- **Backend `core/views_platform_command.py`** — `bulk_create_initiatives_from_clusters_view` accepts optional `names` dict. Missing keys / empty strings / non-dict param → silent fallback to backend default (`{pattern_label}: {cluster.name}`, 200-char cap). Frontend bug cannot 500 the endpoint.
- **Frontend `SignalsClustersView.tsx` `BulkPromoteModal`** — read-only preview replaced with scrollable list of editable inputs; pre-filled with computed defaults; inline character counter when approaching cap; inputs disabled during submit.
- **API client `frontend/src/lib/api.ts`** — signature extended with `names?: Record<string, string>`.
- **NEW** `core/tests/test_s3024_bulk_cluster_names_override.py` — 6 tests including `test_names_applied_by_cluster_id_not_by_position` (Rigby A1 REVISE regression).
- **Test result:** 6/6 pass in 0.638s. Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024): 48/48 pass in 5.818s.
- **Deferred (Rigby A2 zoom-out — Fold A):** `defaultNameFor()` frontend formatter shadows backend default; watch for future default-format change. Codification candidate.

**HEAD at close:** docs cascade → `6166d7cb3` (PR #3733).

Full context:
- `docs/handoffs/SESSION_3024_U6_BULK_CLUSTER_PER_ROW_NAMES.md` — full session close.

---

## S3025 primary directive candidates

**No in-flight arc.** Chris directive-required. **U-series bulk-actions arc trending user-visible:** S3013 U1 → S3014 U2 → S3015 U3 → S3021 U5 → S3022 U5b → S3023 U4-H → S3024 U6. The user-facing bulk polish is now well-covered; remaining tail is progress signaling + fold cleanup.

### Option A — Continue fresh engineering (bias-engineering rule)

- **Progress bar for bulk create** (SSE or optimistic UI): from S3015 forward-carry. Still open; users don't see per-row progress during long batches. ~1 session.
- **S3023 Fold B fix (single-promote → collective-intelligence parity):** wire `bulk_promote_decisions` to trigger Redis broadcast + KnowledgeTransfer for each promoted row (S657 parity). ~1 session.
- **S3023 Fold C fix (masked AttributeError in `promote_decision`):** replace `decision.summary` refs with `decision.rationale or decision.recommended_stance`. Un-mask `learning_created` for single-promote. ~30 min.
- **S3024 Fold A: backend-source default preview API.** Add `GET /api/platform/signal-cluster/<uuid>/default-initiative-name/` OR a bulk variant so frontend stops shadowing the backend default formatter. Watch-for-2nd-trigger candidate (not yet earned codification).

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

### Option E — Governance unification (Rigby A1 zoom-out standing carry, S3023)

- **Decision lifecycle parity:** HAI has decide/defer/verify/execute; ADS has promote/reject/approve + bulk variants. Multi-session arc — needs Chris ratification before scoping.

### Option F — Chris's own priority (supersedes A-E)

**Joint recommendation at close:** **Option A Progress bar for bulk create** — natural next in the user-facing bulk-actions arc. Bulk create at N=100 is opaque; SSE stream of per-row completion (or optimistic UI showing per-row spinners) would close the last UX gap in the bulk cluster promotion flow. Alt (equally good): S3023 Fold B/C bundle fixes (single-promote Redis + AttributeError un-mask), ~1.5 sessions total, closes two known latent bugs from prior arc.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3024 handoff (`docs/handoffs/SESSION_3024_U6_BULK_CLUSTER_PER_ROW_NAMES.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `6166d7cb3` (PR #3733) → S3023 close cascade.
   - `python manage.py test core.tests.test_s3024_bulk_cluster_names_override --keepdb` — 6/6 OK.

---

## S3025 carry-forward seeds

### New from S3024

- **Fold A `1st trigger`** — cross-tier default-formatting shadowing (frontend `defaultNameFor()` mirrors backend). Watch for 2nd trigger before codification.
- **Fold B `informational`** — silent-fallback vs strict-validate asymmetry for optional bulk params (`names` silently ignores non-dict; `cluster_ids` 400s on non-list). Codification candidate.

### Carried from S3023 (STATUS PRESERVED)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes before spec'ing (S3014 note that `_get_pending_decisions` returned both HAI + ADS was false).
- **S3023 Fold B `informational` (single-promote semantics only)** — `bulk_promote_decisions` doesn't trigger the Redis broadcast + KnowledgeTransfer that single `promote_decision` does (S657).
- **S3023 Fold C `informational` (single-promote semantics only)** — `promote_decision` line 2177 masked AttributeError on `decision.summary`.
- **S3023 Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract; future governance unification is a conscious breaking change.
- **Decision lifecycle parity (Rigby A1 zoom-out standing carry)** — HAI vs ADS lifecycle families still fragmented.

### Carried from S3022 (STATUS PRESERVED)

- **Management command for FK backfill** — still deferred per Rigby (no 2nd batch of stranded rows).
- **S3022 Fold A `informational`** — audit-first-then-shape-decide for backfill scope (codification candidate).
- **S3022 Fold B `informational`** — `RunPython.noop` reverse for deterministic-linkage backfills (codification candidate).

### Carried from S3021 (STATUS PRESERVED)

- **S3021 Fold A (backfill-as-separate-PR)** — still `1st trigger` on codification path.
- **S3021 Fold B (hivemind direct-set-then-fallback pattern)** — still `informational`.

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

### Carried from S3017 / older — all preserved from S3023 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (discovery → A1 REVISE → implement → A2 AGREE → ship → recycle-all).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 16 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "continue" + merge decision via Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3733 merge, frontend dist rebuilt confirmed (`sha=6166d7cb3173`).
- **Fold classification (PLAYBOOK-6.10.8):** 2 folds. Fold A `1st trigger`. Fold B `informational`. Rigby A1 REVISE concern `same_pr_mitigatable` (adopted before A2).
- **Verify-before-build (Cycle 1A):** **9th consecutive session** — backend was already 90% parameterized.

---

## Wrapper pin note

The active PA conversation pin at S3024 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3024 shipped 1-PR U6 per-row name editing after discovery revealed the backend was already 90% parameterized (Cycle 1A 9th consecutive win). Rigby A1 REVISE caught the diff-only-payload coupling risk before implementation; final shape sends full names dict. The U-series bulk-actions arc is now user-visible-polished. S3025 opens with Progress bar for bulk create as joint recommendation (alt: S3023 Fold B/C bundle fixes).**
