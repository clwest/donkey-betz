# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3025 CLOSED. **U7 (client-side chunked bulk cluster create with per-row progress bar) shipped.** Users now see a linear rows-completed progress bar + per-row status glyphs during bulk cluster→initiative promotion; Stop button aborts the in-flight chunk and returns partial results. 11-session zero-hallucination Rigby SIGN streak. **10th consecutive Cycle 1A verify-before-build session** — backend was 100% reused (zero diff); all progress semantics live in the frontend chunked submit loop.

**1 feature PR shipped this session.**

**PR #3735 (`0a20b5b25`) — `feat(s3025): U7 — client-side chunked bulk cluster create with per-row progress`.**

- **Frontend `SignalsClustersView.tsx` `BulkPromoteModal`** — `useMutation` replaced with async submit loop; chunks `cluster_ids` (K=10 for N≥50, K=5 smaller) into sequential POSTs to the existing endpoint; 300ms inter-chunk delay; per-row status map (`pending | in_progress | success | already_exists | failed`) drives glyphs left of each name input; progress bar reflects `completed_rows / total_rows`; `AbortController` on Stop button; large-batch warning at N≥25.
- **Frontend `api.ts`** — `bulkCreateInitiativesFromClusters` signature extended with optional `{ signal: AbortSignal }` second argument.
- **Backend `core/views_platform_command.py`** — **unchanged**.
- **Tests:** no new tests (backend behavior unchanged). Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024): **48/48 pass in 5.438s**.
- **Rigby A1 REVISE (all 5 conditions applied same-PR):** K=10 default, linear row-based progress, failure isolation, 300ms delay, large-batch UI copy.
- **Rigby A2 AGREE:** tool_runs-verified all 5 REVISE items shipped + S3024 semantics preserved. Zoom-out flagged 3 Folds (see carry-forwards).

**HEAD at close:** docs cascade → `0a20b5b25` (PR #3735).

Full context:
- `docs/handoffs/SESSION_3025_U7_PROGRESS_BAR_BULK_CREATE.md` — full session close.

---

## S3026 primary directive candidates

**No in-flight arc.** Chris directive-required. The **user-facing bulk-actions arc (S3013 → S3025)** now covers: bulk decide (S3013), single cluster promote (S3014), bulk cluster promote (S3015), auto-link FK (S3021), FK backfill (S3022), bulk agent decisions (S3023), per-row name editing (S3024), chunked progress bar (S3025). **The U-series MVP is functionally complete**; remaining tail is targeted polish or fold cleanup.

### Option A — Fresh user-visible engineering (bias-engineering rule)

- **Async brief generation (non-MVP followup from S3025 A1 zoom-out):** LLM latency is the real slowness in bulk create; move brief generation to a Celery task with per-row status updates instead of blocking the HTTP call. Removes the "large batch may take minutes" warning. ~1-2 sessions.
- **S3023 Fold B fix (single-promote → collective-intelligence parity):** wire `bulk_promote_decisions` to trigger Redis broadcast + KnowledgeTransfer for each promoted row (S657 parity). ~1 session.
- **S3023 Fold C fix (masked AttributeError in `promote_decision`):** replace `decision.summary` refs with `decision.rationale or decision.recommended_stance`. Un-mask `learning_created` for single-promote. ~30 min.
- **S3024 Fold A: backend-source default preview API.** Add `GET /api/platform/signal-cluster/<uuid>/default-initiative-name/` OR a bulk variant so frontend stops shadowing the backend default formatter. Watch-for-2nd-trigger candidate.

### Option B — S3025 Fold C codification (modal refactor)

- **Extract `BulkPromoteModal` chunking + row-status transitions into a reducer/helper.** Rigby flagged as codification candidate at A2 zoom-out. Not yet required (single trigger) but blocks future U8+ additions cleanly. ~30-45 min.
- **S3025 Fold B: distinct `cancelled` row status.** Currently aborted rows revert to `pending` glyph. Minor UX polish; not user-blocking. ~15 min.

### Option C — Continue audit trajectory

- **S3020 Fold A:** audit script per-hit/per-function suppression refactor. ~30 min.
- **Audit script multiline regex extension** — catch `.filter(...)\n.get(...)` split across lines.

### Option D — S3018 Fold extensions

- **Fold B (S3018 REVISE-2):** test-time advisory telemetry for decorator-chain-break. ~1 session.
- **Method-decorator detection extension:** catch `@method_decorator(superuser_required)` on CBV methods. ~1 session.

### Option E — S3016 zoom-out carries (still open)

- Middleware-order snapshot test.
- DRF ViewSet auth-class parallel audit.
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension.

### Option F — Governance unification (Rigby A1 zoom-out standing carry, S3023)

- **Decision lifecycle parity:** HAI has decide/defer/verify/execute; ADS has promote/reject/approve + bulk variants. Multi-session arc — needs Chris ratification before scoping.

### Option G — Chris's own priority (supersedes A-F)

**Joint recommendation at close:** **Option A — async brief generation.** It's the non-MVP followup Rigby flagged during S3025 A1 zoom-out; it removes the actual latency the S3025 progress bar exposes, closes the "large batch may take minutes" UX warning, and is the natural next-step in the arc's *substrate* direction (S3025 was UX polish; async briefs is the underlying-cost fix). Alt: **Option A — S3023 Fold B/C bundle** (single-promote Redis broadcast + AttributeError un-mask) closes two known latent bugs in ~1.5 sessions if Chris wants a fold-cleanup pause.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3025 handoff (`docs/handoffs/SESSION_3025_U7_PROGRESS_BAR_BULK_CREATE.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `0a20b5b25` (PR #3735) → S3024 close cascade.
   - `python manage.py test core.tests.test_s3013_bulk_attention_decide_mutation core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters core.tests.test_s3023_bulk_agent_decision_mutation core.tests.test_s3024_bulk_cluster_names_override --keepdb` — 48/48 OK.

---

## S3026 carry-forward seeds

### New from S3025

- **Fold A `informational`** — `chunks.indexOf(chunk)` inside loop in `BulkPromoteModal.handleSubmit`. Cheap at cap=100, refactor-if-modal-grows.
- **Fold B `informational`** — cancelled rows revert to `pending` glyph. Consider distinct `cancelled` status if repeat feedback.
- **Fold C `codification candidate`** — `BulkPromoteModal` complexity growth. Extract chunking + row-status reducer before U8+ lands more logic. **Watch signal:** next PR adding a 4th responsibility to this modal triggers the extraction.
- **Non-MVP engineering candidate** — async brief generation to remove LLM latency from bulk-create critical path.

### Carried from S3024 (STATUS PRESERVED)

- **Fold A `1st trigger`** — cross-tier default-formatting shadowing (frontend `defaultNameFor()` mirrors backend).
- **Fold B `informational`** — silent-fallback vs strict-validate asymmetry for optional bulk params.

### Carried from S3023 (STATUS PRESERVED)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes before spec'ing.
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

### Carried from S3017 / older — all preserved from S3024 close 00-START.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (discovery → A1 APPROVE-with-REVISE → implement → A2 AGREE → ship → recycle-all).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 17 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "begin Option A" ratified S3025 primary directly.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` twice — once post-branch to bring frontend change live for smoke-verify, once post-merge (`sha=0a20b5b25f27`).
- **Fold classification (PLAYBOOK-6.10.8):** 3 folds. Fold A + B `informational`, Fold C `codification candidate`. Rigby A1 REVISE conditions all classified `same_pr_mitigatable` (adopted before implementation).
- **Verify-before-build (Cycle 1A):** **10th consecutive session** — backend was 100% reused, zero diff.

---

## Wrapper pin note

The active PA conversation pin at S3025 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3025 shipped 1-PR U7 client-side chunked progress bar for bulk cluster create after Rigby A1 approved Shape B (chunked, zero backend churn) over Shape A (SSE) with 5 REVISE conditions all applied same-PR. The user-facing bulk-actions arc (S3013 → S3025) is now functionally complete. S3026 opens with async brief generation as joint recommendation (removes the actual latency U7 exposes) — alt: S3023 Fold B/C bundle for fold cleanup or S3025 Fold C for modal reducer extraction.**
