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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin is `pa-aa54193f240f4846`** ("Session 1300 — Memory research group (kickoff)"), preserved across S1300 → S1301 → S1302 → S1303 → S1304 close for Group 1300 continuity. Mission scope only — no S1270-S1275 turn context carried forward.

**Retired at S1304 close (Chris discretion):** `pa-2614a91a920642fa` — S1304 SIGN isolation pin ("S1304 SIGN — Memory Domain (Categories E↔D) Documentation Corpus ↔ RAG Boundary Audit pressure-test (isolation)"). SIGN cycles 1 + 2 complete; SIGN-clean verdict logged in audit `sign_status: SIGN-clean` frontmatter + §20.10 gating checklist cycle 2 box ticked + handoff. Pin may retire when Chris approves.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — S1304 IS COMMITTED SIGN-CLEAN; S1305 IS FIFTH CHILD AUDIT OF GROUP 1300

Session 1304 landed the **fourth child audit** under Research Group 1300 (Memory / Knowledge / Embeddings) — `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md`, ~1130 lines, `status: draft`, `sign_status: SIGN-clean`. Rigby SIGN-clean via fresh isolation pin `pa-2614a91a920642fa` after **2 cycles** (4-must-fix fold cycle 1 + verification-only cycle 2). **Second child audit to reach SIGN-clean in 2 cycles** matching S1303 (S1301 = 1, S1302 = 3). **Load-bearing verifier-loop finding: partial invalidation of S1301 §19 D3 hypothesis before propagation** — `DocumentEmbedding.source_type` HAS an owner-model-qualified consumer at `content/embeddings.py:965-973` (`semantic_search_sync` source_filter branch) + `:1007` (SearchResult presentation) + `:904` (async-path presentation, Rigby bonus). Only `ingested_via` remains F1-CANDIDATE orphan pending §19 R1 full-tree recheck. **Chris commit-gate: RESOLVED** — audit committed and merged with `--admin` flag authorization.

**Session close artifacts committed at S1304 close:**

```
docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md   [new]
docs/research/ARCHITECTURE_INDEX.md                                    [modified, v15 → v16]
docs/research/OPEN_ARCS.md                                             [modified, Group 1300 row + 2 reconciliation notes]
docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md                 [new]
00-START-NEXT-SESSION.md                                               [modified, this file]
```

Handoff: `docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md`.

### S1305 IS THE NEXT MISSION — Runtime Memory Correctness (Category H, narrow scope)

Per parent doc `1300_memory_domain_scoping.md` §5 P5 slot:

- **Scope:** Category H — **Runtime Memory Correctness**, NARROW scope. Redis-loss on worker recycle + `lru_cache(1)` staleness only. Explicitly **NOT ops-in-general** per parent §7 anti-scope (Celery worker RSS, PID cache, `OBJC_DISABLE_INITIALIZE_FORK_SAFETY`, macOS SIGSEGV playbook all remain OUT of scope).
- **Systems (from parent §3H + S1302 §14 debt d + S1304 §14 D2):**
  - `_load_provenance_docs()` at `core/services/td_handlers_ops.py:78-93` — `@lru_cache(maxsize=1)` per-process indefinite cache; no invalidation mechanism; worker restart is only refresh path (S1304 D2 HIGH severity)
  - `AgentLearningService.save_memory` at `core/services/agent_learning_service.py:462-483` — writes via `redis_client.hset` at :476 with **no `.expire()` / `.setex()`**; Redis-only durability confirmed by S1302 (grep for `.expire()` returned 0 hits)
  - `AgentLearningService` per-user preference models — Redis-only durability; loss-on-worker-recycle
  - Redis embedding cache (7-day TTL per `EmbeddingService` at `core/services/embedding_service.py:66-413`) — this DOES have TTL and is bounded, not a correctness concern (verify)
  - `search_docs` `lru_cache(1)` per-process — companion to `_load_provenance_docs` cache
  - Any in-process memoization surfaces uncovered during sweep (Agent 2 candidate expansion)
- **Anchors:** parent §3H narrow scope; S1302 §14 debt (d) Redis-only durability; S1304 §14 D2 lru_cache(1) staleness + §14 D6 provenance rebuild cadence unscheduled (worker restart is invalidation mechanism); S1304 §15 T2 remediation options (worker restart trigger vs file-watcher vs Redis TTL vs Redis-backed store).
- **Known drift (inherited from S1302 + S1304):**
  - Redis-loss on worker recycle for `AgentLearningService` learning preferences (S1302 §14 debt d)
  - `lru_cache(1)` staleness at `td_handlers_ops.py:78-93` — write-side/read-side sync gap (S1304 D2)
  - Provenance rebuild cadence unscheduled compounds cache staleness (S1304 D6)
- **Adjacency to prior findings:**
  - S1302 T10 write authority framework gap for AgentMemory.create_memory — RELATED but different domain (write authority, not memory correctness); do NOT re-audit
  - S1301 §14.2 21.5% coverage gap — NOT scope (Cat D internal concern)
  - S1303 §14 F9 no auto-cleanup for retired ChatConversation rows — RELATED but distinct concern (retention lifecycle, not memory correctness); Cat F territory
- **Scope discipline (per parent §5 P5 + §7 anti-scope):**
  - NARROW — memory-correctness drift only, not ops-flavored infrastructure questions
  - Do NOT re-audit Cat A/B/C (S1302 owns) — but MAY cite S1302 findings as adjacent evidence
  - Do NOT re-audit Cat D internals (S1301 owns) or E↔D boundary (S1304 owns) — but MAY cite lru_cache finding as first-order scope evidence
  - Do NOT re-audit Cat E (S1304 owns cascade + docs governance) or Cat F (S1303 owns)
  - Do NOT delegate to Employee OS (Category G is delegated per parent §3G)
  - System RAM behavior remains OUT of scope per parent §7

### Two open decisions gating S1305 launch

- **D14 — S1305 launch cadence.** Immediate audit kickoff vs pause for Chris review of the S1304 audit findings first. **Default lean: PROCEED** — S1301 + S1302 + S1303 + S1304 pattern held (Chris commit-gate resolved between sessions, no stacking risk).
- **D15 — Arc pin continuity.** Retain `pa-aa54193f240f4846` (default) vs rotate to fresh Group 1300 pin. **Default lean: RETAIN** — the pin carries S1300 + S1301 + S1302 + S1303 + S1304 mission-scope context that S1305 can reuse without cross-contaminating.

**FIRST THING S1305 open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1304 artifact set was committed to `main` between sessions — if yes, S1305 branches off `main`; if no, continues stacking on `docs/session-1304-memory-docs-rag-boundary`
4. Resolve D14 (launch cadence) + D15 (arc pin) with Chris via `pa-aa54193f240f4846`
5. If greenlit: create branch `docs/session-1305-memory-runtime-correctness`
6. Create `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md` per playbook §11.2 20-section template
7. Launch playbook §13 6-parallel-Explore sweep for Category H narrow scope
8. Feed S1304 §14 D2 (`lru_cache(1)` staleness) + §14 D6 (provenance rebuild unscheduled) + §15 T2 (remediation options) as anchor evidence
9. Feed S1302 §14 debt (d) (AgentLearningService Redis-only durability) as anchor evidence
10. **Apply F1/F4-CANDIDATE discipline from S1303 §14 + S1304 verifier-loop pattern** — owner-model-qualified consumer inventory required for any dead-code / orphan-write claim; keyword grep insufficient
11. **Scope discipline:** narrow per parent §5 P5 ("Redis-loss + lru staleness only; not ops-in-general"). Do NOT re-audit Cat A/B/C/D/E/F internals. Do NOT touch ops-flavored infrastructure. Focus on memory-CORRECTNESS: where does the runtime model assume persistence Redis/lru_cache doesn't guarantee? Where does staleness silently ship wrong results?
12. **Verifier-loop pattern MANDATORY** — before folding sibling-audit hypotheses into S1305 as inherited premises, verify via direct file:line read at the specific consumer sites named. S1304 established this pattern by partially invalidating S1301 §19 D3 broad claim before propagation.

---

## PA / Rigby context

- **Active arc pin:** `pa-aa54193f240f4846` (Group 1300 continuity — S1300 open through S1304 close).
- **Retired at S1304 close:** `pa-2614a91a920642fa` (S1304 SIGN isolation, may retire on commit).
- **Retired earlier in Group 1300:** `pa-23a38300dd84bae2` (S1303 SIGN isolation, retired at S1303 close per Chris discretion). `pa-1b9f0f5264484c6b` (S1302 SIGN isolation, retired at S1302 close per Chris discretion). `pa-a23736a833f646cf` (S1301 SIGN isolation, retired at S1301 close per Chris discretion).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at S1305 open

- **Branch state:** S1304 branch `docs/session-1304-memory-docs-rag-boundary` merged to `main` this session via `--admin` flag authorization. Working tree clean.
- **Handoff continuity:** S1304 handoff at `docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md`. S1303 handoff at `docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`. S1302 handoff at `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`. S1301 handoff at `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`. S1300 handoff at `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. S1270-S1275 handoff-drift backfill remains deferred (Rigby default lean at S1300 close — skip; Chris did not override across S1300 → S1304).
- **ARCHITECTURE_INDEX version:** v16 (S1304 §1.19 + §8 timeline row added).

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1304 artifact set is on `main` — if yes, S1305 branches off `main`; if no, continues stacking
- [ ] Resolve D14 (S1305 launch cadence) + D15 (arc pin retention) with Chris via `pa-aa54193f240f4846`
- [ ] If greenlit: create branch `docs/session-1305-memory-runtime-correctness`
- [ ] Create `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md` per playbook §11.2 20-section template
- [ ] Launch playbook §13 6-parallel-Explore sweep for Category H narrow scope
- [ ] Feed S1304 §14 D2 + D6 + §15 T2 as anchor evidence
- [ ] Feed S1302 §14 debt (d) as anchor evidence
- [ ] Apply F1/F4-CANDIDATE discipline for any dead-code / orphan-write claim (owner-model-qualified consumer inventory required)
- [ ] **Verifier-loop pattern MANDATORY:** verify sibling-audit hypotheses via direct file:line read before folding as inherited premises
- [ ] **Scope discipline:** NARROW — memory-correctness drift only, not ops-flavored infrastructure
- [ ] Do NOT touch Category A/B/C internals (S1302 owns; may cite adjacent findings)
- [ ] Do NOT touch Category D internals (S1301 owns; may cite lru_cache finding)
- [ ] Do NOT touch Category E internals or E↔D boundary (S1304 owns)
- [ ] Do NOT touch Category F (S1303 owns)
- [ ] Do NOT touch Category G (delegated to Employee OS 1200s arc)
- [ ] System RAM / ops-flavored infrastructure remains OUT per parent §7

## Reference — where to look

- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Prior sibling audits:**
  - `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (Cat D, merged to `main` via PRs #2775 + #2776)
  - `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` (Cat A+B+C, merged to `main` via PR #2777 = `c053272a`)
  - `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` (Cat F, merged to `main` via PR #2778 = `6365f33f`)
  - `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` (Cat E↔D, merged to `main` this session)
- **S1304 handoff:** `docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md`
- **S1303 handoff:** `docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`
- **S1302 handoff:** `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`
- **S1301 handoff:** `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`
- **S1300 handoff:** `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template, §13 6-sub-agent sweep, §14 evidence rules, §15 SIGN routing, §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.13 (has drift bullets for Cat H concerns)
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`
- **KNOWLEDGE_RAG_MEMORY narrative (S1158):** `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`
- **S1305 sweep starting hints:**
  - `core/services/td_handlers_ops.py:78-93` (`_load_provenance_docs` `@lru_cache(maxsize=1)`)
  - `core/services/agent_learning_service.py:462-483` (`save_memory` Redis-only; no `.expire()`)
  - `core/services/embedding_service.py:66-413` (EmbeddingService Redis 7-day TTL — bounded, likely OK; verify)
  - `core/conversation_orchestrator.py:749` (14-day freshness window hardcoded — related but S1302-owned)
  - `core/services/memory_promotion_service.py` (MemoryPromotionService — verify what runtime cache it uses)
  - Any other `@lru_cache` decorator usage across `core/services/` (Agent 2 sweep candidate)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean at S1300 close
- Test count drift — minor, ignore unless writing tests
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational)
