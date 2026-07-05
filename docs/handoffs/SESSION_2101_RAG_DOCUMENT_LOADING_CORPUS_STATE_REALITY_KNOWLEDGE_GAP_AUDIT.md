---
session: 2101
status: closed (S2101 P1 Cat A Corpus State Reality→Knowledge Gap Audit CLOSED — FIRST child audit under Group 2100 RAG / Document Loading (Knowledge Loop) arc + NINTH-consecutive application of playbook §11.2 20-section child-audit template after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001; Rigby SIGN cycle 1 CLEAN with 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT across 16 questions in 4 batches (§1-§4 / §5-§10 / §11-§17 / §18-§20) with all 14 STRENGTHEN folds landed pre-commit on preserved arc pin `pa-18b095bb7c4740be`; Chris "agree all" 2026-07-04 on 10-item close card ratified all P1-scope items; ARCHITECTURE_INDEX v71 → v72 with §1.75 S2101 registration; OPEN_ARCS Group 2100 In-progress row updated with 5-step Reality→Knowledge gap matrix summary + KD-1..KD-7 knowledge-debt taxonomy + 7-field core-required metadata contract per D2100.9 hybrid contract shape; Runtime target 6 sessions on track — 2 of 6 shipped)
date: 2026-07-04
arc: Research Group 2100 (RAG / Document Loading — Knowledge Loop) — P1 Cat A Corpus State Reality→Knowledge Gap Audit child (FIRST of 4 children under Group 2100)
category: child_audit (playbook §11.2 20-section child-audit template NINTH-consecutive application; §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft; §15 required SIGN cycle 1 pre-commit executed CLEAN with 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT + 14 folds landed pre-commit; §16 arc-standard arc-pin preservation executed per playbook + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails)
head_commit_before: 053e5fc5006efddeaba34dfa08bdce5caaec3a36 (main; post-S2100 parent scoping + docs cascade merged)
head_commit_after: (this session's commit — pending)
authors: Claude Code (Chris directed via short command "start research group 2101" at S2101 open per Research OS §5 request-classification RESEARCH class §8.1 startup contract; interpretation: Chris opening S2101 P1 Cat A Corpus State Reality→Knowledge Gap Audit per parent §5.1 + 00-START-NEXT-SESSION.md §51 next-session priority; Rigby confirmed service_context: local + arc pin ownership pre-audit + arc pin health_check score=100)
---

# Session 2101 — Group 2100 Cat A — Corpus State: Reality→Knowledge Gap Audit

> **FIRST child audit in the Group 2100 RAG / Document Loading arc.**
> Delivered under NINTH Research OS arc. Playbook §11.2 20-section
> child-audit template NINTH-consecutive application. Rigby SIGN cycle
> 1 CLEAN with 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT. Chris
> "agree all" ratified 10 items across findings + KD taxonomy +
> metadata contract candidate lists + handoff scoping.

## What shipped

- **S2101 P1 audit doc:** `docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md` — 1521 lines post-fold. Playbook §11.2 20-section shape (§1 Executive Summary through §20 Appendix). Status `active` post-Chris ratification.
- **5-step Reality→Knowledge gap matrix:** on-disk 2,908 `.md` files under `docs/` (+ 2 root docs = 2,910 Reality baseline) → `docs/_index.json` 2,905 documents (−5 template files omitted, +2 root docs added) → `.rag/corpus.jsonl` 2,905 unique files / 30,974 chunks (avg 10.66/file) → `Document` table 2,908 rows (+3 vs index; roots + others) → `DocumentEmbedding` table 51,789 chunks (avg 17.81/doc; 0 orphans; chunk distribution p50=11, p95=47, p99=169, max=443 with 29 outliers > p99). **100% embed coverage LOCAL** (0 unembedded Documents).
- **`DocumentEmbedding` metadata inventory (Q8-a authoritative):** complete field-population audit surfaced 51.8% chunks carry `{document_id, document_type, document_title}` in JSONField `metadata`; 48.2% empty `metadata={}`. Split correlates exactly with `ingested_via` value (26,809 `unknown` / 24,980 `sync_docs` / 0 `backfill` LOCAL). `source_type='api'` monoculture (100% chunks). `embedding_model='openai_text_embedding_3_small'` unified (zero model-drift risk).
- **18-field ROI-trim table (§20.3):** Chris's aspirational 18-field list ROI-trimmed to: 7 core-required + ~9 recommended-per-doc-type-profile + 4 derivable-at-ingest + 5 aspirational-deferred. Per D2100.9 hybrid contract shape.
- **Core-required 7-field metadata contract candidate list (§20.2):** `document_id`, `document_type`, `source_path`, `lifecycle_status`, `last_embedded_at`, `chunking_version`, **`provenance_axis`** (Q13 SIGN STRENGTHEN addition — provenance/authority discriminator P3 cannot safely re-infer downstream once mis-populated).
- **3 doc-type profiles:** Profile A (Research artifact: research_group / session / domain_slug / child_slot / canonical_summary / head_commit) + Profile B (Handoff: session / handoff_target / head_commit_before / head_commit_after) + Profile C (Topic doc: subsystem / superseded_by / supersedes / canonical).
- **Core-available (enforced-by-schema, not core-required):** `embedding_model` — schema-present + 100% populated LOCAL; automatically enforced by write-site; downstream MAY consume for model-drift detection.
- **KD-1..KD-7 knowledge-debt classification framework (§15.3):** 7 durable categories (KD-1 unembedded-on-disk / KD-2 stale-embed-post-content-change / KD-3 cascade-PR-forgot-embed-step / KD-4 metadata-blank-at-ingest / KD-5 provenance-index-stale / KD-6 orphan-Document-row-post-file-move / KD-7 mis-linked-embeddings from Q11 SIGN STRENGTHEN). LOCAL observed: KD-1=0, KD-3=0 currently (S1802 historical), KD-4=24,980 chunks (48.2%), KD-5=indeterminate, KD-6=0, KD-7=0 detected (coarse; fine-grained deferred). Explicit-reject list: KD-8 chunking-strategy-drift (P2 concern) / KD-9 retrieval-filter-drift (P3 concern) / KD-10 governance-debt (post-P3 lifecycle contract).
- **5 headline findings (all draft-scoped, Chris ratified):**
  - **F1** `source_type='api'` monoculture despite live consumer at `content/embeddings.py:965-973` — S1304 D3 consumer alive but discriminative axis lost at write time
  - **F2** metadata population asymmetry between ingest paths — WORKING HYPOTHESIS pending P2 code-path verification (Q4 + Q6 SIGN STRENGTHEN)
  - **F3 → D1a + D1b** split (Q9 SIGN STRENGTHEN): D1a LOW instance (5 spokesperson-corpus templates skipped) + D1b MEDIUM generalizable silent-drop-telemetry gap pattern
  - **F4** provenance-index rebuild cadence unmanaged — S1304 T1 STILL-VALID (0 periodic tasks match `provenance`); `build_docs_provenance` manual-only
  - **F5** Documentation Manager scope covers cascade execution/verification/escalation but NOT schema/retrieval semantics/authority framework — S1304 G5 PARTIALLY-REMEDIATED
- **S1304 finding re-attestation (§20.1 + §15.2.1):** T1 STILL-VALID, T2 STILL-VALID (`@lru_cache(maxsize=1)` at `core/services/td_handlers_ops.py:78-79`), T5 STILL-VALID pending R1, G5 PARTIALLY-REMEDIATED. §15.2.1 explicit non-re-attest enumeration per Q10 SIGN STRENGTHEN (S1304 D3/D8/T3/T6 partially covered + non-re-attest with rationale + downstream owner).
- **Institutional-knowledge-layer acceptance criteria scoring (§13):** 1/5 MET (criterion 1 embed coverage); 2-5 not evaluable from static snapshot (P3 designs framework, P4 observes).
- **P2/P3/P4 handoff scoping (§19):** 6 items to P2 (R2.1-R2.6) + 5 items to P3 (R3.1-R3.5) + 4 items to P4 (R4.1-R4.4 including R4.4 conditional-elevation logic for D2100.7 per Q15 SIGN STRENGTHEN) + 2 items to non-Group-2100 arcs (Group 1700 Observability + Documentation / Research Knowledge System §3.15).
- **Batch-discipline attestation (§20.7 + Q16 SIGN STRENGTHEN):** read-only evidence gathering only — no DB writes, no Celery task triggers, no beat edits, no config/env changes, no migrations run, no embedding backfills triggered.
- **Docs cascade artifacts refreshed post-S2100 close** (verified in verifier-loop pre-draft — `docs/_index.json` + `.rag/corpus.jsonl` mtimes 2026-07-04 20:19).
- **OPEN_ARCS Group 2100 In-progress row** updated with S2101 P1 progress + all headline findings summarized.
- **ARCHITECTURE_INDEX.md v71 → v72** with §1.75 S2101 registration + all 10 ratified items enumerated in preamble.
- **00-START-NEXT-SESSION.md overwritten** pointing at S2102 P2 Ingestion / Chunking / Embedding Pipeline Audit as next-session priority per parent §5.2.

## Rigby SIGN cycle 1 record

**Cycle 1 result: CLEAN — 14 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT across 16 questions in 4 batches.**

| Batch | Range | Distribution |
|-------|-------|--------------|
| Batch 1 | §1-§4 (Q1-Q4) | 2 STRENGTHEN + 2 CLEAN |
| Batch 2 | §5-§10 (Q5-Q8) | 4 STRENGTHEN + 0 CLEAN |
| Batch 3 | §11-§17 (Q9-Q12) | 4 STRENGTHEN + 0 CLEAN |
| Batch 4 | §18-§20 (Q13-Q16) | 4 STRENGTHEN + 0 CLEAN |

All 14 STRENGTHEN folds landed pre-commit. Cycle 2 NOT required. Batching-discipline per `feedback_rigby_sign_worker_instability_recovery` held stable across pin turn count — no pin poisoning observed. Full fold-record in doc §20.8.1.

**Batching pattern followed:** 4 batches of 4 questions each (per rigby-sign-worker-instability-recovery rule for 1000+ line audits). All batches text-only response (no tool invocations per prompt directive).

## Chris ratification (10-item close card, "agree all" 2026-07-04)

Per triage-decision-card pattern:

| # | Item | Disposition |
|---|------|-------------|
| 1 | F1 source_type monoculture + S1304 D3 carry-forward | RATIFY |
| 2 | F2 metadata asymmetry as working hypothesis pending P2 code-path verification | RATIFY |
| 3 | D1a/D1b silent-drop split (LOW instance / MEDIUM pattern) | RATIFY |
| 4 | KD-1..KD-7 knowledge-debt taxonomy | RATIFY |
| 5 | 7-field core-required metadata contract (added `provenance_axis` per Q13 SIGN) | RATIFY |
| 6 | 3 doc-type profiles (A research artifact / B handoff / C topic doc) | RATIFY |
| 7 | 4 derivable + 5 aspirational-deferred lists (Chris 18-field ROI-trim) | RATIFY |
| 8 | Partial S1304 re-attestation + §15.2.1 non-re-attest enumeration | RATIFY |
| 9 | R4.4 conditional-elevation logic for D2100.7 (N≥10 threshold; P4 tests) | RATIFY |
| 10 | draft→active + commit/PR + post-merge docs cascade + `build_docs_provenance` | RATIFY |

## Key evidence

**Verifier-loop pre-draft (single-transaction, HEAD 053e5fc5):**
- `Document.objects.count()` = 2,908; `DocumentEmbedding.objects.count()` = 51,789
- Documents with 0 embeddings = 0 (100% coverage LOCAL)
- `find docs -type f -name '*.md' | wc -l` = 2,908
- `docs/_index.json` documents array = 2,905 (5 template files omitted, 2 root docs added)
- `.rag/corpus.jsonl` = 30,974 chunks / 2,905 unique files (avg 10.66/file)
- `DocumentEmbedding.source_type` distribution: `api` = 51,789 (100%)
- `DocumentEmbedding.ingested_via` distribution: `unknown` = 26,809 (51.8%); `sync_docs` = 24,980 (48.2%); `backfill` = 0
- `DocumentEmbedding.embedding_model` = `openai_text_embedding_3_small` (100%)
- Chunk distribution per Document: min 1, p50 11, avg 17.81, p95 47, p99 169, max 443
- Orphan embeddings (FK-null) = 0
- 15 critical artifacts embedded (S2100 parent 97 chunks, all 8 xx99 canonicals 145-227 chunks, ARCHITECTURE_INDEX 443, RESEARCH_OPERATING_SYSTEM 254, OPEN_ARCS 27, CLAUDE.md 20, DOMAIN_RESEARCH_PLAYBOOK 134, S1304 boundary audit 105)
- Latest 5 handoffs (S2000-S2099) all embedded (21-48 chunks each) within cascade-close window
- S1304 T1 re-attest: `PeriodicTask.filter(task__icontains='provenance').count() == 0` — STILL-VALID
- S1304 T2 re-attest: `@lru_cache(maxsize=1)` at `core/services/td_handlers_ops.py:78-79` — STILL-VALID
- S1304 G5 re-attest: `DOCUMENTATION_MANAGER` at `core/employees/jobs.py:187` covers cascade execution/verification/escalation only (schema/retrieval/authority UNOWNED) — PARTIALLY-REMEDIATED
- `refresh_docs_corpus` beat: `PeriodicTask name=refresh-docs-corpus-daily enabled=True schedule=(4 0 * * *) America/Denver` — hash-gated + secondary unembedded-count trigger + embed-fanout wired

## Handoffs

**P2 (S2102) discharges from P1 (§19.1):**
- R2.1 — Publish `docs/topics/docs-ingestion-cascade.md` (S1304 T4)
- R2.2 — Two-lane chunking-strategy audit (10.66 vs 17.81 chunks/doc divergence intent vs drift)
- R2.3 — `content_hash` propagation to chunk-time (KD-2 detection substrate design)
- R2.4 — `source_type` monoculture root-cause audit (`content/embeddings.py:45-63` `_derive_source_type`)
- R2.5 — Discharge S1399 §19 R1 for `ingested_via` (full-tree read-side sweep; wire consumer OR deprecate)
- R2.6 — Cascade EventBus emission design (cross-ref S2001 F3 SPIDER_DATA MISSING-producer)

**P3 (S2103) inherits from P1 (§19.2):**
- R3.1 — Populate D2100.9 hybrid metadata contract (ratify core-required + doc-type profile lists; design enforcement)
- R3.2 — Retrieval authority framework design (8-axis per parent §5.3 + Q7 SIGN fold)
- R3.3 — Ownership assignments (§18 currently-UNASSIGNED axes)
- R3.4 — Cascade governance first-class doc (replaces informal MEMORY.md rules)
- R3.5 — Provenance-index rebuild scheduling (S1304 T1 remediation)

**P4 (S2104) inherits from P1 (§19.3):**
- R4.1 — Knowledge-debt category incidence classification in observation window (KD-1..KD-7)
- R4.2 — Institutional-knowledge-layer acceptance criteria observation (criteria 2, 3, 5)
- R4.3 — Corpus Health Score N-observation-based calibration
- R4.4 — D2100.7 conditional-elevation logic execution (N ≥ 10 case threshold for freshness-bounds-SIGN-quality hypothesis)

**Non-Group-2100 arcs (§19.4):**
- Group 1700 Observability delegated — S1304 T6 filter-counter operator surface (logger.warning + Prometheus + Grafana)
- Documentation / Research Knowledge System (§3.15 not-yet-arc) — MEMORY.md-rules-vs-canonical-doc consolidation

## Anchor updates in this session

- `docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md` — NEW file (1521 lines)
- `docs/research/ARCHITECTURE_INDEX.md` — v71 → v72 with §1.75 S2101 registration
- `docs/research/OPEN_ARCS.md` — Group 2100 In-progress row updated with S2101 P1 progress summary
- `00-START-NEXT-SESSION.md` — overwritten with S2102 P2 open priorities
- `docs/handoffs/SESSION_2101_...md` — this handoff

## Anchor deferrals from this session

- `docs/PLATFORM_WHAT_IT_IS.md` — no touch (P1 does not add narrative-anchor content; xx99 will)
- `docs/PLATFORM_INVENTORY.md` — no touch (P1 delivers audit only; inventory subsection lands at xx99)
- `docs/topics/*.md` — no touch (P2 delivers `docs-ingestion-cascade.md`; R2.1)
- `docs/CLAUDE.md` — no touch this session (no new subsystem row to add for P1 audit)
- `MEMORY.md` — no touch this session (no new project-state / feedback rule / reference emerged from P1)
- **§7 anchor-update batch from S2099 remains queued** as separate follow-up PR per Q4b batch-discipline attestation (NOT bundled with S2101 close per parallel-safety scope discipline). Owner: Group 2000+ residual.

## Post-close mechanical actions (Claude executes)

- [x] Fold all 14 STRENGTHEN edits into P1 audit doc pre-commit
- [x] Flip P1 audit `status: draft` → `active` post-Chris-ratification
- [x] Update `ARCHITECTURE_INDEX.md` (v71 → v72 with §1.75 S2101 registration)
- [x] Update `OPEN_ARCS.md` Group 2100 In-progress row
- [x] Overwrite `00-START-NEXT-SESSION.md` pointing at S2102 P2
- [x] Write this handoff
- [ ] Commit + PR on branch `docs/session-2101-rag-corpus-state-audit`
- [ ] Post-merge: run full 4-step docs cascade + `build_docs_provenance` per `feedback_docs_cascade_at_every_close`
- [ ] Include chunk-count evidence in PR body per `feedback_cascade_pr_must_include_embed_step`

## Runtime status at close

**Group 2100 arc progress:** 2 of 6 sessions shipped (S2100 parent scoping + S2101 P1). Runtime target 6 sessions on track. Arc pin `pa-18b095bb7c4740be` preserved through S2101 per playbook §16 arc-standard + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.

**Rigby SIGN pin surface:** Group 2100 arc pin health_check score=100 recommendation=continue at close (turn count well below rotation threshold).

**Playbook §11.2 20-section child-audit template application count:** 9 (S1301 first + S1401 + S1501 + S1601 + S1701 + S1801 + S1901 + S2001 + S2101 ninth). Discipline pattern MC-1 CODIFICATION-CONFIRMED at S1899 close preserved.

**MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails applied:** arc-pin preservation through S2101 per playbook §16 arc-standard behavior + S1999 close established rule.

**Handoff numbering continuity:** SESSION_2100 (parent scoping) → SESSION_2101 (this session) → next SESSION_2102 (P2).
