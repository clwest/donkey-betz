# Session 1217 — Bounded-Audit Execution: All 3 Chris-Picked Items Closed

**Status:** All 3 Chris-picked items closed in one session. 2 code PRs open (#2506, #2507) + Items 2 + 3 investigation deliverables populated to ~6-7 KB each. Closing-doc PR.
**Date:** 2026-06-23 (same day as Sessions 1214/1215/1216/1217-prep — fifth single-day arc, second of the bounded-audit pair).
**Active conversation:** `pa-58737666f25741dc` — carried forward from Session 1217 prep.
**Prior session:** [`SESSION_1217_PREP_BOUNDED_AUDIT_EXPERIMENT.md`](./SESSION_1217_PREP_BOUNDED_AUDIT_EXPERIMENT.md).
**Next session entry point:** Session 1218 — see 00-START-NEXT-SESSION.md "FIRST THING Session 1218".

## TL;DR

The Session 1217 prep session shipped a self-directed audit deliverable and Chris picked 3 items off it. This session executed all 3 in parallel-where-possible: Items 1A + 1B as 2 code PRs (open, pending merge), Items 2 + 3 as investigation-only deliverable appends. Headline corrections to the original audit numbers: the "59 schemaless handlers" was actually 66 (start-here count mixed raw schema lines with unique handler counts), and **31 of 65 unique surplus agent classes have ZERO AgentExecution rows ever** — the real dead-weight signal.

## Session Manifest

### PRs opened

| # | Title | Item | What |
|---|---|---|---|
| **#2506** | `fix(session-1217): drop dead validated_result guard in concrete_executor (Item 1 Bug A)` | 1A | `ai_core/agents/concrete_executor.py:511` — guard `if 'validated_result' in locals() else result` always evaluated False inside `_execute_project_builder_agent` (the function never assigns `validated_result`; mythology enforcement lives in the sibling `_execute_real_agent` path at line 305). Replaced with plain `result`. 1-line diff. |
| **#2507** | `fix(session-1217): replace broken OpenAIProvider.generate body with deprecation stub (Item 1 Bug B)` | 1B | `ai_core/agents/agent_llm_integration.py:92` — body referenced undefined `messages` variable. Rigby ratified **B1** (keep method, raise `NotImplementedError`) over **B2** (delete class + provider branch) because B2 would change provider-selection semantics for `real_*` agent paths imported by 4 production modules. Drops unused `AsyncLLMAdapter` import. Adds `tests/ai_core_tests/test_agent_llm_integration_provider_stub.py` (1 test, asserts NotImplementedError + message points at canonical path). |
| **(this PR)** | `docs(session-1217): close — bounded-audit execution handoff + Session 1218 start-here update` | — | This handoff + 00-START-NEXT-SESSION.md "FIRST THING Session 1218" rewrite. |

### Deliverables populated

| ID | Title | Final size | Status |
|---|---|---|---|
| `192a390c-ebb6-4574-8d29-6f6e60fd2778` | PA tool schema/handler delta classification (Item 2) | **6,208 chars** | populated via Rigby `deliverable_tool.append` of Claude's findings |
| `b92c41d0-e886-4586-84c6-61206034668a` | PA tool top 10 failure signatures (Item 3) | **7,489 chars** | populated by Rigby (failure_signatures pulls + close note); Claude provided cross-link guidance |

## Item-by-item close

### Item 1 — Two undefined-variable bugs

**Both bugs were precisely as described in the audit deliverable.**

- **Bug A (`concrete_executor.py:511`)**: Confirmed dead branch. `_execute_project_builder_agent` (lines 417-540) never defines `validated_result`. Only `_execute_real_agent` (around line 280) does. The `if 'validated_result' in locals()` guard at 511 always evaluated False → always returned plain `result`. PR #2506 deletes the dead branch. **Intentional non-touch:** line 357 has the same guard expression but inside `_execute_real_agent` where `validated_result` IS defined — guard is redundant but not broken. Per minimum-scope rule, left alone.

- **Bug B (`agent_llm_integration.py:92`)**: Confirmed undefined `messages` reference. Rigby asked first re scope because Chris's lean was "delete the method" but bare deletion breaks the `LLMProvider` ABC contract (instantiation at line 204 would fail). Rigby ratified **B1**: keep method, replace body with deprecation log + `NotImplementedError`. **B2 deferred** (full class removal + drop `openai` branch from `generate_for_agent`) because it would silently change provider-selection semantics for the `real_*` agent paths in `core/views_real_income_builder.py`, `core/orchestra_consumers.py`, `core/unified_hub.py`, `core/agent_platform_consumer.py`. Smoke test asserts `NotImplementedError` raises and message points at `core/services/openai_client_factory.py`.

### Item 2 — 59-handler schema/handler delta classification

**Two headline corrections to the start-here doc.**

| Metric | start-here said | Actual (this session) |
|---|---|---|
| Schema count | 115 | **109 unique** (start-here counted raw `"name":` lines; 6 of those are nested property names, not tool names) |
| Handler-only surplus | 59 | **66** (174 − 108 paired = 66; start-here did 174−115 mixing raw vs unique) |

**Structural finding: all 66 are agent-name aliases for one generic dispatcher.** `tool_dispatcher.py:1071 _handle_agent_tool` is the single underlying handler; the 66 registrations are convenience aliases so callers can `dispatcher.execute("game_predictor", ...)` directly. Rigby reaches them via `run_agent(agent_name="X")` per the schema enum (`pa_tool_schemas.py:1069-1136`). The "schemaless" framing in the audit misread the dispatcher's structure — zero handlers are truly invisible to Rigby.

**Telemetry finding: 31 of 65 unique agent classes have ZERO AgentExecution rows ever.** True dead-weight candidates by domain:

| Domain | Zero-exec classes |
|---|---|
| Markets / Stock | BullCaseAgent, MarketAnomalyDetectorAgent, MarketIntelligenceAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, SignalScannerAgent |
| Sports & Betting | BookmakerAgent, LineMovementAnalyzer, SharpActionDetector |
| Content Studio | ContentDiversityOrchestrator, ContentExecutorAgent, ContrarianAgent, DistributionAgent, PerformanceAnalystAgent |
| Cultural / Narrative | CulturalImpactAgent, NarrativeDriftCoordinator, NarrativeHistorianAgent, TrendBreakDetectorAgent |
| Podcast / Debate | DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |
| Blockchain Audit | ExploitDetectorAgent, SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent |
| Misc | DecisionEnforcerAgent, PromptEngineeringAgent, ResolveAgent, TalkingCharacterAgent, TechnicalDocumentAgent, VoiceCriticAgent |

**Recommendation surfaced (NOT shipped this session — Item 2 is investigation-only):** trim those 31 from `run_agent` enum + `tool_dispatcher.py` register block + `_tool_to_agent_name` mapping. Would visibly shrink Rigby's tool surface area.

**Direct dispatcher callers outside PA: none.** All 16 grep hits for `tool_dispatcher.execute(...)` are inside `unified_pa_entrypoint.py`, `td_handlers_*` gateway re-dispatch, `consumers_pa_conversation.py`, or `pa_status_events.py`.

### Item 3 — Top 10 PA tool failure signatures

**Rigby ran the failure pull via `ops_tool.failure_signatures` (window=7d).** All 10 are watchdog-timeout category — agents timed out via `watchdog_cleanup` after ~3600s (TrainedCreationAgent, AudioAgent, SystemIntelligenceAgent, COOAgent, CTOAgent, etc.).

**Cross-link to Item 2 close finding** (Claude-side guidance, Rigby appended verbatim):
- Failure attribution names the AGENT class, not a PA tool name, because `_handle_agent_tool` returns task_id immediately (Session 1088 Celery async conversion); the failure happens INSIDE the Celery agent task.
- Every failing class is in the **34/65 actively-used surplus set** — none are in the 31 zero-exec dead-weight set (dead-weight never runs to fail).
- **Followup work is the 3600s watchdog ceiling**, not the PA dispatcher.

## What this session did NOT do (deferred per Chris's do-not-touch list)

- Promote `check-reasoning-contract.yml` to enforce mode (Session 1216 P2 carryover).
- Doc-vs-runtime drift triage (#6/#7/#8 from audit).
- Critical-path hub markers (#4 from audit).
- Atlas fleet positioning + narrative staleness (#9/#10).
- Beat schedule disabled tasks classification (Rigby's A4).
- Revenue pipeline aggregation audit (Rigby's C5).
- **Item 2 cleanup PRs**: trimming the 31 dead-weight classes from `run_agent` enum + dispatcher. Surfaced as a recommendation in the deliverable; not shipped because Item 2 was specced investigation-only.

## Open items for Session 1218

1. **Merge PRs #2506 + #2507 + this docs PR.**
2. **Trim 31 dead-weight agent classes** from `pa_tool_schemas.py` + `tool_dispatcher.py` + `td_handlers_agents.py:_tool_to_agent_name`. Verify no `td_handlers_*` gateway calls them by name string first. Should be one PR with 3-file diff + 0 functional changes.
3. **Investigate 3600s watchdog timeout root cause** — every PA tool failure in the 7-day window traces to this. Could be (a) Celery soft-limit too aggressive, (b) agent body genuinely hanging, (c) downstream API timeout absorbed silently.
4. **B2 follow-on for OpenAIProvider** (deferred from PR #2507): full removal of the class + `openai` branch in `generate_for_agent`. Requires first proving the `real_*` agent paths are no longer exercised in production (per Session 1214 handoff note: "the live path appears to use AsyncLLMAdapter directly").
5. Run `python manage.py verify_doc_claims --only-drift` after PR merge to confirm no doc drift from the bug fixes.
6. Run `python manage.py build_docs_index` after PR merge per memory rule.

## Operational invariants (post-merge)

- `_execute_project_builder_agent` returns the raw agent result without mythology validation — that path never had it, the dead guard was hiding the absence. If product wants mythology checks for project-builder agents, that's a separate add (likely call `mythology_enforcer.enforce(...)` before line 511 in the new structure).
- `OpenAIProvider.generate()` will now raise loudly instead of `NameError`-ing if any caller routes through it. Live OpenAI dispatch goes through `core/services/openai_client_factory.py` + `AsyncLLMAdapter` — confirmed no production path lands in this stub.

## Memory updates worth carrying forward

No new feedback memories from this session. Two existing rules dogfooded:
- `feedback_deliverable_tool_use_append_for_large_payloads.md` — used `append` (not `update`) for both Item 2 (5,466 chars) and Item 3 (7,489 chars total). Both verified via returned `content_length`.
- `feedback_rigby_collaboration.md` — pinged Rigby for scope ratification on Bug B before deleting; she steered to B1 over B2 with concrete production-impact reasoning.

## Files touched this session

```
ai_core/agents/concrete_executor.py                                  (1 line)
ai_core/agents/agent_llm_integration.py                              (-60 / +20 lines)
tests/ai_core_tests/test_agent_llm_integration_provider_stub.py      (NEW, 22 lines)
docs/handoffs/SESSION_1217_BOUNDED_AUDIT_EXECUTION.md                (NEW, this file)
00-START-NEXT-SESSION.md                                             (FIRST THING Session 1218 rewrite)
```
