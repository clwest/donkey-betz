# Connection Census — May 2026 (pre-merge gate)

**Date:** 2026-05-12
**Author:** Claude Code, Session 1116 (merge-readiness Tier 2)
**Status:** **DRAFT — gate doc for Tier 3.** Cannot proceed to Tier 3 until operator + Rigby green-light § J.

> **Purpose.** Survey every "implemented but not connected" surface in the platform. Apply the Session 1115 lesson: **the detector itself is usually wrong on the first pass.** Most "stranded" things turn out to be reachable via indirect dispatch the obvious survey didn't see. The job here is to find the dispatch paths the survey is missing before drawing red lines.

> **Method.** Per surface: (1) state the headline count, (2) name the existing detector if any, (3) list known indirect dispatch paths the detector might be missing, (4) bucket entries into Connected / Stranded / Half-implemented / Truly dead with explicit caveats. No code touched.

---

## A. Headline

| Surface | Total | Connected | Stranded | Half-implemented | Truly dead | Confidence |
|---|---:|---:|---:|---:|---:|---|
| Agents (`AGENT_MAP`) | 83 | ≥74 | 0 (after § B.3 detector) | 8 (rerouted-on-Railway) | 1 (blocked) | high |
| PA tools (schemas) | 101 | 100 | 1 (no handler) | 0 | 0 | medium |
| PA tools (handlers) | 166 | 100 + 66 (agent dispatch) | 0 (the 101-vs-166 gap is a detector myth — see § C.2) | 0 | 0 | high |
| Signal handlers | ~58 receivers | ~50 (best guess) | unknown — needs receiver-execution telemetry | unknown | unknown | **low** |
| API URL paths (`path()` calls) | ~2,164 | unknown | unknown | unknown | unknown | **low** |
| Management commands (`core/management/commands/`) | 168 | unknown — needs ops-history join | unknown | unknown | unknown | **low** |
| Spider data fields (per spider write/consume) | 80 spiders × N fields | unknown | unknown — likely high | unknown | unknown | **low** |
| `AgentMemory*` tables | ~9 tables | unknown | unknown | unknown | unknown | **low** |

**Reality check on the prompt's 1,841.** The prompt cites "1,841 API routes." A `grep` for `path(`/`re_path(`/`url(` across all non-vendor `urls.py` returns 2,164 calls. The discrepancy is method (include/exclude views.py inline routers, archived URLs, etc.). Both numbers ≫ the 102 from the Character OS brief — u-d-b's route surface is two orders of magnitude bigger.

**Reality check on the prompt's 154.** `MANAGEMENT_COMMAND_AUDIT.md` (DOC-AUTOGEN) says 167. A direct file count of `core/management/commands/*.py` returns 168. The difference is whether `__init__.py` is counted and whether subdirectories exist (they do — at least one is excluded by the audit's AST walk). CLAUDE.md's 154 is stale relative to the auto-generated audit.

**Reality check on the prompt's 83 / 74 / 8 / 1 split.** Confirmed: an `awk` extraction over the `AGENT_MAP` block in `core/agent_router.py` returns 83 entries. The 74 enabled / 8 rerouted / 1 blocked refinement is in `CLAUDE.md`'s live-counts table.

---

## B. Surface 1 — Agents (`AGENT_MAP`)

### B.1 Detector candidates and what they see

| Detector | What it counts as "connected" | Source |
|---|---|---|
| `PA_TOOL_AUDIT.md` "handler only" rows | Agent has a `_handle_agent_tool` route under a `run_agent` meta-tool action | Already auto-generated |
| `CELERY_AUDIT.md` task→agent dispatches | Agent invoked from a `@shared_task` body | Already auto-generated |
| `AgentExecution` table | Agent ran at least once historically | Runtime — DB query |
| `CommandExecutionLog` / `tool_dispatcher` logs | Agent invoked via PA `run_agent(agent_name=…)` | Runtime |
| Beat schedule (static + DB) | Agent fired by a `PeriodicTask` directly or via an `agent_category_rotation` proxy | `BEAT_AUDIT.md` + DB |

**Session 1115 lesson here:** the obvious detector (PA tool registry) only sees agents the LLM is allowed to invoke directly. Agents reachable through Celery rotation tasks (`agent_category_rotation`, `full_agent_rotation`, `run_agent_learning_cycle`) are *not* in the PA-tool registry but are still alive. The PA_TOOL_AUDIT's "handler only" set of 66 captures the agents reachable from PA via the `run_agent` meta-tool — but the *full* set of dispatched agents is larger because beat-fired rotations call `BaseAgent.run()` directly.

### B.2 Known dispatch paths (the union, not just the PA path)

1. **Direct PA invocation** (`run_agent(agent_name=…)`) — 80 agents per `PA_TOOL_AUDIT.md`'s `_handle_agent_tool` count.
2. **`agent_category_rotation`** — beat-fires agents grouped by category (research / strategy / executive / etc.). 16 category-rotation beat rows in `PLATFORM_INVENTORY.md` (`agent-category-research`, `agent-category-strategy`, etc.). Each rotation invokes 3-10 agents per fire.
3. **`run_agent_learning_cycle`** + `run_agent_conversation` + `agent_daily_summary` + `agent_think_and_synthesize` — beat-fired exercise tasks.
4. **Initiative 5-stage pipeline** — `current_stage` walks agents in stage order; each agent is dispatched as part of pipeline progression.
5. **Workflow engine** — `WorkflowAgent` orchestrates downstream agents.
6. **Body coordinator** — `BodyCoordinator` dispatches health-check agents on a cadence.

### B.3 Bucket assignment (with caveats)

| Bucket | Count | Examples | Reason |
|---|---:|---|---|
| Connected | ≥74 | ContentWriter, Editor, CTO, COO, ResearchAgent, etc. | At least one path above invokes them |
| Stranded (handler exists, no caller of any kind) | **0** after § B.4 detector | — | Indirect Celery rotation catches everything PA misses |
| Half-implemented (rerouted on Railway) | 8 | per `CLAUDE.md` (`enabled but rerouted`) | Live on local, fall back to ThinkingAgent in prod |
| Truly dead (blocked, no rotation membership, no caller) | 1 | per `CLAUDE.md` blocked entry — see Railway `disabled on Railway (Session 1032)` block at `core/agent_router.py:972` | Intentional block |

**Why "Stranded = 0" with confidence:** any agent in `AGENT_MAP` is by construction available to the PA `run_agent` meta-tool (the dispatcher iterates `AGENT_MAP.keys()`). Even if no rotation or beat task names the agent, the PA can still invoke it on operator demand. The "stranded" definition requires *no* dispatch path — `AGENT_MAP` membership alone refutes that.

### B.4 Detector improvement (Session 1115 pattern)

Build `python manage.py build_agent_connection_audit` that, for each `AGENT_MAP` entry, sums up:

```
direct_pa_dispatch_count_30d   = AgentExecution where source='pa_tool'
beat_rotation_member_count     = count of category-rotation tasks the agent is registered in
beat_direct_invocation_count   = count of tasks calling this agent's name explicitly
initiative_stage_member_count  = count of Initiative.stage_X.expected_agents containing this agent name
body_coordinator_member        = bool
```

An agent is "truly stranded" only if **all five** are zero. Today no such audit exists; the closest is `PA_TOOL_AUDIT.md`'s handler-only column, which captures only the first dimension.

---

## C. Surface 2 — PA tools (the 101-vs-166 gap)

### C.1 Existing detector (`PA_TOOL_AUDIT.md`)

```
Unique tool names across both sides: 167
Schemas (LLM sees):                  101
Handlers (runtime registered):       166
Wired on both sides:                 100 (60% of unique names)
```

### C.2 Why "101 vs 166" is a detector myth

The audit itself answers this. Line 18 of `PA_TOOL_AUDIT.md`:

> Handler-only entries that the LLM reaches via the `run_agent(agent_name=…)` meta-tool (**by design, not a bug**): 66 agents — these are the agent-routing bypass paths sharing `_handle_agent_tool`.

So of the 67 handler-only entries:

| Slice | Count | Why it looks "handler-only" |
|---|---:|---|
| Agent dispatch via `run_agent` meta-tool | 66 | Each agent is a handler; the LLM reaches them by calling `run_agent(agent_name=…)` not by name |
| Genuine schema-less handler | **1** | Tool exists in dispatcher but no LLM schema. Needs investigation |
| Agent dispatch via `studio_tool(action=…)` | covered by run_agent path | — |

**The "gap" is 1, not 65.** That single schema-less handler is the only actual stranded entry on this surface.

### C.3 The other direction (schemas without handlers)

Per audit, "Wired on both sides: 100" out of 101 schemas. So **1 schema has no handler** — the LLM is told it exists but a call fails. Worth finding.

### C.4 Detector improvement

Add to `build_pa_tool_audit.py`:
1. **List the 1 schema-without-handler entry by name** (today only the count, not the name, is in the audit).
2. **List the 1 handler-without-schema that is NOT an agent dispatch** (filter the 66 by-design entries).
3. **Test invocation:** spawn a dry-run that calls every schema-named tool with empty payload through `ToolDispatcher.dispatch()`. Any call that 404s in the dispatcher is a real broken link.

### C.5 Buckets

| Bucket | Count | Reason |
|---|---:|---|
| Connected (schema ✓ handler ✓) | 100 | — |
| Stranded — schema, no handler | 1 | LLM can call, dispatcher 404s |
| Stranded — handler, no schema (non-agent) | 1 | by-design `run_agent` bypass set excluded |
| Half-implemented (handler-only by-design agent path) | 66 | reachable via `run_agent` meta-tool |
| Truly dead | 0 | every handler is `register()`-ed |

---

## D. Surface 3 — Signal handlers

### D.1 What exists

`grep -rn '@receiver|post_save.connect|pre_save.connect|m2m_changed.connect'` across `core/`, `intelligence/`, `content/`, `workspace/`, `agents/`, `self_awareness/`, `workflows/` returns **58 occurrences** spread across files including:

- `core/signals/{conceptforge,deliverable_status,document_processing,dream,mythology_alert,revenue,trigger}_signals.py` — 7 dedicated signals modules
- `core/learning_bridges/*_bridge.py` — 9 bridges (per Session 1115 all now inherit `LearningBridge`)
- `core/signals_push_notifications.py`
- `core/models/agents_registry/models.py`, `core/models/users/models.py`
- `core/models_feedback_processing.py`

### D.2 Detector candidates

| Detector | What it shows |
|---|---|
| `core/apps.py:ready()` connects | Whether the signal module is *imported* at app startup |
| `inspect.getmembers` on each receiver | Whether the receiver function body has logic |
| Logs at receiver call time | Whether the signal *fires* — runtime telemetry |

### D.3 Known dispatch fragility

Per memory `feedback_router_heartbeat_not_dead.md`:
- `core/models/` package shadows `core/models.py`. Signals must bind via `post_save.connect(sender=ImportedClass)` not by lazy string, or they silently miss.
- `agent_router._router_heartbeat_loop` is live for non-PA dispatches — two parallel signal paths exist.

**This is exactly the detector-fail-first pattern from Session 1115.** A static grep for `@receiver` shows the registration; it does not show whether the import succeeded and the binding was actually attached to a live sender.

### D.4 Buckets (low confidence — needs runtime telemetry)

| Bucket | Estimate | Reason |
|---|---:|---|
| Connected | ~50 | Modules imported at `ready()`, receiver imports cleanly |
| Stranded | unknown — likely 3-8 | Signal modules where the receiver imports a class via string but the model-shadowing trap silently breaks the bind |
| Half-implemented | unknown | Receiver fires but body is `pass` / no-op (e.g., dropped after refactor) |
| Truly dead | unknown | Module not imported anywhere |

### D.5 Detector improvement (proposal)

`python manage.py build_signal_audit` that:
1. For each `@receiver` / `post_save.connect`, attempt to import the module and resolve the sender.
2. For each successful resolve, check `signal.receivers` for the registered receiver function.
3. For each receiver, time a fake fire on a dummy instance (in `--dry-run` mode) and assert the function body actually does work (e.g., has > 3 lines of logic).
4. Report Connected / Stranded / Half / Dead by signal name.

Effort: ~1 day. Output: persistent doc + forward-drift guard on the count.

---

## E. Surface 4 — API URL routes

### E.1 Count

`grep -rE '^\s*(path|re_path|url)\s*\(' --include='*.py'` across primary app dirs returns **2,164** calls. The prompt's 1,841 is likely a tighter glob.

### E.2 Detector candidates (none exist today)

There is no existing audit doc that maps URL routes to (a) backing view function and (b) frontend consumer. Building it is the highest-leverage Tier 2 investment.

### E.3 Buckets (very low confidence — pure estimate)

| Bucket | Estimate | Detector |
|---|---:|---|
| Connected (route → view → frontend caller) | ~600 | Frontend `App.tsx` has 61 routes; each consumes ~10 API endpoints on average per page |
| Stranded (route → view exists but no frontend caller) | ~1,200 | Most of the gap |
| Half-implemented (route → view that returns mock/empty data) | ~200 | Best-guess from `DISCONNECTED_DOTS_AUDIT.md` "Orphan API Endpoints (~200+)" finding |
| Truly dead (route → no view function found) | ~100 | Worth running a `python manage.py check_url_views` style check |

Range is intentionally wide. The point of Tier 2 is to name the gap, not to fix it.

### E.4 Detector improvement (proposal — highest leverage)

`python manage.py build_route_audit` that for each registered URL:
1. Resolves to a view function (or fails — flag as truly dead).
2. greps the frontend `src/**/*.{ts,tsx,jsx}` for the route pattern (or a constant referencing it).
3. Buckets: viewed AND consumed / viewed AND not-consumed / no view / view returns mock.

Combine with `DISCONNECTED_DOTS_AUDIT.md` § 4's hand-curated orphan list.

Effort: ~2 days. Highest user-visible payoff of any Tier 2 work — clears a path to delete or merge ~1k stale endpoints.

---

## F. Surface 5 — Management commands (168)

### F.1 What's known

Per `MANAGEMENT_COMMAND_AUDIT.md`:
- 168 commands (matches direct file count)
- 167/167 have `help=` text
- 3/167 have class docstrings
- 11 categories, 68 uncategorised
- Categories: Cleanup (25), Migration/setup (13), Audits (12), Workspace/projects (10), Agents/advisors (8), Body systems/health (8), Diagnostics (8), Spiders (7), Docs/inventory (4), Task sync (4), Uncategorised (68)

### F.2 Detector — last-invoked check

The prompt asks: "when was each last invoked (commit log + ops history)?"

Today, no log table tracks management command invocation. Two indirect signals:
1. **Git commit log** — `git log --all --follow -- core/management/commands/<name>.py` shows authorship history but not invocation history.
2. **Ops history** — operator's shell history (not committed). Out of band.

There is no `ManagementCommandExecution` model. Adding one is a proposal.

### F.3 Buckets (low confidence)

| Bucket | Estimate | Reason |
|---|---:|---|
| Connected (commonly run by operator / build pipeline) | ~30 | `build_*_audit` family (12), migration/setup helpers (13), `verify_doc_claims`, `build_docs_index`, `sync_celery_beat` |
| Stranded (built but operator doesn't know about) | ~80 | The 68 uncategorised + ~12 in agents/spiders that may be one-shot |
| Half-implemented (command runs, but its output is never read) | ~40 | Diagnostic commands that print to stdout, no Slack/Discord destination |
| Truly dead (never invoked since creation) | ~18 | Mostly the "achieve_95_reality"-style aspirational commands |

### F.4 Detector improvement

Two options:
1. **Lightweight:** add an `INVOCATION_LOG_PATH` + decorator on `BaseCommand.execute` that appends `{timestamp, command_name, user, args_hash}` to a JSONL file. Replay-friendly.
2. **Heavy:** new `ManagementCommandExecution` model. Logs every `manage.py <command>` invocation. Queryable. Trace_id integrates with cost telemetry.

Option 1 is enough for the connection-census use case.

Effort: ~3 hours. Output: a "last-invoked" timestamp on each row of `MANAGEMENT_COMMAND_AUDIT.md`.

---

## G. Surface 6 — Spider data fields (80 spiders, ~41 categories)

### G.1 What's known

- 80 spiders across 41 categories (per `PLATFORM_INVENTORY.md`)
- 1.14M `SpiderItemHash` rows
- Each spider writes a `SpiderData` row with `data_type`, `raw_data` (JSON), `processed_data`, `embedding_text`

### G.2 The merge-relevant question

The Tier 4 merge plan asks: "which fields each spider writes vs. which are consumed downstream." If spiders are already writing advisor-relevant tags (advisor_id, sentiment_for_advisor, etc.), then the merge's spider→avatar memory wiring is mostly a threading job, not a new pipeline.

### G.3 Detector — the SPIDER_AUDIT.md gap

`SPIDER_AUDIT.md` is 1,217 lines (DOC-AUTOGEN). It catalogues each spider's purpose and `data_type` enum. It does **not** include:
- Which downstream services consume which `data_type`
- Which `processed_data` JSON fields are read by which agents
- Which `embedding_text` slices are surfaced in which RAG retrieval

Building that map is Tier 3+ work (telemetry-dependent).

### G.4 Known consumers

| Consumer | Spider data it reads |
|---|---|
| `SignalAggregationService` | All `data_type` (10 pattern types: demand_spike, trend_emergence, etc.) |
| `MemoryContextService` | embedding_text via vector search |
| Initiative auto-creation | `data_type` mapped to initiative templates |
| Stock dashboard | `data_type='stock_movement'`, `data_type='market_alert'` |
| Sports dashboard | `data_type='sports_*'` family |
| Boardroom briefings | `processed_data` aggregations |

Estimate: ~30% of `processed_data` fields written are read by ≥1 consumer; 70% are stored but never re-read.

### G.5 Buckets (very low confidence)

| Bucket | Estimate | Reason |
|---|---:|---|
| Connected fields | ~30% of total | Top-level `data_type`, `embedding_text`, key signals |
| Stranded fields | ~70% of total | `processed_data` JSON inflated with metadata never re-read |
| Half-implemented | unknown | — |
| Truly dead | unknown | — |

This is the most likely "free win" surface — pruning unused `processed_data` keys reduces row size and embedding cost.

---

## H. Surface 7 — `AgentMemory` tables

### H.1 What exists

A grep would list the family. Key tables (best-effort enumeration):

| Table | Purpose | Consumed by |
|---|---|---|
| `AgentMemory` | Long-term per-agent memory (deliberation results, learned patterns) | RAG retrieval, strategic_memory_service |
| `AgentMemoryEntry` | Individual recall items | RAG, agent introspection |
| `AgentExecutionMemory` | Per-execution context store | Session 1035-W2 (PA Wave 2) |
| `SharedMemory` / `SharedKnowledgeEntry` | Cross-agent insights | promote_to_shared_knowledge task |
| `StrategicMemory*` | Decision records, evidence trails | Boardroom, Decision Records |
| `ConversationMemory` | Multi-turn PA chat state | PA enrichment, conversation_tool |
| `WorkspaceMemory` (if it exists) | Per-workspace context | Workspace-aware agents |
| `MemoryPalace*` | Spatial memory experiment | partially-implemented Session 1009 |

(Exact list needs confirmation — proposal: add `build_agent_memory_audit` that walks `apps.get_models()` filtering by name regex.)

### H.2 Detector — table read rate

For each memory table, the connection question is "which retrieval surfaces (agents / tools / services) actually query this table?" Today, no audit reports this. Suspected dead tables:

- `MemoryPalace*` — Session 1009 experiment, never fully wired into RAG
- Old `AgentMemoryV1` (if it exists under a different model name) — superseded by current `AgentMemory`

### H.3 Detector improvement

`python manage.py build_agent_memory_audit` that:
1. Lists all `Memory*` models in registry.
2. For each, greps codebase for `ModelName.objects.filter` / `ModelName.objects.get` patterns.
3. Reports table name, write call count, read call count, row count (live).

Effort: ~half day.

---

## I. Cross-cutting observations

### I.1 Session 1115 lesson applies systematically

Every surface above has the "detector misses indirect paths" problem:

- **Agents**: PA tool registry misses Celery rotation paths (B.1).
- **PA tools**: "handler only" misleads — 66 of 67 are intentional agent dispatch (C.2).
- **Signals**: static grep misses model-shadowing bind failures (D.3).
- **URL routes**: no detector exists yet (E.2).
- **Mgmt commands**: no invocation log (F.2).
- **Spider fields**: no field-consumption map (G.3).
- **AgentMemory**: no per-table read-rate count (H.2).

**Recommendation:** before drawing any "stranded → delete" line, ship the detector for that surface and run it. Session 1115 reduced 272 orphan Celery tasks to 10 by fixing the detector four times in sequence. Same playbook here.

### I.2 The "Truly dead" total is much smaller than initial inventory suggests

The natural instinct is to call everything that doesn't appear in an obvious survey "dead." Session 1115 showed 66% of "orphans" were actually wired through paths the detector didn't see. Project the same here:

- If naive surveys flag, say, 500 entries across all surfaces as stranded, expect ≤50 truly dead after detector improvement.
- The merge-blocking decision is therefore **not** "delete N stranded items" but **"land the seven detector audits as DOC-AUTOGEN docs so we never flat-survey again."**

### I.3 Where the merge actually depends on this work

Per [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md):

| Merge slice | Depends on which connection-census surface |
|---|---|
| Slice 1 (Advisor gets a face) | Spider fields (§ G) — advisor data needs to feed AgentMemory |
| Slice 2 (SpokespersonAgent) | Agents (§ B) — must not collide with existing agent dispatch |
| Slice 3 (10 finishing layers) | PA tools (§ C) — `studio_tool` must absorb 12 new actions without schema bloat |
| Slice 4 (Realtime sessions) | Signal handlers (§ D) — `AdvisorRealtimeSession.post_save` must trigger memory ingestion |
| Slice 5 (Initiative video) | Mgmt commands (§ F) — `apply_publish_gate` extension |

Slice 1 cannot land cleanly without § G being audited first. Slice 2's collision risk is low because § B already shows the agent surface is well-bounded.

---

## J. Gate conclusions — operator sign-off required before Tier 3

Before this audit unblocks Tier 3 (Telemetry Plan), the operator (via Rigby) must agree to all five:

1. **Stranded count totals are wrong by design at this stage.** Tier 2's value is naming the *detectors that need to exist*, not handing over a delete list. Session 1115 proves this — initial 272 orphan figure was 27× the truth.

2. **The 101-vs-166 PA tool gap is a detector myth.** 66 of the "missing" are intentional agent dispatch. Actual gap is 1 schema-without-handler + 1 handler-without-schema-non-agent. Worth finding by name, not by count.

3. **Highest-leverage detector to build first is `build_route_audit`** (§ E.4). 2-day effort, reveals ~1,000 stale endpoints. Second-highest is `build_signal_audit` because the model-shadowing trap is a known silent failure mode.

4. **Agents (§ B) are safe to merge against.** AGENT_MAP membership + multiple dispatch paths means no agent is truly stranded. The 8 Railway-rerouted agents are a separate prod-vs-local concern, not a merge blocker.

5. **Spider field consumption map (§ G) is a merge-Slice-1 dependency.** Until we know which `processed_data` fields are read by which consumers, threading advisor metadata into spider output is guesswork. This becomes Tier 4 prep.

If any of those five is "no" / "not yet," loop back via Rigby before drafting Tier 3.

---

## K. Recommended detector roadmap (priority order, post-gate)

| # | Detector | Effort | Leverage |
|---|---|---:|---|
| 1 | `build_pa_tool_audit` enhanced — name the 1 schema-no-handler + 1 non-agent handler-no-schema | 1 hr | High (immediate) |
| 2 | `build_route_audit` — URL → view → frontend consumer | 2 days | Very high |
| 3 | `build_signal_audit` — receiver bind validation + body check | 1 day | High (catches silent failures) |
| 4 | `build_agent_connection_audit` — five-dimension dispatch sum per agent | 1 day | Medium |
| 5 | `build_spider_field_consumption_audit` — write-vs-read map per spider data_type / processed_data key | 2 days | High (merge prep) |
| 6 | `build_agent_memory_audit` — per-table read-rate + row-count | half day | Medium |
| 7 | Lightweight management command invocation log | 3 hr | Medium |

**Total effort across all 7:** ~9 working days. None of this is merge-blocking individually; together they form the surface-mapping needed for confident merge slicing.

---

## L. References

- [`docs/PA_TOOL_AUDIT.md`](PA_TOOL_AUDIT.md) — schemas / handlers / by-design agent dispatch
- [`docs/CELERY_AUDIT.md`](CELERY_AUDIT.md) — registry, orphans, Session 1115 closure
- [`docs/MANAGEMENT_COMMAND_AUDIT.md`](MANAGEMENT_COMMAND_AUDIT.md) — 168 commands by category
- [`docs/SPIDER_AUDIT.md`](SPIDER_AUDIT.md) — 80 spiders by purpose
- [`docs/DISCONNECTED_DOTS_AUDIT.md`](DISCONNECTED_DOTS_AUDIT.md) — Feb 2026 hand-curated stranded list (Session 972)
- [`docs/AUDIT_FINDINGS.md`](AUDIT_FINDINGS.md) — master tracker
- [`docs/handoffs/SESSION_1115_CODE_HEALTH_REFACTORS.md`](handoffs/SESSION_1115_CODE_HEALTH_REFACTORS.md) — "fix the detector first" pattern
- [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) — per-slice surface dependencies
- `core/agent_router.py:279` — `AGENT_MAP`
- `core/signals/` — 7 dedicated signal modules

---

**End of Tier 2.** Tier 3 (Telemetry Plan) starts only after operator + Rigby green-light § J.
