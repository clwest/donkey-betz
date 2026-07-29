# Session 3030 — backfill_canonical_drift command

**Date:** 2026-07-28 · **HEAD at close:** `e7fc79282` (PR #3749 merged) + docs cascade

## What shipped

**1 feature PR merged this session.**

### PR #3749 (`e7fc79282`) — `feat(s3030): backfill_canonical_drift command`

Closes the last known residue of the S3026 → S3029 canonical-promotion drift arc. Rigby explicitly deferred this backfill from PR #3747 at S3029 close.

**The bug being healed:** from ~Session 988 through Session 3029, the scheduled boardroom-auto-approve task (`_impl_auto_approve_boardroom_items` in `core/tasks_ops.py`) used bulk `QuerySet.update(status='canonical')` to promote decisions. `.update()` bypasses model save/signals, leaving rows with `status='canonical'` but `is_canonical=False`, `promoted_at=NULL`, `promoted_by=''`. 12 downstream consumers filter on `is_canonical=True` and have been missing these rows for years.

**Shape:**

- **NEW** `core/management/commands/backfill_canonical_drift.py` (+148)
  - Dry-run default; `--apply` to heal; `--limit N` (default 500) for batching
  - Per-row `transaction.atomic()` + try/except (bad row doesn't abort batch)
  - Captures `original_updated_at` BEFORE calling `promote_to_canonical()`; overrides `promoted_at` back to that value (best-effort proxy since true promotion time is unrecoverable; `.update()` bumped `auto_now`)
  - Marker `promoted_by='backfill-s3030-tasks-ops-drift'` — distinct, grep-friendly, does not collide with `filter(promoted_by__icontains='AI')` heuristic in `views_agent_learning:2051`
  - **No broadcast** — rows are up to 5 years old; belated `canonical_decision_promoted` events would be misleading. Verified `promote_to_canonical()` model method has no internal broadcast; all 6 promotion paths emit at caller sites, so simply not calling `emit_canonical_promotion_broadcast()` gives clean no-broadcast semantics without needing a suppress-flag param.
  - Idempotent (filter naturally excludes healed rows)

- **NEW** `core/tests/test_s3030_backfill_canonical_drift.py` (+218, 5 tests)
  - `test_dry_run_reports_drift_and_writes_nothing`
  - `test_apply_heals_drift_rows_with_updated_at_proxy` (locks in the pre-heal `updated_at` = post-heal `promoted_at` contract explicitly)
  - `test_apply_is_idempotent_on_second_run`
  - `test_dry_run_and_apply_both_no_op_on_empty_db`
  - `test_limit_flag_caps_batch_size` (asserts `remaining=N-limit`)

## Results

| Metric | Actual |
|---|---|
| PR #3749 diff | +366/-0 (2 new files: command + tests) |
| S3030 suite | **5/5 pass in 0.071s** |
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026 + S3027 + S3028 + S3029 [both] + S3030) | **74/74 pass in 7.547s** (baseline 69/69 at S3029 close; +5 new = 74) |
| Post-merge `make recycle-all` | clean, `sha=e7fc7928284e` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**15th consecutive session.** Verify pass at T1: read existing `AgentDecisionSummary` model + method, existing backfill command patterns (`backfill_agent_control_blocked_at.py` as the concise template, `backfill_decision_summaries.py` as an inappropriate LLM-based counter-example), 12 downstream `is_canonical=True` consumers via grep. Grounded the T1 spec in reality before dispatching to Rigby.

## Rigby SIGN quality this session

**3 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3029 pattern (**16 sessions continuous**).

Cycle summary:

1. **T1 SIGN — AGREE + 4 REVISE + zoom-out concern** on proposed command + test shape. Also included ORM drift-count probe request (Rigby correctly reported she cannot access `AgentDecisionSummary` via `orm_inspect_tool` — not in the 17-model allowlist — Rigby Tool Gap Ledger candidate for a future slate). Zoom-out flagged 3 items: `promoted_at` proxy semantic-overload caveat (add to docstring), broader drift-class sweep suggestion (deferred as broader effort), and **critical Q: does `promote_to_canonical()` broadcast internally?** All resolved same-turn.
2. **T1-REVISED — AGREE + 3 non-blocking micro-nits.** Claude ran the ORM probe (local DB empty, so heal is prod-only; test suite is correctness gate) and grep-verified the model method has NO internal broadcast (emit is at caller sites). REVISE conditions folded: capture `original_updated_at` BEFORE promote, two-step save, per-row error isolation with final summary, test locks in proxy contract. Micro-nits folded: `processed = healed + errors` for internal consistency, `total_drift` counted BEFORE slicing, test uses queryset re-read.
3. **A2 SIGN (post-code) — AGREE + tool-grounded zoom-out sweep.** Rigby ran repo-wide greps (7 `repo_tool` searches) confirming:
   - No other lingering `.update(status='canonical')` in production (only test/docstring/backfill refs)
   - No `update(**{status: ...})` kwargs-shape hiding same bug
   - No adjacent 'published/is_published' models with same drift-class risk
   - No `.filter(promoted_by='human')` hard filters that would exclude backfilled rows
   - Marker doesn't collide with `filter(promoted_by__icontains='AI')` aggregate

## Folds (pattern evidence, not automatic escalation)

### Fold A `informational` — Rigby ORM tool allowlist gap (new)

`AgentDecisionSummary` is not in `orm_inspect_tool` allowlist (17 models exposed). Blocked Rigby from running the T1 drift-count probe directly; Claude ran it via Django shell. Not urgent for this arc but a repeated pattern (2nd or 3rd time an S30XX model needed direct ORM inspection). **Rigby Tool Gap Ledger candidate** — log for future substrate slate per `feedback_rigby_tool_gap_ledger`.

### Fold B `informational` — Spy `side_effect=lambda` signature fragility (carried from S3029)

Unchanged. Applies to `test_s3029_promote_decision_model_method_convergence.py` spy pattern.

### Fold C `2nd cycle, no discovery` — A2 zoom-out sweep for drift-class pattern

S3029 close flagged Fold C at 1st trigger — "if A2 zoom-out sweep catches another adjacent silent bug, codify as workflow rule." **S3030 A2 sweep applied the pattern cleanly and found ZERO residue.** This is a *different* signal than a discovery — it's the pattern working as designed (confidence bound: the drift class is now genuinely closed). Still counts as evidence for codification, but as "pattern is useful even when it finds nothing" rather than "pattern caught a 2nd bug." Watch continues; genuine 2nd-discovery would still be the stronger codification signal.

### Fold D `informational` — Duplicate-broadcast race (carried from S3029 Fold B)

Unchanged. Still applies; low today; harden via `did_promote` semantics if elevated.

## Forward carries

### New from S3030

- **Fold A `informational` (NEW)** — Rigby ORM allowlist gap for `AgentDecisionSummary`. Ledger candidate for future substrate slate.
- **Fold B `informational` (carried from S3029 Fold A)** — spy `side_effect=lambda` signature fragility.
- **Fold C `2nd cycle, no discovery`** — A2 zoom-out sweep pattern applied cleanly, zero residue found. Different signal from S3029 discovery. Watch for 2nd genuine discovery to elevate codification pressure.
- **Fold D `informational` (carried from S3029 Fold B)** — duplicate-broadcast race.
- **Prod deploy carry** — the backfill has to be run against Railway prod (local DB has 0 rows). Suggested: `python manage.py backfill_canonical_drift` (dry-run to see count) → `--apply` if non-zero → repeat until `remaining=0`.

### Carried from S3029 (STATUS UPDATED)

- **S3029 Fold A `informational`** — carried as new Fold B (same content).
- **S3029 Fold B `informational`** — carried as new Fold D (same content).
- **S3029 Fold C `1st trigger`** — advanced to 2nd cycle, no-discovery (new Fold C).
- **S3029 PR #3747 deferred item** — **RESOLVED** by PR #3749.

### Carried from S3026 → S3028 (STATUS PRESERVED)

- **S3028 Fold A** — FULLY RESOLVED at S3029.
- **S3026 Fold A `1st trigger`** — fold descriptions backed by evidence. S3030 A2 sweep = supporting evidence (Rigby's tool-grounded sweep with `repo_tool`).
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 / S3024 / older — all preserved from S3029 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (PR #3749 planned end-to-end per S3029 forward-carry).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 22 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "Please begin Backfill migration for existing drift rows" ratified the direction; joint Claude+Rigby AGREE on shape; no mid-flight decision routing needed.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3749 merge, clean at `sha=e7fc7928284e`.
- **Fold classification (PLAYBOOK-6.10.8):** 4 folds. A informational (new). B/D informational (carried). C 2nd cycle no-discovery.
- **Verify-before-build (Cycle 1A):** **15th consecutive session** — read model + method + template backfill commands + downstream consumers before spec.

## Wrapper pin note

Session-open pin was `pa-4148265f4c6d4516` (minted at S3029 close). Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.
