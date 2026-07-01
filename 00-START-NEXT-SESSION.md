# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-donkeyking-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active pin is `pa-aa54193f240f4846`** ("Session 1300 — Memory research group (kickoff)"), preserved across S1300 close for S1301 continuity. Fresh at S1300 open — no S1270-S1275 turn context carried forward; mission scope only. **Retired at S1300 open:** `pa-cbcc410b32714f60` (Sessions 1270-1275 — symbol_mapping research chain: architecture / actor_identity / authority_enforcement / whole-platform inventory / cross-domain integration audit / DOMAIN_RESEARCH_PLAYBOOK / option_selection / event_schema_design; 6 research docs + 2 INDEX updates over 6 sessions; not health-scored because research-only sessions don't stress the tool surface). Use `tools/pa_local.sh` for all chats unless you have a reason to override.

## READ THIS SECOND — S1300 ENDED EARLY; S1301 IS FIRST CHILD AUDIT OF GROUP 1300

Session 1300 landed **only the Phase 0 parent-scoping doc** for Research Group 1300 (Memory / Knowledge / Embeddings). See `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`. Chris close directive was "mark the git pr as ended early for core research" — meaning the actual audit sweep (Category D RAG lanes, Categories A+B+C persistence, etc.) has NOT started. That's the S1301 open job.

### Group 1300 arc shape (locked at S1300 close)

```
S1300 (parent, complete — docs/research/domains/memory/1300_memory_domain_scoping.md)
  → S1301 RAG Retrieval Lanes (Category D)         ← YOUR NEXT MISSION
  → S1302 Memory Persistence Architecture (A + B + C)
  → S1303 Conversational / Thread Memory (Category F — no §3 row yet)
  → S1304 Documentation Corpus ↔ RAG Boundary (E ↔ D)
  → S1305 Runtime Memory Correctness (Category H narrow)
  → S1399 Group 1300 Canonical Summary (cross-cutting synthesis)
```

Category G (Employee OS Mission Memory) is **delegated to the Employee OS 1200s follow-up arc** — do NOT fold into Group 1300.

### Two open decisions gating S1301 launch

Chris did NOT answer these at S1300 close (session ended before greenlight):

- **D6 — S1301 launch cadence.** Immediate audit kickoff vs pause for Chris review of the parent doc first. **Default lean: PAUSE.** Rationale: parent doc is fresh; Chris review before P1 kickoff protects against sequencing regret.
- **D7 — Rigby SIGN routing on parent doc.** Skip vs light SIGN before P1 kickoff. **Default lean: SKIP** per playbook §9 (SIGN attaches to audits, not scoping).

**FIRST THING S1301 open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview`.
3. Ask Chris via the S1300 pin (`pa-aa54193f240f4846`) to resolve D6 + D7.
4. If Chris greenlights immediate S1301: begin playbook §11 opening sequence against `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md`, feeding the §6 provenance-filter finding from the parent doc as S1301 input.
5. Launch playbook §7 6-sub-agent sweep for Category D scope.

### Category D scope (S1301 RAG Retrieval Lanes)

From parent doc §3 (Category D):

- **Systems:** `core/rag_integration.py` (pgvector prod), `core/rag.py` (local Ollama keyword), `Document`, `DocumentEmbedding`, HNSW index, `ScopedRetrievalService`, `RAGObservabilityService`, `search_docs` PA tool, provenance filter mechanics.
- **Anchor:** S1273 §3.14 + §5.4 (2-lane concern).
- **Live symptom:** At S1300 open Rigby ran `search_docs` twice against OpsRun/MissionRunner/JobContract terms and got:
  ```
  pre_filter_count: 8
  excluded_missing_provenance: 7
  excluded_mismatch: 1
  result_count: 0
  ```
  100% of semantically-matched candidates dropped via provenance filter. **This is the S1301 audit's live entry point** — trace why + document the class + propose remediation surface (not implementation).

### Audit questions to answer (playbook §4 subset, tailored)

Do NOT re-run all 28 playbook questions — this is a child audit under a parent that already answered arc-level structure. Focus on Category D specifically:

1. What triggers `excluded_missing_provenance`? Is provenance metadata populated at ingestion or synthesized at query time?
2. What triggers `excluded_mismatch` on `originating_session`? Is the session filter meant to exclude cross-session material by default?
3. How does the two-lane split (§5.4) affect provenance? Does `core/rag.py` local lane have the same filter?
4. Is this the same class as S1142 chunk-coverage gap (852 / 14,149 chunks — S1273 §3.13 known drift)?
5. Under what queries does the platform silently return 0 results despite semantic matches existing? What is the operator-facing error surface?
6. What is the 2-lane call-time selector research question flagged in playbook §12 §3.13 note?

---

## PA / Rigby context

- **Active pin:** `pa-aa54193f240f4846` (S1300 fresh — carries mission scope only, no S1270-S1275 turn context).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.

## Repo state at S1301 open

- **Branch state:** S1300 branch `docs/session-1300-memory-research-group-parent-scoping` opened as PR stacked on S1275 branch (#2773). PR body marked "ended early for core research." Should be reviewed/merged before S1301 opens a new branch, OR S1301 stacks on S1300.
- **Handoff drift:** S1270-S1274 landed as research docs without formal `SESSION_1270_*.md` through `SESSION_1274_*.md` handoffs. Rigby's default lean at S1300 close: skip backfill (research-only sessions may intentionally skip). Chris did NOT override at S1300 close. Note: `SESSION_1275_SYMBOL_MAPPING_EVENT_SCHEMA_DESIGN.md` DOES exist on the S1275 branch (upstream of S1300 PR).
- **ARCHITECTURE_INDEX version:** v9 (S1300 §1.13 parent scoping doc registered). S1275 branch also claims v8 with §1.12 — merge order determines final v9/v10 version numbers.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Resolve D6 (S1301 launch cadence) + D7 (Rigby SIGN on parent) with Chris via `pa-aa54193f240f4846`
- [ ] If greenlit: create branch `docs/session-1301-memory-rag-retrieval-lanes` off S1300 branch (or main if S1300 PR merged)
- [ ] Create `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` per playbook §5 20-section template
- [ ] Launch playbook §7 6-sub-agent sweep for Category D scope
- [ ] Feed §6 provenance-filter finding as S1301 input
- [ ] Do NOT touch Categories A/B/C/E/F/H (they have dedicated child audits later)
- [ ] Do NOT touch Category G (delegated to Employee OS 1200s follow-up)

## Reference — where to look

- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **S1300 handoff:** `docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§7 sub-agent sweeps, §11 opening sequence)
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.13/§3.14/§3.15/§5.4
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Cross-domain audit:** `docs/research/platform/cross_domain_integration_audit.md`

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh
- Handoff numbering continuity — legitimate; S1270-S1274 skipped by intent per Rigby lean
- Test count drift — minor, ignore unless writing tests
