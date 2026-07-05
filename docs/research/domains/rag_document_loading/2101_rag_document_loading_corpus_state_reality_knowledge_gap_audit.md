---
title: "Group 2100 — Cat A — Corpus State: Reality→Knowledge Gap Audit (S2101 P1)"
status: active (Chris "agree all" ratification 2026-07-04 post-Rigby SIGN cycle 1 CLEAN with 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT)
session: 2101
child_slot: P1_cat_a
domain_slug: rag_document_loading
research_group: 2100
mission_type: child_audit
date: 2026-07-04
arc_pin: pa-18b095bb7c4740be
authority: |
  P1 child audit under Group 2100 RAG / Document Loading (Knowledge Loop)
  arc. Scope inherited from parent scoping §5.1
  (`2100_rag_document_loading_domain_scoping.md`).

  This doc is RESEARCH AUDIT only. It captures a **static snapshot** of
  the RAG corpus at HEAD `053e5fc5` on `main` (2026-07-04) across the
  five cascade steps (on-disk → `docs/_index.json` → `.rag/corpus.jsonl`
  → `Document` rows → `DocumentEmbedding` rows), enumerates the
  DocumentEmbedding metadata schema present today (Q8-a), ROI-trims
  Chris's 18-field aspirational metadata list against reality, proposes
  a core-required + doc-type-profile candidate list per the D2100.9
  hybrid contract shape, and classifies observed knowledge-debt into
  durable categories.

  Explicit non-scope, per parent §7 anti-scope + Q5 SIGN belongs-to
  boundary rule:
  - Does NOT design the cascade mechanism end-to-end (that IS P2 /
    S2102).
  - Does NOT design the SHOULD-carry metadata contract (that IS P3 /
    S2103 — this audit ships candidate lists only).
  - Does NOT design the retrieval authority framework (that IS P3 /
    S2103).
  - Does NOT observe RAG-quality → SIGN-quality effects (that IS P4 /
    S2104).
  - Does NOT ship migrations, schema changes, cascade command changes,
    beat-schedule additions, or embedding regenerations.
  - Does NOT re-audit `AgentMemory`, personal memories, or conversation
    context (Group 1300 territory per parent §7.2).
  - Does NOT explain causality beyond brief hypothesis tags; the
    deliverable is a **gap matrix + inventory table + knowledge-debt
    taxonomy** (Q5 fold belongs-to boundary).

  Load-bearing inheritance chain re-attested at S2101 open:
  - S1304 §14 D2 `_load_provenance_docs()` `@lru_cache(maxsize=1)`
    staleness — verified STILL LIVE at `core/services/td_handlers_ops.py:78`
  - S1304 §14 D7 `DocumentEmbedding.ingested_via` orphan claim
    (F4-CANDIDATE) — routed via S1399 §19 R1; write-side inventoried
    here, consumer-side deferred
  - S1304 §15 T1 provenance-index rebuild cadence unmanaged — verified
    STILL VALID (0 periodic tasks matching `provenance`)
  - S1304 §15 T5 `ingested_via` write path not wired to retrieval —
    verified STILL VALID
  - S1234 12-day-stale prod corpus incident + 1820-never-pushed
    Documents — REMEDIATED by `refresh_docs_corpus` daily beat
    (verified enabled + hash-gated + embed-fanout wired)
  - S1802 6-unembedded-docs cascade incident — informalized here as
    knowledge-debt sample KD-3 (see §15.3)
  - MEMORY.md `feedback_docs_pipeline_4_step_cascade` +
    `feedback_docs_cascade_at_every_close` +
    `feedback_cascade_pr_must_include_embed_step` — treated as
    informal-cadence knowledge governance
  - Group 2000+ S2001 F3 SPIDER_DATA MISSING-producer / WEAK-consumer
    — spider-data → RAG ingestion path flagged, deferred to P2 as
    ingestion-pipeline concern
verifier_loop: |
  Pre-draft verifier-loop (per parent §5.1 SESSION READY CHECK item 5)
  executed 2026-07-04 at HEAD `053e5fc5`:
  1. Corpus row counts sampled via ORM: `Document.objects.count()=2908`,
     `DocumentEmbedding.objects.count()=51789`
  2. On-disk sweep: `find docs -type f -name '*.md' | wc -l = 2908`
     (matches Document table exactly)
  3. `docs/_index.json` document count = 2905 (5 template files
     omitted; 2 root docs added)
  4. `.rag/corpus.jsonl` = 30974 chunks across 2905 unique files
  5. Critical-artifact embed check: S2100 parent scoping (97 chunks),
     all 8 xx99 canonical summaries (145-227 chunks each),
     ARCHITECTURE_INDEX (443), RESEARCH_OPERATING_SYSTEM (254),
     OPEN_ARCS (27), CLAUDE.md (20) — all embedded
  6. Latest 5 handoffs (S2000-S2099) — all embedded within
     cascade-close window
  7. S1304 findings re-check: T1 (0 periodic tasks), T2 (`@lru_cache`
     still at `td_handlers_ops.py:78`), T5 (`ingested_via` still
     unfiltered), G5 (Documentation Manager exists but scope-limited
     to cascade execution/verification)
  8. Employee OS handles for docs owner: DOCUMENTATION_MANAGER at
     `core/employees/jobs.py:187` — owned by Rigby; scope covers
     cascade execution, verification, escalation; does NOT cover
     schema, retrieval semantics, or authority framework
  9. Beat schedule for embedding: `refresh-docs-corpus-daily`
     enabled, 4am Denver, hash-gated + unembedded-count fallback,
     fans out `generate_document_embeddings.delay()` per doc
owner: claude (drafted S2101; Rigby SIGN cycle 1 folds land pre-commit)
---

# Session 2101 — Group 2100 Cat A — Corpus State: Reality→Knowledge Gap Audit

> **Static snapshot.** This audit captures the RAG corpus as it exists
> at HEAD `053e5fc5` on `main` (2026-07-04, LOCAL DB). It is a
> photograph, not a mechanism explainer. Cascade *how* it flows is P2
> (S2102). Retrieval authority *should carry* contract is P3 (S2103).
> Behavior-substrate effects are P4 (S2104). This document delivers
> what parent §5.1 required: (a) a five-step Reality→Knowledge gap
> matrix; (b) DocumentEmbedding schema-present metadata inventory
> (Q8-a); (c) 18-field ROI-trim; (d) core-required + doc-type-profile
> candidate lists per D2100.9 hybrid contract shape; (e) knowledge-debt
> classification framework anchored to observed incidents.

## 1. Executive Summary

**Corpus posture — one-sentence answer to the central lens question
(P1-scope):** LOCAL Rigby's corpus is *materially complete but
semantically thin* — every on-disk research artifact is embedded, but
half of embedded chunks carry no metadata and the ones that do carry
only three fields (`document_id`, `document_type`, `document_title`).
The corpus is **structurally healthy at the file/embedding boundary,
structurally under-specified at the retrieval-authority boundary.**
Parent scoping's institutional-knowledge-layer maturity criteria (§1
acceptance criteria 1–5) score: **1/5 met unambiguously** (criterion 1
"every canonical summary + closed child audit embedded within the
cascade-close window" — MET); criteria 2–5 not evaluable from static
snapshot alone (they require P3 framework design + P4 observation).

**Coverage ≠ retrieval readiness** (Q1 SIGN STRENGTHEN 2026-07-04):
100% embed coverage can and does coexist with "institutional
knowledge layer not met" because authority / freshness / governance /
lifecycle require metadata + lifecycle signals, not just embeddings.
Embedding is the necessary but insufficient substrate. The gap between
"coverage" and "retrieval readiness" is the object P3 designs and P4
observes.

**Five-step gap matrix — headline numbers (LOCAL 2026-07-04, HEAD
`053e5fc5`):**

| Step | Substrate | Count | Delta vs previous | Delta type |
|------|-----------|-------|-------------------|------------|
| 0    | On-disk `docs/` `.md` files                | 2,908 | — | Reality baseline |
| 0'   | Repo-root docs (`CLAUDE.md`, `00-START-NEXT-SESSION.md`) | +2 | +2 | Reality (extra roots) |
| 1    | `docs/_index.json` document entries        | 2,905 | −5, +2 | Cascade step 1: 5 template files omitted, 2 root docs added |
| 2    | `.rag/corpus.jsonl` unique files           | 2,905 | 0 | Cascade step 2: perfect sync with step 1 |
| 2a   | `.rag/corpus.jsonl` total chunks           | 30,974 | ×10.66 avg | LOCAL keyword-lane chunking (fixed 1200-char) |
| 3    | `Document` rows                            | 2,908 | +3 vs step 2 | Cascade step 3: root docs + others |
| 4    | `DocumentEmbedding` rows                   | 51,789 | ×17.81 avg | Cascade step 4: PROD-lane pgvector chunking |
| 4'   | Documents with ≥1 embedding                | 2,908 | +0 orphan | Coverage: 100% locally |
| 4''  | Orphan embeddings (FK-null OR Document row missing) | 0 | — | Referential integrity intact |
| 4''' | Chunk-distribution per document            | min 1 / p50 11 / avg 17.81 / p95 47 / p99 169 / max 443 (29 outliers > p99) | — | Long-tail exists (max = ARCHITECTURE_INDEX at 443 chunks); watch for pathological chunking on large docs |

**Key readings from the matrix:**
- **No unembedded Documents locally** — the S1234 "1820-never-pushed"
  failure mode is remediated by `refresh_docs_corpus`. LOCAL is
  self-healing daily.
- **5-doc silent-loss at step 1** — spokesperson-corpus template
  files (`docs/docs-pattern/spokesperson-corpus/templates/_facts.md`
  et al.) never make it into `_index.json`. They are frontmatter-less
  scaffold files that `build_docs_index` skips silently.
- **Chunk-count divergence between corpus.jsonl (10.66/doc) and
  DocumentEmbedding (17.81/doc)** — the two lanes chunk with
  different strategies. This is the LOCAL keyword-lane vs PROD
  pgvector-lane divergence S1108 + S1304 §4 documented at the
  boundary. Not a bug; a lane-design fact. P2 (S2102) audits whether
  this divergence is intentional or drift.
- **Metadata-present rate 51.8%** — 26,809 of 51,789 DocumentEmbedding
  chunks carry any `metadata` payload; 24,980 have empty `metadata={}`.
  Split correlates exactly with `ingested_via` split
  (26,809 unknown / 24,980 sync_docs). Write-side asymmetry between
  ingest paths.
- **`source_type='api'` monoculture** — all 51,789 chunks share
  `source_type='api'`. The field lost its discriminative meaning at
  the schema level (see §4.2 Finding F1).
- **Model-drift risk: zero** — all 51,789 chunks embed via
  `openai_text_embedding_3_small`. No mixed-model retrieval risk.

**Five headline findings:**
- **F1 — `source_type` monoculture** (§4.2) — 100% chunks tagged
  `api`; field carries zero discriminative signal despite S1304 D3
  refutation of orphan claim. Likely-cause tag: single write-site
  default at ingest.
- **F2 — Metadata population asymmetry between ingest paths** (§7.3)
  — `unknown` ingest path writes 3 metadata fields; `sync_docs` ingest
  path writes empty metadata. **Working hypothesis pending code-path
  verification (Q4 + Q6 SIGN STRENGTHEN 2026-07-04):** suspected
  missing `metadata=` kwarg in the `sync_docs_index_to_documents`
  step-3 write-site. Confirmation would require (i) grep at each
  write-site, (ii) inspect `metadata=` kwargs, and (iii) trace one
  ingest run per path. P2 audits the mechanism.
- **F3 — Cascade step 1 silently drops 5 template files** (§14 D1) —
  spokesperson-corpus templates lack frontmatter and `build_docs_index`
  skips them without warning. Likely-cause tag: skip-on-missing-
  frontmatter rule with no downstream visibility.
- **F4 — Provenance-index (`docs/_provenance.json`) rebuild
  unscheduled** (§14 D2 = S1304 T1 confirmed) — 0 periodic tasks
  match `provenance`; `build_docs_provenance` remains manual-only.
  Likely-cause tag: cascade-integration debt.
- **F5 — Documentation Manager scope covers cascade execution but
  not retrieval semantics / authority framework** (§18) — S1304 G5
  partially remediated by Employee OS installation; scope-gap
  remains. Likely-cause tag: ownership-boundary asymmetry between
  execution and governance.

**Knowledge-debt taxonomy (§15.3, six categories):**
KD-1 unembedded-on-disk; KD-2 stale-embed-post-content-change;
KD-3 cascade-PR-forgot-embed-step; KD-4 metadata-blank-at-ingest;
KD-5 provenance-index-stale; KD-6 orphan-Document-row-post-file-move.
LOCAL observed instance counts: KD-1=0, KD-4=24,980 chunks,
KD-5=indeterminate (staleness bound not measurable without hash
delta), KD-3 witnessed retrospectively S1802, KD-2/KD-6 not
observed but P2/P3 addressable. See §15.3 for full framework.

**D2100.9 hybrid metadata contract candidate lists (§5.3):**
Core-required (global, fatal-if-missing) = 6 fields;
doc-type profile (research-artifact-specific, recommended per class) =
3 profiles × 3–6 fields each; derivable-at-ingest (schema-computable) =
4 fields; aspirational (requires frontmatter changes to every doc) =
5 fields. Full lists in §5.

**What P1 does NOT decide (per parent §7 anti-scope + Q5 SIGN fold):**
The audit does not commit to *how* metadata gets populated (that is
P2 pipeline design), *what* every chunk MUST carry (that is P3
governance design), or *whether* metadata scarcity actually degrades
Rigby's SIGN quality (that is P4 observation). P1 delivers the
inventory + gap matrix + candidate contract lists that P2/P3/P4 build
on.

**Confidence:** MEDIUM-HIGH on quantitative counts (ORM-sampled at
HEAD `053e5fc5`, single-transaction); MEDIUM on classifications
(likely-cause tags are hypotheses, not verified causality per Q5 SIGN
belongs-to boundary); MEDIUM on knowledge-debt taxonomy (six
categories cover observed incidents but may not enumerate all future
failure modes).

---

## 2. Domain Purpose

The RAG corpus exists to make architectural truth **retrievable,
fresh, governed, and behavior-shaping** inside Rigby (per parent §1
Knowledge Loop framing). It sits at the join between:

- **Reality** — the source-of-truth artifacts: `docs/*.md`,
  `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `docs/_provenance.json`
  (git-history-derived), and the runtime-derived
  `PLATFORM_INVENTORY.md`.
- **Knowledge** — the persisted retrievable state: `docs/_index.json`
  (file-metadata index), `.rag/corpus.jsonl` (LOCAL keyword lane), the
  `content.Document` table (institutional record with UUID FK
  identity), and the `content.DocumentEmbedding` table (PROD pgvector
  lane with per-chunk vectors).

The **corpus-state audit** answers: at any given moment, what
percentage of Reality is representable in Knowledge, along which
axes (existence / coverage / freshness / metadata / model), and
where are the observable gaps? P1 delivers the **static snapshot
view of that question.** P2 answers *how* the cascade steps between
Reality and Knowledge work. P3 answers *what should be true* about
metadata + retrieval authority. P4 answers *whether* corpus health
correlates with Rigby's behavior quality.

**Corpus purpose is NOT** (per parent §7 anti-scope):
- To be a full-text search over every file the repo has ever
  contained (archive/, superseded docs, historical experiments are
  included but are lifecycle-classifiable, not filterable at the
  schema level today).
- To be a substitute for `PLATFORM_INVENTORY.md` runtime-derived
  counts (per DOC_LIFECYCLE.md §2c, inventory-wins-on-conflict for
  runtime facts).
- To be the AI/user-memory substrate (Group 1300 territory —
  `AgentMemory`, `ConversationMemory`, etc. are separate storage).

---

## 3. Canonical Entry Points

Static-snapshot audit reads (not modifies) the substrate at these
canonical entry points. Each is verified STILL PRESENT at HEAD
`053e5fc5`.

### 3.1 Read-side entry points

| Entry point | Purpose | File:line at HEAD |
|-------------|---------|-------------------|
| `_load_provenance_docs()` | Load `docs/_provenance.json`; `@lru_cache(maxsize=1)` per-process cache | `core/services/td_handlers_ops.py:78-93` |
| `search_docs` PA tool handler | RAG retrieval (dispatches to LOCAL keyword or PROD pgvector lane per env) | `core/services/td_handlers_ops.py` (retrieval-side handler; see S1304 §5) |
| `kb_tool` | Knowledge-base search over `Document` + `DocumentEmbedding` | tool schema in `pa_tool_schemas.py` |
| `Document` / `DocumentEmbedding` ORM | Institutional storage | `content/models.py:707-918` (per S1304 §5) |

### 3.2 Write-side entry points

| Entry point | Purpose | File at HEAD |
|-------------|---------|--------------|
| `build_docs_index` mgmt command | Cascade step 1: scan `docs/` → `docs/_index.json` | `core/management/commands/build_docs_index.py` |
| `build_rag_corpus` mgmt command | Cascade step 2: `_index.json` → `.rag/corpus.jsonl` (LOCAL keyword chunks) | `core/management/commands/build_rag_corpus.py` |
| `sync_docs_index_to_documents` mgmt command | Cascade step 3: index → `Document` rows (+ optional `--embed` for step 4 inline) | `core/management/commands/sync_docs_index_to_documents.py` |
| `embed_documents` mgmt command | Cascade step 4: `Document` rows → `DocumentEmbedding` chunks | `core/management/commands/embed_documents.py` |
| `build_docs_provenance` mgmt command | Rebuild `docs/_provenance.json` (git-history-derived) | `core/management/commands/build_docs_provenance.py` |
| `backfill_doc_provenance` mgmt command | Sibling backfill utility | `core/management/commands/backfill_doc_provenance.py` |
| `refresh_docs_corpus` Celery task | Daily beat-driven auto-cascade | `core/tasks.py` (see §5.2) |

### 3.3 Employee-OS ownership

| Handle | Job | File:line | Scope |
|--------|-----|-----------|-------|
| `docs_manager` (Rigby) | `DOCUMENTATION_MANAGER` JobContract | `core/employees/jobs.py:187` | Cascade execution + verification + escalation (§18 flags governance-scope gap) |

---

## 4. Major Models

### 4.1 `content.Document` — institutional record

Concrete Django model, 45 non-relation fields. Represents a stored
document with lifecycle + metadata + processing state.

**Field families (grouped for readability):**

| Family | Fields |
|--------|--------|
| Identity + audit | `id` (UUID), `created_at`, `updated_at`, `version`, `is_active`, `metadata` (JSONField) |
| File-source | `file_path`, `original_filename`, `file_size`, `mime_type` |
| Content | `raw_content`, `processed_content`, `content_hash`, `word_count`, `readability_score`, `language`, `extracted_metadata`, `key_phrases`, `entities` |
| Classification | `title`, `description`, `document_type`, `document_class`, `category`, `collection`, `tags` |
| Lifecycle + governance | `status`, `promotion_status`, `is_pinned`, `is_critical`, `risk_level`, `data_sensitivity`, `is_public` |
| Retrieval + counters | `retrieval_boost`, `view_count`, `download_count`, `last_accessed` |
| Cross-reference | `source_system`, `source_reference`, `source_url`, `cross_references`, `incident_date` |
| Process | `processing_log`, `error_message` |

**Present but underused (Q8-a inventory input):** `status`,
`promotion_status`, `document_class`, `collection` — these are
lifecycle governance carriers per S1304 §4 that P3 will design the
lifecycle transitions on. `retrieval_boost` exists but no discovered
consumer applies it at retrieval-rank time (deferred verification).

### 4.2 `content.DocumentEmbedding` — per-chunk retrieval unit

Concrete Django model, 19 non-relation fields. Represents a single
embedded chunk of a Document.

**Complete field inventory (Q8-a authoritative answer):**

| # | Field | Population (LOCAL 2026-07-04, N=51,789) | Notes |
|---|-------|------------------------------------------|-------|
| 1 | `id` | 100% | UUID PK |
| 2 | `created_at`, `updated_at` | 100% | audit |
| 3 | `version`, `is_active` | 100% | soft lifecycle |
| 4 | `document` (FK) | 100% | join to `Document` |
| 5 | `embedding_model` | 100% (single value: `openai_text_embedding_3_small`) | model-drift risk: ZERO locally |
| 6 | `chunk_index` | 100% | ordinal within document |
| 7 | `chunk_text` | 100% | source text |
| 8 | `chunk_size`, `overlap_size` | 100% | chunking config |
| 9 | `embedding_vector` (pgvector) | 100% | the vector itself |
| 10 | `embedding_dimension` | 100% | derivable from model |
| 11 | `context_before`, `context_after` | population unmeasured (may be empty strings) | retrieval-time context |
| 12 | `metadata` (JSONField) | **51.8% populated** (26,809) / **48.2% empty** (24,980) | asymmetric write-site (see F2 §7.3) |
| 13 | `processing_time_ms`, `embedding_cost` | 100% | ops/telemetry |
| 14 | `source_type` | 100% (single value: `api`) — **F1 monoculture** | S1304 D3: consumer at `content/embeddings.py:965-973, :1007` filters on this; discriminative signal LOST |
| 15 | `ingested_via` | 100% (52% `unknown`, 48% `sync_docs`; `backfill` absent LOCAL) | S1304 D7/T5: still F4-CANDIDATE per S1303 §14 discipline pending §19 R1 full-tree recheck |

**S1304 verifier-loop re-attestation (S2101 refutes/confirms):**
- `source_type` field: **STILL populated** but LOCAL DB shows
  monoculture (`api` only). The S1304 verifier confirmed a
  consumer at `content/embeddings.py:965-973` filters on it, but the
  filter is dead-code-locally because every row shares the same
  value. Finding severity: MEDIUM (schema-consumer alive, but
  discriminative axis missing).
- `ingested_via` field: **STILL populated** with 2 distinct values.
  The S1304 D7 F4-CANDIDATE claim (no retrieval-side consumer)
  remains CANDIDATE — no consumer discovered in this audit's
  read-side sweep. P2 pipeline audit (S2102) should include
  full-tree grep as part of S1399 §19 R1 discharge.

### 4.3 On-disk supporting artifacts

| Artifact | Path | Purpose | Present at HEAD |
|----------|------|---------|-----------------|
| Docs index | `docs/_index.json` | file-metadata scan of `docs/` + selected root docs | YES (4.5MB, mtime 2026-07-04 20:19) |
| LOCAL corpus | `.rag/corpus.jsonl` | keyword-lane chunks (10.66/doc avg) | YES (39MB, mtime 2026-07-04 20:19) |
| Provenance index | `docs/_provenance.json` | git-history-derived per-doc metadata (per S1304 §5) | YES — but refresh cadence unmanaged (see §14 D2 = S1304 T1 STILL VALID) |

---

## 5. Major Services

### 5.1 Cascade services (write-side)

The four cascade commands are the primary write-side services. Each is
a Django `BaseCommand` at `core/management/commands/`. Runtime-flow
detail is P2 (S2102). This audit only names them + confirms presence
at HEAD.

| Step | Command | Substrate written | LOCAL corpus.jsonl mtime confirms 2026-07-04 |
|------|---------|-------------------|-----------------------------------------------|
| 1    | `build_docs_index` | `docs/_index.json` | YES |
| 2    | `build_rag_corpus` | `.rag/corpus.jsonl` | YES |
| 3    | `sync_docs_index_to_documents` | `Document` rows | (Document table live) |
| 4    | `embed_documents` OR `sync --embed` | `DocumentEmbedding` rows | (2908 embedded rows) |

### 5.2 `refresh_docs_corpus` — beat-driven auto-cascade (S1235 remediation)

**Verified live at HEAD `053e5fc5`:** `PeriodicTask
name=refresh-docs-corpus-daily task=core.tasks.refresh_docs_corpus
schedule=(4 0 * * *) America/Denver enabled=True`.

**Docstring evidence (from `core/tasks.py`):**
- Purpose: "Session 1235 P5#2 — closes the 12-day-stale failure mode
  discovered during Session 1234's D9→D16 docs-corpus retrieval arc."
- Behavior: hash-delta gated (compares `docs/_index.json` hash
  against cached `docs_corpus:last_index_hash`) with **secondary
  unembedded-count trigger** (self-heals partial step-4 failures).
- On trigger: runs `build_docs_index` → `build_rag_corpus` →
  `sync_docs_index_to_documents`, then fans out
  `generate_document_embeddings.delay()` per doc if
  `unembedded_count > 0` (avoids 25-min beat-task blocking).
- Idempotency: if hash unchanged AND `unembedded == 0` AND not
  `force`: skip.

**S1802-incident regression coverage (scoped per Q5 SIGN STRENGTHEN
2026-07-04):** the secondary unembedded-count trigger **reduces the
persistence window** of unembedded docs after a cascade PR — it does
not prevent the situation at merge time. Timing gap: unembedded state
persists from cascade PR merge → next-day 4am Denver
`refresh_docs_corpus` fire (worst case: ~24 hours). During that
window, Rigby's RAG is blind to the affected docs. The backstop is
strong across days; the same-day gap remains a legitimate concern for
merges that immediately precede a SIGN cycle. Merge-time protection
would require CI-blocking cascade or event-driven embed fanout — both
out of P1 scope (P2 designs).

**What refresh_docs_corpus does NOT do (§14 D2 / F4 finding):**
- Does NOT rebuild `docs/_provenance.json`. `build_docs_provenance`
  remains manual-only (0 periodic tasks). This is S1304 T1 STILL
  VALID.
- Does NOT invalidate the `@lru_cache(maxsize=1)` cache in
  `_load_provenance_docs()`. This is S1304 T2 STILL VALID
  (worker-restart or file-watcher or Redis-backed cache remain the
  design options).

### 5.3 `DOCUMENTATION_MANAGER` — Employee OS ownership

Located at `core/employees/jobs.py:187`. Handle: `docs_manager`.
Employee: `rigby`. Manager: `chris`.

**Mission (verbatim excerpt):** "Rigby owns running the documentation
cascade, recording evidence, certifying successful runs, and
escalating failures or drift. Sync between docs/ on disk and the
index / RAG corpus / Document table / DocumentEmbedding table is a
best-effort operational target contingent on the cascade commands
succeeding."

**Scope-boundary finding (feeds §18 Ownership Gaps):** The
Documentation Manager scope covers **execution + verification +
escalation** of the 4-step cascade. It does **NOT** cover:
- The `DocumentEmbedding` schema definition (owned by `content` app
  authors implicitly, no named employee)
- Retrieval semantics inside `search_docs` / `kb_tool` (no named
  employee owns retrieval-rank behavior)
- The retrieval authority framework (S1304 G5; S2103 designs)
- The `docs/_provenance.json` write-owner assignment (S1304 T8
  proposed Cat E; still un-assigned)

This is S1304 G5 boundary-unowned finding, **partially remediated**
by the Documentation Manager installation but **not fully closed**
until schema + retrieval + authority ownership are also assigned
(S2103 governance-design deliverable).

---

## 6. Major APIs and Interfaces

RAG retrieval APIs (read-side) are consumed by:
- **PA tool surface** — `search_docs`, `kb_tool` (dispatch to lane
  based on env)
- **Rigby SIGN cycle** — implicit consumer of RAG lookup during
  pressure-test payload construction
- **`refresh_docs_corpus` Celery task** — write-side; not an API but
  an automation surface

This audit does not enumerate every consumer (P4 observation surfaces
consumer-side effects; P3 designs consumer-facing authority contract).
Static snapshot: the read-side handlers exist at
`core/services/td_handlers_ops.py` and consume `Document` /
`DocumentEmbedding` + `docs/_provenance.json` per S1304 §5-§7 flow
diagrams.

**Two-lane divergence (P2 concern, flagged here for record):** LOCAL
keyword-lane vs PROD pgvector-lane operate over the *same*
`.rag/corpus.jsonl` file (LOCAL) vs *same* `DocumentEmbedding` table
(PROD). Chunk counts diverge (10.66/doc vs 17.81/doc) because
`.rag/corpus.jsonl` chunks with fixed 1200-char and
`DocumentEmbedding` chunks with different strategy (P2 audits the
divergence intent).

---

## 7. Runtime Flows

### 7.1 Cascade write-flow (verified structure only — mechanism is P2)

```
┌──────────────┐  build_docs_index  ┌───────────────┐  build_rag_corpus  ┌──────────────────┐
│ docs/*.md    │  ────────────────► │ docs/_index   │  ────────────────► │ .rag/corpus.jsonl│
│ + CLAUDE.md  │                    │ .json (2905)  │                    │ (30,974 chunks)  │
│ + 00-START   │                    │               │                    │                  │
│ (2908 + 2)   │                    └───────────────┘                    └──────────────────┘
└──────────────┘                            │
                                            │ sync_docs_index_to_documents
                                            ▼
                                    ┌────────────────┐  embed_documents  ┌─────────────────────┐
                                    │ Document rows  │  ───────────────► │ DocumentEmbedding   │
                                    │ (2,908)        │                   │ (51,789 chunks)     │
                                    └────────────────┘                   └─────────────────────┘
                                            │                                     ▲
                                            │                                     │
                                            └── generate_document_embeddings ─────┘
                                                (fan-out via refresh_docs_corpus  )
                                                (when unembedded_count > 0        )
```

### 7.2 Cascade read-flow (surface-map only)

Read-side handlers query `Document` / `DocumentEmbedding` + load
`docs/_provenance.json` (via the cached `_load_provenance_docs()`)
for provenance filtering. Mechanism detail deferred to P2.

### 7.3 Ingest-path write-site divergence (F2 finding — WORKING HYPOTHESIS pending code-path verification per Q6 SIGN STRENGTHEN 2026-07-04)

**Verification status label:** This section explains a *working
hypothesis* about why the metadata JSONField population divides
51.8% / 48.2% between the two `ingested_via` values. Author did not
personally grep-trace either write-site at draft time; the causal
inference is derived from S1304 §14 D3 write-site inventory + the
observed LOCAL DB row distribution.

**Confirmation method (deferred to P2 pipeline audit):**
(1) grep both call sites for `metadata=` kwarg presence;
(2) inspect the derivation logic in `content/embeddings.py:45-63`
    `_derive_source_type`;
(3) trace one ingest run per path (log at write-time to observe the
    `metadata=` value the ORM `create()` receives).

At LOCAL 2026-07-04, `DocumentEmbedding.ingested_via` splits into
two populated values (population per 51,789 chunks):

| `ingested_via` | Count | Share | `metadata` payload observed |
|----------------|-------|-------|------------------------------|
| `unknown`      | 26,809 | 51.8% | `{document_id, document_type, document_title}` |
| `sync_docs`    | 24,980 | 48.2% | `{}` (empty JSONField) |
| `backfill`     | 0     | 0%    | (absent LOCAL) |

**Interpretation (likely-cause hypothesis tag, not verified
causality per Q5 SIGN boundary):** the `unknown` path is the
`content/embeddings.py` write-site (per S1304 §14 D3 evidence
inventory); the `sync_docs` path is the `sync_docs_index_to_documents`
step-3 write-site which explicitly annotates `ingested_via='sync_docs'`.
The metadata-population divergence follows from these being two
different call sites with different explicit `metadata=` kwargs. P2
audits the mechanism.

Consequence today: **48.2% of retrievable chunks carry no
document_id / document_type / document_title in the metadata JSONField**.
The parent `Document` row still carries `document_type`, `id`, and
`title`, so the info is join-recoverable — but any retrieval-time
filter that consults `metadata` directly (not via join) is blind to
half the corpus.

### 7.4 Latency dimension (P2 concern — flagged for handoff)

Doc-change-to-embed latency is not measurable from static snapshot —
requires longitudinal observation. P2 designs the hash substrate to
make it measurable; P4 observes it. Parent §5.5 Corpus Health Score
Dimension #8.

---

## 8. Data Ownership and Lifecycle

### 8.1 Lifecycle status carriers (schema-present today)

`Document.status` and `Document.promotion_status` — declared but not
inventoried in this audit (population distribution not sampled per
Q5 SIGN boundary; P3 governance design surfaces the lifecycle
state machine). S1304 §4 documented these as lifecycle carriers
without ratified transitions.

### 8.2 Authority ownership by axis (S1304 G5 depth-view)

| Axis | Owned by (current state) | Gap | S1304 finding |
|------|--------------------------|-----|---------------|
| Cascade execution | Documentation Manager (Rigby) | remediated | G5 partial-remediation |
| Cascade verification | Documentation Manager (Rigby) | remediated | G5 partial-remediation |
| Cascade escalation | Documentation Manager (Rigby) | remediated | G5 partial-remediation |
| `DocumentEmbedding` schema definition | `content` app authors (implicit) | UNOWNED at Employee-OS layer | G5 residual |
| Retrieval semantics (rank, filter, threshold) | Nobody named | UNOWNED | G5 residual |
| Retrieval authority framework | Nobody named | UNOWNED | G5 residual (S2103 designs) |
| `docs/_provenance.json` write | Nobody named — command is manual-only | UNOWNED | S1304 T8 recommended Cat E |
| Corpus health / drift detection | Nobody named | UNOWNED | S1304 T7 recommended |

**Distillation:** ownership is **strong at cascade-execution layer,
absent at semantic-governance layer.** P3 (S2103) governance design
assigns the missing owners; P1 confirms the assignment gap remains
open.

### 8.3 Document lifecycle (P3 concern)

Draft / active / canonical / superseded / deprecated transitions
(per parent §5.3 P3 load-bearing question Q6) are not
schema-enforced. `Document.status` and `Document.promotion_status`
exist but state machine + transition triggers are not defined at the
code level. P3 designs. P1 confirms the schema slots exist to hold
whatever state model P3 ratifies.

---

## 9. Integrations With Other Domains

Static-snapshot integration touch points (for handoff / cross-arc
awareness):

| Adjacent domain | Integration surface | Direction | Status |
|-----------------|---------------------|-----------|--------|
| Group 1300 Memory | Boundary at docs↔RAG (S1304) | Consumed | S1304 baseline (per D2100.4 Q2 SIGN fold — not re-audited) |
| Group 2000+ Event/Integration Architecture | SPIDER_DATA producer → RAG consumer (S2001 F3 WEAK) | Producer → Consumer | Deferred to S2102 P2 pipeline audit |
| Group 1700 Observability | `td_handlers_ops.py:5585-5590` filter counters (S1304 D8) | Consumed | S1304 T6 recommends observability telemetry |
| Group 1900 Authority Enforcement | Authority framework precedent (Plane Precedence Policy pattern) | Pattern-reusable | Deferred to S2103 P3 authority framework |
| Employee OS (`core/employees/jobs.py`) | Documentation Manager handle | Consumed | Cascade-scope only (see §5.3) |

**Explicit anti-scope reaffirmed (parent §7):** this audit does
NOT re-audit Group 1300 memory territory, does NOT re-audit Group
2000+ EventBus/HAI, does NOT design cross-plane composition.

---

## 10. Event Flows

**Static-snapshot answer (non-exhaustive sweep per Q7 SIGN
STRENGTHEN 2026-07-04):** No `event_bus.publish(...)` calls were
discovered in the sampled cascade modules the author inspected —
specifically `core/tasks.py` (`refresh_docs_corpus` body), and the
management-command modules named at §3.2. This is **not** an
exhaustive codebase sweep; P2 pipeline audit performs the full
sweep and confirms/refutes cascade EventBus absence definitively.

**Consequence (contingent on non-exhaustive sweep verdict):**
downstream observers cannot subscribe to cascade events via
EventBus; monitoring is limited to Celery task telemetry
(`CeleryTaskEvent` per S1245 zero-fire audit framework) + ad-hoc
`logger.info` emissions. If P2 confirms the absence, this promotes
to a durable finding (see §14 D7).

**Deferred to P2 pipeline audit (S2102):** whether cascade steps
should emit events, and whether the S2001 F3 SPIDER_DATA
MISSING-producer would benefit from event-driven RAG ingestion (per
parent §5.2 load-bearing question set).

---

## 11. Existing Documentation

Prior work that this audit consumes as baseline (per parent §5.1
delegated-inheritance):

| Doc | Session | Relevance to P1 |
|-----|---------|-----------------|
| S1301 Memory RAG Retrieval Lanes Audit | S1301 | LOCAL keyword vs PROD pgvector lane definition — feeds §6, §7 |
| S1304 Memory ↔ Docs/RAG Boundary Audit | S1304 | Baseline for cascade + D2/D3/D7/D8/T1/T2/T5 findings — this audit re-attests them at HEAD `053e5fc5` |
| S1234 handoff (12-day-stale + 1820-never-pushed incident) | S1234 | Motivated `refresh_docs_corpus` daily-beat installation — verified STILL LIVE |
| S1802 handoff (6-unembedded-docs cascade incident) | S1802 | Motivated `feedback_cascade_pr_must_include_embed_step` MEMORY.md rule — codified here as KD-3 |
| `docs/KNOWLEDGE_PIPELINE.md` | S243-S245, S400 | Existing narrative flow map — companion anchor |
| Parent scoping `2100_rag_document_loading_domain_scoping.md` | S2100 | Ratified D-verdicts + arc frame + Q1-Q12 SIGN folds |
| `DOC_LIFECYCLE.md §2c` | S1275 | `PLATFORM_INVENTORY.md` inventory-wins-on-conflict rule — feeds §17 authority framework |
| MEMORY.md `feedback_docs_pipeline_4_step_cascade` | S1234 close | 4-step cascade codification |
| MEMORY.md `feedback_docs_cascade_at_every_close` | S1399 close | Cascade-at-every-close ritual codification |
| MEMORY.md `feedback_cascade_pr_must_include_embed_step` | S1802 close | Cascade PR must include step 4 embed |

**Gap in existing docs (§14 D3):** No document currently states
*"here are the specific metadata fields DocumentEmbedding.metadata
JSONField carries and their population rate."* This audit's §4.2 +
§7.3 fill that gap.

---

## 12. Research Coverage

Per parent §2.3 depth/lens rubric:

- **S1273 §3.14** row labeled RAG / Document Loading as **DEEP**
  coverage, but P1 re-scoping (parent §1.1) reframes: DEEP-at-Memory-
  boundary-lens (S1301 + S1304), NOT-YET-DEEP-at-RAG-substrate-lens
  (Group 2100 P1-P4).
- **P1 (this audit)** coverage: DEEP on corpus-state snapshot;
  MEDIUM on knowledge-debt taxonomy (six categories cover observed
  incidents but taxonomy may not enumerate all future modes); NOT
  covered: cascade mechanism (P2), retrieval authority (P3), behavior
  substrate effects (P4).

**Session-boundary re-attestation status:** all S1304 findings that
this audit re-verified at HEAD `053e5fc5` are noted per-finding with
CONFIRMED / STILL-VALID / REMEDIATED / F-CANDIDATE tags. See §14
Known Drift for the disposition table.

---

## 13. Architecture Maturity

**Corpus substrate maturity today (P1 snapshot; P4 answers whether
this maturity level is sufficient):**

| Dimension | Maturity | Evidence |
|-----------|----------|----------|
| Cascade execution | HIGH | `refresh_docs_corpus` daily-beat idempotent + hash-gated + unembedded-count fallback |
| Cascade coverage | HIGH | LOCAL: 100% Document rows embedded; 2905/2910 on-disk indexed |
| Cascade freshness | MEDIUM-HIGH | Daily beat cadence; hash-delta gate means no unnecessary rework |
| Metadata population | MEDIUM | 51.8% chunks carry ≥3 metadata fields; 48.2% empty |
| Metadata schema | LOW | `source_type` monoculture; `ingested_via` write-only; no `research_group`/`domain_slug`/`canonical_summary`/`supersedes` slots |
| Provenance-index freshness | LOW | Rebuild unmanaged (S1304 T1 STILL VALID) |
| Retrieval-authority contract | ABSENT | No axes designed (S2103 will design) |
| Governance ownership | PARTIAL | Documentation Manager exists for cascade; schema/retrieval owners absent |
| Observability | LOW | Filter counters exist as response-payload fields but not logged/metered (S1304 T6 recommends) |
| Health scoring | ABSENT | No composite corpus-health measurement (S2199 xx99 proposes §5.5 dimensions) |

**Institutional-knowledge-layer acceptance criteria scoring** (parent
§1 5-criteria):

| # | Criterion | LOCAL @ HEAD `053e5fc5` | Note |
|---|-----------|-------------------------|------|
| 1 | Every canonical summary + closed child audit embedded within cascade-close window | MET | All 8 xx99 + latest handoffs embedded |
| 2 | Retrieval authority framework returns non-conflicting authorities for ≥95% of query classes tested | NOT EVALUABLE | P3 designs the framework; then P4 tests |
| 3 | Superseded docs demoted or excluded from top-k for "current truth" queries | NOT EVALUABLE | No supersession metadata slot (§4.2 + §14 D3); can't rank against something absent |
| 4 | Corpus health score trackable + interpretable | NOT EVALUABLE | §5.5 designs the score; P4 validates via observation |
| 5 | Freshness-bounds and authority conflicts surface visibly (not silently) at retrieval time | NOT MET | Filter counters silent (S1304 D8/T6); no visible conflict-surface |

**Overall maturity verdict (P1 posture only):** the substrate is
**cascade-mature, authority-immature.** P2/P3/P4 map the path from
"documents flow through the pipeline" to "governed institutional
knowledge layer."

---

## 14. Known Drift

**Convention:** drift findings are labeled D1–DN. Each carries an
inheritance tag (S1304 D-ID or S2101-new) and a disposition tag
(CONFIRMED / STILL-VALID / F-CANDIDATE / REMEDIATED-ELSEWHERE).

### D1a — 5 template files silently dropped at cascade step 1 (S2101-new; instance)

- **Affected files:** `docs/docs-pattern/spokesperson-corpus/templates/_facts.md`,
  `_faq.md`, `_overview.md`, `_product.md`, `_story.md`
- **Evidence:** on-disk sweep 2,908 vs `_index.json` `documents` array
  2,905, difference = 5 files not present in index (+2 root-doc
  additions net to 2905)
- **Likely-cause tag** (Q5 SIGN boundary — hypothesis, not verified):
  `build_docs_index` skips files without frontmatter
- **Severity:** LOW — template files, not knowledge artifacts. This
  specific instance is not itself the real finding.
- **Disposition:** may keep or remediate as trivial; the real
  finding is D1b.

### D1b — Silent-drop telemetry gap at cascade step 1 (S2101-new; PATTERN — Q9 SIGN STRENGTHEN 2026-07-04)

- **Pattern:** `build_docs_index` (and by extension any silently
  filtered cascade step) drops files without emitting a warning or
  drop-count telemetry. D1a is the *triggering example* that
  surfaced this pattern; D1b is the durable finding.
- **Generalization risk:** any future add-to-corpus regression
  (renamed frontmatter key, malformed YAML, missing required field,
  path-normalization change) can silently reduce corpus coverage
  with no observability surface. This is exactly the failure mode
  S1802 experienced at cascade step 4.
- **Likely-cause tag** (Q5 SIGN boundary — hypothesis): the cascade
  commands treat "skip on missing precondition" as a valid quiet
  branch instead of a telemetry-emitting event
- **Severity:** MEDIUM — generalizable reliability defect
- **Disposition:** P2 pipeline audit designs the telemetry
  emission (structured log + counter) so future silent-drop
  regressions surface at cascade-close; feeds Corpus Health Score
  §5.5 as a dimension candidate

### D2 — `_load_provenance_docs()` `@lru_cache(maxsize=1)` staleness (S1304 D2 STILL-VALID)

- **Verified at HEAD `053e5fc5`:** `core/services/td_handlers_ops.py:78-79`:
  ```python
  @lru_cache(maxsize=1)
  def _load_provenance_docs() -> dict:
  ```
- **Staleness surface:** per-process cache, no invalidation. Worker
  restarts or explicit `cache_clear()` are the only invalidation paths.
- **Disposition:** S1304 T2 remediation options remain (worker restart
  trigger / file-watcher / Redis / TTL); P3 governance design assigns
  owner + selects mechanism

### D3 — Metadata slots for research-specific fields absent (S2101-new)

- **Evidence:** `DocumentEmbedding.metadata` JSONField is present but
  populated by only 3 fields (`document_id`, `document_type`,
  `document_title`) in the 51.8% populated slice; NONE of Chris's
  aspirational 18-field list (§5.2) are schema-present.
- **Consequence:** cannot filter retrieval by `research_group`,
  `session`, `domain_slug`, `canonical_summary`, `supersedes`,
  `head_commit`, `chunking_version` etc. at the schema level today
- **Likely-cause tag:** no upstream write-site populates these fields
  because they were never designed as slots; frontmatter carries them
  in `.md` files but the cascade doesn't extract → propagate
- **Disposition:** P3 SHOULD-carry contract design decides which
  fields graduate from frontmatter-only to `metadata` slot; P2 designs
  the extraction/propagation mechanism

### D4 — `source_type` monoculture in DocumentEmbedding (F1 detail; S2101-new refinement of S1304 D3)

- **S1304 D3** (2026 pre-refinement): claim was `source_type` is
  orphan-write; S1304 verifier refuted by identifying consumer at
  `content/embeddings.py:965-973, :1007`
- **S2101 refinement:** the consumer exists AND the write-site
  populates the field — but LOCAL DB shows 100% `api` value. The
  discriminative axis is *lost at write time*, not at consumer time.
- **Consequence:** the filter at `content/embeddings.py:965-973` runs
  but has no selection effect (all rows share the same value)
- **Likely-cause tag:** ingest-time `source_type` derivation defaults
  to `'api'` for every path locally; PROD may or may not have this
  monoculture (not verified in P1 scope — LOCAL-only snapshot)
- **Disposition:** P2 audits the write-site derivation logic
  (`content/embeddings.py:45-63` per S1304 §5) and whether the value
  set is intended to diverge across ingest paths

### D5 — `ingested_via` write-only status remains F4-CANDIDATE (S1304 D7 STILL-VALID pending S1399 §19 R1)

- **Verified at HEAD `053e5fc5`:** write-sites at
  `sync_docs_index_to_documents.py:394` (`ingested_via='sync_docs'`),
  `core/tasks_agents.py:4223, 4290, 4351` (`'backfill'`), and
  `content/embeddings.py:654, 753` (`'unknown'` default per
  `_derive_source_type` context) — per S1304 §14 D3 inventory.
- **LOCAL DB slice:** 26,809 chunks `'unknown'` + 24,980 chunks
  `'sync_docs'` + 0 chunks `'backfill'`. `backfill` write-site never
  fires locally (backfill flow does not run in dev environment).
- **Read-side consumer:** NONE FOUND in P1 read-side sweep (this
  audit only re-attests S1304 finding; does not undertake the
  full-tree recheck per S1399 §19 R1 — that is deferred to a
  dedicated verification pass or P2 pipeline audit).
- **Disposition:** F4-CANDIDATE status retained. P2 (S2102) should
  discharge S1399 §19 R1 as part of pipeline audit scope.

### D6 — Provenance-index rebuild cadence unmanaged (S1304 T1 STILL-VALID → promoted to D6)

- **Verified at HEAD `053e5fc5`:** `PeriodicTask.filter(task__icontains='provenance').count() == 0`. `build_docs_provenance` and `backfill_doc_provenance` are the only two references in code; neither is scheduled.
- **Consequence:** `docs/_provenance.json` gets rebuilt manually or
  during specific cascade-close rituals (per MEMORY.md
  `feedback_docs_cascade_at_every_close`); no runtime-guaranteed
  cadence.
- **Disposition:** S1304 T1 remediation candidates remain (add to
  `refresh_docs_corpus` beat OR separate schedule); P3 governance
  design selects mechanism + assigns owner

### D7 — Cascade services emit no EventBus events (S2101-new; §10 detail)

- **Evidence:** no `event_bus.publish(...)` in cascade command source
  or `refresh_docs_corpus` task body
- **Consequence:** downstream observers (health monitors, dashboards,
  drift-detectors) cannot subscribe to cascade lifecycle
- **Likely-cause tag:** cascade predates EventBus adoption; nobody
  went back to wire it after
- **Disposition:** P2 pipeline audit + S2001 F3 (SPIDER_DATA
  MISSING-producer) cross-reference; consider event-driven cascade
  in P2 design

---

## 15. Known Technical Debt

Per playbook §12 (Risk classifications). Debt items D-tier
(depth-of-fix required) — bounded remediation sketches only per Q5
SIGN belongs-to boundary.

### 15.1 Debt-table roll-up (S1304 items re-attested + S2101 additions)

| ID | Debt | Severity | Inherited from / new | Remediation sketch |
|----|------|----------|----------------------|--------------------|
| T1 | Provenance-index rebuild cadence unmanaged | HIGH | S1304 T1 STILL-VALID (see D6) | Add `build_docs_provenance` to `refresh_docs_corpus` beat OR separate schedule; verify index timestamp newer than corpus timestamp |
| T2 | `@lru_cache(maxsize=1)` staleness at `_load_provenance_docs()` | HIGH | S1304 T2 STILL-VALID (see D2) | Worker-restart trigger / file-watcher / move to Redis / time-based TTL |
| T3 | `source_type` monoculture despite live consumer | MEDIUM | S2101-new (see F1/D4) | P2 audits write-site derivation; decide whether to (a) diversify values by ingest path or (b) deprecate consumer + field |
| T4 | Ingestion cascade documentation as topic-doc unpublished | MEDIUM | S1304 T4 STILL-VALID | Publish `docs/topics/docs-ingestion-cascade.md` — deferred to P2 as artifact |
| T5 | `ingested_via` write-path not wired to retrieval | MEDIUM | S1304 T5 STILL-VALID (see D5) | Either add filter on `kb_tool` OR deprecate field after §19 R1 full-tree verification |
| T6 | Filter counters lack operator surface | MEDIUM | S1304 T6 (delegated to Group 1700) | `logger.warning` on drop-rate threshold; Prometheus counter; Grafana dashboard |
| T7 | Corpus-completeness gap not auto-detected | MEDIUM | S1304 T7 (partially remediated by `refresh_docs_corpus` unembedded-count trigger) | Add `verify_provenance_coverage` mgmt command; cache prior confidence breakdown; warn on UNKNOWN increase |
| T8 | Provenance model ownership unassigned | MEDIUM | S1304 T8 STILL-VALID (see §18) | Assign to Cat E ownership; move `build_docs_provenance` into docs-governance mgmt command set; document in `DOC_LIFECYCLE §2b` |
| T9 | Cascade emits no lifecycle events | MEDIUM | S2101-new (see D7) | P2 design decision: whether cascade steps emit `event_bus.publish` for step-complete / embed-fanout / drift-detected |
| T10 | Metadata JSONField schema absent for research-artifact fields | MEDIUM | S2101-new (see D3) | P3 SHOULD-carry contract decides slots; P2 designs extraction; execution debt lands post-arc |

### 15.2 Debt-severity re-attestation summary

| Severity | S1304 baseline | S2101 status | Change |
|----------|----------------|--------------|--------|
| HIGH | T1, T2 | T1, T2 STILL-VALID | 0 net change |
| MEDIUM | T3, T4, T5, T6, T7, T8 | T3, T4, T5, T6 STILL-VALID; T7 PARTIALLY-REMEDIATED (refresh_docs_corpus); T8 STILL-VALID + new T3, T9, T10 | +3 new MEDIUM |

### 15.2.1 S1304 findings NOT re-attested in P1 (Q10 SIGN STRENGTHEN 2026-07-04)

The audit re-attested a subset of S1304 findings sufficient to answer
P1's load-bearing questions. Explicitly enumerating what was NOT
re-attested + why, so future arcs do not misread absence as
invalidation:

| S1304 finding | Re-attest status | Rationale | Downstream owner |
|---------------|------------------|-----------|-------------------|
| S1304 D3 (two provenance systems, complementary-not-duplicate) | NOT re-attested | Q2 SIGN CLEAN + parent scoping D2100.4 explicitly treats S1304 as baseline; no reason to re-open at P1 | P3 governance design (S2103) — assigns owner + scopes |
| S1304 D8 (retrieval filter counters silent) | NOT re-attested | Q5 SIGN belongs-to boundary — this is an observability concern, not a corpus-state concern | Group 1700 Observability (delegated per §19.4) |
| S1304 T3 (two provenance systems partial-decoupled) | NOT re-attested | Same as D3 — baseline | P3 governance design |
| S1304 T4 (ingestion cascade topic-doc unpublished) | STILL-VALID (implicit) — flagged in §15.1 table but no topic doc audited | P1 doesn't ship the topic doc; P2 delivers | P2 pipeline audit (S2102) |
| S1304 T6 (filter-counter operator surface) | NOT re-attested | Same reason as D8 — observability domain | Group 1700 Observability |
| S1304 T7 (corpus-completeness gap auto-detection) | PARTIALLY re-attested | `refresh_docs_corpus` unembedded-count trigger provides partial detection; S1304's full-substrate proposal (`verify_provenance_coverage` mgmt command + cached confidence breakdown + UNKNOWN-increase warning) remains outstanding | P3 governance design (S2103) |
| S1304 T8 (provenance model ownership) | STILL-VALID — surfaced in §18 UNOWNED axis for `docs/_provenance.json` | Explicit re-attest at governance layer | P3 governance design (S2103) |

**Summary:** partial re-attestation was Q5 SIGN belongs-to boundary
compliant — P1 covers what P1 needs to answer its load-bearing
questions. Non-re-attested findings are NOT invalidated; they remain
carried forward per S1304's own severity + disposition until a
downstream arc discharges them.

### 15.3 Knowledge-debt classification framework (parent §5.1 deliverable)

**Definition:** *Knowledge-debt* is a class of technical debt where the
observable failure mode is that Rigby's retrieval (or SIGN cycle, or
downstream reasoning) is missing a knowledge artifact it should have
had, or has an artifact but the artifact's authority/freshness/
metadata is degraded. Distinct from *code debt* because the surface is
the knowledge substrate, not application code.

**Seven knowledge-debt categories (durable taxonomy proposal —
KD-1..KD-7 per Q11 SIGN STRENGTHEN 2026-07-04):**

| Category | Symptom | Detection surface | Observed instances (LOCAL 2026-07-04) |
|----------|---------|-------------------|----------------------------------------|
| **KD-1** — unembedded-on-disk | Doc exists on disk, no `DocumentEmbedding` rows | `Document.objects.filter(embeddings__isnull=True)` | **0 LOCAL** (all 2908 embedded) |
| **KD-2** — stale-embed-post-content-change | Doc content changed since last embed; embedding vectors reflect stale content | Requires `content_hash` at chunk-time vs current `content_hash` (P2 designs hash substrate) | **UNMEASURABLE from static snapshot** (no chunk-time hash tag) |
| **KD-3** — cascade-PR-forgot-embed-step | Cascade PR ran steps 1-3 but forgot step 4; sync succeeded but embed did not | Post-merge `refresh_docs_corpus` next fire catches via unembedded-count trigger (S1235 remediation) | **0 LOCAL currently** (remediated by daily beat); **1 historical: S1802 6-unembedded-docs incident** |
| **KD-4** — metadata-blank-at-ingest | Chunk exists + embedded, but `metadata` JSONField empty or missing required fields | `DocumentEmbedding.objects.filter(metadata={})` count | **24,980 LOCAL** (48.2% of chunks, correlated to `ingested_via='sync_docs'`) |
| **KD-5** — provenance-index-stale | `docs/_provenance.json` older than latest `docs/_index.json` rebuild | Compare file mtimes; `_load_provenance_docs` `@lru_cache` staleness | **INDETERMINATE** — no automated freshness check; both files show mtime 2026-07-04 20:19 today but no bound on drift window |
| **KD-6** — orphan-Document-row-post-file-move | `Document.file_path` points to non-existent file | Iterate `Document` rows + `os.path.exists(file_path)` | **0 LOCAL** (spot-checked handoff subset) |
| **KD-7** — mis-linked-embeddings (Q11 SIGN STRENGTHEN 2026-07-04) | `DocumentEmbedding.document` FK points to wrong Document row (e.g., after rename/refactor); OR chunk text does not match parent Document content | Text-fingerprint compare chunk_text against Document.processed_content window; ORM sweep for FK consistency | **0 detected LOCAL** (0 FK-null; Document-row-present integrity intact per §20.1) — but detection is coarse; fine-grained text-alignment audit deferred |

**Category-boundary rules (per Q5 SIGN belongs-to boundary):**
- KD-1 is diagnostic — the write-side gap.
- KD-2 is measurable-only-with-substrate — requires P2's `content_hash`
  slot design.
- KD-3 is an incident-class — retrospective evidence surfaces it;
  proactive detection is possible via the `refresh_docs_corpus`
  unembedded-count trigger.
- KD-4 is a schema-write-shape issue — visible today via ORM.
- KD-5 is a cross-file freshness issue — surfaces at retrieval-time if
  telemetry existed; today is invisible until manual sweep.
- KD-6 is an integrity issue — visible via ORM sweep; no observed
  instances today but code-change risk exists at file-move time.
- KD-7 is a semantic-integrity issue — coarse detection (FK integrity)
  is easy; fine-grained detection (chunk text ↔ Document content
  alignment) requires substrate P2/P3 may design.

**Explicitly rejected as non-KD categories (parked at proper arc):**
- **KD-7 alternate: chunking-strategy-drift** — belongs to P2 pipeline
  mechanism concerns, not knowledge-debt at rest.
- **KD-8 alternate: retrieval-filter-drift** — belongs to P3
  authority framework governance concerns.
- **KD-9 alternate: governance-debt (missing supersession demotion)**
  — belongs to P3 lifecycle transitions; may be added post-P3 as
  KD-8-graduated once the lifecycle contract exists.

**Framework use by downstream arcs:**
- P2 (S2102) uses categories to bound what mechanism-level changes
  fix which category
- P3 (S2103) uses categories to bound governance contracts (who owns
  detecting/remediating each?)
- P4 (S2104) uses categories to classify observed incidents in the
  Behavior-substrate evidence brief

---

## 16. Boundary Violations

Boundary-lens finding (per S1304 §16 pattern):

**BV-1 — `td_handlers_ops.py:78` reads `docs/_provenance.json`
directly via `_load_provenance_docs()`.** Retrieval-side handler
bypasses any Cat E-provided service abstraction. Boundary-lens verdict
(S1304-inherited): **not a violation** — the file is a contract
artifact and `_load_provenance_docs` is a wrapped reader — but the
coupling is implicit. P3 governance design may formalize reader
service in Cat E.

**BV-2 — Path normalization at `.rag/corpus.jsonl` ↔ cite
reconstruction (S1301-flagged / S1304 §16 inherited).** Corpus paths
drop `docs/` prefix; retrieval-side handler re-adds it via string
prefix. Coupling is deterministic but fragile — a Cat E
path-normalization convention change would silently break citations.

**BV-3 — Ingestion writes to `DocumentEmbedding` with fields only
ingestion understands (`source_type` derivation semantics at
`content/embeddings.py:45-63`) (S1304 inherited).** Retrieval-side
consumer at `content/embeddings.py:965-973` filters on this without a
service-boundary contract naming the value domain. **New S2101
observation:** LOCAL DB shows the field discriminative value is lost
at write time (D4 monoculture) — the boundary contract is de facto
broken by write-side default-value uniformity.

---

## 17. Duplicate or Overlapping Systems

### 17.1 Two chunking lanes (P2 concern; flagged for record)

- **LOCAL keyword lane** (`.rag/corpus.jsonl`): fixed 1200-char
  chunks, 30,974 chunks across 2,905 files, avg 10.66/file
- **PROD pgvector lane** (`DocumentEmbedding` table): different
  strategy, 51,789 chunks across 2,908 docs, avg 17.81/doc
- **Verdict (P1 static-snapshot only) — provenance-anchored per Q8
  SIGN STRENGTHEN 2026-07-04:** two lanes are architecturally
  intentional per **S1304 §4 finding text + observed row counts
  this audit collected LOCAL 2026-07-04**. S1108 is cited as the
  original lane-boundary provenance but was **not re-verified in
  this audit's sweep**. P2 pipeline audit confirms current
  intentionality vs drift.

### 17.2 Two provenance systems (S1304 D3 — partial-decoupled)

- **File-scoped provenance:** `docs/_provenance.json` (git-history-
  derived, per-doc metadata)
- **Row-level provenance:** `DocumentEmbedding.source_type` +
  `ingested_via`
- **S1304 verdict (retained here):** complementary, not duplicate.
  P3 governance design formalizes their scopes / ownership.

### 17.3 Two metadata planes — subset/coverage mismatch, not competing truth (S2101-new; Q12 SIGN STRENGTHEN 2026-07-04)

- **Plane 1 — Frontmatter in `.md` files:** carries research_group,
  session, domain_slug, category, child_slot, status,
  canonical_summary, authority, etc.
- **Plane 2 — `DocumentEmbedding.metadata` JSONField:** carries at
  most 3 fields today (`document_id`, `document_type`,
  `document_title`).
- **Verdict — this is NOT a competing-source-of-truth conflict.**
  Frontmatter is the write-side authoritative source; the
  `DocumentEmbedding.metadata` JSONField is a retrieval-time
  extract that is **failing to populate** (in 48.2% of chunks,
  entirely; in 51.8% of chunks, partially — 3 out of ~15 candidate
  fields). Relationship shape is **subset/coverage mismatch**
  (plane 2 SHOULD be a subset of plane 1 but is under-extracted),
  not **duplicate authority** (both planes claiming truth).
- **P3 SHOULD-carry contract decides which frontmatter fields
  graduate into `metadata` slot.** P2 designs the extraction +
  propagation mechanism.

---

## 18. Ownership Gaps

Consolidated §8.2 ownership-by-axis view for §18 explicit flagging:

| Ownership axis | Owner | Gap | Recommended resolution |
|----------------|-------|-----|------------------------|
| Cascade execution / verification / escalation | Documentation Manager (Rigby) | — | none (remediated by Employee OS install) |
| `DocumentEmbedding` schema | UNASSIGNED (implicit `content` app authors) | HIGH | S2103 P3: assign to Cat E ownership or new employee handle |
| Retrieval semantics (rank, filter, threshold) | UNASSIGNED | HIGH | S2103 P3 governance design |
| Retrieval authority framework | UNASSIGNED | HIGH | S2103 P3 designs the framework AND assigns owner |
| `docs/_provenance.json` writes | UNASSIGNED (`build_docs_provenance` is manual-only) | HIGH (S1304 T1 STILL-VALID) | S2103 P3: assign to Cat E; add to cascade beat |
| Corpus health / drift detection | UNASSIGNED | MEDIUM (S1304 T7 partially-remediated) | S2103 P3: assign; §5.5 Health Score becomes durable metric per D2100.10 |
| Metadata JSONField write-shape | UNASSIGNED (split between `content/embeddings.py` + `sync_docs_index_to_documents.py`) | MEDIUM (F2/D3) | S2103 P3: assign single authority; standardize write-shape at ingest paths |

**Composite ownership verdict:** the cascade *runs* is well-owned;
the substrate *means* is not. This mirrors the §13 maturity verdict
"cascade-mature, authority-immature."

---

## 19. Recommended Future Research

### 19.1 P1 hands off to P2 (S2102 — Ingestion / Chunking / Embedding Pipeline Audit)

- **R2.1 — Mechanism-level cascade documentation.** Publish
  `docs/topics/docs-ingestion-cascade.md` (S1304 T4). Cover: 4-step
  flow, preconditions, postconditions, failure/recovery, cadence
  rationale.
- **R2.2 — Two-lane chunking-strategy audit.** Confirm intent vs
  drift of the 10.66/doc vs 17.81/doc divergence between LOCAL
  keyword lane and PROD pgvector lane. Recommend chunking-version
  metadata slot if warranted.
- **R2.3 — `content_hash` propagation to chunk-time.** Design the
  hash-substrate that KD-2 detection needs. Feeds Corpus Health Score
  Dimension #2 (stale chunk %) and #8 (doc-change-to-embed latency).
- **R2.4 — `source_type` monoculture root-cause.** Audit
  `content/embeddings.py:45-63` `_derive_source_type` logic; decide
  whether to diversify or deprecate.
- **R2.5 — Discharge S1399 §19 R1 for `ingested_via`.** Full-tree
  read-side sweep; either wire a consumer (S1304 T5 option a) or
  deprecate the field (option b).
- **R2.6 — Cascade EventBus emission design.** Whether cascade steps
  should emit lifecycle events; cross-reference S2001 F3
  SPIDER_DATA MISSING-producer.

### 19.2 P1 hands off to P3 (S2103 — Retrieval Authority Framework + Governance)

- **R3.1 — Populate D2100.9 hybrid metadata contract.** Take P1's
  candidate lists (§5.3) and ratify the core-required set +
  doc-type profile fields. Design the enforcement layer (schema
  migration vs service-side validation vs CI check).
- **R3.2 — Retrieval authority framework design.** 8-axis framework
  per parent §5.3 + Q7 SIGN fold (runtime-facts vs research-posture
  split, precedence clarifiers, tie-break rule).
- **R3.3 — Ownership assignments.** Assign owners to §18
  currently-UNASSIGNED axes (`DocumentEmbedding` schema, retrieval
  semantics, retrieval authority framework, `docs/_provenance.json`
  writes, corpus health / drift detection).
- **R3.4 — Cascade governance first-class doc.** Replace informal
  MEMORY.md rules (`feedback_docs_pipeline_4_step_cascade`,
  `feedback_docs_cascade_at_every_close`,
  `feedback_cascade_pr_must_include_embed_step`) with a canonical
  governance doc under `docs/00-START-HERE/` per parent §5.3.
- **R3.5 — Provenance-index rebuild scheduling.** Add
  `build_docs_provenance` to `refresh_docs_corpus` beat OR separate
  schedule (S1304 T1 remediation).

### 19.3 P1 hands off to P4 (S2104 — Behavior Substrate Observation)

- **R4.1 — Knowledge-debt category incidence in observation
  window.** Classify recent SIGN cycles by KD-1..KD-7 category
  (per §15.3 framework); test whether observed KD-4 rate (48.2%
  chunks metadata-blank) has attributable SIGN-quality effect.
- **R4.2 — Institutional-knowledge-layer acceptance criteria
  observation.** Criteria 2, 3, 5 (§13) become observation targets
  once P3 framework lands.
- **R4.3 — Corpus Health Score N-observation-based calibration.**
  Weight + hard-gate thresholds per §5.5 dimensions using P4
  observed incidents.
- **R4.4 — D2100.7 conditional-elevation logic for freshness bounds
  (Q15 SIGN STRENGTHEN 2026-07-04).** P4 explicitly discharges the
  D2100.7 conditional elevation rule: if N ≥ 10 concrete observed
  cases (per Q6 fold) show repeated attributable patterns where
  freshness bounds correlate with SIGN-quality degradation AND
  remediation hooks are enforceable, elevate "RAG freshness bounds
  SIGN quality" from hypothesis → provisional contract. Otherwise
  retain as hypothesis.

**Mechanism-vs-governance boundary re-attestation (Q15 SIGN
STRENGTHEN 2026-07-04):** P2 owns anything requiring **code-path
tracing, cadence design, `content_hash`/latency mechanics, chunking
strategy**. P3 owns anything defining **authority axes,
lifecycle/supersession rules, conflict escalation, metadata contract
enforcement**. The P1 handoff list above conforms to this boundary.

### 19.4 P1 flags for future non-Group-2100 arcs

- **Group 1700 Observability (delegation):** S1304 T6 filter-counter
  operator-surface remediation. `logger.warning` + Prometheus counter
  + Grafana. Cross-arc handoff for observability domain.
- **Documentation / Research Knowledge System (§3.15 not-yet-arc):**
  MEMORY.md-rules-vs-canonical-doc consolidation is arguably a
  research-knowledge-system arc concern too, not solely Group 2100.

### 19.5 P1-scoped follow-ups (must land pre-close if adopted)

None mandatory. All above route to P2/P3/P4 handoffs. P1 status flips
`draft` → `active` on Chris ratification post-Rigby SIGN cycle 1.

---

## 20. Appendix

### 20.1 Verifier-loop evidence log

Executed 2026-07-04 at HEAD `053e5fc5`. All queries LOCAL DB unless
otherwise noted.

**Row counts (single-transaction sample):**
- `Document.objects.count()` = 2,908
- `DocumentEmbedding.objects.count()` = 51,789
- `Document.objects.filter(embeddings__isnull=True).distinct().count()` = 0
- `Document.objects.filter(embeddings__isnull=False).distinct().count()` = 2,908

**On-disk counts:**
- `find docs -type f -name '*.md' | wc -l` = 2,908
- 3 top folders by count: `archive` (1,388), `handoffs` (919), `research` (77)

**Index / corpus counts:**
- `docs/_index.json` `documents` array length = 2,905
- 5 files on-disk missing from index: 5 spokesperson-corpus templates
- 2 extra in index: `CLAUDE.md`, `00-START-NEXT-SESSION.md` (repo root)
- `.rag/corpus.jsonl` line count = 30,974
- Unique `file` values in corpus.jsonl = 2,905 (matches `_index.json`)
- Avg chunks/file in corpus.jsonl = 10.66
- File sizes: `docs/_index.json` = 4.5 MB, `.rag/corpus.jsonl` = 39 MB
- File mtimes: both 2026-07-04 20:19 (fresh)

**DocumentEmbedding aggregate breakdowns:**
- `source_type` distribution: `api` = 51,789 (100%)
- `ingested_via` distribution: `unknown` = 26,809 (51.8%),
  `sync_docs` = 24,980 (48.2%), `backfill` = 0 (0%)
- `embedding_model` distribution: `openai_text_embedding_3_small`
  = 51,789 (100%)
- `metadata` non-empty: 26,809 chunks; empty: 24,980 chunks

**Critical-artifact embed check:**

| Artifact | Chunks |
|----------|--------|
| S2100 parent scoping | 97 |
| S2099 xx99 canonical (Group 2000+) | 188 |
| S1999 xx99 canonical (Authority) | 227 |
| S1399 xx99 canonical (Memory) | 145 |
| S1499 xx99 canonical (Revenue) | 213 |
| S1599 xx99 canonical (Sports) | 224 |
| S1699 xx99 canonical (Content) | 183 |
| S1799 xx99 canonical (Observability) | 182 |
| S1899 xx99 canonical (HumanAttention) | 207 |
| `ARCHITECTURE_INDEX.md` | 443 |
| `OPEN_ARCS.md` | 27 |
| `DOMAIN_RESEARCH_PLAYBOOK.md` | 134 |
| `RESEARCH_OPERATING_SYSTEM.md` | 254 |
| `CLAUDE.md` | 20 |
| S1304 boundary audit | 105 |

All 15 critical artifacts embedded. No canonical summary or arc
parent scoping doc unembedded LOCAL.

**Latest 5 handoffs (S2000-S2099) embed check:**
- SESSION_2000 (48 chunks), SESSION_2001 (21), SESSION_2003 (23),
  SESSION_2004 (23), SESSION_2099 (28) — all embedded within
  cascade-close window

**S1304 finding re-attestation:**
- T1 (`build_docs_provenance` unscheduled) — STILL-VALID:
  `PeriodicTask.filter(task__icontains='provenance').count() == 0`
- T2 (`@lru_cache(maxsize=1)`) — STILL-VALID:
  `core/services/td_handlers_ops.py:78-79` verified
- T5 (`ingested_via` write-only) — STILL-VALID pending R1
- G5 (boundary unowned) — PARTIALLY-REMEDIATED via
  DOCUMENTATION_MANAGER in `core/employees/jobs.py:187`

### 20.2 D2100.9 hybrid metadata contract — candidate lists

Per D2100.9 RATIFIED at S2100 close. P1 delivers **candidate lists**;
P3 ratifies the final contract. Categorization per §5.1 fatal-if-
missing rule + parent §5.1 ROI-trim guidance.

**Candidate core-required set (global, fatal-if-missing for P1/P3
reasoning — 7 fields per Q13 SIGN STRENGTHEN 2026-07-04):**

| # | Field | Rationale | Populatable from |
|---|-------|-----------|------------------|
| 1 | `document_id` (UUID) | join back to `Document` row for any downstream reasoning; already in 51.8% chunks | schema-present in `metadata` JSONField (already written by `unknown` path) |
| 2 | `document_type` | doc-class dispatch (research artifact vs handoff vs topic doc); already in 51.8% chunks | schema-present at `Document.document_type` (join-recoverable) + partial `metadata` |
| 3 | `source_path` (file_path) | provenance + supersession reasoning + cite reconstruction | schema-present at `Document.file_path` (join-recoverable) |
| 4 | `lifecycle_status` (draft/active/canonical/superseded/deprecated) | authority framework filter | schema-present at `Document.status`; state machine TBD in P3 |
| 5 | `last_embedded_at` | freshness bound; Corpus Health Score dim #8 support. **Kept as explicit slot per Q13 SIGN STRENGTHEN** — operational signal ("when did embeddings reflect content") is NOT substituted by Document created/updated timestamps | derivable from chunk `created_at` today; explicit slot recommended once P2 hash-substrate lands |
| 6 | `chunking_version` | prevent stale-chunk retrieval after chunking-strategy migration | NEW slot required — P2 designs |
| 7 | `provenance_axis` (Q13 SIGN STRENGTHEN 2026-07-04 addition) | provenance/authority discriminator that P3 cannot safely re-infer downstream once mis-populated (e.g., a fixed-value diversification of `ingested_via` OR a repaired `source_type` that carries authority provenance: `research_artifact` / `runtime_inventory` / `narrative_anchor` / `handoff` / `topic_doc` / `spider_data`) | NEW semantic slot — P2 designs; P3 governance decides the value domain |

**Core-available (enforced-by-schema, not core-required per Q13
SIGN STRENGTHEN 2026-07-04):**

| Field | Note |
|-------|------|
| `embedding_model` | schema-present + 100% populated LOCAL; automatically enforced by write-site — no P3 contract needed to keep it; but downstream reasoning MAY consume it for model-drift detection when PROD lane introduces new models |

**Candidate doc-type profile (recommended per class):**

*Profile A: Research artifact (parent scoping / child audit /
canonical summary / topic doc)*
- `research_group` (int, e.g. `2100`)
- `session` (int, e.g. `2101`)
- `domain_slug` (str, e.g. `rag_document_loading`)
- `child_slot` (str, e.g. `P1_cat_a`)
- `canonical_summary` (bool)
- `head_commit` (str, at embed time)

*Profile B: Handoff*
- `session` (int)
- `handoff_target` (str: session_open / arc_close / etc.)
- `head_commit_before`, `head_commit_after` (str)

*Profile C: Topic doc / narrative anchor*
- `subsystem` (str)
- `superseded_by` / `supersedes` (UUID FK to `Document`)
- `canonical` (bool)

**Candidate derivable-at-ingest (schema-computable — 4 fields):**

| # | Field | Derivation |
|---|-------|------------|
| 1 | `canonical_summary` flag | filename pattern regex `NN99_.*_canonical_summary\.md` |
| 2 | `head_commit` at embed time | `git rev-parse HEAD` at cascade step 4 |
| 3 | `source_path` | already `Document.file_path` |
| 4 | `last_embedded_at` | already chunk `created_at` |

**Candidate aspirational (require frontmatter changes to every doc
— defer to future arc):**

| # | Field | Reason for deferral |
|---|-------|---------------------|
| 1 | `related_arcs` | requires every doc to have a `related:` frontmatter block; already present in research artifacts, absent in most `docs/` root docs |
| 2 | `T-slot / R-slot references` | research-artifact-specific; not applicable to topic docs or handoffs uniformly |
| 3 | `decisions_locked` | ADR-style; not present in most doc classes today |
| 4 | `implementation_status` | code-adjacent field; would require cross-doc-and-code linkage |
| 5 | `parent_doc` | research-artifact-specific; frontmatter has `companion_anchors:` but no formal parent pointer |

**Fatal-if-missing severity ladder (per §5.1 Q9 fold rule):**
- **(a) Fatal for P1/P3 reasoning** = the 6 core-required fields above
- **(b) Strongly recommended** = doc-type profile fields per class
- **(c) Derivable at ingest** = the 4 derivable fields (bring
  online at P2 pipeline changes)
- **(d) Aspirational for future governance layer** = the 5 aspirational

### 20.3 Field-level cross-reference — Chris's 18-field aspirational list

Per parent §5.1 point 6:

| # | Aspirational field | ROI classification | Placement in candidate lists |
|---|--------------------|--------------------|-------------------------------|
| 1 | `research_group` | schema-present-recommended | doc-type profile A |
| 2 | `session` | schema-present-recommended | profile A + B |
| 3 | `domain_slug` | schema-present-recommended | profile A |
| 4 | `category` (Q14 SIGN STRENGTHEN 2026-07-04) | **Distinct unless current schema truly unifies them** — `document_type` = class of artifact (research audit vs handoff vs topic doc); `category` = domain/topic taxonomy (e.g., `rag_document_loading` domain). Both `document_type` AND `category` exist as distinct Django fields on `Document` (§4.1). Collapsing loses a routing/authority axis. Recommendation: keep both. | schema-present at `Document.category`; recommended per doc-type profile A |
| 5 | `child_slot` | schema-present-recommended | profile A |
| 6 | `status` | fatal-if-missing (renamed `lifecycle_status`) | core-required |
| 7 | `head_commit` | derivable at ingest | derivable |
| 8 | `supersedes` / `superseded_by` | recommended per profile C | profile C |
| 9 | `canonical_summary` flag | derivable at ingest | derivable |
| 10 | `parent_doc` | aspirational | aspirational |
| 11 | `related arcs` (Q14 SIGN STRENGTHEN 2026-07-04) | **Derivable at ingest IF P3 mandates a frontmatter `related:` block** — parent scoping already carries `companion_anchors:` and `related:` frontmatter fields in research artifacts. If P3 elects to formalize the block as mandatory for research-artifact profile, this becomes **recommended + derivable-at-ingest** (once P3 enforces). If P3 does not mandate, remains aspirational. | contingent |
| 12 | `T-slot` / `R-slot` references | aspirational | aspirational |
| 13 | `decisions_locked` | aspirational | aspirational |
| 14 | `implementation_status` | aspirational | aspirational |
| 15 | `source path` | fatal-if-missing (renamed `source_path`) | core-required |
| 16 | `last_embedded_at` | fatal-if-missing | core-required |
| 17 | `content_hash` / `doc_hash` | derivable at ingest (per P2 design) | derivable (contingent on P2) |
| 18 | `embedding_model` | schema-present already (100% populated) | already present at `DocumentEmbedding.embedding_model` |

**ROI-trim summary:** 6 fields collapse into core-required; 5 land
in doc-type profiles; 4 are derivable at ingest; 5 are aspirational
for future. **Chris's 18-field list ROI-trims to 6 fatal + ~9
strongly-recommended + 4 derivable + 5 deferred.** No one-flat
18-field mandate; hybrid contract per D2100.9.

### 20.4 Companion anchors touched

- `docs/PLATFORM_INVENTORY.md` — runtime counts baseline (not
  modified)
- `docs/KNOWLEDGE_PIPELINE.md` — flow-map companion (not modified)
- `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md`
  — baseline for D2/D3/D5/D6 findings
- `core/services/td_handlers_ops.py:78` — verified `@lru_cache(1)`
  still live
- `core/employees/jobs.py:187` — verified `DOCUMENTATION_MANAGER`
  scope
- `core/tasks.py` `refresh_docs_corpus` — verified daily beat +
  hash-gated + embed-fanout
- `content/models.py` — schema field inventories per §4

### 20.5 Provenance chain

- **Parent scoping:** `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` (S2100 ratified 2026-07-04; §5.1 P1 scope + §7 anti-scope + §8 D-verdicts D2100.1a–.10)
- **Baseline inherit:** `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` (S1304 §14 D2/D3/D7/D8; §15 T1/T2/T5/T6/T7/T8)
- **Session context:** `docs/handoffs/SESSION_2099_EVENT_INTEGRATION_ARCHITECTURE_CANONICAL_SUMMARY.md`; `00-START-NEXT-SESSION.md` (S2101 P1 open)
- **Memory rules consulted:** `feedback_docs_pipeline_4_step_cascade`, `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, `feedback_rigby_sign_worker_instability_recovery`
- **HEAD at draft:** `053e5fc5` on `main`; branch `docs/session-2101-rag-corpus-state-audit` created at commit-time

### 20.6 Definitions used

- **Cascade:** the 4-command sequence `build_docs_index` →
  `build_rag_corpus` → `sync_docs_index_to_documents` →
  `embed_documents` (or `sync --embed`)
- **Reality:** files on disk under `docs/` + `CLAUDE.md` +
  `00-START-NEXT-SESSION.md`
- **Knowledge (in the R→R→K→B model):** the embedded + retrievable
  substrate — `Document` + `DocumentEmbedding` rows accessible via
  `search_docs` / `kb_tool`
- **Institutional knowledge layer** (parent §1 term of art): the
  Knowledge substrate + retrieval authority framework + freshness
  bounds + governance ownership — Group 2100 arc's central object of
  design
- **F1/F2 (F-CANDIDATE):** playbook §S1303 §14 finding-severity
  discipline — "orphan-write" or "dead-code" claim requires
  owner-model-qualified consumer inventory, not keyword grep, before
  promotion from CANDIDATE → CONFIRMED
- **KD-1..KD-6:** knowledge-debt category codes (§15.3)

### 20.7 Batch-discipline attestation (per Q4b SIGN fold pattern)

This audit ships as a single P1 doc + a single SIGN routing to Rigby.
Per S2099 Q4b batch-discipline attestation pattern + Q16 SIGN
STRENGTHEN 2026-07-04 (read-only attestation):

- **No parallel work touching shared state files during this session.**
- **No cascade run inside this session.** Full 4-step docs cascade +
  `build_docs_provenance` runs post-Chris-ratification per
  `feedback_docs_cascade_at_every_close` — landing on a single
  atomic commit + PR.
- **No `PLATFORM_INVENTORY.md` or `PLATFORM_WHAT_IT_IS.md` touch this
  session** (P1 delivers audit doc; anchor updates land in xx99 or
  as separate atomic PR per §7 anchor-update batch pattern).
- **§7 anchor-update batch scope from parent §5.5 remains as
  Group-2000+-residual + Group-2100-close-batch** (deferred to S2199
  or dedicated batch session).
- **Read-only evidence gathering only (Q16 SIGN STRENGTHEN
  2026-07-04):** no DB writes (all ORM queries were `.count()`,
  `.filter().count()`, `.values().annotate().order_by()`, or
  `.first()` — no `create()` / `update()` / `delete()` /
  `bulk_create()` / `bulk_update()`). No Celery task triggers
  fired (`refresh_docs_corpus` was inspected via
  `PeriodicTask.filter()` read-only). No beat-schedule edits. No
  config/env changes. No migrations run. No embedding backfills
  triggered. The audit sample is a pure read-only snapshot.

### 20.8 Rigby SIGN cycle 1 routing plan (per playbook §15)

Cycle 1 SIGN target on this draft. Routing per
`feedback_rigby_sign_worker_instability_recovery` pattern — batch
findings 3-4 per prompt for the 1000+-line audit to prevent pin
poisoning at Rigby's LLM boundary. Proposed 4-batch structure:

- **Batch 1 — §1-§4 (executive summary + domain purpose + entry
  points + models):** Q1 posture verdict; Q2 corpus-state one-sentence
  answer; Q3 `DocumentEmbedding` metadata population claim; Q4
  `source_type` monoculture finding
- **Batch 2 — §5-§10 (services + APIs + flows + ownership +
  integrations + events):** Q5 refresh_docs_corpus beat coverage; Q6
  ingest-path divergence causal hypothesis; Q7 event-flow absence;
  Q8 two-lane divergence handling
- **Batch 3 — §11-§17 (existing docs + coverage + maturity + drift +
  debt + boundaries + overlaps):** Q9 D1 template-file skip finding
  severity; Q10 S1304 re-attestation completeness; Q11 KD-1..KD-6
  taxonomy completeness; Q12 knowledge-debt classification framework
  boundaries
- **Batch 4 — §18-§20 (ownership gaps + future research + appendix):**
  Q13 §20.2 hybrid contract candidate list completeness; Q14 §20.3
  18-field ROI-trim; Q15 P2/P3/P4 handoff scoping; Q16 batch-
  discipline attestation

Cycle 2 only if cycle 1 verdict distribution surfaces FOLD/REJECT.
Otherwise cycle 1 STRENGTHEN folds land pre-commit + P1 status flips
`draft` → `active`.

### 20.8.1 SIGN cycle 1 — verdict distribution + fold record (executed 2026-07-04)

**Cycle 1 result: CLEAN — 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT
across 16 questions in 4 batches.**

| Batch | Range | Verdict distribution |
|-------|-------|----------------------|
| Batch 1 | §1–§4 (Q1–Q4) | 2 STRENGTHEN + 2 CLEAN |
| Batch 2 | §5–§10 (Q5–Q8) | 4 STRENGTHEN + 0 CLEAN |
| Batch 3 | §11–§17 (Q9–Q12) | 4 STRENGTHEN + 0 CLEAN |
| Batch 4 | §18–§20 (Q13–Q16) | 4 STRENGTHEN + 0 CLEAN |

**Folds landed pre-commit (all 14 STRENGTHEN):**

| Q | Fold summary | Section touched |
|---|--------------|-----------------|
| Q1 | State that 100% embed coverage can coexist with institutional-layer-not-met | §1 Executive Summary (added coverage-vs-retrieval-readiness paragraph) |
| Q2 | Add orphan-embedding + p50/p95/p99 chunk-distribution to gap matrix | §1 matrix (added rows 4'', 4''') |
| Q3 | (CLEAN — no fold; retained framing) | — |
| Q4 | Reframe F2 causal claim as working hypothesis + name confirmation criteria | §1 F2 finding text |
| Q5 | S1802 "protects" → "reduces persistence window"; call out timing gap | §5.2 |
| Q6 | Label §7.3 as working hypothesis + name confirmation method | §7.3 (added verification-status label) |
| Q7 | Qualify §10 cascade EventBus absence as non-exhaustive sweep | §10 |
| Q8 | Anchor architectural-intent claim to S1304 + observed counts; footnote S1108 as not-re-verified | §17.1 verdict |
| Q9 | Split D1 into D1a (LOW instance) + D1b (MEDIUM pattern) | §14 |
| Q10 | Enumerate S1304 findings NOT re-attested in P1 + rationale + downstream owner | §15.2.1 (new subsection) |
| Q11 | Add KD-7 mis-linked-embeddings; explicit-reject KD-8/KD-9 candidates | §15.3 |
| Q12 | Relabel "two metadata surfaces" → "two metadata planes" + clarify subset/coverage-mismatch | §17.3 |
| Q13 | Add 7th core-required field (provenance_axis discriminator); embedding_model as core-available; keep last_embedded_at explicit | §20.2 |
| Q14 | Flag category vs document_type as distinct; mark related_arcs as contingent-derivable | §20.3 (rows 4, 11) |
| Q15 | Add R4.4 conditional-elevation logic for freshness bounds; explicit mechanism-vs-governance boundary | §19.3 |
| Q16 | Add explicit read-only attestation (no DB writes, no beat edits, no cascade runs) | §20.7 |

**Batching-discipline attestation (per rigby_sign_worker_instability_recovery
rule):** 4 batches of 4 questions each held Rigby's LLM boundary
stable throughout. No pin poisoning observed. Turn count on arc pin
`pa-18b095bb7c4740be` remained well below rotation threshold. Cycle
completed in single session.

**§14 verifier-loop CODIFICATION-CONFIRMED discipline satisfied:**
pre-draft verifier-loop executed (see verifier_loop frontmatter);
Rigby SIGN cycle 1 executed pre-commit; STRENGTHEN folds landed
pre-commit; status flip contingent on Chris ratification per §20.10
close checklist.

### 20.9 D-verdict compliance (§8 parent D-verdicts applied to P1)

| Parent D-verdict | Applied to P1 | Compliance |
|-------------------|---------------|------------|
| D2100.1a — Group 2100 scope lock | P1 stays within RAG substrate; does not enter Group 1300 territory | COMPLIANT (§9 + §7 anti-scope) |
| D2100.1b — Knowledge Loop framing adoption | P1 uses R→R→K→B framing in §1 + §2 + §13 acceptance criteria | COMPLIANT |
| D2100.2 — 4-child taxonomy | P1 references P2/P3/P4 handoffs explicitly in §19 | COMPLIANT |
| D2100.3 — Arc pin `pa-18b095bb7c4740be` | P1 routes SIGN on this pin; frontmatter records | COMPLIANT (see §20.8) |
| D2100.4 — SIGN cycle 1 required | P1 SIGN routing planned per §20.8 | PENDING (routing planned; results land post-cycle) |
| D2100.5 — Design-preparation authority only | P1 ships no code, no schema, no beat changes | COMPLIANT |
| D2100.6 — Central lens question ownership | P1 §1 delivers P1-scope portion of the answer | COMPLIANT |
| D2100.7 — Hypothesis + Q12 conditional elevation | P1 leaves hypothesis intact; P4 tests | COMPLIANT |
| D2100.8 — 8-axis retrieval authority framework | P1 does NOT design (P3 territory); flags via §19.2 handoff | COMPLIANT |
| D2100.9 — Hybrid metadata contract | P1 delivers CANDIDATE LISTS per §5.3 + §20.2; P3 ratifies final | COMPLIANT (candidate lists shipped) |
| D2100.10 — RAG Corpus Health Score standing metric | DEFERRED to P4 per D2100.10; P1 provides §5.5-supporting counts | COMPLIANT |

### 20.10 Close checklist (per Research OS §14 completion contract)

- [ ] Rigby SIGN cycle 1 executed on arc pin `pa-18b095bb7c4740be`
- [ ] All STRENGTHEN folds landed pre-commit
- [ ] Chris ratification of D-verdicts (P1-scope) via close card
- [ ] Status flip `draft` → `active` in frontmatter
- [ ] Commit + PR on branch `docs/session-2101-rag-corpus-state-audit`
- [ ] Full 4-step docs cascade + `build_docs_provenance` run
      post-merge per `feedback_docs_cascade_at_every_close`
- [ ] Chunk-count evidence in PR body per
      `feedback_cascade_pr_must_include_embed_step`
- [ ] `OPEN_ARCS.md` row updated (Group 2100 progress)
- [ ] `ARCHITECTURE_INDEX.md` §1.NN S2101 registration + version bump
- [ ] `00-START-NEXT-SESSION.md` overwritten with S2102 open priorities
- [ ] Handoff `SESSION_2101_RAG_DOCUMENT_LOADING_CORPUS_STATE_AUDIT.md`
      written to `docs/handoffs/`

### 20.11 §10 meta-methodology note (per playbook §11.3 template)

Not required for child audit — §10 meta-methodology is xx99 canonical
summary discipline (S2199 will own). P1 executes playbook §11.2
child-audit shape; xx99 will consolidate P1-P4 meta-methodology at
arc close.

---
