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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin is `pa-aa54193f240f4846`** ("Session 1300 — Memory research group (kickoff)"), preserved across S1300 → S1301 → S1302 → S1303 → S1304 → S1305 close for Group 1300 continuity. Mission scope only — no S1270-S1275 turn context carried forward. This pin is expected to carry through S1399 canonical summary, then retire on Group 1300 arc close.

**Retired at S1305 close (Chris directive `commit + retire pin`):** `pa-56a527a2c5528508` — S1305 SIGN isolation pin ("Session 1305 — Memory Runtime Correctness (Category H) audit pressure-test (isolation)"). SIGN cycles 1 + 2 complete; SIGN-clean verdict logged in audit `sign_status: SIGN-clean` frontmatter + §20.10 gating checklist cycle 2 box ticked + handoff. Retire verified: `updated_count: 2, retired: true` via `session_tool.retire` at S1305 close 2026-07-01.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — S1305 IS COMMITTED SIGN-CLEAN; S1399 IS THE GROUP 1300 CANONICAL SUMMARY

Session 1305 landed the **fifth (and final) child audit** under Research Group 1300 (Memory / Knowledge / Embeddings) — `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md`, ~1080 lines, `status: draft`, `sign_status: SIGN-clean`. Rigby SIGN-clean via fresh isolation pin `pa-56a527a2c5528508` after **2 cycles** (3-must-fix fold cycle 1 + verification-only cycle 2). **Third child audit to reach SIGN-clean in 2 cycles** matching S1303 + S1304 (S1301 = 1, S1302 = 3). **Load-bearing methodology extension: verifier-loop pattern extended from hypothesis-correction to severity-correction** — S1305 downgraded Agent 6's CRITICAL AgentLearningService durability claim to MEDIUM via Redis AOF context (`settings.py:944 REDIS_APPENDONLY=True`) matching S1302 T3 sibling classification. **Chris commit-gate: RESOLVED** — audit committed and merged with `--admin` flag authorization + pin retired.

**Session close artifacts committed at S1305 close:**

```
docs/research/domains/memory/1305_memory_runtime_correctness_audit.md   [new]
docs/research/ARCHITECTURE_INDEX.md                                     [modified, v16 → v17]
docs/research/OPEN_ARCS.md                                              [modified, Group 1300 row + 2 reconciliation notes]
docs/handoffs/SESSION_1305_MEMORY_RUNTIME_CORRECTNESS.md                [new]
00-START-NEXT-SESSION.md                                                [modified, this file]
```

Handoff: `docs/handoffs/SESSION_1305_MEMORY_RUNTIME_CORRECTNESS.md`.

### S1399 IS THE NEXT MISSION — Group 1300 Canonical Summary (arc close)

Per parent doc `1300_memory_domain_scoping.md` §5 P6 slot + playbook §11.3 canonical summary template:

- **Scope:** **Group 1300 Canonical Summary** — bounded work (one session per playbook §11.3). NOT a re-audit. Consumes S1301-S1305 outputs and synthesizes.
- **Deliverables (per parent §5 P6 rationale + playbook §11.3 template):**
  - (a) Consolidated memory-subsystem shape map across all 6 in-scope categories (A Semantic Knowledge / B Personal-Adaptive / C Agent Working / D RAG Retrieval / E Docs Corpus / F Conversational-Thread; G delegated to Employee OS 1200s arc)
  - (b) Cross-cutting patterns discovered across children:
    - **F1** — provenance-filter drift class (S1301 §14.2 21.5% coverage gap + S1304 §14 D2 LRU staleness + D6 cadence unscheduled + S1305 §14 D1 LRU class extension)
    - **F2** — row-level orphan-write pattern (S1301 §14.3 D3 hypothesis + S1302 §14.3 F2 narrowed 11→7 fields + S1304 §14 D3 partial invalidation of D3)
    - **F3** — Redis-only durability + `@lru_cache` staleness pattern (S1302 §14 F4/F5 + §15 T3/T4 + S1304 §14 D2 + S1305 §14 D3/D4/D5/D8 + Cat H 4-DB isolation)
    - **F4** — F1/F4-CANDIDATE discipline as inheritance methodology (S1303 §14 F4-CANDIDATE + S1304 §14 D7 F4-CANDIDATE + S1305 §14 D6 F4-CANDIDATE + S1305 §14 D3 severity-correction extension)
  - (c) `PLATFORM_INVENTORY.md` §3 update recommendations:
    - §3.13 subdivision (per S1302 findings on Cat A/B/C internals)
    - §3.14 lane consolidation (per S1301 findings on `search_docs` LOCAL vs `kb_tool` PROD)
    - New §3.N row for Cat F Conversational/Thread Memory (per S1303 first-inventory landing)
    - New §3.N or §5 row for Cat H Runtime Memory Correctness (per S1305 first-inventory landing)
  - (d) Follow-on research queue (ranked by uncertainty × risk × unblocked flows):
    - S1305 §19 R1 platform_config F4-CANDIDATE full-tree verification (HIGH — blocks T10 remediation)
    - S1305 §19 R6 IntelligentJobMatcher production invocation audit (HIGH — routes T5 MemorySystem severity assessment)
    - S1304 §19 R1 `ingested_via` full-tree recheck (HIGHEST — F1-CANDIDATE hardening)
    - S1303 §19 R1.a/b/c F4-CANDIDATE verification (context_used + agent_results)
    - S1302 §15 T10 write-authority framework design-preparation (HIGH severity debt from S1302)
    - S1305 §19 R2 Cat H remediation design-preparation per surface per S1304 T2 option set (post-S1399)
    - S1305 §19 R4 Cat H ↔ Cat B integration lens (AgentLearningService Redis-only durability + TTL policy + DB writeback design)
  - (e) Cross-link back to Employee OS 1200s Cat G Mission Memory arc (delegated per parent §3G) + Group 1700 Observability arc delegations (filter-drop telemetry from S1301/S1304/S1305)
- **Anchors:** parent §5 P6 rationale + playbook §11.3 canonical summary template. Prior sibling summaries: none (Group 1300 is the first parent-with-children arc in the library that reaches xx99 stage; the S1268-S1272 arc predated the xx99 convention).
- **Rigby SIGN routing:** per playbook §15 stage table, canonical summaries require full SIGN with the 4 additional pressure-test questions (Q10-Q13: child contradictions correctly resolved, anchor-update recommendations complete, cross-cutting patterns not missed, follow-on queue rankings defensible).
- **Scope discipline (per playbook §11.3 + playbook §14):**
  - Bounded work — one session
  - NOT a re-audit — consumes prior child outputs
  - No sub-agent sweep — canonical summaries do NOT spawn 6-parallel Explore agents (parent-scoping doesn't either)
  - No implementation — synthesis only
  - Anchor-update recommendations are proposed here, applied in ARCHITECTURE_INDEX v17 → v18 bump commit or subsequent PR (per playbook §16 canonical summary rule)

### Two open decisions gating S1399 launch

- **D19 — S1399 launch cadence.** Immediate summary kickoff vs pause for Chris review of the 5-audit stack first. **Default lean: PROCEED** — S1301-S1305 pattern held (5 consecutive Chris commit-gates resolved between sessions, no stacking risk); canonical summary is bounded work and closes the arc cleanly.
- **D20 — Arc pin continuity.** Retain `pa-aa54193f240f4846` (default) vs rotate to fresh Group 1300 close pin. **Default lean: RETAIN** — the pin carries S1300 + S1301 + S1302 + S1303 + S1304 + S1305 mission-scope context that S1399 synthesizes across; rotating would lose the arc-carrying continuity. Pin retires at S1399 close on arc closure per OPEN_ARCS.md schema.

**FIRST THING S1399 open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1305 artifact set was committed to `main` between sessions — if yes, S1399 branches off `main`; if no, continues stacking on `docs/session-1305-memory-runtime-correctness`
4. Resolve D19 (launch cadence) + D20 (arc pin) with Chris via `pa-aa54193f240f4846`
5. If greenlit: create branch `docs/session-1399-memory-canonical-summary`
6. Create `docs/research/domains/memory/1399_memory_canonical_summary.md` per playbook §11.3 11-section canonical-summary template
7. Do NOT launch playbook §13 6-parallel-Explore sweep (canonical summaries consume prior outputs, they don't re-audit)
8. Feed S1301-S1305 audit outputs as source material — every finding cited MUST reference its child-audit §-anchor
9. **Apply F1/F4-CANDIDATE + severity-correction discipline** — the summary must preserve child-audit CANDIDATE status rather than resolving to CONFIRMED without §19 R1 verification
10. **Bounded scope:** synthesis + anchor-update recommendations + follow-on queue only. Do NOT re-audit. Do NOT open new drift findings.
11. **Route to Rigby with full SIGN + Q10-Q13 canonical-summary pressure-test questions** per playbook §15

---

## PA / Rigby context

- **Active arc pin:** `pa-aa54193f240f4846` (Group 1300 continuity — S1300 open through S1305 close).
- **Retired at S1305 close:** `pa-56a527a2c5528508` (S1305 SIGN isolation, retired via `session_tool.retire`, `updated_count: 2, retired: true`).
- **Retired earlier in Group 1300:** `pa-2614a91a920642fa` (S1304 SIGN isolation, retired at S1304 close per Chris discretion). `pa-23a38300dd84bae2` (S1303 SIGN isolation, retired at S1303 close). `pa-1b9f0f5264484c6b` (S1302 SIGN isolation, retired at S1302 close). `pa-a23736a833f646cf` (S1301 SIGN isolation, retired at S1301 close).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at S1399 open

- **Branch state (at S1305 close, before merge):** S1305 branch `docs/session-1305-memory-runtime-correctness` PR opened to `main`. If merged between sessions, working tree clean and S1399 branches off `main`.
- **Handoff continuity:** S1305 handoff at `docs/handoffs/SESSION_1305_MEMORY_RUNTIME_CORRECTNESS.md`. S1304 handoff at `docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md`. S1303 at `SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md`. S1302 at `SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md`. S1301 at `SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md`. S1300 at `SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. S1270-S1275 handoff-drift backfill remains deferred (Rigby default lean at S1300 close — skip; Chris did not override across S1300 → S1305).
- **ARCHITECTURE_INDEX version:** v17 (S1305 §1.20 + §8 timeline row added).

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1305 artifact set is on `main` — if yes, S1399 branches off `main`; if no, continues stacking
- [ ] Resolve D19 (S1399 launch cadence) + D20 (arc pin retention) with Chris via `pa-aa54193f240f4846`
- [ ] If greenlit: create branch `docs/session-1399-memory-canonical-summary`
- [ ] Create `docs/research/domains/memory/1399_memory_canonical_summary.md` per playbook §11.3 11-section template
- [ ] Do NOT launch playbook §13 6-parallel-Explore sweep (canonical summaries consume, not audit)
- [ ] Feed S1301-S1305 audit outputs as source material with §-anchor cites
- [ ] **Apply F1/F4-CANDIDATE + severity-correction discipline** — preserve child-audit CANDIDATE status
- [ ] **Bounded scope:** synthesis + anchor-update recommendations + follow-on queue only
- [ ] Route to Rigby with full SIGN + Q10-Q13 canonical-summary pressure-test questions per playbook §15
- [ ] Do NOT touch Category A/B/C internals (S1302 owns; cite adjacent findings only)
- [ ] Do NOT touch Category D internals (S1301 owns; cite lru_cache finding + retrieval mechanics)
- [ ] Do NOT touch Category E internals or E↔D boundary (S1304 owns)
- [ ] Do NOT touch Category F (S1303 owns)
- [ ] Do NOT touch Category G (delegated to Employee OS 1200s arc)
- [ ] Do NOT touch Category H (S1305 owns)

## Reference — where to look

- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **All 5 sibling audits (S1301-S1305):**
  - `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (Cat D)
  - `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` (Cat A+B+C)
  - `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` (Cat F)
  - `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` (Cat E↔D)
  - `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md` (Cat H)
- **S1305 handoff:** `docs/handoffs/SESSION_1305_MEMORY_RUNTIME_CORRECTNESS.md`
- **All 5 prior handoffs:** `docs/handoffs/SESSION_1301_*.md`, `SESSION_1302_*.md`, `SESSION_1303_*.md`, `SESSION_1304_*.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.3 canonical summary template, §14 evidence rules, §15 SIGN routing + Q10-Q13, §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md` (S1399 will propose §3 updates here)
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`
- **KNOWLEDGE_RAG_MEMORY narrative (S1158):** `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`
- **S1399 sweep starting hints (from child §19 downstream routing sections):**
  - S1305 §19 R1-R8 (Cat H follow-on queue)
  - S1304 §19 R1-R8 (Cat E↔D follow-on queue)
  - S1303 §19 R1.a/b/c through R8 (Cat F follow-on queue)
  - S1302 §19 downstream routing (Cat A/B/C)
  - S1301 §19 downstream routing (Cat D)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1399 anchor-update recommendations may motivate this refresh
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean at S1300 close
- Test count drift — minor, ignore unless writing tests
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 may propose narrative updates)
