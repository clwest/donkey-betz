---
session: 1301
status: closed (draft-audit landed, Rigby SIGN-clean, Chris commit-gated)
date: 2026-07-01
arc: Research Group 1300 (Memory / Knowledge / Embeddings) — child P1 (playbook §11.2 20-section audit template). First child audit under the parent-with-children arc shape locked at S1300. Category D exclusive scope (RAG / Document Retrieval per parent §3D + §5D + §6). Traces parent §6 provenance-filter finding (search_docs 8 pre-filter → 7 excluded_missing_provenance + 1 excluded_mismatch → 0) to root cause.
prs_merged: []
prs_open:
  - "S1301 audit + INDEX v13 + OPEN_ARCS + handoff (stacked on docs/session-1300 branch; commit-gated on Chris per playbook §16)"
prs_upstream:
  - "S1300 branch: docs/session-1300-memory-research-group-parent-scoping (parent scoping + Research OS install + Playbook v2 landed there — S1301 branch base)"
branches_open:
  - "docs/session-1301-memory-rag-retrieval-lanes (base = origin/docs/session-1300-memory-research-group-parent-scoping)"
companions:
  - docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md
  - docs/research/domains/memory/1300_memory_domain_scoping.md
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
deliverables:
  - "docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md (1200+ lines, status: draft, authority: research, research_group: 1300, child_slot: P1; 20-section playbook §11.2 template; verifier_loop v1 synthesis + v1.1 Rigby SIGN cycle 1 fold — SIGN-clean)"
  - "docs/research/ARCHITECTURE_INDEX.md — v12 → v13; §1.16 row added; §8 timeline S1301 row added"
  - "docs/research/OPEN_ARCS.md — Group 1300 in-progress row advanced current-child from 'S1301 queued' to 'S1301 SIGN-clean (commit-gated) + S1302 queued'; 2 reconciliation notes added"
  - "docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md (this doc)"
  - "00-START-NEXT-SESSION.md — rotated to S1302 mission spec (Memory Persistence Architecture — Categories A + B + C)"
key_findings:
  - "search_docs runs LOCAL keyword lane (core.rag.top_k on .rag/corpus.jsonl); kb_tool semantic_search runs PROD pgvector lane (core.rag_integration.search_embeddings). Verified at core/services/td_handlers_ops.py:5502. Prior to S1301 the two tools were mentally-modeled as parallel implementations of the same thing; the audit surfaces they run entirely different lanes with different corpus surfaces and different provenance semantics."
  - "Parent §6 finding root-caused: HYP-1 (migration-incomplete: docs/_provenance.json has 464 UNKNOWN entries out of 2156 total per _meta.confidence_breakdown = 21.5% coverage gap) × HYP-4 (never-wired-into-ingestion: row-level DocumentEmbedding.source_type/ingested_via fields added in migration 0044 are populated at ingestion but never read by any retrieval path — grep-confirmed 0 hits in rag_integration.py, rag.py, scoped_retrieval.py). Filter treats 'chunk path not in external index' as excluded_missing_provenance by design per Rigby S1145 P2 spec (td_handlers_ops.py:82-85 docstring)."
  - "Prod pgvector lane bypasses the provenance filter entirely — _filter_chunks_by_originating_session only called from _handle_search_docs. kb_tool semantic_search runs unfiltered."
  - "Two-lane runtime selector NEVER IMPLEMENTED. Playbook §12 §3.13 research question resolved as negative. search_docs hardcoded to local lane at td_handlers_ops.py:5502; kb_tool hardcoded to prod lane."
  - "PA turn enrichment does NOT auto-invoke RAG — tool-call-only. Grep of unified_pa_entrypoint.py returns zero RAG imports. A user asking Rigby a docs-flavored question without triggering a tool call receives zero docs context; Rigby answers from LLM training + conversation memory."
  - "Silent-failure surface confirmed (core/ tree-scoped). Filter counters (excluded_missing_provenance / excluded_mismatch / pre_filter_count) live only in the response payload. Grep across core/**/*.py returned 2 files matched (td_handlers_ops.py handler + test_search_docs_originating_session_filter.py unit test). No log line, no metric, no alert. S1300 anchor finding surfaced only via manual tool inspection."
  - "Subsystem maturity verdict: WORKING (dropped from STABLE). Prod pgvector lane individually STABLE; local keyword lane individually PARTIAL (unchanged from S1273 §3.14). Combined-subsystem WORKING captures the corpus-completeness gap that neither individual verdict conveys — retrieval mechanism is sound, corpus that powers it has coverage gaps that surface as silent zero-result queries."
  - "§19 downstream routing: S1302 owns row-level provenance semantics (persistence-architecture concern that spans Categories A + B + C); S1304 owns E↔D ingestion→retrieval handoff; Group 1700 owns filter-drop telemetry. S1399 canonical summary is expected to name the provenance drift class if it recurs across P1/P2/P4."
open_decisions_carried_forward:
  - "Chris commit-gate on the S1301 branch — audit + INDEX v13 + OPEN_ARCS + handoff + S1302 START-NEXT rotation all landed on working tree; single commit-clean gesture would land the whole session's artifact set. Playbook §16 requires explicit 'commit it' from Chris."
  - "Fresh isolation pin pa-a23736a833f646cf retirement — SIGN cycle complete; pin may retire at Chris's discretion after commit."
  - "S1302 launch cadence — playbook default is 'immediate on session open' but Chris may want a pause to review S1301 audit findings first. Not blocking S1301 close."
rigby_sign_cycle_1:
  fresh_isolation_pin: "pa-a23736a833f646cf"
  pin_title: "S1301 SIGN — RAG Retrieval Lanes audit pressure-test (isolation)"
  ownership_verified: "chris (conversation_owner_match: true)"
  provisional_verdict: "SIGN-with-edits (4 must-fix + 6 nice-to-have) pending grep-verification of claims 4-8 that Rigby could not close in-pin due to repo_tool file-size caps on docs/_provenance.json and time-bounded grep budget."
  must_fix_folded:
    - "MF1 (§14.1 denominator) — added verbatim _meta block quote from docs/_provenance.json:2-14: doc_count 2156, confidence_breakdown HIGH 1356 / MEDIUM 336 / LOW 0 / UNKNOWN 464. Explicit arithmetic 464/2156 = 21.5%."
    - "MF2 (§14.3 D3 grep evidence) — 0 hits on source_type|ingested_via in retrieval-path files (rag_integration.py / rag.py / scoped_retrieval.py); 3 hits in td_handlers_ops.py are on other unrelated handlers, annotated inline."
    - "MF3 (§9.1 MISSING inbound) — hedged classifications to grep-scope: 0 files matched for kb_tool|search_docs|search_embeddings|ScopedRetrievalService|rag_integration|core.rag across content*.py, mission_runner.py, signal_aggregation_service.py; Content Pipeline note added referencing ContentProvenance as adjacent-but-different provenance surface."
    - "MF4 (§14.2 silent-failure claim) — added system-wide grep receipts across core/**/*.py: 2 files matched for the counter names (handler + test); scoped the claim to core/ tree explicitly."
  nice_to_have_deferred:
    - "NH2-NH6: lane decision tree, catastrophic-zero-results warning polish, UI surfacing of counters (design-preparation-phase), crisper drift-class definitions, ownership-routing tone hardening. All non-blocking; correctness intact."
  final_verdict: "SIGN-clean (after fold cycle, same fresh pin)"
  additional_risks_surfaced:
    - "Counter-name coupling meta-risk: 'no consumer' proof is keyed on grep for specific counter names; a future refactor renaming keys would make grep proof stale without changing underlying reality."
    - "Path-normalization join fragility: highest-leverage operational failure mode — no integrity check enforces that .rag/corpus.jsonl file paths match keys in docs/_provenance.json."
next_session_readiness:
  - "S1302 mission is well-scoped by parent + S1301 §19. Categories A + B + C (Semantic Knowledge Memory / Personal-Adaptive Memory / Agent Working Memory) share a 'row-level provenance semantics' inheritance from S1301's §14.3 D3 drift finding — this becomes S1302 first-order scope."
  - "S1301 sub-agent Explore pattern (playbook §13) validated end-to-end for the first time. Parent-agent verifier-loop spot-checks caught two speculation-vs-fact issues (NULL row provenance vs 'unknown' default; search_docs lane assumption) before Rigby SIGN — the loop works."
  - "Rigby SIGN discipline validated for child audits: fresh isolation pin cleanly separated arc pin from SIGN pressure-test. Provisional-then-final verdict shape (with must-fix fold in between) is repeatable."
memory_rule_touches:
  - "feedback_pa_local_verify_ownership.md — S1301 confirmed ownership on both arc pin (pa-aa54193f240f4846) and fresh isolation SIGN pin (pa-a23736a833f646cf). Both = chris. Both match confirmed."
  - "feedback_claude_directs_rigby_then_verifies.md — S1301 open executed the pattern: session_context check directive → Rigby ran platform_config_tool overview → Claude verified. SIGN routing directive → Rigby ran fresh-pin session_tool.create_fresh → Claude verified pin ID + ownership."
  - "feedback_rigby_tool_verification.md — S1301 SIGN cycle 1 first response looked like 'MF1 unverified' but reading the Tool Runs block showed Rigby had grep-hit UNKNOWN=464 and read the mechanism source — she'd verified more than her provisional narrative claimed."
  - "feedback_docs_pipeline_4_step_cascade.md — S1301 handoff, INDEX, OPEN_ARCS, and audit all get pushed to Documents + embedded via the 4-step cascade after Chris commit. Not run in this session."
followup_queue:
  - "S1302 Memory Persistence Architecture — Categories A + B + C (playbook §22 queue)"
  - "S1304 Documentation Corpus ↔ RAG Boundary (Categories E ↔ D) — inherits provenance-boundary questions from S1301"
  - "S1303 Conversational / Thread Memory (Category F — no §3 row yet, child audit adds one)"
  - "S1305 Runtime Memory Correctness (Category H narrow scope — Redis-loss + lru staleness)"
  - "S1399 Group 1300 Canonical Summary (cross-cutting synthesis)"
  - "Group 1700 Observability filter-drop telemetry follow-on"
owner: claude (drafted S1301)
---

# Session 1301 — RAG Retrieval Lanes Audit (Group 1300 Child P1)

## Session shape

**Mission (opened by Chris short command 2026-07-01):** *"Start research group 1300, session 1301: RAG Retrieval Lanes"* — the playbook §21 short-command entry point on the first child audit under Research Group 1300 (Memory / Knowledge / Embeddings).

**Executed contract:**
- Playbook §21 short-command → §11.2 20-section child-audit template.
- Playbook §13 6-parallel-Explore sub-agent sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity).
- Parent-agent verifier-loop spot-checks per playbook §13 synthesis step 2.
- Playbook §15 stage-scoped Rigby routing: full SIGN required on child audits; routed to a fresh isolation pin per fresh-pin discipline.
- Playbook §16 commit policy: draft-first, Chris commit-gate.

**Session close criteria met per playbook §14 completion contract:**
- Audit doc at `status: draft`, all 20 sections populated with cited evidence + honest UNKNOWNs.
- Rigby SIGN cycle 1 → SIGN-clean after 4-must-fix fold.
- INDEX v13 registration (§1.16 + §8 timeline row + frontmatter bump).
- OPEN_ARCS reconciliation notes + Group 1300 current-child advancement.
- This handoff.
- 00-START-NEXT-SESSION.md rotated to S1302.

## What the audit found (executive)

Category D RAG Retrieval Lanes is not one subsystem — it is **two lanes running in parallel** under two PA tools that look similar in name but do entirely different things:

- **`search_docs` (PA tool)** → runs `core.rag.top_k` on `.rag/corpus.jsonl` (LOCAL keyword). Optional `originating_session` filter reads `docs/_provenance.json` (git-history-derived index built by `build_docs_provenance`) and drops chunks whose file path is missing from the index or whose stored session doesn't match.
- **`kb_tool` (PA tool, `semantic_search` action)** → runs `core.rag_integration.search_embeddings` on `DocumentEmbedding` (PROD pgvector cosine over HNSW). Filter pushdown is on Document fields (category, document_class, min_session, is_pinned, promotion_status). **NO provenance filter.**

Parent §6 finding (8 pre-filter → 7 `excluded_missing_provenance` + 1 `excluded_mismatch` → 0) was against the LOCAL keyword lane + external provenance filter. The PROD pgvector lane would not have exhibited the same behavior — it doesn't consult that filter at all.

**Root cause (verifier-loop-confirmed, Rigby SIGN-clean):** the provenance index has systemic coverage gaps (464 UNKNOWN entries out of 2156 docs = 21.5%), the filter treats "path not in index" as exclusion by design (Rigby's S1145 P2 spec), and no observability surface tells the caller the filter fired. Silent zero-result on the caller side; buried filter counters in the response payload; no log / metric / alert.

**Row-level provenance orphans:** `DocumentEmbedding.source_type` and `ingested_via` fields were added in migration 0044 (2026-03-01) and are populated at ingestion by `content/embeddings.py:642-656`. **No query path reads them.** Two provenance systems coexist without a bridge — that's the persistence-architecture question S1302 inherits.

## What did NOT get done

- **No commit landed on `main` or on the S1301 branch.** Per playbook §16, Chris commit-gate is explicit. All artifacts on working tree.
- **No implementation PRs.** Playbook §14.5 forbids implementation during research; the audit is design-input, not design.
- **No corpus rebuild.** Suggesting `build_docs_provenance` re-run as remediation is design-preparation-phase work, not S1301's job.
- **No metric / observability wiring.** Silent-failure surface is characterized; wiring it is Group 1700 Observability follow-on.

## Session-close artifacts on the working tree (uncommitted)

```
docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md   [new, ~1200 lines]
docs/research/ARCHITECTURE_INDEX.md                                       [modified, v12 → v13, §1.16 + §8 row]
docs/research/OPEN_ARCS.md                                                [modified, Group 1300 row advanced + reconciliation notes]
docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md                  [new, this doc]
00-START-NEXT-SESSION.md                                                  [modified, S1302 mission spec]
```

## Ready-to-commit single gesture

```bash
git add docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md \
        docs/research/ARCHITECTURE_INDEX.md \
        docs/research/OPEN_ARCS.md \
        docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md \
        00-START-NEXT-SESSION.md
git commit -m "docs(session-1301): Memory RAG Retrieval Lanes audit + INDEX v13"
```

Chris commit-gate required per playbook §16.

## Reference — where things are

- **S1301 audit:** `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md`
- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.13 / §3.14 / §3.15 / §5.4
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`
- **Retrieval mechanism source:** `core/services/td_handlers_ops.py:78-127` (filter) + `:5468-5610` (search_docs handler) + `:5202` (kb_tool handler entry, semantic_search action)
- **Retrieval Python API:** `core/rag_integration.py:27-224` (prod pgvector) + `core/rag.py:39-82` (local keyword)
- **Provenance index producer:** `core/management/commands/build_docs_provenance.py`
- **Provenance file:** `docs/_provenance.json` (1034674 bytes; generated 2026-06-23; 2156 docs; 464 UNKNOWN)

## Pin state

- **Arc pin (Group 1300 continuity):** `pa-aa54193f240f4846` — carries S1301 mission-side context. Preserved for S1302 continuity.
- **SIGN isolation pin (S1301 only):** `pa-a23736a833f646cf` — SIGN cycle 1 complete + SIGN-clean. May retire at Chris's discretion after commit.
