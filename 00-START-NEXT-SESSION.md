# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2100 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2100 arc pin `pa-18b095bb7c4740be` is ACTIVE post-S2102 close 2026-07-04. `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2100 arc (S2100 → S2101 → S2102 → **S2103** → S2104 → S2199) — playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (guardrails-retained-but-generalized per S2099 MC-4 extension).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2100 P2 INGESTION PIPELINE AUDIT LANDED AT S2102; NEXT-SESSION = S2103 P3 RETRIEVAL AUTHORITY FRAMEWORK + CORPUS GOVERNANCE DESIGN

**Group 2100 RAG / Document Loading (Knowledge Loop) arc: S2102 P2 Ingestion / Chunking / Embedding Pipeline Audit CLOSED 2026-07-04 → next is S2103 P3 Retrieval Authority FRAMEWORK + Corpus Governance Design** per parent scoping `2100_rag_document_loading_domain_scoping.md` §5.3.

- **Active arc pin:** `pa-18b095bb7c4740be` — preserved through S2103 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.
- **Arc progress:** S2100 parent scoping (shipped) → S2101 P1 (shipped) → S2102 P2 (shipped this session) → **S2103 P3 (next)** → S2104 P4 Behavior Substrate Structured Observation + Integration → S2199 xx99 canonical summary. Runtime target: 6 sessions on track — 3 of 6 shipped.

## READ THIS THIRD — S2102 P2 SHIP STATE

**P2 audit doc:** `docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md` (~1,795 lines post-fold; `status: active` post-Rigby-SIGN + post-Chris-ratification).

**SIGN cycle 1 result:** CLEAN with 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT across 20 Qs in 4 batches. All 20 STRENGTHEN folds landed pre-commit. Cycle 2 NOT required per Rigby explicit closure.

**Chris ratified 10 items via "agree all" 2026-07-04:**
1. F1 three-chunker regime + severity split MEDIUM-now / HIGH-blocker-for-P3
2. F2 overlap-metadata data lie — **D2100.11 candidate** for Chris D-verdict at close; retrofill choice (a) forward-fix only vs (b) forward-fix + retrofill OPEN
3. F3 dual-cascade paths HIGH + recommended lean (b) fold A into B; (c) UNLIKELY
4. F4 build_rag_corpus on_warning MEDIUM + risk-class + promote-to-HIGH trigger
5. F5-partial derivation acquitted / upstream Document.source unresolved (U1)
6. F6 backfill dormancy reclassified LOW / incomplete-wiring (NOT drift NOT design-intent) + over-claim admission
7. F7 EventBus MISSING dual-severity MEDIUM current / HIGH criticality-as-enabler
8. F8 step-4 timeout derivative/contingent on F3 option choice
9. §15 T-table +2 HIGH + 3 MEDIUM + 1 LOW + T11-into-T10' merge
10. draft→active + commit/PR + post-merge docs cascade + `build_docs_provenance`

**Headline P2 findings for P3 to build on:**
- **Three chunkers, not two.** Parent §5.2 framed two-lane LOCAL vs PROD; audit refines to three physical chunkers: A `build_rag_corpus.chunk_text` (1200-char no-overlap → LOCAL jsonl); B `sync_docs_index_to_documents.chunk_content` (1000+200 → sync_docs DocumentEmbedding); C `content/embeddings.TextSplitter` (1000+200 semantic → async DocumentEmbedding). Two DocumentEmbedding populations coexist with different chunker provenance, no schema field records which.
- **Overlap-metadata data lie.** 24,980 sync_docs chunks overlap semantically but persist `overlap_size=0`. Data-integrity defect surfaces as D2100.11.
- **Dual cascade paths.** Path A `refresh_docs_corpus` scheduled daily 4 AM Denver + Path B `docs_cascade.py` MissionRunner UNSCHEDULED — architectural debt with divergent safety scaffolding.
- **`_derive_source_type` acquitted** — defaults to `'unknown'` NOT `'api'`. Upstream `Document.source='api'` write-site trace deferred to U1.
- **Backfill dormancy = incomplete wiring** (S2101 D5 reclassified, over-claim admission).
- **EventBus MISSING across both paths** — cross-refs S2001 F3 SPIDER_DATA MISSING-producer.

## READ THIS FOURTH — S2103 P3 RETRIEVAL AUTHORITY FRAMEWORK + CORPUS GOVERNANCE DESIGN SCOPE

Per parent scoping §5.3 + S2102 §19.1 handoff:

**Scope.** Design (NOT implement) two coupled substrates: (a) a **retrieval authority FRAMEWORK** — NOT a single universal ranking — with axes and conflict-resolution rules for constructing query-appropriate authority orderings; (b) corpus governance that names owner(s) for the E↔D boundary and formalizes cascade discipline / artifact lifecycle model across five distinct governance meanings.

**Load-bearing questions per parent §5.3:**
- 8-axis retrieval authority framework (D2100.8 adopted): primary vs synthesized / runtime vs research / specificity / recency / supersession / canonical status / lifecycle status + conflict-resolution rule with runtime-facts vs research-posture split
- D2100.9 hybrid metadata contract shape: core-required set + doc-type profile
- Governance-term disambiguation across 5 meanings (ownership / discipline / enforcement / documentation / policy)
- Q5 superseded outranking canonical
- Q6 draft/active/canonical/superseded/deprecated distinction
- Q7 Rigby knows finding authoritative
- Q8-b SHOULD-carry metadata (contract side)

**P3 triage list per Q18 SIGN STRENGTHEN 2026-07-04 (from S2102 §19.1):**

- **P3.1 must-ship — R3.5 dual-cascade resolution** (F3 discharge). Sets the canonical path and constrains every other P3 handoff. Chris ratified recommended lean = option (b) fold A into B OR option (a) wire B + deprecate A. Option (c) retire B UNLIKELY per S1252/S1253 intent.
- **P3.2 must-ship — R3.2 D2100.9 hybrid metadata contract.** Depends on P3.1 canonical-path decision. MUST cover `chunker_id`, `chunker_version`, `overlap_size_actual` (fix F2 by contract), upstream `Document.source` provenance carry-forward.
- **P3.3 must-ship — R3.3 owner assignments** for §18 UNASSIGNED axes: Path A cascade, chunker regimes, `_derive_source_type`, `Document.source` write-sites, DocumentEmbedding schema, `docs/_provenance.json` writes. Discharges S1304 T8 STILL-VALID.
- **P3.x backlog** (Chris may split into P3a/P3b or defer to post-arc):
  - R3.1 topic doc `docs/topics/docs-ingestion-cascade.md` (S1304 T4, S2101 T4, S2102 T4 STILL-VALID)
  - R3.4 cascade governance canonical doc (replace informal MEMORY.md rules)
  - R3.6 backfill activation criteria (F6 discharge — de-scope OR schedule)
  - R3.7 chunker consolidation design (F1 discharge — retire B in favor of C)
  - R3.8 provenance-index scheduling decision (S1304 T1 + S2102 §15.4 reclassification)

**Delegated inheritance handoffs P3 discharges from P1/P2:**
- S2101 R3.1 D2100.9 core-required set ratification with post-P2 chunker_id + chunker_version additions
- S2101 R3.2 8-axis retrieval authority framework design
- S2101 R3.3 ownership assignments per §18 UNASSIGNED axes
- S2101 R3.4 cascade governance canonical doc
- S2101 R3.5 provenance-index rebuild scheduling
- S2102 R3.5 dual-cascade resolution (F3)
- S2102 R3.6 backfill activation criteria (F6)
- S2102 R3.7 chunker consolidation design (F1)
- S2102 R3.8 provenance-index scheduling decision

**D2100.11 candidate ratification path:** Chris "agree all" at S2102 close surfaced D2100.11 as F2 retrofill decision. May land as ratified D-verdict at P3 open OR as separate execution PR, whichever ships first. Options (a) forward-fix only vs (b) forward-fix + retrofill historical 24,980 sync_docs rows.

**Expected shape.** Playbook §11.2 20-section template (ELEVENTH-consecutive application). ~1000-1500 lines. Design-preparation authority per D2100.5 (no implementation this arc).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### §7 anchor-update batch from S2099 (still queued as separate follow-up PR)

Per Q4b SIGN batch-discipline attestation at S2099 close + parent §5.5 handoff: the §7 anchor-update batch is queued as a single atomic follow-up PR — NOT bundled with S2102 close per parallel-safety scope discipline. Batch scope:

- 10 per-plane topic docs
- 1 index / overview doc
- `PLATFORM_INVENTORY.md` subsection
- `PLATFORM_WHAT_IT_IS.md` §7 update
- `EVENT_SYSTEM_INVENTORY.md` §13 with NEW §13.1.5 Fleet Events sidecar subtable
- `ARCHITECTURE_INDEX.md` v70 §1.73 (already registered at S2099 close)
- `CLAUDE.md` Detailed Breakdown row (Fleet Events)
- `OPEN_ARCS.md` Closed section

Owner: Group 2000+ residual (Claude next session or dedicated batch session). Not blocking S2103 P3 open but should land before S2199 to keep anchors current.

## SESSION READY CHECK (before opening S2103 P3)

Before writing the S2103 P3 design-preparation doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local`
2. Verify arc pin ownership: Rigby returns `conversation_owner_match=true` OR pa-18b095bb7c4740be appears in donkeyking's `session_tool.list_recent`
3. Read parent scoping doc `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` §5.3 + §7 anti-scope + §8 ratified D-verdicts
4. Read S2101 P1 audit §5.3 candidate lists (7-field core-required + 3 doc-type profiles + 18-field ROI-trim) + §19.2 (P3 handoffs R3.1-R3.5)
5. Read S2102 P2 audit at `docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md` §14 (F1-F8 findings), §15 (T-table T11-T17 including T13 HIGH dual-cascade + T16 HIGH KD-2 substrate), §17 (Path A vs Path B duplicate + Chunker B/C overlap), §18 (UNASSIGNED ownership matrix), §19.1 (P3 triage list P3.1-P3.3 must-ships + backlog), §19.2 (P4 handoffs), §20.4 (U1-U6 unknowns including U6 LOCAL↔PROD comparability)
6. Verifier-loop pre-draft:
   - Grep for `Document.objects.create(source=` and `Document(source=` — discharge U1 upstream trace for F5
   - Grep for `content/rag_integration.py` write-side — potential 4th chunker per R2.9 Explore 3 flag
   - Grep for existing 5-meaning governance terminology in docs/ (ownership / discipline / enforcement / documentation / policy) to detect prior semantic drift
   - Sample S1904 §17 posture-register format for §17.1 candidate patterns
   - Read `core/employees/jobs.py:DOCUMENTATION_MANAGER` for R3.3 owner-assignment starting point
7. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — 4-5 findings per batch; expect governance-design shape to yield MORE folds than descriptive-audit shape (S2003 P3 governance-design yielded 12 folds in 4 batches)

**S2103 P3 open command (Chris short command):** `Start research group 2103` or `Continue research group 2100` — either invokes S2103 P3 Cat C Retrieval Authority Framework + Corpus Governance Design under Group 2100 arc pin `pa-18b095bb7c4740be`.
