---
session: 1305
status: closed (draft-audit landed, Rigby SIGN-clean after cycles 1 + 2, Chris commit-gated + pin retired → committing)
date: 2026-07-01
arc: Research Group 1300 (Memory / Knowledge / Embeddings) — child P5 (playbook §11.2 20-section audit template). **Fifth (and final) child audit** under the parent-with-children arc. **Closes the 5-child arc** (S1301 Cat D + S1302 Cat A+B+C + S1303 Cat F + S1304 Cat E↔D + S1305 Cat H). Category H Runtime Memory Correctness NARROW scope per parent §5 P5 slot — Redis-loss on worker recycle + `@lru_cache(1)` staleness drift class only. Explicitly OUT of scope: system RAM, macOS SIGSEGV, Celery worker RSS, PID cache, ops-flavored infrastructure. Explicitly OUT: Cat A/B/C/D/E/F/G internals (owned by sibling audits — MAY be cited as adjacent evidence but NOT re-audited). Inherits S1304 §14 D2 lru_cache staleness gap + §14 D6 provenance rebuild cadence unscheduled + §15 T2 remediation options as first-order scope evidence; S1302 §14 F4/F5 + §15 T3/T4 AgentLearningService Redis-only durability + hardcoded 14-day freshness cutoff as adjacent evidence; S1303 §14 F4-CANDIDATE + S1304 verifier-loop hypothesis-correction pattern extended to severity-correction.
prs_merged: []
prs_open:
  - "S1305 audit + INDEX v17 + OPEN_ARCS + handoff + START-NEXT rotation (branch docs/session-1305-memory-runtime-correctness off main; Chris commit-gate resolved this session → PR opens on push)"
prs_upstream:
  - "S1304 commit-gate on main (PR #2779 = 4271e913) — resolved between S1304 close and S1305 open; S1305 branches off main, not stacked on S1304"
branches_open:
  - "docs/session-1305-memory-runtime-correctness (base = origin/main)"
companions:
  - docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md
  - docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md
  - docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md
  - docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md
  - docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md
  - docs/research/domains/memory/1300_memory_domain_scoping.md
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md
  - docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md
  - docs/research/domains/memory/1305_memory_runtime_correctness_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
deliverables:
  - "docs/research/domains/memory/1305_memory_runtime_correctness_audit.md (~1080 lines, status: draft, sign_status: SIGN-clean, authority: research, research_group: 1300, child_slot: P5, category: H, domain_slug: memory; 20-section playbook §11.2 template; verifier_loop v0.1 pre-SIGN corrections + v0.2 SIGN cycle 1 3-must-fix fold + cycle 2 verification pass — SIGN-clean)"
  - "docs/research/ARCHITECTURE_INDEX.md — v16 → v17; §1.20 row added; §8 timeline S1305 row added; frontmatter last_verified bump; owner-line updated with v17 entry"
  - "docs/research/OPEN_ARCS.md — Group 1300 in-progress row current-child advanced from 'S1304 SIGN-clean (commit-gated) + S1305 queued' to 'S1305 SIGN-clean (committed) + S1399 canonical summary queued'; state annotation 'in-progress (awaiting S1399 canonical summary)'; 2 reconciliation notes added (S1305 open, S1305 close); next-expected pointer rotated to Group 1300 Canonical Summary; **5-child arc complete**"
  - "docs/handoffs/SESSION_1305_MEMORY_RUNTIME_CORRECTNESS.md (this doc)"
  - "00-START-NEXT-SESSION.md — rotated to S1399 mission spec (Group 1300 Canonical Summary per playbook §11.3 template — bounded synthesis, NOT re-audit)"
key_findings:
  - "**FIRST LIBRARY AUDIT to explicitly downgrade a sub-agent severity claim via sibling-inherited context — extends verifier-loop pattern from hypothesis-correction (S1304 partial invalidation of S1301 §19 D3) to severity-correction.** Agent 6 sweep produced a CRITICAL severity classification for `AgentLearningService` Redis-only durability (§14 D3 pre-fold). Parent-agent verifier-loop applied Redis AOF context reading: `settings.py:944 REDIS_APPENDONLY=True` + `:945 REDIS_APPENDFSYNC='everysec'` establishes Redis persistence survives Redis process restart. Loss on Python-worker recycle is only the in-memory `_user_memories` dict delta between last `save_memory()` and recycle — not the durably-persisted preferences. This matches S1302 T3 sibling classification (MEDIUM). Downgraded to MEDIUM pre-SIGN with rationale logged in §20.5 conflicts + §20.6 verifier-loop corrections. Rigby SIGN cycle 1 ratified the downgrade (did not push back). Sets library pattern: verifier-loop applies to severity assertions from sub-agents, not just hypothesis assertions."
  - "**§7.2 gap (a) — AgentLearningService within-process consistency bug CONFIRMED via direct file:line read + Rigby SIGN cycle 1 reinforcement.** `get_user_memory` at `core/services/agent_learning_service.py:410-425`; line :415 `if key in self._user_memories: return self._user_memories[key]` short-circuits BEFORE Redis on hit. `save_memory` at `:462-483`; iterates `memory.long_term.items()` at :473; writes `redis_client.hset(prefs_key, pref_key, json.dumps(pref.to_dict(), default=str))` at :476-479. Grep across full file for `self._user_memories.clear`, `del self._user_memories`, or any dict-mutation on the save path = **0 hits**. After `save_memory()` writes Redis, `_user_memories` still holds pre-save AgentMemory object. Next `get_user_memory()` on same user-agent key returns STALE dict entry. **Distinct from S1302 T3 cross-process recycle-loss.** §14 D4 S1305-new + §15 T4 debt."
  - "**4 `@lru_cache(maxsize=1)` sites in `core/services/` grep-verified 2026-07-01:** `_load_provenance_docs` at `td_handlers_ops.py:78` (S1304 D2 anchor); `_cached_primary_workspace_id` at `platform_config.py:89`; `_cached_primary_user_id` at `platform_config.py:133`; `_load_config` at `fleet_routing.py:64`. Only `platform_config` pair has explicit invalidation contract (`clear_config_cache()` at `:223`); other two rely on worker-restart discipline. §14 D7 S1305-new (LRU staleness class extension of S1304 D2). §14 D6 F4-CANDIDATE per S1303 §14 discipline: `platform_config` LRU depends on setter-routing through `clear_config_cache()` — Django admin / raw ORM / mgmt-command paths NOT verified as routing through setters; requires §19 R1 owner-model-qualified consumer inventory."
  - "**5 production `cache.set(..., timeout=None)` sites within scope after Rigby SIGN cycle 1 tightening:** `core/tasks.py:5936` (docs corpus index hash); `core/memory_system.py:54` (memory index); `:55` (embedding index); `:176` (embedding data); `core/services/discord_bot.py:9723,9728` (Discord bot config). Full 11-file repo grep enumerated at §3 excluded-from-count table with 6 excluded categories: subprocess-timeouts (`views_video.py:47`, `video_editing_service.py:105` `_run_ffmpeg` kwargs, NOT cache calls); test-only (7 sites in `core/tests/test_refresh_docs_corpus.py` + `tests/test_db_health_client_env.py` + `tests/services/conftest.py`); mock fallback (`ai_core/unified_job_search.py:21` — `MockCache.set(key, value, timeout=None)` stub inside try/except cache-import guard, NOT a real cache-set); archive (`archive/scripts/activate_full_system.py:362`, `archive/scripts/verify_agent_tools_and_spiders.py:219` — deprecated per DOC_LIFECYCLE). §14 D10 + §15 T5."
  - "**§14 D5 S1305-new — `MemorySystem` index → data divergence risk.** `core/memory_system.py:54-55` writes `memory_index` + `embedding_index` with `timeout=None`; `:176` writes embedding data with `timeout=None`. Redis `REDIS_MAXMEMORY_POLICY='allkeys-lru'` (settings.py:942) will evict per-key entries under memory pressure. Index at `:133` (`for key in self.memory_index`) can list evicted keys. `retrieve_memory` at `:106` returns None on eviction — no error surfaced to caller. Rigby SIGN cycle 1 grep confirmed `MemorySystem` IS actively used: 9 files reference `MemorySystem(` or `SharedMemorySystem` / `AIMemorySystem` cousins; direct instantiation at `ai_core/agents/intelligent_job_matcher.py:57 self.memory = MemorySystem()`. Closes parent §3H open question 'is MemorySystem used'. **§19 R6 reshaped post-SIGN cycle 1**: from 'verify MemorySystem is used' (answered: yes) to 'verify IntelligentJobMatcher production invocation paths' — routes T5 severity assessment."
  - "**§14 D8 S1305-new — Disjoint 4-DB Redis topology CONFIRMED.** DB 1 (Django cache at `settings.py:452 'BACKEND': 'django.core.cache.backends.redis.RedisCache', LOCATION: REDIS_URL` = `redis://localhost:6379/1` per `:448`); DB 2 (Celery broker at `:802 CELERY_BROKER_URL = 'redis://localhost:6379/2'`); DB 3 (Celery results at `:803`); DB 5 (`AgentLearningService` at `agent_learning_service.py:145 'db': 5` hardcoded). `django.core.cache.cache.clear()` operates on Django cache backend only (DB 1). `AgentLearningService` uses `self.redis_client = redis.Redis(**self.redis_config)` at `:160` — raw redis client on DB 5, BYPASSING Django cache framework entirely. Consequence: `cache.clear()` from ops tooling has zero effect on DB 5 preferences state. Cross-DB flush requires explicit `redis-cli -n 5 FLUSHDB` or `FLUSHALL`. `docs/topics/infrastructure.md` says '3 distinct Redis DBs' — doc drift (§14 D9). Agent 6 sweep initially claimed '3 disjoint DBs' — verifier-loop caught the missed Celery broker DB 2 + results DB 3 split before folding."
  - "**Closes parent §3H 3 open questions:** (i) `search_docs` cache location — parent §3H bullet 'search_docs `lru_cache(1)` per-process' is imprecise; `search_docs` handler at `td_handlers_ops.py:5468` has NO dedicated LRU cache; the LRU is on `_load_provenance_docs` called from `search_docs` when `originating_session` filter is set; §15 T12. (ii) `MemoryPromotionService` runtime cache — Agent 2 verified pure DB I/O; 0 hits for `@lru_cache`, `@cached_property`, or module-level memoization; NO Cat H concern. (iii) `MemorySystem` active-use status — YES, active per §14 D5 above."
  - "**Per-surface maturity verdicts (playbook §12 bounded language, S1274 continuous-language rule applied):** `EmbeddingService` STABLE (bounded 7-day TTL via `CACHE_TTL = 7 * 86400` at `embedding_service.py:80`; deterministic contract per :80 comment — same text+model returns same vector; cache-key includes model name preventing cross-version pollution); `platform_config` LRU pair WORKING (invalidation contract explicit via `clear_config_cache()` at `:223`; race window narrow only when non-setter mutation paths); `_load_provenance_docs` PARTIAL (works when combined with worker-restart discipline; no automation); `AgentLearningService` PARTIAL (works when Redis healthy; degrades silently on cross-process race AND within-process staleness per §7.2 gap (a)); `MemorySystem` EXPERIMENTAL (unbounded index + no lifecycle hook; index → data divergence possible under LRU eviction); `fleet_routing._load_config` PARTIAL (deploy-restart contract; test-only invalidation). Category H as a whole: **WORKING with drift** — none of the surfaces have shipped correctness incidents that ping ops (no known SEV-1 attributable to Cat H staleness), but the S1300 §6 empirical finding (8 → 0 excluded chunks) demonstrates the drift can silently degrade user-visible output."
  - "**§19 downstream routing:** R1 `platform_config` LRU D6 F4-CANDIDATE verification per S1303 §14 discipline (owner-model-qualified consumer inventory for Django admin / raw ORM / mgmt-command mutation paths — HIGH priority, blocks T10 remediation); R2 Cat H remediation design-preparation per surface per S1304 T2 option set (worker-restart trigger vs file-watcher vs Redis-queryable vs TTL) → post-S1399, ideally under a Group 1300 follow-on design track (HIGH); R3 beat-schedule audit for cache-refresh cadence gaps beyond `build_docs_provenance` (extends S1304 D6 pattern to a class of drift) (MEDIUM); R4 Cat H ↔ Cat B integration lens — `AgentLearningService` Redis-only durability + TTL policy + DB writeback design decision (high-leverage: fixes T3 + T4 + T7 together; user-visible correctness impact) (MEDIUM-HIGH); R5 worker-recycle instrumentation — emit metric on cache-repopulation events; alert if repopulation rate exceeds threshold → **delegate to Group 1700 Observability** (MEDIUM); R6 `IntelligentJobMatcher` production invocation audit (post-Rigby-cycle-1-reshape — routes T5 severity assessment) (MEDIUM); R7 full `@lru_cache` sweep across `core/`, `ai_core/`, `content/` — verify no correctness-critical in-process caches exist outside the 4 audited sites (LOW-MEDIUM); R8 doc-drift fix on Redis DB count `docs/topics/infrastructure.md` 3 → 4 (LOW)."
open_decisions_carried_forward:
  - "S1305 SIGN isolation pin `pa-56a527a2c5528508` retirement — **RESOLVED** at S1305 close per Chris directive `commit + retire pin`. Verified: `session_tool.retire` returned `updated_count: 2, retired: true` at 2026-07-01."
  - "S1399 launch cadence — playbook default is 'immediate on session open'. Since S1305 commit-gate resolves this session via 'commit + retire pin' directive, S1305 artifacts land on `main` before S1399 open. S1399 branches off `main` (not stacked)."
  - "S1399 arc pin `pa-aa54193f240f4846` retention — default lean RETAIN through arc close (S1399); pin carries full Group 1300 context S1399 synthesizes across. Retire at S1399 close on arc closure per OPEN_ARCS.md schema."
rigby_sign_cycle_1:
  verdict: SIGN-with-edits
  confidence: Medium
  pin: pa-56a527a2c5528508 (fresh isolation, ownership-verified via memory rule feedback_pa_local_verify_ownership.md)
  must_fix_count: 3
  folds_applied:
    - "F1 — §3 + §14 D10 `cache.set(timeout=None)` scoping tightened. Rigby grep found 11 total files with `timeout=None`; audit's bare '5 sites' claim was under-specified. Fold: added explicit scope definition (`core/` runtime excl. tests + subprocess-timeouts + archive + mock fallbacks) at §3; added excluded-from-count table enumerating all 6 excluded categories; `ai_core/unified_job_search.py:21` identified as MOCK-class fallback and correctly excluded; `archive/scripts/*` (2 sites) enumerated as deprecated."
    - "F2 — §7.2 gap (a) direct code evidence reinforcement. Rigby asked for citation confirming within-process staleness bug or documentation of an invalidation path Claude missed. Fold: verified `agent_learning_service.py:410-425` (get_user_memory :415 short-circuit) + :462-483 (save_memory :476 Redis-only write) + grep for `self._user_memories.clear` / `del self._user_memories` (0 hits). CONFIRMED as real bug; direct file:line citations added inline in §7.2 step 7."
    - "F3 — §14 D8 Redis DB isolation citation strengthening. Rigby asked for one concrete citation showing DB selection and `cache.clear()` scope. Fold: added `settings.py:452 BACKEND` + `LOCATION` cite + `agent_learning_service.py:160` raw `redis.Redis()` client-instantiation cite. Explicit statement that `django.core.cache.cache.clear()` operates on Django backend only (DB 1), while AgentLearningService raw redis client on DB 5 is fully bypassed."
  bonus_fold:
    - "§19 R6 reshape + §20.4 UNKNOWN 4 resolution. Rigby confirmed `MemorySystem` IS actively used at `ai_core/agents/intelligent_job_matcher.py:57`. R6 reshaped from 'verify MemorySystem is used' (answered: yes) to 'verify IntelligentJobMatcher production invocation paths' (routes T5 severity assessment). Same effort budget, higher-leverage question."
  ratifications:
    - "Biggest architectural risk: `MemorySystem` index → data divergence under Redis eviction (D5 + T5) — Rigby independently identified same risk Claude flagged."
    - "Most important next research: §19 R6 IntelligentJobMatcher invocation audit (post-reshape)."
    - "S1305 §14 D3 severity downgrade (Agent 6 CRITICAL → MEDIUM per Redis AOF context) — Rigby did NOT push back; ratified as sibling-inheritance discipline."
rigby_sign_cycle_2:
  verdict: SIGN-clean
  confidence: High
  pin: pa-56a527a2c5528508 (same pin, verification-only pass)
  must_fix_count: 0
  optional_micro_tighten:
    - "§3 excluded-from-count table row rendering for `ai_core/unified_job_search.py:21` — Rigby saw truncation in her tool output (tool-side, not source-file-side) and suggested full-inline rendering. NOT blocking SIGN. Fold deferred to Chris commit-gate discretion."
  ratifications:
    - "All three cycle-1 must-fix folds landed correctly and are grep-survivable."
    - "§19 R6 reshape correct and higher-leverage."
    - "S1304 D1 + D2 (LRU staleness + rebuild cadence) remains biggest architectural risk (unchanged from cycle 1)."
    - "Overall confidence: High."
2_cycle_pattern:
  matches:
    - "S1303 (2 cycles, SIGN-clean High)"
    - "S1304 (2 cycles, SIGN-clean)"
  contrast:
    - "S1301 (1 cycle, SIGN-clean)"
    - "S1302 (3 cycles, SIGN-clean)"
  cause: "Well-scoped verifier-loop pre-corrections (Agent 6 severity + count + DB topology + Agent 1/2 conflict on search_docs cache) + sibling-inheritance discipline let cycle 1 focus on substantive-scope edits (scope tightening, direct-code-evidence citation, isolation citation strengthening) rather than factual corrections."
group_1300_arc_state_at_S1305_close:
  child_audits_complete: 5
  child_audits_shipped_sign_clean:
    - S1301 (Cat D, PR #2775 + #2776)
    - S1302 (Cat A+B+C, PR #2777 = c053272a)
    - S1303 (Cat F, PR #2778 = 6365f33f)
    - S1304 (Cat E↔D, PR #2779 = 4271e913)
    - S1305 (Cat H, PR pending push)
  categories_covered: [A, B, C, D, E, F, H]
  category_delegated: G (Employee OS 1200s arc)
  arc_state: "in-progress (awaiting S1399 canonical summary)"
  next: "S1399 Group 1300 Canonical Summary — bounded work (one session per playbook §11.3)"
chris_commit_gate: RESOLVED (2026-07-01)
chris_commit_gate_directive: "commit + retire pin"
pin_retirement:
  action: "session_tool.retire conversation_id=pa-56a527a2c5528508"
  result: "{updated_count: 2, retired: true}"
  timestamp: 2026-07-01
rigby_arc_pin_state:
  active: pa-aa54193f240f4846 (Group 1300 continuity — S1300 → S1305 close, expected through S1399)
  retired_at_S1305_close: pa-56a527a2c5528508 (S1305 SIGN isolation)
methodology_extension:
  name: "Severity-correction via sibling-inheritance"
  precursor: "S1304 partial invalidation of S1301 §19 D3 (hypothesis-correction via verifier-loop)"
  extension: "S1305 §14 D3 downgrade of Agent 6 CRITICAL → MEDIUM (severity-correction via Redis AOF context + S1302 T3 sibling classification match)"
  library_impact: "Verifier-loop pattern now applies to (a) sub-agent hypothesis claims (S1304 pattern) AND (b) sub-agent severity classifications (S1305 pattern). Rigby SIGN cycles focus on substantive additions rather than upstream evidence/severity corrections."
next_session_expected_first_action:
  - "context-kit orient"
  - "Confirm service_context: local via platform_config_tool overview"
  - "Verify S1305 artifacts on main; if yes, branch off main"
  - "Resolve D19 (S1399 launch cadence) + D20 (arc pin retention) via pa-aa54193f240f4846"
  - "If greenlit: create branch docs/session-1399-memory-canonical-summary"
  - "Create docs/research/domains/memory/1399_memory_canonical_summary.md per playbook §11.3 11-section template"
  - "Do NOT launch playbook §13 6-parallel-Explore sweep (canonical summaries consume prior outputs)"
  - "Feed S1301-S1305 audit outputs as source material with §-anchor cites"
  - "Apply F1/F4-CANDIDATE + severity-correction discipline"
  - "Bounded scope: synthesis + anchor-update recommendations + follow-on queue only"
  - "Route to Rigby with full SIGN + Q10-Q13 canonical-summary pressure-test questions per playbook §15"
---

# Session 1305 — Memory / Group 1300 P5 Child Audit (Category H Runtime Memory Correctness) — Close

> **What this handoff is.** The close artifact for the fifth (and final) child audit under Research Group 1300 Memory. Session 1305 landed `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md` at ~1080 lines with `sign_status: SIGN-clean` (Rigby cycles 1 + 2 complete via fresh isolation pin `pa-56a527a2c5528508`, retired at close). Chris commit-gate resolved this session via directive `commit + retire pin`. **Closes the 5-child arc** (S1301 through S1305) — Group 1300 now awaits S1399 canonical summary.

## Session shape

1. **Open** — Chris invoked `Start research group 1305` via Research OS §5 short command. `context-kit orient` confirmed source-of-truth chain + latest handoff SESSION_1304 as prior close. `service_context: local` confirmed via `platform_config_tool overview`. Repo on `main` at commit `4271e913` (S1304 close) with clean working tree.
2. **Decision card** — D14 (launch cadence PROCEED) + D15 (arc pin RETAIN `pa-aa54193f240f4846`) presented with default leans. Chris ratified via `agree all`. Branch `docs/session-1305-memory-runtime-correctness` created off `main`.
3. **Scaffold** — Audit doc scaffolded per playbook §11.2 20-section template with `sign_status: pre-SIGN`, category H narrow scope frontmatter, anchor-evidence loaded from S1304 §14 D2/D6 + §15 T2 + S1302 §14 F4/F5 + §15 T3/T4.
4. **Playbook §13 6-parallel-Explore sweep** — 6 sub-agents launched simultaneously per playbook §13 rule (single message with 6 tool-use blocks): Agent 1 Models & Persistence, Agent 2 Services & Runtime Flows, Agent 3 APIs Tools Tasks Commands, Agent 4 Integrations & Cross-Domain, Agent 5 Documentation & Prior Research, Agent 6 Drift Debt Ownership & Maturity.
5. **Parent-agent verifier-loop pre-SIGN corrections** — 4 sub-agent claims corrected before folding: (v-l-1) Agent 6 CRITICAL severity on AgentLearningService downgraded to MEDIUM per Redis AOF context; (v-l-2) Agent 6 "13 timeout=None" corrected to 5 production sites; (v-l-3) Agent 6 "3 disjoint DBs" corrected to 4; (v-l-4) Agent 1 vs Agent 2 conflict on search_docs cache location resolved.
6. **v0.1 draft** — 945 lines, 20-section audit per playbook §11.2, with §20.5 conflicts + §20.6 verifier-loop corrections logged.
7. **Rigby SIGN cycle 1** — routed via fresh isolation pin `pa-56a527a2c5528508`. Verdict: SIGN-with-edits, Medium confidence, 3 must-fix folds (§3 + §14 D10 scoping tightening, §7.2 gap (a) direct-code-evidence, §14 D8 DB isolation citation) + 1 bonus fold (§19 R6 reshape post-MemorySystem-active confirmation).
8. **v0.2 fold** — 1080 lines after applying all 3 must-fix folds + bonus + gating checklist updates + §20.7 fold notes + §20.8 SIGN cycle history table.
9. **Rigby SIGN cycle 2** — verification-only pass via same pin. Verdict: SIGN-clean, High confidence, 0 must-fix, 1 optional micro-tighten (NOT blocking). Rigby ratified all 3 cycle-1 folds and §19 R6 reshape.
10. **`sign_status` frontmatter flipped** — `pre-SIGN` → `SIGN-with-edits (cycle 1 folded)` → `SIGN-clean (cycle 2 verification pass)`. Gating checklist updated: all boxes ticked except Chris commit-gate.
11. **Chris close decision card** — D16 COMMIT + D17 S1399 next + D18 RETIRE PIN presented with default leans. Chris ratified via `commit + retire pin`.
12. **Post-decision cascade** — pin retired via Rigby `session_tool.retire` (`updated_count: 2, retired: true`); ARCHITECTURE_INDEX v16 → v17 with §1.20 + §8 timeline row; OPEN_ARCS Group 1300 row advanced + 2 reconciliation notes; 00-START-NEXT-SESSION rotated to S1399 mission spec; this handoff drafted.

## What lands

### Deliverable audit at 1080 lines

- 20-section playbook §11.2 template
- `sign_status: SIGN-clean` (Rigby cycles 1 + 2)
- 20-section §-anchors preserved for future §-references
- §14 Known Drift: 10 rows (D1-D10) with file:line citations, severity, class per playbook §12
- §15 Known Technical Debt: 12 rows (T1-T12) with severity + boundary-scope + remediation sketches
- §18 Ownership Gaps: 5 unassigned invalidation contracts + 2 assigned (platform_config, EmbeddingService)
- §19 Recommended Future Research: 8 rows (R1-R8) with priority ranking
- §20 Appendix: 10 subsections including verifier-loop corrections, Rigby fold notes, SIGN cycle history table

### Index updates

- ARCHITECTURE_INDEX.md v16 → v17
- §1.20 row added with ~200 lines of body (matches S1304 §1.19 length)
- §8 Architecture Timeline S1305 row added (comprehensive prose row)
- Frontmatter `last_verified` block updated with v17 entry summary
- Frontmatter `owner:` line extended with v17 update note

### OPEN_ARCS updates

- Group 1300 in-progress row current-child field advanced
- State annotation "in-progress (awaiting S1399 canonical summary)"
- Next-expected pointer rotated to Group 1300 Canonical Summary S1399 with per-parent §5 P6 rationale + playbook §11.3 template + 5-deliverable breakdown
- 2 reconciliation notes appended (S1305 open, S1305 close)

### Handoff (this doc)

- Full close artifact for Group 1300 P5
- Rigby SIGN cycle 1 + cycle 2 detail preserved
- Pin retirement verified
- Methodology extension (severity-correction) documented
- Next-session first-action punch list

### 00-START-NEXT-SESSION rotation

- Retired-pin note added for pa-56a527a2c5528508
- Active arc pin `pa-aa54193f240f4846` preserved
- S1399 mission spec (bounded canonical summary, playbook §11.3, NOT re-audit) with D19 + D20 default leans

## What's queued for next session (S1399)

**Group 1300 Canonical Summary** — bounded work (one session per playbook §11.3). Deliverables per parent §5 P6 rationale:

1. Consolidated memory-subsystem shape map across all 6 in-scope categories
2. Cross-cutting patterns (F1 provenance-filter drift, F2 orphan-write, F3 Redis-only + LRU staleness, F4 F1/F4-CANDIDATE + severity-correction discipline)
3. `PLATFORM_INVENTORY.md` §3 update recommendations
4. Follow-on research queue with rankings
5. Cross-links to Employee OS 1200s Cat G arc + Group 1700 Observability arc delegations

**Full SIGN routing with Q10-Q13 canonical-summary pressure-test questions per playbook §15.**

## Load-bearing methodology extension

**Severity-correction via sibling-inheritance.** S1305 extends the verifier-loop pattern from hypothesis-correction (S1304 partial invalidation of S1301 §19 D3) to severity-correction. When a sub-agent produces a severity classification that contradicts a sibling audit's classification for the same underlying finding, the parent-agent applies sibling-inheritance discipline to downgrade (or upgrade) with rationale logged in §20.5/§20.6.

Applied at S1305 §14 D3: Agent 6 CRITICAL → MEDIUM per Redis AOF context (`settings.py:944 REDIS_APPENDONLY=True`) matching S1302 T3 sibling classification. Rigby SIGN cycle 1 ratified the downgrade (did not push back).

**Library impact:** Verifier-loop pattern now applies to (a) sub-agent hypothesis claims AND (b) sub-agent severity classifications. Rigby SIGN cycles focus on substantive additions rather than upstream evidence/severity corrections. Future audits under this discipline should expect cleaner cycle 1 folds (evidence + severity pre-corrected).

## Group 1300 arc at S1305 close

- **5 child audits shipped SIGN-clean.** Categories A, B, C, D, E, F, H covered; G delegated to Employee OS 1200s arc.
- **Arc state:** in-progress (awaiting S1399 canonical summary).
- **Next mission:** S1399 Group 1300 Canonical Summary — bounded work.
- **Arc pin:** `pa-aa54193f240f4846` preserved for S1399 continuity + arc close.
- **Prior sibling PRs:** S1301 #2775 + #2776; S1302 #2777 (`c053272a`); S1303 #2778 (`6365f33f`); S1304 #2779 (`4271e913`); S1305 pending push.

## Reference — where to look

- **This audit:** `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md`
- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **All 5 sibling audits:** `docs/research/domains/memory/130[1-5]_*.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 template, §11.3 canonical summary template, §13 sweep, §14 evidence, §15 SIGN routing + Q10-Q13, §16 commit policy)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Arc navigation:** `docs/research/ARCHITECTURE_INDEX.md` §1.20 + §8 S1305 row
- **Arc state:** `docs/research/OPEN_ARCS.md` Group 1300 in-progress row
- **Next session priorities:** `00-START-NEXT-SESSION.md` S1399 mission spec
