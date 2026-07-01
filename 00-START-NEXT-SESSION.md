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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin is `pa-aa54193f240f4846`** ("Session 1300 — Memory research group (kickoff)"), preserved across S1300 → S1301 → S1302 close for Group 1300 continuity. Mission scope only — no S1270-S1275 turn context carried forward.

**Retired at S1302 close (Chris discretion):** `pa-1b9f0f5264484c6b` — S1302 SIGN isolation pin ("S1302 SIGN — Memory Persistence Architecture audit pressure-test (isolation)"). SIGN cycles 1 + 2 + 3 complete; SIGN-clean verdict logged in audit `sign_status: SIGN-clean` frontmatter + §20.7 fold notes + handoff. Pin may retire when Chris approves.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — S1302 IS DRAFT + SIGN-CLEAN; S1303 IS THIRD CHILD AUDIT OF GROUP 1300

Session 1302 landed the **second child audit** under Research Group 1300 (Memory / Knowledge / Embeddings) — `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md`, ~1700 lines, `status: draft`, `sign_status: SIGN-clean`. Rigby SIGN-clean via fresh isolation pin `pa-1b9f0f5264484c6b` after three fold cycles (cycle 1: F2 narrowed via reader-citation evidence on 3 AgentKnowledgeSource fields; cycle 2: 4 AgentMemory fields removed after Memory Palace consumer discovery + methodology tightening from "0 consumers" to "no explicit-qualified references found on the model"; cycle 3: poison_risk_* reclassified from orphan to narrow-consumer-safety-filter via memory_embedding_service.py consumer). **Chris commit-gate pending** on the entire S1302 artifact set (audit + INDEX v14 + OPEN_ARCS + handoff + this rotation).

**Session close artifacts on the working tree (uncommitted):**

```
docs/research/domains/memory/1302_memory_persistence_architecture_audit.md   [new]
docs/research/ARCHITECTURE_INDEX.md                                            [modified, v13 → v14]
docs/research/OPEN_ARCS.md                                                     [modified, Group 1300 row + 3 reconciliation notes]
docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md                  [new]
00-START-NEXT-SESSION.md                                                       [modified, this file]
```

Handoff: `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`.

### S1303 IS THE NEXT MISSION — Conversational / Thread Memory (Category F)

Per parent doc `1300_memory_domain_scoping.md` §5 P3 slot:

- **Scope:** Category F — Conversational / Thread Memory. **First inventory-row landing for this sub-domain** — S1273 has no §3 row for it today; S1303 will produce the missing row.
- **Systems (from parent §3F):**
  - `ConversationSession` (PA session pin identity)
  - `session_tool.create_fresh` carry-forward semantics
  - Tool-call history reinjection into subsequent turns
  - Pin rotation policy (retire vs continue heuristics)
  - PA `unified_pa_entrypoint` enrichment pipeline
- **Anchor:** no direct S1273 §3.x row; referenced obliquely in Employee OS row (§4) and Agent System row (§3.2). S1302 §17.3 documented the `ConversationMemory` name collision (Django model at `core/models/conversations/models.py:19` vs in-process construct at `core/conversation_memory.py:59`) — the Django model is S1302 owned (Cat B), the session/thread state is S1303 owned (Cat F).
- **Known drift (from parent §3F):**
  - Stale-thread dispatcher waste (Session 1212 deliverable 777d9cd8 — ~$3.60/day on retired-thread dispatches)
  - `session_tool.retire` action existence historically questioned; verified working at S1301 close per memory rule `feedback_session_tool_retire_works.md` — Rigby retired SIGN pin `pa-a23736a833f646cf` cleanly. That memory rule STANDS entering S1303.
- **Adjacency to S1302 findings (inherit as evidence):**
  - S1302 §17.3 `ConversationMemory` name-collision resolution — S1303 should establish the ConversationSession ↔ ConversationMemory boundary explicitly.
  - S1302 §14.3 F1 dead-code pattern — worth checking if analogous producer-only patterns exist in the session/thread state layer (e.g., pin-metadata fields populated but never surfaced).
  - S1302 §18.3 category-assignment ambiguity (MemoryPromotionService Cat B vs Cat C) — S1303 should be careful about boundaries with S1302's UserMemoryContext write target.

### Two open decisions gating S1303 launch

- **D10 — S1303 launch cadence.** Immediate audit kickoff vs pause for Chris review of the S1302 audit findings first. **Default lean: PROCEED** — S1301 pattern held (Chris commit-gate resolved between sessions, no stacking risk). If Chris commit-gate on S1302 is not resolved by S1303 open, stacking on `docs/session-1302-memory-persistence-architecture` branch is possible per S1301's stacking pattern.
- **D11 — Arc pin continuity.** Retain `pa-aa54193f240f4846` (default) vs rotate to fresh Group 1300 pin. **Default lean: RETAIN** — the pin carries S1300 + S1301 + S1302 mission-scope context that S1303 can reuse without cross-contaminating.

**FIRST THING S1303 open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1302 artifact set was committed on `main` between sessions — if yes, S1303 branches off `main`; if no, continues stacking on `docs/session-1302-memory-persistence-architecture`
4. Resolve D10 (launch cadence) + D11 (arc pin) with Chris via `pa-aa54193f240f4846`
5. If greenlit: create branch `docs/session-1303-memory-conversational-thread-memory`
6. Create `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` per playbook §11.2 20-section template
7. Launch playbook §13 6-parallel-Explore sweep for Category F scope
8. Feed S1302 §17.3 name-collision resolution + §14.3 F1 dead-code pattern as anchor evidence
9. Feed S1300 parent §3F known drift bullet (stale-thread dispatcher waste — deliverable 777d9cd8) as sweep input
10. Feed memory rule `feedback_session_tool_retire_works.md` as sweep input for pin-retirement mechanism
11. **First-inventory discipline:** since Cat F has no §3 row today, the audit's §11 (Existing Documentation) + §4 (Major Models) will need to define the terrain, not just cite existing coverage. Expect a light research coverage classification (LIGHT or NONE per playbook §12) and plan §7 (Runtime Flows) as the load-bearing section.

---

## PA / Rigby context

- **Active arc pin:** `pa-aa54193f240f4846` (Group 1300 continuity — S1300 open through S1302 close).
- **Retired at S1302 close:** `pa-1b9f0f5264484c6b` (S1302 SIGN isolation, may retire on commit).
- **Retired earlier in Group 1300:** `pa-a23736a833f646cf` (S1301 SIGN isolation, retired at S1301 close per Chris discretion).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at S1303 open

- **Branch state:** S1302 branch `docs/session-1302-memory-persistence-architecture` stacked on `origin/main`. Working tree has 4 modified + 2 new files (all S1302 close artifacts). No commits yet.
- **Handoff continuity:** S1302 handoff landed at `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`. S1301 handoff at `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`. S1300 handoff at `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. S1270-S1275 handoff-drift backfill remains deferred (Rigby default lean at S1300 close — skip; Chris did not override across S1300 → S1302).
- **ARCHITECTURE_INDEX version:** v14 (S1302 §1.17 + §8 timeline row added on this branch, not yet on main).

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1302 artifact set was committed on `main` between sessions — if yes, S1303 branches off `main`; if no, continues stacking on `docs/session-1302-memory-persistence-architecture`
- [ ] Resolve D10 (S1303 launch cadence) + D11 (arc pin retention) with Chris via `pa-aa54193f240f4846`
- [ ] If greenlit: create branch `docs/session-1303-memory-conversational-thread-memory`
- [ ] Create `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` per playbook §11.2 20-section template
- [ ] Launch playbook §13 6-parallel-Explore sweep for Category F scope
- [ ] Feed S1302 §17.3 name-collision resolution (Django `ConversationMemory` vs in-process class) as anchor evidence for §17
- [ ] Feed S1302 §14.3 F1 dead-code detection pattern as sweep input (are there analogous producer-only patterns in session/thread state?)
- [ ] Feed S1300 parent §3F known drift (stale-thread dispatcher waste — Session 1212 deliverable 777d9cd8) as sweep input
- [ ] Feed memory rule `feedback_session_tool_retire_works.md` — retire action works — as sweep input
- [ ] Expect **first-inventory** discipline: Cat F has no §3 row today. §7 (Runtime Flows) will be load-bearing; §11 (Existing Documentation) will show LIGHT or NONE coverage
- [ ] Do NOT touch Category A/B/C (S1302 already owns them)
- [ ] Do NOT touch Category D (S1301 already owns it)
- [ ] Do NOT touch Category E (S1304 will own it)
- [ ] Do NOT touch Category G (delegated to Employee OS 1200s arc)
- [ ] Do NOT touch Category H (S1305 will own it)

## Reference — where to look

- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Prior sibling audits:**
  - `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (Cat D, merged to `main` via PRs #2775 + #2776)
  - `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` (Cat A+B+C, draft on S1302 branch, SIGN-clean)
- **S1302 handoff:** `docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`
- **S1301 handoff:** `docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`
- **S1300 handoff:** `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template, §13 6-sub-agent sweep, §14 evidence rules, §15 SIGN routing, §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` — no §3 row for Cat F yet; will land in S1303
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`
- **KNOWLEDGE_RAG_MEMORY narrative (S1158):** `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`
- **Session-thread specific code entry points (S1303 sweep starting hints):**
  - `core/services/session_tool.py` (or wherever session_tool handler lives — grep to locate)
  - `core/services/unified_pa_entrypoint.py` — enrichment pipeline + PA session identity carry-forward
  - `core/conversation_memory.py` (in-process ConversationMemory — S1302 disambiguation)
  - `core/models/conversations/models.py` — ChatConversation model (adjacent, per S1302 §4.B)
  - Session 1212 deliverable `777d9cd8` — stale-thread dispatcher waste analysis

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean at S1300 close
- Test count drift — minor, ignore unless writing tests
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational)
