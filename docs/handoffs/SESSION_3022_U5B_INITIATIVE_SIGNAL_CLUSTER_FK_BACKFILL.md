# Session 3022 — U5b Initiative.signal_cluster FK Backfill

**Date:** 2026-07-28 · **HEAD at close:** `1ff5475c4` (PR #3729) + docs cascade

## What shipped

**PR #3729 (`1ff5475c4`) — `feat(s3022): U5b — backfill Initiative.signal_cluster FK from parent_topic (data migration 0404)`**

Follow-up to S3021 U5 (PR #3727). S3021 fixed the writer path so new cluster→initiative creates set the FK directly. S3022 normalizes the historical tail — pre-U5 rows that only had the `parent_topic` string hint but NULL FK.

Ratified path: S3021 close 00-START Option A → U5b backfill.

### Audit-first shape

- Pre-migration audit revealed **N=3 eligible rows, all clean-parse, all resolvable**. Zero malformed, zero deleted-cluster references.
- Rigby's original S3021 suggestion was "batched management command with dry-run mode" (appropriate for N=100+ with parse-tail risk).
- Re-routed shape decision to Rigby with actual numbers; she endorsed **Option 1 (data migration)** over management command for the small clean set. Audit already IS the dry-run.

### Migration (`core/migrations/0404_s3022_backfill_initiative_signal_cluster_fk.py`)

Rigby A2 guardrails applied:

1. **Historical models via `apps.get_model`** — no runtime imports (future-safe against model renames).
2. **Idempotent** — only touches `signal_cluster_id IS NULL AND parent_topic matches AND cluster resolves`.
3. **Skip-on-missing** — malformed `parent_topic` OR deleted cluster → row left NULL, logged via `print`.
4. **`RunPython.noop` reverse** — reversing to NULL would drop deterministic linkage; no-op is honest.
5. **Correct dep chain** — depends on `0403_s2995_staleness_backfill`; `Initiative.signal_cluster` field existed since `0217_session_913_initiative_signal_intelligence`.

### Results

| Metric | Target | Actual |
|---|---|---|
| Total Initiatives with `parent_topic` starts `signal_cluster:` | 4 | 4 |
| FK set | 4 | **4 ✅** |
| FK NULL (post-migration) | 0 | **0 ✅** |
| Migration output | `linked=3 skipped_malformed=0 skipped_missing_cluster=0` | — |

- S3013-S3021 regression suite: **60/60 pass in 8.828s**.
- Post-merge `make recycle-all` — HEAD `1ff5475c4`, all services + workers restarted clean.

## Cycle 1A verify-before-build wins

Seventh consecutive session where reuse cut scope:

- **Reused `0403_s2995_staleness_backfill.py` structure** — `apps.get_model` + `iterator(chunk_size=500)` + `RunPython.noop` reverse pattern. Zero novel migration shape.
- **Reused the S3021 audit query** verbatim as the migration's core loop (with `.update()` swap-in for the write path).
- **No new tests** — writer-path invariant lives in S3021 tests (test_signal_cluster_fk_set_at_create_time + _bulk); migration is guarded by idempotent skip-on-missing pattern. Rigby explicitly pushed back on adding heavy migration-executor tests.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3021 pattern (**8 sessions continuous**). Rigby T1 REVISE-catches-something pattern **not triggered this session** (design was clean; audit numbers matched expectation; migration shape converged on first pass). 5-session REVISE streak paused, not broken — recorded as observation only.

Cycle summary:

1. **Shape recalibration (post-audit).** Claude presented Option 1/2/3 after audit numbers surfaced (N=3 all-clean). Rigby endorsed Option 1 (data migration) with 4 concrete guardrails, pushed back on Option 2 (management command) as premature ceremony without evidence of recurring drift.
2. **Merge decision via Rigby** with plain-English framing. Chris routing implicit — session opened with directive "begin U5b backfill" ratifying the primary directive.

## Folds (pattern evidence, not automatic escalation)

### Fold A `informational` — Audit-first-then-shape-decide as canonical for backfill scope

The original S3021 fold specified "batched management command with dry-run mode" for U5b. Actual audit surfaced N=3 all-clean, which flipped the shape to data migration. **Discovery candidate:** codify "audit before committing to shape" for any backfill task — the audit numbers themselves determine the right ceremony level. Codification only after 2nd trigger.

### Fold B `informational` — Reverse-code honesty

For deterministic-linkage backfills, the semantically-correct reverse (set FK back to NULL) is USUALLY wrong because reversing silently drops guarantees the writer path is enforcing. `RunPython.noop` is the honest reverse. **Discovery candidate:** consider adding a convention comment in `docs/` or the migration template about noop-reverse for deterministic-linkage backfills.

## Forward carries

### New from S3022

- **Management command NOT shipped** — deferred per Rigby. Add only if second batch of stranded rows appears (evidence of drift from alternate writer). Not a carry-forward action item — a conscious non-decision.
- **Fold A `informational`** — audit-first-then-shape-decide for backfill scope (codification candidate).
- **Fold B `informational`** — reverse-code honesty for deterministic-linkage backfills.

### Carried from S3021 (STATUS UPDATED)

- **S3021 U5b backfill** — **CLOSED by S3022 PR #3729**.
- **S3021 Fold A (backfill-as-separate-PR)** — first trigger reinforced; U5b IS the separate PR pattern. Still `1st trigger` on the codification path (not codified).
- **S3021 Fold B (hivemind direct-set-then-fallback pattern)** — still `informational`.
- **S3021 Fold C (Rigby T1 REVISE catches something)** — 5 consecutive sessions ended at S3021; not extended this session (see Rigby SIGN quality note above).

### Carried from S3020 / S3019 / S3018 / older — all preserved from S3021 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0008. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (audit → shape-recalibrate → implement → verify → ship → recycle-all).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles.** Zero rubber-stamp. **14 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "begin U5b backfill" ratified primary; merge decision via Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3729 merge.
- **Fold classification (PLAYBOOK-6.10.8):** 2× `informational` (audit-first-then-shape, reverse-code honesty).
- **Verify-before-build (Cycle 1A):** **7th consecutive trigger** — reused 0403 migration structure + S3021 audit query + skip-adding-tests-per-Rigby.

## Chris directive transcript

**T1 (S3022 open):** Chris directive "begin U5b backfill" ratified S3022 primary directive (natural follow-up to S3021 U5).

**T2 (mid-session):** No further routing needed. Audit → Rigby shape-recalibration → migration write → apply → verify → ship. Rigby endorsed merge.

## Wrapper pin

Active PA conversation pin at S3022 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3022 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
