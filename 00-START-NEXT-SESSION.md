# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-chris-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin is `pa-aa54193f240f4846`** ("Session 1300 — Memory research group (kickoff)"), preserved across S1300 → S1301 → S1302 → S1303 close for Group 1300 continuity. Mission scope only — no S1270-S1275 turn context carried forward.

**Retired at S1303 close (Chris discretion):** `pa-23a38300dd84bae2` — S1303 SIGN isolation pin ("S1303 SIGN — Memory Domain (Category F) Conversational / Thread Memory Architecture Audit pressure-test (isolation)"). SIGN cycles 1 + 2 complete; SIGN-clean verdict logged in audit `sign_status: SIGN-clean` frontmatter + §20.10 gating checklist all 12 boxes ticked + handoff. Pin may retire when Chris approves.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — S1303 IS COMMITTED SIGN-CLEAN; S1304 IS FOURTH CHILD AUDIT OF GROUP 1300

Session 1303 landed the **third child audit** under Research Group 1300 (Memory / Knowledge / Embeddings) — `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md`, ~1401 lines, `status: draft`, `sign_status: SIGN-clean`. Rigby SIGN-clean via fresh isolation pin `pa-23a38300dd84bae2` after **2 cycles** (12-edit fold cycle 1 + verification-only cycle 2). **First-inventory landing in the library** — Cat F had no `platform_architecture_inventory.md` §3.N row at audit open; §4 Major Models + §7 Runtime Flows load-bearing (not just referential). **Only child audit to reach SIGN-clean in 2 cycles** (S1301 = 1, S1302 = 3) — verifier-loop spot-checks caught Agent-6's F3 + F4 overreaches BEFORE Rigby SIGN, so cycles focused on substantive gaps not evidence corrections. **Chris commit-gate: RESOLVED** — audit committed and merged.

**Session close artifacts committed at S1303 close:**

```
docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md   [new]
docs/research/ARCHITECTURE_INDEX.md                                                [modified, v14 → v15]
docs/research/OPEN_ARCS.md                                                         [modified, Group 1300 row + 2 reconciliation notes]
docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md                  [new]
00-START-NEXT-SESSION.md                                                           [modified, this file]
```

Handoff: `docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`.

### S1304 IS THE NEXT MISSION — Documentation Corpus ↔ RAG Boundary (Categories E ↔ D)

Per parent doc `1300_memory_domain_scoping.md` §5 P4 slot:

- **Scope:** Categories E ↔ D — Documentation Corpus (Cat E, §3.15) ↔ RAG (Cat D, §3.14). Integration lens between the two. Smaller scope than P1-P3; benefits from §3.14 audit landing first (S1301 shipped).
- **Systems (from parent §3E + §3D + S1301 §19 downstream routing):**
  - `docs/` corpus governance, `build_docs_index`, `sync_docs_index_to_documents`, `verify_doc_claims` registry, `_index.json`, research library, `DOC_LIFECYCLE.md` discipline (inventory-wins-on-conflict)
  - `search_docs` LOCAL keyword lane vs `kb_tool semantic_search` PROD pgvector lane (S1301 finding — verified at `td_handlers_ops.py:5502`)
  - `docs/_provenance.json` (git-history-derived by `build_docs_provenance`); 464 UNKNOWN / 2156 docs = 21.5% coverage gap (S1301 §14.2)
  - `DocumentEmbedding.source_type` + `ingested_via` row-level provenance (migration 0044, populated at ingestion but never read by any retrieval path — S1301 §19 orphan-write pattern)
  - Ingestion → retrieval handoff pathway (4-step docs cascade per memory rule `feedback_docs_pipeline_4_step_cascade.md`)
- **Anchors:** S1273 §3.14 + §3.15; S1301 audit (Cat D exclusive); S1302 §17.3 name-collision boundary methodology.
- **Known drift (inherited from S1301 + S1303):**
  - 21.5% corpus-completeness gap in provenance filter (S1301 §14.2)
  - Two provenance systems coexist without integration (row-level fields never read by retrieval — S1301 §19 orphan-write pattern)
  - `search_docs` `lru_cache(1)` per-process → workers need restart after `build_docs_provenance` (S1301 §14 known drift)
  - PA turn enrichment does NOT auto-invoke RAG — tool-call-only (S1301 §14; S1303 §9 Cat F ↔ Cat D OBSERVED GAP)
- **Adjacency to S1301 + S1302 + S1303 findings (inherit as evidence):**
  - S1301 §19 explicitly routed E↔D handoff to S1304
  - S1302 §17.3 name-collision resolution as boundary methodology pattern
  - S1303 §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3 turn-context → RAG enrichment design proposal — S1304 should decide whether wiring is intentional separation or genuine gap
  - S1303 F4-CANDIDATE discipline (owner-model-qualified consumer inventory) — S1304 should apply the same discipline to any E↔D field-consumer claim

### Two open decisions gating S1304 launch

- **D12 — S1304 launch cadence.** Immediate audit kickoff vs pause for Chris review of the S1303 audit findings first. **Default lean: PROCEED** — S1301 + S1302 + S1303 pattern held (Chris commit-gate resolved between sessions, no stacking risk).
- **D13 — Arc pin continuity.** Retain `pa-aa54193f240f4846` (default) vs rotate to fresh Group 1300 pin. **Default lean: RETAIN** — the pin carries S1300 + S1301 + S1302 + S1303 mission-scope context that S1304 can reuse without cross-contaminating.

**FIRST THING S1304 open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1303 artifact set was committed to `main` between sessions — if yes, S1304 branches off `main`; if no, continues stacking on `docs/session-1303-memory-conversational-thread-memory`
4. Resolve D12 (launch cadence) + D13 (arc pin) with Chris via `pa-aa54193f240f4846`
5. If greenlit: create branch `docs/session-1304-memory-docs-rag-boundary`
6. Create `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` per playbook §11.2 20-section template
7. Launch playbook §13 6-parallel-Explore sweep for E↔D boundary scope
8. Feed S1301 §14.2 silent-failure surface + §19 downstream routing as anchor evidence
9. Feed S1302 §17.3 name-collision resolution as boundary methodology pattern
10. Feed S1303 §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3 turn-context → RAG enrichment design proposal
11. **Apply F4-CANDIDATE discipline from S1303 §14 F4** — owner-model-qualified consumer inventory required for any dead-code claim; keyword grep insufficient
12. **Scope discipline:** smaller than P1-P3 audits per parent §5 P4 rationale ("smaller scope; benefits from §3.14 audit landing first"). Do NOT re-audit Cat D internals (S1301 owns). Do NOT re-audit Cat E docs corpus internals (belongs to Cat E). Focus on the BOUNDARY: how does the corpus become RAG-visible? Where does ingestion hand off to retrieval? Where do the two provenance systems (external `_provenance.json` vs row-level `DocumentEmbedding.source_type`) disagree?

---

## PA / Rigby context

- **Active arc pin:** `pa-aa54193f240f4846` (Group 1300 continuity — S1300 open through S1303 close).
- **Retired at S1303 close:** `pa-23a38300dd84bae2` (S1303 SIGN isolation, may retire on commit).
- **Retired earlier in Group 1300:** `pa-1b9f0f5264484c6b` (S1302 SIGN isolation, retired at S1302 close per Chris discretion). `pa-a23736a833f646cf` (S1301 SIGN isolation, retired at S1301 close per Chris discretion).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at S1304 open

- **Branch state:** S1303 branch `docs/session-1303-memory-conversational-thread-memory` merged to `main` (or stacked if commit-gate not yet resolved). Working tree clean.
- **Handoff continuity:** S1303 handoff at `docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`. S1302 handoff at `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`. S1301 handoff at `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`. S1300 handoff at `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. S1270-S1275 handoff-drift backfill remains deferred (Rigby default lean at S1300 close — skip; Chris did not override across S1300 → S1303).
- **ARCHITECTURE_INDEX version:** v15 (S1303 §1.18 + §8 timeline row added).

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1303 artifact set is on `main` — if yes, S1304 branches off `main`; if no, continues stacking
- [ ] Resolve D12 (S1304 launch cadence) + D13 (arc pin retention) with Chris via `pa-aa54193f240f4846`
- [ ] If greenlit: create branch `docs/session-1304-memory-docs-rag-boundary`
- [ ] Create `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` per playbook §11.2 20-section template
- [ ] Launch playbook §13 6-parallel-Explore sweep for E ↔ D boundary scope
- [ ] Feed S1301 §14.2 silent-failure surface + §19 downstream routing as anchor evidence
- [ ] Feed S1302 §17.3 name-collision resolution as boundary methodology pattern
- [ ] Feed S1303 §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3 turn-context → RAG enrichment as design-hypothesis input
- [ ] Apply F4-CANDIDATE discipline from S1303 for any dead-code claim (owner-model-qualified consumer inventory required)
- [ ] **Scope discipline:** boundary lens only — do NOT re-audit Cat D or Cat E internals
- [ ] Do NOT touch Category A/B/C (S1302 owns)
- [ ] Do NOT touch Category D internals (S1301 owns; boundary only)
- [ ] Do NOT touch Category E internals (S1304 boundary only — full Cat E audit is a possible future arc if warranted)
- [ ] Do NOT touch Category F (S1303 owns)
- [ ] Do NOT touch Category G (delegated to Employee OS 1200s arc)
- [ ] Do NOT touch Category H (S1305 will own it)

## Reference — where to look

- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Prior sibling audits:**
  - `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (Cat D, merged to `main` via PRs #2775 + #2776)
  - `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` (Cat A+B+C, merged to `main` via PR #2777 = `c053272a`)
  - `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` (Cat F, merged to `main` this session)
- **S1303 handoff:** `docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`
- **S1302 handoff:** `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`
- **S1301 handoff:** `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`
- **S1300 handoff:** `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template, §13 6-sub-agent sweep, §14 evidence rules, §15 SIGN routing, §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.14 (Cat D) + §3.15 (Cat E)
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`
- **KNOWLEDGE_RAG_MEMORY narrative (S1158):** `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`
- **S1304 sweep starting hints:**
  - `core/rag.py` (LOCAL keyword lane — `core.rag.top_k` on `.rag/corpus.jsonl` per S1301)
  - `core/rag_integration.py` (PROD pgvector lane — `search_embeddings` per S1301)
  - `core/services/td_handlers_ops.py:5502` (search_docs handler — S1301 verified)
  - `core/services/td_handlers_ops.py:82-85` (provenance filter docstring — S1145 P2 spec)
  - `docs/_provenance.json` (git-history-derived by `build_docs_provenance`)
  - `core/management/commands/build_docs_index.py`, `sync_docs_index_to_documents.py`, `build_docs_provenance.py`
  - `core/management/commands/verify_doc_claims.py` (S1099 doc claim verifier)
  - `core/models/documents.py` `DocumentEmbedding` (migration 0044 for `source_type` + `ingested_via` per S1301 §19 orphan-write pattern)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean at S1300 close
- Test count drift — minor, ignore unless writing tests
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational)
