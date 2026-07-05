# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2100 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2100 arc pin `pa-18b095bb7c4740be` is ACTIVE post-S2101 close 2026-07-04. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2100 arc (S2100 → S2101 → **S2102** → S2103 → S2104 → S2199) — playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (guardrails-retained-but-generalized per S2099 MC-4 extension).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2100 P1 CAT A CORPUS STATE AUDIT LANDED AT S2101; NEXT-SESSION = S2102 P2 INGESTION / CHUNKING / EMBEDDING PIPELINE AUDIT

**Group 2100 RAG / Document Loading (Knowledge Loop) arc: S2101 P1 Cat A Corpus State Reality→Knowledge Gap Audit CLOSED 2026-07-04 → next is S2102 P2 Ingestion / Chunking / Embedding Pipeline Audit** per parent scoping `2100_rag_document_loading_domain_scoping.md` §5.2.

- **Active arc pin:** `pa-18b095bb7c4740be` — preserved through S2102 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.
- **Arc progress:** S2100 parent scoping (shipped) → S2101 P1 (shipped this session) → **S2102 P2 (next)** → S2103 P3 Retrieval Authority Framework + Corpus Governance Design → S2104 P4 Behavior Substrate Structured Observation + Integration → S2199 xx99 canonical summary. Runtime target: 6 sessions on track.

## READ THIS THIRD — S2101 P1 SHIP STATE

**P1 audit doc:** `docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md` (~1521 lines post-fold; `status: active` post-Rigby-SIGN + post-Chris-ratification).

**SIGN cycle 1 result:** CLEAN with 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT across 16 Qs in 4 batches. All 14 STRENGTHEN folds landed pre-commit.

**Chris ratified 10 items via "agree all" 2026-07-04:**
1. F1 `source_type='api'` monoculture + S1304 D3 carry-forward
2. F2 metadata population asymmetry as working hypothesis (P2 discharges)
3. D1a/D1b silent-drop split (LOW instance / MEDIUM pattern)
4. KD-1..KD-7 knowledge-debt taxonomy
5. 7-field core-required metadata contract (added `provenance_axis` per Q13 SIGN)
6. 3 doc-type profiles (A research artifact / B handoff / C topic doc)
7. 4 derivable-at-ingest + 5 aspirational-deferred (Chris's 18-field ROI-trim)
8. Partial S1304 re-attestation + §15.2.1 explicit non-re-attest enumeration
9. R4.4 conditional-elevation logic for D2100.7 (N≥10 threshold; P4 tests)
10. draft→active + commit/PR + post-merge docs cascade + `build_docs_provenance`

**Headline P1 findings for P2 to build on:**
- LOCAL corpus materially complete but semantically thin. All 2908 Documents embedded (0 orphans, 51789 chunks, avg 17.81/doc, p50=11 p95=47 p99=169 max=443, 29 outliers > p99).
- Institutional-knowledge-layer acceptance criteria: 1/5 MET (embed coverage); 2-5 not evaluable from static snapshot.
- F1 `source_type='api'` monoculture — S1304 D3 consumer alive but discriminative axis lost at write time.
- F2 metadata population asymmetry — 48.2% chunks empty metadata (correlates to `ingested_via='sync_docs'` path).
- F3 build_docs_index silent-drop of 5 template files (D1a instance / D1b MEDIUM silent-drop-telemetry pattern).
- F4 `build_docs_provenance` unscheduled (S1304 T1 STILL-VALID; 0 periodic tasks match `provenance`).
- F5 Documentation Manager scope covers cascade execution/verification/escalation but NOT schema/retrieval semantics/authority framework.

## READ THIS FOURTH — S2102 P2 INGESTION / CHUNKING / EMBEDDING PIPELINE AUDIT SCOPE

Per parent scoping §5.2 + P1 handoff §19.1:

**Scope.** Audit the ingestion cascade end-to-end. `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents [--embed]` → `embed_documents`. Plus the two-lane structure (LOCAL keyword vs PROD pgvector) and chunking strategy analysis.

**Load-bearing questions:**
- Chunking / lanes / cadence — LOCAL fixed 1200-char vs PROD configurable semantic; two-lane synchronization contract enforced or aspirational?
- Embedding cadence + refresh triggers — what triggers re-embedding? Content-change detection? File mtime? Content hash? None?
- Embedding-model migration — what happens when `embedding_model` changes?
- Chunking version tagging — do chunks carry `chunking_version` metadata?
- Q3 (redistributed per W7) — How do we detect stale embeddings after docs change?
- Cascade mechanism — document flow as mechanism reference, not just command list; where does each step succeed silently / fail silently / log?
- Doc/content hashing substrate — what fields exist in schema today? What's required for automatic stale-detection?

**Handoffs P2 discharges from P1:**
- R2.1 — Publish `docs/topics/docs-ingestion-cascade.md` (S1304 T4)
- R2.2 — Two-lane chunking-strategy audit (10.66 vs 17.81 chunks/doc divergence)
- R2.3 — `content_hash` propagation to chunk-time (KD-2 detection substrate)
- R2.4 — `source_type` monoculture root-cause (audit `content/embeddings.py:45-63` `_derive_source_type`)
- R2.5 — Discharge S1399 §19 R1 for `ingested_via` (full-tree read-side sweep; wire consumer OR deprecate)
- R2.6 — Cascade EventBus emission design (cross-ref S2001 F3 SPIDER_DATA MISSING-producer)

**Delegated inheritance:**
- S1304 G3 `lru_cache(1)` staleness (T2 HIGH — STILL-VALID per S2101 §20.1)
- S1304 §14 D7 `ingested_via` orphan — write-site full-tree recheck
- S2001 F3 SPIDER_DATA WEAK consumer — spider-data → embedding path under-specification
- S2001 F9 dormant-consumer risk pattern — backfill beat dormancy check
- P1 KD-2 (stale-embed-post-content-change) — measurable only with P2 hash substrate

**Expected shape.** ~800-1100 lines. Ships: cascade flow diagram + lane-divergence matrix + chunking strategy tradeoff analysis + embedding cadence proposed design.

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### §7 anchor-update batch from S2099 (still queued as separate follow-up PR)

Per Q4b SIGN batch-discipline attestation at S2099 close + parent §5.5 handoff: the §7 anchor-update batch is queued as a single atomic follow-up PR — NOT bundled with S2101 close per parallel-safety scope discipline. Batch scope:

- 10 per-plane topic docs
- 1 index / overview doc
- `PLATFORM_INVENTORY.md` subsection
- `PLATFORM_WHAT_IT_IS.md` §7 update
- `EVENT_SYSTEM_INVENTORY.md` §13 with NEW §13.1.5 Fleet Events sidecar subtable
- `ARCHITECTURE_INDEX.md` v70 §1.73 (already registered at S2099 close)
- `CLAUDE.md` Detailed Breakdown row (Fleet Events)
- `OPEN_ARCS.md` Closed section

Owner: Group 2000+ residual (Claude next session or dedicated batch session). Not blocking S2102 P2 open but should land before S2199 to keep anchors current.

## SESSION READY CHECK (before opening S2102 P2)

Before writing the S2102 P2 audit:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local`
2. Verify arc pin ownership: Rigby returns `conversation_owner_match=true`
3. Read parent scoping doc `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` §5.2 + §7 anti-scope + §8 ratified D-verdicts
4. Read S2101 P1 audit at `docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md` §14 (Known Drift), §15 (Known Technical Debt), §19.1 (P2 handoffs R2.1-R2.6)
5. Verifier-loop pre-draft:
   - grep `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `embed_documents` command source; sample each cascade command's docstring + arg surface
   - grep `content/embeddings.py:45-63` `_derive_source_type` for `source_type` write-site derivation logic
   - grep all three `ingested_via=` write-sites: `sync_docs_index_to_documents.py:394`, `core/tasks_agents.py:4223/4290/4351`, `content/embeddings.py:654/753`
   - sample `refresh_docs_corpus` task body for cascade orchestration mechanism
   - measure chunking divergence: sample chunk sizes in `.rag/corpus.jsonl` vs `DocumentEmbedding.chunk_size`

**S2102 P2 open command (Chris short command):** `Start research group 2102` or `Continue research group 2100` — either invokes S2102 P2 Cat B Ingestion / Chunking / Embedding Pipeline Audit under Group 2100 arc pin `pa-18b095bb7c4740be`.
