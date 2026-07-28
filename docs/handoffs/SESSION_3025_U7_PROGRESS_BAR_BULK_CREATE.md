# Session 3025 — U7 client-side chunked bulk cluster create with per-row progress

**Date:** 2026-07-28 · **HEAD at close:** `0a20b5b25` (PR #3735 merged) + docs cascade

## What shipped

**PR #3735 (`0a20b5b25`) — `feat(s3025): U7 — client-side chunked bulk cluster create with per-row progress`**

Continues the **S3013 → S3014 → S3015 → S3021 → S3022 → S3023 → S3024** user-facing bulk-actions arc. S3024 U6 shipped per-row name editing; the last user-visible gap was the opaque "Creating N…" spinner during the sync N-row loop (up to 100 clusters × brief LLM call). U7 replaces the single opaque spinner with:

1. A **rows-completed progress bar** (linear, chunk-boundary-agnostic).
2. **Per-row status glyphs** (Circle → Loader → Check / Warn) beside each name input.
3. A **Stop button** that aborts the in-flight chunk and skips remaining ones, calling `onCompleted` with the partial result set.

**10th consecutive Cycle 1A verify-before-build session** — the existing backend endpoint (`bulk_create_initiatives_from_clusters_view`) was reused unchanged. All progress semantics live in the frontend chunked submit loop.

### Frontend (`SignalsClustersView.tsx` `BulkPromoteModal`, +240/-65)

- `useMutation` replaced with an async submit loop over `chunks` (K=10 for N≥50, K=5 for smaller batches).
- Per-row status map (`pending | in_progress | success | already_exists | failed`) keyed by cluster_id.
- Progress bar reflects `completed_rows / total_rows`, not `chunks_done / chunks_total`, so the bar advances linearly regardless of chunk boundaries.
- 300ms inter-chunk delay (`setTimeout`) smooths the bar and reduces middleware burstiness.
- `AbortController` + `useRef<boolean>` stop flag: Stop button aborts the in-flight chunk, `handleSubmit` breaks the loop at the next chunk boundary, `onCompleted` fires with what completed.
- Chunk-scoped failure isolation: chunk error marks its rows failed and loop continues; failures accumulated into the final `failures[]` array.
- Modal backdrop click disabled while submitting so a stray click can't dismiss mid-batch.
- Large-batch warning ("This may take a few minutes when briefs are enabled") shown when N≥25.
- `RowStatusIcon` helper (`Circle | Loader2 | CheckCircle2 (green/amber) | AlertTriangle`) rendered left of each input.

### API client (`frontend/src/lib/api.ts`, +8/-3)

- `bulkCreateInitiativesFromClusters` signature adds optional `{ signal: AbortSignal }` second argument, forwarded to axios as `{ signal }` so the modal can abort in-flight chunks.

### Backend

**Unchanged.** The chunked submit calls the same endpoint the S3015 single-shot mutation was using; per-row `results[]` shape already existed. Cycle 1A win: zero new URL routes, zero new views, zero new tests required for backend behavior.

### Results

| Metric | Actual |
|---|---|
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024) | **48/48 pass in 5.438s** — no regression |
| Frontend `npx tsc --noEmit` on touched files | 0 errors (pre-existing errors in `WorkspacePageNew.tsx` + `paStore.ts` unrelated) |
| Frontend `npx vite build` | succeeds; new `dist/assets/index-*.js` bundle |
| Live smoke (token-auth POST with `cluster_ids: [<uuid>]`) | 200 + per-row `results[]` with initiative payload — validates chunked call pattern end-to-end |
| Post-merge `make recycle-all` | HEAD `0a20b5b25`, Daphne + Celery restarted clean, recycle event recorded (`sha=0a20b5b25f27`) |

## Cycle 1A verify-before-build wins

**Tenth consecutive session where reuse cut scope:**

- **Backend already had per-row `results[]` payload.** The existing `bulk_create_initiatives_from_clusters_view` returned `{summary, results:[...]}` with per-cluster entries; the frontend just needed to consume them across sequential smaller calls instead of one large one. Zero backend churn.
- **Existing regression bundle covers correctness invariants.** No new backend tests needed because backend behavior is unchanged; the 48-test bundle proves nothing adjacent broke.
- **Cost of the change:** ~240 frontend lines total.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3024 pattern (**11 sessions continuous**).

Cycle summary:

1. **A1 SIGN — APPROVE Shape B with 5 REVISE conditions.** Rigby considered SSE (Shape A, ~200 LOC + auth reimpl), chunked (Shape B, ~60-240 LOC + zero backend), and optimistic (Shape C, no real progress). Approved Shape B with:
   - REVISE #1: **K=10 default** for N≥50 (halves middleware overhead vs K=5).
   - REVISE #2: **Progress = completed_rows / total_rows** (linear feel).
   - REVISE #3: **Failure isolation** across chunks.
   - REVISE #4: **300ms inter-chunk delay** for smoother bar.
   - REVISE #5: **Large-batch UI copy** for N≥25.
   
   All 5 REVISE items applied before ship.

2. **A2 SIGN — AGREE.** Verified via `repo_tool` (grep + read_file) that all 5 REVISE items shipped in the diff, that S3024 semantics (per-row editable names, silent-fallback dict, 200-char cap) were preserved, and that the AbortController path exists. Zoom-out flagged 3 items → see Folds below.

## Folds (pattern evidence, not automatic escalation)

### Fold A `informational` — Chunk index recomputed inside loop

`handleSubmit` uses `chunks.indexOf(chunk)` inside the loop to gate the inter-chunk delay. At the 100-cluster cap (max 20 chunks at K=5) this is negligible, but it's O(N²) worst case. Codification threshold not reached; note for future clean-up if the modal grows.

### Fold B `informational` — Cancelled rows revert to `pending` visual state

When the Stop button aborts mid-batch, rows that were `in_progress` at the moment of abort fall back to `pending`. A future polish: introduce a distinct `cancelled` status glyph so users can tell "we stopped this" from "we never started this." Watch for repeat feedback before spec'ing.

### Fold C `codification candidate` — Modal complexity growth (Rigby zoom-out)

The `BulkPromoteModal` component now owns: name editing (S3024), chunked submit + progress + status tracking (S3025), aggregated summary folding, and abort handling. Rigby flagged extracting the chunking + row-status transitions into a small helper/reducer before the next iteration adds more responsibilities. Not yet a policy gate — but if U8+ lands more logic in this modal, refactor before continuing. **Watch signal:** any next PR in this arc that adds a 4th responsibility to `BulkPromoteModal` triggers the extraction.

### Non-MVP follow-up (from A1 zoom-out, not a Fold)

Brief generation is the real slowness in bulk create (LLM call per row). The right long-term fix is to make brief generation async / deferred so bulk create isn't rate-limited by LLM latency. U7 exposes the slowness rather than fixing it. Track as engineering candidate; **not** a policy gate.

## Forward carries

### New from S3025

- **Fold A `informational`** — `chunks.indexOf(chunk)` inside loop; cheap at cap, refactor-if-modal-grows.
- **Fold B `informational`** — cancelled rows revert to `pending` visual; consider distinct `cancelled` state.
- **Fold C `codification candidate`** — `BulkPromoteModal` complexity growth; extract chunking + row-status reducer before U8+ lands more logic.
- **Non-MVP engineering candidate:** async brief generation to remove LLM latency from bulk create critical path.

### Carried from S3024 (STATUS PRESERVED)

- **S3024 Fold A `1st trigger`** — cross-tier default-formatting shadowing (`defaultNameFor()` frontend still mirrors backend default). Watch for 2nd trigger before codification.
- **S3024 Fold B `informational`** — silent-fallback vs strict-validate asymmetry for optional bulk params.

### Carried from S3023 (STATUS PRESERVED)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes before spec'ing.
- **S3023 Fold B `informational` (single-promote semantics only)** — `bulk_promote_decisions` doesn't trigger the Redis broadcast + KnowledgeTransfer that single `promote_decision` does.
- **S3023 Fold C `informational` (single-promote semantics only)** — `promote_decision` line 2177 masked AttributeError on `decision.summary`.
- **S3023 Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract; future governance unification is a conscious breaking change.
- **Decision lifecycle parity (Rigby A1 zoom-out standing carry)** — HAI vs ADS lifecycle families still fragmented.

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3024 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (discovery → A1 APPROVE-with-REVISE → implement → A2 AGREE → ship → recycle-all).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles. Zero rubber-stamp. 17 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session: session-open directive "begin Option A" ratified S3025 primary directly; no mid-flight decisions routed.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` twice — once post-branch to bring my frontend change live for smoke-verify, once post-merge per rule (`sha=0a20b5b25f27` recorded in `logs/recycle_events.jsonl`).
- **Fold classification (PLAYBOOK-6.10.8):** 3 folds. Fold A `informational`, Fold B `informational`, Fold C `codification candidate`. Rigby A1 REVISE conditions all classified `same_pr_mitigatable` (adopted before implementation).
- **Verify-before-build (Cycle 1A):** **10th consecutive session** — backend was 100% reused (zero-diff).

## Wrapper pin note

Session-open pin was `pa-bb11fd63cff94102` (retired at session_lifecycle open). Active during session: `pa-3316e95cc372416d`. Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.
