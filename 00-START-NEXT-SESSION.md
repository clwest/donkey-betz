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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin is `pa-aa54193f240f4846`** ("Session 1300 — Memory research group (kickoff)"), preserved across S1301 close for S1302 continuity. Group 1300 mission scope only — no S1270-S1275 turn context carried forward.

**Retired at S1301 close (Chris discretion):** `pa-a23736a833f646cf` — S1301 SIGN isolation pin ("S1301 SIGN — RAG Retrieval Lanes audit pressure-test (isolation)"). SIGN cycle complete; SIGN-clean verdict logged in audit §20.7 + handoff. Pin may retire when Chris approves.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — S1301 IS DRAFT + SIGN-CLEAN; S1302 IS SECOND CHILD AUDIT OF GROUP 1300

Session 1301 landed the **first child audit** under Research Group 1300 (Memory / Knowledge / Embeddings) — `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md`, ~1200 lines, `status: draft`. Rigby SIGN-clean via fresh isolation pin `pa-a23736a833f646cf` after cycle 1 fold. **Chris commit-gate pending** on the entire S1301 artifact set (audit + INDEX v13 + OPEN_ARCS + handoff + this rotation).

**Session close artifacts on the working tree (uncommitted):**

```
docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md   [new]
docs/research/ARCHITECTURE_INDEX.md                                       [modified, v12 → v13]
docs/research/OPEN_ARCS.md                                                [modified, Group 1300 row + reconciliation]
docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md                  [new]
00-START-NEXT-SESSION.md                                                  [modified, this file]
```

Handoff: `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`.

### S1302 IS THE NEXT MISSION — Memory Persistence Architecture

Per parent doc `1300_memory_domain_scoping.md` §5 P2 slot (Chris-locked D4 2026-07-01, renamed from "Memory Store Overlap Audit" to widen scope to durability + authority framing, not just overlap surfacing):

- **Scope:** Categories A + B + C — Semantic Knowledge Memory / Personal-Adaptive Memory / Agent Working Memory.
- **Systems (from parent §3):**
  - **Category A — Semantic Knowledge Memory:** `AgentKnowledgeSource` (`core/models_unified_system.py:521`), `EmbeddingService` (`core/services/embedding_service.py`), `LearningBridge` migration (9 bridges S1115), spider → knowledge → agent prompt injection path.
  - **Category B — Personal / Adaptive Memory:** `UserAgentLearning`, `AgentLearningService`, `ConversationMemory` (per-user pgvector), per-user Redis preference models.
  - **Category C — Agent Working Memory:** `AgentMemory` (episodic), `MemoryPromotionService` (score-gated auto-save from PA turns), `FeedbackLoopEngine` (PA-to-Agent feedback closure S990).
- **Anchor:** S1273 §3.13 (Memory / Knowledge / Embeddings) — read as prior evidence per playbook §7 cross-reference policy.
- **Known drift (from parent §3):**
  - No versioning on `AgentKnowledgeSource`; mutations untracked.
  - Redis-only state → worker recycle can lose recent learning.
  - 14-day freshness hardcoded in `ConversationOrchestrator`.
  - `MemoryPromotionService` scoring criteria opaque (EXPERIMENTAL maturity).
  - `spider_context['pa_content_feedback']` consumer UNKNOWN (KNOWLEDGE_RAG_MEMORY.md §6).

### S1301 finding INHERITED as first-order S1302 scope

Per S1301 §14.3 D3 + §17 + §19: **Two provenance systems coexist without integration.**

- Row-level `DocumentEmbedding.source_type` + `ingested_via` fields (migration 0044, populated by ingestion) are NEVER READ by any retrieval path.
- External `docs/_provenance.json` (built by `build_docs_provenance`, read by `search_docs` filter) has 464 UNKNOWN / 2156 = 21.5% coverage gap.
- The persistence-architecture question: **who writes what metadata when, and who reads it — across Categories A + B + C?** This is a broader-than-retrieval question that S1301 explicitly surfaced but did not own. S1302 does.

The audit questions this drives for S1302:
1. Do Categories A / B / C each have their own provenance/metadata patterns? Or shared?
2. Which cells of the "who writes / who reads" matrix are populated? Which are orphaned like D3?
3. Where does data durability degrade (e.g., Redis-only state, 14-day windows, EXPERIMENTAL scoring)?
4. What is the authority boundary — who is allowed to write agent memory / personal memory / knowledge memory, and how is that enforced (if at all)?

### Two open decisions gating S1302 launch

- **D8 — S1302 launch cadence.** Immediate audit kickoff vs pause for Chris review of the S1301 audit findings first. **Default lean: PAUSE.** Rationale: S1301 draft + INDEX v13 + OPEN_ARCS updates are pending commit-gate; sequencing S1302 open before S1301 commit could produce stacking risk.
- **D9 — Arc pin continuity.** Retain `pa-aa54193f240f4846` (default) vs rotate to fresh Group 1300 pin. **Default lean: RETAIN** — the pin carries mission-scope context that S1302 can reuse without cross-contaminating.

**FIRST THING S1302 open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Ask Chris via arc pin whether S1301 artifacts commit-gate is done (if yes: proceed on `main`; if no: continue stacking on `docs/session-1301-memory-rag-retrieval-lanes` branch)
4. Resolve D8 (launch cadence) + D9 (arc pin) with Chris via `pa-aa54193f240f4846`
5. If greenlit: create branch `docs/session-1302-memory-persistence-architecture` off appropriate base
6. Create `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` per playbook §11.2 20-section template
7. Launch playbook §13 6-sub-agent sweep for Categories A + B + C scope
8. Feed S1301 §14.3 D3 finding as anchor evidence for §17 (Duplicate or Overlapping Systems) and §18 (Ownership Gaps)

---

## PA / Rigby context

- **Active arc pin:** `pa-aa54193f240f4846` (Group 1300 continuity — S1300 open through S1301 close).
- **Retired at S1301 close:** `pa-a23736a833f646cf` (SIGN isolation, may retire on commit).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at S1302 open

- **Branch state:** S1301 branch `docs/session-1301-memory-rag-retrieval-lanes` stacked on `origin/docs/session-1300-memory-research-group-parent-scoping`. Working tree has 4 modified + 2 new files (all S1301 close artifacts). No commits yet.
- **Handoff continuity:** S1301 handoff landed at `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`. S1300 handoff still at `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. S1270-S1275 handoff-drift backfill remains deferred (Rigby default lean at S1300 close — skip; Chris did not override).
- **ARCHITECTURE_INDEX version:** v13 (S1301 §1.16 + §8 timeline row added on this branch, not yet on main).

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1301 artifact set was committed on `main` between sessions — if yes, S1302 branches off `main`; if no, continues stacking on `docs/session-1301-memory-rag-retrieval-lanes`
- [ ] Resolve D8 (S1302 launch cadence) + D9 (arc pin retention) with Chris via `pa-aa54193f240f4846`
- [ ] If greenlit: create branch `docs/session-1302-memory-persistence-architecture`
- [ ] Create `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` per playbook §11.2 20-section template
- [ ] Launch playbook §13 6-sub-agent sweep for Categories A + B + C scope
- [ ] Feed S1301 §14.3 D3 finding as anchor evidence (row-level provenance orphaned; two systems, no bridge)
- [ ] Feed S1300 parent §3 known drift bullets (14-day freshness, Redis-only state, EXPERIMENTAL scoring, opaque promotion criteria) as sweep inputs
- [ ] Do NOT touch Category D (S1301 already owns it)
- [ ] Do NOT touch Category E (S1304 will own it)
- [ ] Do NOT touch Category F (S1303 will own it)
- [ ] Do NOT touch Category G (delegated to Employee OS 1200s arc)
- [ ] Do NOT touch Category H (S1305 will own it)

## Reference — where to look

- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **S1301 audit (draft, SIGN-clean):** `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md`
- **S1301 handoff:** `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`
- **S1300 handoff:** `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template, §13 6-sub-agent sweep, §14 evidence rules, §15 SIGN routing, §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.13 (Memory / Knowledge / Embeddings) + §5.4 (Multi-store overlap flag)
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`
- **KNOWLEDGE_RAG_MEMORY narrative (S1158):** `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean at S1300 close
- Test count drift — minor, ignore unless writing tests
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational)
