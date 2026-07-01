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

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1399 merge:**

- **Retiring on Chris commit-gate + merge:** `pa-aa54193f240f4846` ("Session 1300 — Memory research group (kickoff)") — Group 1300 arc pin. Carried S1300 → S1301 → S1302 → S1303 → S1304 → S1305 → S1399 continuity. Retires on arc close per OPEN_ARCS schema. Verify via `session_tool.retire conversation_id=pa-aa54193f240f4846`.
- **Also retiring on merge:** `pa-4fc3329d0db6484f` — S1399 SIGN isolation pin (Rigby SIGN-clean cycle 1 High confidence, 0 must-fix). Verify via `session_tool.retire`.
- **Next arc pin:** to be minted at Group 1400 Revenue open (default lean per playbook §22 queue) OR at whichever single-child follow-on Chris opens instead. If Group 1400: propose short-command opening pin like `pa-<hex>` titled "Session 1400 — Revenue research group (kickoff)". Update `tools/pa_local.sh` header + memory rule `feedback_pa_chat_local_override.md` after mint.

Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — GROUP 1300 CLOSED (pending Chris merge); NEXT ARC IS GROUP 1400 REVENUE (default lean)

Session 1399 landed the **first formal xx99 canonical summary in the library** — `docs/research/domains/memory/1399_memory_canonical_summary.md`, 1224 lines, `status: draft`, `sign_status: SIGN-clean cycle 1 High confidence`. Rigby SIGN cycle 1 on fresh isolation pin `pa-4fc3329d0db6484f` returned **SIGN-clean High confidence, 0 must-fix**, 1 optional nice-to-have (docs↔code naming/category drift micro-pattern acknowledged as §4.5 adjacent evidence rather than promoted to formal F5 — Rigby explicitly said "not required if you want to keep exactly four"; parent §5 P6 rationale preserved). **Group 1300 arc closes on Chris commit-gate + merge.** ARCHITECTURE_INDEX v17 → v18 bump + §1.21 row + §8 timeline S1399 row applied same-commit per playbook §16 canonical-summary rule.

**Session close artifacts committed at S1399 close:**

```
docs/research/domains/memory/1399_memory_canonical_summary.md   [new, 1224 lines]
docs/research/ARCHITECTURE_INDEX.md                             [modified, v17 → v18]
docs/research/OPEN_ARCS.md                                      [modified, Group 1300 row + 2 reconciliation notes]
docs/handoffs/SESSION_1399_MEMORY_CANONICAL_SUMMARY.md          [new]
00-START-NEXT-SESSION.md                                        [modified, this file]
```

Handoff: `docs/handoffs/SESSION_1399_MEMORY_CANONICAL_SUMMARY.md`.

### NEXT-SESSION MISSION — Group 1400 Revenue (default lean per playbook §22 queue)

Per playbook §22 queue + OPEN_ARCS.md Not-started section:

- **Default lean.** Open Group 1400 Revenue via `start research group 1400` short command. Rigby caught this as a missed inventory row in S1273 review; business-value highest under-researched domain.
- **Alternative single-child follow-ons** ranked from S1399 §8.2 top 5 (Chris picks if not doing Group 1400 yet):
  1. **S1304 §19 R1 `ingested_via` full-tree recheck** — F1-CANDIDATE hardening. 3 known write sites (`sync_docs_index_to_documents.py:394`, `core/tasks_agents.py:4223/4290/4351`, `content/embeddings.py:654/753`); requires owner-model-qualified enumeration of every `DocumentEmbedding` consumer (not just keyword grep of `ingested_via`). Unblocks S1304 T5 wire-or-deprecate decision + §17 provenance-system reconciliation design + DB migration to remove field if truly orphan.
  2. **S1303 §19 R1.a/b/c `ChatConversation.context_used` + `.agent_results` verification.** Three sub-questions in order: R1.a owner-model-qualified consumer inventory; R1.b runtime-vs-analytics-vs-UI classification; R1.c canonical-source-of-truth resolution (first-class fields vs `metadata` dict). Do R1.a first — determines whether any dead-code claim is permissible.
  3. **S1305 §19 R1 `platform_config` LRU F4-CANDIDATE mutation-path audit.** Determine whether Django admin / raw ORM / mgmt-command paths mutate `ProjectWorkspace` + `UnifiedUser` without routing through setters at `platform_config.py:252, :269`. Blocks T10 remediation.
  4. **S1305 §19 R6 `IntelligentJobMatcher` production invocation audit.** Rigby SIGN cycle 1 confirmed `MemorySystem` IS instantiated at `ai_core/agents/intelligent_job_matcher.py:57`. Remaining question: is `IntelligentJobMatcher` production-invoked? If yes → T5 MemorySystem severity HIGH; if orphan/experimental/test-only → T5 LOW. Cheap 1-hour investigation. Adjacent: `SharedMemorySystem` at `intelligence/shared_memory.py` used by `live_learning_orchestrator.py` + `command_center_ai.py` + 4 other sites.
  5. **S1302 §15 T10 write-authority framework design-preparation ADR.** Highest-severity debt in Group 1300 arc — no auth gate on `AgentMemory.create_memory:11004`; MemoryPromotionService auto-saves on every PA turn without rate limiting. Design-preparation phase work per playbook §14.5 (implementation-in-research forbidden). Cross-arc anchor for a permission model + rate limiting + audit trail shape.

### Two open decisions gating next-session launch

- **D21 — Next-arc launch.** (i) Group 1400 Revenue (default lean); (ii) single-child follow-on from S1399 §8.2 top 5 above; (iii) parallel — open Group 1400 AND run T10 ADR concurrently. **Default lean: OPEN GROUP 1400.** Rigby-caught missed inventory + business value + playbook §22 queue default.
- **D22 — Arc pin mint.** Fresh pin required for Group 1400. Propose short title "Session 1400 — Revenue research group (kickoff)" mirroring S1300's title pattern. Retire retirement pins BEFORE minting new arc pin to keep `tools/pa_local.sh` clean.

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`
3. Check if S1399 artifact set was committed to `main` between sessions — if yes, next session branches off `main` (not stacked on S1399)
4. Verify `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` retirement status via `session_tool` (should be retired post-Chris merge)
5. Resolve D21 (next-arc launch) + D22 (arc pin mint) with Chris via the newly-minted arc pin
6. If Group 1400 greenlit: create branch `docs/session-1400-revenue-research-group` + `docs/research/domains/revenue/1400_revenue_domain_scoping.md` per playbook §11.1 parent-scoping template
7. If single-child follow-on greenlit: create branch `docs/session-NNNN-<slug>` + audit doc per playbook §11.2 20-section audit template
8. Playbook §13 6-parallel-Explore sweep for domain audits; NOT for canonical summaries
9. Route to Rigby with full SIGN per playbook §15 stage table

---

## PA / Rigby context

- **Arc pin at session start:** `pa-aa54193f240f4846` (Group 1300 continuity — retires on Chris merge of S1399 PR).
- **S1399 SIGN pin:** `pa-4fc3329d0db6484f` (SIGN-clean cycle 1 High confidence; retires on Chris merge).
- **Retired earlier in Group 1300:** `pa-56a527a2c5528508` (S1305 SIGN, retired at S1305 close). `pa-2614a91a920642fa` (S1304 SIGN). `pa-23a38300dd84bae2` (S1303 SIGN). `pa-1b9f0f5264484c6b` (S1302 SIGN). `pa-a23736a833f646cf` (S1301 SIGN).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin). Update pin references after Group 1300 arc close.
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at next-session open

- **Branch state (at S1399 close, before merge):** `docs/session-1399-memory-canonical-summary` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1399 handoff at `docs/handoffs/SESSION_1399_MEMORY_CANONICAL_SUMMARY.md`. Prior handoffs: SESSION_1300 through SESSION_1305 for Group 1300 arc.
- **ARCHITECTURE_INDEX version:** v18 (S1399 §1.21 + §8 timeline row added).
- **OPEN_ARCS state:** Group 1300 row in "In-progress" section pending Chris commit-gate. Post-merge, move to "Closed" section with closure reconciliation note. Group 1400 Revenue in "Not started" section becomes eligible as `in-progress` on Chris D21 verdict.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Check if S1399 artifact set is on `main` — if yes, next session branches off `main`; if no, continues stacking on `docs/session-1399-memory-canonical-summary`
- [ ] Verify `pa-aa54193f240f4846` (arc) + `pa-4fc3329d0db6484f` (SIGN) retirement status via `session_tool`
- [ ] Post-merge cleanup: update `tools/pa_local.sh` header + `feedback_pa_chat_local_override.md` memory rule with next-arc pin placeholder
- [ ] Move OPEN_ARCS.md Group 1300 row from In-progress to Closed section with closure reconciliation note
- [ ] Resolve D21 (next-arc launch: Group 1400 Revenue default lean vs single-child follow-on vs parallel) + D22 (arc pin mint) with Chris via newly-minted arc pin
- [ ] If Group 1400 greenlit: create branch `docs/session-1400-revenue-research-group` + parent scoping doc at `docs/research/domains/revenue/1400_revenue_domain_scoping.md` per playbook §11.1 template
- [ ] If single-child follow-on greenlit: create branch + audit doc per playbook §11.2 20-section template + launch §13 6-parallel-Explore sweep
- [ ] Route to Rigby with full SIGN per playbook §15 stage table (light for parent scoping; full for audits; Q10-Q13 for canonical summaries)

## Reference — where to look

- **Group 1300 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` — start here for anything memory-related
- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **All 5 child audits + S1399 canonical summary:**
  - `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (Cat D)
  - `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` (Cat A+B+C)
  - `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` (Cat F)
  - `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` (Cat E↔D)
  - `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md` (Cat H)
  - `docs/research/domains/memory/1399_memory_canonical_summary.md` (canonical summary)
- **S1399 handoff:** `docs/handoffs/SESSION_1399_MEMORY_CANONICAL_SUMMARY.md`
- **All 6 prior handoffs:** `docs/handoffs/SESSION_1300_*.md` through `SESSION_1305_*.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent-scoping template, §11.2 20-section audit template, §11.3 canonical summary template, §13 6-parallel-Explore sweep, §14 evidence rules, §15 SIGN routing, §16 commit policy, §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v18:** `docs/research/ARCHITECTURE_INDEX.md` — §1.21 for S1399 summary + §8 timeline
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1300 row + Not-started queue
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Whole-platform architecture inventory:** `docs/research/platform_architecture_inventory.md` — apply S1399 §7 anchor-update recommendations (§3.13 subdivision + §3.14 lane consolidation + new Cat F/H rows) in a subsequent PR
- **KNOWLEDGE_RAG_MEMORY narrative:** `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` — apply S1399 §7.4.2 4 targeted edits in a subsequent PR

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1399 §7.1 explicitly does NOT propose direct edits, so this may be stale until Chris regenerates
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean at S1300 close; S1306-S1398 skipped by intent (Chris directive at S1300 lock: "Plan for a 1399 canonical summary once the 1300-series research is complete")
- Test count drift — minor, ignore unless writing tests
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1399 §7 proposes narrative updates for a subsequent PR)
- ARCHITECTURE_INDEX v18 update includes S1399 explicit closure signal — next arc can open cleanly
