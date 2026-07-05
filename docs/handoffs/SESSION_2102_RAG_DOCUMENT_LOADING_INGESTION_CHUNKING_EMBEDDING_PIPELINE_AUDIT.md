---
session: 2102
status: closed (S2102 P2 Ingestion / Chunking / Embedding Pipeline Audit CLOSED — SECOND child audit under Group 2100 RAG / Document Loading (Knowledge Loop) arc + TENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001/S2101; Rigby SIGN cycle 1 CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT across 4 batches (Q1-Q5 §1/§3/§7/§7.3/§9 + Q6-Q10 §10/§13/F1/F2/F3 + Q11-Q15 F4/F5/F6/F7/F8 + Q16-Q20 §15/§17/§19/§20); all 20 STRENGTHEN folds landed pre-commit on preserved arc pin `pa-18b095bb7c4740be`; Cycle 2 NOT required per Rigby explicit closure; Chris "agree all" 2026-07-04 on 10-item close card ratified all P2-scope items; ARCHITECTURE_INDEX v72 → v73 with §1.76 S2102 registration + §1.75 S2101 backfill row; OPEN_ARCS Group 2100 In-progress row updated with 8-finding F1-F8 summary + ORM verifier-loop 51,952 chunks distribution + §15 T-table +2 HIGH + 3 MEDIUM + 1 LOW addition summary + T11-into-T10' merge; Runtime target 6 sessions on track — 3 of 6 shipped)
date: 2026-07-04
arc: Research Group 2100 (RAG / Document Loading — Knowledge Loop) — P2 Ingestion / Chunking / Embedding Pipeline Audit child (SECOND of 4 children under Group 2100)
category: child_audit (playbook §11.2 20-section child-audit template TENTH-consecutive application; §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft; §15 required SIGN cycle 1 pre-commit executed CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT + 20 folds landed pre-commit; §16 arc-standard arc-pin preservation executed per playbook + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails; §13 six-parallel-Explore sub-agent pattern applied — 5 Explore sub-agents fired for cascade command source archaeology)
head_commit_before: 7c84ff654d7c6349c0ad33b9f52767e78d162e4c (main; post-S2101 close + docs cascade merged)
head_commit_after: (this session's commit — pending)
authors: Claude Code (Chris directed via short command "start research group 2102" at S2102 open per Research OS §5 request-classification RESEARCH class §8.1 startup contract; interpretation: Chris opening S2102 P2 Ingestion / Chunking / Embedding Pipeline Audit per parent §5.2 + 00-START-NEXT-SESSION.md §51 next-session priority; Rigby confirmed service_context: local + arc pin ownership pre-audit via session_tool.list_recent showing pa-18b095bb7c4740be under donkeyking with S2101 close reference)
---

# Session 2102 — Group 2100 P2 — Ingestion / Chunking / Embedding Pipeline Audit

> **SECOND child audit in the Group 2100 RAG / Document Loading arc.**
> Delivered under NINTH Research OS arc. Playbook §11.2 20-section
> child-audit template TENTH-consecutive application. Rigby SIGN cycle
> 1 CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT. Chris
> "agree all" ratified 10 items across findings + severity splits +
> reclassifications + T-table additions + handoff triage.

## What shipped

- **S2102 P2 audit doc:** `docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md` — 1,795 lines post-fold. Playbook §11.2 20-section shape (§1 Executive Summary through §20 Appendix). Status `active` post-Chris ratification.
- **8 findings F1-F8 shipped:**
  - **F1 three-chunker regime** (MEDIUM-now / HIGH-blocker-for-P3 per Q8 SIGN split) — extends parent §5.2 two-lane framing to three physical chunkers: Chunker A `build_rag_corpus.chunk_text` (line 49-54) fixed 1200-char no-overlap → LOCAL `.rag/corpus.jsonl`; Chunker B `sync_docs_index_to_documents.chunk_content` (line 408-434) 1000+200 paragraph-sentence → DocumentEmbedding `ingested_via='sync_docs'`; Chunker C `content/embeddings.TextSplitter` (line 395-512) 1000+200 semantic → DocumentEmbedding `ingested_via='unknown'`.
  - **F2 overlap-metadata data lie** (MEDIUM+/HIGH per Q9 SIGN) — 24,980 sync_docs chunks overlap semantically via `chunk_content` line 432 `start = end - overlap` but `DocumentEmbedding.overlap_size` is never passed at create-time → defaults 0. Data-integrity defect surfaces as **D2100.11 candidate** for Chris D-verdict at close (retrofill decision OPEN).
  - **F3 dual-cascade paths HIGH** — Path A `refresh_docs_corpus` scheduled `crontab(hour=4, minute=0)` Denver time via `core/celery.py:495-499` with hash-delta gate + per-doc embed fan-out + NO OpsRun + NO escalation Deliverable; Path B `rigby_documentation_manager_daily` → `docs_cascade.py` MissionRunner 4-step orchestrator with subprocess/timeout + drift observation + escalation Deliverable — UNSCHEDULED (no beat entry). Recommended lean **option (b) fold A into B** per Q10 SIGN.
  - **F4 build_rag_corpus on_warning never wired** (MEDIUM per Q11 SIGN) — `iter_corpus_rows(on_warning=None)` supports drop-count telemetry but `refresh_docs_corpus` calls without wiring callback → step 2 silent drops produce zero signal. Extends S2101 D1b silent-drop telemetry gap generalization to STEP 2. Risk-class label + why-not-HIGH note + promote-to-HIGH trigger added per Q11.
  - **F5-partial `source_type='api'` — derivation function ACQUITTED, upstream Document.source trace UNRESOLVED** (S2101 F1 PARTIAL REFINEMENT per Q12 SIGN) — `_derive_source_type` at `content/embeddings.py:45-63` defaults to `'unknown'` NOT `'api'`. The 100% `api` value = 100% Documents have `source='api'` (branch 4). Upstream write-site trace is U1 (deferred).
  - **F6 backfill dormancy LOW / incomplete-wiring category** (S2101 D5 reclassified per Q13 SIGN + over-claim admission per Q20) — `embed_agent_activity` task has NO beat entry ANYWHERE (LOCAL vs PROD not the discriminator, scheduling absence is). Three internal-content backfill write-sites at `core/tasks_agents.py:4223/4290/4351` never fire. NOT drift NOT design-intent — INCOMPLETE WIRING. P3 governance decision to (a) de-scope OR (b) schedule.
  - **F7 EventBus MISSING** (MEDIUM current harm / HIGH criticality-as-enabler per Q14 SIGN) — grep for `event_bus.publish` in both cascade paths returns zero. Cross-refs S2001 F3 SPIDER_DATA MISSING-producer pattern architecturally. Two-layer emission candidate = coarse EventBus milestones (`docs_cascade.completed`, `_failed`, `.drift_detected`) + detailed OpsRunEvent step-level + rate-limited alert-class events (`silent_drop`, `chunker_regime_change`) per Q6 SIGN.
  - **F8 step-4 timeout derivative/contingent on F3 option choice** (MEDIUM per Q15 SIGN) — Path B `docs_cascade.step_4_embed()` at line 370-377 uses `subprocess.run(timeout=1800s)` + soft warning at 600s; Path A `refresh_docs_corpus` per-doc fan-out has no aggregate wall-clock cap. Auto-resolves under F3 option (a) or (b); persists under (d) explicit dual-path.
- **ORM verifier-loop 2026-07-04 at HEAD `7c84ff65`** LOCAL Postgres:
  - `DocumentEmbedding.objects.count()` = 51,952 (+163 vs S2101 baseline 51,789 — 1 daily beat fire since S2101 close)
  - chunk_size: mean=826.4, median=889, min=0, max=30,152, stdev=263.7; p10=552, p50=889, p90=993, p95=1000, p99=1125
  - chunks-per-doc: mean=17.85, median=11, p50=11, p90=33, p95=47, p99=169, max=443 (matches S2101 shape within 0.2%)
  - chunk_size by ingested_via: `unknown` n=26,972 mean=804.6 + `sync_docs` n=24,980 mean=849.9 + `backfill` n=0
  - overlap_size distribution: 26,072 with 0 (24,980 sync_docs + 1,092 first-chunks async) + 25,880 with 200 (async middle/tail) — perfect ingested_via-plus-chunk_index split explains chunker-provenance regime
- **§15 T-table net additions:** +2 HIGH (T13 dual-cascade + T16 KD-2 substrate) + 3 MEDIUM (T12 overlap-metadata + T14 on_warning + T15 embed telemetry) + 1 LOW (T17 backfill enum honesty); T11 chunker_id merged into T10 renamed to T10' "Contract fields + population discipline" per Q16 SIGN fold to prevent T-table bloat.

## Rigby SIGN cycle 1 result

**CLEAN — 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT across 4 batches on preserved arc pin `pa-18b095bb7c4740be`.**

- **Batch 1 (Q1-Q5, §1/§3/§7/§7.3/§9)** — 5 STRENGTHEN — ranking rubric split + exhaustiveness method line + Path B OpsRun.status transitions + near-isomorphism-not-duplication rename + Path A OVERCOUPLED/MIS-BOUND reclassify
- **Batch 2 (Q6-Q10, §10/§13/F1/F2/F3)** — 5 STRENGTHEN — two-layer event architecture + PARTIAL vs WORKING tipping rule + F1 MEDIUM-now/HIGH-blocker-for-P3 + F2 MEDIUM+/HIGH data-integrity + F3 recommended lean option (b) or (a)
- **Batch 3 (Q11-Q15, F4/F5/F6/F7/F8)** — 5 STRENGTHEN — F4 risk-class + F5 re-scope to partial-discharge + F6 incomplete-wiring category + F7 HIGH-criticality-as-enabler + F8 derivative/contingent-on-F3
- **Batch 4 (Q16-Q20, §15/§17/§19/§20)** — 5 STRENGTHEN — T11-into-T10' merge + §17 primary/secondary rename + P3 triage list + §19.2 P4 measurement bundle + R4.5 conditional branch + U6 LOCAL↔PROD comparability + F6 over-claim admission

**Cycle 2 NOT required** per Rigby explicit closure statement: "Cycle 2 not required if you make those admissions explicit."

All 20 STRENGTHEN folds landed pre-commit — §20.6 verifier-loop corrections section documents section-by-section fold summary.

## Chris ratification 2026-07-04

10-item close card ratified via "agree all":

1. F1 three-chunker regime + severity split MEDIUM-now / HIGH-blocker-for-P3
2. F2 overlap-metadata data lie — **D2100.11 candidate** surfaced as Chris D-verdict at close; retrofill choice (a) forward-fix only vs (b) forward-fix + retrofill remains OPEN
3. F3 dual-cascade paths HIGH + recommended lean (b) fold A into B; (c) retire B UNLIKELY (contradicts S1252/S1253 intent)
4. F4 build_rag_corpus on_warning MEDIUM + risk-class label + promote-to-HIGH trigger
5. F5-partial derivation acquitted / upstream Document.source unresolved (U1)
6. F6 backfill dormancy LOW / incomplete-wiring category (NOT drift, NOT design-intent) + over-claim admission
7. F7 EventBus MISSING dual-severity MEDIUM current-harm / HIGH criticality-as-enabler
8. F8 step-4 timeout derivative/contingent on F3 option choice
9. §15 T-table +2 HIGH + 3 MEDIUM + 1 LOW + T11-into-T10' merge as "Contract fields + population discipline"
10. Draft → Active + commit + PR + full 4-step docs cascade + `build_docs_provenance` per `feedback_docs_cascade_at_every_close`

## What's on the arc-close path (next-session priority)

**S2103 P3 Retrieval Authority FRAMEWORK + Corpus Governance Design** per parent scoping §5.3. 8 R3.x handoffs from S2102 with triage list per Q18 SIGN:

- **P3.1 must-ship** — R3.5 dual-cascade resolution (F3 discharge; sets canonical path constraining every other P3 handoff)
- **P3.2 must-ship** — R3.2 D2100.9 hybrid metadata contract chunker fields (depends on P3.1 canonical-path decision)
- **P3.3 must-ship** — R3.3 owner assignments (blocks all execution)
- **P3.x backlog** (Chris may split into P3a/P3b or defer to post-arc): R3.1 topic doc, R3.4 governance canonical doc, R3.6 backfill activation criteria, R3.7 chunker consolidation design, R3.8 provenance-index scheduling decision

**D2100.11 (F2 retrofill decision)** — CANDIDATE surfaced at S2102 close but decision (a) forward-fix only vs (b) forward-fix + retrofill remains OPEN. May land at P3 governance-decision OR as separate follow-up execution PR, whichever ships first.

## Arc progress

- S2100 parent scoping ✅ shipped
- S2101 P1 Corpus State Reality→Knowledge Gap Audit ✅ shipped
- **S2102 P2 Ingestion / Chunking / Embedding Pipeline Audit ✅ shipped this session**
- S2103 P3 Retrieval Authority Framework + Governance — next
- S2104 P4 Behavior Substrate + Integration
- S2199 xx99 Canonical Summary

Runtime target 6 sessions on track — **3 of 6 shipped**. Runtime cap 8 sessions never invoked (matches Group 1900 S1999 pattern + Group 2000+ S2099 pattern).

## Verifier-loop discipline

- **§14 verifier-loop pre-draft** per playbook: 5 grep/sample tasks executed per START-NEXT §51 step 5 — 4 cascade command source samples (build_docs_index 1112 lines + build_rag_corpus 178 lines + sync_docs_index_to_documents 434 lines + embed_documents 70 lines + content/embeddings.py 1106 lines) + `_derive_source_type` full read + 3 ingested_via write-sites + `refresh_docs_corpus` task body + `docs_cascade.py` MissionRunner + ORM chunk_size/overlap_size distribution.
- **§13 six-parallel-Explore** applied — 5 Explore sub-agents fired (Explore 1 build_docs_index STEP 1 archaeology + Explore 2 build_rag_corpus STEP 2 + Explore 3 sync_docs_index_to_documents STEP 3 + Explore 4 embed_documents STEP 4 + content/embeddings.py + Explore 5 backfill write-sites + refresh_docs_corpus + docs_cascade.py + beat schedule inventory). Sixth Explore slot used for ORM/data sampling by parent-Claude.
- **Third-chunker discovery** — parent §5.2 framed "two-lane LOCAL vs PROD"; Explore 3 revealed `sync_docs_index_to_documents.chunk_content` is a THIRD physical chunker distinct from `content/embeddings.TextSplitter`. Not caught by parent scoping's grep sweep; caught by parent-Claude read of Explore 3 output + follow-up single-file confirmation Read of lines 408-434.

## Meta-methodology capture

- **Playbook §11.2 20-section child-audit template** — TENTH-consecutive application (after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101). MC-5 CODIFICATION-CONFIRMED milestone extended 18 → 19 (from S2099 close baseline).
- **Playbook §16 arc-pin preservation** — SECOND-consecutive within Group 2100 arc (after S2101). MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close continues to hold through S2102.
- **Rigby SIGN batching discipline** — 4 batches × 5 Qs each = 20 Qs; per `feedback_rigby_sign_worker_instability_recovery` (large-audit batch cap 3-4 findings per prompt) held with 5-per-batch shape. No worker instability observed on 1,497-line audit doc. Zero jam-mid-batch.
- **Rigby SIGN 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT** — highest STRENGTHEN density in Group 2100 arc (S2101 was 14 STRENGTHEN + 2 CLEAN across 16 Qs; S2102 is 20 STRENGTHEN across 20 Qs). Ratio reflects more compound-severity + reclassification findings (F1 severity split, F2 severity elevation + Chris D-verdict surface, F5 partial-discharge, F6 category reclassification + over-claim admission, F7 dual-severity, F8 derivative/contingent).
- **Third-chunker discovery pattern** — parent scoping doc framing can under-count physical implementations at the level below the framing abstraction. Two-lane framing (LOCAL vs PROD) was correct at its abstraction; three-chunker regime is a substrate-level refinement. Discovery relied on Explore sub-agent output + parent-Claude cross-file confirmation. **Candidate for playbook v3 §14 verifier-loop enhancement** — pre-draft verifier-loop should include explicit "count physical implementations at one level below parent framing" step.
- **Over-claim admission pattern** (Q20 SIGN + Q13 SIGN interaction) — reclassifying a finding from "drift" to "design intent" without explicit product decision can BE a new form of drift (charitable interpretation replacing hard verdict). Explicit over-claim admission line preserves the honest observation while flagging the risk. **Candidate for xx99 §10 methodology capture** at S2199.

## Cascade discipline per `feedback_docs_cascade_at_every_close`

Per Chris directive S1399 close + reinforced at S1802 close:

1. `python manage.py build_docs_index` — regenerate `docs/_index.json`
2. `python manage.py build_rag_corpus` — regenerate `.rag/corpus.jsonl`
3. `python manage.py sync_docs_index_to_documents` — sync to Document table
4. `python manage.py sync_docs_index_to_documents --embed` OR `python manage.py embed_documents --all-unembedded` — embed unembedded rows
5. `python manage.py build_docs_provenance` — regenerate `docs/_provenance.json`

Chunk count from cascade must appear in commit body per `feedback_cascade_pr_must_include_embed_step`.

## Arc pin status

`pa-18b095bb7c4740be` — Group 2100 arc pin preserved through S2102. Continues through S2103 P3 → S2104 P4 → S2199 xx99 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (extended at S2099 close as guardrails-retained-but-generalized).

Turn count at close: 21 exchanges (up from 17 at S2102 open + 4 SIGN batches). Health-check score expected at close: monitor for turn-2 stall pattern per `feedback_rigby_sign_worker_instability_recovery`.

## Files added

- `docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md` (1,795 lines post-fold)
- `docs/handoffs/SESSION_2102_RAG_DOCUMENT_LOADING_INGESTION_CHUNKING_EMBEDDING_PIPELINE_AUDIT.md` (this file)

## Files modified

- `docs/research/OPEN_ARCS.md` — `last_updated` header + Group 2100 In-progress row updated with S2102 close summary
- `docs/research/ARCHITECTURE_INDEX.md` — v72 → v73 preamble + §1.76 S2102 registration + §1.75 S2101 backfill row
- `00-START-NEXT-SESSION.md` — overwritten for S2103 P3 next-session priorities

## Next session priority

**S2103 P3 Retrieval Authority Framework + Corpus Governance Design** per parent §5.3 + S2102 §19.1 R3.x triage list (P3.1 R3.5 dual-cascade must-ship). Arc pin `pa-18b095bb7c4740be` preserved.
