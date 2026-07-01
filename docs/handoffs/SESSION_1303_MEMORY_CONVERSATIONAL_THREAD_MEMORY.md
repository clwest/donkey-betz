---
session: 1303
status: closed (draft-audit landed, Rigby SIGN-clean after cycles 1 + 2, Chris commit-gated → committed)
date: 2026-07-01
arc: Research Group 1300 (Memory / Knowledge / Embeddings) — child P3 (playbook §11.2 20-section audit template). Third child audit under the parent-with-children arc. Category F Conversational / Thread Memory exclusive scope per parent §5 P3 slot — **first-inventory landing in the library**: Cat F had no `platform_architecture_inventory.md` §3.N row at audit open; audit produces the terrain (§4 Major Models + §7 Runtime Flows load-bearing sections, not just referential). Inherits S1302 §17.3 name-collision resolution as boundary anchor + S1302 §14.3 F1 dead-code detection methodology as evidence-gathering approach (applied per verifier discipline, not as verdict).
prs_merged: []
prs_open:
  - "S1303 audit + INDEX v15 + OPEN_ARCS + handoff + START-NEXT rotation (branch docs/session-1303-memory-conversational-thread-memory off main; Chris commit-gate resolved this session → PR opens on push)"
prs_upstream:
  - "S1302 commit-gate on main (PR #2777 = c053272a) — resolved between S1302 close and S1303 open; S1303 branches off main, not stacked on S1302"
branches_open:
  - "docs/session-1303-memory-conversational-thread-memory (base = origin/main)"
companions:
  - docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md
  - docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md
  - docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md
  - docs/research/domains/memory/1300_memory_domain_scoping.md
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md
  - docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
deliverables:
  - "docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md (~1401 lines, status: draft, sign_status: SIGN-clean, authority: research, research_group: 1300, child_slot: P3, domain_slug: memory; 20-section playbook §11.2 template; verifier_loop v0.1 skeleton + v0.2 synthesis + v0.3 SIGN cycle 1 12-edit fold + v0.4 SIGN cycle 2 verification pass — SIGN-clean)"
  - "docs/research/ARCHITECTURE_INDEX.md — v14 → v15; §1.18 row added; §8 timeline S1303 row added; owner-line updated with v15 entry"
  - "docs/research/OPEN_ARCS.md — Group 1300 in-progress row current-child advanced from 'S1302 SIGN-clean (commit-gated) + S1303 queued' to 'S1303 SIGN-clean (commit-gated) + S1304 queued'; 2 reconciliation notes added (S1303 open, S1303 close)"
  - "docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md (this doc)"
  - "00-START-NEXT-SESSION.md — rotated to S1304 mission spec (Categories E ↔ D Documentation Corpus ↔ RAG Boundary)"
key_findings:
  - "F1 (S1212 deliverable 777d9cd8 stale-thread dispatcher waste, ~$3.60/day on retired-thread dispatches): CONFIRMED RECONCILED via S1248 matched-pair fix. Retire handler at `core/services/td_handlers_core.py:4011-4072` sets `session_active=False` on all rows for the target `conversation_id`; dispatcher gate at `core/services/conversation_action_dispatcher.py:288-316` blocks any `next_steps` dispatch into fully-retired threads. Enforcement is best-effort / fail-open under DB errors (line 317-323 try/except envelope) — availability > correctness by design. Rigby SIGN cycle 1 flagged this as the riskiest practical residual (§14 F1 severity LOW; residual observability question — how often does the fail-open envelope fire? — deferred to §19 R2 → Group 1700 Observability)."
  - "F2 (`session_tool.retire` action existence): CONFIRMED PRESENT via direct read of `td_handlers_core.py:4011-4072`. Memory rule `feedback_session_tool_retire_works.md` stands. Handler returns `{retired: True, updated_count}` on success (line 4061); requires `force=True` if retiring currently-bound thread (line 4035-4050); response includes `pin_rotation_notice` at line 4064-4071 instructing wrapper edit at `tools/pa_local.sh` line 70; idempotent (`.filter(session_active=True).update(...)` returns 0 rows on double-retire). Parent §3F stale bullet ('retire does not exist; retire = stop using + repin') formally resolved to CONFIRMED PRESENT."
  - "F3 (wrong-model + wrong-field usage in `core/agents/content_writer_agent.py`): CONFIRMED SOFT FAIL AT IMPORT + LATENT QUERY-TIME FieldError under guard. Line 76 uses `from core.models_unified_system import ConversationMemory` (soft-fails via try/except at lines 74-80 → `MEMORY_AVAILABLE=False`). Rigby SIGN cycle 1 surfaced deeper issue: guarded branch at line 370 filters `ConversationMemory.objects.filter(user=user, memory_type__in=['success', 'insight', 'learning']).order_by('-created_at')[:5]` — but Django `ConversationMemory` at `core/models/conversations/models.py:19-31` has NO `memory_type` field (that field lives on `UserMemoryContext` at `:253`). Consequence: fixing D1's import alone shifts crash from import-time-soft-fail to query-time-FieldError. D1 debt widened to 'wrong model + wrong field'; fix requires canonical model choice + ORM field realignment. Rigby SIGN cycle 2 confirmed via direct code read."
  - "F4 (`ChatConversation.context_used` + `.agent_results` phantom-field candidates): CANDIDATE — NOT YET PROVEN EITHER WAY. Verifier discipline downgraded Agent-6's 'confirmed dead code / 0 reads' verdict to CANDIDATE per memory rule `feedback_verify_before_deleting_dead_code.md`. Rigby SIGN cycle 1 confirmed the raw-keyword grep catches unrelated variables: `tasks_agents.py:1262` `agent_results = phase_data.get('results', {})` is a local dict in a different scope, NOT a read of `ChatConversation.agent_results` (verifier note); `epa_handlers_utility.py:2910` `aggregate_agent_results()` is a method aggregating over `execution_ids`, NOT reading the field. §19 R1 split into R1.a owner-model-qualified consumer inventory (do first) / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth resolution (first-class fields vs `metadata` dict). Audit does NOT assert dead/unused; future PR proposals MUST wait for R1.a-c."
  - "F7 (no Cat F event stream on EventBus): REFRAMED as gap / partial adoption per Rigby SIGN cycle 1 E11. Zero `CONVERSATION_*` streams in `event_bus.py:21-31`; zero consumers for turn events. Delegated to Group 1700 Observability future arc for spec + adoption decision (§19 R2). Compounds with F9 (no auto-cleanup) + F1 residual fail-open observability."
  - "F8 (pin rotation policy lives only in `tools/pa_local.sh` header comments): CONFIRMED policy-in-tooling anti-pattern. Retire-vs-continue heuristics articulated only inline in the wrapper's retirement record (S1098, S1165, S1267, S1300, S1301, S1302 retire logs). No formal doc; no automation; no audit trail beyond handoff prose. §19 R7."
  - "F9 (no auto-cleanup for retired rows): CONFIRMED MISSING. Zero Celery task, zero management command, zero TTL config for retired-thread deletion or archival. Rows accumulate indefinitely (severity LOW; storage cost, not blocking). §19 R4."
  - "F10 (Discord unlinked-user linkage-completion signal): CONFIRMED MISSING. Discord users start sessions unlinked (`user_id=None`, `discord_user_id=<X>`). No signal fires when the user later links accounts; orphan rows persist. Severity LOW."
  - "Cat F ↔ Cat D wiring: reframed from Agent-4's 'MISSING' to OBSERVED GAP + owner-confirmation-required per Rigby SIGN cycle 1 E6. No verified wiring found from turn-history reinjection (Cat F) → retrieval query augmentation (Cat D). Could be intentional separation (thread memory user-scoped; corpus retrieval source-scoped) or missing integration. §19 R3 delegates to S1304 (Cat E ↔ D boundary)."
  - "Maturity verdict (post-SIGN cycle 1 bounded via E1): WORKING (bounded) — interactive web PA sessions with DB-backed turn reinjection are stable; PARTIAL — lifecycle hygiene (cleanup / events), analytics completeness, and hard policy enforcement (retired-thread gating is best-effort / fail-open under exceptions). Applied per S1274 continuous-language rule for continuous reality."
  - "Load-bearing runtime flow discovery — `_load_conversation_history_from_db()` at `core/services/unified_pa_entrypoint.py:7277-7343`: last 10 ChatConversation rows scoped to `conversation_id` (7300-7302), Discord rows excluded (7294), 5-second `SET LOCAL statement_timeout='5000'` (7291), chronologically ordered (7309), assistant response truncated to 8000 chars (7327 — post-S1085 bump from 2000), tool-call metadata reinjected via `meta.get('tool_calls')` + `meta.get('tool_results')` + `meta.get('response_id')` (7331-7336), fail-open on exception (7342-7343 → empty list). Turn context survives Celery worker recycles (max_tasks_per_child) via this DB reload."
  - "PA_USE_FUNCTION_CALLING env dependency: verified at `unified_pa_entrypoint.py:684` per Agent 2; turn-history persistence is env-agnostic (loads from DB regardless of function-calling mode). Memory rule `feedback_pa_worker_function_calling_env.md` applies to the tool-loop path, not the history-load path."
  - "God-service ranking: `unified_pa_entrypoint.py` = 7,613 lines (verified); `td_handlers_core.py` = 4,168 lines (verified); `conversation_action_dispatcher.py` = 716 lines; `conversation_memory.py` = 211 lines. First two exceed the playbook §13 3000-line god-service flag threshold."
  - "New §20.9 subsection 'Reinjection Metadata Contract' documents 4 expected `ChatConversation.metadata` dict keys (`source`, `tool_calls`, `tool_results`, `response_id`) with producer/consumer citations to prevent F4-style false dead-code claims by distinguishing model fields from metadata dict keys. Grep-verified consumers at `unified_pa_entrypoint.py:7311-7336`."
  - "New §20.10 subsection is explicit `status: draft` → `status: active` gating checklist (12 items); 11 ticked at close; Chris commit-gate is the last box (ticked when this handoff commits)."
  - "§19 downstream routing (updated post-SIGN): R1.a-c owner-model-qualified F4 verification (highest priority); R2 Cat F ↔ EventBus adoption → Group 1700 Observability; R3 turn-context → RAG enrichment → S1304 Cat E ↔ D boundary; R4 retention lifecycle for retired rows; R5 land first-inventory §3.N row via S1399 canonical summary; R6 formalize session identity mint contract (§17 duplicate mechanism — `create_fresh` `pa-<hex>` vs `get_or_create_session` `uuid4()`); R7 doc-in-tooling reconciliation (F8); R8 D1 broken import + field mismatch runtime PR (not research)."
open_decisions_carried_forward:
  - "S1303 SIGN isolation pin `pa-23a38300dd84bae2` retirement — SIGN cycles 1+2 complete + SIGN-clean; pin may retire at Chris's discretion after commit (same pattern as S1301 retire at S1301 close + S1302 retire at S1302 close)."
  - "S1304 launch cadence — playbook default is 'immediate on session open'. If Chris commit-gate on S1303 branch not resolved by S1304 open, stacking on `docs/session-1303-memory-conversational-thread-memory` branch is possible per S1301's stacking pattern; otherwise S1304 branches off `main`."
rigby_sign_cycle_1:
  fresh_isolation_pin: "pa-23a38300dd84bae2"
  pin_title: "S1303 SIGN — Memory Domain (Category F) Conversational / Thread Memory Architecture Audit pressure-test (isolation)"
  ownership_verified: "chris (via `platform_config_tool overview` confirmation of `service_context: local` before pin creation)"
  provisional_verdict: "SIGN-with-edits (2 fold cycles planned). Rigby independently grep-verified load-bearing claims and confirmed the F4 discipline downgrade was correct: her `agent_results` sweep found `tasks_agents.py:1262` matches were unrelated local variable (`agent_results = phase_data.get('results', {})`), NOT a read of the ChatConversation field, which directly validates the F4-CANDIDATE hedge. She also surfaced F3 deeper issue: `content_writer_agent.py:370` filters `memory_type__in=[...]` but Django ConversationMemory has no such field."
  must_fix_folded_12_edits:
    - "E1 §13 maturity verdict — bounded WORKING (interactive web PA + DB-backed turn reinjection) + PARTIAL (lifecycle hygiene / analytics / hard policy enforcement fail-open)"
    - "E2 §14 F3 — keep MED severity at import-time (soft-fail via try/except guard); add query-time FieldError risk clause; tie to D1"
    - "E3 §15 D1 — widen to 'ConversationMemory name collision + wrong model/field usage (import soft-fail + query-time FieldError risk)'; fix requires canonical model choice AND ORM field alignment"
    - "E4 §14 F4 — rewrite as CANDIDATE — NOT YET PROVEN EITHER WAY; evidence incomplete; do NOT assert dead/unused"
    - "E5 §19 R1 — split into R1.a owner-model-qualified consumer inventory (do first) / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth (first-class fields vs metadata dict) resolution"
    - "E6 §9 Cat F ↔ Cat D row — replace MISSING with OBSERVED GAP + interpretation + owner-confirmation-required framing"
    - "E7 §7 Flow E — add fail-open nuance (availability > correctness by design; `try/except Exception` envelope at conversation_action_dispatcher.py:317-323)"
    - "E8 §5.2 retire behavior — add force-required + updated_count + idempotency clauses"
    - "E9 §1 Executive Summary — add 6th 'biggest gap' point on reinjection metadata contract"
    - "E10 §20.9 new subsection — 'Reinjection Metadata Contract' documenting 4 expected metadata keys with producer/consumer citations"
    - "E11 §14 F7 — reframe as gap/partial adoption, not defect (Cat F event streams may be intentional-not-yet-spec'd)"
    - "E12 §20.10 new subsection — explicit `status: draft` → `status: active` gating checklist (12 items)"
  additional_observations:
    - "Q1 metadata contract subsection (new work — E9 + E10 satisfy)"
    - "Q4 Cat F ↔ Cat D reframe (E6 satisfies)"
    - "Q6 riskiest finding = fail-open retired-thread gate (E7 satisfies); second = F4 false-dead-code risk (E4 satisfies)"
rigby_sign_cycle_2:
  same_isolation_pin: "pa-23a38300dd84bae2 (fresh pin preserved across cycles per playbook §15 fold-cycle pattern)"
  final_verdict: "SIGN-clean. Verification pass (not structural rewrite). Cycle 2 confirmed all 3 required verifications via direct code reads: (1) §14 F4 rewrite matches cycle 1 grep evidence + discipline note cites `tasks_agents.py:1262` correctly; (2) §19 R1 split into R1.a/b/c is coherent and ordering defensible; (3) §15 D1 widened framing matches `content_writer_agent.py:370` reality — Rigby independently read `content_writer_agent.py:330-450` + `models/conversations/models.py:1-31` and confirmed ConversationMemory has NO memory_type field (that field lives on UserMemoryContext at :253)."
  bonus_checks_passed:
    - "§13 maturity bounding (E1) reads correctly; separates bounded WORKING vs PARTIAL cleanly including best-effort / fail-open retired-thread gate nuance"
    - "§14 fail-open language consistent with dispatcher-gate code behavior (previously verified in cycle 1)"
  no_edits_required: true
next_session_readiness:
  - "S1304 mission is well-scoped: Category E ↔ D Documentation Corpus ↔ RAG Boundary. Inherits: S1301 §14.2 silent-failure surface + §19 downstream routing; S1302 §17.3 name-collision resolution as boundary anchor pattern; S1303 §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3 turn-context → RAG enrichment design proposal. Parent §5 P4: 'smaller scope; benefits from §3.14 audit landing first (S1301 shipped).'"
  - "S1303 verified the 6-parallel-Explore sweep + parent-agent verifier-loop pattern works for first-inventory audits — the pattern is stable across single-category (S1301), combined-category (S1302), and first-inventory (S1303) audits. Third consecutive Group 1300 child."
  - "S1303 established: verifier-loop spot-checks CAUGHT Agent-6's two overreaches (F3 import-time crash claim, F4 dead-code claim) BEFORE Rigby SIGN. Consequence: SIGN cycle 1 focused on substantive additions (metadata contract, D1 widen, Cat F ↔ Cat D reframe, maturity bounding, R1 split) instead of evidence corrections. Cycle 2 was pure verification. Only child audit to reach SIGN-clean in 2 cycles (S1301 = 1, S1302 = 3). The pattern: catch evidence overreach parent-side first so SIGN cycles focus on substantive gaps, not evidence corrections."
  - "F4-CANDIDATE discipline extends S1302 §14.3 F1 dead-code methodology: keyword grep is insufficient for dead-code verdicts; owner-model qualification is required. Future audits applying this pattern must not accept keyword-grep evidence for dead-code claims. Filed as reusable methodology for S1304 + S1305 + future domain audits."
memory_rule_touches:
  - "feedback_pa_local_verify_ownership.md — S1303 confirmed ownership on both arc pin (pa-aa54193f240f4846) and fresh isolation SIGN pin (pa-23a38300dd84bae2) via `platform_config_tool overview` returning `service_context: local` before first PA call."
  - "feedback_claude_directs_rigby_then_verifies.md — S1303 open executed the pattern: service_context: local check directive → Rigby ran `platform_config_tool overview` → Claude verified. D10/D11 routing directive → Rigby ran default-lean framing → Chris ratified 'agree all' → Claude proceeded."
  - "feedback_rigby_tool_verification.md — S1303 SIGN cycle 1 truncated at Q7 in terminal display; verifier read the Tool Runs (verbose) block to confirm Rigby had grep-verified F4 example (`tasks_agents.py:1262`) before assuming outage. Placeholder-stall pattern NOT hit — Rigby's response was substantive; just truncation in the terminal rendering."
  - "feedback_verify_before_deleting_dead_code.md — LOAD-BEARING for F4 downgrade. Verifier spot-check found Agent-6's 'confirmed dead code / 0 reads' claim relied on keyword grep that catches unrelated variables. Applied memory-rule discipline: cannot claim 'dead' without owner-model-qualified consumer inventory + docs/ + handoffs + audit deliverables via Rigby. Downgraded to CANDIDATE + filed §19 R1 (split into R1.a/b/c) as follow-on research. This is the pattern-application that saved this audit from shipping a wrong verdict."
  - "feedback_session_tool_retire_works.md — carried forward from S1301 close. Direct read of `td_handlers_core.py:4011-4072` confirmed handler exists + returns `{retired: True}` on success. Parent §3F stale bullet ('does not exist') formally resolved."
  - "feedback_verifier_loop_pattern.md — S1303 exercised the pattern: parent-agent verifies EVERY quantitative claim + file path via direct Django ORM read / grep receipt / file read before including in the audit. Caught F3 severity overreach (Agent 6 said 'runtime crash'; verifier found try/except guard → soft-fail). Caught F4 dead-code overreach (Agent 6 said '0 reads'; verifier found keyword grep insufficient). Both downgrades folded into audit v0.2 BEFORE Rigby SIGN, so SIGN cycles focused on substantive gaps not evidence corrections."
  - "feedback_docs_pipeline_4_step_cascade.md — S1303 handoff + INDEX v15 + OPEN_ARCS advancement + audit all get pushed to Documents + embedded via the 4-step cascade after Chris commit. Not run in this session."
followup_queue:
  - "S1304 Documentation Corpus ↔ RAG Boundary (Categories E ↔ D) — inherits provenance-boundary questions from S1301 + S1302 + Cat F ↔ Cat D reframe from S1303"
  - "S1305 Runtime Memory Correctness (Category H narrow scope — Redis-loss + lru staleness)"
  - "S1399 Group 1300 Canonical Summary — cross-cutting synthesis; must resolve (a) row-level orphan-write drift class formalization + owner-model-qualification methodology inheritance from S1303 F4 discipline, (b) MemoryPromotionService Cat B vs Cat C category assignment (S1302 F6), (c) spider_data_bridge naming reconciliation (S1302 F5), (d) write-authority framework anchor recommendation for PLATFORM_INVENTORY §3.13 update (S1302 T10), (e) LAND FIRST-INVENTORY §3.N ROW for Cat F (S1303 R5)"
  - "Group 1700 Observability filter-drop + dead-code / producer-only detection telemetry follow-on + EventBus adoption spec for Cat F (S1303 R2)"
  - "R1.a-c F4 CANDIDATE verification for ChatConversation.context_used + .agent_results (S1303 §19 R1) — HIGHEST PRIORITY follow-on"
  - "R3 turn-context → RAG query augmentation design-preparation doc (Cat F → Cat D wiring) — delegated to S1304"
  - "R6 formalize session identity mint contract (S1303 §17 duplicate mechanism)"
  - "R7 doc-in-tooling reconciliation for pin rotation policy (S1303 F8)"
  - "R8 fix D1 broken import + field mismatch in content_writer_agent.py — runtime PR (not research)"
  - "Design-preparation ADR (post-S1399) — write authority framework for A/B/C. Filed by S1302; carries forward."
owner: claude (drafted S1303)
---

# Session 1303 — Memory Conversational / Thread Memory (Group 1300 Child P3)

## Session shape

**Mission (opened by Chris short command 2026-07-01):** *"Please start research group 1303"* — the playbook §21 continuation form on the third child audit under Research Group 1300 (Memory / Knowledge / Embeddings). Category F Conversational / Thread Memory exclusive scope per parent §5 P3 slot.

**Executed contract:**
- Playbook §21 continuation → §11.2 20-section child-audit template.
- Playbook §13 6-parallel-Explore sub-agent sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity).
- Parent-agent verifier-loop spot-checks per playbook §13 synthesis step 2 (front-ran F3 import-time crash claim, F4 dead-code claim, load-bearing line counts, retire handler direct read, retired-thread gate direct read, turn-history reinject flow direct read).
- Playbook §15 stage-scoped Rigby routing: full SIGN required on child audits; routed to a fresh isolation pin (`pa-23a38300dd84bae2`) per fresh-pin discipline. Two fold cycles (12-edit cycle 1 + verification-only cycle 2).
- Playbook §16 commit policy: draft-first, Chris commit-gate. Chris commit-gate resolved this session via explicit "commit it" instruction.

**Session close criteria met per playbook §14 completion contract:**
- Audit doc at `status: draft`, `sign_status: SIGN-clean`, all 20 sections populated with cited evidence + honest UNKNOWNs + Rigby SIGN fold history.
- Rigby SIGN cycles 1 + 2 → SIGN-clean after one 12-edit fold cycle + one verification pass.
- INDEX v15 registration (§1.18 + §8 timeline row + frontmatter `last_verified` bump + owner-line update).
- OPEN_ARCS Group 1300 row current-child advancement + 2 reconciliation notes (S1303 open, S1303 close).
- This handoff.
- 00-START-NEXT-SESSION.md rotated to S1304.

## What the audit found (executive)

Category F — Conversational / Thread Memory — is the load-bearing runtime substrate for every PA turn on the platform. It carries: (a) the `pa-*` session pin identity that binds a series of PA turns into one conversational thread; (b) the persisted turn history that survives Celery worker recycling and gets reinjected into each new LLM prompt; (c) the retire/set_active lifecycle that gates whether retired threads receive downstream agent dispatches. The domain is **PARTIAL / WORKING (bounded)** — active-session flows are STABLE (session pin generation, retire handler, retired-thread dispatcher gate all shipped and tested), but retention / cleanup / observability edges are MISSING.

The primary storage model is `ChatConversation` at `core/models/conversations/models.py:59-187` — a row-per-exchange table carrying `conversation_id` (CharField, the `pa-<hex[:16]>` pin), `session_active` (BooleanField, the retire marker), and `metadata` (JSONField carrying the load-bearing tool-call reinjection keys `tool_calls` / `tool_results` / `response_id` / `source`). The load-bearing service is `unified_pa_entrypoint.py` — 7,613 lines, a god-service by playbook §13 threshold. The load-bearing runtime flow is `_load_conversation_history_from_db()` at `unified_pa_entrypoint.py:7277-7343` — loads the last 10 rows scoped to `conversation_id`, reinjects tool-call metadata, fails open on DB errors.

**Six biggest gaps discovered:**

1. **No cleanup for retired rows** (§14 F9, §19 R4). No Celery task, no management command, no TTL config. Retained indefinitely.
2. **No event emission on Cat F state changes** (§10, §14 F7, §19 R2). EventBus infrastructure exists with 8 streams; zero of them are `CONVERSATION_*`. ChatConversation writes are silent to observability + downstream consumers.
3. **Turn context does not enrich RAG queries** (§9 Cat F ↔ Cat D, §19 R3). Observed gap; owner confirmation required (could be intentional user-scoped vs source-scoped separation, or missing integration).
4. **Two F4-CANDIDATE phantom-field candidates** (§14 F4, §19 R1). `ChatConversation.context_used` + `.agent_results` show heavy producer surface; consumer-side reads unclear on quick spot-check. Downgraded from Agent-6's "confirmed dead" verdict to CANDIDATE per memory rule `feedback_verify_before_deleting_dead_code.md`. R1 split into R1.a owner-model-qualified consumer inventory (do first) / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth (first-class fields vs `metadata` dict) resolution.
5. **Pin rotation cadence lives only in `tools/pa_local.sh` header comments** (§14 F8, §19 R7). No formal policy doc, no automation, no audit trail for retire-vs-continue decisions.
6. **Reinjection metadata contract is undocumented** (new §20.9). `ChatConversation.metadata` carries load-bearing keys consumed by turn-history reinjection but no schema, no type annotations, no formal contract. New §20.9 subsection documents the 4 verified consumer keys with producer/consumer citations to prevent F4-style false dead-code claims by distinguishing model fields from metadata dict keys.

**Two verifier corrections during synthesis** — captured in `verifier_loop:` frontmatter:

1. **F3 severity downgrade.** Agent 6 claimed `content_writer_agent.py:76` "would fail at import time." Direct read of lines 74-80 showed try/except ImportError guard → SOFT FAIL (feature degradation, not runtime crash). Downgraded CRITICAL → MED. Rigby SIGN cycle 1 then surfaced the deeper issue at line 370: `ConversationMemory.objects.filter(user=user, memory_type__in=[...])` — Django `ConversationMemory` has no `memory_type` field, so import fix alone would shift crash from import-time to query-time. D1 widened to "wrong model + wrong field."

2. **F4 verdict downgrade.** Agent 6 declared `ChatConversation.context_used` + `ChatConversation.agent_results` "confirmed dead code" (0 reads across whole tree). Memory rule `feedback_verify_before_deleting_dead_code.md` forbids dead verdicts without owner-model-qualified consumer grep. Rigby SIGN cycle 1 confirmed the discipline: her `agent_results` sweep found `tasks_agents.py:1262` `agent_results = phase_data.get('results', {})` is a local dict in a different scope, NOT a read of `ChatConversation.agent_results`. Downgraded to CANDIDATE + filed §19 R1.

Both corrections shipped to Rigby BEFORE SIGN, so SIGN cycles focused on substantive edges (metadata contract, D1 widen, Cat F ↔ Cat D reframe, maturity bounding, R1 split) instead of evidence corrections. This is the pattern S1303 validates: **catch evidence overreach parent-side first, so SIGN cycles focus on substantive gaps not evidence corrections**. Consequence: only child audit to reach SIGN-clean in 2 cycles (S1301 = 1, S1302 = 3).

**§19 downstream routing:**
- R1 (F4 candidate verification) split into R1.a owner-model-qualified consumer inventory (do first) / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth resolution. HIGHEST priority follow-on.
- R2 Cat F ↔ EventBus adoption design → Group 1700 Observability future arc.
- R3 turn-context → RAG enrichment design → S1304 (Cat E ↔ D boundary).
- R4 retention lifecycle for retired rows.
- R5 land first-inventory §3.N row for Cat F → S1399 canonical summary.
- R6 formalize session identity mint contract (§17 duplicate mechanism — `create_fresh` `pa-<hex>` vs `get_or_create_session` `uuid4()`).
- R7 doc-in-tooling reconciliation for pin rotation policy (F8).
- R8 fix D1 broken import + field mismatch in `content_writer_agent.py` — runtime PR (not research).

## What did NOT get done

- **No implementation PRs.** Playbook §14.5 forbids implementation during research; the audit is design-input, not design.
- **No full-tree F4 verification sweep.** By design — filed as §19 R1.a-c for follow-on research per memory rule `feedback_verify_before_deleting_dead_code.md`.
- **No formal reinjection metadata schema (TypedDict / pydantic / JSONSchema).** Filed as §15 D4.
- **No git-history trace on `_bound_conversation_id` sentinel introduction.** Not needed for the audit; filed under §20.4 unknowns.
- **No landing of Cat F §3.N row in `platform_architecture_inventory.md`.** Per parent §5, that lands in S1399 canonical summary — audit produces the candidate content, not the row.

## Session-close artifacts on the working tree (uncommitted before this handoff)

```
docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md   [new, ~1401 lines]
docs/research/ARCHITECTURE_INDEX.md                                                [modified, v14 → v15, §1.18 + §8 timeline S1303 row]
docs/research/OPEN_ARCS.md                                                         [modified, Group 1300 row advanced + 2 reconciliation notes + last_updated]
docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md                  [new, this doc]
00-START-NEXT-SESSION.md                                                           [modified, S1304 mission spec]
```

## Ready-to-commit single gesture

```bash
git add docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md \
        docs/research/ARCHITECTURE_INDEX.md \
        docs/research/OPEN_ARCS.md \
        docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md \
        00-START-NEXT-SESSION.md
git commit -m "docs(session-1303): Memory Conversational / Thread Memory audit + INDEX v15"
```

Chris commit-gate: **RESOLVED** — Chris explicit "commit it" instruction 2026-07-01.

## Reference — where things are

- **S1303 audit:** `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md`
- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Sibling audits (Cat D, Cat A+B+C):** `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` + `1302_memory_persistence_architecture_audit.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` (no §3.N row for Cat F today — first-inventory landing target)
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Category F primary model:** `core/models/conversations/models.py:59-187` (`ChatConversation`)
- **Category F in-process facade:** `core/conversation_memory.py:59-211` (`ConversationMemory` facade wrapping Cat B Django model)
- **Category F session_tool handler:** `core/services/td_handlers_core.py:3864` (`_handle_session`), 7 actions: `health_check`, `create_fresh`, `list_recent`, `whoami`, `retire`, `set_active`, `seed`
- **Category F turn-history reinject:** `core/services/unified_pa_entrypoint.py:7277-7343` (`_load_conversation_history_from_db`)
- **Category F retired-thread gate:** `core/services/conversation_action_dispatcher.py:288-316` (S1248 fix for S1212 deliverable 777d9cd8)
- **F3 wrong-model+wrong-field site:** `core/agents/content_writer_agent.py:76` + `:370`
- **Fresh SIGN pin (retirable at Chris discretion):** `pa-23a38300dd84bae2`

## Pin state

- **Arc pin (Group 1300 continuity):** `pa-aa54193f240f4846` — carries S1300 + S1301 + S1302 + S1303 mission-side context. Preserved for S1304 continuity.
- **SIGN isolation pin (S1303 only):** `pa-23a38300dd84bae2` — SIGN cycles 1 + 2 complete + SIGN-clean. May retire at Chris's discretion after commit.
