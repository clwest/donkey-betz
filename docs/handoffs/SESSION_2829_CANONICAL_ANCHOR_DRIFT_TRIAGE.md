---
title: "S2829 — Canonical Anchor Drift Triage (S2826-Class Re-Manifestation Repair)"
session: 2829
date: 2026-07-19
status: shipped
authority: implementation + governance
scope: |
  S2829 open sanity checks re-surfaced 870 status='archived' mismatches
  after S2828 close asserted 0. Joint Claude+Rigby SIGN traced two
  independent defects: (1) backfill_document_status_from_docs_index was
  unguarded — bare invocations wrote against mid-flight _index.json;
  (2) sync_docs_index_to_documents skip-branch never touched status,
  so every unchanged-content sync left drifted rows intact. Shipped as
  one atomic PR (#3271, SHA `584f13026`) that (a) requires --apply or
  --dry-run on backfill (bare CommandError); (b) snapshots + hashes
  _index.json bytes at command start; (c) closes the sync skip-branch
  status-refresh hole; (d) targeted-restores 3 canonical anchors.
  Followed by PR2 execution (bounded backfill --apply run) restoring
  the remaining 867 rows to 0 mismatches. Pattern B/C/D retrieval
  integrity restored: all three canonical queries return canonical
  anchor top-1. PR3 (invariant / playbook / divergent-stack
  investigation) deferred as separate architectural arc per Chris D3.
predecessor: docs/handoffs/SESSION_2828_PATTERN_D_LITERAL_FILENAME_INJECTION.md
merge_pr: 3271
merge_sha: 584f13026
---

# S2829 — Canonical Anchor Drift Triage

## §1 Session shape

Chris opened S2829 with "Please begin". Sanity checks per
`00-START-NEXT-SESSION.md` §Recommended session-open protocol
immediately surfaced drift — three Pattern B/C/D queries all returned
non-canonical top-1 docs and `backfill_document_status_from_docs_index
--dry-run` reported **870 mismatches** (S2828 close asserted 0).

Rather than proceed with the recommended-default S2829 lean (shared
"pointer-intent registry" primitive extraction design), Claude
surfaced the finding via Rigby joint SIGN. Chris ratified A→B
sequenced with Rigby guardrail: **identify the writer FIRST, then
repair**. PR3 (invariant / playbook / divergent-stack) deferred as
separate architectural arc.

## §2 Root-cause investigation

### §2.1 Bulk-update signature

Query on `Document.objects.filter(status='archived', is_active=True,
canonical_authority='repo_canonical')` bucketed by `updated_at`
returned:

| updated_at (UTC)                          | rows | notes                          |
|-------------------------------------------|------|--------------------------------|
| 2026-07-08T04:07:01.509084+00:00          | 1733 | S2826 baseline (correct)       |
| **2026-07-19T03:17:40.403387+00:00**      | **866**  | **S2829 drift bulk update**    |
| 2026-07-19T04:46:25.479427+00:00          | 1    | CLAUDE.md — sync per-row save  |
| 2026-07-19T05:35:04.770343+00:00          | 1    | 00-START-NEXT-SESSION.md       |
| 2026-07-19T05:35:04.988316+00:00          | 1    | docs/INDEX.md                  |
| 2026-07-19T05:35:05.005320+00:00          | 1    | docs/KNOWLEDGE_PIPELINE.md     |

The 866 microsecond-identical `updated_at` values match a single SQL
`UPDATE` bulk-shape. Grep for direct `Document.objects...update(status=
'archived')` writers returned zero matches; the only ORM path that
composes fixed-`now` bulk updates over Document is
`backfill_document_status_from_docs_index.py:164`:

```python
Document.objects.filter(id=doc_id).update(
    status=to_status,
    updated_at=now,
)
```

...within `with transaction.atomic():` after fixing `now = timezone.now()`
outside the loop. If run against an `_index.json` where those 866 docs
were marked `superseded`/`deprecated`, this would flip them to
`ContentStatus.ARCHIVED`. Rigby's ops_tool confirmed **zero celery
events** for backfill in the last 30 days → invocation was manual
(`python manage.py ...` subprocess).

### §2.2 Sync skip-branch persistence

For the 3 canonical anchors (`docs/PLATFORM_INVENTORY.md`,
`00-START-NEXT-SESSION.md`, `CLAUDE.md`), on-disk content_hash matched
DB `content_hash` for two of the three (PLATFORM_INVENTORY, CLAUDE),
so `sync_docs_index_to_documents.py:267-268` returned `'skipped'`
without entering the update-branch. The S2826 fix at line 297 (`existing.
status = STATUS_MAPPING.get(...)`) never executed on skipped docs. The
archived state persisted.

### §2.3 Timeline hypothesis

1. ~2026-07-18 21:17 Chris local (03:17 UTC): backfill ran manually
   against an in-flight `docs/_index.json` where 866 docs were still
   marked `superseded`/`deprecated`; flipped them to archived
2. ~2026-07-18 23:34 local (05:34 UTC): `build_docs_index` regenerated
   `_index.json`, correctly re-flagging those docs as `active`
3. ~2026-07-18 23:35 local (05:35 UTC): sync ran, hit skip-branch on
   unchanged canonical anchors → status stayed archived

## §3 Rigby joint SIGN (2 cycles + verified tool_runs)

### §3.1 Cycle 1 — 5 Q, tool_runs verified

Rigby returned Q1..Q5 verdicts after using `kb_tool.semantic_search`,
`kb_tool.documents`, `scheduled_tasks_tool.list`,
`ops_tool.celery_task_history`, `recent_activity_tool`, `repo_tool.read_file`
(3×), `db_health_tool`. Non-empty tool_runs; anti-rubber-stamp discipline
verified per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

- **Q1** (drift real / blocks retrieval integrity?) → **AGREE**
- **Q2** (A→B sequence?) → **AGREE with guardrail — identify writer FIRST**
- **Q3** (source at 03:17 UTC?) → **UNKNOWN** (no beat, no celery history)
- **Q4** (zoom-out) → status is a production-critical retrieval filter;
  bulk sweeps cause platform-wide epistemic outage; anchors need
  immunity/invariants
- **Q5** (Chris escalation) → define canonical-anchor invariant + check for
  divergent retrieval stacks

### §3.2 Cycle 2 — refined PR1 scope after writer identification

- **Q1** (writer confirmed?) → **AGREE** (backfill @ mid-flight _index.json)
- **Q2** (skip-branch hole?) → **AGREE with nuance** (sync short-circuits
  at content_hash match; S2826 update-branch fix doesn't cover this)
- **Q3** (PR1 scope) → **AGREE** — apply guard + skip-branch fix + targeted
  anchor restore
- **Q4** (stop-writer framing) → BOTH staged: `--apply` guard immediately +
  `_index.json` snapshot/hash for correctness
- **Q5** (pass condition) → AGREE + add `kb_tool.documents(query='<filename>')`
  catalog visibility check

## §4 Chris D-verdict

Chris **"approved"** the A→B sequence with Rigby's guardrail. Rigby's
subsequent refinements were within the ratified scope (no re-routing
needed per S2753 discipline).

Deferred to PR3 architectural arc:
- Canonical-anchor invariant design (pinned/boosted + immune from bulk
  status sweeps + not hidden by processed-only filters)
- Divergent-retrieval-stack investigation (query → top-3 matrix across
  `search_embeddings` vs `kb_tool.semantic_search`)

## §5 Implementation

### §5.1 PR #3271 (SHA `584f13026`)

Files changed: 5 (352 insertions / 15 deletions).

| File                                                             | Change                                                                                   |
|------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| `core/management/commands/backfill_document_status_from_docs_index.py` | Add `--apply` / `--dry-run` explicit-mode guard; snapshot `_index.json` bytes + log sha256 hash |
| `core/management/commands/sync_docs_index_to_documents.py`       | Close skip-branch status-refresh hole; new `'status_refreshed'` stats counter            |
| `core/tests/test_s2829_metadata_sync_hardening.py`               | New — 9 pytests covering both defect closures                                            |
| `core/tests/test_extracted_metadata_clobber_fix.py`              | Regression fix — seed `status=PROCESSED` so skip-branch stays dormant on no-op           |
| `tools/pa_local.sh`                                              | Fresh S2829 pin `pa-d3a4d67126b64e7f`                                                    |

### §5.2 PR2 execution

Post-merge, on the fresh S2829 pin:

```
python manage.py backfill_document_status_from_docs_index --apply
# 867 rows updated

python manage.py backfill_document_status_from_docs_index --dry-run
# Total mismatches: 0
```

The `--apply` guard is now the required entry point for writes; a bare
invocation exits with `CommandError`.

## §6 Pass gates verified

| Gate | Check | Result |
|------|-------|--------|
| (i)  | `search_embeddings(query='where do I start')` → top-1 = `00-START-NEXT-SESSION.md` (Pattern C) | ✓ |
| (i)  | `search_embeddings(query='How many spiders')` → top-1 = `docs/PLATFORM_INVENTORY.md` (Pattern B) | ✓ |
| (i)  | `search_embeddings(query='PLATFORM_INVENTORY')` → top-1 = `docs/PLATFORM_INVENTORY.md` (Pattern D) | ✓ |
| (ii) | `backfill_document_status_from_docs_index --dry-run` = 0 mismatches | ✓ |
| (iii) | 3 canonical anchors visible to catalog path (`status='processed'`) | ✓ |
| (iv) | 9/9 new pytests + 28/28 sync regression tests pass | ✓ |
| (v)  | Stack FRESH on merged SHA `584f13026` post-`make recycle-all` | ✓ |

## §7 Lessons

1. **The S2826 sync-defect had a 2nd-order skip-branch hole.** Fixing
   the update-branch (`content_hash` mismatch) is not enough. The
   skip-branch (`content_hash` matches) must ALSO refresh status
   against docs_index_status, or any prior drift (from ANY writer)
   persists indefinitely on unchanged-content docs.

2. **Backfill commands that operate on `_index.json` should snapshot
   it at command start.** Otherwise mid-flight regeneration (via
   `build_docs_index` or the 4-step cascade) can silently invert the
   command's meaning. Snapshot + hash-log makes divergence detectable
   in post-hoc audits.

3. **Bare-invocation writes must be forbidden for bulk-status
   commands.** The `--apply` guard is not paranoia — it's a fixture
   that closes the "unattended run at the wrong moment" writer class.
   Cost: one CLI flag. Benefit: eliminated a whole class of
   silent-retrieval-outage causes.

4. **`updated_at` bucketing by microsecond is a reliable
   forensic signature.** Same-microsecond `updated_at` across N rows
   ≈ one SQL `.update()` bulk statement. Different-microsecond
   sequences ≈ per-row `.save()` iteration. This distinction narrowed
   the writer class from "any code path" to "commands that use fixed-
   `now` in a bulk-`.update()` loop".

5. **`content_hash` disk-vs-DB parity is the sync-skip-branch entry
   test.** When investigating drift-on-unchanged-content, always
   verify the hash comparison before assuming sync ran and did
   nothing. Two of the three canonical anchors hit the skip-branch
   at 05:35 UTC because their content_hash matched — sync exited
   before the S2826 fix could run.

6. **DO NOT run docs cascade steps manually against uncertainly-fresh
   `_index.json`.** Any manual cascade step (build_docs_index,
   sync_docs_index_to_documents, backfill_document_status_from_docs_index)
   should be run as a single monotonic sequence, not intermixed with
   other repo work. The S2829 drift came from running backfill
   between two `_index.json` states.

7. **DO NOT bundle PR3 with PR1/PR2.** Invariant design + divergent-
   stack investigation are architectural work; combining them with
   the repair increases rollback risk and blurs the smallest-blast-
   radius contract. Rigby Q5 caught this.

## §8 Follow-up carry

- **PR3 (future arc):** Canonical-anchor invariant design — anchors
  pinned/boosted + immune from bulk status sweeps + not hidden by
  processed-only filters. Playbook v0.9-adjacent.
- **Divergent-stack diagnostic:** query → top-3 matrix across
  `search_embeddings` vs `kb_tool.semantic_search` with their
  filters/authority-weighting. Existence-check only (not a refactor).
- **13 out-of-index Document rows:** still deferred per Chris D6.
- **Shared "pointer-intent registry" primitive (S2828 D-Q3):** still
  candidate; S2829 did not touch. Re-open at S2830+.

## §9 Twin-pointer card

📁 **Repo — S2829 artifacts:**

- **Implementation:** `core/management/commands/backfill_document_status_from_docs_index.py` (--apply guard + snapshot hash), `core/management/commands/sync_docs_index_to_documents.py` (skip-branch closure)
- **Pytest coverage:** `core/tests/test_s2829_metadata_sync_hardening.py` (9 tests)
- **Merge SHA:** `584f13026` · **PR:** #3271
- **Handoff:** `docs/handoffs/SESSION_2829_CANONICAL_ANCHOR_DRIFT_TRIAGE.md` (this file)

🖥️ **Workspace UI — S2829 twin-pointer:**

- To mint at close cascade: `ratification_record` deliverable in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`), category `governance`, `diagnostic_status=None`. ORM-direct create per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`.
